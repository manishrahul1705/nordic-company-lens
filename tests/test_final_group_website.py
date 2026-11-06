from types import SimpleNamespace

import pytest

from signalpost.web.html import Page
from signalpost.web.entity_scope import unproven_global_site, enforce
from signalpost.runner import placeholder, update
from signalpost.sources.extract import Source, Section, add
from signalpost.sources.blobstore import BlobStore

ORG='923609016'
CONTEXT={'name':'Permobil AS','phone':'12345678','email':'office@example.no','street':['Gate 12']}


def page(body, url='https://example.com/'):
    return Page(('<html><title>Permobil</title><body>'+body+'</body></html>').encode(),url)


@pytest.mark.parametrize('body,url,withhold',[
    ('Permobil <footer>Copyright Permobil AB</footer>','https://example.com/',True),
    ('Permobil <footer>Copyright Permobil</footer>','https://example.com/',True),
    ('Permobil <footer>Copyright Permobil</footer>','https://example.no/',False),
    ('Permobil <footer>Copyright Permobil AS</footer>','https://example.com/',False),
    ('<main>We established Permobil AS in Norway.</main>','https://example.com/',False),
    ('Permobil AS <footer>Copyright Permobil AB</footer>','https://example.com/',True),
    ('Permobil <footer>Org nr '+ORG+'</footer>','https://example.com/',False),
    ('Permobil <a href="mailto:office@example.no">Email</a>','https://example.com/',False),
    ('Permobil <a href="tel:+4712345678">Phone</a>','https://example.com/',False),
    ('Permobil <footer>Gate 12</footer>','https://example.com/',False),
    ('Permobil <footer>Other street 99; other@example.no</footer>','https://example.com/',True),
])
def test_non_no_brand_only_needs_norwegian_entity_or_registered_corroboration(body,url,withhold):
    assert unproven_global_site([page(body,url)],ORG,CONTEXT,url)==withhold


def test_contact_on_fetched_proof_page_can_establish_norwegian_connection():
    pages=[page('Permobil'),page('Gate 12','https://example.com/contact')]
    assert not unproven_global_site(pages,ORG,CONTEXT,'https://example.com')


def test_live_collection_withholds_brand_only_group_without_attaching_content(tmp_path,monkeypatch):
    import httpx
    from tests.test_websites import execute_web
    body='<html><title>Example</title><main>Example products</main><footer>Copyright Example</footer></html>'
    def response(request):
        if request.url.path=='/robots.txt':return httpx.Response(200,text='User-agent: *\nAllow: /')
        return httpx.Response(200,text=body) if request.url.path=='/' else httpx.Response(404)
    _,row,_,_=execute_web(tmp_path,monkeypatch,response=response,website='https://example.com/')
    assert row['run']['sections']['website']=='ambiguous'
    assert not any(c['field']=='official_website' or c['field'].startswith(('social_profile.','website_description.')) for c in row['claims'])
    assert any(e['code']=='group_site' and e['message']=='group website' for e in row['errors'])


def test_about_page_norwegian_entity_support_survives_final_guard(tmp_path,monkeypatch):
    import httpx
    from tests.test_websites import execute_web
    def response(request):
        if request.url.path=='/robots.txt':return httpx.Response(200,text='User-agent: *\nAllow: /')
        if request.url.path=='/':return httpx.Response(200,text='<html><title>Example</title><footer>Example</footer></html>')
        if request.url.path=='/about':return httpx.Response(200,text='<main>Established Example AS in Norway.</main>')
        return httpx.Response(404)
    _,row,_,_=execute_web(tmp_path,monkeypatch,response=response,website='https://example.com/')
    proof=next(c for c in row['claims'] if c['field']=='official_website')
    assert row['run']['sections']['website']=='available'
    assert any(e['id'] in proof['evidence_ids'] and e['source_url'].endswith('/about') for e in row['evidence'])


def test_final_guard_removes_legacy_carried_group_website_and_derived_content(tmp_path):
    blobs=BlobStore(tmp_path)
    row=placeholder(ORG,'test','2026-11-06T00:00:00Z',('identity','website'))
    body=b'<html><title>Permobil</title><footer>Copyright Permobil</footer></html>'
    source=Source('https://example.com/',body,blobs.put(body),'2026-11-06T00:00:00Z')
    identity=Section();add(identity,source,ORG,'identity','identity.legal_name','Permobil AS','/name');update(row,'identity',identity)
    website=Section();add(website,source,ORG,'website','official_website',{'final_url':'https://example.com','proof_type':'registry_declared_name_tier_a','identity_level':'VERIFIED'},'/website',source_class='company_owned')
    add(website,source,ORG,'website','website_description.synthetic','Permobil','/description',source_class='company_owned')
    website.claims[0].carried_forward=True
    update(row,'website',website)
    enforce([row],blobs,SimpleNamespace(domain_owners={}))
    assert row.run.sections['website']=='ambiguous'
    assert not any(c.family=='website' for c in row.claims)
    assert row.run.refresh['website']['entity_scope']['website_reason']=='group website'
