"""
Regression tests for V6-06:
- Production NAV authentication lifecycle, proactive expiration detection, and force refresh.
- Checkpoint recovery integration.
"""
import os
import time
from unittest.mock import patch
import httpx
import pytest

from signalpost.sources.nav_auth import NavAuthManager

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
async def test_v6_06_expired_env_token_rejected_in_favor_of_public_endpoint():
    """
    V6-06: An expired NAV_API_TOKEN in environment must not be used.
    NavAuthManager must ignore it and fetch a fresh token from the public endpoint.
    """
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


@pytest.mark.anyio
async def test_v6_06_force_refresh_bypasses_env_token():
    """
    V6-06: force_refresh=True must force rotation from public endpoint even if env token is present.
    """
    async def mock_handler(request):
        if request.url.path == "/api/publicToken":
            return httpx.Response(200, text=f"Token:\n{ROTATED_JWT}")
        return httpx.Response(404)

    transport = httpx.MockTransport(mock_handler)
    async with httpx.AsyncClient(transport=transport) as client:
        mgr = NavAuthManager(http_client=client)
        with patch.dict(os.environ, {"NAV_API_TOKEN": VALID_JWT}):
            # Regular fetch uses valid env token
            t1 = await mgr.get_bearer_token(force_refresh=False)
            assert t1 == VALID_JWT

            # Forced refresh fetches rotated token from public endpoint
            t2 = await mgr.get_bearer_token(force_refresh=True)
            assert t2 == ROTATED_JWT
