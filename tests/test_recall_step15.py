"""Step15 nomination/extraction breadth does not relax ownership or vetoes."""
import asyncio,json,socket
from types import SimpleNamespace
import httpx,pytest
from signalpost.budget import Budget,SourceFailure
from signalpost.sources.blobstore import BlobStore
from signalpost.web.candidates import generate,bounded_variants,Candidate
from signalpost.web.collector import proof_page_targets,candidate_proof
from signalpost.web.fetcher import WebsiteHttp
from signalpost.web.html import Page
from signalpost.web.proof import score
from signalpost.web.social import attributed,profile_url
from tests.test_registry import config
ORG='923609016';OTHER='988330752';CONTEXT={'name':'Example Services AS'}

def page(body):return Page(('<html><head><title>Example Services</title></head><body>'+body+'</body></html>').encode(),'https://exampleservices.no/')
def prove(body):return score(page(body),ORG,CONTEXT,'legal_name_slug',[])

def test_bounded_names_norwegian_variants_and_no_before_com():
    urls=bounded_variants('Bl\u00e5 \u00d8rn \u00c6ra AS')
    assert len(urls)<=8 and len(urls)==len(set(urls))
    assert 'blaaoernaera.no' in urls and 'blaornera.no' in urls
    assert all(u.endswith(('.no','.com')) for u in urls)
    assert sorted(urls,key=lambda u:u.endswith('.com'))==urls
    assert 'nordvest.no' in bounded_variants('Nord Vest Holding ASA')
    assert 'arktisholding.no' in bounded_variants('Arktis Holding AS')
    assert not bounded_variants('AS')
    assert all('holding' not in u for u in bounded_variants('Nord Vest Holding AS'))
    assert len([c for c in generate({'name':'Long Trading Name AS'}) if c.origin=='legal_name_slug'])<=8

@pytest.mark.parametrize('email,expected',[('office@exampleservices.no',True),('x@gmail.com',False),('x@outlook.com',False),('x@broadpark.no',False),('x@getmail.no',False),('x@online.no',False)])
def test_email_nomination_excludes_providers_and_never_proves_itself(email,expected):
    nominated=[c for c in generate({**CONTEXT,'email':email}) if c.origin=='registry_email']
    assert bool(nominated)==expected
    assert prove('Example Services AS').level!='VERIFIED'

def test_dns_failure_for_guessed_candidate_makes_no_http_request(tmp_path):
    calls=[]
    async def resolver(host,port):raise SourceFailure('no_such_domain')
    def respond(request):calls.append(request);return httpx.Response(200)
    cfg=config(tmp_path,[ORG],websites=True,website_transient_retry=False)
    async def go():
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            http=WebsiteHttp(client,cfg,Budget(cfg),BlobStore(cfg.state_dir),resolver)
            with pytest.raises(SourceFailure):await http.candidate(Candidate('https://missing.no','missing.no','legal_name_slug'),ORG)
    asyncio.run(go());assert calls==[]

def test_three_same_host_contact_links_and_exact_spaced_vat():
    p=page('<footer><a href="/kontakt-oss">Kontakt oss</a><a href="/personvernerklaering">Personvern</a><a href="/om">Om oss</a><a href="https://other.no/kontakt">Kontakt</a></footer>')
    targets=proof_page_targets(p,p.url)
    assert len(targets)==3 and all(u.startswith('https://exampleservices.no/') for u in targets)
    assert prove('<footer>Example Services AS Org nr NO 923 609 016 MVA</footer>').level=='VERIFIED'
    assert prove('<footer>Similar Example Services AS Org nr '+OTHER+'</footer>').level=='REJECT'

@pytest.mark.parametrize('script',[
    '<script>window.config={"businessInfo":{"name":"Example Services AS","orgnr":"NO 923 609 016 MVA"}};</script>',
    '<script type="application/json">{"organization":{"legalName":"Example Services AS","organizationNumber":"923609016"}}</script>',
    '<footer style="display:none">Example Services AS Org.nr 923 609 016</footer>'])
def test_hidden_explicit_owner_number_proves_without_changing_vetoes(script):
    result=prove(script);assert result.level=='VERIFIED' and result.proof_type=='raw_owner_identifier'
    assert prove('<h1>This domain is for sale</h1>'+script).level=='REJECT'
    assert prove('<footer>Copyright Other Owner AS</footer>'+script).level=='REJECT'

def test_arbitrary_script_customer_numbers_never_prove_ownership():
    for raw in ['<script>const tracking=923609016;</script>', '<script>{"customers":[{"name":"Example Services AS","orgnr":"923609016"}]}</script>','<script>{"businessInfo":{"name":"Other AS","orgnr":"923609016"}}</script>', '<script type="application/json">[{"@type":"Organization","name":"Example Services AS","orgnr":"923609016"}]</script>']:
        assert prove(raw).level!='VERIFIED'

def test_same_name_different_org_owner_stays_vetoed_in_script():
    assert prove('<script>{"organization":{"name":"Example Services AS","orgnr":"'+OTHER+'"}}</script>').level=='REJECT'

def test_header_footer_social_keeps_exact_handle_and_excludes_agency_share_home_employee():
    p=page('<header><a href="https://linkedin.com/company/exampleservices">LinkedIn</a></header><footer><a href="https://instagram.com/exampleservices">Instagram</a><span class="agency-credit"><a href="https://facebook.com/exampleservices">Agency</a></span><a href="https://facebook.com/sharer.php?u=x">Share</a><a href="https://linkedin.com/">Platform</a><a href="https://linkedin.com/in/person">Employee</a></footer>')
    proof={'identity_level':'VERIFIED','final_url':p.url,'proof_page_url':p.url,'other_orgnrs':[]}
    links=attributed(p,proof,CONTEXT)
    assert set(links)=={'https://linkedin.com/company/exampleservices','https://instagram.com/exampleservices'}
    assert not profile_url('https://linkedin.com/')

def test_group_suffixed_handle_without_declared_brand_is_not_relaxed():
    p=page('<footer><a href="https://linkedin.com/company/exampleservices-group">Follow us</a></footer>')
    assert not attributed(p,{'identity_level':'VERIFIED','final_url':p.url,'proof_page_url':p.url,'other_orgnrs':[]},CONTEXT)


def test_proof_page_order_preserves_legacy_links_then_common_paths():
    p=page('<footer><a href="/about">About</a><a href="/kontakt">Kontakt</a><a href="/om-oss">Om oss</a></footer>')
    targets=proof_page_targets(p,p.url,limit=7)
    assert targets[:3]==['https://exampleservices.no/kontakt','https://exampleservices.no/about','https://exampleservices.no/om-oss']
    assert targets.index('https://exampleservices.no/about') < targets.index('https://exampleservices.no/personvern')
    assert len(targets)<=7


@pytest.mark.parametrize('origin,expected',[
    ('legal_name_slug','not_available'),('registry_email','not_available'),
    ('subunit_registry_email','not_available'),('registry_website','failed'),
    ('subunit_registry_website','failed'),('wikidata_website','failed'),
    ('previous_verified','failed')])
@pytest.mark.parametrize('code',['dns_timeout','dns_servfail','no_such_domain','website_tls_error','website_connect_error','website_timeout'])
def test_candidate_transport_failure_only_fails_strong_sources(tmp_path,monkeypatch,origin,expected,code):
    from signalpost.web import collector
    from tests.test_websites import execute_web
    candidate=Candidate('https://example.com/','example.com',origin)
    monkeypatch.setattr(collector,'generate',lambda context:[candidate])
    if origin=='previous_verified':
        monkeypatch.setattr(collector,'previous_nomination',lambda *args:(candidate,None))
    async def fail(self,*args,**kwargs):raise SourceFailure(code)
    monkeypatch.setattr(WebsiteHttp,'candidate',fail)
    _,row,_,_=execute_web(tmp_path,monkeypatch)
    assert row['run']['sections']['website']==expected
    assert not any(c['field']=='official_website' for c in row['claims'])



def test_unwrapped_ssl_error_on_speculative_candidate_is_not_section_exception(tmp_path,monkeypatch):
    import ssl
    from signalpost.web import collector
    from tests.test_websites import execute_web
    monkeypatch.setattr(collector,'generate',lambda context:[Candidate('https://example.com/','example.com','legal_name_slug')])
    def response(request):raise ssl.SSLError('TLS handshake failed')
    _,row,_,_=execute_web(tmp_path,monkeypatch,response=response,website_transient_retry=False)
    assert row['run']['sections']['website']=='not_available'
    assert not any(e['code']=='section_exception' for e in row['errors'])
