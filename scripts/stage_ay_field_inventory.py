"""Offline inventory of saved BRREG JSON leaves versus exact claim locators."""
import collections
import json
import re
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
JURY = Path('C:/Users/Manish/Downloads/jury-audit')
OUT = ROOT / 'bench/reports/stage-ay'


def family(url):
    path = urlsplit(url).path
    if re.fullmatch(r'/enhetsregisteret/api/enheter/\d{9}', path):
        return 'identity'
    if re.fullmatch(r'/enhetsregisteret/api/enheter/\d{9}/roller', path):
        return 'roles'
    if path == '/enhetsregisteret/api/underenheter':
        return 'subunits'
    if re.fullmatch(r'/regnskapsregisteret/regnskap/\d{9}', path):
        return 'accounts'
    return None


def leaves(value, path=''):
    if isinstance(value, dict):
        if not value:
            yield path, value
        for key, item in value.items():
            yield from leaves(item, path + '/' + key.replace('~', '~0').replace('/', '~1'))
    elif isinstance(value, list):
        if not value:
            yield path, value
        for index, item in enumerate(value):
            yield from leaves(item, path + '/' + str(index))
    else:
        yield path, value


def pattern(path):
    return re.sub(r'/\d+(?=/|$)', '/*', path)


def scan(name, envelopes, blobs, allowed=None):
    found = collections.defaultdict(lambda: collections.defaultdict(lambda: [set(), set(), set()]))
    counted = collections.Counter()
    for line in envelopes.open(encoding='utf-8-sig'):
        row = json.loads(line)
        org = row['organisation_number']
        if allowed is not None and org not in allowed:
            continue
        evidences = {e['id']: e for e in row['evidence']}
        by_sha = {}
        for e in evidences.values():
            fam = family(e['source_url'])
            if fam and e.get('content_sha256'):
                by_sha.setdefault(e['content_sha256'], (fam, e['source_url']))
        cited = collections.defaultdict(set)
        for claim in row['claims']:
            if claim['availability'] != 'available':
                continue
            for eid in claim['evidence_ids']:
                e = evidences.get(eid)
                if e and e.get('content_sha256') in by_sha:
                    cited[e['content_sha256']].add(e['locator'])
        for sha, (fam, url) in by_sha.items():
            path = blobs / sha
            if not path.exists():
                raise FileNotFoundError(path)
            data = json.loads(path.read_bytes())
            counted[fam] += 1
            locators = cited[sha]
            for loc, val in leaves(data):
                pat = pattern(loc)
                rec = found[fam][pat]
                rec[0].add(org)
                if loc in locators:
                    rec[1].add(org)
                if any(loc.startswith(x.rstrip('/') + '/') for x in locators if x):
                    rec[2].add(org)
    return {'responses': dict(counted), 'paths': {
        fam: {pat: {'present_companies': len(rec[0]), 'exact_claim_companies': len(rec[1]),
                    'inside_composite_claim_companies': len(rec[2])}
              for pat, rec in sorted(paths.items())}
        for fam, paths in found.items()}}


def main():
    allowed = set(json.loads((JURY / 'jury-sample.json').read_text(encoding='utf8'))['active'][:100])
    cohorts = {
        'jury100': (JURY / 'jury-first-envelopes.jsonl', JURY / 'out/state/blobs', allowed),
        'final1000': (ROOT / 'bench/runs/final-20261120/envelopes.jsonl',
                      ROOT / 'bench/runs/final-20261120/state/blobs', None),
    }
    result = {name: scan(name, *args) for name, args in cohorts.items()}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'field-inventory.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    for name, data in result.items():
        print(name, data['responses'])
        for fam, paths in data['paths'].items():
            missing = [(path, v['present_companies']) for path, v in paths.items() if not v['exact_claim_companies']]
            print(' ', fam, 'paths', len(paths), 'never exact', len(missing), 'examples', missing[:10])


if __name__ == '__main__':
    main()
