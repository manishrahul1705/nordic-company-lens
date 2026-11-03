"""Adversarial regression suite for Stage 3C-R3: Website Ownership, Contradiction, and Input Safety."""
import asyncio
import json
import httpx
import pytest

from signalpost.identity.orgnr import valid, normalize, checksum
from signalpost.web import collector
from signalpost.web.candidates import Candidate
from tests.test_websites import execute_web, html, FILL, OUR, OTHER


# 1. Same-domain foreign organization number: discredited, must NOT be carried forward
def test_same_domain_foreign_orgnr_not_carried_forward(tmp_path, monkeypatch):
    # Run 1: Verified website
    _, first, _, cfg1 = execute_web(tmp_path / "run1", monkeypatch, body=html(f"Org nr {OUR}"))
    assert any(c["field"] == "official_website" and c["availability"] == "available" for c in first["claims"])

    # Run 2: Same domain now displays foreign orgnr, followed by budget exhaustion
    def foreign_response(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        # Same domain displays foreign orgnr
        return httpx.Response(200, text=html(f"Org nr {OTHER}"))

    _, second, _, _ = execute_web(
        tmp_path / "run2", monkeypatch, response=foreign_response,
        previous=cfg1.output, website_request_cap=2
    )

    # Must NOT carry forward the discredited website
    assert not any(c["field"] == "official_website" for c in second["claims"])
    assert any(
        oc["section"] == "website" and oc["previous_state"] == "available"
        for oc in second["run"]["refresh"]["observation_changes"]
    )


# 2. Unrelated-domain foreign organization number does not destroy legitimate history
def test_unrelated_domain_foreign_orgnr_does_not_discredit_history(tmp_path, monkeypatch):
    # Run 1: Verified on example.no
    _, first, _, cfg1 = execute_web(tmp_path / "run1", monkeypatch, body=html(f"Org nr {OUR}"))

    # Run 2: Nominate an unrelated candidate that has foreign orgnr, while example.no has a transient 503
    def multi_response(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.host == "unrelated.no":
            return httpx.Response(200, text=html(f"Org nr {OTHER}"))
        if request.url.host == "example.no":
            return httpx.Response(503, text="Service Unavailable")
        return httpx.Response(404)

    # Inject an extra unrelated candidate
    orig_generate = collector.generate
    monkeypatch.setattr(collector, 'generate', lambda ctx: [
        Candidate('https://unrelated.no', 'unrelated.no', 'discovery')
    ] + orig_generate(ctx))

    _, second, _, _ = execute_web(
        tmp_path / "run2", monkeypatch, response=multi_response,
        previous=cfg1.output, website_request_cap=4
    )

    # The unrelated candidate's failure must NOT destroy example.no's historical claim!
    web_claim = next((c for c in second["claims"] if c["field"] == "official_website"), None)
    assert web_claim is not None
    assert web_claim["carried_forward"] is True


# 3. Multiple candidates: foreign candidate rejected, valid candidate verified
def test_multiple_candidates_foreign_isolation(tmp_path, monkeypatch):
    def dispatch(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.host == "foreign-candidate.no":
            return httpx.Response(200, text=html(f"Org nr {OTHER}"))
        if request.url.host == "example.no":
            return httpx.Response(200, text=html(f"Org nr {OUR}"))
        return httpx.Response(404)

    orig_generate = collector.generate
    monkeypatch.setattr(collector, 'generate', lambda ctx: [
        Candidate('https://foreign-candidate.no', 'foreign-candidate.no', 'discovery')
    ] + orig_generate(ctx))

    _, row, _, _ = execute_web(tmp_path, monkeypatch, response=dispatch, website_total_request_cap=15, website_request_cap=6)
    web_claim = next((c for c in row["claims"] if c["field"] == "official_website"), None)
    assert web_claim is not None
    assert web_claim["value"]["final_url"].startswith("https://example.no")
    assert not web_claim["carried_forward"]


# 4. Budget exhausted after a contradiction prevents carry-forward
def test_budget_exhausted_after_contradiction_prevents_carry(tmp_path, monkeypatch):
    # Run 1: Verified
    _, first, _, cfg1 = execute_web(tmp_path / "run1", monkeypatch, body=html(f"Org nr {OUR}"))

    # Run 2: Previous domain has foreign orgnr, subsequent discovery hits request cap
    def exhausted_response(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        return httpx.Response(200, text=html(f"Org nr {OTHER}"))

    _, second, _, _ = execute_web(
        tmp_path / "run2", monkeypatch, response=exhausted_response,
        previous=cfg1.output, website_request_cap=2
    )

    assert not any(c["field"] == "official_website" for c in second["claims"])


# 5. Website redirect to foreign company discredits old website
def test_website_redirect_to_foreign_company(tmp_path, monkeypatch):
    # Run 1: Verified
    _, first, _, cfg1 = execute_web(tmp_path / "run1", monkeypatch, body=html(f"Org nr {OUR}"))

    # Run 2: Redirects on-domain or within allowed domains to foreign proof page
    def redirect_response(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.path == "/":
            return httpx.Response(302, headers={"Location": "https://example.no/foreign"})
        if request.url.path == "/foreign":
            return httpx.Response(200, text=html(f"Org nr {OTHER}"))
        return httpx.Response(404)

    _, second, _, _ = execute_web(
        tmp_path / "run2", monkeypatch, response=redirect_response,
        previous=cfg1.output
    )

    assert not any(c["field"] == "official_website" for c in second["claims"])


# 6. Valid historical domain with temporarily inaccessible pages is carried forward
def test_valid_historical_domain_with_temporary_inaccessible_pages(tmp_path, monkeypatch):
    # Run 1: Verified
    _, first, _, cfg1 = execute_web(tmp_path / "run1", monkeypatch, body=html(f"Org nr {OUR}"))

    # Run 2: 500 error on example.no
    def transient_error(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        return httpx.Response(500, text="Internal Server Error")

    _, second, _, _ = execute_web(
        tmp_path / "run2", monkeypatch, response=transient_error,
        previous=cfg1.output
    )

    # Must be retained via carry-forward
    claim = next((c for c in second["claims"] if c["field"] == "official_website"), None)
    assert claim is not None
    assert claim["carried_forward"] is True


# 7. Corporate group website: listing sibling org numbers alongside holding org is not falsely refuted
def test_corporate_group_website_not_falsely_refuted(tmp_path, monkeypatch):
    group_html = html(footer=f"Org.nr {OUR}", extra=f"<div>Part of Example Group. Sibling org: {OTHER}. Holding org: {OUR}.</div>")
    _, row, _, _ = execute_web(tmp_path, monkeypatch, body=group_html)
    claim = next((c for c in row["claims"] if c["field"] == "official_website"), None)
    assert claim is not None
    assert claim["value"]["identity_level"] == "VERIFIED"
    assert claim["value"]["relationship_note"] == "group_site"


# 8. Legitimate domain transfer: new owner orgnr discredits old owner
def test_legitimate_domain_transfer_discredits_old_owner(tmp_path, monkeypatch):
    # Run 1: Company A owns example.no
    _, first, _, cfg1 = execute_web(tmp_path / "run1", monkeypatch, body=html(f"Org nr {OUR}"))

    # Run 2: Domain transfer, new company B's orgnr in footer
    def sold_response(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        return httpx.Response(200, text=html(f"Org nr {OTHER}", title="New Company AS"))

    _, second, _, _ = execute_web(tmp_path / "run2", monkeypatch, response=sold_response, previous=cfg1.output)
    assert not any(c["field"] == "official_website" for c in second["claims"])


# 9. Ownership recovery on later refresh: correctly re-publishes as available
def test_ownership_recovery_on_later_refresh(tmp_path, monkeypatch):
    # Run 1: Verified
    _, first, _, cfg1 = execute_web(tmp_path / "run1", monkeypatch, body=html(f"Org nr {OUR}"))
    assert any(c["field"] == "official_website" and not c["carried_forward"] for c in first["claims"])

    # Run 2: Discredited by foreign orgnr
    def sold_response(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        return httpx.Response(200, text=html(f"Org nr {OTHER}"))

    _, second, _, cfg2 = execute_web(tmp_path / "run2", monkeypatch, response=sold_response, previous=cfg1.output)
    assert not any(c["field"] == "official_website" for c in second["claims"])

    # Run 3: Ownership regained, our orgnr back on page
    def recovered_response(request):
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        return httpx.Response(200, text=html(f"Org nr {OUR}"))

    _, third, _, _ = execute_web(tmp_path / "run3", monkeypatch, response=recovered_response, previous=cfg2.output)
    new_claim = next((c for c in third["claims"] if c["field"] == "official_website"), None)
    assert new_claim is not None
    assert new_claim["availability"] == "available"
    assert not new_claim["carried_forward"]
    assert any(
        oc["section"] == "website" and oc["current_state"] == "available"
        for oc in third["run"]["refresh"]["observation_changes"]
    )


# 10. Investigation F-04: Norwegian organization number namespace vs checksum validity
def test_norwegian_orgnr_checksum_validation():
    assert checksum("000000000") is True
    assert valid("000000000") is True
    assert valid("923609016") is True
    assert checksum("812345672") is True
    assert valid("812345672") is True
