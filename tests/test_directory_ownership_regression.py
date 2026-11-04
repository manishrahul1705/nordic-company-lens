"""Copied registry details on S5's two false positives never prove ownership."""
import pytest

from signalpost.budget import SourceFailure
from signalpost.web.candidates import generate
from signalpost.web.html import Page
from signalpost.web.policy import validate_url
from signalpost.web.proof import score
from scripts.accuracy_audit import audit_website_claim


@pytest.mark.parametrize('url,org,name,body', [
    ('https://utdanning.no/bedrift/926698435/', '926698435',
     'UPPSTAD VVS AVDELING HOVDEN AS',
     '<title>UPPSTAD VVS AVDELING HOVDEN AS - Utdanning.no</title>'
     '<h1>UPPSTAD VVS AVDELING HOVDEN AS</h1>'
     '<span>Organisasjonsnummer 926698435</span>'),
    ('https://vat-validation.com/8LkB_Sameiet+Kirkegaten+36B', '911683237',
     'SAMEIET KIRKEGATEN 36B',
     '<title>Sameiet Kirkegaten 36B - VAT-Validation.com - VAT Lookup</title>'
     '<h1>SAMEIET KIRKEGATEN 36B</h1><p>Kirkegaten 36B</p>'),
])
def test_directory_registry_details_do_not_prove_site_ownership(url,org,name,body):
    context={'name':name,'street':['Kirkegaten 36B'],'website':url}
    proof=score(Page(body.encode(),url),org,context,'search_brave',[])
    assert proof.level=='REJECT'
    assert proof.reason=='directory_or_marketplace'
    assert all(candidate.domain not in {'utdanning.no','vat-validation.com'}
               for candidate in generate(context))
    with pytest.raises(SourceFailure):
        validate_url(url,{'utdanning.no','vat-validation.com'})
    claim={'field':'official_website','value':{'final_url':url,'identity_level':'VERIFIED'}}
    assert audit_website_claim(org,claim,{},body,context=context)[0]=='INCORRECT'


@pytest.mark.parametrize('url', ['https://www.utdanning.no/bedrift/926698435/',
                               'https://www.vat-validation.com/company'])
def test_directory_subdomains_cannot_bypass_ownership_guard(url):
    proof=score(Page(b'<footer>Org.nr 926698435</footer>',url),
                '926698435',{'name':'UPPSTAD VVS AVDELING HOVDEN AS'},'registry_website',[])
    assert proof.level=='REJECT'
    assert proof.reason=='directory_or_marketplace'


@pytest.mark.parametrize('host', ['nordlei.no', 'www.nordlei.no', 'unlisted-lei-provider.no'])
def test_lei_directory_record_is_not_an_owned_site_even_on_unlisted_domain(host):
    url=f'https://{host}/lei/254900XUQRFIPTZYQ539/giljeholmen-as'
    body='<title>LEI registration and lookup</title><h1>GILJEHOLMEN AS</h1><p>Selskapsregisternummer 918 270 205</p>'
    context={'name':'GILJEHOLMEN AS','website':url}
    proof=score(Page(body.encode(),url),'918270205',context,'registry_website',[])
    assert proof.level=='REJECT' and proof.reason=='directory_or_marketplace'
    assert all(candidate.url!=url for candidate in generate(context))
    with pytest.raises(SourceFailure):
        validate_url(url,{host.removeprefix('www.')})
    claim={'field':'official_website','value':{'final_url':f'https://{host}',
          'proof_page_url':url,'identity_level':'VERIFIED'}}
    assert audit_website_claim('918270205',claim,{},body,context=context)[0]=='INCORRECT'


def test_company_homepage_can_disclose_its_own_lei():
    body=b'<h1>GILJEHOLMEN AS</h1><footer>Org.nr 918270205; LEI 254900XUQRFIPTZYQ539</footer>'
    assert score(Page(body,'https://giljeholmen.no/'),'918270205',
                 {'name':'GILJEHOLMEN AS'},'registry_website',[]).level=='VERIFIED'
