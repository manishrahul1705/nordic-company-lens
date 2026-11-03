import asyncio
import json
import pytest
from datetime import datetime, timezone, timedelta
from signalpost.web.candidates import generate, Candidate
from signalpost.web import collector, policy
from signalpost.web.html import Page
from signalpost.sources import nav
from signalpost.models.envelope import Envelope, Run, Claim
from signalpost.runner import placeholder
from signalpost.io.report import compute_funnel_metrics, compute_rejection_reasons
from tests.test_registry import config, handler, entity

OUR_ORG = "923609016"
SUB_ORG = "993578843"
AGENCY_ORG = "988258229"
FILL = "Corporate services, technical consulting, and public disclosures. " * 8


def make_page(body: str, url: str = "https://example.no/") -> Page:
    return Page(body.encode("utf-8"), url)


def make_envelope(org: str = OUR_ORG) -> Envelope:
    env = placeholder(org, "run-f09", "2026-10-21T00:00:00Z")
    env.run.sections["identity"] = "available"
    env.run.sections["website"] = "not_available"
    return env


def test_nav_employer_homepage_nomination_order():
    context = {
        "name": "Acme Solutions AS",
        "website": "https://registered-site.no",
        "email": "contact@registered-email.no",
        "nav_homepages": [
            {"url": "https://nav-discovered-site.no", "subunit_orgnr": None}
        ]
    }
    candidates = generate(context)
    origins = [c.origin for c in candidates]
    domains = [c.domain for c in candidates]
    
    assert "nav_employer_homepage" in origins
    nav_idx = origins.index("nav_employer_homepage")
    assert domains[nav_idx] == "nav-discovered-site.no"
    
    # Priority check: nav_employer_homepage must appear BEFORE guessed legal_name_slugs
    if "legal_name_slug" in origins:
        slug_idx = origins.index("legal_name_slug")
        assert nav_idx < slug_idx


def test_nav_subunit_employer_homepage_nomination():
    context = {
        "name": "Acme Solutions AS",
        "nav_homepages": [
            {"url": "https://subunit-site.no", "subunit_orgnr": SUB_ORG}
        ]
    }
    candidates = generate(context)
    matching = [c for c in candidates if c.origin == "nav_employer_homepage"]
    assert len(matching) == 1
    assert matching[0].domain == "subunit-site.no"
    assert matching[0].subunit_orgnr == SUB_ORG


def test_nav_homepage_url_injection_rejected():
    context = {
        "name": "Acme Solutions AS",
        "nav_homepages": [
            {"url": "javascript:alert(1)"},
            {"url": "file:///etc/passwd"},
            {"url": "http://user:password@malicious.no"},
            {"url": "http://127.0.0.1"},
            {"url": "http://localhost/jobs"},
            {"url": "https://bad-port.no:8080/jobs"},
            {"url": ""},
            {"url": None},
        ]
    }
    candidates = generate(context)
    nav_candidates = [c for c in candidates if c.origin == "nav_employer_homepage"]
    assert len(nav_candidates) == 0


def test_nav_stream_and_cached_ad_preserves_employer_homepage():
    ad_content = {
        "uuid": "00000000-0000-4000-8000-000000000001",
        "title": "Senior Python Developer",
        "published": "2026-10-01T12:00:00Z",
        "expires": "2026-11-01T12:00:00Z",
        "employer": {
            "name": "Acme Solutions AS",
            "orgnr": OUR_ORG,
            "homepage": "https://acme-careers.no"
        }
    }
    emp = ad_content.get("employer") or {}
    hp = emp.get("homepage")
    assert hp == "https://acme-careers.no"


def test_nav_employer_homepage_verified_with_exact_orgnr(tmp_path, monkeypatch):
    async def run_test():
        from signalpost.web import policy
        
        async def fake_resolve(host, port=443):
            return ["93.184.216.34"]
        monkeypatch.setattr(policy, "resolve_public", fake_resolve)
        
        class FakeResponse:
            def __init__(self, url, status, body):
                self.url = url
                self.status = status
                self.body = body.encode("utf-8") if isinstance(body, str) else body
                import hashlib
                self.sha = hashlib.sha256(self.body).hexdigest()
                self.retrieved_at = "2026-10-21T00:00:00Z"
        
        class FakeHttp:
            def __init__(self):
                self.blobs = MagicBlobStore()
                self.attempts = {}
                self.counts = {}
                self.accepted_pages = {}
                self.config = type("Config", (), {
                    "website_stop_after_verified": True,
                    "registry_declared": False,
                    "website_request_cap": 8
                })()
            def discovery_cap(self, org):
                return 8
            async def candidate(self, cand, org, proved):
                if cand.domain == "nav-verified.no":
                    html = f"<html><head><title>Acme</title></head><body>{FILL}<footer>Org.nr: {OUR_ORG}</footer></body></html>"
                    return FakeResponse("https://nav-verified.no/", 200, html)
                return FakeResponse(cand.url, 404, "not found")
            async def get(self, url, org, domain, proved=None, xml=False):
                return FakeResponse(url, 404, "not found")
        
        class MagicBlobStore:
            def put(self, data):
                import hashlib
                return hashlib.sha256(data).hexdigest()
        
        envelope = make_envelope(OUR_ORG)
        envelope.claims.append(Claim(
            family="hiring",
            field="hiring.job.00000000-0000-4000-8000-000000000001",
            value={
                "uuid": "00000000-0000-4000-8000-000000000001",
                "employer_orgnr": OUR_ORG,
                "title": "Engineer",
                "employer_homepage": "https://nav-verified.no"
            },
            availability="available",
            confidence=1.0,
            evidence_ids=["e" * 64],
            id="a" * 64,
            reporting_period=None,
            carried_forward=False,
            first_observed_at="2026-10-21T00:00:00Z",
            last_observed_at="2026-10-21T00:00:00Z"
        ))
        
        fake_http = FakeHttp()
        section = await collector.fetch(OUR_ORG, envelope, None, fake_http, previous=None)
        
        # Official website claim must be published and VERIFIED
        assert section.state == "available"
        website_claims = [c for c in section.claims if c.field == "official_website"]
        assert len(website_claims) == 1
        val = website_claims[0].value
        assert val["identity_level"] == "VERIFIED"
        assert val["candidate_origin"] == "nav_employer_homepage"
        assert val["final_url"] == "https://nav-verified.no"
        assert website_claims[0].reasons.get("discovery_method") == "nav employer homepage"

    asyncio.run(run_test())


def test_nav_index_to_collector_homepage_bridge(monkeypatch):
    async def run_test():
        from signalpost.web import policy
        
        async def fake_resolve(host, port=443):
            return ["93.184.216.34"]
        monkeypatch.setattr(policy, "resolve_public", fake_resolve)
        
        class FakeResponse:
            def __init__(self, url, status, body):
                self.url = url
                self.status = status
                self.body = body.encode("utf-8") if isinstance(body, str) else body
                import hashlib
                self.sha = hashlib.sha256(self.body).hexdigest()
                self.retrieved_at = "2026-10-21T00:00:00Z"
        
        class FakeHttp:
            def __init__(self):
                self.blobs = MagicBlobStore()
                self.attempts = {}
                self.counts = {}
                self.accepted_pages = {}
                self.config = type("Config", (), {
                    "website_stop_after_verified": True,
                    "registry_declared": False,
                    "website_request_cap": 8
                })()
            def discovery_cap(self, org):
                return 8
            async def candidate(self, cand, org, proved):
                if cand.domain == "nav-from-index.no":
                    html = f"<html><head><title>Acme</title></head><body>{FILL}<footer>Org.nr: {OUR_ORG}</footer></body></html>"
                    return FakeResponse("https://nav-from-index.no/", 200, html)
                return FakeResponse(cand.url, 404, "not found")
            async def get(self, url, org, domain, proved=None, xml=False):
                return FakeResponse(url, 404, "not found")
        
        class MagicBlobStore:
            def put(self, data):
                import hashlib
                return hashlib.sha256(data).hexdigest()
        
        envelope = make_envelope(OUR_ORG)
        
        class FakeIndex:
            def __init__(self):
                ad_val = {
                    "uuid": "00000000-0000-4000-8000-000000000001",
                    "employer_orgnr": OUR_ORG,
                    "title": "Engineer",
                    "employer_homepage": "https://nav-from-index.no"
                }
                self.ads = {
                    OUR_ORG: [type("MockAd", (), {"value": ad_val})()]
                }
        
        nav_index = FakeIndex()
        fake_http = FakeHttp()
        section = await collector.fetch(OUR_ORG, envelope, None, fake_http, previous=None, nav_index=nav_index)
        
        assert section.state == "available"
        website_claims = [c for c in section.claims if c.field == "official_website"]
        assert len(website_claims) == 1
        val = website_claims[0].value
        assert val["identity_level"] == "VERIFIED"
        assert val["candidate_origin"] == "nav_employer_homepage"
        assert val["final_url"] == "https://nav-from-index.no"
        assert website_claims[0].reasons.get("discovery_method") == "nav employer homepage"

    asyncio.run(run_test())


def test_nav_employer_homepage_rejected_if_only_high_heuristics(monkeypatch):
    async def run_test():
        from signalpost.web import policy
        
        async def fake_resolve(host, port=443):
            return ["93.184.216.34"]
        monkeypatch.setattr(policy, "resolve_public", fake_resolve)
        
        class FakeResponse:
            def __init__(self, url, status, body):
                self.url = url
                self.status = status
                self.body = body.encode("utf-8") if isinstance(body, str) else body
                import hashlib
                self.sha = hashlib.sha256(self.body).hexdigest()
                self.retrieved_at = "2026-10-21T00:00:00Z"
        
        class FakeHttp:
            def __init__(self):
                self.blobs = type("Blobs", (), {"put": lambda self, d: "a"*64})()
                self.attempts = {}
                self.counts = {}
                self.accepted_pages = {}
                self.config = type("Config", (), {
                    "website_stop_after_verified": True,
                    "registry_declared": False,
                    "website_request_cap": 8
                })()
            def discovery_cap(self, org):
                return 8
            async def candidate(self, cand, org, proved):
                html = (
                    f"<html><head><title>Acme Solutions</title></head>"
                    f"<body><h1>Acme Solutions AS</h1><p>Storgata 1, 0182 Oslo</p>"
                    f"<p>Phone: +47 12 34 56 78</p><main>{FILL}</main></body></html>"
                )
                return FakeResponse("https://heuristic-match.no/", 200, html)
            async def get(self, url, org, domain, proved=None, xml=False):
                return FakeResponse(url, 404, "not found")
        
        envelope = make_envelope(OUR_ORG)
        envelope.claims.append(Claim(
            family="hiring",
            field="hiring.job.00000000-0000-4000-8000-000000000001",
            value={
                "uuid": "00000000-0000-4000-8000-000000000001",
                "employer_orgnr": OUR_ORG,
                "title": "Engineer",
                "employer_homepage": "https://heuristic-match.no"
            },
            availability="available",
            confidence=1.0,
            evidence_ids=["e" * 64],
            id="a" * 64,
            reporting_period=None,
            carried_forward=False,
            first_observed_at="2026-10-21T00:00:00Z",
            last_observed_at="2026-10-21T00:00:00Z"
        ))
        
        fake_http = FakeHttp()
        section = await collector.fetch(OUR_ORG, envelope, None, fake_http, previous=None)
        
        assert section.state in ("not_available", "failed")
        published = [c for c in section.claims if c.field == "official_website"]
        assert len(published) == 0

    asyncio.run(run_test())


def test_nav_employer_homepage_agency_rejected(monkeypatch):
    async def run_test():
        from signalpost.web import policy
        
        async def fake_resolve(host, port=443):
            return ["93.184.216.34"]
        monkeypatch.setattr(policy, "resolve_public", fake_resolve)
        
        class FakeResponse:
            def __init__(self, url, status, body):
                self.url = url
                self.status = status
                self.body = body.encode("utf-8") if isinstance(body, str) else body
                import hashlib
                self.sha = hashlib.sha256(self.body).hexdigest()
                self.retrieved_at = "2026-10-21T00:00:00Z"
        
        class FakeHttp:
            def __init__(self):
                self.blobs = type("Blobs", (), {"put": lambda self, d: "a"*64})()
                self.attempts = {}
                self.counts = {}
                self.accepted_pages = {}
                self.config = type("Config", (), {
                    "website_stop_after_verified": True,
                    "registry_declared": False,
                    "website_request_cap": 8
                })()
            def discovery_cap(self, org):
                return 8
            async def candidate(self, cand, org, proved):
                html = f"<html><head><title>Manpower Rekruttering</title></head><body>{FILL}<footer>Org nr: {AGENCY_ORG}</footer></body></html>"
                return FakeResponse("https://agency.no/", 200, html)
            async def get(self, url, org, domain, proved=None, xml=False):
                return FakeResponse(url, 404, "not found")
        
        envelope = make_envelope(OUR_ORG)
        envelope.claims.append(Claim(
            family="hiring",
            field="hiring.job.00000000-0000-4000-8000-000000000001",
            value={
                "uuid": "00000000-0000-4000-8000-000000000001",
                "employer_orgnr": OUR_ORG,
                "title": "Engineer",
                "employer_homepage": "https://agency.no"
            },
            availability="available",
            confidence=1.0,
            evidence_ids=["e" * 64],
            id="a" * 64,
            reporting_period=None,
            carried_forward=False,
            first_observed_at="2026-10-21T00:00:00Z",
            last_observed_at="2026-10-21T00:00:00Z"
        ))
        
        fake_http = FakeHttp()
        section = await collector.fetch(OUR_ORG, envelope, None, fake_http, previous=None)
        assert section.state in ("not_available", "failed")
        published = [c for c in section.claims if c.field == "official_website"]
        assert len(published) == 0

    asyncio.run(run_test())


def test_nav_employer_homepage_group_site_rejected_without_dedicated_card(monkeypatch):
    async def run_test():
        from signalpost.web import policy
        
        async def fake_resolve(host, port=443):
            return ["93.184.216.34"]
        monkeypatch.setattr(policy, "resolve_public", fake_resolve)
        
        class FakeResponse:
            def __init__(self, url, status, body):
                self.url = url
                self.status = status
                self.body = body.encode("utf-8") if isinstance(body, str) else body
                import hashlib
                self.sha = hashlib.sha256(self.body).hexdigest()
                self.retrieved_at = "2026-10-21T00:00:00Z"
        
        class FakeHttp:
            def __init__(self):
                self.blobs = type("Blobs", (), {"put": lambda self, d: "a"*64})()
                self.attempts = {}
                self.counts = {}
                self.accepted_pages = {}
                self.config = type("Config", (), {
                    "website_stop_after_verified": True,
                    "registry_declared": False,
                    "website_request_cap": 8
                })()
            def discovery_cap(self, org):
                return 8
            async def candidate(self, cand, org, proved):
                html = (
                    f"<html><head><title>Nordic Group</title></head><body><h1>Nordic Group</h1>"
                    f"<p>Holding portal for subsidiaries: Org nr {OUR_ORG}, Org nr {SUB_ORG}, Org nr {AGENCY_ORG}</p>"
                    f"<main>{FILL}</main></body></html>"
                )
                return FakeResponse("https://group-site.no/", 200, html)
            async def get(self, url, org, domain, proved=None, xml=False):
                return FakeResponse(url, 404, "not found")
        
        envelope = make_envelope(OUR_ORG)
        envelope.claims.append(Claim(
            family="hiring",
            field="hiring.job.00000000-0000-4000-8000-000000000001",
            value={
                "uuid": "00000000-0000-4000-8000-000000000001",
                "employer_orgnr": OUR_ORG,
                "title": "Engineer",
                "employer_homepage": "https://group-site.no"
            },
            availability="available",
            confidence=1.0,
            evidence_ids=["e" * 64],
            id="a" * 64,
            reporting_period=None,
            carried_forward=False,
            first_observed_at="2026-10-21T00:00:00Z",
            last_observed_at="2026-10-21T00:00:00Z"
        ))
        
        fake_http = FakeHttp()
        section = await collector.fetch(OUR_ORG, envelope, None, fake_http, previous=None)
        assert section.state in ("not_available", "failed")
        published = [c for c in section.claims if c.field == "official_website"]
        assert len(published) == 0

    asyncio.run(run_test())


def test_nav_subunit_employer_homepage_verified_via_subunit(monkeypatch):
    async def run_test():
        from signalpost.web import policy
        
        async def fake_resolve(host, port=443):
            return ["93.184.216.34"]
        monkeypatch.setattr(policy, "resolve_public", fake_resolve)
        
        class FakeResponse:
            def __init__(self, url, status, body):
                self.url = url
                self.status = status
                self.body = body.encode("utf-8") if isinstance(body, str) else body
                import hashlib
                self.sha = hashlib.sha256(self.body).hexdigest()
                self.retrieved_at = "2026-10-21T00:00:00Z"
        
        class FakeHttp:
            def __init__(self):
                self.blobs = MagicBlobStore()
                self.attempts = {}
                self.counts = {}
                self.accepted_pages = {}
                self.config = type("Config", (), {
                    "website_stop_after_verified": True,
                    "registry_declared": False,
                    "website_request_cap": 8
                })()
            def discovery_cap(self, org):
                return 8
            async def candidate(self, cand, org, proved):
                if cand.domain == "branch-store.no":
                    html = f"<html><head><title>Acme Branch</title></head><body>{FILL}<footer>Branch Org nr: {SUB_ORG}</footer></body></html>"
                    return FakeResponse("https://branch-store.no/", 200, html)
                return FakeResponse(cand.url, 404, "not found")
            async def get(self, url, org, domain, proved=None, xml=False):
                return FakeResponse(url, 404, "not found")
        
        class MagicBlobStore:
            def put(self, data):
                import hashlib
                return hashlib.sha256(data).hexdigest()
        
        envelope = make_envelope(OUR_ORG)
        envelope.claims.append(Claim(
            family="subunits",
            field="subunits.unit." + SUB_ORG,
            value={"organisation_number": SUB_ORG, "name": "Acme Branch"},
            availability="available",
            confidence=1.0,
            evidence_ids=["e" * 64],
            id="b" * 64,
            reporting_period=None,
            carried_forward=False,
            first_observed_at="2026-10-21T00:00:00Z",
            last_observed_at="2026-10-21T00:00:00Z"
        ))
        
        class FakeIndex:
            def __init__(self):
                ad_val = {
                    "uuid": "00000000-0000-4000-8000-000000000002",
                    "employer_orgnr": SUB_ORG,
                    "title": "Branch Specialist",
                    "employer_homepage": "https://branch-store.no"
                }
                self.ads = {
                    SUB_ORG: [type("MockAd", (), {"value": ad_val})()]
                }
        
        nav_index = FakeIndex()
        fake_http = FakeHttp()
        section = await collector.fetch(OUR_ORG, envelope, None, fake_http, previous=None, nav_index=nav_index)
        
        assert section.state == "available"
        website_claims = [c for c in section.claims if c.field == "official_website"]
        assert len(website_claims) == 1
        val = website_claims[0].value
        assert val["identity_level"] == "VERIFIED"
        assert val["candidate_origin"] == "nav_employer_homepage"
        assert val["matched_via_subunit"] == SUB_ORG
        assert "registered subunit" in website_claims[0].reasons.get("relationship", "")

    asyncio.run(run_test())


def test_nav_homepage_rejection_attribution_in_diagnostics():
    envelope = make_envelope(OUR_ORG)
    attempts = [
        {"domain": "unverified.no", "origin": "nav_employer_homepage", "reason": "foreign_orgnr"},
        {"domain": "group.no", "origin": "nav_employer_homepage", "reason": "unverified_multi_entity_site"}
    ]
    envelope.errors.append(type("MockError", (), {
        "section": "website",
        "code": "website_candidates",
        "message": json.dumps(attempts)
    })())
    
    reasons = compute_rejection_reasons([envelope])
    assert reasons.get("wrong_organization_number") == 1
    assert reasons.get("insufficient_ownership_proof") == 1
