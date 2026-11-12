from types import SimpleNamespace

import pytest

from signalpost.models.claim import Claim
from signalpost.refresh.diff import reconcile_final_observations


def row(state='ambiguous', claims=()):
    return SimpleNamespace(
        claims=list(claims),
        run=SimpleNamespace(sections={'website': state}, refresh={
            'observation_changes': [{'section': 'website', 'previous_state': 'ambiguous',
                                     'current_state': 'available', 'reason': 'website_candidates'}]}))


def test_provisional_accept_then_final_withhold_is_not_an_observation():
    # 897051982 pattern: guard withholds the provisional proof, exactly as before.
    previous = {'organisation_number': '897051982', 'claims': [],
                'run': {'sections': {'website': 'ambiguous'}}}
    current = row()
    reconcile_final_observations(current, previous)
    assert current.run.refresh['observation_changes'] == []
    assert current.run.sections == {'website': 'ambiguous'} and current.claims == []


@pytest.mark.parametrize('changed', ['state', 'claim'])
def test_final_publication_difference_keeps_observation(changed):
    previous = {'claims': [], 'run': {'sections': {'website': 'ambiguous'}}}
    current = row('available' if changed == 'state' else 'ambiguous')
    if changed == 'claim':
        current.claims = [Claim(field='website.section', value=None, availability='ambiguous',
            id='new', family='website', first_observed_at='now', last_observed_at='now')]
    reconcile_final_observations(current, previous)
    assert len(current.run.refresh['observation_changes']) == 1


def test_runner_reconciles_after_publication_guard(tmp_path, monkeypatch):
    from tests.test_websites import execute_web
    from signalpost.web import entity_scope
    attempted = []

    def withhold(rows, blobs, bulk):
        for current in rows:
            attempted.append(current.run.sections['website'])
            current.claims = [c for c in current.claims if c.family != 'website']
            current.run.sections['website'] = 'ambiguous'
            current.profile.values = {c.field: c.value for c in current.claims}

    monkeypatch.setattr(entity_scope, 'enforce', withhold)
    _, first, _, cfg = execute_web(tmp_path / 'first', monkeypatch)
    report, second, _, _ = execute_web(tmp_path / 'second', monkeypatch, previous=cfg.output)
    assert attempted == ['available', 'available']
    assert first['run']['sections']['website'] == second['run']['sections']['website'] == 'ambiguous'
    assert not any(c['field'] == 'official_website' for c in second['claims'])
    assert report['changes'] == 0 and report['observation_changes'] == 0
