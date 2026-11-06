import pytest

from signalpost.web.html import Page
from signalpost.web.proof import score
from signalpost.web.collector import proof_page_targets
from tests.test_websites import OUR,OTHER


def proof(text,url='https://example.no/kontakt-oss',name='Example AS'):
    return score(Page(text.encode(),url),OUR,{'name':name},'registry_website',[])


def test_cms_own_head_office_section_inside_article_proves_exact_entity():
    body='<article class="page type-page"><h3>Hovedkontor</h3><p>Example AS<br>Gate 1</p><p>Org.nr: '+OUR+'</p></article>'
    result=proof(body)
    assert result.level=='VERIFIED' and result.proof_type=='contact_section_orgnr'
    assert proof(body,url='https://example.no/news/company').level!='VERIFIED'
    assert proof(body,name='Another AS').level!='VERIFIED'


@pytest.mark.parametrize('body', [
    '<article class="post"><h3>Hovedkontor</h3>Example AS Org.nr: '+OUR+'</article>',
    '<article class="type-page"><h3>Hovedkontor kunde</h3>Example AS Org.nr: '+OUR+'</article>',
    '<article class="type-page"><h3>Hovedkontor</h3>Example AS</article>',
    '<article class="type-page"><h3>Hovedkontor</h3>Example AS Org.nr: '+OUR+'</article><footer>Org nr '+OTHER+'</footer>',
])
def test_news_customer_mentions_missing_number_and_foreign_owner_do_not_verify(body):
    assert proof(body).level!='VERIFIED'


@pytest.mark.parametrize('street,shown', [('Storgaten 12','Storgt. 12'),('Elveveien 32','Elvevn. 32'),
                                       ('Dronning Eufemias gate 23','Dronning Eufemias gt. 23')])
def test_exact_name_street_abbreviations_keep_house_number(street,shown):
    ctx={'name':'Example AS','street':[street]}
    page=Page(('<h1>Example AS</h1><footer>'+shown+'</footer>').encode(),'https://example.no/')
    assert score(page,OUR,ctx,'registry_website',[]).level=='VERIFIED'
    assert score(page,OUR,{'name':'Different AS','street':[street]},'registry_website',[]).level!='VERIFIED'
    ctx['street']=[street+'B']
    assert score(page,OUR,ctx,'legal_name_slug',[]).level!='VERIFIED'
    assert score(page,OUR,ctx,'registry_website',[]).proof_type=='registry_declared_name_tier_a'


def test_only_three_extra_proof_targets_are_added():
    page=Page(b'<h1>Example AS</h1>','https://example.no/')
    assert len(proof_page_targets(page,page.url,limit=6))==6
    assert 'https://example.no/impressum' in proof_page_targets(page,page.url,limit=6)


def test_navigation_partners_do_not_hide_own_bounded_contact_section():
    body='<nav>Partnere Kundehistorier</nav><article class="type-page"><h3>Hovedkontor</h3>Example AS<p>Org.nr: '+OUR+'</p><h3>Teknisk bistand</h3>Other Business Partner AS</article>'
    assert proof(body).proof_type=='contact_section_orgnr'


@pytest.mark.parametrize('kind',['"NewsArticle"','["BlogPosting","Article"]'])
def test_news_schema_does_not_become_contact_proof(kind):
    body='<script type="application/ld+json">{"@type":'+kind+'}</script><article class="type-page"><h3>Hovedkontor</h3>Example AS Org.nr: '+OUR+'</article>'
    assert proof(body).level!='VERIFIED'
