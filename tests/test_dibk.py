import asyncio
import hashlib
import httpx
import pytest

from signalpost.budget import Budget
from signalpost.sources import dibk as D
from signalpost.sources.http import Response
from signalpost.sources.blobstore import BlobStore
from tests.test_funding_snapshots import envelope
from tests.test_registry import config
from signalpost.sources.extract import Section, Source, add

ORG = '912492575'


def page(org=ORG, statement='Foretaket har sentral godkjenning', period='22.09.2025&ndash;22.09.2028'):
    return ('<b>Organisasjonsnummer</b><p>' + org + '</p><h3>' + statement + '</h3>'
        '<b>Godkjenningsperiode:</b><span>' + period + '</span><table><thead><tr>'
        '<th>Funksjon</th><th>Fagområde</th><th>Tiltaksklasse</th></tr></thead><tbody>'
        '<tr><td>Utførende</td><td>Installasjon av brannalarmanlegg</td><td>1</td></tr>'
        '<tr class="hidden"><td colspan="4">Explanation mentioning other areas</td></tr>'
        '</tbody></table>').encode()


def response(body=None, status=200, url=None):
    body = page() if body is None else body
    return Response(body, status, url or D.ORIGIN + '/enterprises/' + ORG,
        '2026-11-20T00:00:00Z', hashlib.sha256(body).hexdigest())


def row(code='43.210'):
    r = envelope(ORG); s = Section(); body = b'{}'
    add(s, Source('https://data.brreg.no/test', body, hashlib.sha256(body).hexdigest(), '2026-11-20T00:00:00Z'),
        ORG, 'identity', 'identity.nace1', {'kode': code}, '/')
    r.claims.extend(s.claims); r.evidence.extend(s.evidence)
    return r


@pytest.mark.parametrize('code,expected', [('41.100', True), ('42.110', True), ('43.210', True),
    ('71.121', True), ('71.200', True), ('70.220', False), ('71.300', False), ('43bad', False), ('', False)])
def test_registered_nace_gate(code, expected):
    assert D.selected(row(code)) is expected


def test_failed_identity_and_carried_nace_cannot_select():
    r = row(); r.run.sections['identity'] = 'failed'; assert not D.selected(r)
    r.run.sections['identity'] = 'available'; r.claims[-1].carried_forward = True; assert not D.selected(r)


def test_extract_exact_fields_and_all_verbatim_support():
    r = response(); s = D.extract(r, ORG)
    assert len(s.claims) == 1
    v = s.claims[0].value
    assert v['function'] == 'Utførende' and v['area'] == 'Installasjon av brannalarmanlegg'
    assert v['class'] == '1' and v['valid_from'] == '22.09.2025' and v['valid_to'] == '22.09.2028' and v['status'] == 'approved'
    assert len(s.claims[0].evidence_ids) == 6
    assert all(e.claim_span in r.body.decode() and len(e.claim_span) <= 300 and e.content_sha256 == r.sha for e in s.evidence)


@pytest.mark.parametrize('body,status', [(page('926698435'), 200), (page(), 404),
    (page(statement='Status unknown'), 200), (page(period='01.01.2020&ndash;01.01.2021'), 200),
    (page(period='bad'), 200), (b'<h1>Not found</h1>', 200)])
def test_no_unsupported_or_negative_claim(body, status):
    assert not D.extract(response(body, status), ORG).claims


def test_expired_requires_explicit_status_and_dates():
    s = D.extract(response(page(statement='Godkjenningen er utløpt', period='01.01.2020&ndash;01.01.2021')), ORG)
    assert s.claims[0].value['status'] == 'expired'


def test_duplicate_responsive_table_is_not_double_counted():
    assert len(D.extract(response(page() + page()), ORG).claims) == 1


def trial(tmp_path, *, robots='User-agent: *\nDisallow: /api/\nDisallow: /search', cap=None, status=200):
    cfg = config(tmp_path, [ORG], dibk=True, max_requests=cap)
    budget = Budget(cfg); blobs = BlobStore(tmp_path / 'state'); calls = []
    def handler(request):
        calls.append(str(request.url))
        if request.url.path == '/robots.txt':
            return httpx.Response(200, text=robots)
        assert request.url.path == '/enterprises/' + ORG
        return httpx.Response(status, content=page(), headers={'content-type': 'text/html'})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            collector = D.Collector(client, cfg, budget, blobs)
            # Pacing is tested separately, avoid waiting in every source test.
            cfg.website_politeness_seconds = 0
            r = row(); collector.schedule(r); collector.schedule(r)
            await collector.finish()
            return r, budget, calls
    return asyncio.run(run())


def test_single_enterprise_attempt_and_shared_budgeted_robots(tmp_path):
    r, budget, calls = trial(tmp_path)
    assert len(calls) == 2 and budget.by_company[ORG] == 1
    assert any(c.field.startswith('central_approval.') for c in r.claims)
    assert r.run.refresh['dibk']['requests'] == 1
    assert not any('/api/' in url or '/search' in url for url in calls)


def test_robots_disallowed_makes_no_enterprise_request(tmp_path):
    r, budget, calls = trial(tmp_path, robots='User-agent: *\nDisallow: /enterprises/')
    assert len(calls) == 1 and r.run.refresh['dibk']['reason'] == 'robots'
    assert not any(c.field.startswith('central_approval.') for c in r.claims)


def test_budget_cap_cannot_be_bypassed(tmp_path):
    r, budget, calls = trial(tmp_path, cap=1)
    assert len(calls) == 1 and r.run.refresh['dibk']['reason'] == 'budget_exhausted'
    assert r.run.refresh['dibk']['requests'] == 0


def test_404_only_diagnostic(tmp_path):
    r, budget, calls = trial(tmp_path, status=404)
    assert r.run.refresh['dibk']['state'] == 'not_found'
    assert not any(c.field.startswith('central_approval.') for c in r.claims)


def test_pacing_matches_website_minimum_and_no_retries(tmp_path):
    cfg = config(tmp_path, [ORG], dibk=True); budget = Budget(cfg)
    times = []
    async def handler(request):
        times.append(asyncio.get_running_loop().time())
        return httpx.Response(503, text='unavailable')
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            collector = D.Collector(client, cfg, budget, BlobStore(tmp_path / 'state'))
            await collector.request('/enterprises/' + ORG, ORG)
            await collector.request('/enterprises/' + ORG, ORG)
    asyncio.run(run())
    assert len(times) == 2 and times[1] - times[0] >= 1


def test_redirect_never_follows_api_or_other_page(tmp_path):
    cfg = config(tmp_path, [ORG]); cfg.website_politeness_seconds = 0
    calls = []
    def handler(request):
        calls.append(request.url.path)
        return httpx.Response(302, headers={'location': '/api/enterprises/' + ORG})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            c = D.Collector(client, cfg, Budget(cfg), BlobStore(tmp_path / 'state'))
            result = await c.request('/enterprises/' + ORG, ORG)
            assert result.status == 302
    asyncio.run(run()); assert calls == ['/enterprises/' + ORG]


def test_hard_company_cap_still_applies(tmp_path):
    cfg = config(tmp_path, [ORG]); budget = Budget(cfg); cfg.website_politeness_seconds = 0
    budget.cap = 100
    for _ in range(40): budget.reserve('https://data.brreg.no/', 'data.brreg.no', ORG)
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r: pytest.fail('HTTP beyond cap'))) as client:
            c = D.Collector(client, cfg, budget, BlobStore(tmp_path / 'state'))
            with pytest.raises(Exception, match='company_budget_exhausted'):
                await c.request('/enterprises/' + ORG, ORG)
    # A single-input pool is only 19: expand the synthetic pool while retaining the 40/company cap.
    asyncio.run(run())


def test_schedule_does_not_block_company_crawl(tmp_path, monkeypatch):
    cfg = config(tmp_path, [ORG]); started = asyncio.Event(); release = asyncio.Event()
    async def collect(self, r):
        started.set(); await release.wait()
    monkeypatch.setattr(D.Collector, 'collect', collect)
    async def run():
        async with httpx.AsyncClient() as client:
            c = D.Collector(client, cfg, Budget(cfg), BlobStore(tmp_path / 'state'))
            c.schedule(row()); await started.wait()
            assert not c.tasks[0].done()  # Main crawl can continue before DiBK completes.
            release.set(); await c.finish()
    asyncio.run(run())


def test_final_join_is_bounded_without_claiming_absence(tmp_path, monkeypatch):
    cfg = config(tmp_path, [ORG]); cancelled = []
    async def collect(self, r):
        try:
            await asyncio.sleep(30)
        except asyncio.CancelledError:
            cancelled.append(self.stop_reason); raise
    monkeypatch.setattr(D.Collector, 'collect', collect)
    async def run():
        async with httpx.AsyncClient() as client:
            c = D.Collector(client, cfg, Budget(cfg), BlobStore(tmp_path / 'state'))
            c.schedule(row()); await asyncio.sleep(0); await c.finish(max_wait=.01)
    asyncio.run(run()); assert cancelled == ['dibk_tail_timeout']
