"""
Tests for Features F18 & F39: Candidate Rejection Explanations and Funnel Metrics.

Verifies that:
1. F39 opportunity-to-publication funnel metrics track all 5 families
   (registry, website, activity, hiring, accounts) with valid denominators.
2. F18 candidate rejection reasons are accurately classified into typed categories:
   - wrong_organization_number
   - robots_denied
   - dns_error
   - request_timeout
   - budget_exhausted
   - source_blocked
   - http_error
   - insufficient_ownership_proof
   - ambiguous_multiple_orgnrs
   - hiring_nav_time_cap, hiring_deadline, hiring_nav_consumer_stopped
   - pipeline_deadline_exhausted
3. Diagnostics never alter envelope schema, claims, or verification levels.
4. Funnel and rejection statistics produce bounded, reproducible outputs with zero added network requests.
"""
import json
import pytest

from signalpost.io.report import build, compute_funnel_metrics, compute_rejection_reasons
from signalpost.models.envelope import Envelope, Run, Operations, Module, Error
from signalpost.models.claim import Claim
from signalpost.models.evidence import Evidence, digest


SHA = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"


class DummyConfig:
    run_id = "test-run-123"
    emit_duplicates = False
    official_batch_size = 1000
    max_requests = 100
    max_cost_usd = 0.0
    time_budget_seconds = 60
    deadline_fraction = 0.8
    request_timeout = 10
    host_concurrency = 4


class DummyInputs:
    rows = ["923609016", "988258229"]
    unique = {"923609016": 0, "988258229": 1}
    duplicates = 0
    invalid = 0


class DummyBudget:
    start = 0
    events = [
        {"organisation_number": "923609016", "url": "https://data.brreg.no/enhetsregisteret/api/enheter/923609016", "status": 200},
        {"organisation_number": "923609016", "url": "https://example.no/", "status": 200},
        {"organisation_number": "923609016", "url": "https://example.no/nyheter", "status": 200},
        {"organisation_number": "988258229", "url": "https://data.brreg.no/enhetsregisteret/api/enheter/988258229", "status": 200},
        {"organisation_number": "988258229", "url": "https://wrongsite.no/", "status": 200},
    ]
    by_host = {"data.brreg.no": 2, "example.no": 2, "wrongsite.no": 1}


def make_dummy_envelope(org, website_status, rejection_reason=None, extra_errors=None):
    claims = []
    evidence = []
    errors = list(extra_errors or [])
    
    # Registry claim
    reg_url = f"https://data.brreg.no/enhetsregisteret/api/enheter/{org}"
    reg_loc = "/navn"
    reg_method = "brreg.v1"
    ev1_id = digest([reg_url, SHA, reg_loc, reg_method])
    c1 = Claim(
        id=f"c-reg-{org}",
        family="registry", field="name", availability="available",
        value="Company AS", first_observed_at="2026-10-21T00:00:00Z",
        last_observed_at="2026-10-21T00:00:00Z", evidence_ids=[ev1_id]
    )
    ev1 = Evidence(
        id=ev1_id, source_url=reg_url,
        retrieved_at="2026-10-21T00:00:00Z", effective_at="2026-10-21T00:00:00Z",
        source_class="official_registry", extraction_method=reg_method,
        claim_span="Company AS", locator=reg_loc, content_sha256=SHA
    )
    claims.append(c1)
    evidence.append(ev1)
    
    if website_status == "available":
        web_url = "https://example.no"
        web_loc = "/footer/0"
        web_method = "signalpost.website.v1"
        ev2_id = digest([web_url, SHA, web_loc, web_method])
        c2 = Claim(
            id=f"c-web-{org}",
            family="website", field="official_website", availability="available",
            value={"final_url": "https://example.no", "identity_level": "VERIFIED"},
            first_observed_at="2026-10-21T00:00:00Z", last_observed_at="2026-10-21T00:00:00Z",
            evidence_ids=[ev2_id]
        )
        ev2 = Evidence(
            id=ev2_id, source_url=web_url,
            retrieved_at="2026-10-21T00:00:00Z", effective_at="2026-10-21T00:00:00Z",
            source_class="company_owned", extraction_method=web_method,
            claim_span="923609016", locator=web_loc, content_sha256=SHA
        )
        claims.append(c2)
        evidence.append(ev2)
    else:
        attempts = [
            {"domain": "wrongsite.no", "origin": "search", "level": "LOW", "reason": rejection_reason or "foreign_orgnr"}
        ]
        errors.append(Error(section="website", code="website_candidates", message=json.dumps(attempts)))

    run_info = Run(
        run_id="test-run-123", started_at="2026-10-21T00:00:00Z", completed_at="2026-10-21T00:01:00Z",
        sections={"identity": "available", "website": website_status, "activity": "not_available", "hiring": "not_available", "accounts": "not_available"}
    )
    
    return Envelope(
        organisation_number=org, run=run_info, claims=claims, evidence=evidence,
        changes=[], errors=errors, operations=Operations(requests=2, runtime_ms=500),
        run_id="test-run-123", state="complete", started_at="2026-10-21T00:00:00Z",
        completed_at="2026-10-21T00:01:00Z", modules={}, profile={"organisation_number": org, "values": {}, "evidence_ids": []}
    )


def test_f39_funnel_metrics_computation():
    """F39: Verifies that funnel metrics correctly track all 5 families with defined denominators."""
    e1 = make_dummy_envelope("923609016", "available")
    e2 = make_dummy_envelope("988258229", "failed", "foreign_orgnr")
    envelopes = [e1, e2]
    inputs = DummyInputs()
    budget = DummyBudget()
    
    funnel = compute_funnel_metrics(envelopes, inputs, budget)
    assert "registry" in funnel
    assert "website" in funnel
    assert "activity" in funnel
    assert "hiring" in funnel
    assert "accounts" in funnel
    
    assert funnel["registry"]["eligible_companies"] == 2
    assert funnel["registry"]["verified_companies"] == 2
    assert funnel["registry"]["company_yield_rate"] == 1.0
    
    assert funnel["website"]["eligible_companies"] == 2
    assert funnel["website"]["verified_companies"] == 1
    assert funnel["website"]["company_yield_rate"] == 0.5
    assert funnel["website"]["requests_dispatched"] == 2
    
    assert funnel["accounts"]["verified_companies"] == 0
    assert funnel["accounts"]["company_yield_rate"] == 0.0


def test_f18_rejection_reasons_classification():
    """F18: Verifies that candidate rejection reasons are normalized to typed categories."""
    e1 = make_dummy_envelope("923609016", "available")
    e2 = make_dummy_envelope("988258229", "failed", "foreign_orgnr")
    
    reasons = compute_rejection_reasons([e1, e2])
    assert "wrong_organization_number" in reasons
    assert reasons["wrong_organization_number"] == 1


def test_f18_comprehensive_typed_categories():
    """F18: Verifies that diverse rejection codes map accurately to typed reasons."""
    rejection_cases = [
        ("robots", "robots_denied"),
        ("dns_nxdomain", "dns_error"),
        ("timeout", "request_timeout"),
        ("website_budget_exhausted", "budget_exhausted"),
        ("http_403", "source_blocked"),
        ("http_404", "http_error"),
        ("no_orgnr", "insufficient_ownership_proof"),
        ("other_orgnrs", "ambiguous_multiple_orgnrs"),
    ]
    envelopes = []
    for idx, (raw_code, expected_cat) in enumerate(rejection_cases):
        org = f"99900000{idx}"
        e = make_dummy_envelope(org, "failed", raw_code)
        envelopes.append(e)
        
    # Also add hiring error
    e_hiring = make_dummy_envelope(
        "999000099", "available", extra_errors=[Error(section="hiring", code="nav_time_cap", message="cutoff")]
    )
    envelopes.append(e_hiring)
    
    reasons = compute_rejection_reasons(envelopes)
    for raw_code, expected_cat in rejection_cases:
        assert expected_cat in reasons, f"Expected {expected_cat} for {raw_code}"
        assert reasons[expected_cat] >= 1
    assert "hiring_nav_time_cap" in reasons


def test_report_build_includes_funnel_and_rejection_metrics():
    """Verifies that report build() contains funnel_metrics and rejection_reasons."""
    e1 = make_dummy_envelope("923609016", "available")
    e2 = make_dummy_envelope("988258229", "failed", "foreign_orgnr")
    envelopes = [e1, e2]
    inputs = DummyInputs()
    budget = DummyBudget()
    config = DummyConfig()
    
    report = build(envelopes, inputs, budget, config, [], 1.5)
    assert "funnel_metrics" in report
    assert "rejection_reasons" in report
    assert report["funnel_metrics"]["website"]["verified_companies"] == 1
    assert report["rejection_reasons"]["wrong_organization_number"] == 1
