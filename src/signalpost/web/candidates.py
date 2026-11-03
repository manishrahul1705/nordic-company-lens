import re
from functools import lru_cache
from dataclasses import dataclass
from .policy import domain, normalize_url, SOCIAL, DIRECTORIES, FREE_MAIL
from ..sources.bulk_registry import column

FORMS = r"\b(?:as|asa|ans|da|enk|nuf|sa|ba|ks|iks|sti)\b$"
GENERIC = {"holding", "invest", "eiendom", "bygg", "service", "consult", "regnskap", "transport", "og"}


@dataclass(frozen=True)
class Candidate:
    url: str
    domain: str
    origin: str
    subunit_orgnr: str | None = None


@lru_cache(maxsize=8192)
def legal_name(value):
    text = str(value or "").casefold().strip(" .,-")
    while re.search(FORMS, text):
        text = re.sub(FORMS, "", text).strip(" .,-")
    return " ".join(re.findall(r"\w+", text))


@lru_cache(maxsize=8192)
def legal_name_slugs(name):
    tokens = [t for t in name.split() if t != "og"]
    slugs = []
    if tokens and not all(t in GENERIC for t in tokens):
        # Preserve existing nominations first, then add the requested spelling
        # and native IDNA variants. These are nominations, never identity proof.
        for replacements in (("ae", "o", "aa"), ("a", "oe", "a"), ("ae", "o", "a")):
            converted = " ".join(tokens).replace("æ", replacements[0]).replace("ø", replacements[1]).replace("å", replacements[2])
            words = re.findall(r"[a-z0-9]+", converted)
            for separator in ("", "-"):
                slug = separator.join(words)
                if len(slug) >= 4:
                    for suffix in ("no", "com"):
                        slugs.append(slug + "." + suffix)
        for separator in ('', '-'):
            native = separator.join(tokens)
            try:
                label = native.encode('idna').decode('ascii')
            except UnicodeError:
                continue
            if len(label) >= 4:
                slugs.extend(label + '.' + suffix for suffix in ('no', 'com'))
    return list(dict.fromkeys(slugs))


def context_from_bulk(row):
    return {"name": column(row, "navn")[0], "website": column(row, "hjemmeside")[0],
            "email": column(row, "epostadresse")[0], "phone": column(row, "telefon")[0],
            "municipality": column(row, "forretningsadresse.kommune")[0],
            "street": column(row, "forretningsadresse.adresse")[0],
            "postcode": column(row, "forretningsadresse.postnummer")[0], "city": column(row, "forretningsadresse.poststed")[0]}


def generate(context):
    output = []
    seen = set()
    def add(value, origin, subunit_orgnr=None):
        url = normalize_url(value)
        root = domain(url) if url else ""
        if root and root not in seen and root not in SOCIAL | DIRECTORIES | FREE_MAIL:
            output.append(Candidate(url, root, origin,subunit_orgnr))
            seen.add(root)
    add(context.get("website"), "registry_website")
    email = str(context.get("email") or "")
    if "@" in email:
        add(email.rsplit("@", 1)[1], "registry_email")
    for unit in context.get('subunits',[]):
        add(unit.get('website'),'subunit_registry_website',unit['orgnr'])
        email=str(unit.get('email') or '')
        if '@' in email:add(email.rsplit('@',1)[1],'subunit_registry_email',unit['orgnr'])
    for nav_item in context.get('nav_homepages', []):
        if isinstance(nav_item, dict):
            add(nav_item.get('url') or nav_item.get('homepage'), 'nav_employer_homepage', nav_item.get('subunit_orgnr'))
        elif isinstance(nav_item, str):
            add(nav_item, 'nav_employer_homepage')
    if context.get('nav_homepage'):
        hp = context['nav_homepage']
        if isinstance(hp, dict):
            add(hp.get('url') or hp.get('homepage'), 'nav_employer_homepage', hp.get('subunit_orgnr'))
        elif isinstance(hp, str):
            add(hp, 'nav_employer_homepage')
    name = legal_name(context.get("name"))
    for slug in legal_name_slugs(name):
        add(slug, "legal_name_slug")
    return output[:8]
