import asyncio
import socket
import time
import pytest

from signalpost.budget import SourceFailure
from signalpost.web.fetcher import WebsiteHttp
from signalpost.web import policy


def test_dns_failure_rechecks_public_resolvers_without_http(monkeypatch):
    calls=[]

    class Resolver:
        def __init__(self, configure=False):
            self.nameservers=[]
        async def resolve(self, host, record_type, **kwargs):
            calls.append((self.nameservers[0], record_type))
            return ['93.184.216.34'] if record_type == 'A' else []

    monkeypatch.setattr(policy.dns.asyncresolver, 'Resolver', Resolver)
    async def run():
        async def servfail(*args, **kwargs): raise socket.gaierror(socket.EAI_AGAIN, 'synthetic SERVFAIL')
        monkeypatch.setattr(asyncio.get_running_loop(),'getaddrinfo',servfail)
        return await policy.resolve_public('example.test',443)
    result=asyncio.run(run())
    assert result==['93.184.216.34']
    assert {server for server, _ in calls}=={'1.1.1.1','8.8.8.8'}
    assert not any(address.startswith(('10.','127.','192.168.')) for address in result)


def test_fast_nxdomain_skips_public_resolvers(monkeypatch):
    def unexpected(*args, **kwargs):
        raise AssertionError('public resolver must not run after fast NXDOMAIN')
    monkeypatch.setattr(policy.dns.asyncresolver, 'Resolver', unexpected)
    async def run():
        async def nxdomain(*args, **kwargs): raise socket.gaierror(socket.EAI_NONAME, 'synthetic NXDOMAIN')
        monkeypatch.setattr(asyncio.get_running_loop(),'getaddrinfo',nxdomain)
        with pytest.raises(SourceFailure) as caught:
            await policy.resolve_public('missing.example',443)
        return caught.value
    error=asyncio.run(run())
    assert error.code=='no_such_domain'


def test_registered_nxdomain_candidate_uses_one_public_resolver(monkeypatch):
    calls=[]
    class Resolver:
        def __init__(self, configure=False): self.nameservers=[]
        async def resolve(self, host, record_type, **kwargs):
            calls.append((self.nameservers[0],record_type))
            return ['93.184.216.34'] if record_type=='A' else []
    monkeypatch.setattr(policy.dns.asyncresolver,'Resolver',Resolver)
    state=policy.DNSFallbackBudget();state.register_nxdomain_candidate('org','named.example')
    token=policy.DNS_FALLBACK_STATE.set(state)
    async def run():
        policy.DNS_ORG.set('org')
        async def nxdomain(*args,**kwargs):raise socket.gaierror(socket.EAI_NONAME,'synthetic NXDOMAIN')
        monkeypatch.setattr(asyncio.get_running_loop(),'getaddrinfo',nxdomain)
        return await policy.resolve_public('named.example',443)
    try:
        assert asyncio.run(run())==['93.184.216.34']
        assert {server for server,_ in calls}=={'1.1.1.1'}
        assert state.metrics()['dns_fallback_successes']==1
    finally:
        policy.DNS_FALLBACK_STATE.reset(token)


def test_blocked_public_dns_is_silent_and_capped_at_two_seconds_per_resolver(monkeypatch):
    class BlockedResolver:
        def __init__(self, configure=False):
            self.nameservers=[]
        async def resolve(self, host, record_type, **kwargs):
            await asyncio.sleep(10)  # Models UDP/53 filtered with no response.

    monkeypatch.setattr(policy.dns.asyncresolver, 'Resolver', BlockedResolver)
    started=time.monotonic()
    async def run():
        async def servfail(*args, **kwargs): raise socket.gaierror(socket.EAI_AGAIN, 'synthetic SERVFAIL')
        monkeypatch.setattr(asyncio.get_running_loop(),'getaddrinfo',servfail)
        with pytest.raises(SourceFailure) as caught:
            await policy.resolve_public('blocked.example',443)
        return caught.value
    failure=asyncio.run(run())
    elapsed=time.monotonic()-started
    assert failure.code=='dns_servfail'
    # Both public resolvers have strict 2 s ceilings and run concurrently.
    assert elapsed < 2.5


def test_fallback_budget_is_cumulative_per_company(monkeypatch):
    class QuickResolver:
        def __init__(self, configure=False): self.nameservers=[]
        async def resolve(self, host, record_type, **kwargs):
            return ['93.184.216.34'] if record_type=='A' else []
    monkeypatch.setattr(policy.dns.asyncresolver,'Resolver',QuickResolver)
    state=policy.DNSFallbackBudget();token=policy.DNS_FALLBACK_STATE.set(state)
    try:
        async def run():
            policy.DNS_ORG.set('company-one')
            async def servfail(*args, **kwargs): raise socket.gaierror(socket.EAI_AGAIN,'synthetic SERVFAIL')
            monkeypatch.setattr(asyncio.get_running_loop(),'getaddrinfo',servfail)
            # Simulate that earlier candidate failures used the company's cap.
            state.elapsed_by_company['company-one']=3.99
            with pytest.raises(SourceFailure):
                await policy.resolve_public('next.example',443)
        asyncio.run(run())
        assert state.metrics()['dns_fallback_max_seconds_per_company'] <= 4.0
        assert state.attempts_by_company.get('company-one',0)==0
        state.register_nxdomain_candidate('company-one','one.example')
        state.register_nxdomain_candidate('company-one','two.example')
        state.register_nxdomain_candidate('company-one','three.example')
        assert not state.register_nxdomain_candidate('company-one','fourth.example')
    finally:
        policy.DNS_FALLBACK_STATE.reset(token)


def test_website_dns_resolution_stops_at_remaining_run_budget():
    class Budget:
        deadline=time.monotonic()+0.02
    class Config:
        website_transient_retry=False
    class SlowResolver:
        async def __call__(self,*args):
            await asyncio.sleep(10)
    class Blobs:
        pass
    http=WebsiteHttp(None,Config(),Budget(),Blobs(),resolver=SlowResolver())
    started=time.monotonic()
    with pytest.raises(TimeoutError):
        asyncio.run(http.resolve('slow.example',443,'923609016'))
    assert time.monotonic()-started < 0.2
