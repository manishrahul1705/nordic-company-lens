import pytest

from signalpost.web.html import Page
from signalpost.web.proof import score,orgnrs
from scripts.accuracy_audit import audit_website_claim
from tests.test_websites import OUR,OTHER,execute_web,html


def evaluate(body,context=None,url='https://example.no/'):
    context={'name':'Example AS','phone':'12345678','email':'office@example.no',**(context or {})}
    return score(Page(body.encode(),url),OUR,context,'legal_name_slug',[])


def test_suffix_absent_requires_two_contacts_and_name_derived_domain():
    body='<h1>Example</h1><footer>12 34 56 78 office@example.no</footer>'
    proof=evaluate(body)
    assert proof.level=='VERIFIED' and proof.proof_type=='legal_name_without_suffix_and_two_contacts'
    assert evaluate(body,url='https://unrelated.no/').level=='MEDIUM'
    one='<h1>Example</h1><footer>12 34 56 78</footer>'
    assert evaluate(one).level=='MEDIUM'
    assert evaluate('<h1>Example</h1>').level=='MEDIUM'
    ctx={'name':'Example AS','phone':'12345678','email':'office@example.no'}
    claim={'field':'official_website','value':{'final_url':'https://example.no','proof_type':proof.proof_type,'identity_level':'VERIFIED'}}
    assert audit_website_claim(OUR,claim,{},body,context=ctx)[0]=='CORRECT'
    assert audit_website_claim(OUR,claim,{},one,context=ctx)[0]=='INCORRECT'


@pytest.mark.parametrize('owner',[OTHER,'NO'+OTHER+'MVA'])
def test_suffix_rule_never_overrides_other_owner_identifier(owner):
    assert evaluate('<h1>Example</h1><footer>12345678 office@example.no Org.nr '+owner+'</footer>').level=='REJECT'


def test_repeated_same_contact_category_does_not_count_twice():
    assert evaluate('<h1>Example</h1><footer>12345678 12 34 56 78</footer>').level=='MEDIUM'
    assert evaluate('<h1>Example</h1><footer>office@example.no office@example.no</footer>').level=='MEDIUM'


def test_other_legal_name_same_contacts_never_verified():
    assert evaluate('<h1>Different Example</h1><footer>12345678 office@example.no</footer>',{'name':'Completely Different AS'}).level!='VERIFIED'


def test_suffix_proof_publishes_registry_evidence_and_matching_social(tmp_path,monkeypatch):
    import tests.test_websites as websites
    original=websites.entity
    def custom(org):return {**original(org),'navn':'Example AS','telefon':'12345678','epostadresse':'office@example.no'}
    monkeypatch.setattr(websites,'entity',custom)
    body=html('12345678 office@example.no',title='Example',extra='<footer><a href="https://facebook.com/example">Facebook</a></footer>').replace('<header>Example AS</header>','<header>Example</header>')
    _,row,_,_=execute_web(tmp_path,monkeypatch,body=body)
    c=next(c for c in row['claims'] if c['field']=='official_website' and c['availability']=='available')
    assert c['value']['proof_type']=='legal_name_without_suffix_and_two_contacts'
    assert any(e['source_class']=='official_registry' and e['id'] in c['evidence_ids'] for e in row['evidence'])


def test_prefixed_compact_vat_identifiers_are_not_missed():
    assert orgnrs('NO'+OUR+'MVA')=={OUR}
    assert orgnrs('Org.nr.: NO '+OUR[:3]+' '+OUR[3:6]+' '+OUR[6:]+' MVA')=={OUR}
