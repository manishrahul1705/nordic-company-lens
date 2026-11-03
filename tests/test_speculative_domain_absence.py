import asyncio
import json
from types import SimpleNamespace

import pytest

from signalpost.budget import SourceFailure
from signalpost.web import collector
from signalpost.web.candidates import Candidate


@pytest.mark.parametrize('origins,errors,expected', [
    ([], [], 'not_available'),
    (['legal_name_slug', 'legal_name_slug'], ['no_such_domain', 'no_such_domain'], 'not_available'),
    (['registry_website'], ['no_such_domain'], 'failed'),
    (['registry_email'], ['no_such_domain'], 'failed'),
    (['nav_employer_homepage'], ['website_timeout'], 'failed'),
    (['legal_name_slug', 'registry_website'], ['no_such_domain', 'website_connect_error'], 'failed'),
])
def test_absent_guesses_do_not_hide_known_source_failures(monkeypatch, origins, errors, expected):
    candidates = [Candidate(f'https://candidate{i}.no', f'candidate{i}.no', origin)
                  for i, origin in enumerate(origins)]
    failures = {candidate.domain: error for candidate, error in zip(candidates, errors)}
    monkeypatch.setattr(collector, 'generate', lambda context: candidates)
    monkeypatch.setattr(collector, 'registry_context', lambda *args: ({'name': 'Example AS'}, None, None))

    async def candidate(candidate, org, proved):
        raise SourceFailure(failures[candidate.domain])

    http = SimpleNamespace(blobs=None, attempts={}, candidate=candidate)
    env = SimpleNamespace(claims=[], run=SimpleNamespace(refresh={}))
    result = asyncio.run(collector.fetch('923609016', env, None, http))
    assert result.state == expected
    diagnostics = next(e for e in result.errors if e.code == 'website_candidates')
    assert [attempt['reason'] for attempt in json.loads(diagnostics.message)] == errors
    assert any(e.code == 'website_source_unavailable' for e in result.errors) == (expected == 'failed')
    assert not result.claims
