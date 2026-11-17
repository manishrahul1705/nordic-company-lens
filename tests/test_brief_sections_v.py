"""Stage V: reach, standing and not_established are cited, recomputed and never empty."""
from tests.test_synthesis import envelope
from signalpost.models.synthesis import Sentence
from signalpost.synthesis.cohort import build_index, context
from signalpost.synthesis.sections_extra import percentile, ordinal, generate as extra
from signalpost.synthesis.template import generate
from signalpost.synthesis.validate import ALL_SECTIONS, validate_synthesis, sentence_error


def cohort_of(tmp_path, n, revenue=1000.0):
    row, _ = envelope(tmp_path)
    rows = []
    for i in range(n + 1):
        copy = row.model_copy(deep=True)
        copy.organisation_number = f'{900000000 + i}'
        nace = next(c for c in copy.claims if c.field == 'identity.nace1')
        copy.claims.append(nace.model_copy(update={'field': 'accounts.revenue', 'family': 'accounts', 'value': revenue * (i + 1),
            'id': f'rev{i:061d}', 'reporting_period': {'fiscal_year': '2025', 'currency': 'NOK', 'account_type': 'SELSKAP'}}))
        copy.run.sections['accounts'] = 'available'
        rows.append(copy)
    return rows


def test_all_seven_sections_are_filled_and_cited(tmp_path):
    row, _ = envelope(tmp_path)
    result = generate(row, context(row, build_index([row])))
    ids = {c.id for c in row.claims} | {c.id for c in result.change_claims}
    for key in ALL_SECTIONS:
        assert getattr(result.sections, key), key
    for key in ('reach', 'standing', 'not_established'):
        assert all(s.claim_ids and set(s.claim_ids) <= ids for s in getattr(result.sections, key))
    assert result.checks.sentences == sum(len(getattr(result.sections, k)) for k in ALL_SECTIONS)


def test_percentile_and_thin_comparison(tmp_path):
    assert percentile(5, [1, 2, 3, 4, 6, 7, 8, 9, 10, 11]) == 40 and ordinal(41) == '41st' and ordinal(12) == '12th'
    rows = cohort_of(tmp_path, 12)
    index = build_index(rows)
    top = generate(rows[-1], context(rows[-1], index)).sections.standing[0].text
    assert 'at the 100th percentile of the 12 other companies' in top
    few = cohort_of(tmp_path / 'few', 3)
    thin = generate(few[0], context(few[0], build_index(few))).sections.standing[0].text
    assert 'Comparison too thin: 3 other companies' in thin and 'percentile is given' in thin


def test_forged_standing_or_cohort_is_rejected(tmp_path):
    rows = cohort_of(tmp_path, 12)
    index = build_index(rows)
    result = generate(rows[0], context(rows[0], index))
    result.sections.standing[0].text = result.sections.standing[0].text.replace('at the 0th', 'at the 90th')
    checked = validate_synthesis(result, rows[0])
    assert not checked.sections.standing and any(r['section'] == 'standing' for r in checked.checks.rejections)
    result = generate(rows[0], context(rows[0], index))
    result.cohort.standing.comparables[0].value = 1.0
    assert context(rows[0], index) != result.cohort


def test_absence_wording_must_match_recorded_state(tmp_path):
    row, _ = envelope(tmp_path)
    from signalpost.synthesis.sections_extra import section_claim
    gap = section_claim(row, 'accounts')
    good = next(s for s in extra(row, None)['not_established'] if s.claim_ids == [gap.id])
    assert sentence_error(good, row) is None
    assert sentence_error(Sentence(text='Financials: everything is fine.', claim_ids=[gap.id]), row) == 'unverified_absence'


def test_role_held_at_another_cohort_company_is_cited_from_that_company(tmp_path):
    rows = cohort_of(tmp_path, 1)
    holder, other = rows
    role = next(c for c in other.claims if c.field.startswith('roles.role.') and c.availability == 'available')
    role.value = dict(role.value, entity_organisation_number=holder.organisation_number, inactive=False)
    cohort = context(holder, build_index(rows))
    reach = generate(holder, cohort).sections.reach
    line = next(s for s in reach if s.text.startswith('Registered role at another company'))
    assert role.id in line.claim_ids and '(org. ' + other.organisation_number + ')' in line.text
