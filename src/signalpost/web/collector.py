from ..workers import offload
import html
import json
import asyncio
import re
from urllib.parse import urlsplit, urlunsplit
from ..budget import SourceFailure
from ..models.envelope import Error
from ..models.evidence import digest
import xml.etree.ElementTree as ET
from ..sources.extract import Section, Source, add, missing, response_source
from .candidates import generate, context_from_bulk, legal_name, Candidate, GENERIC, NOMINATED, RECOVERY
from .html import Page
from .policy import domain, normalize_url, SOCIAL, DIRECTORIES, FREE_MAIL, extract
from .proof import score, phone, extract_entity_cards, find_containing_card
from .social import discover, profile_url, attributed, observed_profiles, matches_profile, company_names


STRONG_CANDIDATE_ORIGINS = frozenset({'registry_website', 'subunit_registry_website', 'wikidata_website'})

def extract_sitemap_domains(xml_body, legal_nm, brand_nm):
    raw = xml_body.decode('utf-8', errors='replace')
    if re.search(r'<!\s*(?:DOCTYPE|ENTITY)', raw, re.I): return []
    try: root = ET.fromstring(raw)
    except Exception: return []
    tokens = [t.lower() for t in legal_name(legal_nm).split() if t not in GENERIC and len(t) >= 4]
    if brand_nm: tokens.append(brand_nm.lower())
    urls = []
    for elem in root.iter():
        tag = elem.tag.rsplit('}', 1)[-1]
        if tag == 'loc' and elem.text:
            urls.append(elem.text.strip())
    discovered = []
    seen = set()
    for u in urls:
        norm = normalize_url(u)
        d = domain(norm) if norm else ''
        if not d or d in seen or d in SOCIAL | DIRECTORIES | FREE_MAIL: continue
        d_clean = re.sub(r'[^a-z0-9]', '', d.lower().split('.')[0])
        if any(tok in d_clean for tok in tokens):
            seen.add(d)
            discovered.append((norm, d))
            if len(discovered) >= 5: break
    return discovered


def extract_rss_domains(xml_body, legal_nm, brand_nm):
    raw = xml_body.decode('utf-8', errors='replace')
    if re.search(r'<!\s*(?:DOCTYPE|ENTITY)', raw, re.I): return []
    try: root = ET.fromstring(raw)
    except Exception: return []
    tokens = [t.lower() for t in legal_name(legal_nm).split() if t not in GENERIC and len(t) >= 3]
    if brand_nm: tokens.append(brand_nm.lower())
    discovered = []
    seen = set()
    for item in root.iter():
        tag = item.tag.rsplit('}', 1)[-1]
        if tag in ('item', 'entry'):
            link = next((e.text for e in item if e.tag.rsplit('}', 1)[-1] == 'link' and e.text), None)
            if not link:
                link = next((e.get('href') for e in item if e.tag.rsplit('}', 1)[-1] == 'link' and e.get('href')), None)
            title = next((e.text for e in item if e.tag.rsplit('}', 1)[-1] == 'title' and e.text), '') or ''
            desc = next((e.text for e in item if e.tag.rsplit('}', 1)[-1] in ('description', 'summary') and e.text), '') or ''
            text = f'{title} {desc}'.lower()
            if any(tok in text for tok in tokens) and link:
                norm = normalize_url(link)
                d = domain(norm) if norm else ''
                if d and d not in seen and d not in SOCIAL | DIRECTORIES | FREE_MAIL:
                    seen.add(d)
                    discovered.append((norm, d))
                    if len(discovered) >= 5: break
    return discovered


def extract_public_brand(page: Page, legal_name_val: str | None) -> str | None:
    """
    Extracts verified public brand from page, withholding generic storefront taglines,
    legal/store suffixes, and exact duplicates of the registered legal name.
    """
    candidate_brand = page.meta.get("og:site_name") or page.meta.get("og:sitename")
    if candidate_brand:
        candidate_brand = html.unescape(candidate_brand).strip()
    else:
        parts = [html.unescape(p).strip() for p in re.split(r"\s+[|â€“-]\s+", page.title) if p.strip()]
        if parts:
            generic_store_words = {"nettbutikk", "fiskeutstyr", "bÃ¥tutstyr", "butikk", "webshop", "forside", "hjem", "velkommen", "home", "shop", "online"}
            p0_lower = parts[0].lower()
            if any(w in p0_lower for w in generic_store_words) and len(parts) > 1:
                candidate_brand = parts[-1]
            else:
                candidate_brand = parts[0]

    if not candidate_brand:
        return None

    cleaned_brand = re.sub(r"\s*[-â€“|:]?\s*(?:org(?:anisasjons)?\.?\s*nr\.?|organisasjonsnummer)\s*[:.]?\s*\d{9}\b.*$", "", candidate_brand, flags=re.I).strip(" .,-")
    cleaned_brand = re.sub(r"\s*[-â€“|:]\s*(?:nettbutikk|butikk|webshop|forside|hjem|velkommen|home|shop|store)\b.*$", "", cleaned_brand, flags=re.I).strip(" .,-")
    norm_b = legal_name(cleaned_brand)
    generic_brands = {
        "home", "hjem", "welcome", "velkommen", "kontakt", "contact",
        "kontakt oss", "contact us", "privacy policy", "personvern",
        "vilkar", "vilkar og betingelser", "terms", "terms of service",
        "forside", "hjemmeside"
    }
    is_generic_tagline = (
        re.search(r"\b(?:din|ditt)\s+\w+", cleaned_brand, re.I) is not None
        or re.search(r"\b(?:kontakt|contact)\b", cleaned_brand, re.I) is not None
        or re.search(r"\b(?:vilk[aÃ¥]r|betingelser|privacy|personvern)\b", cleaned_brand, re.I) is not None
        or (re.search(r"\bi\s+[A-ZÃ†Ã˜Ã…a-zÃ¦Ã¸Ã¥]{3,}\b", cleaned_brand) is not None and len(cleaned_brand.split()) > 3)
    )
    if (cleaned_brand and len(cleaned_brand) <= 100 and "\ufffd" not in cleaned_brand
            and norm_b not in generic_brands
            and not is_generic_tagline
            and norm_b != legal_name(legal_name_val)):
        return cleaned_brand
    return None


def registry_context(envelope, bulk, blobs):
    if bulk is not None:
        row, source = bulk
        return context_from_bulk(row), source, "row:" + envelope.organisation_number + "/column:hjemmeside"
    reference = next((e for e in envelope.evidence if e.locator == "/navn"), None)
    if reference is None:
        return {}, None, ""
    body = (blobs.directory / reference.content_sha256).read_bytes()
    data = json.loads(body)
    address = data.get("forretningsadresse") or {}
    context = {"name": data.get("navn"), "website": data.get("hjemmeside"), "email": data.get("epostadresse"),
               "phone": data.get("telefon"), "municipality": address.get("kommune"), "street": address.get("adresse"),
               "postcode": address.get("postnummer"), "city": address.get("poststed")}
    return context, Source(reference.source_url, body, reference.content_sha256, reference.retrieved_at), "/hjemmeside"


def publish(section, response, org, field, value, locator, span):
    if not span or span not in response.body.decode("utf8", errors="replace") or len(span) > 300:
        raise SourceFailure("invalid_span")
    add(section, response_source(response), org, "website", field, value, locator, span=span,
        source_class="company_owned", method="signalpost.website.v1")


def followup_links(page):
    patterns = [r'kontakt|contact',r'om[- ]oss|about',r'personvern|privacy|vilk[Ã¥a]r|terms|impressum']
    ranked=[]
    for link in page.links:
        text=urlsplit(link.href).path+' '+link.text
        priority=next((i for i,p in enumerate(patterns) if re.search(p,text,re.I)),None)
        if priority is not None: ranked.append((priority,link.href))
    return list(dict.fromkeys(url for _,url in sorted(ranked,key=lambda x:x[0])))


# Pages where Norwegian companies state their organisation number. They are tried
# after the links found on the home page; proof rules apply to them unchanged.
FALLBACK_PROOF_PATHS = ('/kontakt', '/om-oss', '/about', '/personvern', '/impressum', '/kontakt-oss', '/privacy-policy', '/om', '/contact', '/privacy', '/personvernerklaering')
FOLLOWUP_PAGES = 3


def proof_page_targets(page, base_url, limit=FOLLOWUP_PAGES):
    base = urlsplit(base_url)
    fixed = [urlunsplit((base.scheme, base.netloc, path, '', '')) for path in FALLBACK_PROOF_PATHS]
    targets = []
    for target in followup_links(page) + fixed:
        target = normalize_url(target)
        if target and urlsplit(target).hostname == base.hostname and target not in targets:
            targets.append(target)
    return targets[:limit]


def previous_nomination(previous, context, units):
    if not previous:
        return None, None
    row = previous if 'claims' in previous else previous.get('profile', {})
    claims = row.get('claims', [])
    old_registry = next((c['value'] for c in claims if c['field'] == 'identity.registered_website' and c['availability'] == 'available'), None)
    if normalize_url(old_registry) != normalize_url(context.get('website')):
        return None, None  # A new registry declaration takes precedence.
    claim = next((c for c in claims if c['field'] == 'official_website' and c['availability'] == 'available'), None)
    value = claim.get('value', {}) if claim else {}
    if value.get('identity_level') != 'VERIFIED' or not value.get('candidate_origin'):
        return None, None
    branch = value.get('matched_via_subunit')
    if branch and branch not in units:
        return None, None  # Historical scope cannot authorize a branch today.
    url = normalize_url(value.get('final_url'))
    proof_url = normalize_url(value.get('proof_page_url'))
    if not url:
        return None, None
    return Candidate(url, domain(url), value['candidate_origin'], branch), proof_url


async def fetch(org, envelope, bulk, http, previous=None, nav_index=None, retry_candidates=None):
    context, registry_source, registry_locator = await offload(registry_context,envelope,bulk,http.blobs)
    context['nace']=next((str(c.value.get('kode','')) for c in envelope.claims if c.field=='identity.nace1' and isinstance(c.value,dict)),'')
    round2=envelope.run.refresh.setdefault('recall_round2',{'candidates':[]})
    units={c.value['organisation_number']:{'name': c.value.get('name'), 'address':c.value.get('address')} for c in envelope.claims
           if c.field.startswith('subunits.unit.') and c.availability=='available' and isinstance(c.value,dict)}
    for c in envelope.claims:
        if c.availability!='available' or not c.field.startswith('subunits.detail.'):continue
        _,_,unit,field=c.field.split('.',3)
        if unit in units and field in {'registered_website','registered_email','registered_phone','registered_mobile'}:
            units[unit][{'registered_website':'website','registered_email':'email','registered_phone':'phone','registered_mobile':'mobile'}[field]]=c.value
    context['subunits']=[{'orgnr':unit,**data} for unit,data in units.items()]
    nav_homepages = list(context.get('nav_homepages') or [])
    active_nav = nav_index or getattr(http, 'nav_index', None)
    if active_nav is not None and hasattr(active_nav, 'ads'):
        for ad_item in active_nav.ads.get(org, []):
            val = getattr(ad_item, 'value', ad_item) if isinstance(ad_item, (dict, object)) else {}
            val_dict = val if isinstance(val, dict) else getattr(val, '__dict__', {})
            hp = val_dict.get('employer_homepage')
            if hp and val_dict.get('employer_orgnr') == org:
                nav_homepages.append({'url': hp, 'subunit_orgnr': None})
        for unit_org in units:
            for ad_item in active_nav.ads.get(unit_org, []):
                val = getattr(ad_item, 'value', ad_item) if isinstance(ad_item, (dict, object)) else {}
                val_dict = val if isinstance(val, dict) else getattr(val, '__dict__', {})
                hp = val_dict.get('employer_homepage')
                if hp and val_dict.get('employer_orgnr') == unit_org:
                    nav_homepages.append({'url': hp, 'subunit_orgnr': unit_org})
    for c in envelope.claims:
        if c.family == 'hiring' and c.availability == 'available' and isinstance(c.value, dict):
            hp = c.value.get('employer_homepage')
            if hp and c.value.get('employer_orgnr') in {org, *units}:
                emp_org = c.value.get('employer_orgnr')
                sub = emp_org if (emp_org and emp_org != org and emp_org in units) else None
                nav_homepages.append({'url': hp, 'subunit_orgnr': sub})
    context['nav_homepages'] = nav_homepages
    from .recall import annual_domains
    context['annual_report_domains'] = await offload(annual_domains, envelope, http.blobs)
    from .wikidata import websites
    context['wikidata_homepages'] = websites(getattr(http, 'wikidata_index', {'records':{}}), org)
    from .search import active_for_search
    context['active_for_search'] = active_for_search(envelope)
    section = Section(state="not_available")
    if registry_source and (social := profile_url(normalize_url(context.get("website")) or "")) and matches_profile(social,company_names(context)):
        add(section, registry_source, org, "website", "registry_social." + digest(social)[:20],
            {"url": social, "platform": domain(social), "verification": "registry_asserted"}, registry_locator)
    candidates = generate(context)
    if retry_candidates is not None:candidates=list(retry_candidates)
    refresh_candidate, refresh_proof = previous_nomination(previous, context, units)
    prior_data=(previous or {}) if not previous or 'claims' in previous else previous.get('profile',{})
    previously_verified=any(c.get('field')=='official_website' and c.get('availability')=='available' and isinstance(c.get('value'),dict) and c['value'].get('identity_level')=='VERIFIED' for c in prior_data.get('claims',[]))
    if refresh_candidate:
        candidates = [refresh_candidate] + [c for c in candidates if c.url != refresh_candidate.url]
    from .round2 import registered_leaders
    leaders = registered_leaders(envelope.claims)
    proved = set()
    successes = []
    attempts = []
    blocked = False
    ambiguous = False
    budget_hit = None
    source_unavailable = False
    registry_failed = False
    refresh_failed = False
    checked = set()
    refuted_previous_website = False
    from .brands import actual_names,candidates as brand_candidates
    brand_names=actual_names(envelope,context,http.blobs) if retry_candidates is None else []
    brand_support={}
    async def nominations():
        for candidate in candidates:yield candidate
        if not successes and retry_candidates is None:
            earlier=envelope.run.refresh.get('brand_candidates',[])
            remaining=max(0,4-len(earlier))
            for candidate,support in brand_candidates(brand_names,{c.domain for c in candidates}|{c['domain'] for c in earlier})[:remaining]:
                brand_support[candidate.domain]=support
                envelope.run.refresh.setdefault('brand_candidates',[]).append({'domain':candidate.domain,**support})
                yield candidate
        search=getattr(http,'search',None)
        if not successes and search and retry_candidates is None:
            existing={c.domain for c in candidates}
            for candidate in await search.nominate(org,context,http):
                if candidate.domain not in existing:yield candidate
    async for candidate in nominations():
        pages = []
        best = None
        entry={'domain':candidate.domain,'origin':candidate.origin,'subunit_orgnr':candidate.subunit_orgnr,'fetched':False,'accepted':False}
        round2['candidates'].append(entry)
        try:
            from .recall import shared_owners
            owners = shared_owners(candidate.domain) | set(getattr(http, 'domain_owners', {}).get(candidate.domain, []))
            if len(owners - {org}) >= 2:
                attempts.append({'domain':candidate.domain,'origin':candidate.origin,'level':'REJECT','reason':'shared_registry_domain'})
                ambiguous = True
                continue
            response = await http.candidate(candidate, org, proved)
            redirected = domain(response.url) != candidate.domain
            if redirected:
                if candidate.domain in brand_support:brand_support[domain(response.url)]=brand_support[candidate.domain]
                from dataclasses import replace
                candidate = replace(candidate, url=response.url, domain=domain(response.url))
            if response.status in (401, 403, 429):
                raise SourceFailure("http_blocked", f"HTTP {response.status}")
            if not 200 <= response.status < 300:
                if response.status >= 500:
                    source_unavailable = True
                attempts.append({"domain": candidate.domain, "level": "LOW", "reason": f"http_{response.status}"})
                continue
            page = await offload(Page,response.body,response.url)
            entry['fetched']=True
            from .recall import redirect_names_company
            if redirected and not redirect_names_company(page, org, context):
                attempts.append({'domain':candidate.domain,'origin':candidate.origin,'level':'REJECT','reason':'redirect_without_company_identity','title':page.title})
                continue
            checked.add(candidate.domain)
            proof = await offload(candidate_proof,page,org,context,candidate,leaders,http.config)
            if retry_candidates is None and proof.level in {'VERIFIED','HIGH','MEDIUM'}:
                from .round2 import named
                if named(page,context.get('name')):
                    for name in [page.meta.get('og:site_name'),*re.split(r'\s+[|–—]\s+',page.title)]:
                        if name and legal_name(name)!=legal_name(context.get('name')):
                            span=page.name_span(name) or page.span_for(name)
                            if span and len(span)<=300 and span in response.body.decode('utf8',errors='replace'):
                                support=Section()
                                add(support,response_source(response),org,'website','brand_nomination',name,'/brand-nomination',span=span,source_class='company_owned')
                                section.evidence+=support.evidence
                                brand_names.append((name,'fetched_company_identity',[e.id for e in support.evidence]))
            from .round2 import unique_eligible,unique_registry
            if candidate.origin!='brand_name' and proof.level in {'LOW','MEDIUM'} and getattr(http.config,'website_unique_no',True) and unique_eligible(page,context,leaders):
                entry['unique_candidate']=True
                support=await unique_registry(org,context,http)
                if support:
                    section.evidence.extend(support)
                    from .proof import Proof
                    proof=Proof('VERIFIED','unique_no_corroborated',['registry_unique_name','name_in_identity','registry_corroboration'],4,token=legal_name(context.get('name')))
                    proof.rule='C'
            pages.append((response, page))
            best = (proof, response, page)
            if proof.level == "BLOCKED":
                raise SourceFailure("block_page")
            if (candidate is refresh_candidate and refresh_proof and refresh_proof != response.url
                    and domain(refresh_proof) == candidate.domain and proof.level != 'REJECT'):
                try:
                    checked_response = await http.get(refresh_proof, org, candidate.domain, proved)
                    if checked_response.status == 200:
                        checked_page = await offload(Page, checked_response.body, checked_response.url)
                        checked_proof = await offload(candidate_proof, checked_page, org, context, candidate, leaders, http.config)
                        if checked_proof.level == 'VERIFIED':
                            pages.append((checked_response, checked_page))
                            best = (checked_proof, checked_response, checked_page)
                            proof, response, page = best
                except SourceFailure as exc:
                    attempts.append({'domain': candidate.domain, 'origin': candidate.origin,
                                     'reason': exc.code, 'page': refresh_proof})
            # Owner conflicts on any checked page cannot be rescued by another
            # page on that domain. Up to three same-domain proof pages are checked.
            vetoes = {'foreign_orgnr','different_legal_entity','hosting_default','parked','shared_registry_domain','placeholder','frameset_placeholder','provider_industry_mismatch'}
            if proof.reason not in vetoes:
                seen = {response.url}
                limit = 5  # Preserve the previous selection before adding pages.
                targets=proof_page_targets(page,response.url,limit=limit)
                if proof.level!='VERIFIED' and getattr(http.config,'website_proof_discovery',True):
                    from .round2 import proof_targets
                    original=set(targets)
                    targets=await proof_targets(page,response.url,http,org,targets)
                    entry['discovered_proof_targets']=[u for u in targets if u not in original]
                # Never let a new path displace an old linked/sitemap/fixed
                # target. The existing stop-after-proof and pooled caps apply.
                previous_targets=list(targets)
                additions=[u for u in proof_page_targets(page,response.url,limit=32)
                           if u not in previous_targets][:2]
                targets=previous_targets+additions
                entry['additional_proof_targets']=additions
                for position,target in enumerate(targets):
                    if position>=FOLLOWUP_PAGES and best[0].level=='VERIFIED':
                        break
                    if target in seen or domain(target) != domain(response.url):
                        continue
                    seen.add(target)
                    try:
                        extra = await http.get(target, org, candidate.domain, proved)
                    except SourceFailure as exc:
                        attempts.append({'domain': candidate.domain, 'reason': exc.code, 'page': target})
                        if exc.code in {'website_budget_exhausted', 'budget_exhausted', 'deadline'}:
                            budget_hit = exc.code
                            break
                        continue
                    if extra.status != 200:
                        continue
                    extra_page = await offload(Page, extra.body, extra.url)
                    extra_proof = await offload(candidate_proof, extra_page, org, context, candidate, leaders, http.config)
                    if candidate.origin!='brand_name' and extra_proof.level in {'LOW','MEDIUM'} and getattr(http.config,'website_unique_no',True) and unique_eligible(extra_page,context,leaders):
                        entry['unique_candidate']=True
                        support=await unique_registry(org,context,http)
                        if support:
                            section.evidence.extend(support)
                            from .proof import Proof
                            extra_proof=Proof('VERIFIED','unique_no_corroborated',['registry_unique_name','name_in_identity','registry_corroboration'],4,token=legal_name(context.get('name')))
                            extra_proof.rule='C'
                    if extra_proof.level == 'BLOCKED':
                        continue
                    pages.append((extra, extra_page))
                    entry['proof_pages_fetched']=entry.get('proof_pages_fetched',0)+1
                    if extra_proof.reason in vetoes:
                        best = (extra_proof, extra, extra_page)
                        break
                    ranks = {'REJECT': -1, 'BLOCKED': -1, 'LOW': 0, 'MEDIUM': 1, 'REGISTRY_DECLARED': 2, 'HIGH': 3, 'VERIFIED': 4}
                    if ranks[extra_proof.level] > ranks[best[0].level]:
                        best = (extra_proof, extra, extra_page)
            proof, response, page = best
            entry.update(proof_type=proof.proof_type,rule=getattr(proof,'rule',None),reason=proof.reason)
            attempts.append({"domain": candidate.domain, "level": proof.level, "points": proof.points, "signals": proof.signals, "origin": candidate.origin, "reason": proof.reason, 'title':page.title, 'proof_page_url':response.url})
            is_prev_domain = bool(refresh_candidate and (candidate is refresh_candidate or candidate.domain == refresh_candidate.domain or domain(response.url) == refresh_candidate.domain))
            if is_prev_domain and (proof.reason == "foreign_orgnr" or (proof.level == "REJECT" and proof.reason == "foreign_orgnr")):
                refuted_previous_website = True
            if candidate is refresh_candidate and proof.level != 'VERIFIED':
                continue  # Previous metadata nominates; only fresh exact proof publishes.
            if candidate.origin in {'nav_employer_homepage', 'subunit_nav_employer_homepage'} and proof.level != 'VERIFIED':
                continue  # NAV employer homepage nominates; only fresh exact proof publishes.
            if proof.level in {"VERIFIED", "HIGH"} or (proof.level=='REGISTRY_DECLARED' and http.config.registry_declared):
                entry['accepted']=True
                final_domain = domain(response.url)
                successes.append((candidate, proof, response, page, pages))
                if proof.level == "VERIFIED":
                    proved.add(final_domain)
                    if http.config.website_stop_after_verified:
                        break
            elif proof.level in {"MEDIUM", 'REGISTRY_DECLARED'}:
                ambiguous = True
            if retry_candidates is None and proof.level != 'REJECT' and not successes and http.counts.get(org, 0) + 2 <= http.discovery_cap(org):
                legal_nm = context.get('name')
                brand_nm = context.get('brand')
                metrics = getattr(http, 'discovery_metrics', None)
                if metrics is None:
                    http.discovery_metrics = {'sitemaps_found': 0, 'sitemap_candidates': 0, 'rss_feeds_found': 0, 'rss_candidates': 0}
                    metrics = http.discovery_metrics
                try:
                    sm_resp = await http.get(f'https://{candidate.domain}/sitemap.xml', org, candidate.domain, xml=True)
                    if sm_resp.status == 200:
                        metrics['sitemaps_found'] += 1
                        for u, d in extract_sitemap_domains(sm_resp.body, legal_nm, brand_nm):
                            if d not in checked and d not in {c.domain for c in candidates}:
                                metrics['sitemap_candidates'] += 1
                                candidates.append(Candidate(u, d, 'sitemap'))
                except SourceFailure: pass
                for feed_path in ('/feed.xml', '/rss.xml', '/feed/', '/blog/feed.xml'):
                    if successes or http.counts.get(org, 0) >= http.discovery_cap(org): break
                    try:
                        rss_resp = await http.get(f'https://{candidate.domain}{feed_path}', org, candidate.domain, xml=True)
                        if rss_resp.status == 200:
                            metrics['rss_feeds_found'] += 1
                            for u, d in extract_rss_domains(rss_resp.body, legal_nm, brand_nm):
                                if d not in checked and d not in {c.domain for c in candidates}:
                                    metrics['rss_candidates'] += 1
                                    candidates.append(Candidate(u, d, 'rss'))
                            break
                    except SourceFailure: pass
        except SourceFailure as exc:
            is_authoritative = candidate.origin in STRONG_CANDIDATE_ORIGINS or (refresh_candidate and candidate.domain == refresh_candidate.domain)
            known_source = is_authoritative
            declared_absent=not previously_verified and known_source and exc.code=='no_such_domain' and getattr(exc,'declared_domain_absent',False)
            if declared_absent:
                envelope.run.refresh.setdefault('website',{}).setdefault('declared_absent_domains',[]).append(candidate.domain)
                section.errors.append(Error(section='website',code='declared_domain_absent',message='declared domain does not exist'))
            absent_guess = exc.code == 'no_such_domain' and (not known_source or declared_absent)
            if known_source and not absent_guess and exc.code in {'website_timeout','website_connect_error','website_tls_error','website_http_5xx','dns_timeout','dns_error','dns_servfail','dns_unavailable','body_cap','no_such_domain','redirect_limit','content_type'}:
                source_unavailable = True
                if known_source:
                    registry_failed = True
                if refresh_candidate and candidate.domain == refresh_candidate.domain:
                    refresh_failed = True
            attempts.append({"domain": candidate.domain,'origin':candidate.origin, "level": "BLOCKED" if is_authoritative and exc.code in {"robots", "robots_unavailable", "http_blocked", "block_page"} else "LOW", "reason": exc.code, "candidate_not_reachable": not known_source and exc.code in {"website_timeout","website_connect_error","website_tls_error","dns_timeout","dns_error","dns_servfail","dns_unavailable","no_such_domain","robots","robots_unavailable","http_blocked","block_page"}})
            if exc.code in {"robots", "robots_unavailable", "http_blocked", "block_page"}:
                blocked = blocked or is_authoritative
                if is_authoritative:
                    section.errors.append(Error(section="website", code=exc.code, message=f"{candidate.domain}: access refused"))
            if exc.code in {"website_budget_exhausted", "budget_exhausted", "deadline"}:
                # Exhausting speculative discovery cannot invalidate a checked absence.
                budget_hit = exc.code if is_authoritative else None
                break
    unique = {}
    for result in successes:
        root = domain(result[2].url)
        if root not in unique or result[1].level == "VERIFIED":
            unique[root] = result
    choices = list(unique.values())
    if len(choices) > 1:
        verified = [x for x in choices if x[1].level == "VERIFIED"]
        if verified:
            choices = verified
    if len(choices) != 1:
        if refuted_previous_website:
            envelope.run.refresh.setdefault('website', {})['refuted_previous_website'] = True
            section.errors.append(Error(section='website', code='foreign_orgnr_on_previous_domain',
                                        message=f'Previous website {refresh_candidate.domain} refuted by foreign organization number'))
        section.state = 'ambiguous' if len(choices)>1 or ambiguous else 'blocked' if blocked else 'failed' if registry_failed or refresh_failed or budget_hit else 'not_available'
        if source_unavailable:
            section.errors.append(Error(section="website", code="website_source_unavailable", message="A candidate source could not be checked"))
        if budget_hit:
            section.errors.append(Error(section="website", code=budget_hit, message="Website work ended at configured budget"))
        section.errors.append(Error(section="website", code="website_candidates", message=json.dumps(attempts+http.attempts.get(org,[]), ensure_ascii=False)))
        return section
    result=await offload(publish_result,org,envelope,http,section,choices,attempts,context)
    if choices[0][0].origin=='brand_name':
        support=brand_support.get(choices[0][0].domain,{})
        refs=support.get('evidence_ids',[])
        for claim in result.claims:
            if claim.field=='official_website':claim.evidence_ids+=refs
        result.evidence.extend(e for e in envelope.evidence if e.id in refs)
    return result


def extract_contacts_and_social(section, org, web_claim, pages, context=None, envelope=None):
    """
    Extracts contacts and verified social profiles from website pages.
    Enforces corporate entity card attribution and filters sibling/group accounts on multi-entity group sites.
    """
    context = context or {}
    web_val = web_claim.value if hasattr(web_claim, "value") and isinstance(web_claim.value, dict) else (web_claim if isinstance(web_claim, dict) else {})
    other_orgnrs = web_val.get("other_orgnrs") or []
    is_group = bool(other_orgnrs) or web_val.get("relationship_note") == "group_site"

    subunits = set()
    if envelope and hasattr(envelope, "claims"):
        for c in envelope.claims:
            if c.field.startswith("subunits.unit.") and isinstance(c.value, dict) and c.value.get("orgnr"):
                subunits.add(c.value.get("orgnr"))
    if context.get("subunits"):
        subunits.update(unit['orgnr'] for unit in context["subunits"] if unit.get('orgnr'))

    proof_url = web_val.get("final_url") or web_val.get("proof_page_url") or ""
    target_domain = domain(proof_url) if proof_url else (domain(pages[0][0].url) if pages else "")

    social_seen, contact_seen = set(), set()
    for source_response, source_page in pages:
        if domain(source_response.url) != target_domain:
            continue
        cards = extract_entity_cards(source_page.raw) if is_group else []
        from .entity_scope import foreign_entity_page
        if foreign_entity_page(source_page, org, context.get('name'), check_ids=not is_group):
            continue
        for url, source_span in ({} if is_group else attributed(source_page, web_val, context)).items():
            if url not in social_seen:
                if is_group:
                    p_path = urlsplit(url).path.rstrip("/").lower()
                    legal_nm = (context.get("name") or "").lower()
                    if any(term in p_path for term in ("group", "holding", "gruppe")) and not any(term in legal_nm for term in ("group", "holding", "gruppe")):
                        continue
                    pos = source_page.raw.find(url)
                    if pos >= 0:
                        c = find_containing_card(cards, pos)
                        if c and c.is_sibling(org, other_orgnrs, subunits):
                            continue
                publish(section, source_response, org, "social_profile." + digest(url)[:20], {"url": url, "platform": domain(url)}, "company-link:" + url, source_span)
                section.claims[-1].reasons['relationship'] = 'Company-owned profile linked from verified website'
                social_seen.add(url)
        contacts = []
        for link in source_page.links:
            if link.href.startswith("tel:") and (number := phone(link.href[4:])):
                contacts.append(("phone", number, link.span))
            if link.href.startswith("mailto:"):
                address = link.href[7:].split("?", 1)[0].strip()
                if address.rsplit("@", 1)[-1].lower() == target_domain:
                    contacts.append(("email", address, link.span))
        for match in re.finditer(r"[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", source_page.visible):
            address = match.group()
            if address.rsplit("@", 1)[-1].lower() == target_domain:
                contacts.append(("email", address, source_page.span_for(address)[:150]))
        for match in re.finditer(r"(?:telefon|tlf|phone)\s*:?\s*((?:\+47|0047)?[ .()0-9-]{8,20})", source_page.visible, re.I):
            if number := phone(match.group(1)):
                contacts.append(("phone", number, source_page.span_for(match.group(1))[:150]))
        for kind, contact, source_span in contacts:
            if (kind, contact.casefold()) not in contact_seen:
                if is_group:
                    pos = source_page.raw.find(contact)
                    if pos >= 0:
                        c = find_containing_card(cards, pos)
                        if c:
                            if c.is_sibling(org, other_orgnrs, subunits) or not c.matches_org(org, context, subunits):
                                continue
                        else:
                            continue
                    else:
                        continue
                publish(section, source_response, org, "contact." + kind + "." + digest(contact.casefold())[:20], contact, "contact:" + contact, source_span)
                contact_seen.add((kind, contact.casefold()))


def candidate_proof(page,org,context,candidate,leaders,config=None):
    options = dict(suffix_contact=getattr(config,"website_suffix_contact_proof",False),
                   domain_location=getattr(config,"website_domain_location_proof",False),
                   nominated_contacts=candidate.origin in NOMINATED)
    context = {**context, 'allowed_orgnrs':{org, *[u['orgnr'] for u in context.get('subunits', [])]}}
    from .round2 import declared_score
    enabled=getattr(config,'website_email_declaration',True) if candidate.origin=='registry_email' else getattr(config,'website_subunit_declaration',True)
    proof=declared_score(page,org,context,candidate.origin,leaders,options,enabled)
    if candidate.subunit_orgnr and (proof.level not in {'VERIFIED','BLOCKED'} or proof.proof_type=='registry_declared_hard_contact_tier_b'):
        unit_context = next((u for u in context.get('subunits', []) if u['orgnr']==candidate.subunit_orgnr), {})
        address = unit_context.get('address') or {}
        unit_context = {**context, **unit_context, 'street':address.get('adresse'), 'postcode':address.get('postnummer'), 'city':address.get('poststed'), 'municipality':address.get('kommune')}
        unit=declared_score(page,candidate.subunit_orgnr,unit_context,candidate.origin,leaders,options,enabled)
        if unit.level=='VERIFIED' and (proof.level!='VERIFIED' or unit.proof_type!='registry_declared_hard_contact_tier_b'):
            unit.subject_orgnr = candidate.subunit_orgnr
            return unit
    return proof


def publish_result(org,envelope,http,section,choices,attempts,context):
    candidate, proof, response, page, pages = choices[0]
    from .entity_scope import unproven_global_site
    if proof.proof_type=='registry_declared_name_tier_a' and unproven_global_site([p for _,p in pages],org,context,response.url):
        envelope.run.refresh.setdefault('website',{}).update(website_reason='group website',group_site=True)
        return missing('website','group_site','group website',state='ambiguous')
    p = urlsplit(response.url)
    root_url = urlunsplit((p.scheme, p.netloc, "", "", ""))
    matched=getattr(proof,'subject_orgnr',None) or org
    contact_proofs={'legal_name_and_registry_contact','legal_name_without_suffix_and_two_contacts',
                    'domain_legal_name_and_registry_location','nominated_two_independent_signals',
                    'registry_declared_name_tier_a','registry_declared_hard_contact_tier_b','unique_no_corroborated'}
    span = page.proof_span(matched) if proof.level == "VERIFIED" and proof.proof_type not in contact_proofs else (page.name_span(proof.token) or page.span_for(proof.token))
    if not span:
        return missing("website", "no_localized_proof", state="ambiguous")
    from .proof import orgnrs
    group_site = bool(proof.other_orgnrs) or any(len(orgnrs(p.visible)) >= 3 for _, p in pages)
    value = {"final_url": root_url, "transport_scheme": p.scheme,
             "identity_level": proof.level, "proof_type": proof.proof_type,
             "proof_page_url": response.url, "signals": proof.signals, "points": proof.points,
             "candidate_origin": candidate.origin, "relationship_note": "group_site" if group_site else None,
             "other_orgnrs": proof.other_orgnrs}
    value['publication_tier'] = 'B' if proof.proof_type == 'registry_declared_hard_contact_tier_b' else 'A'
    value['content_allowed'] = value['publication_tier'] == 'A'
    if matched != org and matched in {u['orgnr'] for u in context.get('subunits', [])}:
        value['matched_via_subunit']=matched
    publish(section, response, org, "official_website", value, "identity-proof:" + matched, span)
    if proof.proof_type=='registry_declared_name_tier_a' and extract(response.url).suffix!='no':
        # A fetched About page may supply the Norwegian legal identity even
        # when the selected homepage proof was only the shorter brand name.
        # Retain that support so the final/carry-forward guard sees it too.
        for support_response,support_page in pages:
            support_span=support_page.name_span(str(context.get('name') or ''))
            if support_span and not unproven_global_site([support_page],org,context,support_response.url):
                support=Section()
                add(support,response_source(support_response),org,'website','website_entity_scope_support',context['name'],
                    '/norwegian-entity',span=support_span,source_class='company_owned')
                section.evidence.extend(support.evidence)
                section.claims[-1].evidence_ids.extend(e.id for e in support.evidence)
    if candidate.origin in {'registry_email', 'subunit_registry_email'}:
        section.claims[-1].reasons['discovery_method'] = 'registry email domain'
    if candidate.origin in {'nav_employer_homepage', 'subunit_nav_employer_homepage'}:
        section.claims[-1].reasons['discovery_method'] = 'nav employer homepage'
    if value.get('matched_via_subunit'):
        section.claims[-1].reasons['relationship'] = 'Website of registered subunit ' + matched
        refs={ref for c in envelope.claims if c.field=='subunits.unit.'+matched for ref in c.evidence_ids}
        section.evidence.extend(e for e in envelope.evidence if e.id in refs)
        section.claims[-1].evidence_ids.extend(sorted(refs))
    elif candidate.subunit_orgnr:
        refs={ref for c in envelope.claims if c.field.startswith(('subunits.unit.'+candidate.subunit_orgnr,'subunits.detail.'+candidate.subunit_orgnr+'.')) for ref in c.evidence_ids}
        section.evidence.extend(e for e in envelope.evidence if e.id in refs)
        section.claims[-1].evidence_ids.extend(sorted(refs))
    # HIGH combines page signals with authoritative registry/roles facts.
    if proof.level in {"HIGH",'REGISTRY_DECLARED'} or proof.proof_type in contact_proofs:
        registry_refs = [e for e in envelope.evidence + section.evidence if e.source_class == "official_registry"]
        registry_refs = list({e.id:e for e in registry_refs}.values())
        section.evidence.extend(registry_refs)
        section.claims[-1].evidence_ids.extend(e.id for e in registry_refs)
    if not value['content_allowed']:
        section.claims = [c for c in section.claims if c.field == 'official_website']
        section.state = 'available'
        http.accepted_pages[org] = []
        envelope.run.refresh['website'] = {'checked_urls':sorted({r.url for r,_ in pages}), 'publication_tier':'B','content_allowed':False}
        section.errors.append(Error(section='website',code='website_candidates',message=json.dumps(attempts+http.attempts.get(org,[]),ensure_ascii=False)))
        return section
    from .descriptions import extract as descriptions
    accepted_domain_pages = [(r, p) for r, p in pages if domain(r.url) == domain(response.url)]
    identity_claim = section.claims[-1]
    from .entity_scope import foreign_entity_page
    safe_pages = [(r, p) for r, p in accepted_domain_pages if not foreign_entity_page(p, org, context.get('name'))]
    if value.get('relationship_note') != 'group_site':
        descriptions(section, org, identity_claim, safe_pages)
    extract_contacts_and_social(section, org, identity_claim, accepted_domain_pages, context=context, envelope=envelope)
    brand = extract_public_brand(page, context.get("name"))
    if brand:
        span = (page.span_for(brand) or "")[:150]
        publish(section, response, org, "public_brand", brand, "meta:brand", span)
    section.state = "available"
    http.accepted_pages[org] = [(r, p) for r, p in pages if domain(r.url) == domain(response.url)]
    envelope.run.refresh['website'] = {'checked_urls': sorted({r.url for r, _ in http.accepted_pages[org]})}
    envelope.run.refresh['website']['observed_social_profiles'] = sorted({url for _, p in http.accepted_pages[org] for url in observed_profiles(p)})
    section.errors.append(Error(section='website',code='website_candidates',message=json.dumps(attempts+http.attempts.get(org,[]),ensure_ascii=False)))
    return section
