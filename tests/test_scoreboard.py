"""Benchmark counting must preserve failures, meaningful zeroes and deduplication."""
import copy

import pytest

from scripts.scoreboard import SECTIONS, build_scoreboard


def fixture():
    def claim(field, family, value, period=None):
        return {'field': field, 'family': family, 'value': value,
                'availability': 'available', 'reporting_period': period}

    states = {family: 'not_available' for family, _ in SECTIONS.values() if family != 'social'}
    first = {'organisation_number': '923609016', 'run': {'sections': {
        **states, 'identity': 'available', 'accounts': 'available', 'website': 'available'}},
        'claims': [claim('identity.latest_submitted_accounts', 'identity', '2025'),
                   claim('accounts.revenue', 'accounts', 0, {'fiscal_year': '2025'}),
                   claim('accounts.revenue', 'accounts', 0, {'fiscal_year': '2025'}),
                   claim('accounts.history.2024.revenue', 'accounts', 12, {'fiscal_year': '2024'}),
                   claim('official_website', 'website', {'final_url': 'https://example.no'}),
                   claim('social_profile.example', 'website', {'url': 'https://linkedin.com/company/example'}),
                   claim('contact.opted_out', 'website', False),
                   claim('contact.missing', 'website', None)],
        'errors': [{'section': 'website', 'code': 'website_budget_exhausted'},
                   {'section': 'website', 'code': 'website_budget_exhausted'}]}
    second = {'organisation_number': '993578843', 'run': {'sections': {
        **states, 'website': 'ambiguous', 'accounts': 'failed'}}, 'claims': [],
        'errors': [{'section': 'accounts', 'code': 'deadline'}]}
    rows = [first, second]
    profiles = [{'organisation_number': row['organisation_number'], 'evidence': {
        key: {'status': {'not_available': 'not_found', 'failed': 'source_error',
                         'ambiguous': 'source_error'}.get(row['run']['sections'][family],
                                                        row['run']['sections'][family])}
        for family, key in SECTIONS.values() if key}} for row in rows]
    report = {'emitted_envelopes': 2, 'runtime_ms': 2000, 'requests': 7,
              'deadline_hits': 1, 'warnings': ['example warning']}
    return rows, report, profiles


def test_scoreboard_counts_preserve_scope_and_meaningful_values():
    rows, report, profiles = fixture()
    score = build_scoreboard(rows, report, profiles, {'wall_seconds': 3.5})
    assert score['sections']['financials']['distinct_facts'] == 2
    assert score['sections']['website']['distinct_facts'] == 2  # site + false; not social/null
    assert score['sections']['social']['distinct_facts'] == 1
    assert score['sections']['website']['states']['ambiguous'] == 1
    assert score['sections']['website']['states']['failed'] == 0
    assert score['sections']['website']['profile_states']['source_error'] == 1
    assert score['sections']['social']['states']['ambiguous'] == 1
    assert score['sections']['financials']['states']['failed'] == 1
    assert score['sections']['financials']['states']['deadline'] == 0
    assert score['sections']['financials']['error_conditions']['deadline'] == 1
    assert score['website_budget_exhausted_count'] == 1
    assert score['latest_year_accounts_count'] == score['registry_latest_year_matched_count'] == 1
    assert score['wall_seconds'] == 3.5
    assert score['wall_seconds_source'] == 'execution'
    assert score['warnings'] == ['example warning']
    fallback = build_scoreboard(rows, report, profiles)
    assert fallback['wall_seconds'] == 2
    assert fallback['wall_seconds_source'] == 'report_runtime_ms'


@pytest.mark.parametrize('mismatch', ['profile_order', 'report_count'])
def test_scoreboard_rejects_mismatched_output_membership(mismatch):
    rows, report, profiles = copy.deepcopy(fixture())
    if mismatch == 'profile_order':
        profiles.reverse()
    else:
        report['emitted_envelopes'] = 1
    with pytest.raises(ValueError):
        build_scoreboard(rows, report, profiles)
