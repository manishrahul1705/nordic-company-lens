from signalpost.web.html import Page
from signalpost.web.social import attributed, drop_shared, matches_profile
from signalpost.runner import placeholder
from signalpost.sources.extract import Section, Source, add
from signalpost.models.evidence import utc_now


CONTEXT={'name':'ROLIDBAKKEN FUS BARNEHAGE AS','subunits':[{'name':'ROLIDBAKKEN FUS BARNEHAGE AS'}]}
PROOF={'final_url':'https://fus.no','proof_page_url':'https://fus.no/rolidbakken'}


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
    assert not matches_profile('https://facebook.com/FUS', [CONTEXT['name']])
    assert not matches_profile('https://instagram.com/designagency', ['Example AS'])
    assert matches_profile('https://linkedin.com/company/aas-betong-as',['Aas Betong AS'])
    assert not matches_profile('https://linkedin.com/company/notexample',['Example AS'])


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
