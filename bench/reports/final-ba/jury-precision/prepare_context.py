import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
sample=[json.loads(l) for l in open(HERE/'sample.jsonl',encoding='utf-8')]
orgs={x['orgnr'] for x in sample};out=[]
for l in open('bench/runs/jury-unseen300-ba/envelopes.jsonl',encoding='utf-8'):
 r=json.loads(l)
 if r['organisation_number'] not in orgs:continue
 used={c['id'] for c in r['claims']}
 evidence={eid for c in r['claims'] for eid in c.get('evidence_ids',[])}
 out.append({'organisation_number':r['organisation_number'],'legal_name':(r.get('run',{}).get('legal_identity') or {}).get('legal_name'),'claims':r['claims'],'evidence':[e for e in r['evidence'] if e['id'] in evidence]})
(HERE/'company-context.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n' for r in out),encoding='utf-8')
print('company context rows',len(out))
