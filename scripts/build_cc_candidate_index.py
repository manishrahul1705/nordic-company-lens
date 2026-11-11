"""Build a deterministic candidate-only CC index from the cached measurement snapshot."""
import csv
import gzip
import hashlib
import io
import json
import random
import re
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'bench/reports/cc-proto/raw/warc-results.jsonl'
OSM = ROOT / 'bench/reports/osm-check/raw'
OUT = ROOT / 'data'
LABEL = re.compile(r'(?i)(?:\borg\s*\.?\s*nr\s*\.?|\borganisasjonsnummer|\bforetaksregisteret)\s*[:#.-]?\s*(?:NO\s*)?((?:[0-9][ .\u00a0]*){8}[0-9])(?![0-9])|\bNO\s*((?:[0-9][ .\u00a0]*){8}[0-9])\s*MVA\b')


def valid(n):
    if not re.fullmatch(r'[0-9]{9}', n):
        return False
    check = (11 - sum(int(d) * w for d, w in zip(n[:8], (3, 2, 7, 6, 5, 4, 3, 2))) % 11) % 11
    return check != 10 and check == int(n[-1])


def labelled(snippet):
    return {re.sub(r'[^0-9]', '', m[1] or m[2]) for m in LABEL.finditer(snippet)}


def textfile(path):
    f = path.open('rb')
    magic = f.read(2)
    f.seek(0)
    return io.TextIOWrapper(gzip.GzipFile(fileobj=f) if magic == b'\x1f\x8b' else f, encoding='utf-8-sig')


def instant(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00')).astimezone(timezone.utc)


def main():
    OUT.mkdir(exist_ok=True)
    csv.field_size_limit(10000000)
    with textfile(OSM / 'subunits.csv.download') as f:
        sample = f.read(32768)
        f.seek(0)
        parents = {r['organisasjonsnummer']: r['overordnetEnhet'] for r in csv.DictReader(f, dialect=csv.Sniffer().sniff(sample, delimiters=';,\t'))}
    # Bound the snapshot so an independently running collector can continue appending.
    snapshot = RAW.stat().st_size
    rows = {}
    digest = hashlib.sha256()
    read = 0
    trailing = 0
    with RAW.open('rb') as f:
        while read < snapshot:
            line = f.readline(snapshot - read)
            read += len(line)
            digest.update(line)
            if not line.endswith(b'\n'):
                trailing += len(line)
                break
            if line.strip():
                r = json.loads(line)
                rows[r['key']] = r
    domain_ids = defaultdict(set)
    for r in rows.values():
        domain_ids[r['domain']].update(n for n in r.get('numbers', {}) if valid(n))
    banned = {d for d, ids in domain_ids.items() if len(ids) >= 3}
    pairs = {}
    rejected_snippets = 0
    crawls = set()
    for r in rows.values():
        crawl = r.get('crawl') or re.search(r'CC-MAIN-\d{4}-\d{2}', r['key'])[0]
        crawls.add(crawl)
        if r['domain'] in banned or r.get('error'):
            continue
        for number, snippet in r.get('numbers', {}).items():
            if not valid(number):
                continue
            snippet = snippet[:120]
            if number not in labelled(snippet):
                rejected_snippets += 1
                continue
            parent = parents.get(number) or number
            if not valid(parent):
                continue
            entry = {'domain': r['domain'], 'crawl': crawl, 'timestamp': instant(r['timestamp']).isoformat(), 'url': r['url'], 'observed_orgnr': number, 'snippet': snippet}
            key = (parent, r['domain'])
            rank = (instant(entry['timestamp']), json.dumps(entry, sort_keys=True))
            if key not in pairs or rank > pairs[key][0]:
                pairs[key] = (rank, entry)
    grouped = defaultdict(list)
    for (parent, _), (rank, entry) in pairs.items():
        grouped[parent].append((rank, entry))
    index = {}
    for parent in sorted(grouped):
        newest = sorted(grouped[parent], key=lambda x: x[0], reverse=True)[:3]
        index[parent] = sorted((e for _, e in newest), key=lambda e: e['domain'])
    payload = (json.dumps(index, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n').encode()
    target = OUT / 'cc_orgnr_index.json.gz'
    target.write_bytes(gzip.compress(payload, compresslevel=9, mtime=0))
    with textfile(OSM / 'universe.jsonl.gz') as f:
        universe = {str(r.get('organisation_number') or r.get('organisasjonsnummer') or r.get('orgnr') or '') for line in f if line.strip() for r in [json.loads(line)]}
    flat = [(p, e) for p, entries in index.items() for e in entries]
    sample = random.Random(20261111).sample(flat, min(30, len(flat)))
    checks = [{'parent_orgnr': p, **e, 'snippet_pass': e['observed_orgnr'] in labelled(e['snippet']), 'mapping_pass': (parents.get(e['observed_orgnr']) or e['observed_orgnr']) == p} for p, e in sample]
    assert all(c['snippet_pass'] and c['mapping_pass'] for c in checks)
    assert json.loads(gzip.decompress(target.read_bytes())) == index
    summary = {'build_utc': datetime.now(timezone.utc).isoformat(), 'source_snapshot_bytes': snapshot, 'source_snapshot_sha256': digest.hexdigest(), 'ignored_incomplete_trailing_bytes': trailing, 'records': len(rows), 'crawls': sorted(crawls), 'parent_companies': len(index), 'entries': len(flat), 'distinct_domains': len({e['domain'] for _, e in flat}), 'gzip_bytes': target.stat().st_size, 'index_sha256': hashlib.sha256(target.read_bytes()).hexdigest(), 'excluded_domains': len(banned), 'rejected_missing_label_snippets': rejected_snippets, 'universe_size': len(universe), 'universe_matches': len(universe & index.keys()), 'expected_per_1000': 1000 * len(universe & index.keys()) / len(universe), 'spot_check_seed': 20261111, 'spot_checks': checks}
    (OUT / 'cc_orgnr_index_build.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({k: v for k, v in summary.items() if k != 'spot_checks'}, indent=2))


if __name__ == '__main__':
    main()
