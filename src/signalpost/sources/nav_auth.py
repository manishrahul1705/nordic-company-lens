"""NAV Arbeidsplassen feed authentication, public token lifecycle, and secret redaction.

Strict invariants:
- Tokens are NEVER persisted to disk, blob store, reports, or git.
- Tokens are strictly redacted from exception messages, logs, and query parameters.
- Proactively rotates tokens before expiration.
- Evaluator-safe: gracefully reports token_unavailable without hanging or crashing.
"""
import base64
import json
import logging
import os
import re
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable

import httpx

from ..budget import SourceFailure

logger = logging.getLogger("signalpost.sources.nav_auth")

BASE = "https://pam-stilling-feed.nav.no"
PUBLIC_TOKEN_URL = f"{BASE}/api/publicToken"

JWT_PATTERN = re.compile(r"\be[y]J[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b")


def token_from(value: Any) -> str | None:
    """Extract raw JWT string from plain text or response wrapper."""
    if not value:
        return None
    match = JWT_PATTERN.search(str(value))
    return match.group() if match else None


def redact_token(text: str, token: str | None = None) -> str:
    """Safely redact any JWT tokens or Authorization headers from string."""
    if not text:
        return ""
    result = str(text)
    if token and token in result:
        result = result.replace(token, "[REDACTED_NAV_TOKEN]")
    # Redact any other JWT pattern matching standard tokens
    result = JWT_PATTERN.sub("[REDACTED_JWT]", result)
    result = re.sub(r"(?i)bearer\s+[a-z0-9_.-]+", "Bearer [REDACTED]", result)
    return result


def parse_jwt_claims(jwt_str: str) -> dict:
    """Safely extract claims without verifying signature (for expiration tracking)."""
    parts = jwt_str.split(".")
    if len(parts) != 3:
        return {}
    payload_b64 = parts[1]
    padded = payload_b64 + "=" * ((4 - len(payload_b64) % 4) % 4)
    try:
        raw_bytes = base64.urlsafe_b64decode(padded.encode("ascii"))
        return json.loads(raw_bytes.decode("utf-8", errors="replace"))
    except Exception:
        return {}


@dataclass
class TokenState:
    token: str
    source: str  # 'env' or 'public_endpoint'
    expires_at: float | None = None  # Unix timestamp
    kid: str | None = None

    def is_expired(self, buffer_seconds: float = 60.0) -> bool:
        if self.expires_at is None:
            return False
        return time.time() + buffer_seconds >= self.expires_at


class NavAuthManager:
    """
    Manages NAV Bearer authentication lifecycle:
    1. Checks environment variable NAV_API_TOKEN.
    2. Falls back to official public experimental token endpoint.
    3. Proactively tracks expiration and handles renewal.
    4. Enforces strict redaction on all outbound representations.
    """

    def __init__(self, http_client: httpx.AsyncClient | None = None, token_url: str = PUBLIC_TOKEN_URL):
        self.client = http_client
        self.token_url = token_url
        self.cached_state: TokenState | None = None

    async def get_bearer_token(self, force_refresh: bool = False) -> str | None:
        """Obtain a valid bearer token, rotating if expired or forced."""
        # 1. Environment variable check (only if not forced and not expired)
        if not force_refresh:
            env_token_raw = os.environ.get("NAV_API_TOKEN")
            env_token = token_from(env_token_raw) if env_token_raw else None
            if env_token:
                claims = parse_jwt_claims(env_token)
                exp = float(claims["exp"]) if "exp" in claims and isinstance(claims["exp"], (int, float)) else None
                now_s = time.time()
                if exp is None or exp > now_s + 30.0:
                    return env_token
                logger.warning("NAV_API_TOKEN in environment is expired (exp=%s, now=%s); falling back to token endpoint", exp, now_s)

        # 2. Check cached public token
        if not force_refresh and self.cached_state and not self.cached_state.is_expired():
            return self.cached_state.token

        # 3. Fetch from public endpoint
        token_str = await self._fetch_public_token()
        if not token_str:
            return None

        claims = parse_jwt_claims(token_str)
        exp = float(claims["exp"]) if "exp" in claims and isinstance(claims["exp"], (int, float)) else None
        kid = str(claims.get("kid", "")) or None
        self.cached_state = TokenState(
            token=token_str,
            source="public_endpoint",
            expires_at=exp,
            kid=kid
        )
        return token_str

    async def _fetch_public_token(self) -> str | None:
        if self.client is None:
            async with httpx.AsyncClient(timeout=10.0) as local_client:
                return await self._execute_token_request(local_client)
        return await self._execute_token_request(self.client)

    async def _execute_token_request(self, client: httpx.AsyncClient) -> str | None:
        try:
            resp = await client.get(self.token_url, headers={"Accept": "text/plain", "User-Agent": "SignalpostAgent/1.0"})
            if resp.status_code == 200:
                return token_from(resp.text)
            return None
        except Exception as exc:
            logger.warning("Failed to obtain NAV public experimental token: %s", type(exc).__name__)
            return None

    def invalidate(self) -> None:
        """Discard current token upon 401/403 or signature failure."""
        self.cached_state = None
