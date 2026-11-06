"""Deterministic regression suite for Stage 3C-R2: NAV freshness, offline safety and boundary handling."""
import asyncio
import gzip
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
import httpx
import pytest

from signalpost.budget import Budget, SourceFailure
from signalpost.config import Config
from signalpost.models.evidence import utc_now
from signalpost.runner import placeholder
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.extract import Section, Source, add
from signalpost.sources.nav import BASE, Index, prefetch, section
from signalpost.sources.nav_index import DEFAULT_PATH, load, write, validate, AD_FIELDS
from tests.test_registry import config
from tests.test_nav import ORG, OTHER, SUB, TOKEN, UUID
from tests.test_nav_streaming import header, ad, SECOND


def artifact(tmp_path, ads=None, built_at=None, **overrides):
    now = built_at or utc_now()
    ads = ads if ads is not None else [{
        'uuid': UUID, 'employer_orgnr': ORG, 'status': 'ACTIVE',
        'published': '2026-10-01T00:00:00Z', 'expires': '2099-01-01T00:00:00Z',
        'last_modified': '2026-10-01T00:00:00Z', 'etag': None
    }]
    data = {
        'schema_version': 1, 'index_version': 'test-v1', 'built_at': now,
        'cursor': BASE + '/api/v1/feed/' + UUID,
        'source_urls': [BASE + '/api/v1/feed', BASE + '/api/v1/feedentry/{uuid}'],
        'ads_count': len(ads), 'employer_count': len({a['employer_orgnr'] for a in ads}),
        'failed_details': 0, 'seeded_from_disk': len(ads), 'fresh_fetched_ads': 0,
        'ads': ads, **overrides
    }
    path = tmp_path / 'index.json.gz'
    write(path, data)
    return path, data


async def run_nav(cfg, path, details=None, items=None, scopes=None, token_ok=True,
                  network_fail=False, now=None):
    index = Index()
    blobs = BlobStore(cfg.state_dir)
    calls = []

    async def names():
        return {ORG: {'Rareone AS'}}

    async def scope():
        return scopes or {ORG: {ORG}}

    names.initial_names = {ORG: {'Rareone AS'}}
    names.scopes_ready = scope

    def response(request):
        calls.append(request.url.path)
        if network_fail:
            raise httpx.ConnectError("Network offline", request=request)
        if request.url.path == '/api/publicToken':
            return httpx.Response(200, text=TOKEN if token_ok else 'not available')
        if '/feedentry/' in request.url.path:
            uuid = request.url.path.rsplit('/', 1)[-1]
            val = (details or {}).get(uuid, ad(uuid, ORG))
            return httpx.Response(503, json={}) if val is None else httpx.Response(200, json=val)
        return httpx.Response(200, json={'items': items or [], 'next_url': None})

    async with httpx.AsyncClient(transport=httpx.MockTransport(response)) as client:
        await prefetch(client, cfg, Budget(cfg), blobs, index, names, now=now)

    row = placeholder(ORG, 'test', utc_now(), ('identity', 'roles', 'subunits', 'accounts', 'hiring'))
    row.run.sections['subunits'] = 'not_available'
    if scopes and SUB in scopes[ORG]:
        s = Section()
        body = json.dumps({'unit': SUB}).encode()
        sha = blobs.put(body)
        add(s, Source('https://data.brreg.no/example', body, sha, utc_now()),
            ORG, 'subunits', 'subunits.unit.' + SUB, {'organisation_number': SUB}, '/unit')
        row.claims.extend(s.claims)
        row.evidence.extend(s.evidence)
        row.run.sections['subunits'] = 'available'

    result = section(row, index, blobs, now=now)
    return index, result, calls


# 1. 20-day index age boundary
def test_boundary_20_days_valid(tmp_path):
    fixed_now = datetime(2026, 11, 3, 12, 0, 0, tzinfo=timezone.utc)
    built = fixed_now - timedelta(days=20)
    path, data = artifact(tmp_path, built_at=built.isoformat())

    loaded, age = load(path, max_age_days=21, now=fixed_now)
    assert age == pytest.approx(20.0, abs=0.01)
    assert loaded['index_version'] == 'test-v1'

    cfg = config(tmp_path, [ORG], hiring=True, nav_index_path=path)
    index, result, calls = asyncio.run(run_nav(cfg, path, now=fixed_now))
    assert index.metrics['source_mode'] == 'declared_index'
    assert result.state == 'available'
    assert len(result.claims) == 1
    assert result.claims[0].value['status'] == 'ACTIVE'


# 2. Exactly 21 days boundary
def test_boundary_exactly_21_days_boundary(tmp_path):
    fixed_now = datetime(2026, 11, 4, 4, 26, 40, tzinfo=timezone.utc)
    built = fixed_now - timedelta(days=21)
    path, data = artifact(tmp_path, built_at=built.isoformat())

    loaded, age = load(path, max_age_days=21, now=fixed_now)
    assert age == pytest.approx(21.0, abs=0.001)

    cfg = config(tmp_path, [ORG], hiring=True, nav_index_path=path)
    index, result, calls = asyncio.run(run_nav(cfg, path, now=fixed_now))
    assert index.metrics['source_mode'] == 'declared_index'
    assert result.state == 'available'


# 3. 21 days plus 1 second boundary
def test_boundary_21_days_plus_1sec_stale(tmp_path):
    fixed_now = datetime(2026, 11, 4, 4, 26, 41, tzinfo=timezone.utc)
    built = fixed_now - timedelta(days=21, seconds=1)
    path, data = artifact(tmp_path, built_at=built.isoformat())

    # Without snapshot permission, load must fail with index_stale
    with pytest.raises(SourceFailure, match='index_stale'):
        load(path, max_age_days=21, now=fixed_now, allow_historical_snapshot=False)

    # With snapshot permission, load succeeds
    loaded, age = load(path, max_age_days=21, now=fixed_now, allow_historical_snapshot=True)
    assert age > 21.0

    # In historical snapshot mode, prefetch marks mode and dating
    cfg = config(tmp_path, [ORG], hiring=True, nav_index_path=path, nav_historical_snapshot=True, nav_index_max_age_days=21)
    index, result, calls = asyncio.run(run_nav(cfg, path, now=fixed_now))
    assert index.metrics['source_mode'] == 'historical_snapshot'
    assert result.state == 'available'
    assert result.claims[0].value['status'] == 'HISTORICAL_SNAPSHOT'
    assert result.claims[0].reasons['dating'] == 'historical_snapshot_as_of_' + data['built_at']


# 4. 22 days boundary
def test_boundary_22_days_stale(tmp_path):
    fixed_now = datetime(2026, 11, 5, 0, 0, 0, tzinfo=timezone.utc)
    built = fixed_now - timedelta(days=22)
    path, data = artifact(tmp_path, built_at=built.isoformat())

    with pytest.raises(SourceFailure, match='index_stale'):
        load(path, max_age_days=21, now=fixed_now)

    cfg = config(tmp_path, [ORG], hiring=True, nav_index_path=path, nav_index_max_age_days=21)
    index, result, calls = asyncio.run(run_nav(cfg, path, now=fixed_now))
    assert index.metrics['source_mode'] == 'full_feed_fallback'
    assert index.metrics['index_fallback_reason'] == 'index_stale'


# 5. 30 days boundary
def test_boundary_30_days_stale(tmp_path):
    fixed_now = datetime(2026, 11, 13, 0, 0, 0, tzinfo=timezone.utc)
    built = fixed_now - timedelta(days=30)
    path, data = artifact(tmp_path, built_at=built.isoformat())

    with pytest.raises(SourceFailure, match='index_stale'):
        load(path, max_age_days=21, now=fixed_now)


# 6. Index corruption
def test_boundary_index_corruption(tmp_path):
    corrupt_gz = tmp_path / 'corrupt.json.gz'
    corrupt_gz.write_bytes(b'not a valid gzip stream')
    with pytest.raises(SourceFailure, match='index_invalid'):
        load(corrupt_gz)

    path, data = artifact(tmp_path)
    with pytest.raises(SourceFailure, match='index_version_invalid'):
        validate({**data, 'schema_version': 2})
    with pytest.raises(SourceFailure, match='index_cursor_invalid'):
        validate({**data, 'cursor': BASE + '/api/v1/feed'})
    with pytest.raises(SourceFailure, match='index_counts_invalid'):
        validate({**data, 'ads_count': len(data['ads']) + 1})


# 7. Offline network failure -> Unavailable source mode (never falsely reports zero hiring)
def test_boundary_offline_network_failure_unavailable_mode(tmp_path):
    fixed_now = datetime(2026, 11, 10, 0, 0, 0, tzinfo=timezone.utc)
    built = fixed_now - timedelta(days=25)
    path, data = artifact(tmp_path, built_at=built.isoformat())

    cfg = config(tmp_path, [ORG], hiring=True, nav_index_path=path)
    index, result, calls = asyncio.run(run_nav(cfg, path, network_fail=True, now=fixed_now))
    assert result.state in {'failed', 'blocked'}
    assert result.state != 'not_available'
    assert not result.claims
    assert any(e.section == 'hiring' for e in result.errors)


# 8. Public token and unverifiable public page -> failed mode, never zero hiring
def test_boundary_public_token_failure_and_unverifiable_page_fail_closed(tmp_path):
    path, data = artifact(tmp_path)
    cfg = config(tmp_path, [ORG], hiring=True, nav_index_path=path)
    index, result, calls = asyncio.run(run_nav(cfg, path, token_ok=False))
    assert index.reason == 'token_unavailable'
    assert index.blocked is False  # An indexed candidate exists, but the public page did not verify.
    assert index.metrics['public_page_fallback_attempted'] is True
    assert index.metrics['public_page_fallback_verified'] == 0
    assert result.state == 'failed'
    assert result.state != 'not_available'
    assert not result.claims
    assert any(e.code == 'token_unavailable' for e in result.errors)


# 9. Expired advertisements filtered
def test_boundary_expired_ads_filtered(tmp_path):
    fixed_now = datetime(2026, 10, 20, 12, 0, 0, tzinfo=timezone.utc)
    expired_time = (fixed_now - timedelta(days=1)).isoformat()
    path, data = artifact(tmp_path, built_at=(fixed_now - timedelta(days=2)).isoformat())
    cfg = config(tmp_path, [ORG], hiring=True, nav_index_path=path)

    expired_ad = ad(UUID, ORG)
    expired_ad['ad_content']['expires'] = expired_time

    index, result, calls = asyncio.run(run_nav(cfg, path, details={UUID: expired_ad}, now=fixed_now))
    assert not result.claims
    assert UUID in index.live_closed


# 10. Explicit INACTIVE advertisements filtered
def test_boundary_inactive_ads_filtered(tmp_path):
    path, data = artifact(tmp_path)
    cfg = config(tmp_path, [ORG], hiring=True, nav_index_path=path)

    inactive_ad = ad(UUID, ORG)
    inactive_ad['status'] = 'INACTIVE'

    index, result, calls = asyncio.run(run_nav(cfg, path, details={UUID: inactive_ad}))
    assert not result.claims
    assert UUID in index.live_closed


# 11. Newly published advertisements in future rejected
def test_boundary_future_published_rejected(tmp_path):
    fixed_now = datetime(2026, 10, 20, 12, 0, 0, tzinfo=timezone.utc)
    future_pub = (fixed_now + timedelta(days=2)).isoformat()
    path, data = artifact(tmp_path, built_at=(fixed_now - timedelta(days=2)).isoformat())
    cfg = config(tmp_path, [ORG], hiring=True, nav_index_path=path)

    future_ad = ad(UUID, ORG)
    future_ad['ad_content']['published'] = future_pub

    index, result, calls = asyncio.run(run_nav(cfg, path, details={UUID: future_ad}, now=fixed_now))
    assert not result.claims
    assert index.metrics.get('detail_failures', {}).get('nav_invalid_dates', 0) > 0


# 12. Verified employer parent match
def test_boundary_employer_parent_matching(tmp_path):
    path, data = artifact(tmp_path)
    cfg = config(tmp_path, [ORG], hiring=True, nav_index_path=path)
    index, result, calls = asyncio.run(run_nav(cfg, path))
    assert result.state == 'available'
    assert len(result.claims) == 1
    assert result.claims[0].value['employer_orgnr'] == ORG
    assert 'organisation ' + ORG in result.claims[0].value['matched_via']


# 13. Verified subunit match
def test_boundary_subunit_matching(tmp_path):
    ad_sub = {'uuid': UUID, 'employer_orgnr': SUB, 'status': 'ACTIVE',
              'published': None, 'expires': None, 'last_modified': None, 'etag': None}
    path, data = artifact(tmp_path, [ad_sub])
    cfg = config(tmp_path, [ORG], hiring=True, nav_index_path=path)
    index, result, calls = asyncio.run(run_nav(cfg, path, details={UUID: ad(UUID, SUB)}, scopes={ORG: {ORG, SUB}}))
    assert result.state == 'available'
    assert len(result.claims) == 1
    assert result.claims[0].value['employer_orgnr'] == SUB
    assert result.claims[0].value['matched_via'] == 'subunit ' + SUB


# 14. Wrong employer organization number rejected
def test_boundary_wrong_employer_orgnr_rejection(tmp_path):
    path, data = artifact(tmp_path)
    cfg = config(tmp_path, [ORG], hiring=True, nav_index_path=path)
    # Detail returns employer OTHER instead of ORG
    index, result, calls = asyncio.run(run_nav(cfg, path, details={UUID: ad(UUID, OTHER)}))
    assert not result.claims
    assert result.state == 'not_available'


# 15. Duplicate advertisements deduplication
def test_boundary_duplicate_ad_deduplication(tmp_path):
    # Two identical ad entries or shared across parents/subunits
    ad_parent = {'uuid': UUID, 'employer_orgnr': ORG, 'status': 'ACTIVE',
                 'published': None, 'expires': None, 'last_modified': None, 'etag': None}
    path, data = artifact(tmp_path, [ad_parent])
    cfg = config(tmp_path, [ORG], hiring=True, nav_index_path=path)
    index, result, calls = asyncio.run(run_nav(cfg, path, scopes={ORG: {ORG, SUB}}))
    assert len(result.claims) == 1
    assert len([c for c in result.claims if c.value['uuid'] == UUID]) == 1


# 16. Repeated refresh closure proof
def test_boundary_repeated_refresh_no_unverified_carry(tmp_path):
    from signalpost.runner import run
    from tests.test_registry import handler
    path, _ = artifact(tmp_path)

    async def execute_run(label, value, previous=None):
        cfg = config(tmp_path / label, [ORG], hiring=True, nav_index_path=path, previous=previous)
        def response(request):
            if request.url.host != 'pam-stilling-feed.nav.no':
                return handler()(request)
            if request.url.path == '/api/publicToken':
                return httpx.Response(200, text=TOKEN)
            if '/feedentry/' in request.url.path:
                return httpx.Response(503, json={}) if value is None else httpx.Response(200, json=value)
            return httpx.Response(200, json={'items': [], 'next_url': None})
        async with httpx.AsyncClient(transport=httpx.MockTransport(response)) as client:
            rep = await run(cfg, client)
        return cfg, json.loads(cfg.output.read_text()), rep

    first, _, _ = asyncio.run(execute_run('run1', ad(UUID, ORG)))
    _, closed, _ = asyncio.run(execute_run('run2', {'uuid': UUID, 'status': 'INACTIVE'}, first.output))
    event = next(e for e in closed['changes'] if e['type'] == 'closed_job')
    assert event['new_evidence_ids'] and event['new_content_sha256']
    assert not any(c['family'] == 'hiring' and c['availability'] == 'available' for c in closed['claims'])


# 17. Historical Snapshot Mode: zero hiring absence is unsupported
def test_boundary_historical_snapshot_mode_absence_unsupported(tmp_path):
    fixed_now = datetime(2026, 11, 10, 0, 0, 0, tzinfo=timezone.utc)
    built = fixed_now - timedelta(days=25)
    # Index with NO ads for ORG
    path, data = artifact(tmp_path, ads=[], built_at=built.isoformat())

    cfg = config(tmp_path, [ORG], hiring=True, nav_index_path=path, nav_historical_snapshot=True, nav_index_max_age_days=21)
    index, result, calls = asyncio.run(run_nav(cfg, path, now=fixed_now))
    assert index.metrics['source_mode'] == 'historical_snapshot'
    assert not result.claims
    # Must report failed with absence unsupported, NOT not_available!
    assert result.state == 'failed'
    assert any(e.code == 'historical_snapshot_absence_unsupported' for e in result.errors)
