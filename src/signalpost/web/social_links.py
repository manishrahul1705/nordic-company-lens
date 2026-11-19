"""Company-page link evidence with explicit person, context and scope vetoes."""
import re
from html.parser import HTMLParser
from urllib.parse import parse_qs,urlsplit,urljoin,unquote
from .policy import domain

VOID={'meta','link','img','br','hr','input','source','area','base','embed','wbr'}


def links(page, *, eligible=False):
    from .social import profile_url
    output={}
    class Parser(HTMLParser):
        def __init__(self):super().__init__(convert_charrefs=True);self.stack=[]
        def handle_starttag(self,tag,pairs):
            attrs=dict(pairs);classes=(attrs.get('class') or '')+' '+(attrs.get('id') or '')
            hidden=('hidden' in attrs or attrs.get('aria-hidden')=='true' or
                    bool(re.search(r'display\s*:\s*none|visibility\s*:\s*hidden',attrs.get('style') or '',re.I)))
            # Layout-wide CMS configuration classes do not make the whole page
            # a share widget. WordPress type-page articles are ordinary pages.
            excluded=(tag in {'script','style','template','noscript'} or hidden
                or tag not in {'html','body'} and bool(re.search(r'(?:^|\s)(?:social[-_]?share|share[-_]?buttons?|sharer|agency[-_]?credit|site[-_]?credit|employee|staff[-_]?profile)(?:\s|[-_]|$)',classes,re.I))
                or tag=='article' and not re.search(r'(?:^|\s)type-page(?:\s|$)',classes))
            blocked=excluded or any(self.stack[i][1] for i in range(len(self.stack)))
            if tag not in VOID:self.stack.append((tag,blocked))
            if eligible and blocked:return
            target=None
            if tag=='a':target=urljoin(page.url,attrs.get('href') or '')
            elif tag=='meta' and (attrs.get('property') or attrs.get('name') or '').casefold()=='og:see_also':
                target=attrs.get('content')
            elif tag=='iframe':
                src=urljoin(page.url,attrs.get('src') or '')
                p=urlsplit(src)
                if domain(src)=='facebook.com' and re.fullmatch(r'/(?:v\d+(?:\.\d+)?/)?plugins/(?:page|likebox)\.php',p.path):
                    target=parse_qs(p.query).get('href',[''])[0]
            elif tag=='div' and 'fb-page' in classes.split():target=attrs.get('data-href')
            if target and (url:=profile_url(target)):
                raw=self.get_starttag_text()
                # Standard evidence rules require a verbatim bounded span.
                needle=target if target in raw else 'href' if 'href' in raw else 'content'
                start=max(0,raw.find(needle)-30)
                output.setdefault(url,raw[start:start+300])
        def handle_endtag(self,tag):
            for i in range(len(self.stack)-1,-1,-1):
                if self.stack[i][0]==tag:self.stack=self.stack[:i];break
    Parser().feed(page.raw)
    return output


def handle(url):
    from .social import compact
    p=urlsplit(url);bits=[unquote(x) for x in p.path.split('/') if x]
    if not bits:return ''
    value=bits[1] if domain(url)=='facebook.com' and bits[0].lower()=='pages' and len(bits)==3 else bits[-1]
    if domain(url)=='facebook.com':value=re.sub(r'-\d{5,}$','',value)
    return compact(value.lstrip('@'))


def veto(url,context):
    from .social import compact,matches_profile,social_company_names
    from .candidates import legal_name
    value=handle(url)
    for name in context.get('role_person_names',[]):
        parts=str(name).split()
        aliases={compact(name)}
        if len(parts)>1:aliases.add(compact(parts[0]+parts[-1]))
        if any(alias and re.fullmatch(re.escape(alias)+r'\d{0,6}',value) for alias in aliases):
            return 'own_registry_person'
    if re.search(r'(?:design|designer|agency|webdesign|byraa)$',value) and not matches_profile(url,social_company_names(context)):
        return 'unattributed_designer_or_agency_handle'
    from .social_universe import assess
    universe=assess(url,context)
    if universe['state']=='withhold':
        return universe['reason']
    if any(value in {compact(name),compact(legal_name(name))}
           for name in context.get('other_company_names',[]) if name):
        return 'other_cohort_company'
    return None


def proven_links(page,proof,context):
    """None means legacy/unproven path, empty dict means proven but vetoed."""
    from .social import organization_social,path_scope
    if proof.get('identity_level')!='VERIFIED':return None
    if (proof.get('content_allowed') is False or proof.get('relationship_note')=='group_site'
        or proof.get('other_orgnrs') or domain(page.url)!=domain(proof.get('final_url',''))):return {}
    scope=path_scope(proof,context)
    if scope:
        # Retain the existing strict branch/template policy on shared domains.
        return None
    found=links(page,eligible=True)
    for url,span in organization_social(page,context).items():found.setdefault(url,span)
    return {url:span for url,span in found.items() if not veto(url,context)}
