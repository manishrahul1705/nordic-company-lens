from pathlib import Path
from signalpost.config import Config
from signalpost.web.html import Page
from signalpost.web.proof import score
from signalpost.web.collector import candidate_proof
from signalpost.web.candidates import Candidate


def test_experimental_owner_rules_are_independent_and_default_off():
    cfg=Config(organisations=Path('batch'),output=Path('out'),report=Path('report'))
    assert not cfg.website_suffix_contact_proof and not cfg.website_domain_location_proof
    candidate=Candidate('https://example.no/','example.no','legal_name_slug')
    ctx={'name':'Example AS','phone':'12345678','email':'hello@example.no'}
    page=Page(b'<h1>Example</h1><footer>12345678 hello@example.no</footer>',candidate.url)
    assert candidate_proof(page,'923609016',ctx,candidate,[],cfg).level!='VERIFIED'
    assert candidate_proof(page,'923609016',ctx,candidate,[],cfg.model_copy(update={'website_suffix_contact_proof':True})).level=='VERIFIED'
    page=Page(b'<footer>Bergen</footer>',candidate.url)
    ctx={'name':'Example AS','municipality':'BERGEN'}
    assert candidate_proof(page,'923609016',ctx,candidate,[],cfg).level!='VERIFIED'
    assert candidate_proof(page,'923609016',ctx,candidate,[],cfg.model_copy(update={'website_suffix_contact_proof':True})).level!='VERIFIED'
    assert candidate_proof(page,'923609016',ctx,candidate,[],cfg.model_copy(update={'website_domain_location_proof':True})).level=='VERIFIED'
