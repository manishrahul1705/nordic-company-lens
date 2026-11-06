import pytest
from signalpost.web.html import Page
from signalpost.web.collector import candidate_proof
from signalpost.web.candidates import Candidate
from signalpost.web.names import same_name,proof_context
from tests.test_recall_step10 import ORG,OTHER,CONTEXT


def page(body,title='Example AS'):
    return Page(f'<html><title>{title}</title><body>{body}</body></html>'.encode(),'https://example.no/')


@pytest.mark.parametrize('name,site,title',[
    ('KN ELEKTRO AS','<footer>All rettigheter reservert - KN Elektro AS</footer>','KN Elektro'),
    ('LOFOTPOSTEN AS','<footer>Utgitt av Lofotposten AS</footer>','Lofotposten'),
    ('CONTROL SOLUTIONS AS',f'<footer>Org.nr {ORG}</footer>','CONTROL SOLUTION AS'),
    ('GS ELEKTRO GJ\ufffdVIK AS',f'<footer>GS ELEKTRO GJØVIK AS Org.nr {ORG} © 2026 GS Elektro Gjøvik AS</footer>','GS Elektro Gjøvik AS'),
])
def test_generic_known_loss_repairs(name,site,title):
    p=page(site,title)
    result=candidate_proof(p,ORG,{**CONTEXT,'name':name},Candidate(p.url,'example.no','registry_website'),[])
    assert result.level=='VERIFIED'


def test_unicode_and_spacing_comparison_never_changes_legal_form_or_guesses_damage():
    assert same_name('ØKONOMI AS','Okonomi AS')
    assert same_name('CONTROL SOLUTIONS AS','ControlSolutions AS')
    assert not same_name('GJ\ufffdVIK AS','GJØVIK AS')
    assert same_name('GJ\ufffdVIK AS','GJØVIK AS',True)
    assert not same_name('Permobil AS','Permobil AB',True,True)
    assert not same_name('Control Solutions AS','Control Solution AS',False,True)
    p=page(f'<main>Our customer {ORG}</main>','Control Solution AS')
    context={**CONTEXT,'name':'Control Solutions AS'}
    assert proof_context(p,ORG,context)==context


def test_own_number_does_not_override_another_copyright_publisher():
    p=page(f'<footer>Org nr {ORG} Copyright Other AB</footer>','Example AS')
    assert candidate_proof(p,ORG,CONTEXT,Candidate(p.url,'example.no','registry_website'),[]).level=='REJECT'


def test_own_as_suffix_in_title_is_not_a_prefix_as_company():
    p=page(f'<footer>Example AS Org.nr {ORG}</footer>','Contact — Example AS Mini Bus Transportation in Norway')
    assert candidate_proof(p,ORG,CONTEXT,Candidate(p.url,'example.no','registry_website'),[]).level=='VERIFIED'


def test_title_prefix_allows_own_number_backed_singular_plural_variant():
    p=page(f'<footer>Org.nr {ORG}</footer>','Ta uforpliktende kontakt! — CONTROL SOLUTION AS')
    assert candidate_proof(p,ORG,{**CONTEXT,'name':'Control Solutions AS'},Candidate(p.url,'example.no','legal_name_slug'),[]).level=='VERIFIED'



def test_split_own_legal_name_in_footer_needs_exact_owner_number():
    p=page(f'<h1>GS ELEKTRO</h1><h1>GJØVIK AS</h1><footer><span>GS ELEKTRO</span><span>GJØVIK AS</span>Org.nr {ORG} © 2026 GS Elektro Gjøvik AS</footer>','')
    result=candidate_proof(p,ORG,{**CONTEXT,'name':'GS ELEKTRO GJ\ufffdVIK AS'},Candidate(p.url,'example.no','registry_email'),[])
    assert result.level=='VERIFIED' and result.proof_type=='orgnr_on_page'
    p=page(f'<h1>Example AS</h1><footer><span>Other</span><span>AB</span>Org.nr {OTHER}</footer>')
    assert candidate_proof(p,ORG,CONTEXT,Candidate(p.url,'example.no','registry_email'),[]).level=='REJECT'
