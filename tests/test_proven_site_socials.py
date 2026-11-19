import pytest
from signalpost.web.html import Page
from signalpost.web.social import attributed,profile_url,profile_key,drop_shared
from signalpost.web.social_links import veto
from signalpost.runner import placeholder
from signalpost.sources.extract import Section,Source,add
from signalpost.sources.blobstore import BlobStore
from signalpost.models.evidence import utc_now

PROOF={'identity_level':'VERIFIED','final_url':'https://example.no/','content_allowed':True}


@pytest.mark.parametrize('url,canonical',[
 ('https://facebook.com/p/Fjelde-Teknikk-As-100091965602197/','https://facebook.com/p/Fjelde-Teknikk-As-100091965602197'),
 ('https://facebook.com/profile.php?id=61584748555742&locale=nb_NO','https://facebook.com/profile.php?id=61584748555742'),
 ('https://linkedin.com/showcase/example/','https://linkedin.com/showcase/example'),
 ('https://linkedin.com/school/example/','https://linkedin.com/school/example'),
 ('https://youtube.com/channel/UC123456789/','https://youtube.com/channel/UC123456789'),
 ('https://instagram.com/example/?igsh=xyz','https://instagram.com/example'),
 ('https://tiktok.com/@example/?lang=en','https://tiktok.com/@example'),
 ('https://mobile.twitter.com/example/','https://twitter.com/example'),
 ('https://www.x.com/example?s=20','https://x.com/example'),
])
def test_added_profile_forms_need_no_handle_match_on_proven_page(url,canonical):
    page=Page(f'<main><a href="{url}">Follow us</a></main>'.encode(),PROOF['final_url'])
    assert profile_url(url)==canonical
    assert canonical in attributed(page,PROOF,{'name':'Fjelde Teknikk AS','organisation_number':'931069373'})
    assert not attributed(page,{**PROOF,'identity_level':'LOW'},{'name':'Other Legal Company AS'})


@pytest.mark.parametrize('url',[
 'https://linkedin.com/in/person','https://linkedin.com/profile/view?id=123',
 'https://facebook.com/tr?id=123456789&ev=PageView','https://facebook.com/profile.php',
 'https://facebook.com/profile.php?id=not-a-number','https://facebook.com/p/name',
 'https://facebook.com/sharer/sharer.php?u=https://example.no','https://x.com/intent/tweet',
 'https://instagram.com/','https://tiktok.com/','https://youtube.com/watch?v=abc',
 'https://facebook.com/example?url=https://evil.test',
])
def test_person_share_tracking_and_invalid_identity_forms_rejected(url):
    assert profile_url(url) is None


def test_facebook_numeric_identity_is_preserved_for_shared_profile_veto():
    assert profile_key('https://facebook.com/profile.php?id=123456789')==profile_key('https://facebook.com/p/Example-123456789/')
    assert profile_key('https://facebook.com/profile.php?id=123456789')!=profile_key('https://facebook.com/profile.php?id=987654321')


@pytest.mark.parametrize('markup',[
 '<meta property="og:see_also" content="https://facebook.com/brand"><meta property="og:see_also" content="https://instagram.com/brand">',
 '<iframe src="https://www.facebook.com/plugins/page.php?href=https%3A%2F%2Ffacebook.com%2Fbrand"></iframe><div class="fb-page" data-href="https://instagram.com/brand"></div>',
 '<iframe src="https://www.facebook.com/v12.0/plugins/page.php?href=https%3A%2F%2Ffacebook.com%2Fbrand&amp;locale=en_US"></iframe><a href="https://instagram.com/brand">Instagram</a>',
])
def test_metadata_and_page_widgets_provide_verbatim_evidence(markup):
    page=Page(markup.encode(),PROOF['final_url'])
    found=attributed(page,PROOF,{'name':'Example AS'})
    assert set(found)=={'https://facebook.com/brand','https://instagram.com/brand'}
    assert all(span in page.raw and len(span)<=300 for span in found.values())


@pytest.mark.parametrize('name,url,people,accepted',[
 ('Objectfront AS','https://twitter.com/bjornkaupang',['Bjørn Kaupang'],False),
 ('Stillasfordeg AS','https://x.com/istiaqdesign',[],False),
 ('Fusa Mekaniske Industri AS','https://facebook.com/fusamek',[],True),
 ('Indre Salten Opplæringskontor AS','https://facebook.com/IndreSaltenOK',[],True),
 ('Scene Midt AS','https://instagram.com/martehallem',['Marte Heie Hallem'],False),
 ('TB Maskin AS','https://youtube.com/user/thomasbech8',['Thomas Bech'],False),
])
def test_four_required_real_cases(name,url,people,accepted):
    page=Page(f'<footer><a href="{url}">Follow us</a></footer>'.encode(),PROOF['final_url'])
    assert bool(attributed(page,PROOF,{'name':name,'role_person_names':people}))==accepted


def test_handle_matching_other_cohort_company_is_rejected():
    assert veto('https://instagram.com/othercompany',{'name':'Example AS','other_company_names':['Other Company AS']})=='other_cohort_company'


@pytest.mark.parametrize('proof',[
 {**PROOF,'content_allowed':False},{**PROOF,'relationship_note':'group_site'},
 {**PROOF,'other_orgnrs':['993578843']},
])
def test_existing_content_and_group_vetoes_remain(proof):
    page=Page(b'<footer><a href="https://facebook.com/brand">Facebook</a></footer>',PROOF['final_url'])
    assert not attributed(page,proof,{'name':'Brand AS'})


def test_contact_page_article_and_global_share_setting_are_not_share_widgets():
    page=Page(b'<body class="tweak-share-buttons-style-icon-only"><article class="page type-page"><p><a href="https://linkedin.com/company/brand">LinkedIn</a></p></article></body>','https://example.no/contact/')
    assert attributed(page,PROOF,{'name':'Example AS'})


def test_editorial_article_on_contact_page_is_still_excluded():
    page=Page(b'<article><a href="https://facebook.com/customer">Customer story</a></article>','https://example.no/contact/')
    assert not attributed(page,PROOF,{'name':'Example AS'})


@pytest.mark.parametrize('markup',[
 '<div class="share-buttons"><a href="https://facebook.com/brand">Share</a></div>',
 '<article><a href="https://facebook.com/brand">Customer story</a></article>',
 '<div class="agency-credit"><a href="https://facebook.com/brand">Designer</a></div>',
 '<div hidden><a href="https://facebook.com/brand">Hidden</a></div>',
])
def test_editorial_share_credit_hidden_contexts_stay_excluded(markup):
    page=Page(markup.encode(),PROOF['final_url'])
    assert not attributed(page,PROOF,{'name':'Example AS'})
