import asyncio
import json
from datetime import datetime, timezone
import httpx
import pytest
from signalpost.budget import Budget
from signalpost.io.input_adapter import read
from signalpost.sources.nav_index import load, DEFAULT_PATH
from signalpost.web.entity_scope import foreign_entity_page
from signalpost.web.html import Page
from tests.test_registry import config, execute, handler, numbers
from tests.test_websites import execute_web, html, OUR, OTHER


def test_line_membership_including_blank_and_whitespace(tmp_path):
    cfg = config(tmp_path, [])
    cfg.organisations.write_text('923609017\n\n   \n 923 609 016 \n', encoding='utf8')
    inputs = read(cfg.organisations)
    assert inputs.rows == ['923609017', '', '', OUR]
    report, rows = execute(cfg)
    assert len(rows) == 4
    assert all(set(r['run']['sections'].values()) == {'failed'} for r in rows[:3])
    assert rows[3]['run']['sections']['identity'] == 'available'


@pytest.mark.parametrize('text,expected', [('', []), ('\n', ['']), ('   ', ['']),
                                          ('\n\n', ['', '']), ('923609016\n', [OUR])])
def test_plain_line_boundaries(tmp_path, text, expected):
    path = tmp_path / 'input.txt'
    path.write_text(text, encoding='utf8')
    assert read(path).rows == expected


def test_nonexistent_registry_identifier_still_emits_one(tmp_path):
    report, rows = execute(config(tmp_path, [numbers(1)[0]]), lambda r: httpx.Response(404))
    assert len(rows) == 1
    assert rows[0]['run']['sections']['identity'] == 'not_applicable'


def test_same_state_identical_refresh_and_actual_changed_values(tmp_path):
    cfg = config(tmp_path, [OUR])
    execute(cfg)
    previous = tmp_path / 'previous.jsonl'
    previous.write_bytes(cfg.output.read_bytes())
    cfg = cfg.model_copy(update={'previous': previous})
    before = set((cfg.state_dir / 'blobs').iterdir())
    report, rows = execute(cfg)
    assert report['changes'] == report['observation_changes'] == 0
    assert before <= set((cfg.state_dir / 'blobs').iterdir())
    report, rows = execute(cfg, handler(role_name='Person Two'))
    changes = rows[0]['changes']
    assert len(changes) == 1
    assert 'Person One' in json.dumps(changes[0]['old_value'])
    assert 'Person Two' in json.dumps(changes[0]['new_value'])


def test_shipped_index_valid_through_november_30_without_redating(tmp_path):
    cfg = config(tmp_path, [OUR])
    data, age = load(DEFAULT_PATH, cfg.nav_index_max_age_days,
                     now=datetime(2026, 11, 30, 23, 59, 59, tzinfo=timezone.utc))
    assert data['built_at'].startswith('2026-11-04')
    assert age < cfg.nav_index_max_age_days


@pytest.mark.parametrize('form', ['AB', 'ASA', 'Ltd', 'GmbH', 'Oy'])
def test_zinzino_foreign_entity_page_not_same_brand_proof(form):
    page = Page(html(extra=f'<h1>Zinzino {form}</h1><p>shares@zinzino.com</p>',
                     title=f'Zinzino {form} investor relations').encode(), 'https://zinzino.com/about')
    assert foreign_entity_page(page, OUR, 'Zinzino AS')


def test_different_orgnr_excludes_contacts_and_description(tmp_path, monkeypatch):
    body = html(extra='<h1>Other Company GmbH</h1><a href="mailto:shares@example.no">Email</a>',
                title='Other Company GmbH')
    _, row, _, _ = execute_web(tmp_path, monkeypatch, body)
    assert not any(c['field'].startswith(('contact.', 'website_description.')) for c in row['claims'])


def test_registry_domain_of_non_input_company_is_group_site(tmp_path, monkeypatch):
    bulk = tmp_path / 'registry.csv'
    bulk.write_text('organisasjonsnummer,navn,hjemmeside\n'
                    f'{OUR},Example AS,https://example.no/subsidiary\n'
                    f'{OTHER},Parent AS,https://www.example.no\n', encoding='utf8')
    body = html(extra='<meta name="description" content="Example makes many excellent synthetic products for local clients.">'
                      '<a href="https://facebook.com/example">Example</a>')
    _, row, _, _ = execute_web(tmp_path, monkeypatch, body, bulk=bulk)
    assert any(c['field'] == 'official_website' for c in row['claims'])
    assert row['run']['refresh']['website']['entity_scope']['other_registry_owners'] == [OTHER]
    assert not any(c['field'].startswith(('social_profile.', 'website_description.')) for c in row['claims'])


@pytest.mark.parametrize('form', ['AB', 'ASA', 'Ltd', 'GmbH', 'Oy'])
def test_zinzino_foreign_page_never_attaches_contacts_or_descriptions(tmp_path, monkeypatch, form):
    import tests.test_websites as fixtures
    original = fixtures.entity
    def zinzino(org):
        data = original(org)
        data['navn'] = 'Zinzino AS'
        return data
    monkeypatch.setattr(fixtures, 'entity', zinzino)
    body = html(title=f'Zinzino {form}', extra=(
        f'<meta name="description" content="Zinzino {form} provides shareholder and investor relations information worldwide.">'
        '<a href="mailto:shares@example.no">Investor contact</a>'))
    _, row, _, _ = execute_web(tmp_path, monkeypatch, body)
    assert any(c['field'] == 'official_website' for c in row['claims'])
    assert not any(c['field'].startswith(('contact.', 'website_description.')) for c in row['claims'])


@pytest.mark.parametrize('kwargs,published', [({}, True), ({'status': 'INACTIVE'}, False),
                                            ({'expired': True}, False), ({'employer': OTHER}, False),
                                            ({'employer': None}, False), ({'subunit': True, 'employer': '993578843'}, True)])
def test_published_nav_jobs_are_active_individual_exact_employer_ads(tmp_path, kwargs, published):
    from tests.test_nav import execute as nav_run
    _, row, _, _ = nav_run(tmp_path, **kwargs)
    jobs = [c['value'] for c in row['claims'] if c['field'].startswith('hiring.job.') and c['availability'] == 'available']
    assert bool(jobs) == published
    for job in jobs:
        assert job['status'] == 'ACTIVE'
        assert job['url'] == 'https://arbeidsplassen.nav.no/stillinger/stilling/' + job['uuid']
        assert job['employer_orgnr'] in {OUR, '993578843'}


@pytest.mark.parametrize('advance_clock', [False, True])
def test_every_site_timeout_preserves_100_outputs_and_hard_caps(tmp_path, monkeypatch, advance_clock):
    from signalpost.runner import run
    from signalpost.web import policy
    from signalpost.web.fetcher import WebsiteHttp
    async def public(*args): return ['93.184.216.34']
    async def no_delay(self): pass
    monkeypatch.setattr(policy, 'resolve_public', public)
    monkeypatch.setattr(WebsiteHttp, 'retry_pause', no_delay)
    cfg = config(tmp_path, numbers(100), websites=True, time_budget_seconds=999999).model_copy(
        update={'website_politeness_seconds': 0})
    import time
    from types import SimpleNamespace
    from signalpost import budget as budget_module
    began = time.monotonic()
    clock = [began]
    if advance_clock:
        monkeypatch.setattr(budget_module, 'time', SimpleNamespace(monotonic=lambda: clock[0]))
    def respond(request):
        if request.url.host == 'data.brreg.no': return handler()(request)
        if advance_clock:
            clock[0] += 12  # Each admitted timeout consumes its full retry timeout.
        raise httpx.ReadTimeout('synthetic all-sites timeout', request=request)
    async def invoke():
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            return await run(cfg, client=client)
    report = asyncio.run(invoke())
    assert len(cfg.output.read_text().splitlines()) == 100
    assert report['requests'] <= 1800
    assert report['limits']['hard_time_budget_seconds'] == 2400
    assert max(r['operations']['requests'] for r in map(json.loads, cfg.output.read_text().splitlines())) <= 18
    if advance_clock:
        assert clock[0] - began <= 2400
        assert any(e['code'] == 'deadline' for r in map(json.loads, cfg.output.read_text().splitlines()) for e in r['errors'])


def test_full_feed_fallback_cannot_escape_global_cap_or_skip_inputs(tmp_path):
    from signalpost.runner import run
    from tests.test_nav import TOKEN
    from uuid import UUID
    cfg = config(tmp_path, numbers(100), hiring=True, max_requests=420, nav_max_pages=10000)
    pages = [0]
    def respond(request):
        if request.url.host == 'data.brreg.no': return handler()(request)
        if request.url.path == '/api/publicToken': return httpx.Response(200, text=TOKEN)
        pages[0] += 1
        return httpx.Response(200, json={'items': [], 'next_url':
            'https://pam-stilling-feed.nav.no/api/v1/feed/' + str(UUID(int=pages[0]))})
    async def invoke():
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            return await run(cfg, client=client)
    report = asyncio.run(invoke())
    assert len(cfg.output.read_text().splitlines()) == 100
    assert 0 < pages[0] <= 420
    assert report['requests'] <= 420 < 1800
    assert report['hiring_prefetch']['source_mode'] == 'full_feed_fallback'
    assert not report['hiring_prefetch']['complete']
