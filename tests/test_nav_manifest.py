"""Unit and adversarial verification for NAV Index Manifest and Checkpoints (F05 & F06)."""
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import pytest

from signalpost.sources.nav_manifest import (
    IndexManifest,
    certify_index_data,
    NavCheckpointManager,
    CERT_COMPLETE,
    CERT_PARTIAL,
    CERT_STALE,
    CERT_INTEGRITY_FAILED
)


def sample_ad(uuid="00000000-0000-0000-0000-000000000001", org="923609016", status="ACTIVE", expires="2026-11-01T00:00:00Z"):
    return {
        "uuid": uuid,
        "employer_orgnr": org,
        "status": status,
        "published": "2026-10-01T00:00:00Z",
        "expires": expires,
        "last_modified": "2026-10-01T00:00:00Z",
        "etag": None
    }


def test_certify_complete_fresh_index():
    now = datetime(2026, 10, 21, 12, 0, 0, tzinfo=timezone.utc)
    built = (now - timedelta(days=5)).isoformat().replace("+00:00", "Z")
    data = {
        "schema_version": 1,
        "index_version": "test-v1",
        "built_at": built,
        "cursor": "https://pam-stilling-feed.nav.no/api/v1/feed/11111111-1111-1111-1111-111111111111",
        "source_urls": ["https://pam-stilling-feed.nav.no/api/v1/feed"],
        "ads_count": 2,
        "employer_count": 1,
        "failed_details": 0,
        "seeded_from_disk": 0,
        "fresh_fetched_ads": 2,
        "ads": [
            sample_ad(uuid="00000000-0000-0000-0000-000000000001", expires="2026-11-01T00:00:00Z"),
            sample_ad(uuid="00000000-0000-0000-0000-000000000002", expires="2026-10-15T00:00:00Z")  # Expired
        ]
    }
    manifest = certify_index_data(data, now=now)
    assert manifest.certification_status == CERT_COMPLETE
    assert manifest.total_ads_count == 2
    assert manifest.active_unexpired_count == 1
    assert manifest.expired_count == 1
    assert manifest.distinct_employer_orgnrs == 1
    assert manifest.is_usable_for_publication() is True


def test_certify_stale_index():
    now = datetime(2026, 10, 21, 12, 0, 0, tzinfo=timezone.utc)
    built = (now - timedelta(days=25)).isoformat().replace("+00:00", "Z")
    data = {
        "schema_version": 1,
        "index_version": "test-v1",
        "built_at": built,
        "cursor": "https://pam-stilling-feed.nav.no/api/v1/feed/11111111-1111-1111-1111-111111111111",
        "ads": [sample_ad()]
    }
    manifest = certify_index_data(data, now=now, max_age_days=21)
    assert manifest.certification_status == CERT_STALE
    assert any("index_stale" in r for r in manifest.reasons)
    assert manifest.is_usable_for_publication() is False


def test_certify_partial_index_with_failed_details():
    now = datetime(2026, 10, 21, 12, 0, 0, tzinfo=timezone.utc)
    built = (now - timedelta(days=2)).isoformat().replace("+00:00", "Z")
    data = {
        "schema_version": 1,
        "index_version": "test-v1",
        "built_at": built,
        "cursor": "https://pam-stilling-feed.nav.no/api/v1/feed/11111111-1111-1111-1111-111111111111",
        "failed_details": 5,
        "ads": [sample_ad()]
    }
    manifest = certify_index_data(data, now=now)
    assert manifest.certification_status == CERT_PARTIAL
    assert any("failed_details" in r for r in manifest.reasons)


def test_certify_corrupt_ad_invalid_orgnr():
    now = datetime(2026, 10, 21, 12, 0, 0, tzinfo=timezone.utc)
    built = (now - timedelta(days=1)).isoformat().replace("+00:00", "Z")
    data = {
        "schema_version": 1,
        "index_version": "test-v1",
        "built_at": built,
        "cursor": "https://pam-stilling-feed.nav.no/api/v1/feed/11111111-1111-1111-1111-111111111111",
        "ads": [sample_ad(org="12345")]  # Invalid orgnr
    }
    manifest = certify_index_data(data, now=now)
    assert manifest.distinct_employer_orgnrs == 0
    assert any("invalid_employer_orgnr" in r for r in manifest.reasons)


def test_transactional_checkpoint_atomic_save_and_load(tmp_path):
    cp_file = tmp_path / "nav_checkpoint.json"
    mgr = NavCheckpointManager(cp_file)

    # Initial state
    assert mgr.load_checkpoint() is None

    # Atomic write
    ok = mgr.save_checkpoint(
        cursor="https://pam-stilling-feed.nav.no/api/v1/feed/next-uuid",
        pages_processed=10,
        items_processed=500,
        extra={"last_sync": "2026-10-21"}
    )
    assert ok is True
    assert cp_file.exists()

    # Load and verify
    data = mgr.load_checkpoint()
    assert data is not None
    assert data["cursor"] == "https://pam-stilling-feed.nav.no/api/v1/feed/next-uuid"
    assert data["pages_processed"] == 10
    assert data["items_processed"] == 500
    assert data["extra"]["last_sync"] == "2026-10-21"
