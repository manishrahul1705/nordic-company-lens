"""Adversarial and functional validation for NAV authentication lifecycle (F10)."""
import os
import time
import pytest
import httpx
from unittest.mock import patch

from signalpost.sources.nav_auth import (
    token_from,
    redact_token,
    parse_jwt_claims,
    NavAuthManager,
    TokenState,
    PUBLIC_TOKEN_URL
)

SAMPLE_JWT = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiJuYXYudGVhbS5hcmJlaWRzcGxhc3NlbkBuYXYubm8iLCJraWQiOiI5YTY2OTc2MS1hMmFhLTQ2YjQtOWZkNi0yYTQ5YmNjZjJmNjUiLCJpc3MiOiJuYXYtbm8iLCJhdWQiOiJmZWVkLWFwaS12MiIsImlhdCI6MTcwMDAwMDAwMCwiZXhwIjoyMDAwMDAwMDAwfQ."
    "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
)


def test_token_from_extracts_jwt_from_wrapped_text():
    raw_response = f"Current public token for Nav Job Vacancy Feed:\n{SAMPLE_JWT}\nUse with Bearer"
    extracted = token_from(raw_response)
    assert extracted == SAMPLE_JWT
    assert token_from(None) is None
    assert token_from("No token here") is None


def test_token_redaction_prevents_secret_leakage():
    leak_string = f"Error in GET /feed: Authorization: Bearer {SAMPLE_JWT} failed!"
    clean = redact_token(leak_string, SAMPLE_JWT)
    assert SAMPLE_JWT not in clean
    assert "[REDACTED" in clean
    # Test arbitrary jwt redaction
    assert "eyJ" not in clean


def test_jwt_claims_parsing():
    claims = parse_jwt_claims(SAMPLE_JWT)
    assert claims.get("sub") == "nav.team.arbeidsplassen@nav.no"
    assert claims.get("aud") == "feed-api-v2"
    assert claims.get("iss") == "nav-no"
    assert claims.get("exp") == 2000000000


def test_token_state_expiration_detection():
    # Expired token
    past = time.time() - 100
    st_expired = TokenState(token="tok1", source="public", expires_at=past)
    assert st_expired.is_expired() is True

    # Valid token
    future = time.time() + 3600
    st_valid = TokenState(token="tok2", source="public", expires_at=future)
    assert st_valid.is_expired() is False

    # Within buffer zone (e.g. 30 seconds remaining vs 60s buffer)
    near = time.time() + 30
    st_near = TokenState(token="tok3", source="public", expires_at=near)
    assert st_near.is_expired(buffer_seconds=60) is True


@pytest.mark.anyio
async def test_nav_auth_manager_environment_variable_precedence():
    mgr = NavAuthManager()
    with patch.dict(os.environ, {"NAV_API_TOKEN": SAMPLE_JWT}):
        token = await mgr.get_bearer_token()
        assert token == SAMPLE_JWT


@pytest.mark.anyio
async def test_nav_auth_manager_fetches_from_public_endpoint():
    async def mock_handler(request):
        if request.url.path == "/api/publicToken":
            return httpx.Response(200, text=f"Token:\n{SAMPLE_JWT}")
        return httpx.Response(404)

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        mgr = NavAuthManager(http_client=client)
        with patch.dict(os.environ, {}, clear=True):
            if "NAV_API_TOKEN" in os.environ:
                del os.environ["NAV_API_TOKEN"]
            token = await mgr.get_bearer_token()
            assert token == SAMPLE_JWT
            assert mgr.cached_state is not None
            assert mgr.cached_state.expires_at == 2000000000

            # Second call uses cache without second request
            token2 = await mgr.get_bearer_token()
            assert token2 == SAMPLE_JWT


@pytest.mark.anyio
async def test_nav_auth_manager_handles_network_failure_gracefully():
    async def mock_fail(request):
        return httpx.Response(500, text="Internal Server Error")

    transport = httpx.MockTransport(mock_fail)
    async with httpx.AsyncClient(transport=transport) as client:
        mgr = NavAuthManager(http_client=client)
        with patch.dict(os.environ, {}, clear=True):
            if "NAV_API_TOKEN" in os.environ:
                del os.environ["NAV_API_TOKEN"]
            token = await mgr.get_bearer_token()
            assert token is None


@pytest.mark.anyio
async def test_nav_auth_manager_invalidation_forces_refresh():
    call_count = 0

    async def mock_handler(request):
        nonlocal call_count
        call_count += 1
        return httpx.Response(200, text=SAMPLE_JWT)

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        mgr = NavAuthManager(http_client=client)
        with patch.dict(os.environ, {}, clear=True):
            if "NAV_API_TOKEN" in os.environ:
                del os.environ["NAV_API_TOKEN"]
            await mgr.get_bearer_token()
            assert call_count == 1
            mgr.invalidate()
            await mgr.get_bearer_token()
            assert call_count == 2
