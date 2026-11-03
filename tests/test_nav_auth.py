"""Adversarial and functional validation for NAV authentication lifecycle (F10)."""
from signalpost.sources.nav_auth import parse_jwt_claims


SAMPLE_JWT = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
    "eyJzdWIiOiJuYXYudGVhbS5hcmJlaWRzcGxhc3NlbkBuYXYubm8iLCJraWQiOiI5YTY2OTc2MS1hMmFhLTQ2YjQtOWZkNi0yYTQ5YmNjZjJmNjUiLCJpc3MiOiJuYXYtbm8iLCJhdWQiOiJmZWVkLWFwaS12MiIsImlhdCI6MTcwMDAwMDAwMCwiZXhwIjoyMDAwMDAwMDAwfQ."
    "dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk"
)


def test_jwt_claims_parsing():
    claims = parse_jwt_claims(SAMPLE_JWT)
    assert claims.get("sub") == "nav.team.arbeidsplassen@nav.no"
    assert claims.get("aud") == "feed-api-v2"
    assert claims.get("iss") == "nav-no"
    assert claims.get("exp") == 2000000000
