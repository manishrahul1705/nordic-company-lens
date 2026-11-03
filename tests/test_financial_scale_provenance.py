"""
Adversarial tests for Blocker C: Financial Original-Source Scale & Provenance.

Verifies that:
1. NOK vs TNOK scale mismatch fails comparability with unit_mismatch.
2. Missing currency fails comparability with currency_mismatch.
3. Missing unit fails comparability with unit_mismatch.
4. Conflicting units fail comparability with unit_mismatch.
5. Mixed SELSKAP / KONSERN scope fails with differing_accounting_scope.
6. Partial / non-standard periods (<350 or >375 days) fail with non_standard_period_length.
7. Period gaps (>35 days) fail with period_gap.
8. Overlapping periods fail with overlapping_periods.
9. Zero prior base revenue safely suppresses percentage growth (growth_rate is None).
10. Negative prior base operating profit safely suppresses percentage growth.
11. Differing organization numbers fail with differing_legal_entity.
12. Raw observations are preserved without discarded data; unproved scale triggers safe abstention.
"""
import pytest
from signalpost.sources.financial_comparability import (
    ComparablePeriodGate,
    FinancialObservation,
    compare_periods,
)


def test_financial_provenance_nok_vs_tnok_abstains():
    """NOK vs TNOK scale mismatch must abstain from calculating growth."""
    obs_curr = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2024",
        period_start="2024-01-01",
        period_end="2024-12-31",
        currency="NOK",
        unit="NOK",
        metrics={"revenue": 10_000_000}
    )
    obs_prior = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2023",
        period_start="2023-01-01",
        period_end="2023-12-31",
        currency="NOK",
        unit="TNOK",  # Thousands NOK
        metrics={"revenue": 9_000}
    )
    res = ComparablePeriodGate().compare(obs_curr, obs_prior, metric="revenue")
    assert res.comparable is False
    assert "unit_mismatch" in res.reason_codes
    assert res.nominal_change is None
    assert res.growth_rate is None


def test_financial_provenance_missing_currency_abstains():
    """Missing currency must trigger currency_mismatch and abstain."""
    obs_curr = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2024",
        period_start="2024-01-01",
        period_end="2024-12-31",
        currency=None,
        unit="NOK",
        metrics={"revenue": 10_000_000}
    )
    obs_prior = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2023",
        period_start="2023-01-01",
        period_end="2023-12-31",
        currency="NOK",
        unit="NOK",
        metrics={"revenue": 9_000_000}
    )
    res = ComparablePeriodGate().compare(obs_curr, obs_prior, metric="revenue")
    assert res.comparable is False
    assert "currency_mismatch" in res.reason_codes


def test_financial_provenance_missing_unit_abstains():
    """Missing unit scale must trigger unit_mismatch and abstain."""
    obs_curr = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2024",
        period_start="2024-01-01",
        period_end="2024-12-31",
        currency="NOK",
        unit=None,  # Missing unit
        metrics={"revenue": 10_000_000}
    )
    obs_prior = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2023",
        period_start="2023-01-01",
        period_end="2023-12-31",
        currency="NOK",
        unit=None,
        metrics={"revenue": 9_000_000}
    )
    res = ComparablePeriodGate().compare(obs_curr, obs_prior, metric="revenue")
    assert res.comparable is False
    assert "unit_mismatch" in res.reason_codes


def test_financial_provenance_conflicting_units_abstains():
    """EUR vs NOK or MNOK vs NOK must trigger mismatches."""
    obs_curr = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2024",
        period_start="2024-01-01",
        period_end="2024-12-31",
        currency="NOK",
        unit="MNOK",
        metrics={"revenue": 10}
    )
    obs_prior = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2023",
        period_start="2023-01-01",
        period_end="2023-12-31",
        currency="NOK",
        unit="NOK",
        metrics={"revenue": 9_000_000}
    )
    res = ComparablePeriodGate().compare(obs_curr, obs_prior, metric="revenue")
    assert res.comparable is False
    assert "unit_mismatch" in res.reason_codes


def test_financial_provenance_mixed_scope_selskap_konsern_abstains():
    """Comparing company (SELSKAP) with group (KONSERN) must abstain."""
    obs_curr = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2024",
        period_start="2024-01-01",
        period_end="2024-12-31",
        currency="NOK",
        unit="NOK",
        account_type="KONSERN",  # Consolidated
        metrics={"revenue": 50_000_000}
    )
    obs_prior = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2023",
        period_start="2023-01-01",
        period_end="2023-12-31",
        currency="NOK",
        unit="NOK",
        account_type="SELSKAP",  # Company
        metrics={"revenue": 10_000_000}
    )
    res = ComparablePeriodGate().compare(obs_curr, obs_prior, metric="revenue")
    assert res.comparable is False
    assert "differing_accounting_scope" in res.reason_codes


def test_financial_provenance_partial_period_short_year_abstains():
    """Short fiscal year (e.g. 6-month formation period) must abstain."""
    obs_curr = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2024",
        period_start="2024-01-01",
        period_end="2024-12-31",
        currency="NOK",
        unit="NOK",
        metrics={"revenue": 10_000_000}
    )
    obs_prior = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2023",
        period_start="2023-07-01",  # 6-month period
        period_end="2023-12-31",
        currency="NOK",
        unit="NOK",
        metrics={"revenue": 4_000_000}
    )
    res = ComparablePeriodGate().compare(obs_curr, obs_prior, metric="revenue")
    assert res.comparable is False
    assert "non_standard_period_length" in res.reason_codes


def test_financial_provenance_period_gap_over_35_days_abstains():
    """Gap exceeding 35 days between periods must abstain."""
    obs_curr = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2024",
        period_start="2024-05-01",  # Gap from 2023-12-31 to 2024-05-01 = 122 days
        period_end="2025-04-30",
        currency="NOK",
        unit="NOK",
        metrics={"revenue": 10_000_000}
    )
    obs_prior = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2023",
        period_start="2023-01-01",
        period_end="2023-12-31",
        currency="NOK",
        unit="NOK",
        metrics={"revenue": 9_000_000}
    )
    res = ComparablePeriodGate().compare(obs_curr, obs_prior, metric="revenue")
    assert res.comparable is False
    assert "period_gap" in res.reason_codes


def test_financial_provenance_overlapping_periods_abstains():
    """Overlapping periods must abstain."""
    obs_curr = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2024",
        period_start="2023-11-01",  # Overlaps with 2023-12-31
        period_end="2024-10-31",
        currency="NOK",
        unit="NOK",
        metrics={"revenue": 10_000_000}
    )
    obs_prior = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2023",
        period_start="2023-01-01",
        period_end="2023-12-31",
        currency="NOK",
        unit="NOK",
        metrics={"revenue": 9_000_000}
    )
    res = ComparablePeriodGate().compare(obs_curr, obs_prior, metric="revenue")
    assert res.comparable is False
    assert "overlapping_periods" in res.reason_codes


def test_financial_provenance_zero_prior_base_safely_suppresses_growth():
    """Zero prior revenue must suppress percentage growth without ZeroDivisionError."""
    obs_curr = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2024",
        period_start="2024-01-01",
        period_end="2024-12-31",
        currency="NOK",
        unit="NOK",
        metrics={"revenue": 10_000_000}
    )
    obs_prior = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2023",
        period_start="2023-01-01",
        period_end="2023-12-31",
        currency="NOK",
        unit="NOK",
        metrics={"revenue": 0}  # Pre-revenue
    )
    res = ComparablePeriodGate().compare(obs_curr, obs_prior, metric="revenue")
    assert res.comparable is True
    assert res.nominal_change == 10_000_000
    assert res.growth_rate is None  # Suppressed safely
    assert "non_positive_prior_base" in res.reason_codes


def test_financial_provenance_negative_prior_base_safely_suppresses_growth():
    """Negative operating result must suppress percentage growth."""
    obs_curr = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2024",
        period_start="2024-01-01",
        period_end="2024-12-31",
        currency="NOK",
        unit="NOK",
        metrics={"operating_result": 2_000_000}
    )
    obs_prior = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2023",
        period_start="2023-01-01",
        period_end="2023-12-31",
        currency="NOK",
        unit="NOK",
        metrics={"operating_result": -1_500_000}
    )
    res = ComparablePeriodGate().compare(obs_curr, obs_prior, metric="operating_result")
    assert res.comparable is True
    assert res.nominal_change == 3_500_000
    assert res.growth_rate is None
    assert "non_positive_prior_base" in res.reason_codes


def test_financial_provenance_differing_orgnr_abstains():
    """Differing organization numbers must abstain."""
    obs_curr = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2024",
        period_start="2024-01-01",
        period_end="2024-12-31",
        currency="NOK",
        unit="NOK",
        metrics={"revenue": 10_000_000}
    )
    obs_prior = FinancialObservation(
        organisation_number="988258229",  # Different company
        fiscal_year="2023",
        period_start="2023-01-01",
        period_end="2023-12-31",
        currency="NOK",
        unit="NOK",
        metrics={"revenue": 9_000_000}
    )
    res = ComparablePeriodGate().compare(obs_curr, obs_prior, metric="revenue")
    assert res.comparable is False
    assert "differing_legal_entity" in res.reason_codes
