import asyncio
import json
from types import SimpleNamespace
from datetime import datetime,timezone
import pytest
from signalpost.web.html import Page
from signalpost.web.candidates import Candidate
from signalpost.web.collector import candidate_proof
from signalpost.web.round2 import named,real_page,unique_eligible,unique_registry,proof_targets
from signalpost.web.jobs import active_job,board_scope,within_board,staffing
from tests.test_recall_step10 import CONTEXT,ORG,SUB,OTHER,job_page


def page(body,url='https://example.no/',title='Welcome'):
    return Page(('<html><head><title>'+title+'</title></head><body>'+body+'</body></html>').encode(),url)


@pytest.mark.parametrize('body,title',[
    ('<h1>Example</h1>','Welcome'),('<footer>Example</footer>','Welcome'),
    ('<img src="logo.svg" alt="Example">','Welcome'),('<meta property="og:site_name" content="Example">','Welcome'),('', 'Example'),
])
def test_email_declaration_requires_name_in_approved_identity(body,title):
    p=page(body,title=title);candidate=Candidate(p.url,'example.no','registry_email')
    result=candidate_proof(p,ORG,CONTEXT,candidate,[])
    assert result.level=='VERIFIED' and result.proof_type=='registry_declared_name_tier_a'
    assert getattr(result,'rule',None)=='A'


def test_email_body_name_alone_does_not_establish_declared_identity():
    p=page('<main>Example is mentioned in our customer story.</main>')
    assert candidate_proof(p,ORG,CONTEXT,Candidate(p.url,'example.no','registry_email'),[]).level!='VERIFIED'


def test_email_link_only_and_provider_mismatch():
    p=page('Call 12345678')
    assert candidate_proof(p,ORG,CONTEXT,Candidate(p.url,'example.no','registry_email'),[]).level!='VERIFIED'
    p=page('<h1>Example</h1>',title='Example regnskapskontor')
    assert candidate_proof(p,ORG,{**CONTEXT,'nace':'47.100'},Candidate(p.url,'example.no','registry_email'),[]).reason=='provider_industry_mismatch'
    assert candidate_proof(p,ORG,{**CONTEXT,'nace':'69.201'},Candidate(p.url,'example.no','registry_email'),[]).level=='VERIFIED'


def test_prefix_as_publisher_is_not_the_email_domain_subject():
    p=page('<h1>AS Betongbygg</h1> Call 12345678')
    assert candidate_proof(p,ORG,CONTEXT,Candidate(p.url,'example.no','registry_email'),[]).reason=='different_legal_entity'


@pytest.mark.parametrize('label',['Utgitt av Example AS','All rettigheter reservert - Example AS'])
def test_own_publisher_prefix_is_not_another_legal_entity(label):
    assert real_page(page('<footer>'+label+'</footer>'),CONTEXT) is None


@pytest.mark.parametrize('subject,publisher',[
    ('Example', 'Example Norge AS'),
    ('Example AS', 'Example Norge AS'),
    ('Example', 'Example AB'),
])
def test_complete_footer_publisher_cannot_only_contain_subject_core(subject,publisher):
    assert real_page(page('<footer><p>'+publisher+'</p></footer>'),
                     {**CONTEXT,'name':subject}) == 'different_legal_entity'


def test_complete_footer_publisher_allows_exact_core_without_form():
    assert real_page(page('<footer><p>Example AS</p></footer>'),
                     {**CONTEXT,'name':'Example'}) is None


def test_final_publisher_guard_preserves_own_number_title_variant():
    p=page('<footer>Org.nr '+ORG+'</footer>',title='Example Solution AS')
    assert real_page(p,{**CONTEXT,'name':'Example Solutions AS','allowed_orgnrs':{ORG}}) is None
    assert real_page(p,{**CONTEXT,'name':'Example Solutions AS','allowed_orgnrs':{'000000000'}}) == 'different_legal_entity'


def test_board_member_and_auditor_do_not_establish_website_ownership():
    from signalpost.web.round2 import registered_leaders
    claims=[SimpleNamespace(family='roles',value={'name':name,'role_type':{'kode':role}})
            for name,role in [('Director Name','DAGL'),('Chair Name','LEDE'),('Shared Founder','MEDL'),('Audit Firm','REVI')]]
    assert registered_leaders(claims)==['Director Name','Chair Name']


@pytest.mark.parametrize('origin,signals',[
    ('registry_email',['registry_declared_domain','street','postcode']),
    ('registry_website',['registry_declared_domain','registered_role_holder']),
])
def test_rejected_contact_trials_cannot_return_from_previous_snapshot(tmp_path,origin,signals):
    from signalpost.web.entity_scope import enforce
    from signalpost.runner import placeholder,update
    from signalpost.sources.blobstore import BlobStore
    from signalpost.sources.extract import Source,Section,add
    blobs=BlobStore(tmp_path);row=placeholder(ORG,'test','2026-11-06T00:00:00Z',('identity','website'))
    body=b'<html><title>Another brand</title><main>Shared Founder, CTO. Shared street 1, 0123.</main></html>'
    source=Source('https://anotherbrand.no',body,blobs.put(body),'2026-11-06T00:00:00Z')
    identity=Section();add(identity,source,ORG,'identity','identity.legal_name','Example AS','/name');update(row,'identity',identity)
    role=Section();add(role,source,ORG,'roles','roles.person',{'name':'Shared Founder','role_type':{'kode':'MEDL'}},'/role');update(row,'roles',role)
    website=Section();add(website,source,ORG,'website','official_website',{'final_url':source.url,'proof_type':'registry_declared_hard_contact_tier_b','candidate_origin':origin,'signals':signals},'/website',source_class='company_owned')
    website.claims[0].carried_forward=True;update(row,'website',website)
    enforce([row],blobs,SimpleNamespace(domain_owners={}))
    assert row.run.sections['website']=='ambiguous'
    assert not any(c.field=='official_website' for c in row.claims)


@pytest.mark.parametrize('body',['<h1>Example</h1> Coming soon','<h1>Example</h1> This domain is for sale',
    '<frameset><frame src="https://other.no"></frameset>','<h1>Example</h1> Index of /',
    '<h1>Example</h1> Proudly Served by LiteSpeed','<h1>Example</h1><footer>Other AS</footer>'])
def test_new_rules_never_rescue_placeholders_or_foreign_publishers(body):
    p=page(body)
    assert candidate_proof(p,ORG,CONTEXT,Candidate(p.url,'example.no','registry_email'),[]).level=='REJECT'
    assert not unique_eligible(p,CONTEXT,[])


def test_subunit_declaration_accepts_registered_subunit_identity():
    p=page('<h1>Branch Shop</h1>')
    ctx={**CONTEXT,'subunits':[{'orgnr':SUB,'name':'Branch Shop'}]}
    result=candidate_proof(p,ORG,ctx,Candidate(p.url,'example.no','subunit_registry_email',SUB),[])
    assert result.level=='VERIFIED' and result.subject_orgnr==SUB and result.rule=='B'


def test_strict_unique_no_needs_corroboration_and_identity():
    assert unique_eligible(page('<h1>Example</h1> Oslo'),{**CONTEXT,'municipality':'OSLO'},[])
    assert unique_eligible(page('<footer>Example</footer> 0123'),CONTEXT,[])
    assert not unique_eligible(page('<h1>Example</h1>'),CONTEXT,[])
    assert not unique_eligible(page('<h1>Example</h1> Oslo',url='https://example.com'),{**CONTEXT,'municipality':'OSLO'},[])
    assert not unique_eligible(page('<main>Example Oslo</main>'),{**CONTEXT,'municipality':'OSLO'},[])


def test_registry_uniqueness_is_complete_and_cached(tmp_path):
    from signalpost.sources.blobstore import BlobStore
    from signalpost.sources.http import Response
    blobs=BlobStore(tmp_path)
    class Http:
        calls=0
        async def get(self,url,org):
            self.calls+=1;body=json.dumps({'page':{'totalPages':1,'totalElements':1},'_embedded':{'enheter':[{'organisasjonsnummer':ORG,'navn':'Example AS'}]}}).encode()
            return Response(body,200,url,'2026-11-06T00:00:00Z',blobs.put(body))
    registry=Http();http=SimpleNamespace(registry_http=registry)
    assert asyncio.run(unique_registry(ORG,CONTEXT,http))
    assert asyncio.run(unique_registry(ORG,CONTEXT,http)) and registry.calls==1


@pytest.mark.parametrize('page_info,entries',[
    ({'totalPages':2,'totalElements':1},[{'organisasjonsnummer':ORG,'navn':'Example AS'}]),
    ({'totalPages':1,'totalElements':2},[{'organisasjonsnummer':ORG,'navn':'Example AS'}]),
    ({'totalPages':1,'totalElements':2},[{'organisasjonsnummer':ORG,'navn':'Example AS'},{'organisasjonsnummer':OTHER,'navn':'Example ASA'}]),
])
def test_incomplete_or_nonunique_registry_query_never_proves_site(tmp_path,page_info,entries):
    from signalpost.sources.blobstore import BlobStore
    from signalpost.sources.http import Response
    blobs=BlobStore(tmp_path)
    class Registry:
        async def get(self,url,org):
            body=json.dumps({'page':page_info,'_embedded':{'enheter':entries}}).encode()
            return Response(body,200,url,'2026-11-06T00:00:00Z',blobs.put(body))
    assert not asyncio.run(unique_registry(ORG,CONTEXT,SimpleNamespace(registry_http=Registry())))


def test_sitemap_proof_paths_are_same_domain_and_bounded():
    class Http:
        async def get(self,*args,**kwargs):
            return SimpleNamespace(status=200,body=b'<urlset><url><loc>https://example.no/custom/impressum</loc></url><url><loc>https://other.no/about</loc></url></urlset>')
    p=page('<footer><a href="/company/contact">Contact</a></footer>')
    targets=asyncio.run(proof_targets(p,p.url,Http(),ORG,['https://example.no/about']*8))
    assert targets==['https://example.no/company/contact','https://example.no/custom/impressum','https://example.no/about']


def test_linked_board_can_authorize_no_org_but_never_a_different_employer():
    p=job_page(hiringOrganization={'name':'Example AS'})
    assert active_job(p,ORG,{ORG:'Example AS'},{ORG},linked_board=True)['employer_identity_proof']=='linked_board'
    assert active_job(job_page(hiringOrganization={'name':'Other AS'}),ORG,{ORG:'Example AS'},{ORG},linked_board=True) is None
    assert active_job(job_page(hiringOrganization={'identifier':OTHER}),ORG,{ORG:'Example AS'},{ORG},linked_board=True) is None
    assert active_job(job_page(validThrough='2020-01-01'),ORG,{ORG:'Example AS'},{ORG},linked_board=True) is None
    scope=board_scope('https://example.teamtailor.com')
    assert within_board('https://example.teamtailor.com/jobs/1',scope)
    assert not within_board('https://other.teamtailor.com/jobs/1',scope)
    assert board_scope('https://www.webcruiter.com/') is None
    assert staffing(page('We are a staffing agency.'))


@pytest.mark.parametrize('employer,accepted',[('Example AS',True),('Other AS',False)])
def test_company_to_shared_ats_board_to_individual_job_retains_link_chain(tmp_path,employer,accepted):
    from signalpost.web.jobs import fetch
    from signalpost.runner import placeholder,update
    from signalpost.sources.extract import Section,Source,add
    from signalpost.sources.http import Response
    from signalpost.sources.blobstore import BlobStore
    blobs=BlobStore(tmp_path)
    row=placeholder(ORG,'test','2026-11-06T00:00:00Z',('identity','website','hiring'))
    body=b'<title>Example AS</title><a href="/careers">Careers</a>'
    source=Source('https://example.no/',body,blobs.put(body),'2026-11-06T00:00:00Z')
    identity=Section();add(identity,source,ORG,'identity','identity.legal_name','Example AS','/name');update(row,'identity',identity)
    website=Section();add(website,source,ORG,'website','official_website',{'final_url':'https://example.no','identity_level':'VERIFIED','content_allowed':True},'/website');update(row,'website',website)
    initial=Response(body,200,source.url,source.retrieved_at,source.sha)
    class Http:
        accepted_pages={ORG:[(initial,Page(body,source.url))]}
        async def get(self,url,*args,**kwargs):
            if url=='https://example.no/careers':raw=b'<a href="https://emp.jobylon.com/companies/42-example/">Careers board</a>'
            elif '/companies/' in url:raw=b'<h1>Example Careers</h1><a href="/jobs/123-engineer/">Engineer</a>'
            else:
                raw=('<script type="application/ld+json">'+json.dumps({'@type':'JobPosting','title':'Engineer','url':url,'datePosted':'2026-01-01','validThrough':'2099-01-01','hiringOrganization':{'name':employer}})+'</script>').encode()
            return Response(raw,200,url,source.retrieved_at,blobs.put(raw))
    result=asyncio.run(fetch(row,Http()))
    assert bool(result.claims)==accepted
    if accepted:
        assert result.claims[0].value['employer_identity_proof']=='linked_board'
        urls={e.source_url for e in result.evidence}
        assert {'https://example.no/','https://example.no/careers','https://emp.jobylon.com/companies/42-example/'}<=urls
