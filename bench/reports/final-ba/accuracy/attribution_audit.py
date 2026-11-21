"""Cross-company attribution audit, rerunnable from the committed extract (no bench/runs).

Usage: uv run python bench/reports/stage-x-accuracy/attribution_audit.py [--write]

Checks every envelope in extract/envelopes.jsonl.xz:
  1. dangling: a published claim cites an evidence id missing from its own envelope;
  2. registry_mismatch: an entity-specific registry URL (/enheter/{n}, /regnskap/{n}) names a
     number other than the envelope's own;
  3. page_reuse: a company-owned page (any host other than the official APIs) or its content hash
     is cited by more than one envelope;
  4. foreign_label: an evidence span labels an organisation number ("org.nr 123 456 789") that is
     neither the envelope's own nor one its own claims publish (subunits, role-holding entities,
     group parents).
Without --write it exits non-zero unless the counts equal the committed attribution.json.
"""
import collections, json, re, sys
from pathlib import Path
from urllib.parse import urlsplit
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as C

OFFICIAL = {'data.brreg.no', 'api.gleif.org', 'api.ted.europa.eu', 'ted.europa.eu', 'query.wikidata.org',
            'www.wikidata.org', 'pam-stilling-feed.nav.no', 'arbeidsplassen.nav.no'}
REG = re.compile(r'/(?:enheter|regnskap)/(\d{9})(?:[/?#]|$)')
LABEL = re.compile(r'(?i)\borg(?:anisasjons)?\.?\s*-?\s*n(?:umme)?r\.?\s*:?\s*(?:NO\s*)?(\d{3}\s?\d{3}\s?\d{3})(?:\s*MVA)?\b')
NINE = re.compile(r'(?<!\d)\d{9}(?!\d)')


def main():
    write = '--write' in sys.argv
    dangling = mismatch = foreign = 0; examples = collections.defaultdict(list)
    page_users = collections.defaultdict(set); hash_users = collections.defaultdict(set)
    n = claims = evidence = 0
    for r in C.read_envelopes():
        n += 1; org = r['organisation_number']; ev = {e['id']: e for e in r['evidence']}
        claims += len(r['claims']); evidence += len(ev)
        own = {org} | {m for c in r['claims'] for m in NINE.findall(json.dumps(c['value'], ensure_ascii=False))}
        for c in r['claims']:
            for i in c['evidence_ids']:
                if i not in ev:
                    dangling += 1; examples['dangling'].append([org, c['field'], i])
        for e in ev.values():
            url = e['source_url'] or ''; host = (urlsplit(url).hostname or '').lower()
            for m in REG.findall(url):
                if m != org:
                    mismatch += 1; examples['registry_mismatch'].append([org, url])
            if host and host not in OFFICIAL:
                page_users[url].add(org)
                if e.get('content_sha256'):
                    hash_users[e['content_sha256']].add(org)
            for m in LABEL.findall(e.get('claim_span') or ''):
                m = re.sub(r'\s', '', m)
                if m not in own:
                    foreign += 1; examples['foreign_label'].append([org, url, m])
    reuse_url = {u: sorted(s) for u, s in page_users.items() if len(s) > 1}
    reuse_hash = {h: sorted(s) for h, s in hash_users.items() if len(s) > 1}
    got = {'envelopes': n, 'published_claims': claims, 'cited_evidence_records': evidence,
           'dangling': dangling, 'registry_mismatch': mismatch,
           'page_url_reused_across_envelopes': len(reuse_url), 'page_hash_reused_across_envelopes': len(reuse_hash),
           'foreign_label': foreign,
           'examples': {k: v[:20] for k, v in sorted(examples.items())} | {'page_url_reuse': dict(list(sorted(reuse_url.items()))[:20]),
                                                                          'page_hash_reuse': dict(list(sorted(reuse_hash.items()))[:20])}}
    path = C.HERE / 'attribution.json'
    if write:
        path.write_text(json.dumps(got, indent=1, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in got.items() if k != 'examples'}))
    if not write:
        if json.loads(path.read_text(encoding='utf-8')) != got:
            print('FAIL: counts differ from committed attribution.json'); sys.exit(1)
        print('OK: attribution audit reproduced from committed data')


if __name__ == '__main__':
    main()
