"""Stage X accuracy sample: stratified random sample of published claims + mechanical evidence check.

Usage: python bench/reports/stage-x-accuracy/sample_and_check.py [run_dir]
Writes sample.jsonl (one item per sampled claim, with the cited evidence and the mechanical
check). Verdicts are recorded separately in verdicts.jsonl after hand review.

Population: every published claim (availability == 'available', excluding '*.section'
placeholders) in the run, plus every synthesis sentence (family 'synthesis').
Families: identity (excl. GLEIF), gleif (identity.gleif.*), roles, subunits, accounts,
activity (registry_change, dated_item), ted (procurement_award), website (official_website,
contact, website_description), social (social_profile, registry_social), brands
(public_brand), hiring, synthesis.
Allocation: 1 per family, the remaining 200-12 by largest remainder in proportion to family
size. Within a family: random.Random(SEED).sample over items sorted by (orgnr, field, id).
"""
import collections, json, random, re, sys
from pathlib import Path
from urllib.parse import unquote

SEED = 20261119
SIZE = 200
ROOT = Path(__file__).resolve().parents[3]
RUN = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'bench/runs/final-frozen-20261118'
OUT = Path(__file__).resolve().parent


def family(c):
    f = c['field']; p = f.split('.')[0]
    if f.startswith('identity.gleif'): return 'gleif'
    return {'identity': 'identity', 'roles': 'roles', 'subunits': 'subunits', 'accounts': 'accounts',
            'registry_change': 'activity', 'dated_item': 'activity', 'procurement_award': 'ted',
            'official_website': 'website', 'contact': 'website', 'website_description': 'website',
            'social_profile': 'social', 'registry_social': 'social', 'public_brand': 'brands',
            'hiring': 'hiring'}.get(p, 'other:' + p)


def pointer(doc, loc):
    for part in [unquote(x).replace('~1', '/').replace('~0', '~') for x in loc.split('/')[1:]]:
        doc = doc[int(part)] if isinstance(doc, list) else doc[part]
    return doc


def norm(v):
    return re.sub(r'\s+', ' ', json.dumps(v, ensure_ascii=False, sort_keys=True)).casefold() if not isinstance(v, str) else re.sub(r'\s+', ' ', v).casefold()


def mechanical(c, row, ev, blobs):
    """Value-at-locator / span-in-bytes and org attribution checks. Returns dict of findings."""
    org = row['organisation_number']; out = {'evidence_found': False}
    cited = [ev[i] for i in c['evidence_ids'] if i in ev]
    if not cited: return {'evidence_found': False, 'note': 'no resolvable evidence'}
    e = cited[0]; out['evidence_found'] = True
    path = blobs / e['content_sha256']
    body = path.read_bytes() if path.exists() else b''
    out['blob_present'] = bool(body)
    from signalpost.sources.text import decode_body
    text = decode_body(body) if body else ''
    out['span_in_body'] = bool(e.get('claim_span')) and e['claim_span'] in text
    out['org_in_source_url'] = org in e['source_url'] or org in unquote(e['source_url'])
    if body[:1] in (b'{', b'[') and e['locator'].startswith('/'):
        try:
            doc = json.loads(body); at = pointer(doc, e['locator'])
            out['value_at_locator'] = at if len(json.dumps(at, ensure_ascii=False)) < 600 else '(large)'
            out['org_in_located_record'] = org in json.dumps(at, ensure_ascii=False)
        except Exception as exc:
            out['locator_error'] = type(exc).__name__
    return out


def main():
    blobs = RUN / 'state' / 'blobs'
    pop = collections.defaultdict(list)
    rows = {}
    for line in open(RUN / 'envelopes.jsonl', encoding='utf-8-sig'):
        r = json.loads(line); org = r['organisation_number']; rows[org] = r
        for c in r['claims']:
            if c['availability'] == 'available' and not c['field'].endswith('.section'):
                pop[family(c)].append((org, c['field'], c['id'], 'claim'))
        for sec, sentences in r['run']['synthesis']['sections'].items():
            for i, s in enumerate(sentences):
                pop['synthesis'].append((org, f'synthesis.{sec}.{i}', s['text'][:40], 'sentence'))
    fams = sorted(pop); total = sum(len(pop[f]) for f in fams)
    alloc = {f: 1 for f in fams}; rest = SIZE - len(fams)
    quota = {f: rest * len(pop[f]) / total for f in fams}
    for f in fams: alloc[f] += int(quota[f])
    for f in sorted(fams, key=lambda f: -(quota[f] - int(quota[f])))[:SIZE - sum(alloc.values())]: alloc[f] += 1
    rng = random.Random(SEED); items = []
    for f in fams:
        for org, field, ident, kind in rng.sample(sorted(pop[f]), alloc[f]):
            r = rows[org]; ev = {x['id']: x for x in r['evidence']}
            item = {'family': f, 'orgnr': org, 'legal_name': r['run']['legal_identity'].get('legal_name'), 'field': field}
            if kind == 'claim':
                c = next(x for x in r['claims'] if x['id'] == ident)
                e = ev.get(c['evidence_ids'][0]) if c['evidence_ids'] else None
                item.update(value=c['value'], evidence={k: e.get(k) for k in ('source_url', 'locator', 'claim_span', 'content_sha256')} if e else None,
                            check=mechanical(c, r, ev, blobs))
            else:
                sec, i = field.split('.')[1], int(field.split('.')[2])
                s = r['run']['synthesis']['sections'][sec][i]
                byid = {x['id']: x for x in r['claims']} | {x['id']: x for x in r['run']['synthesis'].get('change_claims', [])}
                item.update(value=s['text'], cited_claims=[{'field': byid[i]['field'], 'value': byid[i]['value']} if i in byid else {'unresolved': i} for i in s.get('claim_ids', [])], sentence_keys=sorted(s))
            items.append(item)
    with open(OUT / 'sample.jsonl', 'w', encoding='utf-8') as fh:
        for it in items: fh.write(json.dumps(it, ensure_ascii=False, default=str) + '\n')
    (OUT / 'population.json').write_text(json.dumps({'seed': SEED, 'size': SIZE, 'run': str(RUN.relative_to(ROOT)), 'population': {f: len(pop[f]) for f in fams}, 'allocation': alloc}, indent=1) + '\n', encoding='utf-8')
    print(json.dumps({'population': {f: len(pop[f]) for f in fams}, 'allocation': alloc}, indent=1))


if __name__ == '__main__':
    main()
