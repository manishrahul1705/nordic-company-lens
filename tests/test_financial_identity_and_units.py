"""
Regression and verification suite for V6-01 and V6-02.
V6-01: Per-filing legal identity verification on all historical Regnskapsregisteret records.
V6-02: Unit and scale comparability gating.
"""
import hashlib
import json
import pytest

from signalpost.budget import SourceFailure
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.regnskap import extract
from signalpost.sources.financial_comparability import (
    ComparablePeriodGate,
    FinancialObservation,
    compare_periods,
)


def make_dummy_response(records: list):
    body = json.dumps(records).encode("utf-8")
    sha = hashlib.sha256(body).hexdigest()

    class Resp:
        pass

    resp = Resp()
    resp.url = "https://data.brreg.no/regnskapsregisteret/regnskap/923609016"
    resp.body = body
    resp.sha = sha
    resp.retrieved_at = "2026-10-21T12:00:00Z"
    resp.status = 200
    return resp


def test_v6_01_historical_filing_identity_attribution_proof(tmp_path):
    """
    V6-01: Historical records lacking explicit matching orgnr must be omitted,
    never published as verified company history.
    """
    blobs = BlobStore(tmp_path / "blobs")
    org = "923609016"

    records = [
        # Filing 1: 2025, exact matching orgnr -> accepted as latest
        {
            "regnskapstype": "SELSKAP",
            "journalnr": "1001",
            "valuta": "NOK",
            "virksomhet": {"organisasjonsnummer": org},
            "regnskapsperiode": {"fraDato": "2025-01-01", "tilDato": "2025-12-31"},
            "resultatregnskapResultat": {"aarsresultat": 10},
        },
        # Filing 2: 2024, missing virksomhet entirely -> MUST BE REJECTED
        {
            "regnskapstype": "SELSKAP",
            "journalnr": "1002",
            "valuta": "NOK",
            "virksomhet": {},
            "regnskapsperiode": {"fraDato": "2024-01-01", "tilDato": "2024-12-31"},
            "resultatregnskapResultat": {"aarsresultat": 999},
        },
        # Filing 3: 2023, mismatched orgnr -> MUST BE REJECTED
        {
            "regnskapstype": "SELSKAP",
            "journalnr": "1003",
            "valuta": "NOK",
            "virksomhet": {"organisasjonsnummer": "999888777"},
            "regnskapsperiode": {"fraDato": "2023-01-01", "tilDato": "2023-12-31"},
            "resultatregnskapResultat": {"aarsresultat": 888},
        },
        # Filing 4: 2022, exact matching orgnr -> accepted as history
        {
            "regnskapstype": "SELSKAP",
            "journalnr": "1004",
            "valuta": "NOK",
            "virksomhet": {"organisasjonsnummer": org},
            "regnskapsperiode": {"fraDato": "2022-01-01", "tilDato": "2022-12-31"},
            "resultatregnskapResultat": {"aarsresultat": 42},
        },
    ]

    resp = make_dummy_response(records)
    section = extract(org, resp, blobs)

    published_fields = {c.field: c.value for c in section.claims}

    # Latest 2025 must be present
    assert published_fields.get("accounts.net_result") == 10

    # 2024 (missing identity) MUST NOT be present
    assert "accounts.history.2024.net_result" not in published_fields

    # 2023 (wrong company) MUST NOT be present
    assert "accounts.history.2023.net_result" not in published_fields

    # 2022 (matching identity) must be present
    assert published_fields.get("accounts.history.2022.net_result") == 42


def test_v6_01_latest_record_missing_identity_fails_closed(tmp_path):
    """
    If the newest filing itself lacks matching orgnr, extract must fail closed.
    """
    blobs = BlobStore(tmp_path / "blobs")
    org = "923609016"

    records = [
        {
            "regnskapstype": "SELSKAP",
            "journalnr": "1001",
            "valuta": "NOK",
            "virksomhet": {"organisasjonsnummer": "999999999"},
            "regnskapsperiode": {"fraDato": "2025-01-01", "tilDato": "2025-12-31"},
            "resultatregnskapResultat": {"aarsresultat": 50},
        }
    ]

    resp = make_dummy_response(records)
    with pytest.raises(SourceFailure) as exc_info:
        extract(org, resp, blobs)
    assert exc_info.value.code == "wrong_company"


def test_v6_02_unit_scale_comparability_gate():
    """
    V6-02: Comparing periods with differing units or scales must flag unit_mismatch.
    """
    gate = ComparablePeriodGate()

    obs_curr = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2024",
        period_start="2024-01-01",
        period_end="2024-12-31",
        currency="NOK",
        unit="NOK",
        account_type="SELSKAP",
        metrics={"revenue": 1000000},
    )

    # Prior with same unit NOK -> comparable
    obs_prior_ok = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2023",
        period_start="2023-01-01",
        period_end="2023-12-31",
        currency="NOK",
        unit="NOK",
        account_type="SELSKAP",
        metrics={"revenue": 800000},
    )

    res_ok = gate.compare(obs_curr, obs_prior_ok, metric="revenue")
    assert res_ok.comparable is True
    assert "unit_mismatch" not in res_ok.reason_codes
    assert res_ok.growth_rate == pytest.approx(0.25)

    # Prior with differing unit TNOK (thousands) -> unit_mismatch
    obs_prior_tnok = FinancialObservation(
        organisation_number="923609016",
        fiscal_year="2023",
        period_start="2023-01-01",
        period_end="2023-12-31",
        currency="NOK",
        unit="TNOK",
        account_type="SELSKAP",
        metrics={"revenue": 800},
    )

    res_tnok = gate.compare(obs_curr, obs_prior_tnok, metric="revenue")
    assert res_tnok.comparable is False
    assert "unit_mismatch" in res_tnok.reason_codes
    assert res_tnok.growth_rate is None
    assert "unit_mismatch" in res_tnok.explanation
