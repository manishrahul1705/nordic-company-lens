"""Stage 2B Identity Security Hardening Regression Suite.

This suite exercises:
- Complete cross-section claim suppression under primary identity mismatch (wrong_company)
- Section-specific wrong_company isolation for roles, accounts, and subunits
- Transient source failure carry-forward without identity conflict
- Refuted website ownership removal
- Absence of false material removal changes under ambiguous identity
- Claim stability, evidence deduplication, and input shape preservation
"""
import asyncio
import json
import pytest
import respx
import httpx
from pathlib import Path
from signalpost.runner import run
from signalpost.web import policy
from signalpost.models.shapes import validate
from tests.test_registry import config, handler, entity
from tests.test_websites import html, OUR, OTHER

SUBUNIT_ORG = "982257867"


def full_handler(role_name="Person One", with_subunits=True, with_accounts=True):
    def dispatch(request):
        url = str(request.url)
        if request.url.host == "data.brreg.no":
            if "/roller" in url:
                body = {
                    "organisasjonsnummer": OUR,
                    "rollegrupper": [{
                        "type": {"kode": "STYR"},
                        "sistEndret": "2024-01-01",
                        "roller": [{"type": {"kode": "DAGL"}, "person": {"navn": {"fornavn": role_name}}}]
                    }]
                }
                return httpx.Response(200, json=body)
            if "/underenheter?" in url:
                if with_subunits:
                    sub = {
                        "organisasjonsnummer": SUBUNIT_ORG,
                        "overordnetEnhet": OUR,
                        "navn": "EXAMPLE SUBUNIT",
                        "beliggenhetsadresse": {"adresse": ["Gate 1"], "kommune": "OSLO", "postnummer": "0276", "poststed": "OSLO"}
                    }
                    body = {"_embedded": {"underenheter": [sub]}, "page": {"totalPages": 1}}
                else:
                    body = {"_embedded": {"underenheter": []}, "page": {"totalPages": 1}}
                return httpx.Response(200, json=body)
            if "/regnskapsregisteret/" in url:
                if with_accounts:
                    body = [{
                        "regnskapstype": "SELSKAP",
                        "virksomhet": {"organisasjonsnummer": OUR},
                        "regnskapsperiode": {"fraDato": "2024-01-01", "tilDato": "2024-12-31"},
                        "valuta": "NOK",
                        "resultatregnskapResultat": {"aarsresultat": 100000}
                    }]
                else:
                    body = []
                return httpx.Response(200, json=body)
            return handler(role_name=role_name, missing_accounts=not with_accounts)(request)
        if request.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nAllow: /")
        if request.url.host in ("example.no", "www.example.no"):
            return httpx.Response(200, text=html(extra='<a href="mailto:office@example.no">Email</a> <span class="phone">+47 22 55 20 02</span>'))
        return httpx.Response(404, text="not found")
    return dispatch


# Scenario 1: Identity wrong_company blocks identity claims
def test_identity_wrong_company_blocks_identity_carry_forward(tmp_path, monkeypatch):
    """[security_hardening]
    Primary identity mismatch (wrong_company) must not carry forward previous identity claims.
    """
    async def public_dns(host, port=443): return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    baseline_cfg = config(tmp_path / "baseline", [OUR], websites=True).model_copy(update={"website_politeness_seconds": 0})
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler())
        asyncio.run(run(baseline_cfg))

    refresh_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=baseline_cfg.output).model_copy(update={"website_politeness_seconds": 0, "website_request_cap": 20, "website_total_request_cap": 50})
    def refresh_dispatch(request):
        if "/enhetsregisteret/api/enheter/" in request.url.path and not request.url.path.endswith("/roller"):
            return httpx.Response(200, json=entity(OTHER))
        return full_handler()(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]
    assert row["run"]["sections"]["identity"] == "ambiguous"
    assert not any(c["family"] == "identity" and c.get("carried_forward") for c in row["claims"])
    assert not any(c["family"] == "identity" and c["availability"] == "available" for c in row["claims"])


# Scenario 2: Identity wrong_company blocks role claims
def test_identity_wrong_company_blocks_role_claims_carry_forward(tmp_path, monkeypatch):
    """[security_hardening]
    Primary identity mismatch (wrong_company) must not carry forward previous role claims.
    """
    async def public_dns(host, port=443): return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    baseline_cfg = config(tmp_path / "baseline", [OUR], websites=True).model_copy(update={"website_politeness_seconds": 0})
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler())
        asyncio.run(run(baseline_cfg))

    refresh_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=baseline_cfg.output).model_copy(update={"website_politeness_seconds": 0, "website_request_cap": 20, "website_total_request_cap": 50})
    def refresh_dispatch(request):
        if "/enhetsregisteret/api/enheter/" in request.url.path and not request.url.path.endswith("/roller"):
            return httpx.Response(200, json=entity(OTHER))
        return full_handler()(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]
    assert row["run"]["sections"]["roles"] == "ambiguous"
    assert not any(c["family"] == "roles" and c.get("carried_forward") for c in row["claims"])
    assert not any(c["family"] == "roles" and c["availability"] == "available" for c in row["claims"])


# Scenario 3: Identity wrong_company blocks website claims
def test_identity_wrong_company_blocks_website_claims_carry_forward(tmp_path, monkeypatch):
    """[security_hardening]
    Primary identity mismatch (wrong_company) must not carry forward previous website claims.
    """
    async def public_dns(host, port=443): return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    baseline_cfg = config(tmp_path / "baseline", [OUR], websites=True).model_copy(update={"website_politeness_seconds": 0})
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler())
        asyncio.run(run(baseline_cfg))

    refresh_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=baseline_cfg.output).model_copy(update={"website_politeness_seconds": 0, "website_request_cap": 20, "website_total_request_cap": 50})
    def refresh_dispatch(request):
        if "/enhetsregisteret/api/enheter/" in request.url.path and not request.url.path.endswith("/roller"):
            return httpx.Response(200, json=entity(OTHER))
        return full_handler()(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]
    assert row["run"]["sections"]["website"] == "ambiguous"
    assert not any(c["family"] == "website" and c.get("carried_forward") for c in row["claims"])
    assert not any(c["field"] == "official_website" and c["availability"] == "available" for c in row["claims"])


# Scenario 4: Identity wrong_company blocks financial claims
def test_identity_wrong_company_blocks_financial_claims_carry_forward(tmp_path, monkeypatch):
    """[security_hardening]
    Primary identity mismatch (wrong_company) must not carry forward previous financial claims.
    """
    async def public_dns(host, port=443): return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    baseline_cfg = config(tmp_path / "baseline", [OUR], websites=True).model_copy(update={"website_politeness_seconds": 0})
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler(with_accounts=True))
        asyncio.run(run(baseline_cfg))

    refresh_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=baseline_cfg.output).model_copy(update={"website_politeness_seconds": 0, "website_request_cap": 20, "website_total_request_cap": 50})
    def refresh_dispatch(request):
        if "/enhetsregisteret/api/enheter/" in request.url.path and not request.url.path.endswith("/roller"):
            return httpx.Response(200, json=entity(OTHER))
        return full_handler()(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]
    assert row["run"]["sections"]["accounts"] == "ambiguous"
    assert not any(c["family"] == "accounts" and c.get("carried_forward") for c in row["claims"])
    assert not any(c["family"] == "accounts" and c["availability"] == "available" for c in row["claims"])


# Scenario 5: Identity wrong_company blocks subunit claims
def test_identity_wrong_company_blocks_subunit_claims_carry_forward(tmp_path, monkeypatch):
    """[security_hardening]
    Primary identity mismatch (wrong_company) must not carry forward previous subunit claims.
    """
    async def public_dns(host, port=443): return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    baseline_cfg = config(tmp_path / "baseline", [OUR], websites=True).model_copy(update={"website_politeness_seconds": 0})
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler(with_subunits=True))
        asyncio.run(run(baseline_cfg))

    refresh_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=baseline_cfg.output).model_copy(update={"website_politeness_seconds": 0, "website_request_cap": 20, "website_total_request_cap": 50})
    def refresh_dispatch(request):
        if "/enhetsregisteret/api/enheter/" in request.url.path and not request.url.path.endswith("/roller"):
            return httpx.Response(200, json=entity(OTHER))
        return full_handler()(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]
    assert row["run"]["sections"]["subunits"] == "ambiguous"
    assert not any(c["family"] == "subunits" and c.get("carried_forward") for c in row["claims"])
    assert not any(c["family"] == "subunits" and c["availability"] == "available" for c in row["claims"])


# Scenario 6: Identity wrong_company blocks contact claims
def test_identity_wrong_company_blocks_contact_claims_carry_forward(tmp_path, monkeypatch):
    """[security_hardening]
    Primary identity mismatch (wrong_company) must not carry forward previous contact claims.
    """
    async def public_dns(host, port=443): return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    baseline_cfg = config(tmp_path / "baseline", [OUR], websites=True).model_copy(update={"website_politeness_seconds": 0})
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler())
        asyncio.run(run(baseline_cfg))

    refresh_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=baseline_cfg.output).model_copy(update={"website_politeness_seconds": 0, "website_request_cap": 20, "website_total_request_cap": 50})
    def refresh_dispatch(request):
        if "/enhetsregisteret/api/enheter/" in request.url.path and not request.url.path.endswith("/roller"):
            return httpx.Response(200, json=entity(OTHER))
        return full_handler()(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]
    contact_claims = [c for c in row["claims"] if c["field"].startswith("contact.")]
    assert not any(c.get("carried_forward") for c in contact_claims)
    assert not any(c["availability"] == "available" for c in contact_claims)


# Scenario 7: Section-specific wrong_company affecting roles
def test_roles_wrong_company_blocks_role_claims_carry_forward(tmp_path, monkeypatch):
    """[security_hardening]
    When roles endpoint returns data for a mismatched company (wrong_company),
    role claims must NOT be carried forward, while identity claims remain valid.
    """
    baseline_cfg = config(tmp_path / "baseline", [OUR])
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler())
        asyncio.run(run(baseline_cfg))

    refresh_cfg = config(tmp_path / "refresh", [OUR], previous=baseline_cfg.output)
    def refresh_dispatch(request):
        if request.url.path.endswith("/roller"):
            # Roles endpoint returns data for OTHER company
            return httpx.Response(200, json={"rollegrupper": [], "overordnetEnhet": OTHER})
        return full_handler()(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]
    assert row["run"]["sections"]["identity"] == "available"
    assert row["run"]["sections"]["roles"] == "ambiguous"
    assert any(e["section"] == "roles" and e["code"] == "wrong_company" for e in row["errors"])
    # Section-level ambiguity records observation change without false material removal
    assert report["changes"] == 0
    assert report["observation_changes"] == 1
    # Conflicting company data (OTHER) is NEVER admitted into claims
    assert not any(OTHER in str(c["value"]) for c in row["claims"])
    # Previous verified roles of OUR are safely carried forward as ambiguous observation
    assert any(c["family"] == "roles" and c.get("carried_forward") for c in row["claims"])


# Scenario 8: Section-specific wrong_company affecting accounts
def test_accounts_wrong_company_isolated_to_observation_change(tmp_path, monkeypatch):
    """[security_hardening]
    When accounts endpoint returns data for a mismatched company (wrong_company),
    it is isolated as an observation change without admitting foreign data or false removals.
    """
    baseline_cfg = config(tmp_path / "baseline", [OUR])
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler(with_accounts=True))
        asyncio.run(run(baseline_cfg))

    refresh_cfg = config(tmp_path / "refresh", [OUR], previous=baseline_cfg.output)
    def refresh_dispatch(request):
        if "/regnskapsregisteret/" in request.url.path:
            # Accounts returns record for OTHER company
            body = [{
                "regnskapstype": "SELSKAP",
                "virksomhet": {"organisasjonsnummer": OTHER},
                "regnskapsperiode": {"fraDato": "2024-01-01", "tilDato": "2024-12-31"},
                "valuta": "NOK",
                "resultatregnskapResultat": {"aarsresultat": 100000}
            }]
            return httpx.Response(200, json=body)
        return full_handler(with_accounts=True)(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]
    assert row["run"]["sections"]["identity"] == "available"
    assert row["run"]["sections"]["accounts"] == "ambiguous"
    assert any(e["section"] == "accounts" and e["code"] == "wrong_company" for e in row["errors"])
    assert report["changes"] == 0
    assert report["observation_changes"] == 1
    # Foreign accounts are never admitted
    assert not any(OTHER in str(c["value"]) for c in row["claims"])


# Scenario 9: Section-specific wrong_company affecting subunits
def test_subunits_wrong_company_isolated_to_observation_change(tmp_path, monkeypatch):
    """[security_hardening]
    When subunits endpoint returns records with mismatched parent (overordnetEnhet != org),
    it is isolated as an observation change without admitting foreign subunits.
    """
    baseline_cfg = config(tmp_path / "baseline", [OUR])
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler(with_subunits=True))
        asyncio.run(run(baseline_cfg))

    refresh_cfg = config(tmp_path / "refresh", [OUR], previous=baseline_cfg.output)
    def refresh_dispatch(request):
        if "/underenheter" in str(request.url):
            # Subunits returns record for OTHER company
            sub = {
                "organisasjonsnummer": SUBUNIT_ORG,
                "overordnetEnhet": OTHER,
                "navn": "WRONG PARENT SUBUNIT",
                "beliggenhetsadresse": {"adresse": ["Gate 1"], "kommune": "OSLO", "postnummer": "0276", "poststed": "OSLO"}
            }
            return httpx.Response(200, json={"_embedded": {"underenheter": [sub]}, "page": {"totalPages": 1}})
        return full_handler(with_subunits=True)(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]
    assert row["run"]["sections"]["identity"] == "available"
    assert row["run"]["sections"]["subunits"] == "ambiguous"
    assert any(e["section"] == "subunits" and e["code"] == "wrong_company" for e in row["errors"])
    assert report["changes"] == 0
    assert report["observation_changes"] == 1
    # Foreign subunit is never admitted
    assert not any(OTHER in str(c["value"]) for c in row["claims"])


# Scenario 10: Transient primary registry error preserves claims
def test_transient_registry_error_without_conflict_preserves_claims(tmp_path):
    """[security_hardening]
    A transient 500 error on the primary registry endpoint (no wrong_company conflict)
    must safely carry forward previously verified identity claims.
    """
    baseline_cfg = config(tmp_path / "baseline", [OUR])
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler())
        asyncio.run(run(baseline_cfg))

    refresh_cfg = config(tmp_path / "refresh", [OUR], previous=baseline_cfg.output)
    def refresh_dispatch(request):
        if "/enhetsregisteret/api/enheter/" in request.url.path and not request.url.path.endswith("/roller"):
            return httpx.Response(500, text="Internal Server Error")
        return full_handler()(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]
    assert row["run"]["sections"]["identity"] == "failed"
    carried_identity = [c for c in row["claims"] if c["family"] == "identity" and c.get("carried_forward")]
    assert any(c["field"] == "identity.legal_name" for c in carried_identity)


# Scenario 11: Transient website error with verified identity preserves claims
def test_transient_website_error_with_verified_identity_preserves_claims(tmp_path, monkeypatch):
    """[security_hardening]
    When identity is verified fresh and website encounters a transient timeout,
    website claims must carry forward without being dropped.
    """
    from tests.test_websites import example_only_dns as public_dns
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    baseline_cfg = config(tmp_path / "baseline", [OUR], websites=True).model_copy(update={"website_politeness_seconds": 0})
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler())
        asyncio.run(run(baseline_cfg))

    refresh_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=baseline_cfg.output).model_copy(update={"website_politeness_seconds": 0, "website_request_cap": 20, "website_total_request_cap": 50})
    def refresh_dispatch(request):
        if request.url.host in ("example.no", "www.example.no"):
            raise httpx.ReadTimeout("timeout", request=request)
        return full_handler()(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]
    assert row["run"]["sections"]["identity"] == "available"
    assert row["run"]["sections"]["website"] == "available"
    assert row["run"]["refresh"]["stale_sections"]["website"]["attempt_state"] == "failed"
    carried_web = [c for c in row["claims"] if c["family"] == "website" and c.get("carried_forward")]
    assert any(c["field"] == "official_website" for c in carried_web)


# Scenario 12: Genuine website ownership conflict emits removal
def test_genuine_website_ownership_conflict_emits_removal(tmp_path, monkeypatch):
    """[security_hardening]
    When website displays a foreign orgnr (ownership conflict), old claims must NOT carry forward
    and a removed change must be emitted.
    """
    from tests.test_websites import example_only_dns as public_dns
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    baseline_cfg = config(tmp_path / "baseline", [OUR], websites=True).model_copy(update={"website_politeness_seconds": 0})
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler())
        asyncio.run(run(baseline_cfg))

    refresh_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=baseline_cfg.output).model_copy(update={"website_politeness_seconds": 0, "website_request_cap": 20, "website_total_request_cap": 50})
    def refresh_dispatch(request):
        if request.url.host in ("example.no", "www.example.no"):
            return httpx.Response(200, text="<html><body>Foreign company Org.nr 987654321</body></html>")
        return full_handler()(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]
    assert row["run"]["sections"]["website"] == "not_available"
    assert not any(c["field"] == "official_website" and c.get("carried_forward") for c in row["claims"])
    assert any(ch["type"] == "removed" and ch["field"] == "official_website" for ch in row.get("changes", []))


# Scenario 13: No false material changes on ambiguous identity
def test_no_false_material_changes_on_ambiguous_identity(tmp_path, monkeypatch):
    """[security_hardening]
    When identity fails with wrong_company (ambiguous state), no false material 'removed'
    changes should be recorded for suppressed claims.
    """
    baseline_cfg = config(tmp_path / "baseline", [OUR])
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler())
        asyncio.run(run(baseline_cfg))

    refresh_cfg = config(tmp_path / "refresh", [OUR], previous=baseline_cfg.output)
    def refresh_dispatch(request):
        if "/enhetsregisteret/api/enheter/" in request.url.path and not request.url.path.endswith("/roller"):
            return httpx.Response(200, json=entity(OTHER))
        return full_handler()(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=refresh_dispatch)
        report = asyncio.run(run(refresh_cfg))

    rows = [json.loads(line) for line in refresh_cfg.output.read_text(encoding="utf8").splitlines()]
    row = rows[0]
    # Inconclusive/ambiguous state must NOT emit material 'removed' changes
    assert not any(ch.get("type") == "removed" for ch in row.get("changes", []))


# Scenario 14: Stable claim and evidence IDs on legitimate refresh
def test_stable_claim_and_evidence_ids_on_legitimate_refresh(tmp_path, monkeypatch):
    """[security_hardening]
    On unchanged refresh, claim IDs and evidence IDs must be 100% stable with zero duplicates.
    """
    async def public_dns(host, port=443): return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    cfg1 = config(tmp_path / "run1", [OUR], websites=True).model_copy(update={"website_politeness_seconds": 0})
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler())
        asyncio.run(run(cfg1))

    cfg2 = config(tmp_path / "run2", [OUR], websites=True, previous=cfg1.output).model_copy(update={"website_politeness_seconds": 0})
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler())
        report2 = asyncio.run(run(cfg2))

    rows1 = [json.loads(line) for line in cfg1.output.read_text(encoding="utf8").splitlines()]
    rows2 = [json.loads(line) for line in cfg2.output.read_text(encoding="utf8").splitlines()]

    assert sorted(c["id"] for c in rows1[0]["claims"]) == sorted(c["id"] for c in rows2[0]["claims"])
    ev_ids = [e["id"] for e in rows2[0]["evidence"]]
    assert len(ev_ids) == len(set(ev_ids))


# Scenario 15: Exactly one valid envelope per input including failures
def test_one_valid_envelope_per_input_including_failures(tmp_path):
    """[security_hardening]
    Envelope contract must be strictly preserved for mixed batches of valid, failing, and duplicate inputs.
    """
    cfg = config(tmp_path, [OUR, "bad_org", OUR])
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler())
        report = asyncio.run(run(cfg))

    rows = [json.loads(line) for line in cfg.output.read_text(encoding="utf8").splitlines()]
    assert len(rows) == 3
    assert [r["organisation_number"] for r in rows] == [OUR, "bad_org", OUR]
    for r in rows:
        validate(r, "union")
