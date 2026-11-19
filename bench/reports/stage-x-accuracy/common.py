"""Shared helpers for the Stage X accuracy sample and the attribution audit.

Both scripts read only the committed extract in ./extract/ (see extract.py), so they run from
a fresh clone with no bench/runs directory.
"""
import base64, collections, hashlib, lzma, json, math, random, re
from pathlib import Path
from urllib.parse import unquote

HERE = Path(__file__).resolve().parent
EXTRACT = HERE / 'extract'
SEED = 20261119
SIZE = 200


def family(field):
    p = field.split('.')[0]
    if field.startswith('identity.gleif'):
        return 'gleif'
    return {'identity': 'identity', 'roles': 'roles', 'subunits': 'subunits', 'accounts': 'accounts',
            'registry_change': 'activity', 'dated_item': 'activity', 'procurement_award': 'ted',
            'official_website': 'website', 'contact': 'website', 'website_description': 'website',
            'social_profile': 'social', 'registry_social': 'social', 'public_brand': 'brands',
            'hiring': 'hiring', 'group': 'group'}.get(p, 'other:' + p)


def published(c):
    return c.get('availability') == 'available' and not c['field'].endswith('.section')


def read_envelopes(path=EXTRACT / 'envelopes.jsonl.xz'):
    with lzma.open(path, 'rt', encoding='utf-8') as fh:
        for line in fh:
            yield json.loads(line)


def read_blobs(path=EXTRACT / 'blobs.jsonl.xz'):
    """sha256 -> bytes. Each blob's hash is recomputed, so a corrupted extract fails loudly."""
    out = {}
    with lzma.open(path, 'rt', encoding='utf-8') as fh:
        for line in fh:
            row = json.loads(line); body = base64.b64decode(row['b64'])
            if hashlib.sha256(body).hexdigest() != row['sha256']:
                raise SystemExit(f"blob hash mismatch: {row['sha256']}")
            out[row['sha256']] = body
    return out


def population(rows):
    pop = collections.defaultdict(list)
    for r in rows:
        org = r['organisation_number']
        for c in r['claims']:
            if published(c):
                pop[family(c['field'])].append((org, c['field'], c['id'], 'claim'))
        for sec, sentences in r['synthesis'].items():
            for i, s in enumerate(sentences):
                pop['synthesis'].append((org, f'synthesis.{sec}.{i}', s['text'][:40], 'sentence'))
    return pop


def allocate(pop):
    fams = sorted(pop); total = sum(len(pop[f]) for f in fams)
    alloc = {f: 1 for f in fams}; rest = SIZE - len(fams)
    quota = {f: rest * len(pop[f]) / total for f in fams}
    for f in fams:
        alloc[f] += int(quota[f])
    for f in sorted(fams, key=lambda f: -(quota[f] - int(quota[f])))[:SIZE - sum(alloc.values())]:
        alloc[f] += 1
    return alloc


def draw(pop, alloc):
    rng = random.Random(SEED); picked = []
    for f in sorted(pop):
        picked += [(f,) + x for x in rng.sample(sorted(pop[f]), alloc[f])]
    return picked


def pointer(doc, loc):
    for part in [unquote(x).replace('~1', '/').replace('~0', '~') for x in loc.split('/')[1:]]:
        doc = doc[int(part)] if isinstance(doc, list) else doc[part]
    return doc


def mechanical(org, c, ev, blobs):
    from signalpost.sources.text import decode_body
    cited = [ev[i] for i in c['evidence_ids'] if i in ev]
    if not cited:
        return {'evidence_found': False, 'note': 'no resolvable evidence'}
    e = cited[0]; out = {'evidence_found': True}
    body = blobs.get(e['content_sha256'], b'')
    out['blob_present'] = bool(body)
    text = decode_body(body) if body else ''
    out['span_in_body'] = bool(e.get('claim_span')) and e['claim_span'] in text
    out['org_in_source_url'] = org in e['source_url'] or org in unquote(e['source_url'])
    if body[:1] in (b'{', b'[') and (e.get('locator') or '').startswith('/'):
        try:
            at = pointer(json.loads(body), e['locator'])
            out['value_at_locator'] = at if len(json.dumps(at, ensure_ascii=False)) < 600 else '(large)'
            out['org_in_located_record'] = org in json.dumps(at, ensure_ascii=False)
        except Exception as exc:
            out['locator_error'] = type(exc).__name__
    return out


def build_items(picked, rows_by_org, blobs):
    items = []
    for f, org, field, ident, kind in picked:
        r = rows_by_org[org]; ev = {x['id']: x for x in r['evidence']}
        item = {'family': f, 'orgnr': org, 'legal_name': r['legal_name'], 'field': field}
        if kind == 'claim':
            c = next(x for x in r['claims'] if x['id'] == ident)
            e = ev.get(c['evidence_ids'][0]) if c['evidence_ids'] else None
            item.update(value=c['value'],
                        evidence={k: e.get(k) for k in ('source_url', 'locator', 'claim_span', 'content_sha256')} if e else None,
                        check=mechanical(org, c, ev, blobs))
        else:
            sec, i = field.split('.')[1], int(field.split('.')[2])
            s = r['synthesis'][sec][i]
            byid = {x['id']: x for x in r['claims']} | {x['id']: x for x in r.get('change_claims', [])}
            item.update(value=s['text'],
                        cited_claims=[{'field': byid[k]['field'], 'value': byid[k]['value']} if k in byid else {'unresolved': k}
                                      for k in s.get('claim_ids', [])])
        items.append(item)
    return items


def wilson_lower(k, n, z=1.959963984540054):
    if n == 0:
        return 0.0
    p = k / n; d = 1 + z * z / n
    return (p + z * z / (2 * n) - z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))) / d
