"""Adversarial entity-resolution challenge set and wrong-company traps for NAV hiring (F08).

Validates all 17 corporate identity and workplace attribution scenarios:
1. Direct employer exact orgnr match
2. Registered workplace subunit match with attribution
3. Parent organization ad not attributed to subsidiary
4. Subsidiary ad not attributed to parent without registry subunit link
5. Corporate group holding ad rejected as subsidiary vacancy
6. Shared brand name across different legal entities rejected
7. Recruitment agency ad naming target company rejected
8. Staffing agency ad rejected
9. Franchise store with separate AS rejected
10. Municipality ad not attributed to separate municipal enterprise (KF/AS)
11. Public sector department sub-entity isolation
12. Renamed legal entity requiring exact orgnr proof
13. Same-name unrelated company rejected
14. Missing employer orgnr in detail rejected
15. Contradictory employer orgnr rejected
16. Employment location different from headquarters accepted if orgnr verified
17. Multiple work locations preserved without loss
"""
from datetime import datetime, timedelta, timezone
import pytest

from signalpost.models.envelope import Claim, Error, Run
from signalpost.models.evidence import Evidence, digest
from signalpost.runner import placeholder
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.nav import Ad, Index, Section, section

TARGET_PARENT_ORG = "923609016"  # Example Target AS
REGISTERED_SUBUNIT_ORG = "993578843"  # Official subunit
UNRELATED_SAME_NAME_ORG = "911222333"  # Example AS (unrelated)
STAFFING_AGENCY_ORG = "988776655"  # Staffing AS
HOLDING_COMPANY_ORG = "811222333"  # Example Group ASA
SUBSIDIARY_ORG = "922333444"  # Example Tech AS (subsidiary)
MUNICIPALITY_ORG = "874611212"  # Stavanger kommune


def make_envelope(parent_org=TARGET_PARENT_ORG, subunits=None):
    env = placeholder(parent_org, "run-test", "2026-10-21T12:00:00Z")
    env.run.sections["hiring"] = "available"
    env.run.sections["subunits"] = "available"
    if subunits:
        for sub_org in subunits:
            eid = "e" * 64
            env.claims.append(Claim(
                family="subunits",
                field="subunits.record",
                value={"organisation_number": sub_org, "name": f"Subunit {sub_org}"},
                availability="available",
                confidence=1.0,
                evidence_ids=[eid],
                id=f"sub_{sub_org}" + "0" * (64 - len(sub_org) - 4),
                first_observed_at="2026-10-21T12:00:00Z",
                last_observed_at="2026-10-21T12:00:00Z"
            ))
    return env


def make_nav_ad(blobs, uuid="00000000-0000-0000-0000-000000000001", employer_org=TARGET_PARENT_ORG, title="Software Engineer", locations=None):
    val = {
        "uuid": uuid,
        "employer_orgnr": employer_org,
        "status": "ACTIVE",
        "title": title,
        "published": "2026-10-01T00:00:00Z",
        "expires": (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "location": locations or [{"municipality": "OSLO", "city": "Oslo"}],
        "occupation_categories": ["IT"],
        "url": f"https://arbeidsplassen.nav.no/stillinger/stilling/{uuid}"
    }
    raw = bytes(f'{{"uuid":"{uuid}","ad_content":{{"title":"{title}"}}}}', "utf-8")
    sha = blobs.put(raw)
    return Ad(
        value=val,
        sha=sha,
        url=f"https://pam-stilling-feed.nav.no/api/v1/feedentry/{uuid}",
        retrieved_at="2026-10-21T12:00:00Z",
        page_sha=None,
        page_url=None,
        page_locator=None,
        page_retrieved_at=None
    )


# 1. Direct employer exact orgnr match
def test_direct_employer_exact_orgnr_match_accepted(tmp_path):
    blobs = BlobStore(tmp_path)
    env = make_envelope(TARGET_PARENT_ORG)
    index = Index(complete=True)
    ad = make_nav_ad(blobs, uuid="11111111-1111-1111-1111-111111111111", employer_org=TARGET_PARENT_ORG)
    index.ads[TARGET_PARENT_ORG] = [ad]

    sec = section(env, index, blobs)
    assert sec.state == "available"
    assert len(sec.claims) == 1
    assert sec.claims[0].value["uuid"] == "11111111-1111-1111-1111-111111111111"
    assert "organisation " in sec.claims[0].value["matched_via"]


# 2. Registered workplace subunit match with attribution
def test_registered_workplace_subunit_orgnr_match_accepted_with_subunit_attribution(tmp_path):
    blobs = BlobStore(tmp_path)
    env = make_envelope(TARGET_PARENT_ORG, subunits=[REGISTERED_SUBUNIT_ORG])
    index = Index(complete=True)
    ad = make_nav_ad(blobs, uuid="22222222-2222-2222-2222-222222222222", employer_org=REGISTERED_SUBUNIT_ORG)
    index.ads[REGISTERED_SUBUNIT_ORG] = [ad]

    sec = section(env, index, blobs)
    assert sec.state == "available"
    assert len(sec.claims) == 1
    assert sec.claims[0].value["uuid"] == "22222222-2222-2222-2222-222222222222"
    assert sec.claims[0].value["matched_via"] == f"subunit {REGISTERED_SUBUNIT_ORG}"


# 3. Parent organization ad not attributed to subsidiary
def test_parent_org_ad_not_attributed_to_subsidiary(tmp_path):
    blobs = BlobStore(tmp_path)
    # Target is SUBSIDIARY, but ad belongs to HOLDING_COMPANY_ORG
    env = make_envelope(SUBSIDIARY_ORG)
    index = Index(complete=True)
    ad = make_nav_ad(blobs, uuid="33333333-3333-3333-3333-333333333333", employer_org=HOLDING_COMPANY_ORG)
    index.ads[HOLDING_COMPANY_ORG] = [ad]

    sec = section(env, index, blobs)
    assert len(sec.claims) == 0
    assert sec.state == "not_available"


# 4. Subsidiary ad not attributed to parent without registry subunit link
def test_subsidiary_ad_not_attributed_to_parent_without_registry_link(tmp_path):
    blobs = BlobStore(tmp_path)
    # Target is PARENT, but ad belongs to SUBSIDIARY_ORG (which is an independent AS, not a subunit)
    env = make_envelope(TARGET_PARENT_ORG)
    index = Index(complete=True)
    ad = make_nav_ad(blobs, uuid="44444444-4444-4444-4444-444444444444", employer_org=SUBSIDIARY_ORG)
    index.ads[SUBSIDIARY_ORG] = [ad]

    sec = section(env, index, blobs)
    assert len(sec.claims) == 0
    assert sec.state == "not_available"


# 5. Corporate group holding ad rejected as subsidiary vacancy
def test_corporate_group_holding_ad_rejected_as_subsidiary_vacancy(tmp_path):
    blobs = BlobStore(tmp_path)
    env = make_envelope(TARGET_PARENT_ORG)
    index = Index(complete=True)
    ad = make_nav_ad(blobs, uuid="55555555-5555-5555-5555-555555555555", employer_org=HOLDING_COMPANY_ORG)
    index.ads[HOLDING_COMPANY_ORG] = [ad]

    sec = section(env, index, blobs)
    assert len(sec.claims) == 0


# 6. Shared brand name across different legal entities rejected
def test_shared_brand_different_legal_entity_rejected(tmp_path):
    blobs = BlobStore(tmp_path)
    env = make_envelope(TARGET_PARENT_ORG)
    index = Index(complete=True)
    ad = make_nav_ad(blobs, uuid="66666666-6666-6666-6666-666666666666", employer_org=UNRELATED_SAME_NAME_ORG, title="Brand Specialist")
    # Even if stored in index under the unrelated org, it never leaks to TARGET_PARENT_ORG
    index.ads[UNRELATED_SAME_NAME_ORG] = [ad]

    sec = section(env, index, blobs)
    assert len(sec.claims) == 0


# 7. Recruitment agency ad naming target company rejected
def test_recruitment_agency_posting_for_client_rejected(tmp_path):
    blobs = BlobStore(tmp_path)
    env = make_envelope(TARGET_PARENT_ORG)
    index = Index(complete=True)
    # Employer is staffing agency, even if the text mentions Target AS
    ad = make_nav_ad(blobs, uuid="77777777-7777-7777-7777-777777777777", employer_org=STAFFING_AGENCY_ORG, title="Senior Consultant at Example Target AS")
    index.ads[STAFFING_AGENCY_ORG] = [ad]

    sec = section(env, index, blobs)
    assert len(sec.claims) == 0


# 8. Staffing agency ad rejected
def test_staffing_agency_consultant_position_rejected(tmp_path):
    blobs = BlobStore(tmp_path)
    env = make_envelope(TARGET_PARENT_ORG)
    index = Index(complete=True)
    ad = make_nav_ad(blobs, uuid="88888888-8888-8888-8888-888888888888", employer_org=STAFFING_AGENCY_ORG, title="External Contractor")
    index.ads[STAFFING_AGENCY_ORG] = [ad]

    sec = section(env, index, blobs)
    assert len(sec.claims) == 0


# 9. Franchise store with separate AS rejected
def test_franchise_store_different_legal_orgnr_rejected(tmp_path):
    blobs = BlobStore(tmp_path)
    FRANCHISE_LOCAL_ORG = "933444555"
    env = make_envelope(TARGET_PARENT_ORG)  # Target is Franchisor AS
    index = Index(complete=True)
    ad = make_nav_ad(blobs, uuid="99999999-9999-9999-9999-999999999999", employer_org=FRANCHISE_LOCAL_ORG, title="Store Clerk")
    index.ads[FRANCHISE_LOCAL_ORG] = [ad]

    sec = section(env, index, blobs)
    assert len(sec.claims) == 0


# 10. Municipality ad not attributed to separate municipal enterprise (KF/AS)
def test_municipality_ad_not_attributed_to_municipal_corporation_as(tmp_path):
    blobs = BlobStore(tmp_path)
    MUNICIPAL_ENTERPRISE_AS = "977888999"  # Separate municipal AS
    env = make_envelope(MUNICIPAL_ENTERPRISE_AS)
    index = Index(complete=True)
    ad = make_nav_ad(blobs, uuid="aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa", employer_org=MUNICIPALITY_ORG, title="Kommune Lærer")
    index.ads[MUNICIPALITY_ORG] = [ad]

    sec = section(env, index, blobs)
    assert len(sec.claims) == 0


# 11. Public sector department sub-entity isolation
def test_public_sector_agency_department_sub_entity_isolation(tmp_path):
    blobs = BlobStore(tmp_path)
    DEPT_A = "988111222"
    DEPT_B = "988333444"
    env = make_envelope(DEPT_A)
    index = Index(complete=True)
    ad = make_nav_ad(blobs, uuid="bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb", employer_org=DEPT_B, title="Saksbehandler")
    index.ads[DEPT_B] = [ad]

    sec = section(env, index, blobs)
    assert len(sec.claims) == 0


# 12. Renamed legal entity requiring exact orgnr proof
def test_renamed_legal_entity_requires_orgnr_not_old_name_alone(tmp_path):
    blobs = BlobStore(tmp_path)
    env = make_envelope(TARGET_PARENT_ORG)
    index = Index(complete=True)
    # Ad has same orgnr but perhaps older registered name
    ad = make_nav_ad(blobs, uuid="cccccccc-cccc-cccc-cccc-cccccccccccc", employer_org=TARGET_PARENT_ORG, title="CTO (Old Company Name)")
    index.ads[TARGET_PARENT_ORG] = [ad]

    sec = section(env, index, blobs)
    assert len(sec.claims) == 1
    assert sec.claims[0].value["uuid"] == "cccccccc-cccc-cccc-cccc-cccccccccccc"


# 13. Same-name unrelated company rejected
def test_same_name_unrelated_norwegian_company_rejected(tmp_path):
    blobs = BlobStore(tmp_path)
    env = make_envelope(TARGET_PARENT_ORG)
    index = Index(complete=True)
    ad = make_nav_ad(blobs, uuid="dddddddd-dddd-dddd-dddd-dddddddddddd", employer_org=UNRELATED_SAME_NAME_ORG, title="Developer")
    index.ads[UNRELATED_SAME_NAME_ORG] = [ad]

    sec = section(env, index, blobs)
    assert len(sec.claims) == 0


# 14. Missing employer orgnr in detail rejected
def test_missing_employer_orgnr_in_detail_rejected(tmp_path):
    blobs = BlobStore(tmp_path)
    env = make_envelope(TARGET_PARENT_ORG)
    index = Index(complete=True)
    ad = make_nav_ad(blobs, uuid="eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee", employer_org="", title="Ghost Position")
    # Even if mistakenly indexed in TARGET_PARENT_ORG list, section check verifies actual_emp in parents
    index.ads[TARGET_PARENT_ORG] = [ad]

    sec = section(env, index, blobs)
    assert len(sec.claims) == 0


# 15. Contradictory employer orgnr rejected
def test_contradictory_employer_orgnr_rejected(tmp_path):
    blobs = BlobStore(tmp_path)
    env = make_envelope(TARGET_PARENT_ORG)
    index = Index(complete=True)
    # Index key says TARGET_PARENT_ORG, but internal ad value says UNRELATED_SAME_NAME_ORG
    ad = make_nav_ad(blobs, uuid="ffffffff-ffff-ffff-ffff-ffffffffffff", employer_org=UNRELATED_SAME_NAME_ORG)
    index.ads[TARGET_PARENT_ORG] = [ad]

    sec = section(env, index, blobs)
    assert len(sec.claims) == 0  # actual_emp not in parents rejects it!


# 16. Employment location different from headquarters accepted if orgnr verified
def test_employment_location_different_from_hq_accepted_if_legal_orgnr_matches(tmp_path):
    blobs = BlobStore(tmp_path)
    env = make_envelope(TARGET_PARENT_ORG)
    index = Index(complete=True)
    # HQ is Oslo, but workplace is Tromsø
    ad = make_nav_ad(blobs, uuid="10101010-1010-1010-1010-101010101010", employer_org=TARGET_PARENT_ORG, locations=[{"municipality": "TROMSØ", "city": "Tromsø"}])
    index.ads[TARGET_PARENT_ORG] = [ad]

    sec = section(env, index, blobs)
    assert len(sec.claims) == 1
    assert sec.claims[0].value["location"][0]["municipality"] == "TROMSØ"


# 17. Multiple work locations preserved without loss
def test_multiple_work_locations_all_preserved_in_claim_value(tmp_path):
    blobs = BlobStore(tmp_path)
    env = make_envelope(TARGET_PARENT_ORG)
    index = Index(complete=True)
    locs = [
        {"municipality": "BERGEN", "city": "Bergen"},
        {"municipality": "STAVANGER", "city": "Stavanger"},
        {"municipality": "TRONDHEIM", "city": "Trondheim"}
    ]
    ad = make_nav_ad(blobs, uuid="20202020-2020-2020-2020-202020202020", employer_org=TARGET_PARENT_ORG, locations=locs)
    index.ads[TARGET_PARENT_ORG] = [ad]

    sec = section(env, index, blobs)
    assert len(sec.claims) == 1
    stored_locs = sec.claims[0].value["location"]
    assert len(stored_locs) == 3
    assert {l["city"] for l in stored_locs} == {"Bergen", "Stavanger", "Trondheim"}
