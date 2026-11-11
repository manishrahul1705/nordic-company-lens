"""Additional registry-backed proofs, evaluated only after existing identity vetoes."""
import re
from . import shared_identifiers
from .shared_identifiers import phone_key
from .policy import FREE_MAIL


def additional_proof(page, org, context):
    from .proof import Proof, orgnrs
    # These new rules do not waive page-wide conflicts or foreign-entity checks.
    if orgnrs(page.visible) - {org}:
        return None
    from .entity_scope import foreign_entity_page
    if foreign_entity_page(page, org, context.get('name'), check_ids=False):
        return None
    text = page.owner_text
    # A title/URL in a blank application shell or parked placeholder is not
    # independent ownership evidence for these additional rules.
    if not text.strip() or (len(text.strip()) < 200 and re.match(r'\s*her kommer\b', text, re.I)):
        return None
    counts = shared_identifiers.bundled('shared_identifiers.json.gz')
    email = str(context.get('email') or '').strip().casefold()
    email_domain = email.rsplit('@', 1)[-1] if '@' in email else ''
    emails = set(re.findall(r'(?<![\w.+-])[\w.+-]+@(?:[a-z0-9-]+\.)+[a-z]{2,}(?![\w-])', text.casefold()))
    emails.update(link.href[7:].split('?')[0].casefold() for link in page.links if link.href.casefold().startswith('mailto:'))
    frequency = counts.get('email_domains', {}).get(email_domain, 0)
    if email in emails and email_domain not in FREE_MAIL and frequency == 1:
        return Proof('VERIFIED','registry_email_on_site',['registry_email'],token=email)
    numbers = {phone_key(link.href[4:]): link.href[4:] for link in page.links if link.href.startswith('tel:')}
    for match in re.finditer(r'(?<![\d+])(?:(?:\+47|0047)[ .-]*)?(?:\d[ .()-]*){8}(?!\d)', text):
        numbers[phone_key(match.group())] = match.group()
    for value in (context.get('phone'), context.get('mobile')):
        number = phone_key(value)
        frequency = counts.get('phones', {}).get(number, 0)
        if number and number in numbers and 0 < frequency < 5:
            return Proof('VERIFIED','registry_phone_on_site',['registry_phone'],token=numbers[number])
    return None
