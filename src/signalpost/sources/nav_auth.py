"""Decode NAV JWT claims for expiration checks without verifying signatures."""
import base64
import json


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
