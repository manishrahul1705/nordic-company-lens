import pytest
from signalpost.web.html import Page
from signalpost.web.proof import score
from signalpost.web.social import attributed, profile_url
from signalpost.web import shared_identifiers as shared
from signalpost.web.candidates import generate

ORG='999609384'
CONTEXT={'name':'Example Unique AS','email':'hello@example.no','phone':'12345678','postcode':'0123'}

@pytest.fixture(autouse=True)
def counts(monkeypatch):
    data={'phones':{'12345678':1},'email_domains':{'example.no':1},'name_keys':{'example unique':1}}
    monkeypatch.setattr(shared,'bundled',lambda filename:data if filename=='shared_identifiers.json.gz' else {})
    return data

def proof(html,context=None,url='https://candidate.no'):
    return score(Page(('<html><head></head><body>'+html+'</body></html>').encode(),url),ORG,context or CONTEXT,'cc_index',[])

def test_email_alone(counts):
    assert proof('<a href="mailto:hello@example.no">Email</a>').proof_type=='registry_email_on_site'
    assert proof('Contact hello@example.no.').proof_type=='registry_email_on_site'
    counts['email_domains']['example.no']=5
    assert proof('hello@example.no').level!='VERIFIED'

def test_freemail(counts):
    counts['email_domains']['gmail.com']=1
    assert proof('hello@gmail.com',{**CONTEXT,'email':'hello@gmail.com'}).level!='VERIFIED'

def test_exact_email_not_substring():
    assert proof('nothello@example.no').level!='VERIFIED'

def test_phone_alone(counts):
    assert proof('<a href="tel:+4712345678">Call</a>').proof_type=='registry_phone_on_site'
    counts['phones']['12345678']=5
    assert proof('12 34 56 78').level!='VERIFIED'

def test_mobile():
    assert proof('12 34 56 78',{**CONTEXT,'phone':'','mobile':'12345678'}).proof_type=='registry_phone_on_site'

def test_masthead():
    p=Page(b'<html><head><title>Example Unique AS</title></head><body>Welcome</body></html>','https://candidate.no')
    assert score(p,ORG,CONTEXT,'cc_index',[]).level!='VERIFIED'

def test_longer_name():
    p=Page(b'<html><head><title>Another Example Unique AS</title></head><body>Welcome</body></html>','https://candidate.no')
    assert score(p,ORG,CONTEXT,'cc_index',[]).level!='VERIFIED'

@pytest.mark.parametrize('html',['hello@example.no','12 34 56 78','Example Unique AS'])
def test_other_orgnr_veto(html):
    assert proof(html+'<footer>Org.nr 970540334</footer>').level=='REJECT'

def test_unique_domain(counts):
    assert proof('Example Unique',url='https://example-unique.no').level!='VERIFIED'
    counts['name_keys']['example unique']=2
    assert proof('Example Unique',url='https://example-unique.no').level!='VERIFIED'

def test_unique_domain_requires_no_and_tokens():
    assert proof('Example Unique',url='https://example-unique.com').level!='VERIFIED'
    assert proof('Example',url='https://example-unique.no').level!='VERIFIED'

@pytest.mark.parametrize('url',['https://facebook.com/sharer.php?u=x','https://facebook.com/groups/123','https://facebook.com/profile.php?id=1','https://instagram.com/example/reels/','https://linkedin.com/in/example','https://facebook.com/wix','https://instagram.com/shopify','https://facebook.com/'])
def test_social_exclusions(url):
    assert profile_url(url) is None

def test_verified_template_profile():
    p=Page(b'<footer><a href="https://facebook.com/tradingbrand">Facebook</a></footer>','https://candidate.no')
    assert not attributed(p,{'identity_level':'VERIFIED','final_url':p.url},CONTEXT)
    own=Page(b'<footer><a href="https://facebook.com/exampleunique">Facebook</a></footer>',p.url)
    assert attributed(own,{'identity_level':'VERIFIED','final_url':p.url},CONTEXT)
    assert not attributed(p,{'identity_level':'LOW','final_url':p.url},CONTEXT)

def test_page_plugin():
    p=Page(b'<iframe src="https://www.facebook.com/plugins/page.php?href=https%3A%2F%2Ffacebook.com%2Fexampleunique"></iframe>','https://candidate.no')
    assert 'https://facebook.com/exampleunique' in attributed(p,{'identity_level':'VERIFIED','final_url':p.url},CONTEXT)

def test_cc_candidates_are_ranked_not_proof(monkeypatch):
    monkeypatch.setattr(shared,'bundled',lambda _: {ORG:[{'domain':'archive.no'}]})
    candidates=generate({**CONTEXT,'orgnr':ORG,'website':'https://declared.no'})
    assert candidates[0].origin=='registry_website'
    cc=next(i for i,c in enumerate(candidates) if c.origin=='cc_index')
    assert cc<next(i for i,c in enumerate(candidates) if c.origin=='legal_name_slug')
    assert proof('No identity',url='https://archive.no').level!='VERIFIED'

def test_normalization():
    assert shared.phone_key('+47 123 45 678')=='12345678'
    assert shared.name_key('Example Holding AS')=='example'
    assert shared.name_key('Unique Example ASA')=='example unique'


def test_copyright_masthead():
    for marker in ('Copyright', chr(169)):
        assert proof('<footer>'+marker+' 2026 Example Unique AS</footer>').level!='VERIFIED'


def test_postcode_masthead():
    assert proof('<p>Example Unique AS</p><p>0123 Oslo</p>').level!='VERIFIED'


def test_longer_copyright_rejected():
    assert proof('<footer>Copyright 2026 Another Example Unique AS</footer>').level!='VERIFIED'


def test_parked_veto():
    assert proof('This domain is for sale hello@example.no').level=='REJECT'


def test_phone_evidence_localizes():
    p=Page(b'<footer>Phone: 12 34 56 78</footer>','https://candidate.no')
    result=score(p,ORG,CONTEXT,'cc_index',[])
    assert p.span_for(result.token)


@pytest.mark.parametrize('url',['https://facebook.com/wixcom','https://facebook.com/%73harer.php','https://facebook.com/proffno'])
def test_encoded_share_and_builder_variants(url):
    assert profile_url(url) is None


def test_hidden_plugin_cannot_publish():
    p=Page(b'<div hidden><iframe src="https://facebook.com/plugins/page.php?href=https%3A%2F%2Ffacebook.com%2Ftradingbrand"></iframe></div>','https://candidate.no')
    assert not attributed(p,{'identity_level':'VERIFIED','final_url':p.url},CONTEXT)


def test_missing_counts_never_imply_unique(counts):
    counts.clear()
    assert proof('12 34 56 78 hello@example.no').level!='VERIFIED'
    assert proof('Example Unique',url='https://exampleunique.no').level!='VERIFIED'


@pytest.mark.parametrize('body',['Her kommer: www.exampleunique.no','Contact post@exampleunique.no','www.exampleunique.no'])
def test_domain_and_email_repetition_never_proves_unique_name(body):
    assert proof(body,url='https://exampleunique.no').level!='VERIFIED'


def test_blank_app_shell_masthead_is_not_ownership():
    p=Page(b'<head><title>Example Unique AS</title></head><body><div id="root"></div></body>','https://candidate.no')
    assert score(p,ORG,CONTEXT,'cc_index',[]).level!='VERIFIED'


def test_shared_employee_email_cannot_identify_the_site_owner(counts):
    counts['email_domains']['example.no']=4
    assert proof('<div class="person">Employee <a href="mailto:hello@example.no">hello@example.no</a></div>').level!='VERIFIED'


@pytest.mark.parametrize('handle',['johnsmith','creativeworks','otherbusiness'])
def test_verified_site_footer_does_not_authorize_unrelated_accounts(handle):
    p=Page(('<footer><a href="https://facebook.com/'+handle+'">Follow</a></footer>').encode(),'https://candidate.no')
    assert not attributed(p,{'identity_level':'VERIFIED','final_url':p.url},CONTEXT)
