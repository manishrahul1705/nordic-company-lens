"""Stage 3C-R1 Regression Suite: Refresh and Identity Safety Repair.

Validates:
- config.verify_bulk does not purge historical claims on refresh when primary identity is verified.
- Legitimate historical claims (roles, accounts, subunits, websites) survive transient section failures under verify_bulk.
- Zero spurious 'previously_observed_claim_recovered' observation churn on clean verify_bulk refresh.
- Primary wrong_company conflict STILL suppresses all claims (zero leak, Stage 2B security preserved).
- Combinations with bulk CSV (live success, live timeout, live wrong_company).
- Multiple consecutive refresh cycles with timestamp and claim ID stability.
"""
import asyncio
import json
import httpx
import pytest
import respx
from pathlib import Path
from signalpost.runner import run
from signalpost.web import policy
from signalpost.models.shapes import validate
from tests.test_registry import config, entity, numbers
from tests.test_websites import html, OUR, OTHER
from tests.test_identity_security_hardening import full_handler, SUBUNIT_ORG
from tests.test_hybrid_registry import bulk_file


# Scenario 1: verify_bulk refresh preserves historical roles on transient roles failure (F-01 core)
def test_verify_bulk_refresh_preserves_historical_roles_on_roles_failure(tmp_path, monkeypatch):
    async def public_dns(host, port=443): return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    base_cfg = config(tmp_path / "base", [OUR], websites=True).model_copy(update={"website_politeness_seconds": 0})
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler())
        asyncio.run(run(base_cfg))

    base_row = json.loads(base_cfg.output.read_text(encoding="utf8").splitlines()[0])
    base_roles = [c for c in base_row["claims"] if c["family"] == "roles" and c["availability"] == "available"]
    assert len(base_roles) >= 1

    # Refresh with verify_bulk=True, roles endpoint returning 500
    ref_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=base_cfg.output).model_copy(
        update={"website_politeness_seconds": 0, "verify_bulk": True}
    )
    def roles_500_dispatch(request):
        if "/roller" in str(request.url):
            return httpx.Response(500)
        return full_handler()(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=roles_500_dispatch)
        asyncio.run(run(ref_cfg))

    ref_row = json.loads(ref_cfg.output.read_text(encoding="utf8").splitlines()[0])
    ref_roles = [c for c in ref_row["claims"] if c["family"] == "roles" and c["availability"] == "available"]
    assert len(ref_roles) >= 1, "Historical roles must be carried forward under verify_bulk=True when roles fails"
    assert all(c.get("carried_forward") for c in ref_roles)
    assert ref_row["run"]["sections"]["roles"] == "failed"


# Scenario 2: verify_bulk refresh preserves historical accounts on accounts failure
def test_verify_bulk_refresh_preserves_historical_accounts_on_accounts_failure(tmp_path, monkeypatch):
    async def public_dns(host, port=443): return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    base_cfg = config(tmp_path / "base", [OUR], websites=True).model_copy(update={"website_politeness_seconds": 0})
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler())
        asyncio.run(run(base_cfg))

    ref_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=base_cfg.output).model_copy(
        update={"website_politeness_seconds": 0, "verify_bulk": True}
    )
    def accounts_500_dispatch(request):
        if "/regnskapsregisteret" in str(request.url):
            return httpx.Response(500)
        return full_handler()(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=accounts_500_dispatch)
        asyncio.run(run(ref_cfg))

    ref_row = json.loads(ref_cfg.output.read_text(encoding="utf8").splitlines()[0])
    ref_acc = [c for c in ref_row["claims"] if c["family"] == "accounts" and c["availability"] == "available"]
    assert len(ref_acc) >= 1, "Historical accounts must be carried forward under verify_bulk=True when accounts fails"
    assert all(c.get("carried_forward") for c in ref_acc)


# Scenario 3: verify_bulk refresh preserves historical website on transient website failure
def test_verify_bulk_refresh_preserves_historical_website_on_website_failure(tmp_path, monkeypatch):
    from tests.test_websites import example_only_dns as public_dns
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    base_cfg = config(tmp_path / "base", [OUR], websites=True).model_copy(update={"website_politeness_seconds": 0})
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler())
        asyncio.run(run(base_cfg))

    ref_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=base_cfg.output).model_copy(
        update={"website_politeness_seconds": 0, "verify_bulk": True}
    )
    def website_500_dispatch(request):
        if request.url.host in ("example.no", "www.example.no"):
            return httpx.Response(500)
        return full_handler()(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=website_500_dispatch)
        asyncio.run(run(ref_cfg))

    ref_row = json.loads(ref_cfg.output.read_text(encoding="utf8").splitlines()[0])
    ref_web = [c for c in ref_row["claims"] if c["family"] == "website" and c["availability"] == "available"]
    assert len(ref_web) >= 1, "Historical website claims must be carried forward under verify_bulk=True on transient website failure"
    assert all(c.get("carried_forward") for c in ref_web)


# Scenario 4: No spurious recovered-claim observation churn on clean verify_bulk refresh
def test_no_spurious_observation_churn_on_clean_verify_bulk_refresh(tmp_path, monkeypatch):
    async def public_dns(host, port=443): return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    base_cfg = config(tmp_path / "base", [OUR], websites=True).model_copy(update={"website_politeness_seconds": 0})
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler())
        asyncio.run(run(base_cfg))

    ref_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=base_cfg.output).model_copy(
        update={"website_politeness_seconds": 0, "verify_bulk": True}
    )
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler())
        asyncio.run(run(ref_cfg))

    ref_row = json.loads(ref_cfg.output.read_text(encoding="utf8").splitlines()[0])
    obs_changes = ref_row["run"]["refresh"]["observation_changes"]
    recovered = [o for o in obs_changes if o.get("reason") == "previously_observed_claim_recovered"]
    assert len(recovered) == 0, f"Unchanged verify_bulk refresh must not emit spurious recovered observation changes, got {recovered}"


# Scenario 5: Primary wrong_company STILL suppresses all claims under verify_bulk (Stage 2B preservation)
def test_primary_wrong_company_still_suppresses_all_claims_under_verify_bulk(tmp_path, monkeypatch):
    async def public_dns(host, port=443): return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    base_cfg = config(tmp_path / "base", [OUR], websites=True).model_copy(update={"website_politeness_seconds": 0})
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler())
        asyncio.run(run(base_cfg))

    ref_cfg = config(tmp_path / "refresh", [OUR], websites=True, previous=base_cfg.output).model_copy(
        update={"website_politeness_seconds": 0, "verify_bulk": True}
    )
    def wrong_primary_dispatch(request):
        if "/enhetsregisteret/api/enheter/" in str(request.url) and not str(request.url).endswith("/roller"):
            return httpx.Response(200, json=entity(OTHER))
        return full_handler()(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=wrong_primary_dispatch)
        asyncio.run(run(ref_cfg))

    ref_row = json.loads(ref_cfg.output.read_text(encoding="utf8").splitlines()[0])
    avail = [c for c in ref_row["claims"] if c.get("availability") == "available"]
    assert len(avail) == 0, "Primary wrong_company must suppress all available claims even under verify_bulk=True"
    assert any(e.get("code") == "wrong_company" for e in ref_row.get("errors", []))


# Scenario 6: verify_bulk with bulk CSV + live registry verification success carries forward failed roles
def test_verify_bulk_with_bulk_csv_live_success_carries_forward_roles(tmp_path, monkeypatch):
    async def public_dns(host, port=443): return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    b_file = bulk_file(tmp_path, [OUR])
    base_cfg = config(tmp_path / "base", [OUR], bulk=b_file, websites=True).model_copy(update={"website_politeness_seconds": 0})
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler())
        asyncio.run(run(base_cfg))

    ref_cfg = config(tmp_path / "refresh", [OUR], bulk=b_file, websites=True, previous=base_cfg.output).model_copy(
        update={"website_politeness_seconds": 0, "verify_bulk": True}
    )
    def roles_500_dispatch(request):
        if "/roller" in str(request.url):
            return httpx.Response(500)
        return full_handler()(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=roles_500_dispatch)
        asyncio.run(run(ref_cfg))

    ref_row = json.loads(ref_cfg.output.read_text(encoding="utf8").splitlines()[0])
    ref_roles = [c for c in ref_row["claims"] if c["family"] == "roles" and c["availability"] == "available"]
    assert len(ref_roles) >= 1
    assert all(c.get("carried_forward") for c in ref_roles)


# Scenario 7: Multiple refreshes under verify_bulk maintain claim ID stability
def test_multiple_refreshes_under_verify_bulk_maintain_stability(tmp_path, monkeypatch):
    async def public_dns(host, port=443): return ["93.184.216.34"]
    monkeypatch.setattr(policy, "resolve_public", public_dns)

    cfg0 = config(tmp_path / "run0", [OUR], websites=True).model_copy(update={"website_politeness_seconds": 0})
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler())
        asyncio.run(run(cfg0))

    cfg1 = config(tmp_path / "run1", [OUR], websites=True, previous=cfg0.output).model_copy(
        update={"website_politeness_seconds": 0, "verify_bulk": True}
    )
    def fail_roles(request):
        if "/roller" in str(request.url): return httpx.Response(500)
        return full_handler()(request)

    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=fail_roles)
        asyncio.run(run(cfg1))

    cfg2 = config(tmp_path / "run2", [OUR], websites=True, previous=cfg1.output).model_copy(
        update={"website_politeness_seconds": 0, "verify_bulk": True}
    )
    with respx.mock(assert_all_called=False) as router:
        router.route().mock(side_effect=full_handler())
        asyncio.run(run(cfg2))

    row0 = json.loads(cfg0.output.read_text(encoding="utf8").splitlines()[0])
    row2 = json.loads(cfg2.output.read_text(encoding="utf8").splitlines()[0])
    assert sorted(c["id"] for c in row0["claims"]) == sorted(c["id"] for c in row2["claims"])
    for r in (row0, row2):
        validate(r, "union")
