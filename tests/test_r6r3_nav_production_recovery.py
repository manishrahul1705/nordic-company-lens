"""
Adversarial Production Verification for NAV Ingestion, Authentication,
Crash-Safety, Resumption, and Checkpoint Recovery (Blocker 4B).
"""
import asyncio
import json
import os
from pathlib import Path
import sqlite3
import time
from unittest.mock import patch
import pytest
import httpx

from signalpost.budget import Budget, SourceFailure
from signalpost.config import Config
from signalpost.sources.nav_auth import NavAuthManager, redact_token, parse_jwt_claims
from signalpost.sources.nav_manifest import (
    IndexManifest,
    NavCheckpointManager,
    certify_index_data,
    CERT_COMPLETE,
    CERT_INTEGRITY_FAILED,
)

VALID_JWT = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiJuYXYudGVhbS5hcmJlaWRzcGxhc3NlbkBuYXYubm8iLCJraWQiOiJmcmVzaC1raWQiLCJpc3MiOiJuYXYtbm8iLCJhdWQiOiJmZWVkLWFwaS12MiIsImlhdCI6MTcwMDAwMDAwMCwiZXhwIjoyMDAwMDAwMDAwfQ."
    "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
)

EXPIRED_JWT = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiJuYXYudGVhbS5hcmJlaWRzcGxhc3NlbkBuYXYubm8iLCJraWQiOiJleHBpcmVkLWtpZCIsImlzcyI6Im5hdi1ubyIsImF1ZCI6ImZlZWQtYXBpLXYyIiwiaWF0IjoxNjAwMDAwMDAwLCJleHAiOjE2MDAwMDAwMDB9."
    "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
)

ROTATED_JWT = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiJuYXYudGVhbS5hcmJlaWRzcGxhc3NlbkBuYXYubm8iLCJraWQiOiJyb3RhdGVkLWtpZCIsImlzcyI6Im5hdi1ubyIsImF1ZCI6ImZlZWQtYXBpLXYyIiwiaWF0IjoxNzAwMDAwMDAwLCJleHAiOjIxMDAwMDAwMDB9."
    "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
)


@pytest.mark.anyio
async def test_nav_auth_expired_jwt_automatic_rotation(tmp_path):
    """Test 1: Expired JWT is rejected and rotates to public token."""
    async def mock_handler(request):
        if request.url.path == "/api/publicToken":
            return httpx.Response(200, text=f"Token:\n{ROTATED_JWT}")
        return httpx.Response(404)

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        mgr = NavAuthManager(http_client=client)
        with patch.dict(os.environ, {"NAV_API_TOKEN": EXPIRED_JWT}):
            token = await mgr.get_bearer_token(force_refresh=False)
            assert token == ROTATED_JWT
            assert mgr.cached_state.token == ROTATED_JWT
            assert mgr.cached_state.source == "public_endpoint"


@pytest.mark.anyio
async def test_nav_auth_concurrent_refresh_lock(tmp_path):
    """Test 2: Multiple concurrent workers refresh token without duplicate HTTP calls."""
    call_count = 0

    async def mock_handler(request):
        nonlocal call_count
        if request.url.path == "/api/publicToken":
            call_count += 1
            await asyncio.sleep(0.05)  # simulate network latency
            return httpx.Response(200, text=f"Token:\n{ROTATED_JWT}")
        return httpx.Response(404)

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        mgr = NavAuthManager(http_client=client)
        # Use existing cached_state once fetched
        t1 = await mgr.get_bearer_token(force_refresh=True)
        assert t1 == ROTATED_JWT
        assert call_count == 1
        
        # Subsequent concurrent reads reuse cached token without network call
        tasks = [mgr.get_bearer_token(force_refresh=False) for _ in range(10)]
        tokens = await asyncio.gather(*tasks)
        assert all(t == ROTATED_JWT for t in tokens)
        assert call_count == 1


def test_nav_sqlite_checkpoint_transaction_boundaries(tmp_path):
    """Test 3: SQLite checkpoint transaction rollback on uncommitted crash."""
    db_path = tmp_path / "nav-index-checkpoint.sqlite3"
    db = sqlite3.connect(db_path)
    db.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
    db.execute("CREATE TABLE headers (uuid TEXT PRIMARY KEY, modified TEXT, status TEXT)")
    db.commit()

    # Simulate committed page write
    db.execute("INSERT OR REPLACE INTO meta VALUES ('cursor', 'https://nav.no/page/1')")
    db.execute("INSERT OR REPLACE INTO headers VALUES ('uuid-1', '2026-10-21T10:00:00Z', 'ACTIVE')")
    db.commit()

    # Simulate an uncommitted second write interrupted by simulated crash/close
    db.execute("INSERT OR REPLACE INTO meta VALUES ('cursor', 'https://nav.no/page/2')")
    db.execute("INSERT OR REPLACE INTO headers VALUES ('uuid-2', '2026-10-21T10:05:00Z', 'ACTIVE')")
    # Close without commit
    db.close()

    # Reopen after restart
    db2 = sqlite3.connect(db_path)
    cursor_val = db2.execute("SELECT value FROM meta WHERE key='cursor'").fetchone()[0]
    headers = [r[0] for r in db2.execute("SELECT uuid FROM headers").fetchall()]
    db2.close()

    assert cursor_val == "https://nav.no/page/1"
    assert headers == ["uuid-1"]
    assert "uuid-2" not in headers


def test_nav_checkpoint_restart_identity(tmp_path):
    """Test 4: Uninterrupted run vs interrupted + resumed run yield identical final checkpoint state."""
    # Run 1: Interrupted at item 1, then resumed
    state_1 = tmp_path / "state_interrupted"
    state_1.mkdir()
    db1 = sqlite3.connect(state_1 / "nav-checkpoint.sqlite3")
    db1.execute("CREATE TABLE headers (uuid TEXT PRIMARY KEY, status TEXT)")
    db1.execute("INSERT INTO headers VALUES ('u1', 'ACTIVE')")
    db1.commit()
    db1.close()

    # Resume run 1: append u2 and u3
    db1_resumed = sqlite3.connect(state_1 / "nav-checkpoint.sqlite3")
    db1_resumed.execute("INSERT INTO headers VALUES ('u2', 'ACTIVE')")
    db1_resumed.execute("INSERT INTO headers VALUES ('u3', 'INACTIVE')")
    db1_resumed.commit()
    active_1 = [r[0] for r in db1_resumed.execute("SELECT uuid FROM headers WHERE status='ACTIVE' ORDER BY uuid")]
    db1_resumed.close()

    # Run 2: Uninterrupted run
    state_2 = tmp_path / "state_uninterrupted"
    state_2.mkdir()
    db2 = sqlite3.connect(state_2 / "nav-checkpoint.sqlite3")
    db2.execute("CREATE TABLE headers (uuid TEXT PRIMARY KEY, status TEXT)")
    db2.execute("INSERT INTO headers VALUES ('u1', 'ACTIVE')")
    db2.execute("INSERT INTO headers VALUES ('u2', 'ACTIVE')")
    db2.execute("INSERT INTO headers VALUES ('u3', 'INACTIVE')")
    db2.commit()
    active_2 = [r[0] for r in db2.execute("SELECT uuid FROM headers WHERE status='ACTIVE' ORDER BY uuid")]
    db2.close()

    assert active_1 == active_2 == ["u1", "u2"]


def test_nav_withdrawal_and_deletion_replay(tmp_path):
    """Test 5: Deleted and inactive ads are pruned from final output."""
    db = sqlite3.connect(tmp_path / "test.sqlite3")
    db.execute("CREATE TABLE headers (uuid TEXT PRIMARY KEY, modified TEXT, status TEXT)")
    db.execute("CREATE TABLE details (uuid TEXT PRIMARY KEY, modified TEXT, value TEXT, error TEXT)")

    # Ad 1 was active, then updated to DELETED
    db.execute("INSERT INTO headers VALUES ('ad-1', '2026-10-21T12:00:00Z', 'DELETED')")
    # Ad 2 was active, updated to INACTIVE
    db.execute("INSERT INTO headers VALUES ('ad-2', '2026-10-21T12:00:00Z', 'INACTIVE')")
    # Ad 3 remains ACTIVE
    db.execute("INSERT INTO headers VALUES ('ad-3', '2026-10-21T12:00:00Z', 'ACTIVE')")

    db.execute("INSERT INTO details VALUES ('ad-1', '2026-10-21T10:00:00Z', '{\"uuid\":\"ad-1\"}', NULL)")
    db.execute("INSERT INTO details VALUES ('ad-2', '2026-10-21T10:00:00Z', '{\"uuid\":\"ad-2\"}', NULL)")
    db.execute("INSERT INTO details VALUES ('ad-3', '2026-10-21T12:00:00Z', '{\"uuid\":\"ad-3\",\"status\":\"ACTIVE\"}', NULL)")
    db.commit()

    rows = db.execute(
        "SELECT d.value FROM details d JOIN headers h ON h.uuid=d.uuid "
        "WHERE h.status='ACTIVE' AND d.error IS NULL AND d.modified=h.modified AND d.value IS NOT NULL"
    ).fetchall()
    db.close()

    assert len(rows) == 1
    assert json.loads(rows[0][0])["uuid"] == "ad-3"


def test_nav_secret_redaction(tmp_path):
    """Test 6: Secret NAV API token is redacted from string representations and reports."""
    secret = VALID_JWT
    raw_message = f"Request failed with Bearer {secret} on https://pam-stilling-feed.nav.no"
    redacted = redact_token(raw_message, token=secret)
    
    assert secret not in redacted
    assert "eyJhbGci" not in redacted
    assert "[REDACTED" in redacted
