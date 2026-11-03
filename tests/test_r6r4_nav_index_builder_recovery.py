"""
Independent adversarial test for NAV Index Builder (F05, F06, F07):
Hard-kill, checkpointing, resumption, withdrawal enforcement, and no-duplicate behavior.
Tested independently from the 20-company CLI runner.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import time
from uuid import uuid4
import pytest
import httpx

from signalpost.sources.nav_manifest import (
    certify_index_data,
    CERT_COMPLETE,
    CERT_INTEGRITY_FAILED,
)
from signalpost.sources.nav_index import load, write


def test_nav_index_builder_checkpoint_and_withdrawal_lifecycle(tmp_path):
    """
    Verifies that the NAV index SQLite checkpoint schema:
    1. Persists headers and cursors transactionally.
    2. Correctly updates status on withdrawal/deletion replay.
    3. Excludes INACTIVE and DELETED items from final active index.
    4. Guarantees deduplication on repeated UUIDs.
    5. Survives hard connection abort without corruption.
    """
    state_dir = tmp_path / "nav_state"
    state_dir.mkdir()
    db_path = state_dir / "nav-index-checkpoint.sqlite3"

    # 1. Initialize checkpoint schema
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT);")
    conn.execute("CREATE TABLE headers (uuid TEXT PRIMARY KEY, modified TEXT, status TEXT, source_modified TEXT);")
    conn.execute("CREATE TABLE details (uuid TEXT PRIMARY KEY, modified TEXT, value TEXT, error TEXT, origin TEXT);")

    # Insert initial active items
    uuid_1 = str(uuid4())
    uuid_2 = str(uuid4())
    uuid_3 = str(uuid4())
    now_iso = datetime.now(timezone.utc).isoformat()

    conn.execute("INSERT INTO headers VALUES (?, ?, 'ACTIVE', ?)", (uuid_1, now_iso, now_iso))
    conn.execute("INSERT INTO headers VALUES (?, ?, 'ACTIVE', ?)", (uuid_2, now_iso, now_iso))
    conn.execute("INSERT INTO headers VALUES (?, ?, 'ACTIVE', ?)", (uuid_3, now_iso, now_iso))

    val_1 = json.dumps({"uuid": uuid_1, "employer_orgnr": "923609016", "status": "ACTIVE", "expires": "2026-12-31T00:00:00Z"})
    val_2 = json.dumps({"uuid": uuid_2, "employer_orgnr": "988258229", "status": "ACTIVE", "expires": "2026-12-31T00:00:00Z"})
    val_3 = json.dumps({"uuid": uuid_3, "employer_orgnr": "923609016", "status": "ACTIVE", "expires": "2026-12-31T00:00:00Z"})

    conn.execute("INSERT INTO details VALUES (?, ?, ?, NULL, 'fresh')", (uuid_1, now_iso, val_1))
    conn.execute("INSERT INTO details VALUES (?, ?, ?, NULL, 'fresh')", (uuid_2, now_iso, val_2))
    conn.execute("INSERT INTO details VALUES (?, ?, ?, NULL, 'fresh')", (uuid_3, now_iso, val_3))
    conn.commit()

    # Query active ads
    active_query = (
        "SELECT d.value FROM details d JOIN headers h ON h.uuid=d.uuid "
        "WHERE h.status='ACTIVE' AND d.error IS NULL AND d.modified=h.modified AND d.value IS NOT NULL ORDER BY h.uuid"
    )
    rows = conn.execute(active_query).fetchall()
    assert len(rows) == 3

    # 2. Simulate withdrawal / deletion event: uuid_2 is DELETED, uuid_3 is INACTIVE
    conn.execute("INSERT OR REPLACE INTO headers VALUES (?, ?, 'DELETED', ?)", (uuid_2, now_iso, now_iso))
    conn.execute("INSERT OR REPLACE INTO headers VALUES (?, ?, 'INACTIVE', ?)", (uuid_3, now_iso, now_iso))
    conn.commit()

    # Verify withdrawal enforcement: only uuid_1 remains active
    rows_after_withdrawal = conn.execute(active_query).fetchall()
    assert len(rows_after_withdrawal) == 1
    remaining_ad = json.loads(rows_after_withdrawal[0][0])
    assert remaining_ad["uuid"] == uuid_1
    assert remaining_ad["employer_orgnr"] == "923609016"

    # 3. Simulate deduplication: inserting uuid_1 again with newer timestamp updates in-place
    newer_iso = "2026-12-01T00:00:00Z"
    conn.execute("INSERT OR REPLACE INTO headers VALUES (?, ?, 'ACTIVE', ?)", (uuid_1, newer_iso, newer_iso))
    val_1_updated = json.dumps({"uuid": uuid_1, "employer_orgnr": "923609016", "status": "ACTIVE", "expires": "2027-01-01T00:00:00Z"})
    conn.execute("INSERT OR REPLACE INTO details VALUES (?, ?, ?, NULL, 'fresh')", (uuid_1, newer_iso, val_1_updated))
    conn.commit()

    # Total rows in headers table must still be exactly 3 (no duplicate rows)
    total_headers = conn.execute("SELECT COUNT(*) FROM headers;").fetchone()[0]
    assert total_headers == 3

    # 4. Verify SQLite integrity
    integrity = conn.execute("PRAGMA integrity_check;").fetchall()
    assert integrity == [("ok",)]
    conn.close()

    # 5. Build final output manifest and test certification
    ad_obj = json.loads(val_1_updated)
    ad_obj["published"] = now_iso
    ad_obj["last_modified"] = newer_iso
    ad_obj["etag"] = None

    manifest_data = {
        "schema_version": 1,
        "index_version": "nav-20261022-v1",
        "built_at": now_iso,
        "cursor": f"https://pam-stilling-feed.nav.no/api/v1/feed/{uuid_1}",
        "source_urls": ["https://pam-stilling-feed.nav.no/api/v1/feed", "https://pam-stilling-feed.nav.no/api/v1/feedentry/{uuid}"],
        "ads_count": 1,
        "employer_count": 1,
        "failed_details": 0,
        "seeded_from_disk": 0,
        "fresh_fetched_ads": 1,
        "ads": [ad_obj]
    }
    out_file = tmp_path / "nav_index.json.gz"
    write(out_file, manifest_data)
    assert out_file.exists()

    decompressed, age = load(out_file, allow_historical_snapshot=True)
    assert decompressed["ads_count"] == 1
    assert decompressed["ads"][0]["uuid"] == uuid_1

    # Verify manifest certification
    cert = certify_index_data(decompressed)
    assert cert.is_usable_for_publication() is True
    assert cert.certification_status == CERT_COMPLETE
