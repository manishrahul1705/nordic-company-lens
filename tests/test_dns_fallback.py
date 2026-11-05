import asyncio
import socket
import time
import pytest

from signalpost.budget import SourceFailure
from signalpost.web.fetcher import WebsiteHttp
from signalpost.web import policy


def test_dns_failure_rechecks_public_resolvers_without_http(monkeypatch):
    calls=[]

    class Loop:
        async def getaddrinfo(self, host, port, type):
            raise socket.gaierror(socket.EAI_NONAME, 'synthetic NXDOMAIN')

    class Resolver:
        def __init__(self, configure=False):
            self.nameservers=[]
        async def resolve(self, host, record_type, **kwargs):
            calls.append((self.nameservers[0], record_type))
            return ['93.184.216.34'] if record_type == 'A' else []

    monkeypatch.setattr(asyncio, 'get_running_loop', lambda: Loop())
    monkeypatch.setattr(policy.dns.asyncresolver, 'Resolver', Resolver)
    result=asyncio.run(policy.resolve_public('example.test',443))
    assert result==['93.184.216.34']
    assert {server for server, _ in calls}=={'1.1.1.1','8.8.8.8'}
    assert not any(address.startswith(('10.','127.','192.168.')) for address in result)


def test_blocked_public_dns_is_silent_and_capped_at_two_seconds_per_resolver(monkeypatch):
    class Loop:
        async def getaddrinfo(self, host, port, type):
            raise socket.gaierror(socket.EAI_NONAME, 'synthetic NXDOMAIN')

    class BlockedResolver:
        def __init__(self, configure=False):
            self.nameservers=[]
        async def resolve(self, host, record_type, **kwargs):
            await asyncio.sleep(10)  # Models UDP/53 filtered with no response.

    monkeypatch.setattr(asyncio, 'get_running_loop', lambda: Loop())
    monkeypatch.setattr(policy.dns.asyncresolver, 'Resolver', BlockedResolver)
    started=time.monotonic()
    with pytest.raises(SourceFailure) as caught:
        asyncio.run(policy.resolve_public('blocked.example',443))
    elapsed=time.monotonic()-started
    assert caught.value.code=='no_such_domain'
    # Each public resolver is tried once and has its own strict 2 s ceiling.
    assert elapsed < 4.5


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
