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
from signalpost.sources.nav_manifest import (
    CERT_COMPLETE,
    CERT_INTEGRITY_FAILED,
    certify_index_data,
)


def test_v6_03_nav_manifest_strict_certification():
    """
    V6-03: Malformed inputs (unsupported schema, external cursor, bad UUID, bad employer orgnr)
    must fail certification with INTEGRITY_FAILED and usable=False.
    """
    now = datetime(2026, 10, 21, 12, 0, 0, tzinfo=timezone.utc)
    built = now.isoformat().replace("+00:00", "Z")

    # 1. Unsupported schema
    bad_schema = {
        "schema_version": 999,
        "index_version": "v1",
        "built_at": built,
        "cursor": "https://pam-stilling-feed.nav.no/api/v1/feed/11111111-1111-1111-1111-111111111111",
        "ads": [
            {
                "uuid": "11111111-1111-1111-1111-111111111111",
                "employer_orgnr": "923609016",
                "status": "ACTIVE",
                "published": built,
                "expires": "2026-12-31T23:59:59Z",
            }
        ],
    }
    m1 = certify_index_data(bad_schema, now=now)
    assert m1.certification_status == CERT_INTEGRITY_FAILED
    assert any("unsupported_schema_version" in r for r in m1.reasons)
    assert m1.is_usable_for_publication() is False

    # 2. External / evil cursor
    bad_cursor = dict(bad_schema)
    bad_cursor["schema_version"] = 1
    bad_cursor["cursor"] = "https://evil.invalid/feed/attack"
    m2 = certify_index_data(bad_cursor, now=now)
    assert m2.certification_status == CERT_INTEGRITY_FAILED
    assert any("invalid_cursor_external_url" in r for r in m2.reasons)
    assert m2.is_usable_for_publication() is False

    # 3. Invalid ad UUID
    bad_uuid = dict(bad_schema)
    bad_uuid["schema_version"] = 1
    bad_uuid["cursor"] = "https://pam-stilling-feed.nav.no/api/v1/feed/11111111-1111-1111-1111-111111111111"
    bad_uuid["ads"] = [
        {
            "uuid": "not-a-valid-uuid",
            "employer_orgnr": "923609016",
            "status": "ACTIVE",
            "published": built,
            "expires": "2026-12-31T23:59:59Z",
        }
    ]
    m3 = certify_index_data(bad_uuid, now=now)
    assert m3.certification_status == CERT_INTEGRITY_FAILED
    assert any("invalid_uuid" in r for r in m3.reasons)
    assert m3.is_usable_for_publication() is False

    # 4. Invalid employer orgnr
    bad_org = dict(bad_schema)
    bad_org["schema_version"] = 1
    bad_org["cursor"] = "https://pam-stilling-feed.nav.no/api/v1/feed/11111111-1111-1111-1111-111111111111"
    bad_org["ads"] = [
        {
            "uuid": "11111111-1111-1111-1111-111111111111",
            "employer_orgnr": "12345",  # invalid
            "status": "ACTIVE",
            "published": built,
            "expires": "2026-12-31T23:59:59Z",
        }
    ]
    m4 = certify_index_data(bad_org, now=now)
    assert m4.certification_status == CERT_INTEGRITY_FAILED
    assert any("invalid_employer_orgnr" in r for r in m4.reasons)
    assert m4.is_usable_for_publication() is False

    # 5. Clean valid index
    good_index = dict(bad_schema)
    good_index["schema_version"] = 1
    good_index["cursor"] = "https://pam-stilling-feed.nav.no/api/v1/feed/11111111-1111-1111-1111-111111111111"
    m5 = certify_index_data(good_index, now=now)
    assert m5.certification_status == CERT_COMPLETE
    assert m5.is_usable_for_publication() is True


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
