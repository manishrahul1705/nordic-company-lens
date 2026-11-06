import pytest

from signalpost.web.candidates import generate, legal_name, legal_name_slugs


def test_candidate_source_priority_and_subunit_names():
    nominations = generate({'website':'registry.no', 'email':'a@email.no',
        'nav_homepages':[{'url':'nav.no'}], 'name':'Distinctive AS',
        'subunits':[{'orgnr':'993578843','name':'Branchbrand AS','website':'branch.no','email':'a@branchmail.no'}]})
    assert [c.origin for c in nominations[:5]] == ['registry_website','registry_email','nav_employer_homepage','subunit_registry_website','subunit_registry_email']
    assert next(c for c in nominations if c.domain=='branchbrand.no').subunit_orgnr=='993578843'
    assert any(c.domain=='distinctive.no' for c in nominations)
    assert len([c for c in nominations if c.origin.endswith('name_slug')]) <= 4


def test_legal_forms_spelling_and_suffixes():
    slugs=legal_name_slugs(legal_name('Bjørk Åsen Ægir ASA'))
    assert {'bjorkasenaegir.no','bjorkasenaegir-as.no','bjorkasenaegiras.no','bjorkasenaegir.as','bjorkasenaegir.com','bjoerkaasenaegir.no'} <= set(slugs)


@pytest.mark.parametrize('provider', ['gmail.com','hotmail.com','outlook.com','live.com','icloud.com','yahoo.com','online.no','getmail.no','broadpark.no'])
def test_consumer_email_does_not_nominate_website(provider):
    assert not generate({'email':'someone@'+provider,'name':'Holding AS'})


@pytest.mark.parametrize('name', ['ABC AS', 'Eiendom Holding Invest AS', 'Consult Service DA'])
def test_short_or_generic_names_not_guessed(name):
    assert not generate({'name':name})
