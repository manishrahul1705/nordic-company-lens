"""Comprehensive regression suite for Stage 2 evidence-refresh integrity and security.

Every test specifies whether it targets:
- state_classification: ensuring source errors map to 'failed' or 'blocked', not 'not_available'
- claim_carry_forward: retaining verified prior claims when current check is inconclusive
- genuine_removal: confirming true removals are detected and emitted
- security_isolation: ensuring foreign entities or wrong-company matches are never published
- idempotency_and_provenance: verifying claim ID stability, timestamps, and deduplication
"""
import asyncio
import json
import pytest
import respx
import httpx
from pathlib import Path
from signalpost.runner import run
from signalpost.web import policy, candidates
from signalpost.budget import SourceFailure
from signalpost.models.shapes import validate
from tests.test_registry import config, handler, entity
from tests.test_websites import html, OUR, OTHER, FILL

SUBUNIT_ORG = "982257867"


def test_refresh_oversized_response_preserves_claims_and_sets_failed(tmp_path, monkeypatch):
    """[state_classification & claim_carry_forward]
    Website response >2 MiB (body_cap) during refresh must set section state to 'failed'
    (not 'not_available'), retain prior claims with carried_forward=True, and emit 0 material removals.
    """
    async def public_dns(host, port=443):
        return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    # 1. Baseline: Verified website and contact
    baseline_cfg = config(tmp_path / "baseline", [OUR], websites=True).model_copy(
        update={"website_politeness_seconds": 0}
    )
    def baseline_dispatch(request):
        if request.url.host == "data.brreg.no":
            return handler()(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.host == "example.no":
            return httpx.Response(200, text=html(extra='<a href="mailto:office@example.no">Email</a>'))
        return httpx.Response(404, text="not found")

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=baseline_dispatch)
        asyncio.run(run(baseline_cfg))

    # 2. Refresh: candidate returns >2 MiB body without exhausting budget cap
    refresh_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=baseline_cfg.output).model_copy(
        update={"website_politeness_seconds": 0, "website_request_cap": 8, "website_total_request_cap": 50}
    )
    def refresh_dispatch(request):
        if request.url.host == "data.brreg.no":
            return handler()(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.host in ("example.no", "www.example.no"):
            return httpx.Response(200, text="x" * (2 * 1024 * 1024 + 100))
        return httpx.Response(404, text="not found")

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]

    assert row["run"]["sections"]["website"] == "failed"
    website_claims = [c for c in row["claims"] if c["family"] == "website" and c.get("carried_forward")]
    assert any(c["field"] == "official_website" for c in website_claims)
    assert any(c["field"].startswith("contact.email.") for c in website_claims)
    assert not any(ch["type"] == "removed" and ch["field"] == "official_website" for ch in row.get("changes", []))
    assert not any(ch["type"] == "removed" and ch["field"].startswith("contact.") for ch in row.get("changes", []))


def test_refresh_dns_nxdomain_preserves_previous_state_as_stale(tmp_path, monkeypatch):
    """[state_classification & claim_carry_forward]
    DNS NXDOMAIN during refresh must retain the previous state as stale,
    retaining prior claims with carried_forward=True, rather than producing false removals.
    """
    dns_fail = False
    async def mock_dns(host, port=443):
        if dns_fail:
            raise SourceFailure("no_such_domain")
        return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", mock_dns)

    baseline_cfg = config(tmp_path / "baseline", [OUR], websites=True).model_copy(
        update={"website_politeness_seconds": 0}
    )
    def baseline_dispatch(request):
        if request.url.host == "data.brreg.no":
            return handler()(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.host == "example.no":
            return httpx.Response(200, text=html(extra='<a href="mailto:office@example.no">Email</a>'))
        return httpx.Response(404, text="not found")

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=baseline_dispatch)
        asyncio.run(run(baseline_cfg))

    dns_fail = True
    refresh_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=baseline_cfg.output).model_copy(
        update={"website_politeness_seconds": 0}
    )
    def refresh_dispatch(request):
        if request.url.host == "data.brreg.no":
            return handler()(request)
        return httpx.Response(404, text="not found")

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]

    assert row["run"]["sections"]["website"] == "available"
    assert row["run"]["refresh"]["stale_sections"]["website"]["attempt_state"] == "failed"
    carried = [c for c in row["claims"] if c["family"] == "website" and c.get("carried_forward")]
    assert any(c["field"] == "official_website" for c in carried)
    assert not any(ch["type"] == "removed" for ch in row.get("changes", []))


def test_refresh_transient_dns_failure_preserves_claims(tmp_path, monkeypatch):
    """[state_classification & claim_carry_forward]
    Transient DNS timeout or error must retain the previous state and stale claims.
    """
    dns_fail = False
    async def mock_dns(host, port=443):
        if dns_fail:
            raise SourceFailure("dns_timeout")
        return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", mock_dns)

    baseline_cfg = config(tmp_path / "baseline", [OUR], websites=True).model_copy(
        update={"website_politeness_seconds": 0}
    )
    def baseline_dispatch(request):
        if request.url.host == "data.brreg.no":
            return handler()(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.host == "example.no":
            return httpx.Response(200, text=html(extra='<a href="mailto:office@example.no">Email</a>'))
        return httpx.Response(404, text="not found")

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=baseline_dispatch)
        asyncio.run(run(baseline_cfg))

    dns_fail = True
    refresh_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=baseline_cfg.output).model_copy(
        update={"website_politeness_seconds": 0}
    )
    def refresh_dispatch(request):
        if request.url.host == "data.brreg.no":
            return handler()(request)
        return httpx.Response(404, text="not found")

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]

    assert row["run"]["sections"]["website"] == "available"
    assert row["run"]["refresh"]["stale_sections"]["website"]["attempt_state"] == "failed"
    carried = [c for c in row["claims"] if c["family"] == "website" and c.get("carried_forward")]
    assert any(c["field"] == "official_website" for c in carried)
    assert not any(ch["type"] == "removed" for ch in row.get("changes", []))


def test_refresh_http_403_429_on_non_registry_candidate_is_blocked(tmp_path, monkeypatch):
    """[state_classification & security_isolation]
    HTTP 403 / 429 on a candidate discovered via previous nomination or subunit (not in parent registry)
    must set state to 'blocked' (not 'not_available'), carrying forward claims.
    """
    async def public_dns(host, port=443):
        return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    # Baseline: company has empty registry hjemmeside, but discovers example.no via brand candidate
    baseline_cfg = config(tmp_path / "baseline", [OUR], websites=True).model_copy(
        update={"website_politeness_seconds": 0}
    )
    def baseline_dispatch(request):
        if request.url.host == "data.brreg.no":
            data = entity(OUR)
            data["hjemmeside"] = None  # No registry website
            if "/enhetsregisteret/api/enheter/" + OUR in request.url.path:
                return httpx.Response(200, json=data)
            return handler()(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.host == "example.no":
            return httpx.Response(200, text=html(extra='<a href="mailto:office@example.no">Email</a>'))
        return httpx.Response(404, text="not found")

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=baseline_dispatch)
        asyncio.run(run(baseline_cfg))

    # Refresh: candidate was nominated from previous run; website returns HTTP 403
    refresh_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=baseline_cfg.output).model_copy(
        update={"website_politeness_seconds": 0}
    )
    def refresh_dispatch(request):
        if request.url.host == "data.brreg.no":
            data = entity(OUR)
            data["hjemmeside"] = None
            if "/enhetsregisteret/api/enheter/" + OUR in request.url.path:
                return httpx.Response(200, json=data)
            return handler()(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.host == "example.no":
            return httpx.Response(403, text="Forbidden")
        return httpx.Response(404, text="not found")

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]

    assert row["run"]["sections"]["website"] == "blocked"
    carried = [c for c in row["claims"] if c["family"] == "website" and c.get("carried_forward")]
    assert any(c["field"] == "official_website" for c in carried)
    assert not any(ch["type"] == "removed" for ch in row.get("changes", []))


def test_refresh_robots_exclusion_on_non_registry_candidate_is_blocked(tmp_path, monkeypatch):
    """[state_classification & security_isolation]
    Robots exclusion on a non-registry nominated website must set state to 'blocked'
    and carry forward claims, not fall through to 'not_available'.
    """
    async def public_dns(host, port=443):
        return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    baseline_cfg = config(tmp_path / "baseline", [OUR], websites=True).model_copy(
        update={"website_politeness_seconds": 0}
    )
    def baseline_dispatch(request):
        if request.url.host == "data.brreg.no":
            data = entity(OUR)
            data["hjemmeside"] = None
            if "/enhetsregisteret/api/enheter/" + OUR in request.url.path:
                return httpx.Response(200, json=data)
            return handler()(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.host == "example.no":
            return httpx.Response(200, text=html())
        return httpx.Response(404, text="not found")

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=baseline_dispatch)
        asyncio.run(run(baseline_cfg))

    refresh_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=baseline_cfg.output).model_copy(
        update={"website_politeness_seconds": 0}
    )
    def refresh_dispatch(request):
        if request.url.host == "data.brreg.no":
            data = entity(OUR)
            data["hjemmeside"] = None
            if "/enhetsregisteret/api/enheter/" + OUR in request.url.path:
                return httpx.Response(200, json=data)
            return handler()(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /")
        return httpx.Response(200, text=html())

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]

    assert row["run"]["sections"]["website"] == "blocked"
    carried = [c for c in row["claims"] if c["family"] == "website" and c.get("carried_forward")]
    assert any(c["field"] == "official_website" for c in carried)
    assert not any(ch["type"] == "removed" for ch in row.get("changes", []))


def test_refresh_subunit_website_inaccessible_carries_forward(tmp_path, monkeypatch):
    """[claim_carry_forward & historical flage.no pattern]
    Company whose website is registered under a subunit (origin: subunit_registry_website)
    must carry forward claims if the website becomes inaccessible on refresh.
    """
    async def public_dns(host, port=443):
        return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    def brreg_with_subunit(request):
        url = str(request.url)
        if "/underenheter?" in url:
            sub = {
                "organisasjonsnummer": SUBUNIT_ORG,
                "overordnetEnhet": OUR,
                "navn": "EXAMPLE AS AVDELING",
                "hjemmeside": "www.flage.no",
                "epostadresse": "flage@flage.no",
                "telefon": "22552002",
                "beliggenhetsadresse": {"adresse": ["Gate 1"], "kommune": "OSLO", "postnummer": "0276", "poststed": "OSLO"}
            }
            return httpx.Response(200, json={"_embedded": {"underenheter": [sub]}, "page": {"totalPages": 1}})
        data = entity(OUR)
        data["hjemmeside"] = None
        if "/enhetsregisteret/api/enheter/" + OUR in url and not url.endswith("/roller"):
            return httpx.Response(200, json=data)
        return handler()(request)

    baseline_cfg = config(tmp_path / "baseline", [OUR], websites=True).model_copy(
        update={"website_politeness_seconds": 0}
    )
    def baseline_dispatch(request):
        if request.url.host == "data.brreg.no":
            return brreg_with_subunit(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.host in ("www.flage.no", "flage.no"):
            return httpx.Response(200, text=html(extra=f'<a href="mailto:flage@flage.no">Office</a> <span class="phone">+47 22 55 20 02</span>'))
        return httpx.Response(404, text="not found")

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=baseline_dispatch)
        asyncio.run(run(baseline_cfg))

    # In refresh: flage.no connection times out
    refresh_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=baseline_cfg.output).model_copy(
        update={"website_politeness_seconds": 0, "website_request_cap": 20, "website_total_request_cap": 50}
    )
    def refresh_dispatch(request):
        if request.url.host == "data.brreg.no":
            return brreg_with_subunit(request)
        if request.url.host in ("www.flage.no", "flage.no"):
            raise httpx.ReadTimeout("timeout", request=request)
        return httpx.Response(404, text="not found")

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]

    assert row["run"]["sections"]["website"] == "available"
    assert row["run"]["refresh"]["stale_sections"]["website"]["attempt_state"] == "failed"
    carried = [c for c in row["claims"] if c["family"] == "website" and c.get("carried_forward")]
    assert any(c["field"] == "official_website" for c in carried)
    assert not any(ch["type"] == "removed" and ch["field"] == "official_website" for ch in row.get("changes", []))


def test_refresh_checked_low_candidate_does_not_mask_verified_site_timeout(tmp_path, monkeypatch):
    """[state_classification & claim_carry_forward]
    When a non-matching candidate returns HTTP 200 (LOW proof) and the true verified candidate
    times out, retain the prior verified state and record the failed attempt as stale.
    """
    async def public_dns(host, port=443):
        return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    baseline_cfg = config(tmp_path / "baseline", [OUR], websites=True).model_copy(
        update={"website_politeness_seconds": 0}
    )
    def baseline_dispatch(request):
        if request.url.host == "data.brreg.no":
            return handler()(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.host == "example.no":
            return httpx.Response(200, text=html(extra='<a href="mailto:office@example.no">Email</a>'))
        return httpx.Response(404, text="not found")

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=baseline_dispatch)
        asyncio.run(run(baseline_cfg))

    # In refresh: Candidate 1 (unrelated) returns 200 with LOW proof (no company signals).
    # Candidate 2 (verified example.no) times out.
    from signalpost.web import collector
    from signalpost.web.candidates import Candidate
    monkeypatch.setattr(collector, "generate", lambda ctx: [
        Candidate("https://unrelated.no/", "unrelated.no", "brand"),
        Candidate("https://example.no/", "example.no", "legal_name_slug"),
    ])
    refresh_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=baseline_cfg.output).model_copy(
        update={"website_politeness_seconds": 0, "website_request_cap": 20, "website_total_request_cap": 50}
    )
    def refresh_dispatch(request):
        if request.url.host == "data.brreg.no":
            data = entity(OUR)
            data["hjemmeside"] = None  # Registry has no declared website
            if "/enhetsregisteret/api/enheter/" + OUR in request.url.path:
                return httpx.Response(200, json=data)
            return handler()(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.host in ("example.no", "www.example.no"):
            raise httpx.ReadTimeout("timeout", request=request)
        if request.url.host in ("unrelated.no", "www.unrelated.no"):
            # Returns 200 with generic text, scoring LOW proof
            return httpx.Response(200, text="<html><body>Unrelated generic company</body></html>")
        return httpx.Response(404, text="not found")

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]

    assert row["run"]["sections"]["website"] == "available"
    assert row["run"]["refresh"]["stale_sections"]["website"]["attempt_state"] == "failed"
    carried = [c for c in row["claims"] if c["family"] == "website" and c.get("carried_forward")]
    assert any(c["field"] == "official_website" for c in carried)
    assert not any(ch["type"] == "removed" for ch in row.get("changes", []))


def test_refresh_request_budget_exhaustion_carries_forward(tmp_path, monkeypatch):
    """[claim_carry_forward & state_classification]
    When website work exhausts request budget, state is 'failed' and claims are carried forward.
    """
    async def public_dns(host, port=443):
        return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    baseline_cfg = config(tmp_path / "baseline", [OUR], websites=True).model_copy(
        update={"website_politeness_seconds": 0}
    )
    def baseline_dispatch(request):
        if request.url.host == "data.brreg.no":
            return handler()(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.host == "example.no":
            return httpx.Response(200, text=html())
        return httpx.Response(404, text="not found")

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=baseline_dispatch)
        asyncio.run(run(baseline_cfg))

    refresh_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=baseline_cfg.output).model_copy(
        update={"website_politeness_seconds": 0, "website_request_cap": 1}
    )
    def refresh_dispatch(request):
        if request.url.host == "data.brreg.no":
            return handler()(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        raise httpx.ReadTimeout("timeout", request=request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]

    assert row["run"]["sections"]["website"] == "failed"
    carried = [c for c in row["claims"] if c["family"] == "website" and c.get("carried_forward")]
    assert any(c["field"] == "official_website" for c in carried)


def test_refresh_genuine_confirmed_removal_emits_removal(tmp_path, monkeypatch):
    """[genuine_removal]
    When a website is confirmed removed (e.g. registry website removed, all discovery clean with no hits),
    the system must emit a material 'removed' change and NOT carry forward old claims.
    """
    from tests.test_websites import example_only_dns as public_dns
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    # 1. Baseline: verified website
    baseline_cfg = config(tmp_path / "baseline", [OUR], websites=True).model_copy(
        update={"website_politeness_seconds": 0}
    )
    def baseline_dispatch(request):
        if request.url.host == "data.brreg.no":
            return handler()(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.host == "example.no":
            return httpx.Response(200, text=html(extra='<a href="mailto:office@example.no">Email</a>'))
        return httpx.Response(404, text="not found")

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=baseline_dispatch)
        asyncio.run(run(baseline_cfg))

    # 2. Refresh: Registry removes hjemmeside, and previous domain clean 404 (not found)
    refresh_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=baseline_cfg.output).model_copy(
        update={"website_politeness_seconds": 0, "website_request_cap": 20, "website_total_request_cap": 50}
    )
    def refresh_dispatch(request):
        if request.url.host == "data.brreg.no":
            data = entity(OUR)
            data["hjemmeside"] = None  # Registry field removed
            if "/enhetsregisteret/api/enheter/" + OUR in request.url.path:
                return httpx.Response(200, json=data)
            return handler()(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        # Domain genuinely returns 404 with clean empty body
        return httpx.Response(404, text="<html><body>Not Found</body></html>")

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]

    # Because candidate was 404 and registry has no website, section is not_available
    assert row["run"]["sections"]["website"] == "not_available"
    # Genuine removal change must be emitted
    assert any(ch["type"] == "removed" and ch["field"] == "official_website" for ch in row.get("changes", []))


def test_refresh_foreign_orgnr_on_website_rejects_and_removes(tmp_path, monkeypatch):
    """[security_isolation & genuine_removal]
    If a previously verified website now displays a foreign organization number (ownership change),
    it must be rejected (level='REJECT'), section set to 'not_available', and old evidence removed.
    """
    from tests.test_websites import example_only_dns as public_dns
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    baseline_cfg = config(tmp_path / "baseline", [OUR], websites=True).model_copy(
        update={"website_politeness_seconds": 0}
    )
    def baseline_dispatch(request):
        if request.url.host == "data.brreg.no":
            return handler()(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.host == "example.no":
            return httpx.Response(200, text=html())
        return httpx.Response(404, text="not found")

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=baseline_dispatch)
        asyncio.run(run(baseline_cfg))

    refresh_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=baseline_cfg.output).model_copy(
        update={"website_politeness_seconds": 0}
    )
    def refresh_dispatch(request):
        if request.url.host == "data.brreg.no":
            return handler()(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        # Page now displays foreign org number OTHER
        return httpx.Response(200, text=html(footer=f"Org nr {OTHER}"))

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]

    assert row["run"]["sections"]["website"] == "not_available"
    assert any(ch["type"] == "removed" and ch["field"] == "official_website" for ch in row.get("changes", []))
    assert not any(c["field"] == "official_website" and c.get("carried_forward") for c in row["claims"])


def test_registry_wrong_company_never_carries_forward_identity_claims(tmp_path):
    """[security_isolation]
    When a registry query returns an organization number differing from the requested entity,
    incompatible historical identity claims must NOT be carried forward into current claims.
    """
    baseline_cfg = config(tmp_path / "baseline", [OUR])
    def baseline_dispatch(request):
        return handler()(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=baseline_dispatch)
        asyncio.run(run(baseline_cfg))

    # In refresh: Registry returns mismatched org number
    refresh_cfg = config(tmp_path / "refresh", [OUR], previous=baseline_cfg.output)
    def refresh_dispatch(request):
        if "/enhetsregisteret/api/enheter/" in request.url.path and not request.url.path.endswith("/roller"):
            body = entity(OTHER)  # Wrong company!
            return httpx.Response(200, json=body)
        return handler()(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]

    assert row["run"]["sections"]["identity"] == "ambiguous"
    # Identity claims must NOT be carried forward under the wrong company!
    assert not any(c["family"] == "identity" and c.get("carried_forward") for c in row["claims"])


def test_transient_registry_failure_preserves_identity_claims(tmp_path):
    """[claim_carry_forward & state_classification]
    When registry returns transient 500 or timeout (not wrong company),
    prior identity claims must be carried forward with carried_forward=True.
    """
    baseline_cfg = config(tmp_path / "baseline", [OUR])
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=handler())
        asyncio.run(run(baseline_cfg))

    refresh_cfg = config(tmp_path / "refresh", [OUR], previous=baseline_cfg.output)
    def refresh_dispatch(request):
        if "/enhetsregisteret/api/enheter/" in request.url.path and not request.url.path.endswith("/roller"):
            return httpx.Response(500, text="Internal Server Error")
        return handler()(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]

    assert row["run"]["sections"]["identity"] == "failed"
    carried = [c for c in row["claims"] if c["family"] == "identity" and c.get("carried_forward")]
    assert any(c["field"] == "identity.legal_name" for c in carried)


def test_idempotent_refresh_stable_ids_no_duplicate_evidence(tmp_path, monkeypatch):
    """[idempotency_and_provenance]
    Refreshing against identical sources must produce 0 changes, 0 observation changes,
    identical claim IDs, and no duplicate evidence IDs.
    """
    async def public_dns(host, port=443):
        return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    def dispatch(request):
        if request.url.host == "data.brreg.no":
            return handler()(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.host == "example.no":
            return httpx.Response(200, text=html(extra='<a href="mailto:office@example.no">Email</a>'))
        return httpx.Response(404, text="not found")

    cfg1 = config(tmp_path / "run1", [OUR], websites=True).model_copy(update={"website_politeness_seconds": 0})
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=dispatch)
        asyncio.run(run(cfg1))

    cfg2 = config(tmp_path / "run2", [OUR], websites=True, previous=cfg1.output).model_copy(
        update={"website_politeness_seconds": 0}
    )
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=dispatch)
        report2 = asyncio.run(run(cfg2))

    rows1 = [json.loads(line) for line in cfg1.output.read_text(encoding="utf8").splitlines()]
    rows2 = [json.loads(line) for line in cfg2.output.read_text(encoding="utf8").splitlines()]

    assert report2["changes"] == 0
    assert report2["observation_changes"] == 0
    assert len(rows2[0]["changes"]) == 0

    claim_ids1 = sorted(c["id"] for c in rows1[0]["claims"])
    claim_ids2 = sorted(c["id"] for c in rows2[0]["claims"])
    assert claim_ids1 == claim_ids2

    ev_ids2 = [e["id"] for e in rows2[0]["evidence"]]
    assert len(ev_ids2) == len(set(ev_ids2)), "No duplicate evidence IDs permitted"


def test_carried_forward_preserves_original_timestamps_and_provenance(tmp_path, monkeypatch):
    """[idempotency_and_provenance]
    Carried forward claims must preserve their original first_observed_at,
    last_observed_at, and evidence_ids.
    """
    async def public_dns(host, port=443):
        return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    cfg1 = config(tmp_path / "run1", [OUR], websites=True).model_copy(update={"website_politeness_seconds": 0})
    def dispatch1(request):
        if request.url.host == "data.brreg.no":
            return handler()(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.host == "example.no":
            return httpx.Response(200, text=html(extra='<a href="mailto:office@example.no">Email</a>'))
        return httpx.Response(404, text="not found")

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=dispatch1)
        asyncio.run(run(cfg1))

    row1 = json.loads(cfg1.output.read_text(encoding="utf8").splitlines()[0])
    orig_web = next(c for c in row1["claims"] if c["field"] == "official_website")

    # In run 2: site has temporary timeout
    cfg2 = config(tmp_path / "run2", [OUR], websites=True, previous=cfg1.output).model_copy(
        update={"website_politeness_seconds": 0}
    )
    def dispatch2(request):
        if request.url.host == "data.brreg.no":
            return handler()(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        raise httpx.ReadTimeout("timeout", request=request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=dispatch2)
        asyncio.run(run(cfg2))

    row2 = json.loads(cfg2.output.read_text(encoding="utf8").splitlines()[0])
    carried_web = next(c for c in row2["claims"] if c["field"] == "official_website")

    assert carried_web["carried_forward"] is True
    assert carried_web["first_observed_at"] == orig_web["first_observed_at"]
    assert carried_web["last_observed_at"] == orig_web["last_observed_at"]
    assert carried_web["evidence_ids"] == orig_web["evidence_ids"]
    assert carried_web["id"] == orig_web["id"]


def test_one_valid_envelope_per_input_including_duplicates(tmp_path):
    """[idempotency_and_provenance]
    Input membership must be strictly preserved, including order, duplicates, and contract shape.
    """
    cfg = config(tmp_path, [OUR, OTHER, OUR])
    def dispatch(request):
        return handler()(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=dispatch)
        report = asyncio.run(run(cfg))

    rows = [json.loads(line) for line in cfg.output.read_text(encoding="utf8").splitlines()]
    assert len(rows) == 3
    assert [r["organisation_number"] for r in rows] == [OUR, OTHER, OUR]
    for r in rows:
        validate(r, "union")
