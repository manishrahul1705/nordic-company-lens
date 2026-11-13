import pytest
from signalpost.web.candidates import generate, registry_website_url


@pytest.mark.parametrize('raw,expected',[
    ('/www.balticyachts.no','https://www.balticyachts.no/'),
    ('www/oppdal.com','https://www.oppdal.com/'),
    ('www:stiklestad-golfklubb.no','https://www.stiklestad-golfklubb.no/'),
    ('www/no.tm.org','https://www.no.tm.org/'),
    ('  WWW/OPPDAL.COM  ','https://www.oppdal.com/'),
    ('www.example.no','https://www.example.no/'),
    ('https://www.example.no/contact','https://www.example.no/contact'),
])
def test_registry_www_separator_is_candidate_syntax_only(raw,expected):
    assert registry_website_url(raw)==expected
    context={'website':raw,'name':None}
    candidates=generate(context)
    assert len(candidates)==1 and candidates[0].url==expected
    assert candidates[0].origin=='registry_website'
    assert context['website']==raw


@pytest.mark.parametrize('raw',[
    'mailto:post@example.no','post@example.no','www/facebook.com/company',
    '/www.proff.no','www/telenor.no','www/no-such-tld.cno','93823663',
    'www.example.no trailing text',
])
def test_registry_normalization_preserves_nonwebsite_and_existing_domain_vetoes(raw):
    assert generate({'website':raw,'name':None})==[]


def test_repaired_www_subunit_retains_exact_registry_scope():
    candidates=generate({'subunits':[{'orgnr':'931166492','website':'www/oppdal.com'}]})
    assert len(candidates)==1 and candidates[0].origin=='subunit_registry_website'
    assert candidates[0].subunit_orgnr=='931166492'
