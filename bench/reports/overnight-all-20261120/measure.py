"""Read-only publication accounting for the overnight live run."""
from pathlib import Path
from collections import defaultdict,Counter
import json
run=Path('bench/runs/overnight-all-20261120'); out=Path(__file__).parent
r=json.loads((run/'report.json').read_text(encoding='utf-8')); m=json.loads((run/'measurement.json').read_text(encoding='utf-8'))
counts=Counter(); companies=defaultdict(set); facts=set();platforms=Counter();pc=defaultdict(set);states=defaultdict(Counter)
for line in (run/'envelopes.jsonl').open(encoding='utf-8'):
 row=json.loads(line);org=row['organisation_number']
 for kind,v in row['run']['refresh'].get('brreg_extended',{}).items():states[kind][v['state']]+=1
 for c in row['claims']:
  if c['availability']!='available' or c['value'] is None:continue
  f=c['field']
  if not f.endswith('.section'):facts.add((org,f,json.dumps(c['value'],sort_keys=True),json.dumps(c.get('reporting_period'),sort_keys=True)))
  labels=[]
  if f=='official_website':labels.append('websites')
  if f.startswith(('social_profile.','registry_social.')) and isinstance(c['value'],dict):
   labels.append('social');platform=c['value'].get('platform','unknown');platforms[platform]+=1;pc[platform].add(org)
  if f=='public_brand' or f.startswith('public_brand.'):labels.append('brands')
  if f.startswith('identity.gleif.'):labels.append('gleif')
  if f.startswith('procurement_award.'):labels.append('ted')
  if f.startswith('hiring.') and not f.endswith('.section'):labels.append('hiring')
  if f.startswith('identity.group_structure.'):labels.append('group_structure')
  if f=='roles.signatur.registered_basis':labels.append('signatur')
  if f=='roles.prokura.registered_basis':labels.append('prokura')
  for label in labels:counts[label]+=1;companies[label].add(org)
summary={'run':str(run),'commit':m['commit'],'run_status':r['run_status'],'wall_seconds':m['wall_seconds'],'projection_1100_seconds':round(m['wall_seconds']*1.1,3),'deadline_hits':r['deadline_hits'],'handled_exceptions':r['handled_exceptions'],'unhandled_exceptions':r['unhandled_exceptions'],'warnings':r['warnings'],'total_http':r['requests'],'pooled_percent':r['requests']/19000*100,'max_requests_per_company':r['max_requests_per_company'],'families':{k:{'companies':len(companies[k]),'claims':counts[k]} for k in ['websites','social','brands','gleif','ted','hiring','group_structure','signatur','prokura']},'social_platforms':{k:{'companies':len(pc[k]),'claims':platforms[k]} for k in sorted(platforms)},'supported_facts_excluding_sections':len(facts),'brreg_states':{k:dict(v) for k,v in states.items()},'stages':r['finalisation'],'site':r['site'],'official_extra':r['official_extra'],'wikidata':r['wikidata']}
(out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps({k:v for k,v in summary.items() if k not in ['official_extra','site','brreg_states']},indent=2))
