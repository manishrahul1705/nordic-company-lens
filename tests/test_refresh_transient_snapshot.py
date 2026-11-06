"""A failed transport attempt must not replace the last supported snapshot."""
import json

import pytest

from signalpost.models.envelope import Error
from signalpost.models.shapes import serialize
from signalpost.refresh.diff import apply
from signalpost.runner import placeholder, update
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.extract import Section, Source, add, missing

ORG = '923609016'
FIRST = '2026-11-05T12:00:00Z'
SECOND = '2026-11-06T12:00:00Z'


def snapshot(tmp_path, state='available'):
    blobs = BlobStore(tmp_path)
    row = placeholder(ORG, 'first', FIRST, ('website', 'activity'))
    section = Section(state=state)
    if state == 'available':
        body = b'Org nr 923609016'
        source = Source('https://example.no/', body, blobs.put(body), FIRST)
        add(section, source, ORG, 'website', 'official_website',
            {'final_url': 'https://example.no', 'identity_level': 'VERIFIED'},
            'footer', span=body.decode(), source_class='company_owned')
    update(row, 'website', section)
    update(row, 'activity', Section(state='not_available'))
    row.run.refresh = {'website': {'checked_urls': ['https://example.no/']}}
    return row, blobs


@pytest.mark.parametrize('state', ['available', 'not_available', 'ambiguous'])
@pytest.mark.parametrize('reason', ['website_timeout', 'dns_timeout', 'dns_servfail',
                                   'no_such_domain', 'connection_reset', 'website_tls_error'])
def test_transient_attempt_restores_entire_previous_section(tmp_path, state, reason):
    previous, blobs = snapshot(tmp_path, state)
    current = previous.model_copy(deep=True)
    current.run.completed_at = SECOND
    update(current, 'website', missing('website', 'website_source_unavailable'))
    current.errors.append(Error(section='website', code='website_candidates',
                                message=json.dumps([{'domain': 'example.no', 'reason': reason}])))
    current.run.refresh['website'] = {'checked_urls': []}
    prior = [c for c in previous.claims if c.family == 'website']
    apply(current, serialize(previous, 'union'), blobs)
    carried = [c for c in current.claims if c.family == 'website']
    assert current.run.sections['website'] == state
    assert [(c.id, c.value, c.availability, c.evidence_ids) for c in carried] == [
        (c.id, c.value, c.availability, c.evidence_ids) for c in prior]
    assert all(c.carried_forward and c.stale_since == SECOND for c in carried)
    assert {e.id for e in previous.evidence} <= {e.id for e in current.evidence}
    assert current.run.refresh['website']['checked_urls'] == ['https://example.no/']
    stale = current.run.refresh['stale_sections']['website']
    assert stale['previous_state'] == state and stale['attempt_state'] == 'failed'
    assert stale['failed_attempt_at'] == SECOND and stale['failure_codes'] == [reason]
    assert not current.changes and not current.run.refresh['observation_changes']


def test_website_failure_restores_dependent_activity_absence(tmp_path):
    previous, blobs = snapshot(tmp_path, 'not_available')
    current = previous.model_copy(deep=True)
    current.run.completed_at = SECOND
    update(current, 'website', missing('website', 'dns_timeout'))
    update(current, 'activity', missing('activity', 'website_check_incomplete'))
    apply(current, serialize(previous, 'union'), blobs)
    assert current.run.sections == previous.run.sections
    assert sorted(c.id for c in current.claims) == sorted(c.id for c in previous.claims)
    assert set(current.run.refresh['stale_sections']) == {'website', 'activity'}
    assert not current.changes and not current.run.refresh['observation_changes']


def test_first_attempt_has_no_snapshot_to_restore(tmp_path):
    current, blobs = snapshot(tmp_path)
    update(current, 'website', missing('website', 'dns_timeout'))
    apply(current, None, blobs)
    assert current.run.sections['website'] == 'failed'
    assert 'stale_sections' not in current.run.refresh


@pytest.mark.parametrize('reason', ['http_404', 'http_410', 'gone'])
def test_proven_gone_is_not_hidden_by_an_unrelated_timeout(tmp_path, reason):
    previous, blobs = snapshot(tmp_path)
    current = previous.model_copy(deep=True)
    update(current, 'website', Section(state='not_available'))
    current.errors.append(Error(section='website', code='website_candidates', message=json.dumps([
        {'domain': 'example.no', 'reason': reason},
        {'domain': 'another.no', 'reason': 'dns_timeout'}])))
    apply(current, serialize(previous, 'union'), blobs)
    assert not current.run.refresh['stale_sections']
    assert any(c.type == 'removed' and c.field == 'official_website' for c in current.changes)


def test_owner_conflict_overrides_transient_failures(tmp_path):
    previous, blobs = snapshot(tmp_path)
    current = previous.model_copy(deep=True)
    current.claims = [c for c in current.claims if c.family != 'website']
    update(current, 'website', missing('website', 'website_timeout'))
    current.run.refresh['website']['refuted_previous_website'] = True
    apply(current, serialize(previous, 'union'), blobs)
    assert current.run.sections['website'] == 'failed'
    assert not any(c.field == 'official_website' for c in current.claims)
    assert not current.run.refresh['stale_sections']


def test_successful_new_value_is_not_hidden_by_optional_page_timeout(tmp_path):
    previous, blobs = snapshot(tmp_path)
    current = previous.model_copy(deep=True)
    claim = next(c for c in current.claims if c.field == 'official_website')
    claim.value = {**claim.value, 'final_url': 'https://replacement.no'}
    current.errors.append(Error(section='website', code='website_timeout', message='optional page'))
    apply(current, serialize(previous, 'union'), blobs)
    assert not current.run.refresh['stale_sections']
    assert any(c.field == 'official_website' and c.type == 'changed' for c in current.changes)


def test_same_command_absence_then_timeout_has_identical_claim_ids(tmp_path, monkeypatch):
    import httpx
    from tests.test_websites import execute_web
    from signalpost.web import collector
    from signalpost.web.candidates import Candidate
    monkeypatch.setattr(collector, 'generate', lambda context: [
        Candidate('https://example.no/', 'example.no', 'registry_website')])

    def absent(request):
        return httpx.Response(200, text='User-agent: *\nAllow: /') if request.url.path == '/robots.txt' else httpx.Response(404)

    def timeout(request):
        raise httpx.ReadTimeout('fixture timeout', request=request)

    _, before, _, _ = execute_web(tmp_path, monkeypatch, response=absent)
    assert before['run']['sections']['website'] == 'not_available'
    report, after, _, _ = execute_web(tmp_path, monkeypatch, response=timeout)
    assert after['run']['refresh']['previous_run_id'] == before['run_id']
    assert after['run']['sections']['website'] == 'not_available'
    assert sorted(c['id'] for c in before['claims']) == sorted(c['id'] for c in after['claims'])
    assert report['changes'] == report['observation_changes'] == 0
    assert after['run']['refresh']['stale_sections']['website']['failed_attempt_at'] == after['run']['completed_at']


def test_tls_failed_refresh_retains_verified_snapshot(tmp_path, monkeypatch):
    import httpx
    from tests.test_websites import execute_web
    _, before, _, cfg = execute_web(tmp_path / 'baseline', monkeypatch)

    def tls_failure(request):
        raise httpx.ConnectError('TLS handshake failed', request=request)

    report, after, _, _ = execute_web(tmp_path / 'refresh', monkeypatch,
                                    response=tls_failure, previous=cfg.output)
    assert after['run']['sections']['website'] == 'available'
    assert 'website_tls_error' in after['run']['refresh']['stale_sections']['website']['failure_codes']
    assert report['changes'] == report['observation_changes'] == 0
    assert sorted(c['id'] for c in before['claims']) == sorted(c['id'] for c in after['claims'])
