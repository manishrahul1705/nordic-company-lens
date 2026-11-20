"""One advertised same-domain news resource, only for already verified publishers."""
import re
import html
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from datetime import datetime,date,timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urljoin,urlsplit
from ..budget import SourceFailure
from ..models.evidence import digest
from ..sources.extract import Section,Source,add
from ..sources.text import decode_body
from .policy import domain,normalize_url

MONTHS={m:i for i,pair in enumerate([('januar','january'),('februar','february'),('mars','march'),('april','april'),('mai','may'),('juni','june'),('juli','july'),('august','august'),('september','september'),('oktober','october'),('november','november'),('desember','december')],1) for m in pair}


def explicit_date(text,today=None):
    raw=(text or '').strip()
    try:
        if re.fullmatch(r'\d{4}-\d{2}-\d{2}(?:T.*)?',raw):d=datetime.fromisoformat(raw.replace('Z','+00:00')).date()
        elif re.fullmatch(r'\d{1,2}\.\d{1,2}\.\d{4}',raw):d=datetime.strptime(raw,'%d.%m.%Y').date()
        else:
            m=re.fullmatch(r'(\d{1,2})\.?\s+([A-Za-z]+)\s+(\d{4})',raw)
            if m and m[2].lower() in MONTHS:d=date(int(m[3]),MONTHS[m[2].lower()],int(m[1]))
            else:d=parsedate_to_datetime(raw).date()
        return d.isoformat() if d<=(today or datetime.now(timezone.utc).date()) else None
    except (ValueError,TypeError,OverflowError,KeyError):return None


def same_url(raw,base):
    url=normalize_url(urljoin(base,raw or ''))
    if not url or domain(url)!=domain(base):return None
    return url


class Advertisements(HTMLParser):
    def __init__(self,base):super().__init__();self.base=base;self.feeds=[];self.maps=[];self.nav=[];self.anchor=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='link' and 'alternate' in a.get('rel','').lower().split() and a.get('type','').lower() in {'application/rss+xml','application/atom+xml'}:
            if u:=same_url(a.get('href'),self.base):self.feeds.append((u,'feed'))
        if tag=='link' and a.get('rel','').lower()=='sitemap':
            if u:=same_url(a.get('href'),self.base):self.maps.append((u,'sitemap'))
        if tag=='a':self.anchor=[a.get('href',''),'']
    def handle_data(self,data):
        if self.anchor:self.anchor[1]+=data
    def handle_endtag(self,tag):
        if tag!='a' or self.anchor is None:return
        href,text=self.anchor;self.anchor=None;u=same_url(href,self.base)
        if not u:return
        if re.search(r'(?:^|/)sitemap[^/]*\.xml$',urlsplit(u).path,re.I):self.maps.append((u,'sitemap'))
        elif re.search(r'(?i)(?:^|[ /_-])(news|nyheter|aktuelt|presse|press)(?:$|[ /_-])',text+' '+urlsplit(u).path):self.nav.append((u,'html'))


def discover(home):
    p=Advertisements(home.url);p.feed(home.raw)
    found=p.feeds+p.maps+p.nav
    return next(iter(found),None)


def local(tag):return tag.rsplit('}',1)[-1]


def extract(body,url,kind):
    text=decode_body(body);items=[]
    def put(title,rawdate,target,locator,date_kind):
        target=same_url(target,url);day=explicit_date(rawdate)
        title=' '.join(html.unescape(title or '').split())
        if target and day and title and len(title)<=400:items.append({'title':title,'date':day,'url':target,'date_kind':date_kind,'locator':locator})
    if kind in {'feed','sitemap'}:
        if '<!DOCTYPE' in text.upper() or '<!ENTITY' in text.upper():return []
        try:root=ET.fromstring(text)
        except ET.ParseError:return []
        for n,node in enumerate(root.iter()):
            tag=local(node.tag)
            if tag not in {'item','entry','url'}:continue
            values={local(x.tag):''.join(x.itertext()).strip() for x in node}
            target=values.get('link') or values.get('loc')
            if tag=='entry':target=next((x.attrib.get('href') for x in node if local(x.tag)=='link' and x.attrib.get('rel','alternate')=='alternate'),None)
            if tag=='url':
                # Sitemap URLs lack editorial titles: publish only an explicit
                # image/news title, never invent a title from the URL slug.
                title=next((''.join(x.itertext()).strip() for x in node.iter() if local(x.tag)=='title'),None)
                rawdate=values.get('lastmod');date_kind='sitemap last modification (not publication date)'
            else:
                title=values.get('title');rawdate=values.get('pubDate') or values.get('published') or values.get('updated');date_kind='feed publication' if values.get('pubDate') or values.get('published') else 'feed update'
            put(title,rawdate,target,'XML record '+str(n),date_kind)
    else:
        # Each article/card must contain its own explicit date and headline link.
        for n,m in enumerate(re.finditer(r'<article\b[^>]*>(.*?)</article\s*>',text,re.I|re.S)):
            block=m[1]
            if re.search(r'<(?:script|style)\b',block,re.I):block=re.sub(r'<(script|style)\b.*?</\1>', '',block,flags=re.I|re.S)
            a=re.search(r'<a\b[^>]*href=[\"\']([^\"\']+)[\"\'][^>]*>(.*?)</a>',block,re.I|re.S)
            tm=re.search(r'<time\b([^>]*)>(.*?)</time>',block,re.I|re.S)
            if not a or not tm:continue
            attr=re.search(r'datetime=[\"\']([^\"\']+)',tm[1],re.I)
            rawdate=attr[1] if attr else re.sub('<[^>]+>','',tm[2]).strip()
            title=re.sub('<[^>]+>','',a[2]);put(title,rawdate,a[1],'article['+str(n)+']','page explicit date')
    unique={}
    for item in sorted(items,key=lambda x:(x['date'],x['url']),reverse=True):unique.setdefault(item['url'],item)
    return list(unique.values())[:5]


async def collect(envelope,http,pages):
    proof=next((c for c in envelope.claims if c.field=='official_website' and c.availability=='available' and c.value.get('identity_level')=='VERIFIED'),None)
    if proof is None or proof.carried_forward or proof.value.get('content_allowed') is False or proof.value.get('relationship_note')=='group_site':return
    org=envelope.organisation_number;diag={'scope':'verified website only','published':0,'resource_requests':0}
    envelope.run.refresh['news_items']=diag
    base=proof.value['final_url'];home=next(((r,p) for r,p in pages if domain(r.url)==domain(base) and urlsplit(r.url).path in {'','/'}),None)
    if home is None:diag['state']='no_fetched_homepage';return
    target=discover(home[1])
    if target is None:diag['state']='no_discoverable_resource';return
    url,kind=target;diag.update(resource_url=url,resource_kind=kind)
    try:
        cached=next((r for r,p in pages if r.url==url),None)
        if cached is None:
            diag['resource_requests']=1
            # Existing fetcher enforces robots for this exact path, budgets,
            # DNS/SSRF/TLS, body caps and same-domain redirect restrictions.
            response=await http.get_news_resource(url,org,domain(base),xml=kind!='html')
        else:response=cached
        if response.status!=200:diag.update(state='fetch_failed',reason='HTTP '+str(response.status));return
        section=Section();source=Source(response.url,response.body,response.sha,response.retrieved_at)
        for item in extract(response.body,response.url,kind):
            locator=item.pop('locator');span=source.excerpt(item['title'],locator)
            add(section,source,org,'activity','news_item.'+digest(item['url'])[:20],{**item,'source_url':response.url,'identity_claim_id':proof.id},locator,span=span,source_class='company_owned',method='signalpost.news.explicit-date.v1')
            section.claims[-1].evidence_ids.append(proof.evidence_ids[0])
            section.claims[-1].reasons['label']='Company news / dated item'
        envelope.claims.extend(section.claims);envelope.evidence.extend(section.evidence)
        diag.update(state='published' if section.claims else 'no_explicit_dated_items',published=len(section.claims))
    except SourceFailure as exc:diag.update(state='withheld',reason=exc.code)
