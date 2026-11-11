"""Additional registry-backed proofs, evaluated only after existing identity vetoes."""
import re
from . import shared_identifiers
from .shared_identifiers import phone_key, name_key, name_tokens, folded
from .policy import FREE_MAIL, extract, domain


def additional_proof(page, org, context):
    from .proof import Proof, orgnrs
    # These new rules do not waive page-wide conflicts or foreign-entity checks.
    if orgnrs(page.visible) - {org}:
        return None
    from .entity_scope import foreign_entity_page
    if foreign_entity_page(page, org, context.get('name'), check_ids=False):
        return None
    counts = shared_identifiers.bundled('shared_identifiers.json.gz')
    text = page.owner_text
    email = str(context.get('email') or '').strip().casefold()
    email_domain = email.rsplit('@', 1)[-1] if '@' in email else ''
    emails = set(re.findall(r'(?<![\w.+-])[\w.+-]+@(?:[a-z0-9-]+\.)+[a-z]{2,}(?![\w-])', text.casefold()))
    emails.update(link.href[7:].split('?')[0].casefold() for link in page.links if link.href.casefold().startswith('mailto:'))
    frequency = counts.get('email_domains', {}).get(email_domain, 0)
    if email in emails and email_domain not in FREE_MAIL and 0 < frequency < 5:
        return Proof('VERIFIED','registry_email_on_site',['registry_email'],token=email)
    numbers = {phone_key(link.href[4:]): link.href[4:] for link in page.links if link.href.startswith('tel:')}
    for match in re.finditer(r'(?<![\d+])(?:(?:\+47|0047)[ .-]*)?(?:\d[ .()-]*){8}(?!\d)', text):
        numbers[phone_key(match.group())] = match.group()
    for value in (context.get('phone'), context.get('mobile')):
        number = phone_key(value)
        frequency = counts.get('phones', {}).get(number, 0)
        if number and number in numbers and 0 < frequency < 5:
            return Proof('VERIFIED','registry_phone_on_site',['registry_phone'],token=numbers[number])
    normal = lambda s: ' '.join(re.findall(r'\w+', str(s or '').casefold()))
    name = normal(context.get('name'))
    def own_name(segment):
        # A complete entity phrase must equal ours; a preceding distinctive word
        # makes it a longer legal name, not an occurrence of this company.
        segment = re.sub(r'^(?:copyright|\u00a9)\s*(?:20\d\d\s*)?', '', segment, flags=re.I)
        segment = normal(segment)
        return segment == name
    if re.search(r'\b(?:as|asa)$',name):
        masthead = any(own_name(part.strip()) for part in re.split(r'[|\u2013\u2014]|\s+-\s+',page.title))
        for part in re.split(r'[\n|\u00a9]',text):
            if 'copyright' in part.casefold() or ('\u00a9'+part) in text:
                phrase = re.split(r'\b(?:all rights|alle rettigheter|org\.?\s*nr)\b',part,flags=re.I)[0]
                phrase = re.sub(r'^\s*20\d\d\s*', '', phrase)
                masthead |= own_name(phrase.strip())
        postcode = str(context.get('postcode') or '')
        if re.fullmatch(r'\d{4}',postcode):
            for match in re.finditer(r'(?<!\d)'+postcode+r'(?!\d)',text):
                window = text[max(0,match.start()-150):match.end()+150]
                for phrase in re.findall(r'(?:^|[\n|:;])\s*([^\n|:;]{1,100}?\b(?:AS|ASA))\b',window,re.I):
                    masthead |= own_name(phrase.strip())
        if masthead:
            return Proof('VERIFIED','legal_name_masthead',['full_legal_name'],token=str(context['name']))
    tokens = name_tokens(context.get('name'))
    key = name_key(context.get('name'))
    host = extract(page.url)
    label = folded(host.domain)
    page_words = set(re.findall(r'[a-z0-9]+',folded(text)))
    if (host.suffix == 'no' and tokens and key
            and label in {''.join(tokens), '-'.join(tokens)}
            and set(key.split()) <= page_words
            and counts.get('name_keys', {}).get(key) == 1):
        return Proof('VERIFIED','unique_legal_name_domain',['unique_name_key','exact_no_domain'],token=next(iter(key.split())))
    return None
