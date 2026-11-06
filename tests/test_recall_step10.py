import asyncio
import json
from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from signalpost.web.html import Page
from signalpost.web.proof import score
from signalpost.web.candidates import generate, bounded_variants
from signalpost.web.collector import candidate_proof
from signalpost.web.candidates import Candidate
from signalpost.web.social import attributed
from signalpost.web.jobs import active_job
from signalpost.web.recall import annual_domains, redirect_names_company, prove_unique_core
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.http import Response
from signalpost.budget import Budget, SourceFailure
from tests.test_registry import config, numbers

ORG='923609016'; SUB='982257867'; OTHER='993578843'
CONTEXT={'name':'Example AS','phone':'12345678','email':'office@example.no','street':['Example gate 1'], 'postcode':'0123','city':'OSLO'}


def page(text, title='Company', url='https://example.no/'):
    return Page(f'<html><head><title>{title}</title></head><body><main>{text}</main></body></html>'.encode(),url)


@pytest.mark.parametrize('name',['Example AS','Example'])
def test_tier_a_declared_exact_name_needs_no_contact(name):
    proof=score(page(name),ORG,CONTEXT,'registry_website',[],nominated_contacts=True)
    assert proof.level=='VERIFIED' and proof.proof_type=='registry_declared_name_tier_a'


@pytest.mark.parametrize('text',['<a href="tel:12345678">Call</a>','office@example.no','Example gate 1','0123 OSLO','Jane Person'])
def test_tier_b_hard_corroboration_without_name(text):
    proof=score(page(text),ORG,CONTEXT,'registry_website',['Jane Person'],nominated_contacts=True)
    assert proof.level=='VERIFIED' and proof.proof_type=='registry_declared_hard_contact_tier_b'


@pytest.mark.parametrize('text',[f'Example AS Org nr {OTHER}','Example AB','Example AS this domain is for sale','Example AS welcome to nginx','Example AS domain is parked'])
def test_declared_signal_never_overrides_veto(text):
    assert score(page(text),ORG,CONTEXT,'registry_website',[],nominated_contacts=True).level=='REJECT'


def test_email_nomination_requires_two_independent_categories():
    assert score(page('Example'),ORG,CONTEXT,'registry_email',[],nominated_contacts=True).level!='VERIFIED'
    accepted=score(page('Example <a href="tel:12345678">Call</a>'),ORG,CONTEXT,'registry_email',[],nominated_contacts=True)
    assert accepted.level=='VERIFIED' and accepted.proof_type=='nominated_two_independent_signals'
    address_only=score(page('Example gate 1 0123 OSLO'),ORG,{**CONTEXT,'name':'Unrelated AS'},'registry_email',[],nominated_contacts=True)
    assert address_only.level!='VERIFIED'  # Street + postcode are one address category.


def test_any_registered_subunit_id_can_prove_parent_site():
    context={**CONTEXT,'subunits':[{'orgnr':SUB,'name':'Trading Shop'}]}
    proof=candidate_proof(page('Trading Shop Org nr '+SUB),ORG,context,Candidate('https://example.no','example.no','registry_email'),[],SimpleNamespace())
    assert proof.level=='VERIFIED' and proof.subject_orgnr==SUB


@pytest.mark.parametrize('name',['Example Holding AS','Example Invest AS','Kapital Example AS','Sameiet Solsiden','Sol Borettslag'])
def test_investment_and_housing_names_skip_guesses(name):
    assert not bounded_variants(name)


def test_guess_limit_and_trading_name_interleaving():
    candidates=generate({'name':'Ærlig Ørn AS','subunits':[{'orgnr':SUB,'name':'Unique Trading Shop'}]})
    guessed=[c for c in candidates if c.origin in {'legal_name_slug','subunit_name_slug'}]
    assert len(guessed)<=4
    assert any(c.origin=='subunit_name_slug' for c in guessed)
    assert any('aerlig' in c.domain or 'erlig' in c.domain for c in guessed)


def test_unique_name_is_registry_confirmed_and_non_no_needs_street_postcode():
    context={**CONTEXT,'unique_registry_core':True}
    assert score(page('Example'),ORG,context,'legal_name_slug',[]).proof_type=='unique_legal_core_domain'
    assert score(page('Example',url='https://example.com'),ORG,context,'legal_name_slug',[]).level!='VERIFIED'
    assert score(page('Example Example gate 1 0123 OSLO',url='https://example.com'),ORG,context,'legal_name_slug',[]).level=='VERIFIED'
    assert score(page('Example'),ORG,CONTEXT,'legal_name_slug',[]).level!='VERIFIED'


def test_uniqueness_query_must_be_complete_and_include_only_this_core(tmp_path):
    blobs=BlobStore(tmp_path);calls=[]
    class Registry:
        extra=False
        async def get(self,url,org):
            calls.append(url)
            rows=[{'organisasjonsnummer':ORG,'navn':'Example AS'}]+([{'organisasjonsnummer':OTHER,'navn':'Example ASA'}] if self.extra else [])
            body=json.dumps({'_embedded':{'enheter':rows},'page':{'totalPages':1,'totalElements':len(rows)}}).encode()
            return Response(body,200,url,'2026-11-06T00:00:00Z',blobs.put(body))
    registry=Registry();context=dict(CONTEXT)
    assert asyncio.run(prove_unique_core(ORG,context,SimpleNamespace(registry_http=registry)))
    assert context['unique_registry_core']
    registry.extra=True
    assert not asyncio.run(prove_unique_core(ORG,dict(CONTEXT),SimpleNamespace(registry_http=registry)))
    assert len(calls)==2


def test_redirect_requires_company_identity_not_only_a_phone():
    assert not redirect_names_company(page('12345678'),ORG,CONTEXT)
    assert redirect_names_company(page('Example'),ORG,CONTEXT)
    assert redirect_names_company(page('Org nr '+ORG),ORG,CONTEXT)


def test_contact_links_and_jsonld_social_keep_owner_matching():
    p=page('<main><a href="https://instagram.com/example">Instagram</a><a href="https://linkedin.com/in/employee">Staff</a><div class="social-share"><a href="https://facebook.com/example">Share</a></div></main>',url='https://example.no/kontakt')
    links=attributed(p,{'identity_level':'VERIFIED','final_url':'https://example.no'},CONTEXT)
    assert 'https://instagram.com/example' in links
    assert not any('employee' in u or 'facebook' in u for u in links)


def job_page(**overrides):
    node={'@type':'JobPosting','title':'Engineer','url':'https://example.teamtailor.com/jobs/1','datePosted':'2026-10-01','validThrough':'2099-01-01','hiringOrganization':{'name':'Example AS','identifier':ORG},**overrides}
    return page('<script type="application/ld+json">'+json.dumps(node)+'</script>',url='https://example.teamtailor.com/jobs/1')


def test_only_single_active_exact_employer_postings_publish():
    assert active_job(job_page(),ORG,{ORG:'Example AS'},{ORG})['status']=='ACTIVE'
    assert active_job(job_page(validThrough='2020-01-01'),ORG,{ORG:'Example AS'},{ORG}) is None
    assert active_job(job_page(hiringOrganization={'name':'Other AS','identifier':OTHER}),ORG,{ORG:'Example AS'},{ORG}) is None
    assert active_job(job_page(hiringOrganization={'name':'Example AS'}),ORG,{ORG:'Example AS'},{ORG}) is None
    assert active_job(job_page(hiringOrganization={'name':'Example ASA','identifier':ORG}),ORG,{ORG:'Example AS'},{ORG}) is None
    assert active_job(job_page(validThrough=None),ORG,{ORG:'Example AS'},{ORG}) is None
    assert active_job(page('<a href="/jobs/1">Careers</a>'),ORG,{ORG:'Example AS'},{ORG}) is None


def test_pooled_budget_allows_forty_but_keeps_global_eighteen_per_input(tmp_path):
    orgs=numbers(3);budget=Budget(config(tmp_path,orgs))
    for _ in range(40):budget.reserve('https://example.no','example.no',orgs[0])
    with pytest.raises(SourceFailure,match='company_budget_exhausted'):budget.reserve('https://example.no','example.no',orgs[0])
    for _ in range(14):budget.reserve('https://example.no','example.no',orgs[1])
    with pytest.raises(SourceFailure,match='budget_exhausted'):budget.reserve('https://example.no','example.no',orgs[2])
    assert budget.hard_request_cap==54


def test_tier_b_emits_only_the_link_including_refresh_content_guard(tmp_path, monkeypatch):
    from tests.test_websites import execute_web
    from signalpost.models.envelope import Envelope
    body=b'<html><title>Welcome</title><main>Call 12 34 56 78</main><footer><a href="https://instagram.com/example">Instagram</a><p>Our excellent company services.</p></footer></html>'
    _,row,_,_=execute_web(tmp_path,monkeypatch,body=body.decode())
    proof=next(c for c in row['claims'] if c['field']=='official_website')
    assert proof['value']['publication_tier']=='B' and proof['value']['content_allowed'] is False
    assert [c['field'] for c in row['claims'] if c['family']=='website' and c['availability']=='available']==['official_website']


def test_declared_shared_domain_is_withheld_even_with_own_number(tmp_path, monkeypatch):
    from tests.test_websites import execute_web
    from signalpost.web import recall
    monkeypatch.setattr(recall,'shared_owners',lambda host:{OTHER,SUB} if host=='example.no' else set())
    _,row,_,_=execute_web(tmp_path,monkeypatch)
    assert not any(c['field']=='official_website' for c in row['claims'])
    assert row['run']['sections']['website']=='ambiguous'


def test_careers_to_ats_to_single_active_job(tmp_path):
    from signalpost.web.jobs import fetch
    from signalpost.sources.extract import Section, Source, add
    from signalpost.runner import placeholder, update
    from signalpost.web.html import Page
    blobs=BlobStore(tmp_path);row=placeholder(ORG,'test','2026-11-06T00:00:00Z',('identity','website','hiring'))
    source=Source('https://example.no',b'Example AS',blobs.put(b'Example AS'),'2026-11-06T00:00:00Z')
    identity=Section();add(identity,source,ORG,'identity','identity.legal_name','Example AS','/name',span='Example AS');update(row,'identity',identity)
    website=Section();add(website,source,ORG,'website','official_website',{'final_url':'https://example.no','identity_level':'VERIFIED','content_allowed':True},'/site',span='Example AS');update(row,'website',website)
    class Http:
        calls=[]
        accepted_pages={ORG:[(None,page('<a href="/careers">Careers</a>'))]}
        async def get(self,url,org,candidate_domain,**kwargs):
            self.calls.append(url)
            if url=='https://example.no/careers':body=b'<a href="https://example.teamtailor.com">Jobs</a>'
            elif url=='https://example.teamtailor.com/':body=b'<a href="/jobs/1">Engineer</a>'
            else:body=job_page().body
            return Response(body,200,url,source.retrieved_at,blobs.put(body))
    http=Http();result=asyncio.run(fetch(row,http))
    assert result.state=='available' and len(result.claims)==1
    assert result.claims[0].value['source']=='company_site'
    assert len(http.calls)==3 and all(e.claim_span for e in result.evidence)


def test_registered_location_is_typed_and_deduplicates_workplace(tmp_path):
    from tests.test_synthesis import envelope
    from signalpost.profiles import project
    from signalpost.locations import registered_location
    from signalpost.models.claim import Claim
    from signalpost.models.evidence import digest
    row,_=envelope(tmp_path)
    address=registered_location(row.claims)
    assert address
    raw=project(row)
    assert any(v.get('type')=='registered_business_address' for v in raw['evidence']['locations']['value']['locations'])
    row.claims.append(Claim(field='subunits.unit.'+SUB,value={'organisation_number':SUB,'name':'Workplace','address':address.value},availability='available',evidence_ids=address.evidence_ids,id=digest(['location',SUB]),family='subunits',first_observed_at=address.first_observed_at,last_observed_at=address.last_observed_at))
    assert registered_location(row.claims) is None


def test_annual_report_candidates_use_only_retained_text_and_do_not_download(tmp_path):
    from signalpost.runner import placeholder, update
    from signalpost.sources.extract import Section, Source, add
    blobs=BlobStore(tmp_path)
    row=placeholder(ORG,'test','2026-11-06T00:00:00Z',('accounts',))
    body=b'{"company":"Example AS", "website":"https://example.no", "schema":"https://xbrl.org"}'
    source=Source('https://data.brreg.no/report',body,blobs.put(body),'2026-11-06T00:00:00Z')
    section=Section()
    add(section,source,ORG,'accounts','accounts.report',{'website':'https://example.no'},'/website',span='https://example.no')
    update(row,'accounts',section)
    assert annual_domains(row,blobs)==['example.no']


def test_feed_date_cannot_replace_an_article_publication_date():
    from signalpost.web.activity import article
    body=('<main><h1>News</h1><p>'+'Company news with sufficient article text. '*5+'</p></main>').encode()
    assert article(body,'https://example.no/news/item',datetime.now(timezone.utc),('2026-10-01','pubDate')) is None
