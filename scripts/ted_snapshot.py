"""Build the bundled TED award-notice snapshot offline (Stage U).

Scope: TED contract award notices (notice types can-standard and can-social)
published in the 36-month window before the build date, where TED records a
Norwegian buyer or winner and at least one winner/buyer identifier is a
checksum-valid Norwegian organisation number. Full XML is kept only for notices
naming a company of the declared universe (whitespace-normalised identifier);
the rest are kept as metadata-only records that the runtime fetches live.

Every record keeps the verbatim notice XML so the runtime applies the existing
``award_extract`` acceptance rules to the same bytes a live fetch would return.

Usage (resumable; raw responses are cached under bench/cache/, which is ignored):

    uv run --frozen python scripts/ted_snapshot.py build
    uv run --frozen python scripts/ted_snapshot.py write

``build`` runs the search and fetches XML at most one request per second,
retrying HTTP 202 in later passes. ``write`` packs data/ted-no-notices.jsonl.gz
and data/ted_snapshot_build.json from the cache without network access.
"""
import argparse
import gzip
import hashlib
import json
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor
import time
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from signalpost.identity.orgnr import checksum  # noqa: E402
from signalpost.sources.official_extra import NS, TED, text  # noqa: E402

CACHE = ROOT / 'bench' / 'cache' / 'ted-snapshot'
OUTPUT = ROOT / 'data' / 'ted-no-notices.jsonl.gz'
MANIFEST = ROOT / 'data' / 'ted_snapshot_build.json'
SCHEMA_VERSION = 1
FIELDS = ['publication-number', 'notice-type', 'publication-date', 'winner-identifier',
          'buyer-identifier', 'winner-country', 'buyer-country', 'links']
TYPES = {'can-standard', 'can-social'}
HEADERS = {'User-Agent': 'signalpost-ted-snapshot/1 (offline cache build)'}


def window(today):
    try:
        since = today.replace(year=today.year - 3)
    except ValueError:
        since = today.replace(year=today.year - 3, day=28)
    return since


def query(since, start, end):
    return ('notice-type IN (can-standard can-social) AND (buyer-country = NOR OR winner-country = NOR)'
            f' AND publication-date >= {start:%Y%m%d} AND publication-date < {end:%Y%m%d}')


def norwegian(identifier):
    value = re.sub(r'^NO\s*|\s*MVA$', '', str(identifier), flags=re.I).replace(' ', '')
    return len(value) == 9 and value.isdigit() and checksum(value)


class Polite:
    def __init__(self):
        self.client = httpx.Client(timeout=60, headers=HEADERS, follow_redirects=False)
        self.last = 0.0
        self.calls = 0
        self.statuses = {}
        self.lock = threading.Lock()

    def request(self, method, url, **kw):
        # At most one request *start* per second, whatever the concurrency.
        with self.lock:
            wait = self.last + 1.0 - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self.last = time.monotonic()
            self.calls += 1
        r = self.client.request(method, url, **kw)
        with self.lock:
            self.statuses[str(r.status_code)] = self.statuses.get(str(r.status_code), 0) + 1
        return r


def search(http, since, until):
    """Search in monthly slices so every slice stays well inside page limits."""
    out = CACHE / 'search'
    out.mkdir(parents=True, exist_ok=True)
    start = since
    while start < until:
        end = min((start.replace(day=1) + timedelta(days=32)).replace(day=1), until)
        target = out / f'{start:%Y%m%d}-{end:%Y%m%d}.json'
        if not target.exists():
            q = query(since, start, end)
            notices, page = [], 1
            while True:
                for attempt in range(6):
                    r = http.request('POST', TED, json={'query': q, 'fields': FIELDS, 'limit': 250,
                                                        'page': page, 'scope': 'ALL'})
                    if r.status_code == 200:
                        break
                    time.sleep(5 * (attempt + 1))
                else:
                    raise SystemExit(f'search failed {r.status_code} for {q} page {page}')
                data = r.json()
                if data.get('timedOut'):
                    raise SystemExit(f'search timed out for {q}')
                notices += data['notices']
                if page * 250 >= data['totalNoticeCount']:
                    break
                page += 1
            if len(notices) != data['totalNoticeCount']:
                raise SystemExit(f'count mismatch {len(notices)} != {data["totalNoticeCount"]} for {q}')
            target.write_text(json.dumps({'query': q, 'total': data['totalNoticeCount'], 'notices': notices,
                                          'retrieved_at': datetime.now(timezone.utc).isoformat()}), encoding='utf8')
            print(f'search {start}..{end}: {len(notices)}', flush=True)
        start = end


def candidates():
    seen = {}
    for f in sorted((CACHE / 'search').glob('*.json')):
        for item in json.loads(f.read_text(encoding='utf8'))['notices']:
            if item.get('notice-type') not in TYPES:
                continue
            ids = (item.get('winner-identifier') or []) + (item.get('buyer-identifier') or [])
            if any(norwegian(x) for x in ids):
                seen[item['publication-number']] = item
    return seen


def universe(path):
    """Organisation numbers of the declared company universe (read locally; not redistributed)."""
    out = set()
    with gzip.open(path, 'rt', encoding='utf8') as f:
        for line in f:
            if line.strip():
                out.add(re.sub(r'\D', '', str(json.loads(line)['organisation_number'])))
    return out


def names_universe_company(item, members):
    # Whitespace-only normalisation, the same rule the runtime uses for nomination.
    ids = (item.get('winner-identifier') or []) + (item.get('buyer-identifier') or [])
    return bool(members & {re.sub(r'\s', '', str(x)) for x in ids})


def xml_url(item):
    link = ((item.get('links') or {}).get('xml') or {}).get('MUL')
    return link if isinstance(link, str) and link else f'https://ted.europa.eu/en/notice/{item["publication-number"]}/xml'


def fetch(http, items, passes):
    out = CACHE / 'xml'
    out.mkdir(parents=True, exist_ok=True)
    for n in range(passes):
        pending = [k for k in sorted(items) if not (out / (k + '.json')).exists()]
        print(f'pass {n + 1}: {len(pending)} pending', flush=True)
        if not pending:
            return
        def one(args):
            i, notice = args
            url = xml_url(items[notice])
            try:
                r = http.request('GET', url, headers={'Accept': 'application/xml,text/xml'})
            except httpx.HTTPError as exc:
                print('error', notice, type(exc).__name__, flush=True)
                return
            if r.status_code != 200:
                return
            retrieved = datetime.now(timezone.utc).isoformat()
            (out / (notice + '.xml')).write_bytes(r.content)
            # The metadata file is written last: its presence marks a complete fetch.
            (out / (notice + '.json')).write_text(json.dumps({'url': url, 'retrieved_at': retrieved,
                                                              'sha256': hashlib.sha256(r.content).hexdigest()}), encoding='utf8')
            if i % 200 == 0:
                print(f'  {i}/{len(pending)} statuses={http.statuses}', flush=True)
        with ThreadPoolExecutor(3) as pool:
            list(pool.map(one, enumerate(pending)))
        time.sleep(60)


def awards(body):
    """Informational per-contract summary; the runtime re-applies award_extract to the XML."""
    root = ET.fromstring(body)
    if root.tag.split('}')[-1] != 'ContractAwardNotice':
        return []
    orgs = {}
    for company in root.findall('.//efac:Organizations/efac:Organization/efac:Company', NS):
        orgs[text(company, 'cac:PartyIdentification/cbc:ID')] = text(company, 'cac:PartyLegalEntity/cbc:CompanyID')
    parties = {text(p, 'cbc:ID'): sorted(text(t, 'cbc:ID') for t in p.findall('efac:Tenderer', NS))
               for p in root.findall('.//efac:NoticeResult/efac:TenderingParty', NS)}
    tenders = {}
    for t in root.findall('.//efac:NoticeResult/efac:LotTender', NS):
        amount = t.find('cac:LegalMonetaryTotal/cbc:PayableAmount', NS)
        if amount is None:
            amount = t.find('cbc:PayableAmount', NS)
        party = text(t, 'efac:TenderingParty/cbc:ID')
        tenders[text(t, 'cbc:ID')] = {'lot': text(t, 'efac:TenderLot/cbc:ID'), 'tendering_party': party,
                                      'tenderer_ids': [orgs.get(x) for x in parties.get(party, [])],
                                      'amount': amount.text if amount is not None else None,
                                      'currency': amount.get('currencyID') if amount is not None else None}
    result = []
    for contract in root.findall('.//efac:NoticeResult/efac:SettledContract', NS):
        linked = [text(t, 'cbc:ID') for t in contract.findall('efac:LotTender', NS)]
        result.append({'contract_id': text(contract, 'cbc:ID'), 'award_date': text(contract, 'cbc:AwardDate'),
                       'lot_tenders': [dict(id=x, **tenders[x]) for x in linked if x in tenders]})
    return result


def write(built, members, universe_meta):
    items = candidates()
    records, failed, outside = [], [], []
    for notice in sorted(items):
        meta_path = CACHE / 'xml' / (notice + '.json')
        item = items[notice]
        if not names_universe_company(item, members):
            # Metadata only: an input outside the universe can still be served by a live XML fetch.
            outside.append(notice)
            records.append({'publication_number': notice, 'notice_type': item['notice-type'],
                            'publication_date': item.get('publication-date'),
                            'winner_identifier': item.get('winner-identifier') or [],
                            'buyer_identifier': item.get('buyer-identifier') or [],
                            'winner_country': item.get('winner-country') or [],
                            'buyer_country': item.get('buyer-country') or [],
                            'xml_url': xml_url(item), 'retrieved_at': None, 'content_sha256': None,
                            'awards': [], 'xml': None, 'xml_omitted': 'no_universe_company'})
            continue
        if not meta_path.exists():
            # Kept so the runtime can report affected companies as fetch-failed, not absent.
            failed.append(notice)
            records.append({'publication_number': notice, 'notice_type': item['notice-type'],
                            'publication_date': item.get('publication-date'),
                            'winner_identifier': item.get('winner-identifier') or [],
                            'buyer_identifier': item.get('buyer-identifier') or [],
                            'winner_country': item.get('winner-country') or [],
                            'buyer_country': item.get('buyer-country') or [],
                            'xml_url': xml_url(item), 'retrieved_at': None, 'content_sha256': None,
                            'awards': [], 'xml': None})
            continue
        meta = json.loads(meta_path.read_text(encoding='utf8'))
        body = (CACHE / 'xml' / (notice + '.xml')).read_bytes()
        if hashlib.sha256(body).hexdigest() != meta['sha256']:
            raise SystemExit('cache hash mismatch ' + notice)
        records.append({'publication_number': notice, 'notice_type': item['notice-type'],
                        'publication_date': item.get('publication-date'),
                        'winner_identifier': item.get('winner-identifier') or [],
                        'buyer_identifier': item.get('buyer-identifier') or [],
                        'winner_country': item.get('winner-country') or [],
                        'buyer_country': item.get('buyer-country') or [],
                        'xml_url': meta['url'], 'retrieved_at': meta['retrieved_at'].replace('+00:00', 'Z'),
                        'content_sha256': meta['sha256'], 'awards': awards(body),
                        'xml': body.decode('utf-8')})
    lines = b''.join(json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode('utf8') + b'\n'
                     for r in records)
    packed = gzip.compress(lines, compresslevel=9, mtime=0)
    OUTPUT.write_bytes(packed)
    searches = [json.loads(f.read_text(encoding='utf8')) for f in sorted((CACHE / 'search').glob('*.json'))]
    since = window(built)
    manifest = {'schema_version': SCHEMA_VERSION, 'built_at': built.isoformat(),
                'window': {'since': since.isoformat(), 'until_exclusive': (built + timedelta(days=1)).isoformat()},
                'query_template': query(since, date(1, 1, 1), date(1, 1, 1)).replace('00010101', '<YYYYMMDD>'),
                'query_slices': [s['query'] for s in searches],
                'search_retrieved_at': [min(s['retrieved_at'] for s in searches), max(s['retrieved_at'] for s in searches)],
                'search_total': sum(s['total'] for s in searches),
                'scope_filter': 'notice-type can-standard/can-social and at least one winner/buyer identifier that is a checksum-valid Norwegian organisation number',
                'records': len(records) - len(failed) - len(outside), 'failed_notices': failed,
                'metadata_only_notices': len(outside), 'universe': universe_meta,
                'retrieved_at_range': [min(r['retrieved_at'] for r in records if r['retrieved_at']),
                                       max(r['retrieved_at'] for r in records if r['retrieved_at'])] if any(r['retrieved_at'] for r in records) else None,
                'file': OUTPUT.name, 'file_bytes': len(packed), 'file_sha256': hashlib.sha256(packed).hexdigest(),
                'uncompressed_bytes': len(lines)}
    MANIFEST.write_text(json.dumps(manifest, indent=1) + '\n', encoding='utf8')
    print(json.dumps({k: v for k, v in manifest.items() if k != 'query_slices'}, indent=1))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('step', choices=['build', 'write'])
    p.add_argument('--built', default=None, help='build date (YYYY-MM-DD); default today UTC, fixed in cache')
    p.add_argument('--passes', type=int, default=12)
    p.add_argument('--universe', type=Path, default=ROOT / 'bench/reports/osm-check/raw/universe.jsonl.gz',
                   help='declared company universe JSONL.gz; XML is kept only for notices naming one of its companies')
    a = p.parse_args()
    CACHE.mkdir(parents=True, exist_ok=True)
    stamp = CACHE / 'built.txt'
    if not stamp.exists():
        stamp.write_text(a.built or datetime.now(timezone.utc).date().isoformat())
    built = date.fromisoformat(stamp.read_text().strip())
    members = universe(a.universe)
    universe_meta = {'source': 'https://builderr.ai/signalpost-company-universe-2025.jsonl.gz', 'companies': len(members),
                     'sha256': hashlib.sha256(a.universe.read_bytes()).hexdigest()}
    if a.step == 'build':
        http = Polite()
        search(http, window(built), built + timedelta(days=1))
        items = candidates()
        kept = {k: v for k, v in items.items() if names_universe_company(v, members)}
        print('in scope', len(items), 'naming a universe company', len(kept), flush=True)
        fetch(http, kept, a.passes)
        print('requests', http.calls, http.statuses, flush=True)
    else:
        write(built, members, universe_meta)


if __name__ == '__main__':
    main()
