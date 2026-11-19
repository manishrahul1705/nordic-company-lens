"""Count actual published claims, not the pre-publication Wikidata index metrics."""
import json
import sys
from collections import defaultdict, Counter
from pathlib import Path

PROPS = ('P1448','P571','P159','P452','P1128','P2139','P856','P2002','P2003','P2013','P4264')
run = Path(sys.argv[1])
target = Path(sys.argv[2])
companies = defaultdict(set)
claims = defaultdict(set)
overall_companies = defaultdict(set)
overall_claims = defaultdict(set)
conflicts = []
comparisons = []
samples = []
cache = {}
available = 0

def binding(ev):
    sha = ev['content_sha256']
    if sha not in cache:
        cache[sha] = json.loads((run/'state'/'blobs'/sha).read_bytes())
    node = cache[sha]
    for bit in ev['locator'].split('/')[1:]:
        node = node[int(bit)] if isinstance(node,list) else node[bit]
    return node

for line in (run/'envelopes.jsonl').open(encoding='utf-8'):
    row = json.loads(line)
    org = row['organisation_number']
    evidence = {e['id']:e for e in row['evidence']}
    company = next((c['value'] for c in row['claims'] if c['field']=='identity.legal_name'),org)
    for claim in row['claims']:
        if claim['availability'] != 'available':
            continue
        available += 1
        field = claim['field']
        broad = []
        if field=='identity.legal_name' or field.startswith('identity.wikidata.official_name.'):broad.append('official_name')
        if field=='identity.founding_date' or field.startswith('identity.wikidata.inception.'):broad.append('inception')
        if 'headquarters' in field:broad.append('explicit_headquarters')
        if field.startswith('identity.nace') or '.wikidata.industry.' in field:broad.append('industry_including_NACE')
        if field=='identity.employees' or '.wikidata.employees.' in field:broad.append('employee_count')
        if field=='accounts.revenue' or '.wikidata.revenue.' in field:broad.append('revenue_current_or_wikidata')
        if field=='official_website':broad.append('ownership_verified_official_website')
        if field.startswith('social_profile.'):
            platform=claim['value'].get('platform','')
            if platform in {'x.com','twitter.com'}:broad.append('X')
            if platform=='instagram.com':broad.append('Instagram')
            if platform=='facebook.com':broad.append('Facebook')
            if platform=='linkedin.com':broad.append('LinkedIn')
        for label in broad:
            overall_companies[label].add(org);overall_claims[label].add((org,claim['id']))
        for ref in claim['evidence_ids']:
            ev=evidence[ref]
            if ev['source_class']!='wikidata':continue
            source=binding(ev)
            assert source['org']['value']==org
            prop=source['property']['value'].rsplit('/',1)[-1]
            if prop not in PROPS:continue
            companies[prop].add(org);claims[prop].add((org,claim['id']))
            samples.append({'organisation_number':org,'company':company,'claim':claim,'evidence':ev,'binding':source,'property':prop})
    diag=row['run']['refresh'].get('wikidata',{})
    conflicts.extend({'organisation_number':org,'company':company,**c} for c in diag.get('disagreements',[]))
    comparisons.extend({'organisation_number':org,'company':company,**c} for c in diag.get('comparisons',[]))
report=json.loads((run/'report.json').read_text(encoding='utf-8'))
index=json.loads((run/'state'/'wikidata-index.json').read_text(encoding='utf-8'))
present_companies=defaultdict(set);present_values=defaultdict(set)
for org, records in index['records'].items():
    for r in records:
        prop=r['property']
        present_companies[prop].add(org)
        present_values[prop].add((org,r['item'],r['value'],r.get('pointInTime')))
summary={'run':str(run),'companies':1000,'total_available_claims':available,
         'http_requests':report['requests'],'wikidata_http_requests':report['wikidata']['requests'],
         'wikidata_metrics':report['wikidata'],
         'properties':{p:{'companies':len(companies[p]),'claims':len(claims[p]),
                           'source_companies':len(present_companies[p]),'source_values':len(present_values[p])} for p in PROPS},
         'overall_information_types':{label:{'companies':len(overall_companies[label]),'claims':len(overall_claims[label])}
            for label in ('official_name','inception','explicit_headquarters','industry_including_NACE','employee_count',
                          'revenue_current_or_wikidata','ownership_verified_official_website','X','Instagram','Facebook','LinkedIn')},
         'disagreements':conflicts,'dated_comparisons':comparisons,
         'deadline_hits':report['deadline_hits'],'handled_exceptions':report['handled_exceptions'],
         'unhandled_exceptions':report['unhandled_exceptions'],'warnings':report['warnings']}
target.write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
target.with_name(target.stem+'-claims.json').write_text(json.dumps(samples,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k not in {'disagreements','dated_comparisons','wikidata_metrics'}},indent=2))
