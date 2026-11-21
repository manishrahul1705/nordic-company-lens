import sys,json,random,collections,hashlib,lzma,base64
from pathlib import Path
from urllib.parse import urlsplit,unquote
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'accuracy'))
import common as C
from signalpost.sources.text import decode_body
HERE=Path(__file__).resolve().parent
ACTIVE=set((HERE/'active-organisations.txt').read_text(encoding='utf-8').splitlines())
rows={};pop=collections.defaultdict(list)
with open('bench/runs/jury-unseen300-ba/envelopes.jsonl',encoding='utf-8') as fh:
 for line in fh:
  r=json.loads(line);org=r['organisation_number']
  if org not in ACTIVE or org in rows:continue
  rows[org]=r
  for c in r['claims']:
   if C.published(c):pop[C.family(c['field'])].append((org,c['id']))
if len(rows)!=300:raise SystemExit(f'expected 300 active orgs, got {len(rows)}')
n=min(100,sum(map(len,pop.values())));alloc={k:1 for k in pop}
while sum(alloc.values())<n:
 k=max(sorted(pop),key=lambda k:len(pop[k])/(alloc[k]+1) if alloc[k]<len(pop[k]) else -1);alloc[k]+=1
rng=random.Random(7);picks={pair for k in sorted(pop) for pair in rng.sample(sorted(pop[k]),alloc[k])}
items=[];blobs={}
for org,r in rows.items():
 ev={e['id']:e for e in r['evidence']}
 for c in r['claims']:
  if (org,c['id']) not in picks:continue
  e=ev[c['evidence_ids'][0]];body=(Path('bench/runs/jury-unseen300-ba/state/blobs')/e['content_sha256']).read_bytes()
  if hashlib.sha256(body).hexdigest()!=e['content_sha256']:raise SystemExit('blob hash mismatch')
  try:doc=json.loads(body);at=C.pointer(doc,e['locator'])
  except Exception:doc=None;at=None
  url=e['source_url'];host=urlsplit(url).hostname
  exact=at is not None and at==c['value'] and org in unquote(url) and host in {'data.brreg.no','data.norge.no'} and bool(e['claim_span']) and e['claim_span'] in decode_body(body)
  blobs[e['content_sha256']]=body
  items.append({'orgnr':org,'legal_name':r.get('legal_name'),'family':C.family(c['field']),'field':c['field'],'claim_id':c['id'],'value':c['value'],'evidence':{k:e.get(k) for k in ('source_url','locator','claim_span','content_sha256')},'mechanical_exact':exact,'initial_verdict':'correct' if exact else 'needs_source_review'})
(HERE/'sample.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in items),encoding='utf-8')
(HERE/'population.json').write_text(json.dumps({'seed':7,'size':len(items),'active_companies':len(ACTIVE),'population_by_family':{k:len(v) for k,v in sorted(pop.items())},'allocation':alloc},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
with lzma.open(HERE/'source-blobs.jsonl.xz','wt',encoding='utf-8',preset=9|lzma.PRESET_EXTREME) as out:
 for sha,body in sorted(blobs.items()):out.write(json.dumps({'sha256':sha,'b64':base64.b64encode(body).decode('ascii')},sort_keys=True)+'\n')
print(json.dumps({'sampled':len(items),'mechanical_exact':sum(x['mechanical_exact'] for x in items),'review':sum(not x['mechanical_exact'] for x in items),'allocation':alloc,'blobs':len(blobs)},indent=2))
