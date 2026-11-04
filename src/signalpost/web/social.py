import re
from urllib.parse import urlsplit, urlunsplit, unquote, urljoin
import unicodedata
from .candidates import legal_name
from .policy import SOCIAL, domain
from .html import json_values


def profile_url(url):
    try:
        p = urlsplit(url)
        root = domain(url)
    except (TypeError, ValueError):
        # Broken third-party sameAs values must not discard valid site proof.
        return None
    if p.scheme not in {"http", "https"} or root not in SOCIAL:
        return None
    bits = [x for x in p.path.split("/") if x]
    if not bits:
        return None
    lowered = [x.lower() for x in bits]
    if any(x in {"share", "sharer", "sharer.php", "intent", "login", "explore", "hashtag", "search", "privacy", "watch", "p", "reel", "reels", "profile.php", "l.php", "dialog", "status", "statuses"} for x in lowered):
        return None
    allowed = False
    if root == "linkedin.com":
        allowed = len(bits) == 2 and lowered[0] == "company"
    elif root in {"instagram.com", "x.com", "twitter.com"}:
        allowed = len(bits) == 1 and lowered[0] not in {"home", "i", "settings", "tos"}
    elif root == "facebook.com":
        allowed = len(bits) == 1 or (len(bits) == 3 and lowered[0] == "pages")
    elif root == "youtube.com":
        allowed = (len(bits) == 1 and bits[0].startswith("@")) or (len(bits) == 2 and lowered[0] in {"channel", "c", "user"})
    elif root == "tiktok.com":
        allowed = len(bits) == 1 and bits[0].startswith("@")
    return urlunsplit((p.scheme, (p.hostname or "").lower(), "/" + "/".join(bits), "", "")) if allowed else None


ORGANIZATION_TYPES={'Organization','LocalBusiness','Corporation','ProfessionalService','Store',
                    'AccountingService','Electrician','AutoRepair','ChildCare','NGO','EducationalOrganization','GovernmentOrganization'}


def organization_objects(value):
    if isinstance(value,list):
        for item in value:yield from organization_objects(item)
    elif isinstance(value,dict):
        types=value.get('@type',[])
        types=types if isinstance(types,list) else [types]
        types={str(t).rsplit('/',1)[-1].rsplit(':',1)[-1] for t in types}
        if 'Person' in types:return
        if types & ORGANIZATION_TYPES:yield value
        for item in value.values():yield from organization_objects(item)


def organization_social(page,context=None,scope=None):
    found={}
    for body in page.jsonld:
        for node in organization_objects(body):
            name=node.get('legalName') or node.get('name')
            if context and name and (not isinstance(name,str) or not name_matches(name,company_names(context))):continue
            if scope:
                own=node.get('url') or node.get('@id')
                if not isinstance(own,str):continue
                own=urljoin(page.url,own)
                if domain(own)!=domain(page.url) or not (urlsplit(own).path.rstrip('/')==scope or urlsplit(own).path.startswith(scope+'/')):continue
            values=node.get('sameAs',[])
            for value in values if isinstance(values,list) else [values]:
                value=value.get('@id') if isinstance(value,dict) else value
                if isinstance(value,str) and (url:=profile_url(value)):
                    found.setdefault(url,page.span_for(value))
    return found


def discover(page,context=None,*,same_as=True):
    found = {}
    for link in page.links:
        url = profile_url(link.href)
        if url and link.owned_context:
            found.setdefault(url, link.span)
    if same_as:
        for url,span in organization_social(page,context).items():found.setdefault(url,span)
    return found


def compact(value):
    value = str(value or '').casefold().replace('æ', 'ae').replace('ø', 'o').replace('å', 'a')
    return ''.join(c for c in unicodedata.normalize('NFKD', value) if c.isalnum())


def company_names(context):
    return [n for n in [context.get('name'), *context.get('registered_brands', []),
                       *(u.get('name') for u in context.get('subunits', []))] if n]


def name_matches(value, names):
    """Whole handle/name equality, allowing legal suffix and trailing profile ID."""
    value = unquote(str(value or '')).lstrip('@')
    value = re.sub(r'[-_. ]*\d{5,}$', '', value)
    actual = compact(legal_name(value.replace('-', ' ').replace('_', ' ')))
    for name in names:
        expected = compact(legal_name(name))
        if len(expected) >= 3 and actual in {expected, expected+'as', expected+'asa'}:
            return True
    return False


def matches_profile(url, names):
    parsed = profile_url(url)
    if not parsed:
        return False
    bits = [unquote(x) for x in urlsplit(parsed).path.split('/') if x]
    handle = bits[1] if domain(parsed)=='facebook.com' and len(bits)==3 and bits[0].lower()=='pages' else bits[-1]
    if handle.isdigit() or domain(parsed)=='youtube.com' and bits[0].lower()=='channel':
        return False
    return name_matches(handle, names)


def mentions_company(text, names):
    words = re.findall(r'\w+', str(text).casefold())
    text = ' '.join(words)
    return any(re.search(r'(?<!\w)'+re.escape(legal_name(n))+r'(?!\w)', text) for n in names if legal_name(n))


def observed_profiles(page):
    """Track all observed handles, including ones in unpublishable contexts."""
    found={url for link in page.links if (url:=profile_url(link.href))}
    for body in page.jsonld:
        for values in json_values(body,'sameAs'):
            for value in values if isinstance(values,list) else [values]:
                if isinstance(value,str) and (url:=profile_url(value)):found.add(url)
    return found


def profile_key(url):
    root=domain(url)
    if root=='twitter.com':root='x.com'
    path=unquote(urlsplit(url).path).rstrip('/').casefold()
    if root=='facebook.com' and (identifier:=re.search(r'(?:^|[-/])(\d{5,})$',path)):
        path='/'+identifier[1]
    return root+path


def path_scope(proof, context):
    """A company-named branch path on a shared domain needs local attribution."""
    url = proof.get('proof_page_url') or proof.get('final_url') or ''
    bits = [unquote(x).casefold() for x in urlsplit(url).path.split('/') if x]
    subject_bits = bits[1:] if bits and bits[0] in {'en','no','nb'} else bits
    if not subject_bits or subject_bits[0] in {'kontakt','kontakt-oss','contact','contact-us','om','om-oss','about','privacy','personvern','pages'}:
        return None
    names = company_names(context)
    first = compact(subject_bits[0])
    if any(first == compact(t) and len(first) >= 4 for n in names for t in legal_name(n).split()):
        return '/' + '/'.join(bits)
    return None


def attributed(page, proof, context, *, same_as=True):
    names = company_names(context)
    scope = path_scope(proof, context)
    found = discover(page,context,same_as=same_as) if not scope else {
        profile_url(x.href): x.span for x in page.links
        if profile_url(x.href) and not x.template_context
        and (urlsplit(page.url).path.rstrip('/') == scope or urlsplit(page.url).path.startswith(scope+'/'))}
    if scope and same_as:
        for url,span in organization_social(page,context,scope).items():found.setdefault(url,span)
    return {u:s for u,s in found.items() if matches_profile(u, names)}


def drop_shared(envelopes, blobs=None):
    """A profile observed for multiple legal companies is never company-specific."""
    owners = {}
    for envelope in envelopes:
        for observed in envelope.run.refresh.get('website', {}).get('observed_social_profiles', []):
            url = profile_key(observed)
            owners.setdefault(url, set()).add(envelope.organisation_number)
        for claim in envelope.claims:
            if claim.field.startswith(('social_profile.','registry_social.')) and claim.availability == 'available':
                url = profile_key(str(claim.value.get('url', '')))
                owners.setdefault(url, set()).add(envelope.organisation_number)
    for envelope in envelopes:
        removed = []
        context={'name':next((c.value for c in envelope.claims if c.field=='identity.legal_name' and c.availability=='available'),''),
                 'subunits':[c.value for c in envelope.claims if c.field.startswith('subunits.unit.') and c.availability=='available']}
        names=company_names(context)
        proof=next((c.value for c in envelope.claims if c.field=='official_website' and c.availability=='available'),{})
        evidence={e.id:e for e in envelope.evidence}
        shared_count=0
        for claim in envelope.claims:
            if claim.field.startswith(('social_profile.','registry_social.')) and claim.availability == 'available':
                target=str(claim.value.get('url',''));url=profile_key(target)
                rejected=not matches_profile(target,names)
                # Refresh carry-forward must obey the current attribution rules.
                if not rejected and blobs is not None and path_scope(proof,context):
                    from .html import Page
                    allowed=False
                    for ref in claim.evidence_ids:
                        e=evidence.get(ref)
                        if not e:continue
                        if e.source_class=='wikidata':allowed=True;break
                        try:
                            page=Page((blobs.directory/e.content_sha256).read_bytes(),e.source_url)
                            if target in attributed(page,proof,context):allowed=True;break
                        except (OSError,ValueError):pass
                    rejected=not allowed
                shared=len(owners[url])>1
                if rejected or shared:
                    removed.append(claim.id)
                    shared_count+=int(shared)
        if removed:
            fields = {c.field for c in envelope.claims if c.id in removed}
            envelope.claims = [c for c in envelope.claims if c.id not in removed]
            envelope.changes = [c for c in envelope.changes if c.field not in fields]
            envelope.run.refresh.setdefault('website', {})['shared_social_dropped'] = shared_count
            envelope.run.refresh['website']['social_attribution_dropped'] = len(removed)
            if hasattr(envelope.profile, 'values'):
                envelope.profile.values = {c.field:c.value for c in envelope.claims}
            else:
                envelope.profile.claims = envelope.claims
