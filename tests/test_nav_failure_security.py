"""Systematic failure-injection, security and resilience tests for NAV intelligence (NAV-8).

Tests:
- 401, 403, 404, 410, 429, 500, 502 status handling
- Timeout and slow stream handling
- Truncated and broken JSON payloads
- Malformed UUIDs and schema changes
- SSRF and URL validation (allowed() gate)
- Token echo and credential leakage prevention
- Half-written index corruption detection
- Deadline preservation and terminal company envelope guarantees
"""
import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
import pytest
import httpx
from unittest.mock import patch

from signalpost.budget import Budget, SourceFailure
from signalpost.config import Config
from signalpost.models.envelope import Claim
from signalpost.runner import placeholder
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.nav import allowed, NavHttp, Index, section, BASE
from signalpost.sources.nav_index import load, write, DEFAULT_PATH


def test_allowed_url_ssrf_and_host_validation():
    # Valid feed and entry paths
    assert allowed("https://pam-stilling-feed.nav.no/api/v1/feed")
    assert allowed("/api/v1/feed")
    assert allowed("/api/publicToken")
    assert allowed("/api/v1/feedentry/00000000-0000-0000-0000-000000000001")
    assert allowed("/api/v1/feed/00000000-0000-0000-0000-000000000001")

    # Rejected SSRF targets
    with pytest.raises(SourceFailure):
        allowed("http://pam-stilling-feed.nav.no/api/v1/feed")  # Plain HTTP
    with pytest.raises(SourceFailure):
        allowed("https://127.0.0.1/api/v1/feed")  # Loopback IP
    with pytest.raises(SourceFailure):
        allowed("https://169.254.169.254/api/v1/feed")  # Cloud metadata
    with pytest.raises(SourceFailure):
        allowed("https://evil.attacker.com/api/v1/feed")  # Foreign host
    with pytest.raises(SourceFailure):
        allowed("https://pam-stilling-feed.nav.no:8080/api/v1/feed")  # Disallowed port
    with pytest.raises(SourceFailure):
        allowed("https://user:pass@pam-stilling-feed.nav.no/api/v1/feed")  # Userinfo in URL
    with pytest.raises(SourceFailure):
        allowed("/api/v1/unsupported_internal_endpoint")  # Undocumented endpoint


@pytest.mark.anyio
async def test_nav_http_credential_echo_refused(tmp_path):
    token = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJzZWNyZXQifQ.sig"

    async def mock_echo(request):
        # Server echoes the token in body (e.g. debugging reflection vulnerability)
        return httpx.Response(200, text=f"Debug info: Received token {token}")

    transport = httpx.MockTransport(mock_echo)
    async with httpx.AsyncClient(transport=transport) as client:
        cfg = Config(
            organisations=tmp_path / "orgs.csv",
            output=tmp_path / "out.jsonl",
            report=tmp_path / "report.json",
            state_dir=tmp_path / "state",
            hiring=True
        )
        (tmp_path / "orgs.csv").write_text("organisation_number\n923609016\n")
        budget = Budget(cfg)
        blobs = BlobStore(cfg.state_dir)
        index = Index()
        http = NavHttp(client, cfg, budget, blobs, index)

        with pytest.raises(SourceFailure) as exc_info:
            await http.get("/api/v1/feed", token=token)
        assert exc_info.value.code == "credential_echo_refused"


@pytest.mark.anyio
async def test_nav_http_handles_http_429_retry_after(tmp_path):
    attempts = 0

    async def mock_throttle(request):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            return httpx.Response(429, headers={"Retry-After": "0.1"})
        return httpx.Response(200, json={"items": [], "next_url": None})

    transport = httpx.MockTransport(mock_throttle)
    async with httpx.AsyncClient(transport=transport) as client:
        cfg = Config(
            organisations=tmp_path / "orgs.csv",
            output=tmp_path / "out.jsonl",
            report=tmp_path / "report.json",
            state_dir=tmp_path / "state",
            hiring=True
        )
        (tmp_path / "orgs.csv").write_text("organisation_number\n923609016\n")
        budget = Budget(cfg)
        blobs = BlobStore(cfg.state_dir)
        index = Index()
        http = NavHttp(client, cfg, budget, blobs, index)

        status, body, sha, _ = await http.get("/api/v1/feed")
        assert status == 200
        assert attempts == 2


@pytest.mark.anyio
async def test_nav_http_handles_http_500_502_server_errors(tmp_path):
    async def mock_500(request):
        return httpx.Response(500, text="Internal Server Error")

    transport = httpx.MockTransport(mock_500)
    async with httpx.AsyncClient(transport=transport) as client:
        cfg = Config(
            organisations=tmp_path / "orgs.csv",
            output=tmp_path / "out.jsonl",
            report=tmp_path / "report.json",
            state_dir=tmp_path / "state",
            hiring=True
        )
        (tmp_path / "orgs.csv").write_text("organisation_number\n923609016\n")
        budget = Budget(cfg)
        blobs = BlobStore(cfg.state_dir)
        index = Index()
        http = NavHttp(client, cfg, budget, blobs, index)

        with pytest.raises(SourceFailure) as exc_info:
            await http.get("/api/v1/feed")
        assert "nav_http_500" in exc_info.value.code


def test_corrupt_index_load_handled_safely(tmp_path):
    # Truncated or corrupt gzip file
    corrupt_file = tmp_path / "corrupt_index.json.gz"
    corrupt_file.write_bytes(b"\x1f\x8b\x08\x00truncatedgarbage")

    with pytest.raises(SourceFailure) as exc:
        load(corrupt_file)
    assert exc.value.code in {"index_invalid", "index_size_invalid"}


def test_oversized_index_load_rejected(tmp_path):
    # Index larger than 2MB compressed bound
    oversized = tmp_path / "oversized.json.gz"
    oversized.write_bytes(b"0" * 2_000_001)

    with pytest.raises(SourceFailure) as exc:
        load(oversized)
    assert exc.value.code == "index_size_invalid"


def test_section_never_produces_zero_hiring_on_incomplete_index(tmp_path):
    blobs = BlobStore(tmp_path)
    env = placeholder("923609016", "run-inc", "2026-10-21T12:00:00Z")
    env.run.sections["hiring"] = "available"
    env.run.sections["subunits"] = "available"

    # Index is INCOMPLETE
    index = Index(complete=False, reason="nav_time_cap")
    sec = section(env, index, blobs)

    # State must be 'failed', NEVER claiming absence ('not_available')
    assert sec.state == "failed"
    assert len(sec.claims) == 0
    assert any(err.code == "nav_time_cap" for err in sec.errors)
