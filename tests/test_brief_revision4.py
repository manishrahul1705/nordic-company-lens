"""Revision 4: what changed, what remains unknown and what the company does."""
import json

import pytest

from signalpost.models.envelope import Error
from signalpost.synthesis.company_brief import generate, validate, dated_events, registry_event
from signalpost.synthesis.template import generate as template_generate, brief_summary
from tests.test_synthesis import envelope


def add(row, field, value, family='activity'):
    seed = next(c for c in row.claims if c.field == 'identity.legal_name')
    claim = seed.model_copy(update={'id': 'r4-' + field, 'field': field, 'value': value, 'family': family})
    row.claims.append(claim)
    return claim


@pytest.fixture
def permit(monkeypatch):
    from signalpost.synthesis import validate as gate
    original = gate.permitted
    monkeypatch.setattr(gate, 'permitted', lambda c, e: c.id.startswith('r4-') or original(c, e))


def announcement(**extra):
    return {'company_orgnr': '923609016', 'event_id': extra.pop('event_id', 1), 'date': extra.pop('date', '2026-07-14T18:02:01Z'),
            'kind': 'Registry announcement', 'title': extra.pop('title', 'Registry change'),
            'url': 'https://data.brreg.no/enhetsregisteret/api/oppdateringer/enheter?oppdateringsid=1', **extra}


def test_registry_events_are_tiered_and_bare_records_never_count():
    assert registry_event(announcement(changed_field='/navn', new_value='NEW NAME AS'))[:2] == (1, 'name')
    assert registry_event(announcement(changed_field='/forretningsadresse', new_value={'adresse': ['Gate 1'], 'postnummer': '0150', 'poststed': 'OSLO'}))[2] \
        == 'a new business address (Gate 1, 0150 Oslo)'
    assert registry_event(announcement(changed_field='/sisteInnsendteAarsregnskap', new_value='2025'))[:2] == (2, 'accounts')
    assert registry_event(announcement(subunit_orgnr='988258229', event_type='Ny'))[:2] == (1, 'workplace_new')
    for bare in [announcement(title='Registry update recorded', event_type='Endring'),
                 announcement(subunit_orgnr='988258229', event_type='Endring'),
                 announcement(title='Registry event recorded (type unspecified)', event_type='Ukjent'),
                 announcement(changed_field='/registreringsdatoAntallAnsatteNAVAaregisteret', new_value='2026-11-10'),
                 announcement(changed_field='/kapital/innfortDato', new_value='2020-01-01')]:
        assert registry_event(bare) is None


def test_changes_cite_dated_announcements_and_replace_first_observation(tmp_path, permit):
    row, _ = envelope(tmp_path)
    synthesis = row.run.synthesis
    assert row.run.refresh['mode'] == 'baseline'
    before = generate(synthesis, row)
    assert [s.text for s in before.changes] == ['First observation; no previous snapshot and no dated changes in the checked sources.']
    address = add(row, 'registry_change.addr', announcement(event_id=2, date='2026-02-12T10:00:00Z', changed_field='/forretningsadresse',
                                                              new_value={'adresse': ['Gate 1'], 'postnummer': '0150', 'poststed': 'OSLO'}))
    filed = [add(row, 'registry_change.acc' + y, announcement(event_id=10 + int(y[-1]), date=y + '-07-15T18:02:01Z',
                                                              changed_field='/sisteInnsendteAarsregnskap', new_value=str(int(y) - 1)))
             for y in ('2025', '2026')]
    add(row, 'registry_change.bare', announcement(event_id=3, date='2026-11-01T10:00:00Z', title='Registry update recorded', event_type='Endring'))
    brief = generate(synthesis, row)
    texts = [s.text for s in brief.changes]
    assert texts == ['A registry announcement on 15 Jul 2026 records that annual accounts for 2025 were filed.',
                     'A registry announcement on 12 Feb 2026 records a new business address (Gate 1, 0150 Oslo).']
    assert brief.changes[0].claim_ids == [filed[1].id] and brief.changes[1].claim_ids == [address.id]
    assert not any('First observation' in t for t in texts)
    assert validate(brief, synthesis, row) == brief


def test_events_are_capped_newest_first_one_per_category(permit, tmp_path):
    row, _ = envelope(tmp_path)
    for n, (path, day) in enumerate([('/navn', '2024-01-02'), ('/kapital/belop', '2025-03-04'), ('/postadresse', '2026-05-06'),
                                     ('/forretningsadresse', '2023-01-01'), ('/postadresse', '2026-06-01')]):
        add(row, f'registry_change.{n}', announcement(event_id=n, date=day + 'T00:00:00Z', changed_field=path, new_value=1 if 'kapital' in path else None))
    events = dated_events([c for c in row.claims if c.id.startswith('r4-')])
    assert len(events) == 3
    assert [e['date'] for e in events] == sorted([e['date'] for e in events], reverse=True)
    assert len({e['category'] for e in events}) == 3


def test_what_states_purpose_and_never_asserts_nace_as_activity(tmp_path, permit):
    row, _ = envelope(tmp_path)
    nace = next(c for c in row.claims if c.field == 'identity.nace1')
    nace.value = {'kode': '47.540', 'beskrivelse': 'Detaljhandel med elektriske husholdningsapparater'}
    row.claims = [c for c in row.claims if c.field not in {'identity.statutory_purpose', 'identity.registered_activity'}]
    add(row, 'identity.statutory_purpose', ['Eie og drive fast eiendom og datterselskaper'], 'identity')
    text = ' '.join(s.text for s in generate(row.run.synthesis, row).what)
    assert 'working in' not in text
    assert 'its registered purpose (in Norwegian) is «Eie og drive fast eiendom og datterselskaper»' in text
    assert text.index('registered purpose') < text.index('registered industry code is NACE 47.540')


def test_own_website_description_is_quoted_and_contact_blocks_are_not(tmp_path, permit):
    row, _ = envelope(tmp_path)
    add(row, 'website_description.meta_description.a', {'text': 'Centrum Regnskap\r\nGate 10, 8310 Kabelvag\r\n47850000\r\npost@cr1.no',
        'self_description': True, 'kind': 'meta_description'}, 'website')
    assert 'own website' not in ' '.join(s.text for s in generate(row.run.synthesis, row).what)
    add(row, 'website_description.og_description.b', {'text': 'We build and service heat pumps for homes in Northern Norway. Call us today!',
        'self_description': True, 'kind': 'og_description'}, 'website')
    what = generate(row.run.synthesis, row).what
    assert 'on its own website it describes itself as «We build and service heat pumps for homes in Northern Norway»' in what[0].text
    assert 'r4-website_description.og_description.b' in what[0].claim_ids


def test_unknowns_name_the_recorded_website_reason(tmp_path):
    row, _ = envelope(tmp_path)
    row.run.sections['website'] = 'not_available'
    attempts = [{'domain': 'example-owner.no', 'reason': 'insufficient_owner_proof'},
                {'domain': 'parked-example.no', 'reason': 'placeholder'},
                {'domain': 'missing-example.no', 'reason': 'no_such_domain', 'candidate_not_reachable': True}]
    row.errors.append(Error(section='website', code='website_candidates', message=json.dumps(attempts)))
    text = next(s.text for s in generate(row.run.synthesis, row).unknowns if s.text.startswith('Website'))
    assert 'a candidate site (example-owner.no) didn\'t prove it belongs to this company' in text
    assert 'a parked or placeholder page (parked-example.no)' in text
    row.errors[-1] = Error(section='website', code='website_candidates', message=json.dumps(attempts[2:]))
    text = next(s.text for s in generate(row.run.synthesis, row).unknowns if s.text.startswith('Website'))
    assert text == 'Website and social media: none found: no website is registered with Brønnøysund, and none of the 1 likely domain names exist.'


def test_summary_and_site_render_the_same_three_parts(tmp_path, permit):
    from signalpost.site import profile
    row, _ = envelope(tmp_path)
    add(row, 'registry_change.name', announcement(event_id=9, date='2026-03-01T00:00:00Z', changed_field='/navn', new_value='RENAMED AS'))
    synthesis = template_generate(row)
    assert 'A registry announcement on 1 Mar 2026 records a name change to «RENAMED AS».' in synthesis.summary
    assert synthesis.summary == brief_summary(synthesis)
    row.run.synthesis = synthesis
    from signalpost.site import normalize
    from signalpost.models.shapes import serialize
    html = profile(normalize(serialize(row, 'union')), 'Nordic Company Lens')
    for heading in ('What the company is and does', 'What changed', 'What&#x27;s still unknown'):
        assert heading in html
    for part in (synthesis.brief.what, synthesis.brief.changes, synthesis.brief.unknowns):
        for sentence in part:
            from html import escape
            assert escape(sentence.text) in html


def test_revenue_trend_is_a_cited_change(tmp_path, monkeypatch):
    row, _ = envelope(tmp_path)
    seed = next(c for c in row.claims if c.field == 'identity.legal_name')
    accounts = next((c for c in row.claims if c.family == 'accounts' and c.evidence_ids), seed)
    for year, revenue in (('2025', 1100000), ('2024', 1000000)):
        row.claims.append(seed.model_copy(update={'id': 'r4-' + year, 'family': 'accounts', 'field': 'accounts.history.' + year + '.revenue',
            'value': revenue, 'evidence_ids': accounts.evidence_ids, 'reporting_period': {'fiscal_year': year, 'period_start': year + '-01-01',
            'period_end': year + '-12-31', 'currency': 'NOK', 'unit': 'NOK', 'account_type': 'SELSKAP'}}))
    from signalpost.synthesis import validate as gate
    original = gate.permitted
    monkeypatch.setattr(gate, 'permitted', lambda c, e: c.id.startswith('r4-') or original(c, e))
    brief = generate(row.run.synthesis, row)
    trend = brief.changes[0]
    assert trend.text == 'Revenue rose 10.0%, from NOK 1.0 million in FY2024 to NOK 1.1 million in FY2025.'
    assert trend.claim_ids == ['r4-2025', 'r4-2024'] and trend.value_kind == 'derived'
    assert not any('%' in s.text for s in brief.what)
