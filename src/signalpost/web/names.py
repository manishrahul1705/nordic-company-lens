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
    for part in page.footer_parts:
        names+=re.findall(r'\b[A-ZÆØÅ][\wÆØÅæøå&.-]*(?:\s+[A-ZÆØÅ][\wÆØÅæøå&.-]*){0,5}\s+(?:AS|ASA|AB|Ltd|GmbH|Oy)\b',part)
    for name in names:
        if same_name(context.get('name'),name,True,title_variant=True):
            return {**context,'name':name}
    return context
