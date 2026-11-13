import asyncio
import socket

import httpx
import pytest

from signalpost.budget import Budget, SourceFailure
from signalpost.sources.blobstore import BlobStore
from signalpost.web.fetcher import WebsiteHttp, retryable_transport
from signalpost.web import policy
from signalpost.web.policy import resolve_public
from tests.test_registry import config, execute, numbers
from tests.test_websites import OUR


@pytest.mark.parametrize('error', [httpx.ReadTimeout('read'), httpx.ConnectTimeout('connect'),
    httpx.ConnectError('connection reset by peer'), httpx.ConnectError('connection refused'),
    SourceFailure('dns_servfail'), SourceFailure('dns_timeout')])
def test_transient_retry_classifier(error):
    assert retryable_transport(error)


@pytest.mark.parametrize('error', [httpx.ConnectError('TLS certificate verify failed'),
    SourceFailure('no_such_domain'), SourceFailure('ssrf'), SourceFailure('dns_error'),
    httpx.ConnectError('unclassified connect failure'), SourceFailure('http_429')])
def test_permanent_or_unclassified_errors_are_not_retried(error):
    assert not retryable_transport(error)


@pytest.mark.parametrize('path', ['/robots.txt','/','/kontakt'])
def test_each_fetch_retries_once_with_12_second_timeout(tmp_path,monkeypatch,path):
    async def no_delay(self): pass
    monkeypatch.setattr(WebsiteHttp,'retry_pause',no_delay)
    attempts=[]
    def respond(request):
        if request.url.path!=path:
            return httpx.Response(200,text='User-agent: *\nAllow: /')
        attempts.append(request.extensions['timeout']['read'])
        if len(attempts)==1:raise httpx.ReadTimeout('synthetic',request=request)
        return httpx.Response(200,text='ok')
    async def dns(*args):return ['93.184.216.34']
    cfg=config(tmp_path,[OUR]).model_copy(update={'website_politeness_seconds':0})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            h=WebsiteHttp(client,cfg,Budget(cfg),BlobStore(cfg.state_dir),dns)
            r=(await h.raw('https://example.no'+path,OUR,{'example.no'}) if path=='/robots.txt'
               else await h.get('https://example.no'+path,OUR,'example.no'))
            assert r.status==200
    asyncio.run(run())
    assert attempts==[8,12]


def test_exhausted_robots_retry_is_not_retried_by_outer_page(tmp_path,monkeypatch):
    async def no_delay(self):pass
    monkeypatch.setattr(WebsiteHttp,'retry_pause',no_delay)
    attempts=[]
    def respond(request):
        attempts.append(str(request.url))
        raise httpx.ConnectError('connection refused',request=request)
    async def dns(*args):return ['93.184.216.34']
    cfg=config(tmp_path,[OUR]).model_copy(update={'website_politeness_seconds':0})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            h=WebsiteHttp(client,cfg,Budget(cfg),BlobStore(cfg.state_dir),dns)
            with pytest.raises(SourceFailure):await h.get('https://example.no/',OUR,'example.no')
    asyncio.run(run())
    assert attempts==['https://example.no/robots.txt']*2


@pytest.mark.parametrize('status',[400,401,403,404,410,429])
def test_no_http_4xx_retry(tmp_path,monkeypatch,status):
    attempts=[]
    def respond(request):
        attempts.append(str(request.url));return httpx.Response(status,text='no')
    async def dns(*args):return ['93.184.216.34']
    cfg=config(tmp_path,[OUR]).model_copy(update={'website_politeness_seconds':0})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            h=WebsiteHttp(client,cfg,Budget(cfg),BlobStore(cfg.state_dir),dns)
            r=await h.raw('https://example.no/',OUR,{'example.no'})
            assert r.status==status
    asyncio.run(run());assert len(attempts)==1


def test_dns_servfail_retried_but_nxdomain_not(tmp_path,monkeypatch):
    async def no_delay(self):pass
    monkeypatch.setattr(WebsiteHttp,'retry_pause',no_delay)
    from signalpost.web.candidates import Candidate
    for code,expected in [('dns_servfail',2),('no_such_domain',1)]:
        calls=[]
        async def dns(*args):
            calls.append(args)
            if len(calls)==1:raise SourceFailure(code)
            return ['93.184.216.34']
        cfg=config(tmp_path/code,[OUR])
        async def run():
            async with httpx.AsyncClient() as client:
                h=WebsiteHttp(client,cfg,Budget(cfg),BlobStore(cfg.state_dir),dns)
                if code=='no_such_domain':
                    with pytest.raises(SourceFailure):await h.precheck(Candidate('https://example.no','example.no','legal_name_slug'),OUR)
                else:await h.precheck(Candidate('https://example.no','example.no','legal_name_slug'),OUR)
        asyncio.run(run());assert len(calls)==expected


def test_system_dns_temporary_error_is_distinct_from_nxdomain(monkeypatch):
    async def run():
        loop=asyncio.get_running_loop()
        async def fail(*args,**kwargs):raise socket.gaierror(socket.EAI_AGAIN,'temporary failure')
        monkeypatch.setattr(loop,'getaddrinfo',fail)
        class BlockedResolver:
            def __init__(self, configure=False):self.nameservers=[]
            async def resolve(self,*args,**kwargs):raise policy.dns.exception.Timeout()
        monkeypatch.setattr(policy.dns.asyncresolver,'Resolver',BlockedResolver)
        with pytest.raises(SourceFailure) as error:await resolve_public('example.no')
        assert error.value.code=='dns_servfail'
    asyncio.run(run())


def test_global_hard_caps_cannot_be_raised_by_overrides(tmp_path):
    cfg=config(tmp_path,numbers(3),max_requests=999999,time_budget_seconds=999999)
    budget=Budget(cfg)
    assert budget.cap==57
    assert budget.total_seconds==72
    assert budget.deadline<=budget.start+72


def test_global_cap_exhaustion_preserves_all_output_rows(tmp_path):
    cfg=config(tmp_path,numbers(4),max_requests=1)
    report,rows=execute(cfg)
    assert len(rows)==4 and report['requests']==1
    assert any(e['code']=='budget_exhausted' for r in rows for e in r['errors'])
