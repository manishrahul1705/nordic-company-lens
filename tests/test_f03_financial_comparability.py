import pytest
from datetime import date
from signalpost.sources.financial_comparability import (
    ComparablePeriodGate,
    FinancialObservation,
    ComparabilityResult,
    compare_periods
)


def make_obs(
    org="923609016",
    year="2024",
    start=None,
    end=None,
    currency="NOK",
    unit="NOK",
    account_type="SELSKAP",
    revenue=10_000_000,
    net_result=1_000_000,
    journalnr="1001"
):
    s = start or f"{year}-01-01"
    e = end or f"{year}-12-31"
    return FinancialObservation(
        organisation_number=org,
        fiscal_year=year,
        period_start=s,
        period_end=e,
        currency=currency,
        unit=unit,
        account_type=account_type,
        metrics={"revenue": revenue, "net_result": net_result},
        journalnr=journalnr
    )


def test_comparable_standard_consecutive_years():
    obs_2024 = make_obs(year="2024", start="2024-01-01", end="2024-12-31", revenue=12_000_000)
    obs_2023 = make_obs(year="2023", start="2023-01-01", end="2023-12-31", revenue=10_000_000)
    
    gate = ComparablePeriodGate()
    result = gate.compare(obs_2024, obs_2023, metric="revenue")
    
    assert result.comparable is True
    assert result.reason_codes == []
    assert result.growth_rate == pytest.approx(0.20, abs=1e-4)
    assert result.nominal_change == 2_000_000


def test_non_comparable_currency_mismatch():
    obs_2024 = make_obs(year="2024", currency="NOK", revenue=12_000_000)
    obs_2023 = make_obs(year="2023", currency="EUR", revenue=1_000_000)
    
    gate = ComparablePeriodGate()
    result = gate.compare(obs_2024, obs_2023, metric="revenue")
    
    assert result.comparable is False
    assert "currency_mismatch" in result.reason_codes
    assert result.growth_rate is None


def test_non_comparable_differing_scope():
    obs_2024 = make_obs(year="2024", account_type="SELSKAP")
    obs_2023 = make_obs(year="2023", account_type="KONSERN")
    
    gate = ComparablePeriodGate()
    result = gate.compare(obs_2024, obs_2023, metric="revenue")
    
    assert result.comparable is False
    assert "differing_accounting_scope" in result.reason_codes
    assert result.growth_rate is None


def test_non_comparable_short_fiscal_year():
    obs_2024 = make_obs(year="2024", start="2024-01-01", end="2024-12-31")  # 365 days
    obs_2023 = make_obs(year="2023", start="2023-07-01", end="2023-12-31")  # 184 days
    
    gate = ComparablePeriodGate()
    result = gate.compare(obs_2024, obs_2023, metric="revenue")
    
    assert result.comparable is False
    assert "non_standard_period_length" in result.reason_codes
    assert result.growth_rate is None


def test_non_comparable_temporal_gap():
    obs_2024 = make_obs(year="2024", start="2024-01-01", end="2024-12-31")
    obs_2022 = make_obs(year="2022", start="2022-01-01", end="2022-12-31")  # Gap of 1 year
    
    gate = ComparablePeriodGate()
    result = gate.compare(obs_2024, obs_2022, metric="revenue")
    
    assert result.comparable is False
    assert "period_gap" in result.reason_codes
    assert result.growth_rate is None


def test_non_comparable_overlapping_periods():
    obs_2024 = make_obs(year="2024", start="2024-01-01", end="2024-12-31")
    obs_alt = make_obs(year="2024b", start="2024-06-01", end="2025-05-31")
    
    gate = ComparablePeriodGate()
    result = gate.compare(obs_alt, obs_2024, metric="revenue")
    
    assert result.comparable is False
    assert "overlapping_periods" in result.reason_codes
    assert result.growth_rate is None


def test_non_comparable_differing_entity():
    obs_1 = make_obs(org="923609016")
    obs_2 = make_obs(org="993578843")
    
    gate = ComparablePeriodGate()
    result = gate.compare(obs_1, obs_2, metric="revenue")
    
    assert result.comparable is False
    assert "differing_legal_entity" in result.reason_codes


def test_zero_or_negative_prior_base_growth_policy():
    obs_2024 = make_obs(year="2024", revenue=5_000_000)
    obs_2023_zero = make_obs(year="2023", revenue=0)
    
    gate = ComparablePeriodGate()
    result_zero = gate.compare(obs_2024, obs_2023_zero, metric="revenue")
    
    # Periods themselves are comparable, but growth percentage is undefined/withheld
    assert result_zero.comparable is True
    assert result_zero.nominal_change == 5_000_000
    assert result_zero.growth_rate is None
    assert "non_positive_prior_base" in result_zero.reason_codes
    
    obs_2023_neg = make_obs(year="2023", revenue=-100_000)
    result_neg = gate.compare(obs_2024, obs_2023_neg, metric="revenue")
    assert result_neg.growth_rate is None
    assert "non_positive_prior_base" in result_neg.reason_codes


def test_compare_periods_helper_from_claims():
    from signalpost.models.envelope import Claim
    
    c2024 = Claim(
        family="accounts",
        field="accounts.revenue",
        value=15_000_000,
        availability="available",
        confidence=1.0,
        evidence_ids=["e" * 64],
        id="1" * 64,
        reporting_period={
            "fiscal_year": "2024",
            "period_start": "2024-01-01",
            "period_end": "2024-12-31",
            "currency": "NOK",
            "unit": "NOK",
            "account_type": "SELSKAP"
        },
        carried_forward=False,
        first_observed_at="2026-10-21T00:00:00Z",
        last_observed_at="2026-10-21T00:00:00Z"
    )
    c2023 = Claim(
        family="accounts",
        field="accounts.history.2023.revenue",
        value=10_000_000,
        availability="available",
        confidence=1.0,
        evidence_ids=["e" * 64],
        id="2" * 64,
        reporting_period={
            "fiscal_year": "2023",
            "period_start": "2023-01-01",
            "period_end": "2023-12-31",
            "currency": "NOK",
            "unit": "NOK",
            "account_type": "SELSKAP"
        },
        carried_forward=False,
        first_observed_at="2026-10-21T00:00:00Z",
        last_observed_at="2026-10-21T00:00:00Z"
    )
    
    res = compare_periods(c2024, c2023, org="923609016")
    assert res.comparable is True
    assert res.growth_rate == pytest.approx(0.50, abs=1e-4)


def test_site_rendering_with_comparability_gate():
    from signalpost.site import profile
    from signalpost.models.envelope import Claim, Evidence
    from signalpost.models.evidence import digest
    from signalpost.runner import placeholder
    
    env = placeholder("923609016", "run-comp", "2026-10-21T00:00:00Z")
    env.run.sections["accounts"] = "available"
    
    url = "https://example.com"
    sha = "a" * 64
    m = "signalpost.registry.v1"
    eid1 = digest([url, sha, "row:1", m])
    eid2 = digest([url, sha, "row:2", m])
    
    e1 = Evidence(
        id=eid1, source_url=url, source_class="accounts",
        retrieved_at="2026-10-21T00:00:00Z", content_sha256=sha,
        claim_span="20M", locator="row:1", extraction_method=m
    )
    e2 = Evidence(
        id=eid2, source_url=url, source_class="accounts",
        retrieved_at="2026-10-21T00:00:00Z", content_sha256=sha,
        claim_span="10M", locator="row:2", extraction_method=m
    )
    env.evidence.extend([e1, e2])

    # 2024 claim
    env.claims.append(Claim(
        family="accounts",
        field="accounts.revenue",
        value=20_000_000,
        availability="available",
        confidence=1.0,
        evidence_ids=[eid1],
        id="1" * 64,
        reporting_period={"fiscal_year": "2024", "period_start": "2024-01-01", "period_end": "2024-12-31", "currency": "NOK", "unit": "NOK", "account_type": "SELSKAP"},
        carried_forward=False,
        first_observed_at="2026-10-21T00:00:00Z",
        last_observed_at="2026-10-21T00:00:00Z"
    ))
    # 2023 claim
    env.claims.append(Claim(
        family="accounts",
        field="accounts.history.2023.revenue",
        value=10_000_000,
        availability="available",
        confidence=1.0,
        evidence_ids=[eid2],
        id="2" * 64,
        reporting_period={"fiscal_year": "2023", "period_start": "2023-01-01", "period_end": "2023-12-31", "currency": "NOK", "unit": "NOK", "account_type": "SELSKAP"},
        carried_forward=False,
        first_observed_at="2026-10-21T00:00:00Z",
        last_observed_at="2026-10-21T00:00:00Z"
    ))
    
    html = profile(env.model_dump(mode="json"), "Signalpost")
    assert "financial-trend-banner" in html
    assert "Comparable" in html
    assert "+100.0%" in html


def test_profile_projection_attaches_comparability():
    from signalpost.profiles import project
    from signalpost.models.envelope import Claim, Evidence
    from signalpost.models.evidence import digest
    from signalpost.runner import placeholder
    
    env = placeholder("923609016", "run-comp", "2026-10-21T00:00:00Z")
    env.run.sections["accounts"] = "available"
    
    url = "https://example.com"
    sha = "a" * 64
    m = "signalpost.registry.v1"
    eid1 = digest([url, sha, "row:1", m])
    eid2 = digest([url, sha, "row:2", m])
    
    e1 = Evidence(
        id=eid1, source_url=url, source_class="accounts",
        retrieved_at="2026-10-21T00:00:00Z", content_sha256=sha,
        claim_span="20M", locator="row:1", extraction_method=m
    )
    e2 = Evidence(
        id=eid2, source_url=url, source_class="accounts",
        retrieved_at="2026-10-21T00:00:00Z", content_sha256=sha,
        claim_span="10M", locator="row:2", extraction_method=m
    )
    env.evidence.extend([e1, e2])

    env.claims.append(Claim(
        family="accounts",
        field="accounts.revenue",
        value=20_000_000,
        availability="available",
        confidence=1.0,
        evidence_ids=[eid1],
        id="1" * 64,
        reporting_period={"fiscal_year": "2024", "period_start": "2024-01-01", "period_end": "2024-12-31", "currency": "NOK", "unit": "NOK", "account_type": "SELSKAP"},
        carried_forward=False,
        first_observed_at="2026-10-21T00:00:00Z",
        last_observed_at="2026-10-21T00:00:00Z"
    ))
    env.claims.append(Claim(
        family="accounts",
        field="accounts.history.2023.revenue",
        value=10_000_000,
        availability="available",
        confidence=1.0,
        evidence_ids=[eid2],
        id="2" * 64,
        reporting_period={"fiscal_year": "2023", "period_start": "2023-01-01", "period_end": "2023-12-31", "currency": "NOK", "unit": "NOK", "account_type": "SELSKAP"},
        carried_forward=False,
        first_observed_at="2026-10-21T00:00:00Z",
        last_observed_at="2026-10-21T00:00:00Z"
    ))
    
    prof = project(env)
    fin_records = prof["evidence"]["financials"]["value"]["records"]
    assert len(fin_records) == 2
    comp = fin_records[0].get("comparability_with_prior")
    assert comp is not None
    assert comp["comparable"] is True
    assert comp["growth_rate"] == pytest.approx(1.0, abs=1e-4)



def test_r6r2_new_001_missing_currency_and_unit_gating():
    """
    R6R2-NEW-001: Missing currency or unverified unit in claims or profile dicts must not
    be defaulted to NOK. Comparability must fail-closed with currency_mismatch and unit_mismatch.
    """
    c_none = {
        "field": "accounts.revenue",
        "value": 100,
        "reporting_period": {
            "fiscal_year": "2024",
            "period_start": "2024-01-01",
            "period_end": "2024-12-31",
            "currency": None,
            "unit": None,
        },
    }
    c_prior_none = {
        "field": "accounts.history.2023.revenue",
        "value": 80,
        "reporting_period": {
            "fiscal_year": "2023",
            "period_start": "2023-01-01",
            "period_end": "2023-12-31",
            "currency": None,
            "unit": None,
        },
    }
    res_both_none = compare_periods(c_none, c_prior_none, org="923609016")
    assert res_both_none.comparable is False
    assert "currency_mismatch" in res_both_none.reason_codes
    assert "unit_mismatch" in res_both_none.reason_codes

    c_nok = {
        "field": "accounts.history.2023.revenue",
        "value": 80,
        "reporting_period": {
            "fiscal_year": "2023",
            "period_start": "2023-01-01",
            "period_end": "2023-12-31",
            "currency": "NOK",
            "unit": "NOK",
        },
    }
    res_one_none = compare_periods(c_none, c_nok, org="923609016")
    assert res_one_none.comparable is False
    assert "currency_mismatch" in res_one_none.reason_codes
    assert "unit_mismatch" in res_one_none.reason_codes


def test_financial_observation_default_abstains_safely():
    # Observations created without explicit currency/unit must abstain safely
    obs_1 = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2024",
        period_start="2024-01-01",
        period_end="2024-12-31",
        metrics={"revenue": 1000}
    )
    obs_2 = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2023",
        period_start="2023-01-01",
        period_end="2023-12-31",
        metrics={"revenue": 800}
    )
    assert obs_1.currency is None
    assert obs_1.unit is None
    assert obs_2.currency is None
    assert obs_2.unit is None
    res = ComparablePeriodGate().compare(obs_1, obs_2, metric="revenue")
    assert res.comparable is False
    assert "currency_mismatch" in res.reason_codes
    assert "unit_mismatch" in res.reason_codes
    assert res.growth_rate is None
