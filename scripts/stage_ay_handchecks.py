"""Deterministic source-level checks across newly replayed registry fields."""
import collections
import hashlib
import json
from pathlib import Path
from stage_ay_field_inventory import JURY, OUT


def at(data, locator):
    for part in locator.strip('/').split('/'):
        part = part.replace('~1', '/').replace('~0', '~')
        data = data[int(part)] if isinstance(data, list) else data[part]
    return data


def main():
    original = {x['organisation_number']: x for x in map(json.loads,
        (JURY / 'jury-first-envelopes.jsonl').open(encoding='utf8'))}
    checks = collections.defaultdict(list)
    for row in map(json.loads, (OUT / 'jury100-envelopes.jsonl').open(encoding='utf8')):
        prior = {c['id'] for c in original[row['organisation_number']]['claims']}
        ev = {e['id']: e for e in row['evidence']}
        for claim in row['claims']:
            if claim['id'] in prior or claim['family'] not in {'identity', 'roles', 'accounts', 'subunits'}:
                continue
            proof = ev[claim['evidence_ids'][0]]
            body = (JURY / 'out/state/blobs' / proof['content_sha256']).read_bytes()
            raw = at(json.loads(body), proof['locator'])
            assert hashlib.sha256(body).hexdigest() == proof['content_sha256']
            assert raw == claim['value'], (claim['field'], raw, claim['value'])
            assert proof['claim_span'] in body.decode('utf8', errors='replace')
            checks[claim['family']].append({'orgnr': row['organisation_number'],
                'field': claim['field'], 'value': claim['value'], 'locator': proof['locator'],
                'sha': proof['content_sha256'], 'source_url': proof['source_url'],
                'period': claim['reporting_period'], 'result': 'exact JSON value, SHA and verbatim span verified'})
    selected = []
    requested = {
        'identity': ['business_address.postal_code','industry1.kode','institutional_sector.kode','registered_capital.belop'],
        'roles': ['group.0.type_kode','role_type_kode','holder_organisasjonsnummer','holder_form_kode'],
        'accounts': ['filing_id','journal_number','filing_id'],
        'subunits': ['beliggenhetsadresse.postnummer','naeringskode1.kode','naeringskode2.kode','employees'],
    }
    for family, suffixes in requested.items():
        seen_orgs = set()
        for suffix in suffixes:
            item = next((x for x in checks[family] if x['field'].endswith(suffix) and x['orgnr'] not in seen_orgs), None)
            assert item is not None, (family,suffix)
            selected.append(item);seen_orgs.add(item['orgnr'])
    (OUT / 'handchecks.json').write_text(json.dumps(selected, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({'checks': len(selected), 'families': dict(collections.Counter(x['field'].split('.')[0] for x in selected))}))


if __name__ == '__main__':
    main()
