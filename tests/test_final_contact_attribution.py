"""Shared staff/adviser contacts must not identify another legal entity's site."""
import pytest
from signalpost.web.html import Page
from signalpost.web.proof import score
from signalpost.web.social import profile_url
from signalpost.web import shared_identifiers

@pytest.mark.parametrize('name,registered,body',[
 ('Clinic Services AS',{'mobile':'90951108'},'<title>Outdoor Adventures</title><footer>Outdoor Adventures AS Tel 90951108</footer>'),
 ('Harbour Property AS',{'email':'tom@lawfirm.no'},'<title>Contact - Lawfirm</title><p>Tom: tom@lawfirm.no</p>'),
])
def test_other_business_contact_does_not_prove_ownership(monkeypatch,name,registered,body):
 monkeypatch.setattr(shared_identifiers,'bundled',lambda _: {'phones':{'90951108':1},'email_domains':{'lawfirm.no':1}})
 p=Page(body.encode(),'https://otherbusiness.no/')
 assert score(p,'923609016',{'name':name,**registered},'registry_email',[]).level!='VERIFIED'


def test_contact_with_own_exact_legal_identity_still_proves(monkeypatch):
 monkeypatch.setattr(shared_identifiers,'bundled',lambda _: {'phones':{'12345678':1}})
 p=Page(b'<title>Example Services AS</title><footer>Phone 12 34 56 78</footer>','https://example.no/')
 assert score(p,'923609016',{'name':'Example Services AS','phone':'12345678'},'legal_name_slug',[]).level=='VERIFIED'

@pytest.mark.parametrize('url',['https://facebook.com/Company Name','https://facebook.com/Company%20Name','https://instagram.com/Company%09Name'])
def test_profile_handle_whitespace_rejected(url):assert profile_url(url) is None
