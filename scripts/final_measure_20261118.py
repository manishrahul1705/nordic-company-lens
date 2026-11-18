"""Family counts for a frozen-1,000 run. Definitions reproduce final-uvw-under-load/measurement.json:
supported facts = available claims whose evidence ids all resolve; GLEIF = claims citing api.gleif.org;
social = social_profile + registry_social claims; TED awards = procurement_award claims."""
import json, sys, collections
run = sys.argv[1]
rep = json.load(open(f'{run}/report.json', encoding='utf-8-sig'))
fam = collections.defaultdict(lambda: [set(), 0]); supported = 0; n = 0
for line in open(f'{run}/envelopes.jsonl', encoding='utf-8-sig'):
    e = json.loads(line); n += 1; org = e['organisation_number']; ev = {x['id']: x for x in e['evidence']}
    for c in e['claims']:
        if c['availability'] != 'available': continue
        if c['evidence_ids'] and all(i in ev for i in c['evidence_ids']): supported += 1
        p = c['field'].split('.')[0]
        hosts = {ev[i]['source_url'].split('/')[2] for i in c['evidence_ids'] if i in ev}
        key = ('websites' if p == 'official_website' else 'social' if p in ('social_profile', 'registry_social')
               else 'brands' if p == 'public_brand' else 'ted_awards' if p == 'procurement_award'
               else 'gleif' if 'api.gleif.org' in hosts else None)
        if key: fam[key][0].add(org); fam[key][1] += 1
print(json.dumps({'envelopes': n, 'run_status': rep.get('run_status'), 'success_rate': rep.get('success_rate'),
    'requests': rep['requests'], 'deadline_hits': rep['deadline_hits'],
    'handled_exceptions': rep['handled_exceptions'], 'unhandled_exceptions': rep['unhandled_exceptions'],
    'source_errors_by_family': rep.get('source_errors_by_family'), 'supported_facts': supported,
    'families': {k: {'companies': len(v[0]), 'claims': v[1]} for k, v in sorted(fam.items())},
    'site': rep.get('site', {}).get('state'), 'warnings': rep['warnings']}, indent=1))
