import re
from urllib.parse import urlsplit, urlunsplit, unquote
import unicodedata
from .candidates import legal_name
from .policy import SOCIAL, domain
from .html import json_values


def profile_url(url):
    p = urlsplit(url)
    root = domain(url)
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


def discover(page):
    found = {}
    for link in page.links:
        url = profile_url(link.href)
        if url and link.owned_context:
            found.setdefault(url, link.span)
    for body in page.jsonld:
        for values in json_values(body, "sameAs", exclude_person=True):
            for value in values if isinstance(values, list) else [values]:
                if isinstance(value, str) and (url := profile_url(value)):
                    found.setdefault(url, page.span_for(value))
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
    handle = urlsplit(parsed).path.rstrip('/').rsplit('/', 1)[-1]
    return name_matches(handle, names)


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
    found = discover(page) if not scope else {
        profile_url(x.href): x.span for x in page.links
        if profile_url(x.href) and not x.template_context
        and (urlsplit(page.url).path.rstrip('/') == scope or urlsplit(page.url).path.startswith(scope+'/'))}
    return {u:s for u,s in found.items() if matches_profile(u, names)}


def drop_shared(envelopes):
    """A profile observed for multiple legal companies is never company-specific."""
    owners = {}
    for envelope in envelopes:
        for observed in envelope.run.refresh.get('website', {}).get('observed_social_profiles', []):
            url = observed.lower().replace('://www.', '://').replace('http://', 'https://')
            owners.setdefault(url, set()).add(envelope.organisation_number)
        for claim in envelope.claims:
            if claim.field.startswith('social_profile.') and claim.availability == 'available':
                url = str(claim.value.get('url', '')).lower().replace('://www.', '://').replace('http://', 'https://')
                owners.setdefault(url, set()).add(envelope.organisation_number)
    for envelope in envelopes:
        removed = []
        for claim in envelope.claims:
            if claim.field.startswith('social_profile.') and claim.availability == 'available':
                url = str(claim.value.get('url', '')).lower().replace('://www.', '://').replace('http://', 'https://')
                if len(owners[url]) > 1:
                    removed.append(claim.id)
        if removed:
            fields = {c.field for c in envelope.claims if c.id in removed}
            envelope.claims = [c for c in envelope.claims if c.id not in removed]
            envelope.changes = [c for c in envelope.changes if c.field not in fields]
            envelope.run.refresh.setdefault('website', {})['shared_social_dropped'] = len(removed)
            if hasattr(envelope.profile, 'values'):
                envelope.profile.values = {c.field:c.value for c in envelope.claims}
            else:
                envelope.profile.claims = envelope.claims
