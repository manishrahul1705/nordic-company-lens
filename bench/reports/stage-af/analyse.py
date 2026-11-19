"""Independent accounting and source-pointer audit of the saved live benchmark."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

run = Path('bench/runs/stage-af-final-20261119')
out = Path(__file__).parent
report = json.loads((run/'report.json').read_text(encoding='utf-8'))
measurement = json.loads((run/'measurement.json').read_text(encoding='utf-8'))
if measurement['projection_exceeds_user_stop_threshold']:
    raise SystemExit('STOP: 1,100-company projection exceeds 3,000 seconds; do not continue without the user')
events = report['request_log']
groups = {}
rows = set()
claims = defaultdict(list)
states = defaultdict(Counter)
source_hashes = set()
existing_coverage = Counter()
existing_claim_counts = Counter()
diagnostics = []

def pointer(data, path):
    if path == '/':
        return data
    for key in path.split('/')[1:]:
        key = key.replace('~1', '/').replace('~0', '~')
        data = data[int(key)] if isinstance(data, list) else data[key]
    return data

def subset(value, raw):
    if isinstance(value, dict):
        return isinstance(raw, dict) and all(key in raw and subset(item, raw[key]) for key, item in value.items())
    if isinstance(value, list):
        return isinstance(raw, list) and len(value) == len(raw) and all(subset(a, b) for a, b in zip(value, raw))
    return value == raw

def without_personal_identifiers(raw):
    if isinstance(raw, dict):
        return {key:without_personal_identifiers(value) for key,value in raw.items()
                if key not in {'fodselsdato', 'fodselsnummer', 'dNummer'}}
    if isinstance(raw, list):
        return [without_personal_identifiers(value) for value in raw]
    return raw

def body(e):
    raw = (run/'state'/'blobs'/e['content_sha256']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == e['content_sha256']
    source_hashes.add(e['content_sha256'])
    return json.loads(raw)

with (run/'envelopes.jsonl').open(encoding='utf-8') as stream:
    for line in stream:
        row = json.loads(line)
        org = row['organisation_number']
        rows.add(org)
        groups[org] = any(c['field'] == 'identity.part_of_group' and c['value'] is True and c['availability'] == 'available' for c in row['claims'])
        for kind, state in row['run']['refresh'].get('brreg_extended', {}).items():
            states[kind][(state['state'], state.get('reason'))] += 1
        evidence = {e['id']: e for e in row['evidence']}
        company = next(c['value'] for c in row['claims'] if c['field'] == 'identity.legal_name')
        exceptions = [e for e in row['errors'] if e['code'] in {'section_exception','company_exception','deadline'}]
        failed = {kind:state for kind,state in row['run']['refresh'].get('brreg_extended',{}).items()
                  if state['state'] == 'not_available_fetch_failed'}
        if exceptions or failed:
            diagnostics.append({'organisation_number':org, 'company':company, 'errors':exceptions, 'new_source_failures':failed})
        for label, prefix in (('websites', 'official_website'), ('hiring', 'hiring.'), ('ted_awards', 'procurement_award.')):
            published = sum(c['availability'] == 'available' and c['field'].startswith(prefix) for c in row['claims'])
            existing_claim_counts[label] += published
            if published:
                existing_coverage[label] += 1
        for claim in row['claims']:
            field = claim['field']
            kind = ('group_structure' if field.startswith('identity.group_structure.') else
                    'signatur' if field == 'roles.signatur.registered_basis' else
                    'prokura' if field == 'roles.prokura.registered_basis' else None)
            if not kind or claim['availability'] != 'available':
                continue
            assert not claim['carried_forward']
            e = evidence[claim['evidence_ids'][0]]
            data = body(e)
            raw = pointer(data, e['locator'])
            assert subset(claim['value'], raw), (org, field, 'value not stated at cited pointer')
            if kind == 'group_structure':
                assert groups[org]
                assert e['source_url'] == f'https://data.brreg.no/enhetsregisteret/api/konsernstruktur/{org}'
                pending = [data]
                own = []
                while pending:
                    node = pending.pop()
                    if str(node.get('organisasjonsnummer')) == org:
                        own.append(node)
                    pending.extend(node.get('children', []))
                assert len(own) == 1
                source_identity = {'organisation_number':str(own[0]['organisasjonsnummer']), 'name':own[0].get('navn')}
                if field.endswith('.parent'):
                    assert str(raw['organisasjonsnummer']) == org
                    assert str(raw['parentOrganisasjonsnummer']) != org
                else:
                    assert str(raw['parentOrganisasjonsnummer']) == org
                    assert str(raw['organisasjonsnummer']) != org
            else:
                assert str(data['enhet']['organisasjonsnummer']) == org
                source_identity = {'organisation_number':str(data['enhet']['organisasjonsnummer']), 'name':data['enhet'].get('navn')}
                assert e['source_url'] == f'https://data.brreg.no/fullmakt/enheter/{org}/{kind}'
                assert e['locator'] == '/signeringsGrunnlag/signaturProkuraRoller'
                assert claim['value'] == without_personal_identifiers(raw), 'Registered wording or conditions omitted'
                assert not any(key in json.dumps(claim['value']) for key in ('fodselsdato', 'fodselsnummer', 'dNummer'))
            claims[kind].append({'organisation_number': org, 'company': company, 'field': field,
                                 'claim_id': claim['id'], 'value': claim['value'], 'evidence': e,
                                 'source_identity':source_identity,
                                 'source_node': {k:v for k,v in raw.items() if k != 'children'} if kind == 'group_structure' else claim['value']})

request_counts = Counter()
request_status = defaultdict(Counter)
attempted = defaultdict(set)
latencies = defaultdict(list)
for event in events:
    url = event['url']
    kind = ('group_structure' if '/api/konsernstruktur/' in url else
            url.rsplit('/', 1)[-1] if '/fullmakt/enheter/' in url else None)
    if kind:
        org = event['organisation_number']
        if kind == 'group_structure':
            assert groups[org], ('group requested without flag', org)
        request_counts[kind] += 1
        request_status[kind][str(event['status'])] += 1
        attempted[kind].add(org)
        latencies[kind].append(event.get('runtime_ms', 0)/1000)
assert attempted['signatur'] == attempted['prokura'] == set(rows), 'Both mandate endpoints must be attempted for all inputs'
assert attempted['group_structure'] == {org for org, flag in groups.items() if flag}, 'Group gate must be exact'
by_company = Counter(e['organisation_number'] for e in events if e['organisation_number'] in rows)
assert max(by_company.values()) <= 40
assert len(events) <= 19 * len(rows)
counts = {kind: {'companies': len({c['organisation_number'] for c in values}), 'claims': len(values)} for kind, values in claims.items()}
group_edges = {label: {'companies':len({c['organisation_number'] for c in claims['group_structure'] if token in c['field']}),
                       'claims':sum(token in c['field'] for c in claims['group_structure'])}
               for label,token in (('parents','.parent'),('subsidiaries','.subsidiary.'))}
summary = {
    'companies': len(rows), 'coverage': counts, 'group_edges':group_edges,
    'requests': len(events), 'pooled_cap': 19*len(rows), 'pooled_percent': round(100*len(events)/(19*len(rows)), 3),
    'max_attributed_requests_per_company': max(by_company.values()),
    'companies_at_cap': sum(n == 40 for n in by_company.values()),
    'new_endpoint_requests': dict(request_counts),
    'new_endpoint_companies_attempted': {k:len(v) for k,v in attempted.items()},
    'new_endpoint_http_statuses': {k:dict(v) for k,v in request_status.items()},
    'new_endpoint_request_seconds_sum_not_wall': {k:round(sum(v),3) for k,v in latencies.items()},
    'new_endpoint_states': {k:[{'state':s, 'reason':r, 'companies':n} for (s,r),n in v.items()] for k,v in states.items()},
    'wall_seconds': measurement['wall_seconds'], 'baseline_wall_seconds': 1744.427,
    'delta_wall_seconds': round(measurement['wall_seconds'] - 1744.427,3),
    'projected_1100': {'wall_seconds': measurement['projection_1100_seconds'],
                       'requests': round(len(events)*1.1,1), 'pooled_cap':20900,
                       'pooled_percent': round(100*len(events)/19000,3)},
    'finalisation': report['finalisation'], 'site': report.get('site'),
    'deadline_hits': report['deadline_hits'], 'handled_exceptions':report['handled_exceptions'],
    'unhandled_exceptions':report['unhandled_exceptions'], 'warnings':report['warnings'],
    'new_claim_source_hashes_verified':len(source_hashes), 'new_claim_source_pointer_audit_passed': True,
    'source_unchanged_during_run':measurement['source_unchanged']}
baseline = json.loads(Path('bench/runs/ted-budget-network-20261119/report.json').read_text(encoding='utf-8'))
summary['baseline_requests'] = baseline['requests']
summary['baseline_pooled_percent'] = round(baseline['requests']/190, 3)
summary['baseline_finalisation'] = baseline['finalisation']
summary['existing_coverage_companies'] = dict(existing_coverage)
summary['ted_awards_published'] = existing_claim_counts['ted_awards']
summary['ted_award_companies'] = existing_coverage['ted_awards']
(out/'measurement.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False),encoding='utf-8')
(out/'diagnostics.json').write_text(json.dumps(diagnostics, indent=2, ensure_ascii=False),encoding='utf-8')
# Candidate samples are not labelled reviewed by this script. The human review
# records are completed after reading the company, complete value and source node.
samples = {}
for kind, values in claims.items():
    selected = []
    seen = set()
    pools = ([c for c in values if c['field'].endswith('.parent')],
             [c for c in values if '.subsidiary.' in c['field']]) if kind == 'group_structure' else (values,)
    for pool in pools:
        for candidate in pool:
            if candidate['organisation_number'] in seen:
                continue
            selected.append(candidate); seen.add(candidate['organisation_number'])
            if len(selected) >= (5 if kind == 'group_structure' and pool is pools[0] else 10):
                break
    if len(selected) < 10:
        for candidate in values:
            if candidate['organisation_number'] not in seen:
                selected.append(candidate); seen.add(candidate['organisation_number'])
            if len(selected) == 10:
                break
    samples[kind] = selected
(out/'review-candidates.json').write_text(json.dumps(samples,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k not in {'site','new_endpoint_states'}},indent=2,ensure_ascii=False))
