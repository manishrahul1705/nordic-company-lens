"""Offline paired replay of official_extra.collect: saved TED search responses and saved notice XML, mock transport."""
import asyncio,json,os,re,sys,time,hashlib
from pathlib import Path
SRC=Path(sys.argv[1]);OUT=Path(sys.argv[2])
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(SRC/'src'),str(ROOT)]
import httpx
import signalpost.sources.official_extra as ox
assert Path(ox.__file__).resolve().is_relative_to(SRC.resolve()),ox.__file__
from signalpost.sources.blobstore import BlobStore
from tests.test_registry_changes import envelope
RUN=ROOT/'bench/runs/stage-u-ws';B=RUN/'state/blobs'
report=json.load(open(RUN/'report.json'))
notices={}
for e in report['request_log']:
    if e.get('host')=='api.ted.europa.eu':
        for n in json.load(open(B/e['content_sha256'],encoding='utf8'))['notices']:notices[n['publication-number']]=n
xml={}
for e in report['request_log']:
    m=re.search(r'/notice/([^/]+)/xml',str(e.get('url','')))
    if m and e.get('status')==200:xml[m.group(1)]=B/e['content_sha256']
for d in (ROOT/'bench/runs/stage-u-ws-ted/xml',ROOT/'bench/cache/ted-snapshot/xml'):
    for n in notices:
        if n not in xml and (d/f'{n}.xml').exists():xml[n]=d/f'{n}.xml'
orgs=[json.loads(l)['organisation_number'] for l in open(RUN/'envelopes.jsonl',encoding='utf8') if json.loads(l)['run']['sections'].get('identity')=='available']
served=[]
def dispatch(request):
    if request.url.host=='api.gleif.org':return httpx.Response(200,json={'data':[],'meta':{'pagination':{'lastPage':1}}})
    if request.url.host=='api.ted.europa.eu':
        return httpx.Response(200,json={'notices':list(notices.values()),'totalNoticeCount':1})
    n=re.search(r'/notice/([^/]+)/xml',str(request.url)).group(1)
    if n in xml:served.append(n);return httpx.Response(200,content=Path(xml[n]).read_bytes())
    return httpx.Response(202,text='')
class Budget:
    def __init__(self):self.deadline=time.monotonic()+3600
    def reserve(self,url,host,org):return {'url':url,'host':host}
async def nosleep(*a,**k):pass
ox.asyncio.sleep=nosleep  # replay: no politeness delay needed against a mock
async def go():
    async with httpx.AsyncClient(transport=httpx.MockTransport(dispatch)) as client:
        return await collect_({o:envelope(o) for o in sorted(orgs)},client,Budget(),BlobStore(OUT/'blobs'))
collect_=ox.collect
result,metrics=asyncio.run(go())
dump=lambda c:c.model_dump(mode='json') if hasattr(c,'model_dump') else c.__dict__
awards=[{'orgnr':o,'claim':dump(c)} for o,s in result.items() for c in s.claims if c.field.startswith('procurement_award.')]
states={o:e.run.refresh.get('official_extra',{}).get('TED') for o,e in ((o,env) for o,env in [])}
OUT.mkdir(parents=True,exist_ok=True)
json.dump({'code':str(SRC),'eligible':len(orgs),'search_notices':len(notices),'xml_available':len(xml),'metrics':metrics,'served':sorted(set(served)),'awards':awards,
           'evidence':{e.id:dump(e) for s in result.values() for e in s.evidence}},open(OUT/'replay.json','w',encoding='utf8'),indent=1,default=str)
print(SRC.name,'nominated',metrics['tender_notices_nominated'],'failures',len(metrics['ted_failures']),'awards',len(awards),'companies',len({a['orgnr'] for a in awards}))
