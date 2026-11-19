import asyncio,json,time
import httpx
import pytest
from signalpost.sources.official_extra import Fetcher,collect
from signalpost.sources.blobstore import BlobStore
from signalpost.budget import SourceFailure
from tests.test_official_extra import ORG,xml
from tests.test_registry_changes import envelope

class Budget:
    def __init__(self): self.deadline=time.monotonic()+1000;self.events=[]
    def reserve(self,url,host,org):
        event={'url':url,'organisation_number':org};self.events.append(event);return event

@pytest.mark.parametrize('statuses,success', [([202,202,200],True),([202,202,202],False)])
def test_202_retries_only_twice_with_requested_backoff(tmp_path,monkeypatch,statuses,success):
    pauses=[];requests=[]
    async def sleep(delay):pauses.append(delay)
    monkeypatch.setattr('signalpost.sources.official_extra.asyncio.sleep',sleep)
    def dispatch(request):
        requests.append(request);assert request.headers['Accept']=='application/xml,text/xml'
        return httpx.Response(statuses[len(requests)-1],text=xml())
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(dispatch)) as client:
            fetch=Fetcher(client,Budget(),BlobStore(tmp_path),1000)
            if success:assert (await fetch.get('https://ted.europa.eu/notice/download.xml')).status==200
            else:
                with pytest.raises(SourceFailure,match='extra_http_202'):await fetch.get('https://ted.europa.eu/notice/download.xml')
                assert fetch.ted_failures[-1]['code']=='extra_http_202'
            assert fetch.ted_calls==3 and fetch.calls==3
            assert fetch.ted_statuses['202']==(2 if success else 3)
    asyncio.run(run())
    assert [p for p in pauses if p>=3]==[3,8]
    assert len(requests)==3

@pytest.mark.parametrize('url',['http://ted.europa.eu/a','https://evil.example/a','https://ted.europa.eu.evil.example/a','https://ted.europa.eu:444/a','https://user@ted.europa.eu/a'])
def test_download_link_must_stay_in_https_allowlist(tmp_path,url):
    async def run():
        fetch=Fetcher(None,Budget(),BlobStore(tmp_path),1000)
        with pytest.raises(SourceFailure,match='extra_url_refused'):await fetch.get(url)
        assert fetch.calls==0
    asyncio.run(run())

def test_redirect_not_followed_and_ted_250_cap_applies_before_request(tmp_path):
    calls=[]
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r:(calls.append(r) or httpx.Response(302,headers={'Location':'https://evil.example'})))) as client:
            fetch=Fetcher(client,Budget(),BlobStore(tmp_path),1000)
            with pytest.raises(SourceFailure,match='extra_http_302'):await fetch.get('https://ted.europa.eu/a')
            fetch.ted_calls=250
            with pytest.raises(SourceFailure,match='ted_request_cap'):await fetch.get('https://ted.europa.eu/b')
    asyncio.run(run());assert len(calls)==1

@pytest.mark.parametrize('with_link',[True,False])
def test_collect_uses_returned_xml_link_or_old_fallback(tmp_path,monkeypatch,with_link):
    seen=[];returned='https://ted.europa.eu/download/specific.xml';fallback='https://ted.europa.eu/en/notice/1-2026/xml'
    async def sleep(delay):pass
    monkeypatch.setattr('signalpost.sources.official_extra.asyncio.sleep',sleep)
    def dispatch(request):
        seen.append(str(request.url))
        if request.url.host=='api.gleif.org':return httpx.Response(200,json={'data':[],'meta':{'pagination':{'lastPage':1}}})
        if request.method=='POST':
            assert 'links' in json.loads(request.content)['fields']
            notice={'publication-number':'1-2026','notice-type':'can-standard','winner-identifier':[ORG]}
            if with_link:notice['links']={'xml':{'MUL':returned}}
            return httpx.Response(200,json={'notices':[notice],'totalNoticeCount':1})
        assert str(request.url)==(returned if with_link else fallback)
        return httpx.Response(200,text=xml())
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(dispatch)) as client:
            sections,metrics=await collect({ORG:envelope()},client,Budget(),BlobStore(tmp_path))
            assert len(sections[ORG].claims)==1
            assert sections[ORG].claims[0].value['matched_role']=='winner'
            assert metrics['ted_requests']==2
    asyncio.run(run())


@pytest.mark.parametrize('recovery',[False,True])
def test_202_outage_opens_breaker_and_records_skipped_notices(tmp_path,monkeypatch,recovery):
    attempts={};original_sleep=asyncio.sleep
    async def sleep(delay):await original_sleep(0)
    monkeypatch.setattr('signalpost.sources.official_extra.asyncio.sleep',sleep)
    def dispatch(request):
        if request.url.host=='api.gleif.org':
            return httpx.Response(200,json={'data':[],'meta':{'pagination':{'lastPage':1}}})
        if request.method=='POST':
            return httpx.Response(200,json={'notices':[
                {'publication-number':f'{i}-2026','notice-type':'can-standard','winner-identifier':[ORG]}
                for i in range(1,9)],'totalNoticeCount':8})
        key=str(request.url);attempts[key]=attempts.get(key,0)+1
        return httpx.Response(200,text=xml()) if recovery and request.url.path.endswith('/3-2026/xml') else httpx.Response(202)
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(dispatch)) as client:
            rows={f'{i:09}':envelope() for i in range(39)}
            rows[ORG]=envelope()
            sections,metrics=await collect(rows,client,Budget(),BlobStore(tmp_path))
            assert len(sections[ORG].claims)==(1 if recovery else 0)
            assert rows[ORG].run.refresh['official_extra']['TED']=='not_available_fetch_failed'
            assert rows[ORG].run.refresh['official_extra']['TED_reason']=='ted_202_circuit_open'
            breaker=metrics['ted_202_circuit_breaker']
            assert breaker['open'] and breaker['threshold']==3
            assert len(breaker['skipped_notices'])==(2 if recovery else 5)
            assert sum(f['code']=='ted_202_circuit_open' for f in metrics['ted_failures'])==(2 if recovery else 5)
    asyncio.run(run())
    assert len(attempts)==(6 if recovery else 3)
    assert sorted(attempts.values())==([1,3,3,3,3,3] if recovery else [3,3,3])


def test_concurrent_downloads_preserve_host_pacing_and_attempt_cap(tmp_path):
    starts=[];active=0;peak=0
    async def dispatch(request):
        nonlocal active,peak
        starts.append(time.monotonic());active+=1;peak=max(peak,active)
        await asyncio.sleep(1.1)
        active-=1
        return httpx.Response(200,text=xml())
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(dispatch)) as client:
            budget=Budget();fetch=Fetcher(client,budget,BlobStore(tmp_path),1000)
            results=await asyncio.gather(*(fetch.get(f'https://ted.europa.eu/{i}.xml') for i in range(3)))
            assert all(r.status==200 for r in results)
            assert fetch.calls==len(budget.events)==3
            fetch.ted_calls=249
            results=await asyncio.gather(*(fetch.get(f'https://ted.europa.eu/limit-{i}.xml') for i in range(3)),return_exceptions=True)
            assert sum(isinstance(r,SourceFailure) and r.code=='ted_request_cap' for r in results)==2
            assert fetch.ted_calls==250
    asyncio.run(run())
    assert peak>=2
    assert all(b-a>=.98 for a,b in zip(starts,starts[1:]))


@pytest.mark.parametrize('probe_recovers',[False,True])
def test_open_breaker_reprobes_after_25_skips_and_can_close(tmp_path,monkeypatch,probe_recovers):
    attempts={};original_sleep=asyncio.sleep
    async def sleep(delay):await original_sleep(0)
    monkeypatch.setattr('signalpost.sources.official_extra.asyncio.sleep',sleep)
    def dispatch(request):
        if request.url.host=='api.gleif.org':
            return httpx.Response(200,json={'data':[],'meta':{'pagination':{'lastPage':1}}})
        if request.method=='POST':
            return httpx.Response(200,json={'notices':[
                {'publication-number':f'{i:03}-2026','notice-type':'can-standard','winner-identifier':[ORG]}
                for i in range(1,80)],'totalNoticeCount':79})
        number=int(request.url.path.split('/')[-2].split('-')[0])
        attempts[number]=attempts.get(number,0)+1
        return httpx.Response(200,text=xml()) if probe_recovers and number>=29 else httpx.Response(202)
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(dispatch)) as client:
            rows={f'{i:09}':envelope() for i in range(999)};rows[ORG]=envelope()
            sections,metrics=await collect(rows,client,Budget(),BlobStore(tmp_path))
            breaker=metrics['ted_202_circuit_breaker']
            assert breaker['reprobe_every_skipped']==25
            assert breaker['open'] is not probe_recovers
            assert breaker['reprobes']==([{'notice':'029-2026','success':True,'reason':None}] if probe_recovers else [
                {'notice':'029-2026','success':False,'reason':'extra_http_202'},
                {'notice':'055-2026','success':False,'reason':'extra_http_202'}])
            assert len(breaker['skipped_notices'])==(25 if probe_recovers else 74)
            assert breaker['reason']=='ted_202_circuit_open'
            assert rows[ORG].run.refresh['official_extra']['TED']=='not_available_fetch_failed'
            assert rows[ORG].run.refresh['official_extra']['TED_reason']=='ted_202_circuit_open'
            # Later verified awards survive while skipped notices remain incomplete.
            assert len(sections[ORG].claims)==(10 if probe_recovers else 0)
    asyncio.run(run())
    if probe_recovers:
        assert set(attempts)=={1,2,3,*range(29,80)}
        assert all(attempts[n]==1 for n in range(29,80))
    else:
        assert set(attempts)=={1,2,3,29,55}
        assert sum(attempts.values())==15
