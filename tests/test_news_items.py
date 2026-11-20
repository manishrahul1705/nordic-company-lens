import asyncio
from datetime import date
from types import SimpleNamespace
import pytest
from signalpost.web.news_items import explicit_date,discover,extract,collect
from signalpost.web.html import Page
from signalpost.sources.extract import Section,Source,add
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.http import Response
from signalpost.models.evidence import utc_now
from signalpost.runner import placeholder
from signalpost.budget import SourceFailure

BASE='https://example.no/'


@pytest.mark.parametrize('raw,expected',[
 ('2026-11-19','2026-11-19'),('2026-11-19T10:00:00Z','2026-11-19'),
 ('19.11.2026','2026-11-19'),('19. november 2026','2026-11-19'),('19 November 2026','2026-11-19'),
 ('Thu, 19 Nov 2026 12:00:00 GMT','2026-11-19'),('2026-02-30',None),('2027-01-01',None),
 ('2026',None),('11/12/2026',None),('yesterday',None),('',None)])
def test_explicit_dates(raw,expected):assert explicit_date(raw,date(2026,11,20))==expected


def test_feed_precedes_nav_and_cross_domain_is_never_selected():
    p=Page(b'<a href="/news">News</a><link rel="alternate" type="application/rss+xml" href="https://foreign.no/feed"><link rel="alternate" type="application/atom+xml" href="/feed">',BASE)
    assert discover(p)==(BASE+'feed','feed')


def test_no_discoverable_feed_or_nav():assert discover(Page(b'<a href="/products">Products</a>',BASE)) is None


def test_sitemap_reference_only_no_automatic_path_guess():
    assert discover(Page(b'<link rel="sitemap" href="/sitemap.xml">',BASE))==(BASE+'sitemap.xml','sitemap')
    assert discover(Page(b'no links',BASE)) is None


def test_rss_cap_sort_dedupe_and_exact_domain():
    body='<rss><channel>'+''.join(f'<item><title>Story {i}</title><pubDate>2026-11-{i:02}</pubDate><link>{BASE}news/{i}</link></item>' for i in range(1,9))+'<item><title>Foreign</title><pubDate>2026-11-19</pubDate><link>https://foreign.no/x</link></item></channel></rss>'
    r=extract(body.encode(),BASE+'feed','feed');assert len(r)==5 and r[0]['title']=='Story 8' and r[-1]['title']=='Story 4'


def test_atom_and_future_and_no_date():
    b=b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Own</title><published>2026-01-01T10:00:00Z</published><link href="/news/1"/></entry><entry><title>No date</title><link href="/news/2"/></entry></feed>'
    assert [x['title'] for x in extract(b,BASE+'feed','feed')]==['Own']


def test_sitemap_lastmod_is_not_called_publication_and_no_invented_title():
    b=b'<urlset><url><loc>https://example.no/news/1</loc><lastmod>2026-01-01</lastmod><title>Explicit title</title></url><url><loc>https://example.no/news/2</loc><lastmod>2026-01-01</lastmod></url></urlset>'
    r=extract(b,BASE+'sitemap.xml','sitemap');assert len(r)==1 and 'not publication' in r[0]['date_kind']


def test_visible_article_date_is_local_to_item():
    b=b'<article><a href="/news/1"><h2>Own story</h2></a><time datetime="2026-01-02">2 January 2026</time></article><article><a href="/news/2">Undated</a></article>'
    r=extract(b,BASE+'news','html');assert len(r)==1 and r[0]['title']=='Own story'


def test_xml_entity_declarations_are_rejected():assert extract(b'<!DOCTYPE foo><rss/>',BASE,'feed')==[]


def setup(tmp_path,verified=True):
    row=placeholder('923609016','test',utc_now());section=Section();body=b'<link rel="alternate" type="application/rss+xml" href="/feed">'
    blobs=BlobStore(tmp_path/'state');sha=blobs.put(body);response=Response(body,200,BASE,utc_now(),sha)
    add(section,Source(BASE,body,sha,response.retrieved_at),row.organisation_number,'website','official_website',{'identity_level':'VERIFIED' if verified else 'HIGH','final_url':BASE},'/')
    row.claims.extend(section.claims);row.evidence.extend(section.evidence);return row,[(response,Page(body,BASE))],blobs


@pytest.mark.parametrize('code',['robots','company_budget_exhausted','budget_exhausted','deadline'])
def test_fetcher_veto_withholds_without_placeholder(tmp_path,code):
    row,pages,blobs=setup(tmp_path)
    class HTTP:
        async def get_news_resource(self,*a,**kw):raise SourceFailure(code)
    asyncio.run(collect(row,HTTP(),pages));assert not any(c.field.startswith('news_item.') for c in row.claims)
    assert row.run.refresh['news_items']['reason']==code


def test_unverified_site_makes_no_request(tmp_path):
    row,pages,blobs=setup(tmp_path,False)
    class HTTP:
        async def get_news_resource(self,*a,**kw):raise AssertionError('must not fetch')
    asyncio.run(collect(row,HTTP(),pages));assert 'news_items' not in row.run.refresh


def test_one_resource_and_exact_retained_evidence(tmp_path):
    row,pages,blobs=setup(tmp_path);calls=[];raw=b'<rss><channel><item><title>Story</title><pubDate>2026-01-01</pubDate><link>https://example.no/news/1</link></item></channel></rss>'
    class HTTP:
        async def get_news_resource(self,url,org,host,**kw):
            calls.append((url,host,kw));return Response(raw,200,url,utc_now(),blobs.put(raw))
    asyncio.run(collect(row,HTTP(),pages));claims=[c for c in row.claims if c.field.startswith('news_item.')]
    assert len(calls)==len(claims)==1 and calls[0][2]['xml'] is True
    ev=next(e for e in row.evidence if e.id==claims[0].evidence_ids[0]);assert ev.claim_span in raw.decode() and len(ev.claim_span)<=300
    assert claims[0].value['source_url']==BASE+'feed' and claims[0].value['date']=='2026-01-01'


@pytest.mark.parametrize('blocked,cap,expected',[(True,40,'robots'),(False,1,'budget_exhausted'),(False,40,None)])
def test_real_fetcher_robots_and_pooled_budget(tmp_path,blocked,cap,expected):
    import httpx,respx
    from signalpost.config import Config
    from signalpost.budget import Budget
    from signalpost.web.fetcher import WebsiteHttp
    row,pages,blobs=setup(tmp_path);inputs=tmp_path/'input.txt';inputs.write_text(row.organisation_number)
    cfg=Config(organisations=inputs,output=tmp_path/'out',report=tmp_path/'report',max_requests=cap)
    budget=Budget(cfg);seen=[]
    async def resolver(*args):return ['93.184.216.34']
    def response(request):
        seen.append(str(request.url))
        if request.url.path=='/robots.txt':return httpx.Response(200,text='User-agent: *\n'+('Disallow: /feed' if blocked else 'Allow: /'))
        return httpx.Response(200,headers={'content-type':'application/rss+xml'},content=b'<rss><channel><item><title>Story</title><pubDate>2026-01-01</pubDate><link>https://example.no/news/1</link></item></channel></rss>')
    async def run():
        async with httpx.AsyncClient() as client:
            http=WebsiteHttp(client,cfg,budget,blobs,resolver)
            with respx.mock(assert_all_called=False) as router:
                router.route().mock(side_effect=response)
                await collect(row,http,pages)
    asyncio.run(run())
    if expected:assert row.run.refresh['news_items']['reason']==expected
    else:assert row.run.refresh['news_items']['published']==1
    assert len(budget.events)<=cap
    assert len([u for u in seen if u.endswith('/feed')])==(0 if expected else 1)


def test_real_fetcher_rejects_cross_domain_redirect_without_request(tmp_path):
    import httpx,respx
    from signalpost.config import Config
    from signalpost.budget import Budget
    from signalpost.web.fetcher import WebsiteHttp
    row,pages,blobs=setup(tmp_path);inputs=tmp_path/'input.txt';inputs.write_text(row.organisation_number)
    cfg=Config(organisations=inputs,output=tmp_path/'out',report=tmp_path/'report');budget=Budget(cfg);seen=[]
    async def resolver(*args):return ['93.184.216.34']
    def reply(request):
        seen.append(str(request.url))
        if request.url.path=='/robots.txt':return httpx.Response(200,text='User-agent: *\nAllow: /')
        return httpx.Response(302,headers={'location':'https://foreign.no/feed'})
    async def run():
        async with httpx.AsyncClient() as client:
            http=WebsiteHttp(client,cfg,budget,blobs,resolver)
            with respx.mock(assert_all_called=False) as router:
                router.route().mock(side_effect=reply);await collect(row,http,pages)
    asyncio.run(run());assert not any('foreign.no' in u for u in seen)
    assert not any(c.field.startswith('news_item.') for c in row.claims)
