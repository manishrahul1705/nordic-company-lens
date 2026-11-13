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
