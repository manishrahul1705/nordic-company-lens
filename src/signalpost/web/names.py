"""Comparison-only repairs: never rewrite the registry's published facts."""
import re
import unicodedata


def normalized(value):
    value=str(value or '')
    if 'Ã' in value or 'Â' in value:
        try:value=value.encode('latin1').decode('utf8')
        except (UnicodeError,ValueError):pass
    value=value.casefold().replace('ø','o').replace('æ','ae')
    value=''.join(c for c in unicodedata.normalize('NFKD',value) if not unicodedata.combining(c))
    return ' '.join(re.findall(r'[\w\ufffd]+',value))


def same_name(expected,actual,own_number=False,title_variant=False):
    left=normalized(expected).replace(' ','');right=normalized(actual).replace(' ','')
    if left==right:return True
    if not own_number:return False
    if 0<left.count('\ufffd')<=2 and re.fullmatch(re.escape(left).replace('\ufffd','[a-z]'),right):return True
    # Singular/plural spelling in a title needs the exact owner identifier;
    # legal forms must still agree, so AS/AB can never be repaired this way.
    if title_variant:
        a=re.fullmatch(r'(.{8,}?)(as|asa|ab|ltd|gmbh|oy)',left)
        b=re.fullmatch(r'(.{8,}?)(as|asa|ab|ltd|gmbh|oy)',right)
        if a and b and a[2]==b[2] and a[1].rstrip('s')==b[1].rstrip('s'):return True
    return False


def proof_context(page,org,context):
    from .proof import orgnrs
    # Only a number in publisher/header/footer context permits a damaged-name
    # repair. A customer/article reference to our orgnr cannot trigger it.
    if orgnrs(' '.join(page.brand_parts))!={org}:return context
    names=[page.title,' '.join(page.identity_headings)]
    for value in list(names):
        names+=re.findall(r'\b[A-ZÆØÅ][\wÆØÅæøå&.-]*(?:\s+[A-ZÆØÅ][\wÆØÅæøå&.-]*){0,5}\s+(?:AS|ASA|AB|Ltd|GmbH|Oy)\b',value)
    for part in page.footer_parts:
        names+=re.findall(r'\b[A-ZÆØÅ][\wÆØÅæøå&.-]*(?:\s+[A-ZÆØÅ][\wÆØÅæøå&.-]*){0,5}\s+(?:AS|ASA|AB|Ltd|GmbH|Oy)\b',part)
    for name in names:
        if same_name(context.get('name'),name,True,title_variant=True) or owner_descriptor_alias(page,org,context,name):
            return {**context,'name':name}
    return context


def owner_descriptor_alias(page,org,context,name):
    """One omitted trading descriptor is not a different identified publisher.

    This comparison repair never proves a site by name: the caller requires
    the sole publisher/header/footer orgnr to be the exact subject number.
    All ownership scoring and final vetoes still run with the actual page.
    """
    expected=normalized(context.get('name')).split()
    actual=normalized(name).split()
    if len(expected)<4 or expected[-2:]!=['forretning','as']:
        return False
    title_parts={normalized(part) for part in re.split(r'[|\u2013\u2014]',page.title)}
    if actual!=expected[:-2]+['as'] or normalized(name) not in title_parts:
        return False
    footer=normalized(' '.join(page.footer_parts))
    if not re.search(r'(?<!\w)'+re.escape(' '.join(actual))+r'(?!\w)',footer):
        return False
    from .proof import orgnrs
    if orgnrs(' '.join(page.brand_parts))!={org}:
        return False
    # A shortened name registered to someone else remains a different entity.
    # Missing/corrupt universe data cannot authorize a comparison repair.
    from .social_universe import index,name_keys
    data=index()
    if data is None:return False
    matches={other for key in name_keys(name) for other in data['keys'].get(key,[])}
    return not (matches-{org})
