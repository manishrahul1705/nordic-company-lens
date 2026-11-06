"""Step 11 nominations and bounded proof recovery; never search-engine discovery."""
import html
import json
import re
from urllib.parse import urlsplit, urljoin, urlencode, unquote
from .candidates import legal_name
from .policy import extract, domain, normalize_url
from .proof import Proof, score, phone
from .social import compact

DECLARED={'registry_email','subunit_registry_email','subunit_registry_website'}
PROOF_PATH=re.compile(r'kontakt|contact|om[-_/]?oss|about|personvern|privacy|impressum|vilk[aå]r|terms',re.I)


from .names import normalized


def registered_leaders(claims):
    return [c.value['name'] for c in claims if c.family=='roles' and isinstance(c.value,dict)
            and isinstance(c.value.get('name'),str) and not c.value.get('inactive')
            and (c.value.get('role_type') or {}).get('kode') in {'DAGL','LEDE'}]


def identity_text(page):
    return ' '.join([page.title,str(page.meta.get('og:site_name','')),*page.identity_headings,*page.logo_names,*page.footer_parts])


def named(page,name):
    core=normalized(legal_name(name))
    return bool(core and re.search(r'(?<!\w)'+re.escape(core)+r'(?!\w)',normalized(identity_text(page))))


def real_page(page,context):
    text=page.title+' '+page.visible
    if re.search(r'<frameset\b',page.raw,re.I):return 'frameset_placeholder'
    if re.search(r'<iframe\b',page.raw,re.I) and len(' '.join(page.visible.split()))<100:return 'frameset_placeholder'
    if re.search(r'\b(?:coming soon|under construction|website (?:is )?under maintenance|we are doing some work on our site|er til salgs|is for sale|domain parking|index of\b|directory listing|proudly served by|suspended account|account suspended|default web site|hosting placeholder)\b',text,re.I):return 'placeholder'
    if re.search(r'\b(?:this domain|domenet)\b.{0,50}\b(?:sale|parked|parkert|registrert)\b',text,re.I):return 'placeholder'
    # Plain footer company names are publisher identity too, not just copyright.
    expected={normalized(n) for n in [context.get('name'),*[u.get('name') for u in context.get('subunits',[])]] if n}
    from .proof import orgnrs
    own_ids=set(context.get('allowed_orgnrs',()))
    joined_footer=normalized(' '.join(page.footer_parts))
    split_own_footer=bool(own_ids and orgnrs(' '.join(page.brand_parts))<=own_ids and orgnrs(' '.join(page.brand_parts))
        and any(re.search(r'(?<!\w)'+re.escape(n)+r'(?!\w)',joined_footer) for n in expected))
    joined_headings=normalized(' '.join(page.identity_headings))
    split_own_heading=split_own_footer and joined_headings in expected
    for value in [page.title,*page.identity_headings,str(page.meta.get('og:site_name',''))]:
        for entity in re.findall(r'(?:^|[|—–:])\s*(AS\s+[A-ZÆØÅ][\wÆØÅæøå&.-]*(?:\s+[A-ZÆØÅ][\wÆØÅæøå&.-]*){0,4})',value):
            if compact(entity) not in {compact(n) for n in expected}:return 'different_legal_entity'
        for entity in re.findall(r'\b[A-ZÆØÅ0-9][\wÆØÅæøå&.-]*(?:\s+[A-ZÆØÅ0-9][\wÆØÅæøå&.-]*){0,5}\s+(?:AS|ASA|AB|Ltd|GmbH|Oy)\b',value):
            actual=normalized(entity)
            if split_own_heading and value in page.identity_headings and any(n.endswith(' '+actual) for n in expected):continue
            if not any(compact(name)==compact(actual) or name.endswith(' '+actual) for name in expected):return 'different_legal_entity'
    footer=' '.join(page.footer_parts)
    for value in page.footer_parts:
        if re.search(r'levert|design|utvikl|powered|nettside|endelav|en del av',value,re.I):continue
        position=footer.find(value)
        if re.search(r'levert|design|utvikl|powered|nettside|laget av|partner|medlem',footer[max(0,position-70):position],re.I):continue
        value=re.sub(r'^(?:Copyright\s*)?(?:\u00a9\s*)?(?:20\d\d\s*[-:]?\s*)?','',value,flags=re.I).strip(' \t\n|.,')
        own_footer=any(re.search(r'(?<!\w)'+re.escape(n)+r'(?!\w)',normalized(value)) for n in expected)
        # A line-broken own legal name is not a new publisher. Require both
        # the complete adjacent name and its exact owner identifier.
        if split_own_footer and any(n.endswith(' '+normalized(value)) for n in expected):own_footer=True
        if re.fullmatch(r'[\wÆØÅæøå& .-]{2,85}\s+(?:AS|ASA|AB|Ltd|GmbH|Oy)',value) and not own_footer:
            return 'different_legal_entity'
    return None


def provider_mismatch(page,context):
    code=str(context.get('nace') or '')
    text=page.title+' '+str(page.meta.get('description',''))+' '+str(page.meta.get('og:description',''))+' '+page.owner_text[:700]
    categories=[(r'regnskapsbyr[aå]|regnskapskontor|accounting (?:firm|services)|bokf[oø]ring',('69',)),
                (r'webbyr[aå]|web agency|webhotell|hosting (?:services|provider)|IT[- ](?:selskap|konsulent)|digital(?:t)? byr[aå]',('62','63','73'))]
    return any(re.search(pattern,text,re.I) and not code.startswith(prefixes) for pattern,prefixes in categories)


def declared_score(page,org,context,origin,leaders,options,enabled=True):
    from .names import proof_context
    context=proof_context(page,org,context)
    veto=real_page(page,context)
    if veto:return Proof('REJECT',reason=veto)
    if origin in DECLARED and provider_mismatch(page,context):return Proof('REJECT',reason='provider_industry_mismatch')
    original=score(page,org,context,origin,leaders,**options)
    if original.level in {'VERIFIED','REJECT','BLOCKED'}:return original
    if origin not in DECLARED or not enabled:return original
    from copy import copy
    identity_page=copy(page)
    identity_page.owner_text=page.owner_text+' '+' '.join(page.logo_names)
    declared=score(identity_page,org,context,'registry_website',leaders,**options)
    if declared.level=='VERIFIED' and declared.proof_type=='registry_declared_name_tier_a' and not named(page,context.get('name')):
        declared=score(page,org,{**context,'name':''},'registry_website',leaders,**options)
    # The Step 11 review found shared addresses on unrelated email-domain sites.
    # Keep the name-based declaration rule; retire its contact-only extension.
    if declared.proof_type=='registry_declared_hard_contact_tier_b':return original
    if declared.level=='VERIFIED':declared.rule='A' if origin=='registry_email' else 'B'
    return declared if declared.level=='VERIFIED' else original


def unique_eligible(page,context,leaders):
    core=legal_name(context.get('name'))
    if extract(page.url).suffix!='no' or extract(page.url).domain!=compact(core) or len(compact(core))<5 or not named(page,core) or real_page(page,context):return False
    text=normalized(page.owner_text)
    for key in ('postcode','municipality'):
        value=normalized(context.get(key))
        if value and (len(value)>=3) and re.search(r'(?<!\w)'+re.escape(value)+r'(?!\w)',text):return True
    result=score(page,'',context,'legal_name_slug',leaders)
    if set(result.signals)&{'phone','email'}:return True
    return any(isinstance(name,str) and len(name.split())>=2 and normalized(name) in text for name in leaders)


async def unique_registry(org,context,http):
    """Only a complete official query can establish registry-wide uniqueness."""
    cache=getattr(http,'unique_names',None)
    if cache is None:http.unique_names=cache={}
    if org in cache:return cache[org]
    cache[org]=[]
    if not getattr(http,'registry_http',None):return []
    from ..sources.extract import Section,add,response_source
    try:
        core=legal_name(context.get('name'))
        url='https://data.brreg.no/enhetsregisteret/api/enheter?'+urlencode({'navn':core,'size':1000})
        response=await http.registry_http.get(url,org)
        if response.status!=200:return []
        data=json.loads(response.body);entries=data.get('_embedded',{}).get('enheter',[]);page=data.get('page',{})
        if page.get('totalPages',2)>1 or page.get('totalElements')!=len(entries):return []
        if {str(r.get('organisasjonsnummer')) for r in entries if legal_name(r.get('navn'))==core}!={org}:return []
        support=Section();add(support,response_source(response),org,'website','registry_name_uniqueness',{'core':core,'orgnr':org},'/_embedded/enheter')
        cache[org]=support.evidence
    except Exception:pass
    return cache[org]


async def proof_targets(page,url,http,org,existing):
    """Sitemap is nomination only; HTML proof remains bounded to six pages."""
    found=[l.href for l in page.links if l.template_context and PROOF_PATH.search(unquote(l.href+' '+l.text))]
    try:
        response=await http.get(urljoin(url,'/sitemap.xml'),org,domain(url),xml=True)
        if response.status==200 and not re.search(br'<!\s*(?:DOCTYPE|ENTITY)',response.body,re.I):
            import xml.etree.ElementTree as ET
            root=ET.fromstring(response.body)
            if root.tag.rsplit('}',1)[-1]=='sitemapindex':
                children=[e.text.strip() for e in root.iter() if e.tag.rsplit('}',1)[-1]=='loc' and e.text and domain(e.text)==domain(url)]
                children.sort(key=lambda child:('page' not in child,child))
                if children:
                    child=await http.get(children[0],org,domain(url),xml=True)
                    if child.status==200 and not re.search(br'<!\s*(?:DOCTYPE|ENTITY)',child.body,re.I):root=ET.fromstring(child.body)
            found += [e.text.strip() for e in root.iter() if e.tag.rsplit('}',1)[-1]=='loc' and e.text and PROOF_PATH.search(unquote(e.text))]
    except Exception:pass
    return list(dict.fromkeys(u for value in [*found,*existing] if (u:=normalize_url(urljoin(url,value))) and domain(u)==domain(url)))[:5]
