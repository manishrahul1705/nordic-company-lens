"""Replay new BRREG scalar claims from saved proof blobs; no network client."""
import collections
import json
from pathlib import Path

from signalpost.sources import brreg_enhet, brreg_roller, brreg_underenheter, regnskap
from signalpost.sources.extract import Section, Source
from signalpost.sources.http import Response
from stage_ay_field_inventory import ROOT, JURY, OUT, family


def wanted(claim):
    field = claim.field
    return (field.startswith(('identity.business_address.', 'identity.postal_address.',
                               'identity.organisation_form.', 'identity.industry',
                               'identity.institutional_sector.', 'identity.support_unit_code.',
                               'identity.registered_capital.', 'roles.group.',
                               'subunits.detail.')) or
            (field.startswith('roles.detail.') and field.rsplit('.',1)[-1].startswith(
                ('role_type_', 'holder_', 'holder_form_', 'elected_by_')) or
                field.startswith('roles.detail.') and field.endswith(('.inactive','.from_date'))) or
            (field.startswith('accounts.statement.') or field.startswith('accounts.consolidated.'))
            and field.endswith(('.filing_id', '.journal_number')))


def replay(name, source, blob_dir, allowed=None):
    target = OUT / f'{name}-envelopes.jsonl'
    before = collections.Counter()
    added = collections.Counter()
    examples = []
    rows = 0
    seen_orgs = set()
    with source.open(encoding='utf-8-sig') as inp, target.open('w', encoding='utf8') as out:
        for line in inp:
            row = json.loads(line)
            org = row['organisation_number']
            if allowed is not None and org not in allowed:
                continue
            if org in seen_orgs:
                continue
            seen_orgs.add(org)
            rows += 1
            before.update(c['family'] for c in row['claims'] if c['availability'] == 'available')
            existing_ids = {c['id'] for c in row['claims']}
            evidence = {e['id']: e for e in row['evidence']}
            existing_locators = {(e['content_sha256'], e['locator']) for e in evidence.values()}
            responses = {}
            for e in evidence.values():
                fam = family(e['source_url'])
                if fam and e.get('content_sha256'):
                    responses.setdefault((fam, e['content_sha256']), e)
            for (fam, sha), e in responses.items():
                body = (blob_dir / sha).read_bytes()
                url, stamp = e['source_url'], e['retrieved_at']
                if fam == 'identity':
                    section = brreg_enhet.extract(org, json.loads(body), Source(url, body, sha, stamp))
                else:
                    response = Response(body, 200, url, stamp, sha)
                    if fam == 'roles':
                        section = brreg_roller.extract(org, response)
                    elif fam == 'accounts':
                        section = regnskap.extract(org, response, None)
                    else:
                        section = Section()
                        from urllib.parse import parse_qs, urlsplit
                        page = int(parse_qs(urlsplit(url).query).get('page', ['0'])[0])
                        brreg_underenheter.extract_page(org, response, section, page)
                generated_evidence = {x.id: x for x in section.evidence}
                for claim in section.claims:
                    if not wanted(claim) or claim.availability != 'available' or claim.id in existing_ids:
                        continue
                    cited = [generated_evidence[x] for x in claim.evidence_ids]
                    if any((x.content_sha256, x.locator) in existing_locators for x in cited):
                        continue
                    row['claims'].append(claim.model_dump(mode='json'))
                    existing_ids.add(claim.id)
                    for item in cited:
                        if item.id not in evidence:
                            raw = item.model_dump(mode='json')
                            row['evidence'].append(raw)
                            evidence[item.id] = raw
                        existing_locators.add((item.content_sha256, item.locator))
                    added[claim.family] += 1
                    if len(examples) < 60:
                        examples.append({'orgnr': org, 'field': claim.field, 'value': claim.value,
                                         'locator': cited[0].locator, 'sha': sha, 'source_url': url,
                                         'claim_span': cited[0].claim_span, 'reporting_period': claim.reporting_period})
            out.write(json.dumps(row, ensure_ascii=False, separators=(',', ':')) + '\n')
    return {'rows': rows, 'before': dict(before), 'new': dict(added),
            'after': {k: before[k] + added[k] for k in before | added},
            'examples': examples, 'output': str(target), 'http_requests': 0}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    allowed = set(json.loads((JURY / 'jury-sample.json').read_text(encoding='utf8'))['active'][:100])
    result = {
        'jury100': replay('jury100', JURY / 'jury-first-envelopes.jsonl', JURY / 'out/state/blobs', allowed),
        'final1000': replay('final1000', ROOT / 'bench/runs/final-20261120/envelopes.jsonl',
                            ROOT / 'bench/runs/final-20261120/state/blobs'),
    }
    # The saved synthesis uses the original mixed 316-row cohort. Preserve
    # that full membership for the strict cross-company verification gate.
    updated = {x['organisation_number']: x for x in map(json.loads,
        (OUT / 'jury100-envelopes.jsonl').open(encoding='utf8'))}
    with (JURY / 'jury-first-envelopes.jsonl').open(encoding='utf8') as source, \
            (OUT / 'jury316-envelopes.jsonl').open('w', encoding='utf8') as target:
        for line in source:
            original = json.loads(line)
            target.write(json.dumps(updated.get(original['organisation_number'], original),
                                    ensure_ascii=False, separators=(',', ':')) + '\n')
    (OUT / 'replay.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    for name, data in result.items():
        print(name, data['rows'], data['before'], data['new'], data['after'])


if __name__ == '__main__':
    main()
