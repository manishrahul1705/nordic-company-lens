"""TED/GLEIF-only measurement: runs the runtime's official_extra.collect for the frozen companies."""
import asyncio,json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path[:0]=[str(ROOT/'src'),str(ROOT)]
import httpx
from signalpost.sources.official_extra import collect
from signalpost.sources.blobstore import BlobStore
from tests.test_registry_changes import envelope
src,out=sys.argv[1],Path(sys.argv[2])
orgs=[]
for line in open(src,encoding='utf8'):
    e=json.loads(line)
    if e['run']['sections'].get('identity')=='available':orgs.append(e['organisation_number'])
log=[]
class Budget:
    def __init__(self):self.deadline=time.monotonic()+3600
    def reserve(self,url,host,org):
        ev={'url':url,'host':host};log.append(ev);return ev
async def go():
    async with httpx.AsyncClient(headers={'User-Agent':'signalpost-benchmark'}) as client:
        return await collect({o:envelope(o) for o in sorted(orgs)},client,Budget(),BlobStore(out/'blobs'))
t=time.monotonic();result,metrics=asyncio.run(go())
awards=[{'orgnr':o,'claim':c.model_dump(mode='json') if hasattr(c,'model_dump') else c.__dict__} for o,s in result.items() for c in s.claims if c.field.startswith('procurement_award.')]
evidence={e.id:(e.model_dump(mode='json') if hasattr(e,'model_dump') else e.__dict__) for s in result.values() for e in s.evidence}
json.dump({'eligible':len(orgs),'seconds':round(time.monotonic()-t,1),'metrics':metrics,'awards':awards,'evidence':evidence,'request_log':log},open(out/'ted-only.json','w',encoding='utf8'),indent=1,default=str)
print(len(orgs),metrics['tender_notices_nominated'],metrics['ted_requests'],metrics['ted_http_statuses'],len(metrics['ted_failures']),'awards',len(awards),'companies',len({a['orgnr'] for a in awards}))
