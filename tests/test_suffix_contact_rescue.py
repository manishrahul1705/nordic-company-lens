import pytest

from signalpost.web.html import Page
from signalpost.web.proof import rescue_suffix_host
from tests.test_websites import OUR, OTHER, execute_web, html


def pages(*bodies):
    return [Page(body.encode(),'https://example.no/'+str(i)) for i,body in enumerate(bodies)]


@pytest.mark.parametrize('contact,context,signal',[
    ('Call +47 12 34 56 78',{'phone':'0047 12345678'},'phone'),
    ('office@example.no',{'email':'office@example.no'},'email'),
    ('sales@example.no',{'email':'office@example.no'},'email_domain'),
])
def test_suffix_rescue_uses_contact_on_another_page_of_same_host(contact,context,signal):
    pp=pages('<title>Example</title>', '<footer>'+contact+'</footer>')
    result=rescue_suffix_host(pp,OUR,{'name':'Example AS',**context},'legal_name_slug',[])
    assert result and result[0].proof_type=='legal_name_without_suffix_and_registry_contact'
    assert signal in result[0].signals
    assert result[1]==0 and result[2]==1


@pytest.mark.parametrize('body',[
    '<h1>Example</h1><p>Example road 1, 0123 Oslo</p>',
    '<h1>Example</h1><p>not-office@example.no.evil.com</p>',
    '<h1>Example</h1><p>office@example.no.evil.com</p>',
    '<h1>Example</h1><p>123456789</p>',
])
def test_name_or_address_and_partial_contacts_do_not_rescue(body):
    assert rescue_suffix_host(pages(body),OUR,{'name':'Example AS','phone':'12345678','email':'office@example.no'},'legal_name_slug',[]) is None


def test_rescue_does_not_combine_subdomains_or_foreign_owner():
    ctx={'name':'Example AS','phone':'12345678'}
    pp=pages('<h1>Example</h1>')+[Page(b'<footer>12345678</footer>','https://other.example.no/contact')]
    assert rescue_suffix_host(pp,OUR,ctx,'legal_name_slug',[]) is None
    assert rescue_suffix_host(pages('<h1>Example</h1>','<footer>12345678 Org.nr '+OTHER+'</footer>'),OUR,ctx,'legal_name_slug',[]) is None


def test_registry_contact_in_visible_cms_article_is_eligible():
    pp=pages('<title>Example</title>','<article><h1>Contact us</h1><p>12 34 56 78</p></article>')
    result=rescue_suffix_host(pp,OUR,{'name':'Example AS','phone':'12345678'},'registry_website',[])
    assert result and result[2]==1


def test_registered_contact_can_prove_a_non_name_domain_but_not_a_parked_site():
    pp=[Page(b'<h1>Example</h1><footer>12345678</footer>','https://unrelated.no/')]
    assert rescue_suffix_host(pp,OUR,{'name':'Example AS','phone':'12345678'},'registry_website',[]) is not None
    assert rescue_suffix_host(pages('<h1>Example</h1>','<footer>12345678 this domain is for sale</footer>'),OUR,{'name':'Example AS','phone':'12345678'},'legal_name_slug',[]) is None


def test_rescue_publishes_name_and_contact_page_evidence(tmp_path,monkeypatch):
    def response(request):
        if request.url.path=='/robots.txt':return __import__('httpx').Response(200,text='User-agent: *\nAllow: /')
        if request.url.host!='example.no':return __import__('httpx').Response(404,text='missing')
        body=html('',title='Example',extra='<a href="/kontakt">Contact</a>').replace('<header>Example AS</header>','<header>Example</header>')
        if request.url.path=='/kontakt':body='<title>Contact</title><footer>12 34 56 78</footer>'
        elif request.url.path!='/':return __import__('httpx').Response(404,text='missing')
        return __import__('httpx').Response(200,text=body)
    _,row,_,_=execute_web(tmp_path,monkeypatch,response=response,
        website_suffix_contact_proof=False,website_suffix_contact_rescue=True)
    claim=next(c for c in row['claims'] if c['field']=='official_website')
    assert claim['value']['proof_type']=='legal_name_without_suffix_and_registry_contact'
    ev=[e for e in row['evidence'] if e['id'] in claim['evidence_ids'] and e['source_class']=='company_owned']
    assert {e['source_url'] for e in ev}=={'https://example.no/','https://example.no/kontakt'}
