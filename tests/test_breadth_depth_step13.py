import asyncio
import json
import time
from collections import Counter
from datetime import datetime,timezone
from types import SimpleNamespace
import pytest
from signalpost.web.brands import labels,candidates,actual_names
from signalpost.web.candidates import Candidate
from signalpost.web.collector import candidate_proof
from signalpost.web.html import Page
from signalpost.web.second_pass import candidates as retry_candidates,run as second_pass
from signalpost.sources.extract import Section,Source,add
from signalpost.sources.http import Response
from signalpost.sources.blobstore import BlobStore
from signalpost.runner import placeholder,update,isolate
from signalpost.budget import SourceFailure
from signalpost.config import Config
from signalpost.models.envelope import Error
from tests.test_recall_step10 import ORG,OTHER,CONTEXT


def test_brand_variants_are_actual_names_bounded_and_no_before_com():
    names=[('Blå Ørn AS avdeling Oslo','registered_subunit',['support'])]
    values=candidates(names,set())
    assert len(values)<=4
    assert values[0][0].domain=='blaorn.no'
    assert [c.domain.rsplit('.',1)[1] for c,_ in values]==['no','no','com','com']
    assert all(s['evidence_ids']==['support'] for _,s in values)
    assert labels('AS Avdeling Oslo')==[]
    assert labels('Hjem Service AS')==[] and labels('AB AS')==[]
    assert all(c.domain!='blaorn.no' for c,_ in candidates(names,{'blaorn.no'}))


def test_brand_name_alone_never_verifies():
    p=Page(b'<title>Bright Fox</title><h1>Bright Fox</h1>','https://brightfox.no')
    assert candidate_proof(p,ORG,CONTEXT,Candidate(p.url,'brightfox.no','brand_name'),[]).level!='VERIFIED'
    p=Page(('<title>Bright Fox</title><footer>Org nr '+OTHER+'</footer>').encode(),p.url)
    assert candidate_proof(p,ORG,CONTEXT,Candidate(p.url,'brightfox.no','brand_name'),[]).level=='REJECT'


def test_nav_brand_uses_exact_verified_employer_and_subunit_registry_chain(tmp_path):
    blobs=BlobStore(tmp_path);row=placeholder(ORG,'test','2026-11-06T00:00:00Z',('identity','hiring','subunits'))
    for employer in [ORG,OTHER]:
        raw=json.dumps({'ad_content':{'employer':{'orgnr':employer,'name':'Bright Fox'}}}).encode()
        source=Source('https://pam-stilling-feed.nav.no/api/v1/feedentry/'+employer,raw,blobs.put(raw),'2026-11-06T00:00:00Z')
        section=Section();add(section,source,ORG,'hiring','hiring.job.'+employer,{'employer_orgnr':employer},'/ad_content')
        row.claims+=section.claims;row.evidence+=section.evidence
    names=actual_names(row,CONTEXT,blobs)
    assert len(names)==1 and names[0][:2]==('Bright Fox','exact_nav_employer')


def retry_row():
    row=placeholder(ORG,'test','2026-11-06T00:00:00Z',('identity','website'))
    row.run.sections['website']='failed'
    row.errors=[Error(section='website',code='website_candidates',message=json.dumps([
        {'domain':'first.no','reason':'dns_servfail'},{'domain':'second.no','status':429},
        {'domain':'absent.no','reason':'no_such_domain'},{'domain':'forbidden.no','status':403},
        {'domain':'third.no','reason':'website_timeout'},{'domain':'fourth.no','reason':'website_connect_error'}]))]
    row.run.refresh['recall_round2']={'candidates':[{'domain':d,'origin':'registry_email'} for d in ['first.no','second.no','absent.no','forbidden.no','third.no','fourth.no']]}
    return row


def test_second_pass_is_top_three_transient_only_never_nxdomain_or_403():
    row=retry_row();assert [c.domain for c in retry_candidates(row)]==['first.no','second.no','third.no']
    row.run.sections['website']='available';assert retry_candidates(row)==[]


def test_second_pass_clears_failed_dns_uses_same_budget_and_preserves_failure(tmp_path,monkeypatch):
    from signalpost.web import collector
    row=retry_row();budget=SimpleNamespace(events=[],by_company=Counter(),deadline=time.monotonic()+30,check=lambda:None)
    config=Config(organisations=tmp_path/'in',output=tmp_path/'out',report=tmp_path/'report')
    http=SimpleNamespace(config=config,budget=budget,dns_cache={'first.no':'dns_servfail','www.first.no':'dns_unavailable'},accepted_pages={})
    async def fetch(org,envelope,bulk,http,previous,nav,retry_candidates):
        assert 'first.no' not in http.dns_cache and not http.config.website_transient_retry
        assert len(retry_candidates)==3
        budget.events.append({'organisation_number':org})
        return Section(state='not_available')
    monkeypatch.setattr(collector,'fetch',fetch)
    result=asyncio.run(second_pass({ORG:row},http,{}, {},None,isolate,update))
    assert result['attempted']==1 and result['requests']==1 and result['recovered']==0
    assert row.run.sections['website']=='failed' and http.config is config


def test_second_pass_never_dispatches_past_company_cap(tmp_path,monkeypatch):
    row=retry_row();budget=SimpleNamespace(events=[],by_company=Counter({ORG:40}),deadline=time.monotonic()+30,check=lambda:None)
    config=Config(organisations=tmp_path/'in',output=tmp_path/'out',report=tmp_path/'report')
    result=asyncio.run(second_pass({ORG:row},SimpleNamespace(config=config,budget=budget),{}, {},None,isolate,update))
    assert result['attempted']==result['requests']==0


def test_second_pass_success_is_recorded_and_original_budget_is_used(tmp_path,monkeypatch):
    from signalpost.web import collector
    row=retry_row();blobs=BlobStore(tmp_path/'blobs')
    budget=SimpleNamespace(events=[],by_company=Counter(),deadline=time.monotonic()+30,check=lambda:None)
    config=Config(organisations=tmp_path/'in',output=tmp_path/'out',report=tmp_path/'report')
    http=SimpleNamespace(config=config,budget=budget,dns_cache={},accepted_pages={})
    async def fetch(org,envelope,bulk,transport,previous,nav,retry_candidates):
        assert transport.budget is budget
        body=('<footer>Org nr '+ORG+'</footer>').encode();source=Source('https://first.no',body,blobs.put(body),'2026-11-06T00:00:00Z')
        result=Section();add(result,source,ORG,'website','official_website',{'final_url':'https://first.no'},'/proof',source_class='company_owned')
        budget.events.append({'organisation_number':org});return result
    monkeypatch.setattr(collector,'fetch',fetch)
    result=asyncio.run(second_pass({ORG:row},http,{}, {},None,isolate,update))
    assert result['recovered']==result['requests']==1 and result['unexpected_failures']==0
    assert row.run.sections['website']=='available' and row.run.refresh['website_second_pass']['recovered']


def test_every_returned_financial_year_is_retained_with_exact_period(tmp_path):
    from signalpost.sources.regnskap import extract
    from tests.test_multiyear_financials import make_account_row,make_response
    rows=[make_account_row(ORG,y) for y in range(2019,2026)]
    response=make_response('https://data.brreg.no/regnskapsregisteret/regnskap/'+ORG,rows)
    section=extract(ORG,response,BlobStore(tmp_path))
    revenues=[c for c in section.claims if c.field=='accounts.revenue' or c.field.endswith('.revenue')]
    assert {c.reporting_period['fiscal_year'] for c in revenues}=={str(y) for y in range(2019,2026)}
    assert len({c.field for c in section.claims})==len(section.claims)


def test_all_role_codes_including_deputies_and_contacts_with_no_duplicate(tmp_path):
    from signalpost.sources.brreg_roller import extract
    codes=['DAGL','LEDE','NEST','MEDL','VARA','REVI','REGN','KONT']
    roles=[{'type':{'kode':code},'person':{'navn':{'fornavn':'Person','etternavn':code}}} for code in codes]
    body=json.dumps({'organisasjonsnummer':ORG,'rollegrupper':[{'roller':roles+[roles[-1]]}]}).encode()
    section=extract(ORG,Response(body,200,'https://data.brreg.no/enhetsregisteret/api/enheter/'+ORG+'/roller','2026-11-06T00:00:00Z',BlobStore(tmp_path).put(body)))
    assert {c.value['role_type']['kode'] for c in section.claims if c.field.startswith('roles.role.')}==set(codes)
    assert len(section.claims)==len(codes)


def test_postal_addresses_project_as_typed_places_and_deduplicate(tmp_path):
    from signalpost.profiles import project
    blobs=BlobStore(tmp_path);row=placeholder(ORG,'test','2026-11-06T00:00:00Z',('identity','subunits'))
    body=b'{}';source=Source('https://data.brreg.no/test',body,blobs.put(body),'2026-11-06T00:00:00Z')
    section=Section()
    for field,value in [('identity.registered_address',{'adresse':['Gate 1'],'postnummer':'0123'}),('identity.postal_address',{'adresse':['Postboks 9'],'postnummer':'0124'})]:add(section,source,ORG,'identity',field,value,'/'+field)
    update(row,'identity',section)
    place=project(row)['evidence']['locations']['value']['locations']
    assert [p['type'] for p in place]==['registered_business_address','registered_postal_address']
    row.claims[-1].value=row.claims[-2].value
    place=project(row)['evidence']['locations']['value']['locations'];assert len(place)==1


def test_postbox_abbreviations_deduplicate_without_merging_postcodes():
    from signalpost.locations import address_key
    assert address_key({'adresse':'PB 993','postnummer':'4682'})==address_key({'adresse':['Postboks 993'],'postnummer':'4682'})
    assert address_key({'adresse':'PB993','postnummer':'4682'})!=address_key({'adresse':'Postboks 993','postnummer':'4683'})


def test_activity_discovery_does_not_truncate_eleven_supported_candidates():
    from signalpost.web.activity import parse_html
    body=''.join(f'<article><a href="/news/item-{n}">Headline {n}</a><time datetime="2026-01-01">Jan</time></article>' for n in range(12)).encode()
    assert len(parse_html(body,'https://example.no/news',datetime.now(timezone.utc)))==12


def test_article_alias_redirects_publish_one_canonical_claim(tmp_path):
    from signalpost.web.activity import publish_articles
    body=b'<html><title>New office</title><main><h1>New office</h1><time datetime="2026-01-01">January</time><p>Our own company announces its new office and services in Norway. This is a genuine dated news article about our work.</p></main></html>'
    blobs=BlobStore(tmp_path)
    class Http:
        async def get(self,*args,**kwargs):return Response(body,200,'https://example.no/news/canonical','2026-11-06T00:00:00Z',blobs.put(body))
    proof=SimpleNamespace(value={'final_url':'https://example.no','identity_level':'VERIFIED'},id='proof')
    section=Section();items=[({'url':'https://example.no/news/'+name},'/item','') for name in ['alias-a','alias-b']]
    asyncio.run(publish_articles(section,items,ORG,proof,Http(),set()))
    assert len(section.claims)==1 and section.claims[0].value['url']=='https://example.no/news/canonical'
