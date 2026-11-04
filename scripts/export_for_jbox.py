"""Convert a signalpost profiles.jsonl into companies.json and facts.json for the JBox site.

Usage:
    python export_for_jbox.py profiles.jsonl out_dir

Only sections with status "available" become facts. Missing values stay null (never 0).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

LABELS = {
    "registry_live": "identity",
    "registry": "identity",
    "financials": "financials",
    "roles": "people",
    "locations": "locations",
    "website": "website",
    "social": "social",
    "hiring": "jobs",
    "jobs": "jobs",
    "public_activity": "news",
    "activity": "news",
    "registry_changes": "news",
}

SOURCE_NAMES = {
    "data.brreg.no/enhetsregisteret": "Brønnøysund Enhetsregisteret",
    "data.brreg.no/regnskapsregisteret": "Brønnøysund Regnskapsregisteret",
    "arbeidsplassen.nav.no": "NAV job ads",
    "nav.no": "NAV",
}

ROLE_EN = {
    "DAGL": "CEO", "LEDE": "Board Chair", "NEST": "Deputy Chair", "MEDL": "Board Member",
    "VARA": "Deputy Board Member", "OBS": "Board Observer", "REVI": "Auditor", "REGN": "Accountant",
    "INNH": "Owner", "DTPR": "Partner (proportional liability)", "DTSO": "Partner (joint liability)",
    "KONT": "Contact Person", "FFØR": "Business Manager", "KOMP": "General Partner", "SAM": "Co-owner",
    "BEST": "Managing Shipowner", "REPR": "Norwegian Representative", "KDEB": "Estate Administrator",
    "PROK": "Authorised Signatory (procura)", "SIGN": "Signatory",
}

FIN_FIELDS = [
    ("revenue", "Revenue"),
    ("operating_result", "Operating result"),
    ("profit_before_tax", "Profit before tax"),
    ("annual_result", "Annual result"),
    ("assets", "Total assets"),
    ("equity", "Equity"),
    ("debt", "Debt"),
]


def source_name(url: str | None, source_type: str | None) -> str:
    url = url or ""
    if "data.brreg.no/enhetsregisteret/api/oppdateringer" in url:
        return "Brønnøysund Enhetsregisteret (update log)"
    for key, name in SOURCE_NAMES.items():
        if key in url:
            return name
    if source_type in ("website", "company_owned"):
        return "Company website"
    if source_type == "official_nav":
        return "NAV job ads"
    if source_type == "official_registry":
        return "Brønnøysund Enhetsregisteret"
    return (source_type or "source").replace("_", " ").title()


def text(v) -> str | None:
    if v is None:
        return None
    if isinstance(v, list):
        v = ", ".join(str(x) for x in v if x is not None)
    s = str(v).strip()
    return s or None


def addr(a: dict | None) -> str | None:
    if not a:
        return None
    street = text(a.get("adresse"))
    parts = [street, " ".join(p for p in [a.get("postnummer"), a.get("poststed")] if p)]
    return text(", ".join(p for p in parts if p))


def year_of(period: dict | None) -> str | None:
    if not period:
        return None
    end = period.get("tilDato") or ""
    return end[:4] or None


def period_of(period: dict | None) -> str | None:
    if not period:
        return None
    a, b = period.get("fraDato"), period.get("tilDato")
    return f"{a} to {b}" if a and b else (a or b)


def fact(org, category, field, value, sec, period=None, note=None):
    value = text(value)
    if value is None:
        return None
    return {
        "org_number": org,
        "category": category,
        "field": field,
        "value": value,
        "source_name": source_name(sec.get("source_url"), sec.get("source_type")),
        "source_url": sec.get("source_url") or None,
        "retrieved_at": sec.get("retrieved_at"),
        "reporting_period": period,
        "excerpt": note or f"{field}: {value}",
        "evidence_sha256": sec.get("content_sha256"),
    }


def generic(org, category, name, value, sec, out):
    """Flatten unknown section shapes into readable facts."""
    if isinstance(value, dict):
        for k, v in value.items():
            if isinstance(v, (dict, list)) and v:
                generic(org, category, f"{name} {k}".strip(), v, sec, out)
            else:
                f = fact(org, category, f"{name} {k}".strip().replace("_", " "), v, sec)
                if f:
                    out.append(f)
    elif isinstance(value, list):
        for i, v in enumerate(value, 1):
            if isinstance(v, dict):
                title = text(v.get("title") or v.get("name") or v.get("headline") or v.get("url"))
                url = v.get("url") or v.get("link")
                when = text(v.get("published") or v.get("date") or v.get("published_at"))
                if title:
                    f = fact(org, category, name or category, title, sec, period=when)
                    if f:
                        if url and str(url).startswith(("http://", "https://")):
                            f["source_url"] = url
                        out.append(f)
                        continue
                generic(org, category, f"{name} {i}".strip(), v, sec, out)
            else:
                f = fact(org, category, name or category, v, sec)
                if f:
                    out.append(f)
    else:
        f = fact(org, category, name or category, value, sec)
        if f:
            out.append(f)


def convert(profile: dict):
    org = profile.get("organisation_number")
    ev = profile.get("evidence") or {}
    company = {
        "org_number": org,
        "legal_name": profile.get("name"),
        "legal_form": None,
        "municipality": profile.get("municipality"),
        "industry_code": None,
        "industry_text": None,
        "employees": None,
        "founded": None,
        "address": None,
        "website": profile.get("website"),
        "latest_year": None,
        "latest_revenue": None,
        "latest_profit": None,
        "currency": None,
        "revenue_growth": None,
        "board_chair": None,
        "ceo": None,
        "locations_count": 0,
        "jobs_count": 0,
        "news_count": 0,
        "sections": {},
    }
    facts: list[dict] = []

    for key, sec in ev.items():
        if not isinstance(sec, dict):
            continue
        category = LABELS.get(key, key.replace("_", " "))
        company["sections"][category] = sec.get("status")
        if sec.get("status") != "available":
            continue
        val = sec.get("value")

        if key in ("registry_live", "registry") and isinstance(val, dict):
            ind = val.get("industry") or {}
            company.update(
                legal_form=val.get("legal_form"),
                industry_code=ind.get("kode"),
                industry_text=ind.get("beskrivelse"),
                employees=val.get("employees"),
                founded=sec.get("effective_at"),
                address=addr(val.get("business_address")),
            )
            registry_site = val.get("website")
            if registry_site:
                company["registry_website"] = registry_site
            ba = addr(val.get("business_address"))
            if ba:
                f = fact(org, "locations", "Business address", ba, sec)
                if f:
                    facts.append(f)
            for f in [
                fact(org, "identity", "Legal name", val.get("name"), sec),
                fact(org, "identity", "Organisation number", val.get("organisation_number"), sec),
                fact(org, "identity", "Legal form", val.get("legal_form"), sec),
                fact(org, "identity", "Industry", ind.get("beskrivelse"), sec, note=f"NACE {ind.get('kode')}: {ind.get('beskrivelse')}" if ind.get("kode") else None),
                fact(org, "identity", "Industry code", ind.get("kode"), sec, note=f"NACE {ind.get('kode')}: {ind.get('beskrivelse')}" if ind.get("kode") else None),
                fact(org, "identity", "Municipality", (val.get("business_address") or {}).get("kommune"), sec, note=f"Business address municipality ({(val.get('business_address') or {}).get('kommunenummer') or ''})"),
                fact(org, "identity", "Employees", val.get("employees"), sec),
                fact(org, "identity", "Founded", sec.get("effective_at"), sec),
                fact(org, "identity", "Postal address", addr(val.get("postal_address")) if addr(val.get("postal_address")) != addr(val.get("business_address")) else None, sec),
                fact(org, "identity", "Latest submitted accounts", val.get("latest_submitted_accounts"), sec),
            ]:
                if f:
                    facts.append(f)

        elif key == "financials" and isinstance(val, dict):
            recs = [r for r in val.get("records", []) if isinstance(r, dict)]
            recs.sort(key=lambda r: (r.get("period") or {}).get("tilDato") or "", reverse=True)
            if recs:
                latest = recs[0]
                company.update(
                    latest_year=year_of(latest.get("period")),
                    latest_revenue=latest.get("revenue"),
                    latest_profit=latest.get("annual_result"),
                    currency=latest.get("currency"),
                )
                comp = latest.get("comparability_with_prior") or {}
                if comp.get("comparable") and comp.get("growth_rate") is not None:
                    company["revenue_growth"] = comp["growth_rate"]
            for r in recs:
                period = period_of(r.get("period"))
                yr = year_of(r.get("period"))
                scope = "company" if r.get("account_type") == "SELSKAP" else (r.get("account_type") or "").lower()
                for fk, label in FIN_FIELDS:
                    v = r.get(fk)
                    if v is None:
                        continue
                    f = fact(org, "financials", f"{label} {yr}", f"{v:,.0f} {r.get('unit') or r.get('currency') or ''}".strip(), sec, period=period, note=f"{label} {yr}: {v:,.0f} {r.get('unit') or r.get('currency') or ''} ({scope} accounts, period {period})".strip())
                    if f:
                        f["year"] = yr
                        f["metric"] = fk
                        f["amount"] = v
                        facts.append(f)

        elif key == "roles" and isinstance(val, dict):
            for r in val.get("roles", []):
                if r.get("inactive"):
                    continue
                who = text(r.get("name"))
                role = ROLE_EN.get(r.get("role_code"), r.get("role"))
                if r.get("role_code") == "DAGL" and not company["ceo"]:
                    company["ceo"] = who
                if r.get("role_code") == "LEDE" and not company["board_chair"]:
                    company["board_chair"] = who
                f = fact(org, "people", role, who, sec, period=r.get("last_changed"),
                         note=f"{role}: {who} (registered role {r.get('role_code')}, last changed {r.get('last_changed') or 'unknown'})")
                if f:
                    facts.append(f)

        elif key == "locations" and isinstance(val, dict):
            locs = val.get("locations", [])
            company["locations_count"] = len(locs)
            for loc in locs:
                f = fact(org, "locations", "Registered workplace", addr(loc.get("address")), sec,
                         note=f"{text(loc.get('name')) or 'Workplace'} (org. no. {loc.get('organisation_number')})")
                if f:
                    facts.append(f)

        elif key == "website" and isinstance(val, dict):
            url = val.get("final_url")
            if url:
                company["website"] = url
                proof = {
                    "orgnr_on_page": "Organisation number shown on the company's page",
                    "jsonld_vatid": "Organisation number in the page's structured data",
                    "signals": "Legal name plus registered details matched on the page",
                }.get(val.get("proof_type"), "Ownership verified on the page")
                f = fact(org, "website", "Website", url, sec,
                         note=f"{proof}: {val.get('proof_page_url') or url}")
                if f:
                    f["source_url"] = val.get("proof_page_url") or sec.get("source_url") or url
                    facts.append(f)
            for link in val.get("social") or val.get("social_links") or []:
                href = link.get("url") if isinstance(link, dict) else link
                if href:
                    f = fact(org, "social", (link.get("platform") if isinstance(link, dict) else None) or "Social profile",
                             href, sec, note="Linked from the verified company website")
                    if f:
                        facts.append(f)

        elif key in ("hiring", "jobs") and isinstance(val, dict):
            for j in val.get("jobs", []):
                if (j.get("status") or "").upper() != "ACTIVE":
                    continue
                occ = ", ".join(o.get("level2") or o.get("level1") or "" for o in j.get("occupation_categories") or [] if o)
                place = ", ".join(text(l.get("city") or l.get("municipality")) or "" for l in j.get("location") or [] if l)
                label = occ or "Job ad"
                value = " · ".join(p for p in [label, place.title() if place else None] if p)
                f = fact(org, "jobs", label, value, sec,
                         period=f"Published {str(j.get('published',''))[:10]}, expires {str(j.get('expires',''))[:10]}",
                         note=text(j.get("title")))
                if f:
                    f["source_url"] = j.get("url") or sec.get("source_url")
                    facts.append(f)
                    company["jobs_count"] += 1

        elif key in ("activity", "public_activity", "registry_changes") and isinstance(val, dict):
            seen_items = set()
            for it in val.get("items", []):
                if not isinstance(it, dict):
                    continue
                if (it.get("date_source") or "").lower() in ("lastmod", "modified", "updated", "feed_updated"):
                    continue  # a modified date is not a publish date
                date = text(it.get("date") or it.get("published"))
                title = text(it.get("title") or it.get("label"))
                url = it.get("url") or sec.get("source_url")
                if not title or not date:
                    continue
                k = (title.lower(), date, url)
                if k in seen_items:
                    continue
                seen_items.add(k)
                if (it.get("title_source") or "").startswith("title from URL"):
                    title = title[:1].upper() + title[1:]
                f = fact(org, "news", "News", title, sec, period=date[:10],
                         note=f"{title} — dated {date[:10]}" + (f" ({it.get('date_source')})" if it.get("date_source") else ""))
                if f:
                    f["source_url"] = url
                    f["source_name"] = source_name(url, sec.get("source_type"))
                    f["date"] = date[:10]
                    facts.append(f)
                    company["news_count"] += 1

        else:
            before = len(facts)
            generic(org, category, "", val, sec, facts)
            added = len(facts) - before
            if category == "jobs":
                company["jobs_count"] += added
            elif category == "news":
                company["news_count"] += added
            elif category == "website" and not company["website"]:
                site = next((f["value"] for f in facts[before:] if str(f["value"]).startswith("http")), None)
                company["website"] = site

    # Social: no independent section; derive an honest state from the website check.
    if any(f["category"] == "social" for f in facts):
        company["sections"]["social"] = "available"
    elif company["sections"].get("website") in ("available", "not_found"):
        company["sections"]["social"] = "not_found"
    else:
        company["sections"]["social"] = company["sections"].get("website") or "not_found"
    if any(f["category"] == "locations" for f in facts):
        company["sections"]["locations"] = "available"
    company["locations_count"] = sum(1 for f in facts if f["category"] == "locations" and f["field"] == "Registered workplace")
    loc_src = next((f for f in facts if f["category"] == "locations" and f["field"] == "Registered workplace"), None)
    if loc_src:
        c = dict(loc_src); c.update(field="Number of Locations", value=str(company["locations_count"]),
                                    excerpt=f"{company['locations_count']} registered workplace(s) in the subunit register")
        facts.append(c)
    for f in facts:
        if f["category"] in ("website", "social") and not f.get("reporting_period") and f.get("retrieved_at"):
            f["reporting_period"] = f"Checked {str(f['retrieved_at'])[:10]}"
        if f["category"] == "website" and not f.get("excerpt"):
            f["excerpt"] = "Ownership verified on the company's page"
    if INDUSTRY_EN and company.get("industry_code"):
        company["industry_text_en"] = INDUSTRY_EN.get(company["industry_code"])
    company["news_count"] = sum(1 for f in facts if f["category"] == "news")
    company["jobs_count"] = sum(1 for f in facts if f["category"] == "jobs")

    # A section marked available must show at least one fact; otherwise it was
    # only supported by items we refuse to publish (e.g. modified-date "news").
    by_cat: dict[str, int] = {}
    for f in facts:
        by_cat[f["category"]] = by_cat.get(f["category"], 0) + 1
    for cat, state in list(company["sections"].items()):
        if state == "available" and by_cat.get(cat, 0) == 0 and cat in ("news", "jobs", "website", "social"):
            company["sections"][cat] = "not_found"
    return company, facts


INDUSTRY_EN: dict[str, str] = {}


def load_industry_en(path: str) -> None:
    """Load code -> English name from an SSB KLASS-style JSON (any nesting)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    def walk(x):
        if isinstance(x, dict):
            code, name = x.get("code"), x.get("name") or x.get("shortName")
            if isinstance(code, str) and isinstance(name, str):
                INDUSTRY_EN.setdefault(code, name)
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(data)


def main() -> None:
    if len(sys.argv) == 4:
        load_industry_en(sys.argv[3])
        print("english industry names:", len(INDUSTRY_EN))
        sys.argv = sys.argv[:3]
    if len(sys.argv) != 3:
        sys.exit("usage: python export_for_jbox.py profiles.jsonl out_dir")
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    out.mkdir(parents=True, exist_ok=True)
    companies, facts, seen = [], [], set()
    with src.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            profile = json.loads(line)
            org = profile.get("organisation_number")
            if not org or org in seen:
                continue
            seen.add(org)
            c, f = convert(profile)
            companies.append(c)
            facts.extend(f)
    (out / "companies.json").write_text(json.dumps(companies, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    (out / "facts.json").write_text(json.dumps(facts, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    cats: dict[str, int] = {}
    for f in facts:
        cats[f["category"]] = cats.get(f["category"], 0) + 1
    print(f"companies: {len(companies)}  facts: {len(facts)}")
    print("facts by category:", json.dumps(cats))
    sec_states: dict[str, dict[str, int]] = {}
    for c in companies:
        for k, s in c["sections"].items():
            sec_states.setdefault(k, {}).setdefault(s or "none", 0)
            sec_states[k][s or "none"] += 1
    print("section states:", json.dumps(sec_states))


if __name__ == "__main__":
    main()
