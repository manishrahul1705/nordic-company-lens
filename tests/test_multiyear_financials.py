"""
Tests for Stage 4A: Multi-Year Financial Intelligence.
Verifies all 20 dimensions:
1. Single-year statements (preserves existing behavior)
2. Two-year statements (extracts both years)
3. Three-year statements (extracts up to 3 years)
4. Nonconsecutive fiscal years
5. Duplicate year records
6. Restatements
7. Missing revenue in older years (partial statements)
8. Zero revenue
9. Negative profits and losses
10. Different currencies
11. Invalid/incomplete accounts
12. Consolidated vs. individual (SELSKAP vs. KONSERN)
13. Latest-year backward compatibility
14. Claim-field uniqueness
15. Evidence and SHA-256 integrity
16. Reporting-period correctness
17. Historical refresh stability
18. Deterministic output
19. Zero additional HTTP requests
20. All evaluator schema constraints (Contract, Reference, Union)
"""
import copy
import hashlib
import json
from pathlib import Path
import httpx
import pytest

from signalpost.sources import regnskap
from signalpost.sources.blobstore import BlobStore
from signalpost.models.shapes import serialize, validate
from signalpost.models.envelope import Envelope
from signalpost.profiles import project
from signalpost.runner import run
from signalpost.refresh import diff
from tests.test_registry import config, handler, execute


def make_response(url: str, data: list):
    body = json.dumps(data).encode("utf-8")
    sha = hashlib.sha256(body).hexdigest()

    class Resp:
        pass

    resp = Resp()
    resp.url = url
    resp.body = body
    resp.sha = sha
    resp.retrieved_at = "2026-10-21T12:00:00Z"
    resp.status = 200
    return resp


def make_account_row(orgnr: str, year: int, rev: float | None = 1000000.0, net: float = 100000.0,
                     account_type: str = "SELSKAP", currency: str = "NOK", journalnr: str | None = None):
    row = {
        "regnskapstype": account_type,
        "virksomhet": {"organisasjonsnummer": orgnr},
        "regnskapsperiode": {
            "fraDato": f"{year}-01-01",
            "tilDato": f"{year}-12-31"
        },
        "valuta": currency,
        "resultatregnskapResultat": {
            "driftsresultat": {
                "driftsinntekter": {
                    "sumDriftsinntekter": rev
                } if rev is not None else {},
                "driftsresultat": net * 1.2
            },
            "ordinaertResultatFoerSkattekostnad": net * 1.1,
            "aarsresultat": net
        },
        "egenkapitalGjeld": {
            "egenkapital": {"sumEgenkapital": 500000.0},
            "gjeldOversikt": {"sumGjeld": 300000.0}
        },
        "eiendeler": {
            "sumEiendeler": 800000.0
        }
    }
    if journalnr:
        row["journalnr"] = journalnr
    return row


# -------------------------------------------------------------------------
# Test 1: Single-year statements (preserves existing behavior)
# -------------------------------------------------------------------------
def test_1_single_year_statement_preserves_existing_behavior(tmp_path):
    org = "923609016"
    store = BlobStore(tmp_path / "blobs")
    rows = [make_account_row(org, 2025, rev=5000000.0, net=250000.0)]
    resp = make_response(f"https://data.brreg.no/regnskapsregisteret/regnskap/{org}", rows)

    sec = regnskap.extract(org, resp, store)
    assert sec.state == "available"

    # Latest year claims
    revenue_claim = next((c for c in sec.claims if c.field == "accounts.revenue"), None)
    assert revenue_claim is not None
    assert revenue_claim.value == 5000000.0
    assert revenue_claim.reporting_period["fiscal_year"] == "2025"

    # No history claims should exist when only 1 year was provided
    history_claims = [c for c in sec.claims if c.field.startswith("accounts.history.")]
    assert len(history_claims) == 0


# -------------------------------------------------------------------------
# Test 2: Two-year statements (extracts both years)
# -------------------------------------------------------------------------
def test_2_two_year_statement_extracts_both_years(tmp_path):
    org = "923609016"
    store = BlobStore(tmp_path / "blobs")
    rows = [
        make_account_row(org, 2024, rev=4000000.0, net=200000.0),
        make_account_row(org, 2025, rev=5000000.0, net=250000.0),
    ]
    resp = make_response(f"https://data.brreg.no/regnskapsregisteret/regnskap/{org}", rows)

    sec = regnskap.extract(org, resp, store)
    assert sec.state == "available"

    # Latest year 2025
    rev_latest = next((c for c in sec.claims if c.field == "accounts.revenue"), None)
    assert rev_latest is not None and rev_latest.value == 5000000.0
    assert rev_latest.reporting_period["fiscal_year"] == "2025"

    # Prior year 2024
    rev_prior = next((c for c in sec.claims if c.field == "accounts.history.2024.revenue"), None)
    assert rev_prior is not None, "Prior year 2024 revenue must be extracted"
    assert rev_prior.value == 4000000.0
    assert rev_prior.reporting_period["fiscal_year"] == "2024"
    assert rev_prior.reporting_period["period_end"] == "2024-12-31"


# -------------------------------------------------------------------------
# Test 3: Three-year statements (extracts up to 3 years)
# -------------------------------------------------------------------------
def test_3_statement_extracts_all_available_years(tmp_path):
    org = "923609016"
    store = BlobStore(tmp_path / "blobs")
    rows = [
        make_account_row(org, 2022, rev=2000000.0, net=100000.0),
        make_account_row(org, 2023, rev=3000000.0, net=150000.0),
        make_account_row(org, 2024, rev=4000000.0, net=200000.0),
        make_account_row(org, 2025, rev=5000000.0, net=250000.0),
    ]
    resp = make_response(f"https://data.brreg.no/regnskapsregisteret/regnskap/{org}", rows)

    sec = regnskap.extract(org, resp, store)

    # Every distinct year returned by the official response is retained.
    years_extracted = {c.reporting_period["fiscal_year"] for c in sec.claims if c.reporting_period}
    assert "2025" in years_extracted
    assert "2024" in years_extracted
    assert "2023" in years_extracted
    assert "2022" in years_extracted, "Do not discard available fiscal years"

    # Verify claim values
    assert next(c for c in sec.claims if c.field == "accounts.revenue").value == 5000000.0
    assert next(c for c in sec.claims if c.field == "accounts.history.2024.revenue").value == 4000000.0
    assert next(c for c in sec.claims if c.field == "accounts.history.2023.revenue").value == 3000000.0


# -------------------------------------------------------------------------
# Test 4: Nonconsecutive fiscal years
# -------------------------------------------------------------------------
def test_4_nonconsecutive_fiscal_years(tmp_path):
    org = "923609016"
    store = BlobStore(tmp_path / "blobs")
    rows = [
        make_account_row(org, 2022, rev=1500000.0, net=50000.0),
        make_account_row(org, 2025, rev=5000000.0, net=250000.0),
    ]
    resp = make_response(f"https://data.brreg.no/regnskapsregisteret/regnskap/{org}", rows)

    sec = regnskap.extract(org, resp, store)
    assert next(c for c in sec.claims if c.field == "accounts.revenue").value == 5000000.0
    rev_2022 = next((c for c in sec.claims if c.field == "accounts.history.2022.revenue"), None)
    assert rev_2022 is not None
    assert rev_2022.value == 1500000.0
    assert rev_2022.reporting_period["fiscal_year"] == "2022"


# -------------------------------------------------------------------------
# Test 5: Duplicate year records deduplicated deterministically
# -------------------------------------------------------------------------
def test_5_duplicate_year_records_deduplicated(tmp_path):
    org = "923609016"
    store = BlobStore(tmp_path / "blobs")
    # Two filings for 2024: older filing and newer filing
    row_2024_old = make_account_row(org, 2024, rev=4000000.0, net=200000.0, journalnr="2025-01-10")
    row_2024_new = make_account_row(org, 2024, rev=4200000.0, net=220000.0, journalnr="2025-03-15")
    row_2025 = make_account_row(org, 2025, rev=5000000.0, net=250000.0)

    rows = [row_2024_old, row_2024_new, row_2025]
    resp = make_response(f"https://data.brreg.no/regnskapsregisteret/regnskap/{org}", rows)

    sec = regnskap.extract(org, resp, store)
    claims_2024 = [c for c in sec.claims if c.field == "accounts.history.2024.revenue"]
    assert len(claims_2024) == 1, "Duplicate year 2024 must be deduplicated to exactly one claim"


# -------------------------------------------------------------------------
# Test 6: Restatements take precedence deterministically
# -------------------------------------------------------------------------
def test_6_restatements_precedence(tmp_path):
    org = "923609016"
    store = BlobStore(tmp_path / "blobs")
    # In Regnskapsregisteret, if multiple statements exist for the same period end,
    # the later one in submission order (or higher index) is the restatement.
    row_2024_original = make_account_row(org, 2024, rev=4000000.0, net=200000.0)
    row_2024_restated = make_account_row(org, 2024, rev=4500000.0, net=250000.0)
    row_2025 = make_account_row(org, 2025, rev=5000000.0, net=300000.0)

    # Put restated after original
    rows = [row_2024_original, row_2024_restated, row_2025]
    resp = make_response(f"https://data.brreg.no/regnskapsregisteret/regnskap/{org}", rows)

    sec = regnskap.extract(org, resp, store)
    rev_2024 = next(c for c in sec.claims if c.field == "accounts.history.2024.revenue")
    assert rev_2024.value == 4500000.0, "Restated value must take precedence"


# -------------------------------------------------------------------------
# Test 7: Missing revenue in older years (partial statements)
# -------------------------------------------------------------------------
def test_7_missing_revenue_in_older_years(tmp_path):
    org = "923609016"
    store = BlobStore(tmp_path / "blobs")
    row_2024 = make_account_row(org, 2024, rev=None, net=150000.0)
    row_2025 = make_account_row(org, 2025, rev=5000000.0, net=250000.0)

    rows = [row_2024, row_2025]
    resp = make_response(f"https://data.brreg.no/regnskapsregisteret/regnskap/{org}", rows)

    sec = regnskap.extract(org, resp, store)
    assert sec.state == "available"
    net_2024 = next(c for c in sec.claims if c.field == "accounts.history.2024.net_result")
    assert net_2024.value == 150000.0
    rev_2024 = next(c for c in sec.claims if c.field == "accounts.history.2024.revenue")
    assert rev_2024.value is None and rev_2024.availability == "not_available"


# -------------------------------------------------------------------------
# Test 8: Zero revenue (valid non-operating companies)
# -------------------------------------------------------------------------
def test_8_zero_revenue_preserves_numeric_zero(tmp_path):
    org = "923609016"
    store = BlobStore(tmp_path / "blobs")
    row_2024 = make_account_row(org, 2024, rev=0.0, net=-10000.0)
    row_2025 = make_account_row(org, 2025, rev=0.0, net=-5000.0)

    rows = [row_2024, row_2025]
    resp = make_response(f"https://data.brreg.no/regnskapsregisteret/regnskap/{org}", rows)

    sec = regnskap.extract(org, resp, store)
    rev_latest = next(c for c in sec.claims if c.field == "accounts.revenue")
    assert rev_latest.value == 0.0 and rev_latest.availability == "available"
    rev_prior = next(c for c in sec.claims if c.field == "accounts.history.2024.revenue")
    assert rev_prior.value == 0.0 and rev_prior.availability == "available"


# -------------------------------------------------------------------------
# Test 9: Negative profits and losses across years
# -------------------------------------------------------------------------
def test_9_negative_profits_and_losses_across_years(tmp_path):
    org = "923609016"
    store = BlobStore(tmp_path / "blobs")
    row_2024 = make_account_row(org, 2024, rev=2000000.0, net=-350000.0)
    row_2025 = make_account_row(org, 2025, rev=3000000.0, net=150000.0)

    rows = [row_2024, row_2025]
    resp = make_response(f"https://data.brreg.no/regnskapsregisteret/regnskap/{org}", rows)

    sec = regnskap.extract(org, resp, store)
    assert next(c for c in sec.claims if c.field == "accounts.net_result").value == 150000.0
    assert next(c for c in sec.claims if c.field == "accounts.history.2024.net_result").value == -350000.0


# -------------------------------------------------------------------------
# Test 10: Different currencies
# -------------------------------------------------------------------------
def test_10_different_currencies_handling(tmp_path):
    org = "923609016"
    store = BlobStore(tmp_path / "blobs")
    row_2024 = make_account_row(org, 2024, rev=100000.0, net=10000.0, currency="EUR")
    row_2025 = make_account_row(org, 2025, rev=120000.0, net=15000.0, currency="EUR")

    rows = [row_2024, row_2025]
    resp = make_response(f"https://data.brreg.no/regnskapsregisteret/regnskap/{org}", rows)

    sec = regnskap.extract(org, resp, store)
    c_2025 = next(c for c in sec.claims if c.field == "accounts.revenue")
    c_2024 = next(c for c in sec.claims if c.field == "accounts.history.2024.revenue")
    assert c_2025.reporting_period["currency"] == "EUR"
    assert c_2025.reporting_period["unit"] is None  # NOK unit calibration not applied
    assert c_2024.reporting_period["currency"] == "EUR"
    assert c_2024.reporting_period["unit"] is None


# -------------------------------------------------------------------------
# Test 11: Invalid/incomplete accounts handled gracefully
# -------------------------------------------------------------------------
def test_11_invalid_incomplete_accounts_handled_gracefully(tmp_path):
    org = "923609016"
    store = BlobStore(tmp_path / "blobs")
    # Row with missing regnskapsperiode or malformed virksomhet
    bad_row = {"regnskapstype": "SELSKAP", "virksomhet": None}
    valid_row = make_account_row(org, 2025, rev=1000000.0, net=50000.0)

    rows = [bad_row, valid_row]
    resp = make_response(f"https://data.brreg.no/regnskapsregisteret/regnskap/{org}", rows)

    sec = regnskap.extract(org, resp, store)
    assert sec.state == "available"
    assert next(c for c in sec.claims if c.field == "accounts.revenue").value == 1000000.0


# -------------------------------------------------------------------------
# Test 12: Consolidated vs. individual (SELSKAP vs. KONSERN)
# -------------------------------------------------------------------------
def test_12_consolidated_vs_individual_filter(tmp_path):
    org = "923609016"
    store = BlobStore(tmp_path / "blobs")
    row_selskap_2024 = make_account_row(org, 2024, rev=2000000.0, net=100000.0, account_type="SELSKAP")
    row_selskap_2025 = make_account_row(org, 2025, rev=3000000.0, net=150000.0, account_type="SELSKAP")
    row_konsern_2024 = make_account_row(org, 2024, rev=99000000.0, net=990000.0, account_type="KONSERN")
    row_konsern_2025 = make_account_row(org, 2025, rev=99900000.0, net=999000.0, account_type="KONSERN")

    rows = [row_selskap_2024, row_selskap_2025, row_konsern_2024, row_konsern_2025]
    resp = make_response(f"https://data.brreg.no/regnskapsregisteret/regnskap/{org}", rows)

    sec = regnskap.extract(org, resp, store)
    assert next(c for c in sec.claims if c.field == "accounts.revenue").value == 3000000.0
    assert next(c for c in sec.claims if c.field == "accounts.history.2024.revenue").value == 2000000.0
    # Group accounts are retained separately and never become company metrics.
    for c in sec.claims:
        if not c.field.startswith('accounts.consolidated.'):
            assert c.value != 99000000.0 and c.value != 99900000.0
    assert next(c for c in sec.claims if c.field=='accounts.consolidated.2024.revenue').value==99000000.0
    assert next(c for c in sec.claims if c.field=='accounts.consolidated.2025.revenue').value==99900000.0
    assert all(c.reporting_period['account_type']=='KONSERN' for c in sec.claims if c.field.startswith('accounts.consolidated.'))


# -------------------------------------------------------------------------
# Test 13: Latest-year backward compatibility (real fixture)
# -------------------------------------------------------------------------
def test_13_latest_year_backward_compatibility(tmp_path):
    org = "823884362"
    blob_path = Path("tests/fixtures/integration_bundle/blobs/5532fdca11301e14e6d88c1fa93d12cb7fdcfabbc387114c2d2dbec52f2a6ca9")
    raw = blob_path.read_bytes()
    store = BlobStore(tmp_path / "blobs")

    class Resp:
        url = f"https://data.brreg.no/regnskapsregisteret/regnskap/{org}"
        body = raw
        sha = blob_path.name
        retrieved_at = "2026-10-21T00:00:00Z"
        status = 200

    sec = regnskap.extract(org, Resp, store)
    # Baseline expected values for 2025
    assert next(c for c in sec.claims if c.field == "accounts.revenue").value == 113580676.0
    assert next(c for c in sec.claims if c.field == "accounts.operating_result").value == 3786576.0
    assert next(c for c in sec.claims if c.field == "accounts.result_before_tax").value == 3600543.0
    assert next(c for c in sec.claims if c.field == "accounts.net_result").value == 2744402.0
    assert next(c for c in sec.claims if c.field == "accounts.equity").value == 5080610.0
    assert next(c for c in sec.claims if c.field == "accounts.total_assets").value == 36156807.0


# -------------------------------------------------------------------------
# Test 14: Claim-field uniqueness invariant
# -------------------------------------------------------------------------
def test_14_claim_field_uniqueness_invariant(tmp_path):
    cfg = config(tmp_path, ["923609016"])

    def multi_year_handler(request):
        res = handler()(request)
        if "/regnskapsregisteret/" in request.url.path:
            rows = [
                make_account_row("923609016", 2023, rev=1000000.0, net=50000.0),
                make_account_row("923609016", 2024, rev=2000000.0, net=100000.0),
                make_account_row("923609016", 2025, rev=3000000.0, net=150000.0),
            ]
            return httpx.Response(200, json=rows)
        return res

    report, rows = execute(cfg, multi_year_handler)
    env = rows[0]
    claims = env["claims"]
    field_names = [c["field"] for c in claims]
    assert len(field_names) == len(set(field_names)), "All claim fields in envelope must be unique"


# -------------------------------------------------------------------------
# Test 15: Evidence and SHA-256 integrity
# -------------------------------------------------------------------------
def test_15_evidence_and_sha256_integrity(tmp_path):
    cfg = config(tmp_path, ["923609016"])

    def multi_year_handler(request):
        res = handler()(request)
        if "/regnskapsregisteret/" in request.url.path:
            rows = [
                make_account_row("923609016", 2024, rev=2000000.0, net=100000.0),
                make_account_row("923609016", 2025, rev=3000000.0, net=150000.0),
            ]
            return httpx.Response(200, json=rows)
        return res

    report, rows = execute(cfg, multi_year_handler)
    env = rows[0]
    evidence_map = {e["id"]: e for e in env["evidence"]}

    # Check prior year claim evidence
    claim_2024 = next(c for c in env["claims"] if c["field"] == "accounts.history.2024.revenue")
    assert len(claim_2024["evidence_ids"]) >= 1
    registry_ev = [evidence_map[eid] for eid in claim_2024["evidence_ids"] if evidence_map[eid]["source_class"] == "official_registry"]
    assert len(registry_ev) == 1
    assert registry_ev[0]["content_sha256"] is not None
    # Locator should point to the correct JSON index
    assert registry_ev[0]["locator"].startswith("/")


# -------------------------------------------------------------------------
# Test 16: Reporting-period correctness
# -------------------------------------------------------------------------
def test_16_reporting_period_correctness(tmp_path):
    org = "923609016"
    store = BlobStore(tmp_path / "blobs")
    rows = [
        make_account_row(org, 2024, rev=2000000.0, net=100000.0),
        make_account_row(org, 2025, rev=3000000.0, net=150000.0),
    ]
    resp = make_response(f"https://data.brreg.no/regnskapsregisteret/regnskap/{org}", rows)

    sec = regnskap.extract(org, resp, store)
    c_2024 = next(c for c in sec.claims if c.field == "accounts.history.2024.revenue")
    rp = c_2024.reporting_period
    assert rp["fiscal_year"] == "2024"
    assert rp["period_start"] == "2024-01-01"
    assert rp["period_end"] == "2024-12-31"
    assert rp["currency"] == "NOK"
    assert rp["account_type"] == "SELSKAP"


# -------------------------------------------------------------------------
# Test 17: Historical refresh stability
# -------------------------------------------------------------------------
def test_17_historical_refresh_stability(tmp_path):
    cfg1 = config(tmp_path / "run1", ["923609016"])

    def rows_provider():
        return [
            make_account_row("923609016", 2024, rev=2000000.0, net=100000.0),
            make_account_row("923609016", 2025, rev=3000000.0, net=150000.0),
        ]

    def transport(request):
        res = handler()(request)
        if "/regnskapsregisteret/" in request.url.path:
            return httpx.Response(200, json=rows_provider())
        return res

    report1, envs1 = execute(cfg1, transport)

    # Run 2: Refresh mode with same data
    cfg2 = config(tmp_path / "run2", ["923609016"], previous=cfg1.output)
    report2, envs2 = execute(cfg2, transport)

    env2 = envs2[0]
    assert env2["run"]["refresh"]["mode"] == "refresh"
    # No spurious observation changes or dropped claims for accounts
    account_obs = [o for o in env2["run"]["refresh"].get("observation_changes", []) if o.get("section") == "accounts"]
    assert len(account_obs) == 0, f"Expected 0 account observation changes on identical refresh, got {account_obs}"


# -------------------------------------------------------------------------
# Test 18: Deterministic output
# -------------------------------------------------------------------------
def test_18_deterministic_output(tmp_path):
    cfg1 = config(tmp_path / "run1", ["923609016"])
    cfg2 = config(tmp_path / "run2", ["923609016"])

    def transport(request):
        res = handler()(request)
        if "/regnskapsregisteret/" in request.url.path:
            return httpx.Response(200, json=[
                make_account_row("923609016", 2023, rev=1000000.0, net=50000.0),
                make_account_row("923609016", 2024, rev=2000000.0, net=100000.0),
                make_account_row("923609016", 2025, rev=3000000.0, net=150000.0),
            ])
        return res

    _, envs1 = execute(cfg1, transport)
    _, envs2 = execute(cfg2, transport)

    claims1 = [(c["field"], c["value"], c["id"]) for c in envs1[0]["claims"]]
    claims2 = [(c["field"], c["value"], c["id"]) for c in envs2[0]["claims"]]
    assert claims1 == claims2, "Repeated execution must produce identical claim IDs and values"


# -------------------------------------------------------------------------
# Test 19: Zero additional HTTP requests
# -------------------------------------------------------------------------
def test_19_zero_additional_http_requests(tmp_path):
    cfg = config(tmp_path, ["923609016"])
    requests_made = []

    def transport(request):
        requests_made.append(str(request.url))
        res = handler()(request)
        if "/regnskapsregisteret/" in request.url.path:
            return httpx.Response(200, json=[
                make_account_row("923609016", 2023, rev=1000000.0, net=50000.0),
                make_account_row("923609016", 2024, rev=2000000.0, net=100000.0),
                make_account_row("923609016", 2025, rev=3000000.0, net=150000.0),
            ])
        return res

    report, rows = execute(cfg, transport)
    regnskap_requests = [r for r in requests_made if "/regnskapsregisteret/" in r]
    assert len(regnskap_requests) == 1, f"Expected exactly 1 request to regnskap API, got {len(regnskap_requests)}"


# -------------------------------------------------------------------------
# Test 20: All evaluator schema constraints and profile projection
# -------------------------------------------------------------------------
def test_20_all_evaluator_schema_constraints_and_profiles(tmp_path):
    cfg = config(tmp_path, ["923609016"], profiles_output=tmp_path / "profiles.jsonl")

    def transport(request):
        res = handler()(request)
        if "/regnskapsregisteret/" in request.url.path:
            return httpx.Response(200, json=[
                make_account_row("923609016", 2023, rev=1000000.0, net=50000.0),
                make_account_row("923609016", 2024, rev=2000000.0, net=100000.0),
                make_account_row("923609016", 2025, rev=3000000.0, net=150000.0),
            ])
        return res

    report, rows = execute(cfg, transport)
    raw_env = rows[0]

    # Validate against all 3 schema shapes
    validate(raw_env, "union")
    validate(serialize(Envelope.model_validate(raw_env), "contract"), "contract")
    validate(serialize(Envelope.model_validate(raw_env), "reference"), "reference")

    # Validate profile output projection
    profiles_text = cfg.profiles_output.read_text(encoding="utf-8")
    profile = json.loads(profiles_text.splitlines()[0])
    records = profile["evidence"]["financials"]["value"]["records"]
    assert len(records) == 3, f"Profile financials.records must contain 3 fiscal years, got {len(records)}"

    # Check chronological ordering: latest first
    assert records[0]["period"]["tilDato"] == "2025-12-31"
    assert records[0]["revenue"] == 3000000.0
    assert records[1]["period"]["tilDato"] == "2024-12-31"
    assert records[1]["revenue"] == 2000000.0
    assert records[2]["period"]["tilDato"] == "2023-12-31"
    assert records[2]["revenue"] == 1000000.0
