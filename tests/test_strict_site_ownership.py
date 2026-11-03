import httpx
import pytest

from signalpost.web.html import Page
from signalpost.web.proof import score
from tests.test_websites import OUR, OTHER, execute_web, html


def proof(body, context=None, url='https://example.no/'):
    return score(Page(body.encode(), url), OUR, context or {'name':'Example AS'}, 'legal_name_slug', [])


def test_short_footer_exact_orgnr_is_sufficient():
    assert proof('<footer>Org.nr 923 609 016 MVA</footer>').level=='VERIFIED'


@pytest.mark.parametrize('contact,context', [
    ('<a href="tel:12345678">Call</a>', {'phone':'12345678'}),
    ('Telephone 12 34 56 78', {'phone':'12345678'}),
    ('office@example.no', {'email':'office@example.no'}),
    ('Example gate 1', {'street':['Example gate 1']}),
    ('0001 Oslo', {'postcode':'0001','city':'OSLO'}),
])
def test_exact_legal_name_and_registry_contact_verified(contact, context):
    body='<h1>Example AS</h1><footer>'+contact+'</footer>'
    assert proof(body, {'name':'Example AS',**context}).level=='VERIFIED'
    from scripts.accuracy_audit import audit_website_claim
    claim={'field':'official_website','value':{'final_url':'https://example.no/', 'identity_level':'VERIFIED',
        'proof_type':'legal_name_and_registry_contact'}}
    assert audit_website_claim(OUR,claim,{},body,context={'name':'Example AS',**context})[0]=='CORRECT'
    assert audit_website_claim(OUR,claim,{},body,context={'name':'Example AS'})[0]=='INCORRECT'


def test_name_only_is_ambiguous():
    assert proof('<h1>Example AS</h1>').level=='MEDIUM'
    assert proof('<h1>Example</h1><a href="tel:12345678">Call</a>', {'name':'Example AS','phone':'12345678'}).level!='VERIFIED'


def test_foreign_owner_rejects_even_with_target_mention():
    assert proof('<main>Org nr '+OUR+'</main><footer>Org nr '+OTHER+'</footer>').level=='REJECT'


def test_parent_group_without_exact_orgnr_rejected():
    assert proof('<head><title>Parent Group</title></head><h1>Example AS</h1><a href="tel:12345678">Call</a>', {'name':'Example AS','phone':'12345678'}).level=='REJECT'


def test_foreign_contact_page_refutes_verified_homepage(tmp_path, monkeypatch):
    def response(request):
        if request.url.path=='/robots.txt':
            return httpx.Response(200,text='User-agent: *\nAllow: /')
        if request.url.host not in {'example.no', 'www.example.no'}:
            return httpx.Response(404)
        if request.url.path=='/kontakt':
            return httpx.Response(200,text=html('Org.nr '+OTHER))
        if request.url.path=='/':
            return httpx.Response(200,text=html('Org.nr '+OUR))
        return httpx.Response(404)
    _,row,_,_=execute_web(tmp_path,monkeypatch,response=response)
    assert not any(c['field']=='official_website' and c['availability']=='available' for c in row['claims'])
