import re
import json
from urllib.parse import urlsplit
from dataclasses import dataclass, field
from ..identity.orgnr import valid
from .candidates import legal_name
from .html import json_values
from .candidates import GENERIC
from .policy import domain, extract, DIRECTORIES, SOCIAL, is_directory_record
from .social import compact


def orgnrs(text):
    result = set()
    text=re.sub(r'(?<!\w)NO\s*((?:[0-9][ .\u00a0]*){8}[0-9])(?:\s*MVA)?(?!\w)',r' \1 ',str(text),flags=re.I)
    for match in re.finditer(r"(?<!\w)[0-9](?:[0-9 .\u00a0]*[0-9])?(?!\w)", text):
        digits = re.sub(r"[^0-9]", "", match.group())
        if valid(digits):
            result.add(digits)
    return result


def owner_identifier_markup(raw):
    """Mask layout attributes and CSS before scanning raw owner identifiers.

    Preserve offsets, visible text, metadata and structured script contents.
    Attribute matching is confined to parsed start tags, never JSON strings.
    """
    from html.parser import HTMLParser
    offsets = [0]
    for line in raw.split('\n')[:-1]:
        offsets.append(offsets[-1] + len(line) + 1)
    masked = list(raw)
    class LayoutMask(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=False)
            self.css = False
        def _raw_offset(self):
            line, col = self.getpos()
            return offsets[line - 1] + col
        def handle_starttag(self, tag, attrs):
            start = self._raw_offset()
            pattern = r"""([^\s/>="']+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s>"']+))"""
            for match in re.finditer(pattern, self.get_starttag_text()):
                key = match[1].casefold()
                if key in {'id', 'class', 'style'} or key.startswith('data-'):
                    for pos in range(start + match.start(), start + match.end()):
                        if masked[pos].isdigit(): masked[pos] = ' '
            if tag == 'style': self.css = True
        def handle_endtag(self, tag):
            if tag == 'style': self.css = False
        def handle_data(self, data):
            if self.css:
                start = self._raw_offset()
                for pos in range(start, start + len(data)):
                    if masked[pos] not in '\r\n': masked[pos] = ' '
    parser = LayoutMask()
    parser.feed(raw)
    return ''.join(masked)


def hidden_owner_ids(page, context):
    """Read explicit site-owner identifiers, never customer IDs or analytics numbers."""
    from html import unescape
    found = set()
    keys = {'orgnr', 'organisasjonsnummer', 'organizationnumber', 'organisationnumber', 'vatid', 'taxid'}
    own_keys = {'organization', 'organisation', 'businessinfo', 'business', 'companyinfo', 'siteowner'}
    def walk(node, owner=False):
        if isinstance(node, list):
            return  # lists commonly contain clients, products or other companies
        if not isinstance(node, dict): return
        types = node.get('@type', [])
        types = types if isinstance(types, list) else [types]
        explicit = owner or any(t in {'Organization', 'LocalBusiness', 'Corporation'} for t in types)
        if explicit and isinstance(node.get('legalName') or node.get('name'), str):
            named = legal_name(node.get('legalName') or node.get('name')) == legal_name(context.get('name'))
            for key, value in node.items():
                if key.casefold().replace('_', '') in keys and isinstance(value, (str, int)):
                    numbers = orgnrs(str(value))
                    if named:
                        found.update(numbers)
                    else:
                        found.update(numbers - set(context.get('allowed_orgnrs', ())))
        for key, value in node.items():
            if key.casefold() in {'customers','clients','partners','products','employees','provider','publisher','parentorganization','suborganization'}:
                continue
            if isinstance(value, dict): walk(value, key.casefold() in own_keys)
    for match in re.finditer(r'<script\b[^>]*>(.*?)</script\s*>', page.raw, re.I | re.S):
        content = unescape(match[1]).strip()
        try:
            # Plain JSON, or a JSON object assigned to a window CMS variable.
            start = content.find('{')
            if start >= 0:
                prefix = content[:start].strip()
                if prefix and not re.fullmatch(r'(?:(?:var|let|const)\s+)?(?:window\.)?[A-Za-z_$][\w.$]*\s*=\s*', prefix):
                    continue
                node, _ = json.JSONDecoder().raw_decode(content[start:])
                walk(node)
        except (ValueError, TypeError, RecursionError):
            continue
    # Hidden footer templates still need the exact legal identity and an
    # explicitly labelled identifier. A number in arbitrary raw HTML is not proof.
    expected = legal_name(context.get('name'))
    for match in re.finditer(r'<footer\b[^>]*>(.*?)</footer\s*>', page.raw, re.I | re.S):
        text = unescape(re.sub(r'<[^>]+>', ' ', owner_identifier_markup(match[1])))
        if (expected and re.search(r'(?<!\w)'+re.escape(expected)+r'(?!\w)', legal_name(text))
                and not re.search(r'\b(?:customer|client|partner|kunde|referanse)',text,re.I)
                and re.search(r'org(?:anisasjons)?\.?\s*(?:nr|nummer)|vat|tax\s*id', text, re.I)):
            found.update(orgnrs(text))
    return found


def phone(value):
    text = str(value or "").strip()
    if text.startswith("+") and not text.startswith("+47"):
        return None
    number = re.sub(r"\D", "", str(value or ""))
    if number.startswith("0047"):
        number = number[4:]
    elif len(number) == 10 and number.startswith("47"):
        number = number[2:]
    return "+47" + number if len(number) == 8 else None


def contact_section_number(page, org, context):
    """Exact own-company number in a CMS contact page, never a news article."""
    path=urlsplit(page.url).path.rstrip('/').split('/')[-1].casefold()
    if path not in {'kontakt','kontakt-oss','contact','contact-us','impressum','imprint','personvern','privacy','privacy-policy'}:
        return False
    if not re.search(r'<article\b[^>]*\bclass=[\'"][^\'"]*\btype-page\b',page.raw,re.I):
        return False
    if any(str(t).rsplit('/',1)[-1] in {'NewsArticle','BlogPosting','Article'}
           for body in page.jsonld for declared in json_values(body,'@type')
           for t in (declared if isinstance(declared,list) else [declared])):
        return False
    normalize=lambda value:' '.join(re.findall(r'\w+',str(value or '').casefold()))
    name=normalize(context.get('name'))
    if not name:return False
    visible=' '.join(page.visible.split())
    number=re.compile(r'(?<!\d)'+r'[\s.]?'.join(org)+r'(?!\d)')
    for match in number.finditer(visible):
        block=visible[max(0,match.start()-400):match.end()]
        headings=list(re.finditer(r'\b(?:hovedkontor|kontaktinformasjon|registered office|company details|impressum)\b',block,re.I))
        if not headings:continue
        block=block[headings[-1].start():]
        if (re.search(r'(?<!\w)'+re.escape(name)+r'(?!\w)',normalize(block))
                and re.search(r'\b(?:hovedkontor|kontaktinformasjon|registered office|company details|impressum)\b',block,re.I)
                and re.search(r'\b(?:org\.?\s*nr|organisasjonsnummer|vat|tax\s*id)',block,re.I)
                and not re.search(r'\b(?:kunde|kunder|customer|customers|partner|partners|client|clients|referanser)\b',block,re.I)):
            return True
    return False


def normalized_address(value):
    text=' '.join(re.findall(r'\w+',str(value or '').casefold()))
    text=re.sub(r'\b(\w+?)(?:gata|gaten|gate|gt)\b',r'\1gate',text)
    text=re.sub(r'\b(\w+?)(?:veien|vegen|vei|veg|vn)\b',r'\1vei',text)
    text=re.sub(r'\bgt\b','gate',text)
    return re.sub(r'\b(?:vn|vegen|veien|veg)\b','vei',text)


from html.parser import HTMLParser


def has_copyright_owner(page, org, name):
    """Independent own-brand/footer proof, not a nearby customer mention."""
    # Compare the complete legal/brand spelling, allowing word spacing only.
    # This is a proof comparison, never a rewrite of a published legal name.
    compact=lambda text:re.sub(r'\s+', '', legal_name(text))
    expected = compact(name)
    if not expected or compact(page.title)!=expected:
        return False
    class Footer(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True);self.active=False;self.parts=[];self.footers=[];self.hidden=0
        def handle_starttag(self,tag,attrs):
            if tag in {'script','style','template'}:self.hidden+=1
            if tag=='footer':self.active=True;self.parts=[]
        def handle_endtag(self,tag):
            if tag=='footer' and self.active:self.footers.append(' '.join(self.parts));self.active=False
            if tag in {'script','style','template'}:self.hidden=max(0,self.hidden-1)
        def handle_data(self,data):
            if self.active and not self.hidden:self.parts.append(data)
    parsed=Footer();parsed.feed(page.raw)
    for text in parsed.footers:
        if orgnrs(text)!={org}:continue
        owners=re.finditer(r'(?:©|copyright)\s*(?:\d{4}\s*)?(.+?)(?=\s*(?:organisasjonsnummer|org\.?\s*nr|vat|©|copyright)|$)',text,re.I)
        if any(compact(owner.group(1).strip(' .,:;'))==expected for owner in owners):return True
    return False


class EntityCard:
    """Represents a discrete corporate entity or department container on a web page."""
    def __init__(self, start: int, end: int, raw: str, text: str, tag: str, attrs: dict):
        self.start = start
        self.end = end
        self.raw = raw
        self.text = text
        self.tag = tag
        self.attrs = attrs
        self.identifier_raw = owner_identifier_markup(raw)
        self.orgnrs = orgnrs(re.sub(r'<[^>]+>', ' ', self.identifier_raw)) | orgnrs(self.identifier_raw)

    def matches_org(self, org: str, context: dict | None = None, subunits: set[str] | None = None) -> bool:
        org_pat = re.compile(r'\b' + org[:3] + r'[\s.]?' + org[3:6] + r'[\s.]?' + org[6:9] + r'\b')
        if org in self.orgnrs or org_pat.search(self.identifier_raw):
            return True
        if subunits:
            for sub in subunits:
                sub_pat = re.compile(r'\b' + sub[:3] + r'[\s.]?' + sub[3:6] + r'[\s.]?' + sub[6:9] + r'\b')
                if sub in self.orgnrs or sub_pat.search(self.identifier_raw):
                    return True
        if context and context.get("name"):
            subj_tokens = [t.lower() for t in re.findall(r'[a-zA-ZæøåÆØÅ]{3,}', context["name"]) if t.lower() not in {"as", "asa", "holding", "group", "norge", "nordic", "the"}]
            if subj_tokens and all(t in self.text.lower() for t in subj_tokens) and not any(sib in self.text.lower() for sib in ["group", "gruppe", "holding"]):
                if not any(o != org for o in self.orgnrs if not (subunits and o in subunits)):
                    return True
        return False

    def is_sibling(self, org: str, other_orgnrs: set[str] | list[str] | None = None, subunits: set[str] | None = None) -> bool:
        other_set = set(other_orgnrs or [])
        if other_set and any(o in self.orgnrs for o in other_set if o != org):
            return True
        if any(o != org for o in self.orgnrs if not (subunits and o in subunits)):
            return True
        # Foreign corporate entity registration identifiers (Swedish 556xxx-xxxx, Danish CVR 8 digits, Polish REGON/NIP 10 digits)
        if re.search(r'\b(?:556\d{3}-\d{4}|\d{8}|\d{10})\b', self.text) and not bool(re.search(r'\b' + org[:3] + r'[\s.]?' + org[3:6] + r'[\s.]?' + org[6:9] + r'\b', self.text)):
            return True
        return False


def extract_entity_cards(raw_html: str) -> list[EntityCard]:
    """
    Partitions HTML into discrete corporate entity card/container elements
    (e.g. elements with classes matching card, entity, unit, company, box, invoice, contact).
    """
    cards = []
    line_offsets = [0]
    for line in raw_html.split('\n')[:-1]:
        line_offsets.append(line_offsets[-1] + len(line) + 1)

    class Parser(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.stack = []

        def _offset(self):
            line, col = self.getpos()
            return line_offsets[line - 1] + col

        def handle_starttag(self, tag, attrs):
            attrs_dict = {k.lower(): v or '' for k, v in attrs}
            cls = attrs_dict.get('class', '')
            tag_id = attrs_dict.get('id', '')
            is_card = bool(re.search(r'\b(?:card|entity|unit|company|box|invoice|contact-card|contact-box)\b', cls + ' ' + tag_id, re.I)) or tag in ('section', 'article')
            offset = self._offset()
            self.stack.append({'tag': tag, 'is_card': is_card, 'start': offset, 'attrs': attrs_dict, 'text_parts': []})

        def handle_data(self, data):
            for s in self.stack:
                s['text_parts'].append(data)

        def handle_endtag(self, tag):
            for i in range(len(self.stack) - 1, -1, -1):
                if self.stack[i]['tag'] == tag:
                    entry = self.stack[i]
                    if entry['is_card']:
                        parent_is_card = any(s['is_card'] for s in self.stack[:i])
                        if not parent_is_card:
                            end_offset = self._offset() + len(tag) + 3
                            card_raw = raw_html[entry['start']:end_offset]
                            card_text = ' '.join(''.join(entry['text_parts']).split())
                            cards.append(EntityCard(entry['start'], end_offset, card_raw, card_text, entry['tag'], entry['attrs']))
                    self.stack = self.stack[:i]
                    break

    p = Parser()
    try:
        p.feed(raw_html)
    except Exception:
        pass
    return cards


def find_containing_card(cards: list[EntityCard], pos: int) -> EntityCard | None:
    """Finds the entity card enclosing the character offset pos."""
    for c in cards:
        if c.start <= pos <= c.end:
            return c
    return None


def is_dedicated_entity_card(raw_html: str, org: str, name: str = "") -> bool:
    """Checks whether org appears inside a dedicated corporate entity card/block rather than an arbitrary directory table."""
    cards = extract_entity_cards(raw_html)
    for c in cards:
        if c.matches_org(org, context={"name": name}):
            return True
    pat = re.compile(r"\b" + org[0:3] + r"[\s.]?" + org[3:6] + r"[\s.]?" + org[6:9] + r"\b")
    for m in pat.finditer(owner_identifier_markup(raw_html)):
        start = max(0, m.start() - 350)
        end = min(len(raw_html), m.end() + 250)
        window = raw_html[start:end]

        has_id_label = bool(re.search(r"(?:organisation\s+number|organisasjonsnummer|org\.?\s*nr|faktura|invoice|mva|vat)", window, re.I))
        if not has_id_label:
            continue

        is_partner = bool(re.search(r"\b(?:kunder|våre\s+kunder|partnere|våre\s+partnere|partners|clients|referanser|portfolio|directory|leverandører)\b", window, re.I))
        if is_partner:
            continue

        has_card_or_heading = bool(re.search(r'<(?:h[1-6]|div|section|article|p)[^>]*class=[\'"][^\'"]*(?:card|entity|unit|company|box|contact|invoice)[^\'"]*[\'"]', window, re.I))
        has_heading = bool(re.search(r"<h[1-6][^>]*>[^<]+</h[1-6]>", window, re.I))

        name_match = False
        if name:
            tokens = [t.lower() for t in re.findall(r"[a-zA-ZæøåÆØÅ]{3,}", name) if t.lower() not in {"as", "asa", "holding", "group", "norge", "nordic", "the"}]
            if any(t in window.lower() for t in tokens):
                name_match = True

        if (has_card_or_heading or has_heading) and (name_match or not name):
            return True
    return False


@dataclass
class Proof:
    level: str
    proof_type: str = ""
    signals: list[str] = field(default_factory=list)
    points: int = 0
    other_orgnrs: list[str] = field(default_factory=list)
    reason: str = ""
    token: str = ""
    subject_orgnr: str = ''


def score(page, org, context, origin, leaders, *, suffix_contact=False, domain_location=False, nominated_contacts=False):
    from .names import proof_context,same_name
    context=proof_context(page,org,context)
    if domain(page.url) in DIRECTORIES | SOCIAL or is_directory_record(page.url):
        return Proof('REJECT', reason='directory_or_marketplace')
    raw = page.raw.lower()
    # A registry nomination or shared contact cannot override an explicit
    # copyright/publisher naming another legal entity on the same page.
    expected = {' '.join(re.findall(r'\w+', str(n or '').casefold())) for n in
                [context.get('name'), *[u.get('name') for u in context.get('subunits', [])]]}
    for label in re.findall(r'(?:copyright|\u00a9|owned by|utgitt av|eies av)\s*(?:\u00a9\s*)?(?:20\d\d\s*)?([^|<>\n]{1,100}?\b(?:AS|ASA|AB|Ltd|GmbH|Oy)\b)', page.owner_text, re.I):
        if re.search(r'web levert av|website by|design|nettside|utviklet av',label,re.I):continue
        label = re.split(r'owned by|utgitt av|eies av',label,flags=re.I)[-1]
        # Corporate share ownership is not the site's publisher identity.
        if re.match(r'\s*(?:konsernet|gruppen|the group)\b',label,re.I):continue
        label = re.sub(r'copyright|all rights reserved|all[e]? rettigheter reservert|\b(?:19|20)\d\d(?:\s*[-\u2013]\s*(?:19|20)\d\d)?\b',' ',label,flags=re.I)
        normalized = ' '.join(re.findall(r'\w+', label.casefold()))
        if not any(same_name(name,normalized,orgnrs(' '.join(page.brand_parts))=={org}) for name in expected):
            return Proof('REJECT', reason='different_legal_entity')
    is_active_challenge = (
        any(x in raw for x in ("cf-chl-", "cf-turnstile", "verify you are human", "checking your browser"))
        or bool(re.search(r'\b(?:captcha|challenge|security check|sikkerhetskontroll)\b', page.title, re.I))
        or bool(re.search(r'\b(?:complete\s+the\s+captcha|prove\s+you\s+are\s+human|security\s+challenge|bekreft\s+at\s+du\s+er\s+et\s+menneske)\b', page.visible, re.I))
        or ('g-recaptcha-response' in raw and '<form' in raw and len(page.visible.strip()) < 500)
    )
    if is_active_challenge:
        return Proof("BLOCKED", reason="block_page")
    if any(x in raw for x in ("this domain is for sale", "domenet er til salgs", "domain is parked", "buy this domain", "sedo.com/search")):
        return Proof("REJECT", reason="parked")
    if re.search(r'\b(?:is parked|in parked|not set up yet|registrert domene|default (?:web ?site|page)|welcome to nginx|apache2? (?:debian|ubuntu) default|index of /)\b', page.title + ' ' + page.visible, re.I):
        return Proof('REJECT', reason='hosting_default')
    if nominated_contacts or origin == 'registry_website':
        if re.search(r'\b(?:default (?:web ?site|page)|welcome to nginx|apache2? (?:debian|ubuntu) default|index of /|domain (?:has been|is) registered|domenet er (?:parkert|registrert))\b', page.title + ' ' + page.visible, re.I):
            return Proof('REJECT', reason='hosting_default')
        from .entity_scope import foreign_entity_page
        identity_text = page.title + ' ' + page.meta.get('og:site_name','') + ' ' + ' '.join(page.identity_headings)
        legal_identity = ' '.join(re.findall(r'\w+', identity_text.casefold()))
        expected_names = [context.get('name'), *[u.get('name') for u in context.get('subunits', [])]]
        own_brand = any((name := legal_name(n)) and re.search(r'(?<!\w)' + re.escape(name) + r'(?!\w)', legal_identity) for n in expected_names)
        if not own_brand and re.search(r'\b[A-ZÆØÅ][\wÆØÅæøå&.-]*(?:\s+[A-ZÆØÅ][\wÆØÅæøå&.-]*){0,5}\s+(?:AS|ASA|AB|Ltd|GmbH|Oy)\b', identity_text):
            return Proof('REJECT', reason='different_legal_entity')
        allowed = set(context.get('allowed_orgnrs', {org}))
        if foreign_entity_page(page, org, context.get('name'), check_ids=False):
            return Proof('REJECT', reason='different_legal_entity')
    visible = orgnrs(page.owner_text)
    meta = orgnrs(" ".join(page.meta.values()))
    json_ids = set()
    from .social import organization_objects
    for body in [node for document in page.jsonld for node in organization_objects(document,own_only=True)]:
        for key in ("vatID", "taxID", "identifier"):
            for value in json_values(body, key, exclude_person=True):
                # NO123456789MVA is permitted only inside an explicit identifier
                # field. Never search leiCode or arbitrary script contents.
                if isinstance(value, str):
                    normalized = re.sub(r"^\s*NO\s*|\s*MVA\s*$", " ", value, flags=re.I).strip()
                    json_ids |= orgnrs(normalized)
                elif isinstance(value, dict):
                    json_ids |= orgnrs(value.get("value", ""))
    hidden_ids = hidden_owner_ids(page, {**context, 'allowed_orgnrs': context.get('allowed_orgnrs', {org})})
    all_ids = visible | meta | json_ids | hidden_ids
    allowed = set(context.get('allowed_orgnrs', {org}))
    others = sorted(all_ids - allowed)
    owner_ids = orgnrs(' '.join(page.brand_parts)) | json_ids | hidden_ids
    if owner_ids - allowed:
        return Proof('REJECT', other_orgnrs=sorted(owner_ids - allowed), reason='foreign_orgnr')
    if org not in all_ids and not others and (subjects := all_ids & allowed):
        subject = sorted(subjects)[0]
        return Proof('VERIFIED', 'registered_subunit_orgnr', token=subject, subject_orgnr=subject)
    if not others and contact_section_number(page,org,context):
        return Proof('VERIFIED','contact_section_orgnr',token=org)
    if org in all_ids:
        # A listed partner/customer is not the operator of the page. Exact
        # identifiers in directory text need an independent entity card or
        # structured owner identifier before they can establish ownership.
        if len(others) < 2 and org not in json_ids and re.search(
            r'\b(?:our\s+partners|our\s+clients|our\s+customers|directory|våre\s+partnere|våre\s+kunder)\b',
            page.visible, re.I,
        ) and not is_dedicated_entity_card(page.raw, org, context.get('name', '')) and not has_copyright_owner(page, org, context.get('name', '')):
            return Proof("REJECT", other_orgnrs=others, reason="partner_directory_mention")
        if len(others) >= 2 and org not in json_ids:
            # Multi-entity group site check: requires registry-origin domain and dedicated entity card
            is_valid_group = False
            if origin == "registry_website":
                if is_dedicated_entity_card(page.raw, org, context.get("name", "")):
                    is_valid_group = True
            if not is_valid_group:
                return Proof("REJECT", other_orgnrs=others, reason="unverified_multi_entity_site")
        return Proof("VERIFIED", "jsonld_vatid" if org in json_ids else "raw_owner_identifier" if org in hidden_ids and org not in visible | meta else "orgnr_on_page", other_orgnrs=others, token=org)
    if others:
        return Proof("REJECT", other_orgnrs=others, reason="foreign_orgnr")
    def normalized(value):
        return " ".join(re.findall(r"\w+", str(value or "").casefold()))
    full_name = normalized(context.get('name'))
    owner_text = normalized(page.title + ' ' + page.meta.get('og:site_name', '') + ' ' + page.owner_text)
    exact_name = bool(full_name and re.search(r'(?<!\w)' + re.escape(full_name) + r'(?!\w)', owner_text))
    branding = normalized(page.title + ' ' + page.meta.get('og:site_name', ''))
    if re.search(r'\b(?:group|gruppen|gruppe|holding)\b', branding) and not re.search(r'\b(?:group|gruppen|gruppe|holding)\b', full_name):
        return Proof('REJECT', reason='parent_group_without_exact_orgnr')
    signals = ['exact_legal_name'] if exact_name else []
    street = context.get('street')
    streets = street if isinstance(street, list) else [street]
    address_text=normalized_address(page.owner_text)
    if any(s and len(str(s)) > 4 and re.search(r'(?<!\w)'+re.escape(normalized_address(s))+r'(?!\w)',address_text) for s in streets):
        signals.append('street')
    city = context.get('city') or context.get('municipality')
    if context.get('postcode') and city and str(context['postcode']) in owner_text and normalized(city) in owner_text:
        signals.append('postcode_city')
    expected_phone = phone(context.get('phone'))
    page_phones = {phone(link.href[4:]) for link in page.links if link.href.startswith('tel:')}
    for match in re.finditer(r'(?<!\d)(?:(?:\+47|0047)[ .-]*)?(?:\d[ .()-]*){8}(?!\d)', page.owner_text):
        page_phones.add(phone(match.group()))
    if expected_phone and expected_phone in page_phones:
        signals.append('phone')
    email = str(context.get('email') or '').strip().casefold()
    if email and (email in page.owner_text.casefold() or any(link.href.casefold().split('?')[0] == 'mailto:' + email for link in page.links)):
        signals.append('email')
    if exact_name and len(signals) >= 2:
        return Proof('VERIFIED', 'legal_name_and_registry_contact', signals, 2 * len(signals), token=str(context['name']))
    base_name=legal_name(context.get('name'))
    independent_name_text = owner_text
    for value in [context.get('email'), *[s for s in streets if s]]:
        if value:
            independent_name_text = independent_name_text.replace(normalized(value), ' ')
    exact_base=bool(base_name and re.search(r'(?<!\w)'+re.escape(normalized(base_name))+r'(?!\w)',independent_name_text))
    label=compact(extract(page.url).domain)
    derived=label in {compact(base_name),compact(base_name)+'as',compact(base_name)+'asa'} and len(compact(base_name))>=4
    contacts=[s for s in signals if s in {'street','postcode_city','phone','email'}]
    declared = origin == 'registry_website'
    if declared and (exact_name or exact_base):
        return Proof('VERIFIED', 'registry_declared_name_tier_a', ['registry_declared_domain', 'legal_name'], 4,
                     token=str(context['name']) if exact_name else base_name)
    if declared:
        holder = next((name for name in leaders if isinstance(name,str) and len(name.split()) >= 2 and
                       re.search(r'(?<!\w)' + re.escape(normalized(name)) + r'(?!\w)', owner_text)), None)
        if contacts or holder:
            token = str(context.get('email') or '') if 'email' in contacts else str(holder) if holder else str(context.get('postcode')) if 'postcode_city' in contacts else ''
            if not token and 'street' in contacts:
                token = next((str(s) for s in streets if s and normalized_address(s) in address_text), '')
            if not token and 'phone' in contacts:
                token = next((m.group() for m in re.finditer(r'(?<!\d)(?:(?:\+47|0047)[ .-]*)?(?:\d[ .()-]*){8}(?!\d)', page.owner_text) if phone(m.group())==expected_phone), str(context.get('phone')))
            return Proof('VERIFIED', 'registry_declared_hard_contact_tier_b', ['registry_declared_domain', *contacts, *(['registered_role_holder'] if holder else [])], 4, token=token)
    if nominated_contacts:
        categories = set()
        if exact_name or exact_base: categories.add('legal_name')
        if 'phone' in contacts: categories.add('registry_phone')
        if 'email' in contacts: categories.add('registry_email')
        if 'street' in contacts or 'postcode_city' in contacts: categories.add('registry_address')
        if 'legal_name' in categories and len(categories) >= 2:
            token = str(context.get('name') if exact_name else base_name) if exact_name or exact_base else ''
            if not token and 'registry_email' in categories:token = email
            if not token and 'registry_phone' in categories:
                token = next((m.group() for m in re.finditer(r'(?<!\d)(?:(?:\+47|0047)[ .-]*)?(?:\d[ .()-]*){8}(?!\d)', page.owner_text) if phone(m.group())==expected_phone), str(context.get('phone')))
            return Proof('VERIFIED', 'nominated_two_independent_signals', sorted(categories),
                         2 * len(categories), token=token)
    if suffix_contact and exact_base and derived and len(contacts)>=2:
        return Proof('VERIFIED','legal_name_without_suffix_and_two_contacts',
                     ['legal_name_without_suffix','name_derived_domain',*contacts],2*len(contacts),token=base_name)
    generic = GENERIC | {'company', 'business', 'services', 'consulting', 'gruppe', 'gruppen', 'norge', 'norway', 'nordic'}
    distinctive = (len(compact(base_name)) >= 6 and base_name.split()
                   and not all(word in generic for word in base_name.split()))
    if domain_location and distinctive and label == compact(base_name):
        location_text = normalized(page.owner_text)
        for key in ('postcode', 'municipality'):
            location = normalized(context.get(key))
            valid_location = bool(re.fullmatch(r'\d{4}', location)) if key == 'postcode' else len(location) >= 3
            if valid_location and re.search(r'(?<!\w)' + re.escape(location) + r'(?!\w)', location_text):
                return Proof('VERIFIED', 'domain_legal_name_and_registry_location',
                             ['exact_legal_domain', 'registry_' + key], 4, token=str(context[key]))
    from .additional_proof import additional_proof
    recovered = additional_proof(page, org, context)
    if recovered:
        return recovered
    if suffix_contact and exact_base:
        return Proof('MEDIUM','signals',['legal_name_without_suffix',*contacts],2*len(contacts),reason='name_without_suffix_insufficient_contacts_or_domain',token=base_name)
    return Proof('MEDIUM' if exact_name else 'LOW', 'signals', signals, 2 * len(signals), reason='name_only' if exact_name else 'insufficient_owner_proof', token=str(context.get('name') or ''))
