"""Typed locations projected from original registry claims, without new research."""
import re
from .web.proof import normalized_address


def address_key(address):
    address = address or {}
    street = address.get('adresse') or address.get('street') or []
    if isinstance(street, list):street = ' '.join(str(v) for v in street)
    street = normalized_address(street)
    street = re.sub(r'^(?:pb|p b|postbok|postboks|postbox|boks)\s*(\d+)\b',r'postboks \1',street)
    postcode = re.sub(r'\D', '', str(address.get('postnummer') or address.get('postcode') or ''))
    return (street, postcode) if street and postcode else None


def registered_location(claims):
    """Use the exact-parent address only when no workplace duplicates it."""
    address = next((c for c in claims if c.field == 'identity.registered_address' and c.availability == 'available'), None)
    if address is None or not isinstance(address.value, dict) or not address_key(address.value):return None
    workplaces = [c.value.get('address') for c in claims if c.availability == 'available' and c.field.startswith('subunits.unit.') and isinstance(c.value, dict)]
    return address if all(address_key(a) != address_key(address.value) for a in workplaces) else None
