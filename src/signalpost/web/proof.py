import re
from dataclasses import dataclass, field
from ..identity.orgnr import valid
from .candidates import legal_name
from .html import json_values
from .candidates import GENERIC
from .policy import domain, DIRECTORIES, SOCIAL, is_directory_record


def orgnrs(text):
    result = set()
    for match in re.finditer(r"(?<!\w)[0-9](?:[0-9 .\u00a0]*[0-9])?(?!\w)", str(text)):
        digits = re.sub(r"[^0-9]", "", match.group())
        if valid(digits):
            result.add(digits)
    return result


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
        self.orgnrs = orgnrs(text) | orgnrs(raw)

    def matches_org(self, org: str, context: dict | None = None, subunits: set[str] | None = None) -> bool:
        org_pat = re.compile(r'\b' + org[:3] + r'[\s.]?' + org[3:6] + r'[\s.]?' + org[6:9] + r'\b')
        if org in self.orgnrs or org_pat.search(self.raw):
            return True
        if subunits:
            for sub in subunits:
                sub_pat = re.compile(r'\b' + sub[:3] + r'[\s.]?' + sub[3:6] + r'[\s.]?' + sub[6:9] + r'\b')
                if sub in self.orgnrs or sub_pat.search(self.raw):
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
    for m in pat.finditer(raw_html):
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


def score(page, org, context, origin, leaders):
    if domain(page.url) in DIRECTORIES | SOCIAL or is_directory_record(page.url):
        return Proof('REJECT', reason='directory_or_marketplace')
    raw = page.raw.lower()
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
    visible = orgnrs(page.owner_text)
    meta = orgnrs(" ".join(page.meta.values()))
    json_ids = set()
    for body in page.jsonld:
        for key in ("vatID", "taxID", "identifier"):
            for value in json_values(body, key, exclude_person=True):
                # NO123456789MVA is permitted only inside an explicit identifier
                # field. Never search leiCode or arbitrary script contents.
                if isinstance(value, str):
                    normalized = re.sub(r"^\s*NO\s*|\s*MVA\s*$", " ", value, flags=re.I).strip()
                    json_ids |= orgnrs(normalized)
                elif isinstance(value, dict):
                    json_ids |= orgnrs(value.get("value", ""))
    all_ids = visible | meta | json_ids
    others = sorted(all_ids - {org})
    owner_ids = orgnrs(' '.join(page.brand_parts)) | json_ids
    if owner_ids - {org}:
        return Proof('REJECT', other_orgnrs=sorted(owner_ids - {org}), reason='foreign_orgnr')
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
        return Proof("VERIFIED", "jsonld_vatid" if org in json_ids else "orgnr_on_page", other_orgnrs=others, token=org)
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
    if any(s and len(str(s)) > 4 and normalized(s) in owner_text for s in streets):
        signals.append('street')
    if context.get('postcode') and context.get('city') and str(context['postcode']) in owner_text and normalized(context['city']) in owner_text:
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
    return Proof('MEDIUM' if exact_name else 'LOW', 'signals', signals, 2 * len(signals), reason='name_only' if exact_name else 'insufficient_owner_proof', token=str(context.get('name') or ''))
