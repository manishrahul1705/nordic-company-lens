import pytest
from signalpost.web.html import Page
from signalpost.web.proof import score
from scripts.accuracy_audit import audit_website_claim
from tests.test_websites import OUR, OTHER, execute_web, html


def evaluate(body, name='Northlight AS', url='https://northlight.no/', **context):
    context={'name':name, **context}
    proof=score(Page(body.encode(),url),OUR,context,'legal_name_slug',[],domain_location=True)
    return proof, context

@pytest.mark.parametrize('body,ctx', [
    ('<footer>Office in Bergen</footer>', {'municipality':'BERGEN'}),
    ('<footer>0461</footer>', {'postcode':'0461'}),
])
def test_exact_domain_and_visible_registry_location(body,ctx):
    proof,context=evaluate(body,**ctx)
    assert proof.proof_type=='domain_legal_name_and_registry_location'
    claim={'field':'official_website','value':{'final_url':'https://northlight.no/','proof_type':proof.proof_type,'identity_level':'VERIFIED'}}
    assert audit_website_claim(OUR,claim,{},body,context=context)[0]=='CORRECT'

@pytest.mark.parametrize('name,url', [
    ('Northlight AS','https://northlightas.no/'),
    ('Northlight AS','https://northlight.other.no/'),
    ('Short AS','https://short.no/'),
    ('Service AS','https://service.no/'),
    ('Bygg Service AS','https://byggservice.no/'),
])
def test_partial_short_or_generic_domains_never_prove(name,url):
    assert evaluate('<footer>Bergen</footer>',name,url,municipality='BERGEN')[0].level!='VERIFIED'

@pytest.mark.parametrize('body,ctx', [
    ('<script>"Bergen"</script>', {'municipality':'BERGEN'}),
    ('<article>Customer in Bergen</article>', {'municipality':'BERGEN'}),
    ('<footer>Bergenhus</footer>', {'municipality':'BERGEN'}),
    ('<footer>104610</footer>', {'postcode':'0461'}),
    ('<footer>Oslo</footer>', {'municipality':'BERGEN'}),
    ('<footer>Bergen Org.nr '+OTHER+'</footer>', {'municipality':'BERGEN'}),
])
def test_missing_location_and_conflicts_do_not_prove(body,ctx):
    assert evaluate(body,**ctx)[0].level!='VERIFIED'


def test_location_proof_publishes_local_span_and_registry_evidence(tmp_path,monkeypatch):
    import tests.test_websites as websites
    original=websites.entity
    monkeypatch.setattr(websites,'entity',lambda org:{**original(org),'navn':'Example AS','forretningsadresse':{'kommune':'BERGEN','postnummer':'5000'}})
    body=html('Office in Bergen',title='Welcome').replace('<header>Example AS</header>','')
    _,row,_,_=execute_web(tmp_path,monkeypatch,body=body,website_domain_location_proof=True)
    proof=next(c for c in row['claims'] if c['field']=='official_website')
    assert proof['value']['proof_type']=='domain_legal_name_and_registry_location'
    assert any(e['source_class']=='official_registry' and e['id'] in proof['evidence_ids'] for e in row['evidence'])
    assert any('Bergen' in e.get('claim_span','') for e in row['evidence'] if e['id'] in proof['evidence_ids'])
