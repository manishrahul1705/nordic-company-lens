"""Build an offline precision-review ledger from the pinned fresh sample."""
import collections,hashlib,json,random
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'bench/reports/s6-step22'
RUN=ROOT/'bench/cache/s6-step22-official'
def pointer(d,p):
 for k in p.strip('/').split('/'):
  if not k:return d
  k=k.replace('~1','/').replace('~0','~');d=d[int(k)] if isinstance(d,list) else d[k]
 return d
def main():
 rows=[json.loads(l) for l in (RUN/'validation/run1-envelopes.jsonl').open(encoding='utf-8')]
 rng=random.Random(2026110722);cache={};items=[];families=collections.defaultdict(list);special=[]
 def support(row,c):
  es={e['id']:e for e in row['evidence']};out=[]
  for eid in c['evidence_ids']:
   e=es[eid];sha=e['content_sha256'];b=(RUN/'out/state/blobs'/sha).read_bytes()
   assert hashlib.sha256(b).hexdigest()==sha
   text=b.decode('utf-8',errors='replace');assert e['claim_span'] in text
   x={'evidence':e}
   try:x['raw_located_value']=pointer(json.loads(text),e['locator'])
   except (ValueError,KeyError,TypeError,IndexError):
    at=text.find(e['claim_span']);x['raw_context']=text[max(0,at-700):at+len(e['claim_span'])+700]
   out.append(x)
  return out
 def item(row,c,group):
  return {'orgnr':row['organisation_number'],'company':next((x['value'] for x in row['claims'] if x['field']=='identity.legal_name'),''),'group':group,'claim':c,'support':support(row,c),'verdict':'pending'}
 for row in rows:
  for c in row['claims']:
   if c['availability']!='available':continue
   f=c['field'];group=None
   if c['family']=='website' and ('social' in f or f=='official_website'):group='website/social'
   if f.startswith('identity.gleif.'):group='GLEIF'
   if f.startswith('procurement_award.'):group='TED'
   if c['family']=='hiring':group='job'
   if group:special.append(item(row,c,group))
   if c['family'] in ['identity','roles','subunits','accounts']:families[c['family']].append((row,c))
   if f.startswith('registry_change.'):families['registry announcements'].append((row,c))
 for family,pool in families.items():
  for row,c in rng.sample(pool,min(10,len(pool))):items.append(item(row,c,family))
 briefings=[]
 for row in rng.sample([r for r in rows if r['run'].get('synthesis') and r['run']['synthesis'].get('analyst_brief')],10):
  cs={c['id']:c for c in row['claims']};syn=row['run']['synthesis'];sentences=syn['analyst_brief']['sentences'];context={c['id']:c for c in syn['analyst_brief'].get('context_claims',[])}
  frames=[]
  for s in sentences:
   frames.append({'sentence':s,'claims':[cs[i] for i in s['claim_ids'] if i in cs],'context':[context[i] for i in s['claim_ids'] if i in context],'raw_support':{i:support(row,cs[i]) for i in s['claim_ids'] if i in cs}})
  briefings.append({'orgnr':row['organisation_number'],'frames':frames,'verdict':'pending'})
 data={'special':special,'sampled':items,'briefings':briefings}
 (OUT/'review-ledger.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'special':dict(collections.Counter(x['group'] for x in special)),'sampled':dict(collections.Counter(x['group'] for x in items)),'briefings':len(briefings)}))
if __name__=='__main__':main()
