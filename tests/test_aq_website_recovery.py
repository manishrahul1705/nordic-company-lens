import pytest
from signalpost.web.html import Page
from signalpost.web.proof import score
from signalpost.web.round2 import real_page
from signalpost.web import social_universe
from tests.test_websites import OUR, OTHER


def owner_page(number=OUR, title='Haugesund Elektriske AS', copyright=''):
    return Page(('<html><head><title>'+title+'</title></head><body><footer><p>'+title+'</p><p>Org nr: '+number+'</p>'+copyright+'</footer></body></html>').encode(), 'https://haugel.no/')


def universe(monkeypatch, matches=()):
    monkeypatch.setattr(social_universe, 'index', lambda: {'keys': {'haugesundelektriske': list(matches)}})


def test_exact_publisher_id_resolves_omitted_trading_descriptor(monkeypatch):
    universe(monkeypatch)
    page = owner_page(); context = {'name': 'HAUGESUND ELEKTRISKE FORRETNING AS', 'allowed_orgnrs': {OUR}}
    proof = score(page, OUR, context, 'registry_website', [])
    assert proof.level == 'VERIFIED' and proof.proof_type == 'orgnr_on_page'
    assert real_page(page, context) is None
    assert context['name'] == 'HAUGESUND ELEKTRISKE FORRETNING AS'


@pytest.mark.parametrize('number', ['', OTHER, OUR+' '+OTHER])
def test_descriptor_repair_never_uses_name_only_or_foreign_publisher(monkeypatch, number):
    universe(monkeypatch)
    assert score(owner_page(number), OUR, {'name': 'HAUGESUND ELEKTRISKE FORRETNING AS'}, 'registry_website', []).level != 'VERIFIED'


def test_other_registered_company_and_missing_universe_still_veto(monkeypatch):
    universe(monkeypatch, [OTHER])
    assert score(owner_page(), OUR, {'name': 'HAUGESUND ELEKTRISKE FORRETNING AS'}, 'registry_website', []).reason == 'different_legal_entity'
    monkeypatch.setattr(social_universe, 'index', lambda: None)
    assert score(owner_page(), OUR, {'name': 'HAUGESUND ELEKTRISKE FORRETNING AS'}, 'registry_website', []).reason == 'different_legal_entity'


@pytest.mark.parametrize('title', ['Haugesund Elektriske AB', 'Different Company AS'])
def test_descriptor_repair_does_not_relax_distinct_names_or_legal_forms(monkeypatch, title):
    universe(monkeypatch)
    assert score(owner_page(title=title), OUR, {'name': 'HAUGESUND ELEKTRISKE FORRETNING AS'}, 'registry_website', []).reason == 'different_legal_entity'


def test_explicit_other_copyright_owner_is_still_rejected(monkeypatch):
    universe(monkeypatch)
    p = owner_page(copyright='<p>Copyright Different Company AS</p>')
    assert score(p, OUR, {'name': 'HAUGESUND ELEKTRISKE FORRETNING AS'}, 'registry_website', []).reason == 'different_legal_entity'


def test_exact_publisher_descriptor_repair_survives_service_page_title(monkeypatch):
    universe(monkeypatch)
    p=Page(('<html><head><title>Montere stikkontakt | Haugesund Elektriske AS</title></head><body>'
        '<footer><p>Haugesund Elektriske AS</p><p>Org nr '+OUR+'</p></footer></body></html>').encode(),'https://haugel.no/tjenester/stikkontakt')
    context={'name':'HAUGESUND ELEKTRISKE FORRETNING AS','allowed_orgnrs':{OUR}}
    assert score(p,OUR,context,'registry_website',[]).level=='VERIFIED'
    assert real_page(p,context) is None
