"""Replay the saved 79-notice 202 outage, retaining measured HTTP latency."""
import asyncio,json,time,collections
from pathlib import Path
from types import SimpleNamespace
import httpx
from signalpost.sources.official_extra import collect
from signalpost.sources.blobstore import BlobStore
from signalpost.io.input_adapter import read

baseline=json.loads(Path('bench/runs/frozen-repro-20261119/report.json').read_text())
saved=collections.defaultdict(list)
for e in baseline['request_log']:
    if e.get('host')=='ted.europa.eu':saved[e['url']].append(e)
orgs=read(Path('bench/inputs/1000-r3/batch.jsonl')).unique
org=sorted(orgs)[0];attempts=collections.Counter()
class Budget:
    def __init__(self):self.deadline=time.monotonic()+120;self.events=[]
    def reserve(self,url,host,org):
        event={'url':url};self.events.append(event);return event
async def dispatch(request):
    url=str(request.url)
    if request.url.host=='api.gleif.org':
        return httpx.Response(200,json={'data':[],'meta':{'pagination':{'lastPage':1}}})
    if request.method=='POST':
        return httpx.Response(200,json={'notices':[{'publication-number':url.split('/')[-2],
            'notice-type':'can-standard','winner-identifier':[org],'links':{'xml':{'MUL':url}}}
            for url in saved],'totalNoticeCount':len(saved)})
    event=saved[url][attempts[url]];attempts[url]+=1
    await asyncio.sleep(event['runtime_ms']/1000)
    return httpx.Response(event['status'])
async def main():
    async with httpx.AsyncClient(transport=httpx.MockTransport(dispatch)) as client:
        rows={o:SimpleNamespace(run=SimpleNamespace(refresh={})) for o in orgs}
        _,metrics=await collect(rows,client,Budget(),BlobStore(Path('out/ted-outage-replay')))
    old=max(e['attempt_started']+e['runtime_ms']/1000 for events in saved.values() for e in events)-min(e['attempt_started'] for events in saved.values() for e in events)
    result={'scope':'Controlled TED-only replay; original HTTP statuses and durations, real retry/pacing sleeps. Prelude responses synthetic; not a full pipeline benchmark.',
            'old_ted_xml_span_seconds':round(old,3),'new_ted_xml_seconds':metrics['ted_xml_seconds'],
            'saving_seconds':round(old-metrics['ted_xml_seconds'],3),'xml_attempts':sum(attempts.values()),
            'breaker':metrics['ted_202_circuit_breaker']}
    Path('bench/reports/ted-retry-budget-20261119/outage-replay.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))
asyncio.run(main())
