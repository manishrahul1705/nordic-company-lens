from signalpost.web.html import Page
import pytest

from signalpost.web.social import attributed, drop_shared, matches_profile, profile_url
from signalpost.runner import placeholder
from signalpost.sources.extract import Section, Source, add
from signalpost.models.evidence import utc_now


CONTEXT={'name':'ROLIDBAKKEN FUS BARNEHAGE AS','subunits':[{'name':'ROLIDBAKKEN FUS BARNEHAGE AS'}]}
PROOF={'final_url':'https://fus.no','proof_page_url':'https://fus.no/rolidbakken'}


@pytest.mark.parametrize('host,path', [
    ('no.linkedin.com', 'company/example'), ('facebook.com', 'example'),
    ('instagram.com', 'example'), ('youtube.com', '@example'),
    ('tiktok.com', '@example'), ('x.com', 'example'), ('twitter.com', 'example'),
    ('threads.net', '@example'), ('threads.com', '@example'), ('vimeo.com', 'example'),
    ('snapchat.com', 'add/example'), ('snapchat.com', 'p/example'),
])
def test_company_profile_paths_require_a_matching_company(host, path):
    url = f'https://{host}/{path}'
    page = Page(f'<footer><a href="{url}">Follow us</a></footer>'.encode(), 'https://different.no/')
    proof = {'final_url': page.url, 'identity_level': 'VERIFIED'}
    assert url in attributed(page, proof, {'name': 'Example AS'})
    assert not attributed(page, proof, {'name': 'Different Company AS'})


@pytest.mark.parametrize('url', [
    'https://lnkd.in/example', 'https://www.linkedin.com/sharing/share-offsite/',
    'https://www.linkedin.com/company/example?url=https://different.no',
    'https://l.facebook.com/example', 'https://twitter.com/intent/follow',
    'https://www.threads.com/', 'https://www.threads.net/@example/post/123',
    'https://vimeo.com/123456', 'https://vimeo.com/channels/example',
    'https://snapchat.com/share/example', 'https://snapchat.com/',
])
def test_social_profile_parser_rejects_non_profiles(url):
    assert profile_url(url) is None


def test_diseth_profile_cannot_be_attributed_to_rolidbakken():
    page=Page(b'<main><a href="https://facebook.com/Diseth-FUS-barnehage-As-1287226694698749">Facebook</a></main>',PROOF['proof_page_url'])
    assert not attributed(page,PROOF,CONTEXT)


def test_own_matching_handle_inside_path_accepted():
    page=Page(b'<main><a href="https://facebook.com/Rolidbakken-FUS-Barnehage-AS">Facebook</a></main>',PROOF['proof_page_url'])
    assert len(attributed(page,PROOF,CONTEXT))==1


def test_shared_footer_even_matching_handle_rejected():
    page=Page(b'<footer><a href="https://facebook.com/Rolidbakken-FUS-Barnehage-AS">Facebook</a></footer>',PROOF['proof_page_url'])
    assert not attributed(page,PROOF,CONTEXT)


def test_agency_and_partial_generic_token_rejected():
    # A short or generic one-token handle is not company-specific.
    assert not matches_profile('https://facebook.com/FUS', [CONTEXT['name']])
    assert not matches_profile('https://facebook.com/transport', ['Falsen Transport AS'])
    assert not matches_profile('https://instagram.com/designagency', ['Example AS'])
    assert matches_profile('https://linkedin.com/company/aas-betong-as',['Aas Betong AS'])
    assert not matches_profile('https://linkedin.com/company/notexample',['Example AS'])


def test_social_handle_token_containment_and_qualifiers():
    assert matches_profile('https://linkedin.com/company/cchange-transformation', ['CChange AS'])
    assert matches_profile('https://linkedin.com/company/vokser-group', ['Vokser AS'])
    assert matches_profile('https://x.com/rent-hall-global', ['Renthall AS'])
    assert not matches_profile('https://twitter.com/bjornkaupang', ['Objectfront AS'])
    assert not matches_profile('https://x.com/istiaqdesign', ['Stillasfordeg AS'])
    assert matches_profile('https://facebook.com/lefdal.no', ['Lefdal Installasjon AS'])
    assert not matches_profile('https://linkedin.com/company/sagarr', ['Saga Regnskap og Rådgivning AS'])
    assert not matches_profile('https://facebook.com/soa.no', ['Sigmund Olsen Agentur AS'])


def test_norwegian_letters_and_run_together_handles_match():
    assert matches_profile('https://www.facebook.com/lorenskogbandasje', ['LØRENSKOG BANDASJE AS'])
    assert matches_profile('https://instagram.com/storendyreklinikk', ['STØREN DYREKLINIKK AS'])
    assert matches_profile('https://www.facebook.com/buoybakeri', ['BUØY BAKERI & KONDITORI AS'])
    assert matches_profile('https://www.facebook.com/ControlSolutionsAS', ['CONTROL SOLUTIONS AS'])
    assert matches_profile('https://www.youtube.com/@geonordas', ['GEONORD AS'])
    assert matches_profile('https://www.facebook.com/HillerenProsjekteringAS', ['HILLEREN PROSJEKTERING AS'])


def test_verified_site_brand_does_not_replace_registered_name_match():
    page=Page(b'<main><a href="https://facebook.com/soa.no">Facebook</a></main>','https://soa.no/')
    context={'name':'Sigmund Olsen Agentur AS','registered_brands':['soa']}
    proof={'identity_level':'VERIFIED','final_url':page.url,'proof_page_url':page.url,'other_orgnrs':[]}
    assert not attributed(page,proof,context)


def test_profile_shared_by_different_companies_is_removed():
    rows=[]
    for org in ('923609016','993578843'):
        row=placeholder(org,'test',utc_now());section=Section()
        add(section,Source('https://example.no',b'body','a'*64,utc_now()),org,'website','social_profile.example',{'url':'https://facebook.com/example'},'/')
        row.claims=section.claims;rows.append(row)
    drop_shared(rows)
    assert all(not r.claims for r in rows)


def test_profile_observed_on_another_company_but_not_published_is_dropped():
    first=placeholder('923609016','test',utc_now());second=placeholder('993578843','test',utc_now())
    section=Section()
    add(section,Source('https://example.no',b'body','a'*64,utc_now()),'923609016','website','social_profile.example',{'url':'https://facebook.com/example'},'/')
    first.claims=section.claims
    second.run.refresh['website']={'observed_social_profiles':['https://www.facebook.com/example']}
    drop_shared([first,second])
    assert not first.claims


def test_language_prefix_does_not_allow_shared_template_footer():
    page=Page(b'<footer><a href="https://facebook.com/Rolidbakken-FUS-Barnehage-AS">Facebook</a></footer>','https://fus.no/en/rolidbakken')
    assert not attributed(page,{**PROOF,'proof_page_url':page.url},CONTEXT)
