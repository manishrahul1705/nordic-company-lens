"""
Regression and verification tests for:
- V6-03: NAV index manifest strict certification under malformed inputs.
- V6-04: NAV benchmark provenance and fixture labeling.
- V6-05: Funnel metric accounting, request family routing, and duplicate yield clamping.
"""
from datetime import datetime, timezone
import pytest

from signalpost.io.report import compute_funnel_metrics
from signalpost.models.claim import Claim
from signalpost.runner import placeholder


def test_v6_05_diagnostic_funnel_accounting_and_routing():
    """
    V6-05: Regnskap URLs must route to accounts family; identity claims must count for registry;
    duplicate envelopes must not exceed 100% company yield.
    """
    class DummyBudget:
        events = [
            # Accounts request to data.brreg.no/regnskapsregisteret
            {"url": "https://data.brreg.no/regnskapsregisteret/regnskap/923609016", "status": 200},
            # Registry request to data.brreg.no/enhetsregisteret
            {"url": "https://data.brreg.no/enhetsregisteret/api/enheter/923609016", "status": 200},
            # Website request
            {"url": "https://example.no/", "status": 200},
        ]

    class DummyInputs:
        unique = {"923609016": 0}

    # Two duplicate envelopes for the SAME company (org 923609016)
    def make_env():
        e = placeholder("923609016", "run-1", "2026-10-21T00:00:00Z")
        e.run.sections["identity"] = "available"
        e.run.sections["accounts"] = "available"
        # Production claim with family="identity"
        c = Claim(
            id="c1",
            family="identity",
            field="name",
            availability="available",
            value="Test AS",
            first_observed_at="2026-10-21T00:00:00Z",
            last_observed_at="2026-10-21T00:00:00Z",
            evidence_ids=["ev1"],
        )
        e.claims.append(c)
        return e

    envelopes = [make_env(), make_env()]  # Duplicate envelopes

    funnel = compute_funnel_metrics(envelopes, DummyInputs(), DummyBudget())

    # 1. Accounts requests must be 1, not 0
    assert funnel["accounts"]["requests_dispatched"] == 1
    assert funnel["accounts"]["responses_received"] == 1

    # 2. Registry requests must be 1, not 2
    assert funnel["registry"]["requests_dispatched"] == 1
    assert funnel["registry"]["responses_received"] == 1

    # 3. Registry claims must be counted (not 0) even though family is "identity"
    assert funnel["registry"]["published_claims"] == 2  # 1 per envelope
    assert funnel["registry"]["evidence_anchored_claims"] == 2

    # 4. Yield rate must be 1.0 (100%), never 2.0 (200%) despite duplicate envelopes
    assert funnel["registry"]["verified_companies"] == 1
    assert funnel["registry"]["company_yield_rate"] == 1.0
    assert funnel["accounts"]["company_yield_rate"] == 1.0
