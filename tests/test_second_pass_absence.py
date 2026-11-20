import asyncio
from collections import Counter
import json
import time
from types import SimpleNamespace

import pytest
from signalpost.budget import SourceFailure
from signalpost.config import Config
from signalpost.models.envelope import Error
from signalpost.runner import update,isolate
from signalpost.sources.extract import Section
from signalpost.web.second_pass import candidates,run
from tests.test_breadth_depth_step13 import retry_row,ORG


def row(reason='website_timeout',extra=()):
    r=retry_row();r.run.sections['website']='not_available'
    r.errors=[Error(section='website',code='website_candidates',message=json.dumps([
        {'domain':'first.no','reason':reason,'level':'LOW','candidate_not_reachable':True},*extra]))]
    return r


@pytest.mark.parametrize('reason',['website_timeout','website_connect_error','dns_timeout','dns_unavailable'])
def test_new_transient_candidates_are_admitted(reason):
    assert [c.domain for c in candidates(row(reason))]==['first.no']


@pytest.mark.parametrize('reason',['no_such_domain','website_tls_error','robots','robots_unavailable',
    'foreign_orgnr','different_legal_entity','shared_registry_domain','name_only','insufficient_owner_proof',
    'dns_servfail','http_403'])
def test_definitive_or_out_of_scope_failure_not_admitted(reason):
    assert candidates(row(reason))==[]


@pytest.mark.parametrize('reason',['foreign_orgnr','different_legal_entity','shared_registry_domain','parent_group_without_exact_orgnr','parked'])
def test_veto_on_same_candidate_cannot_be_overridden_by_transient(reason):
    assert candidates(row(extra=[{'domain':'first.no','reason':reason,'level':'REJECT'}]))==[]


def test_one_nxdomain_fallback_does_not_hide_final_transient_summary():
    r=row('dns_timeout',extra=[{'domain':'first.no','url':'http://www.first.no/','reason':'no_such_domain'}])
    assert len(candidates(r))==1


def setup(tmp_path,remaining=30):
    cfg=Config(organisations=tmp_path/'in',output=tmp_path/'out',report=tmp_path/'report')
    budget=SimpleNamespace(events=[],by_company=Counter(),deadline=time.monotonic()+remaining,check=lambda:None)
    http=SimpleNamespace(config=cfg,budget=budget,dns_cache={'first.no':'dns_unavailable'},accepted_pages={})
    return http


def test_one_retry_and_no_second_dispatch_on_reentry(tmp_path,monkeypatch):
    http=setup(tmp_path);r=row();calls=[]
    async def fetch(org,envelope,bulk,http,previous,nav,retry_candidates):
        calls.append(retry_candidates)
        assert not http.config.website_transient_retry and http.budget is budget
        assert 'first.no' not in http.dns_cache
        return Section(state='not_available')
    budget=http.budget
    monkeypatch.setattr('signalpost.web.collector.fetch',fetch)
    asyncio.run(run({ORG:r},http,{}, {},None,isolate,update))
    asyncio.run(run({ORG:r},http,{}, {},None,isolate,update))
    assert len(calls)==1 and len(calls[0])==1 and candidates(r)==[]
    assert r.run.sections['website']=='not_available'


def test_company_budget_exhaustion_prevents_dispatch(tmp_path,monkeypatch):
    http=setup(tmp_path);http.budget.by_company[ORG]=40;r=row()
    async def fetch(*a,**k):pytest.fail('no request beyond company cap')
    monkeypatch.setattr('signalpost.web.collector.fetch',fetch)
    result=asyncio.run(run({ORG:r},http,{}, {},None,isolate,update))
    assert result['attempted']==0 and r.run.refresh['website_second_pass']['reason']=='company_budget_exhausted'


def test_pooled_budget_error_preserves_original_without_deadline(tmp_path,monkeypatch):
    http=setup(tmp_path);r=row()
    async def fetch(*a,**k):raise SourceFailure('budget_exhausted')
    monkeypatch.setattr('signalpost.web.collector.fetch',fetch)
    result=asyncio.run(run({ORG:r},http,{}, {},None,isolate,update))
    assert result['recovered']==0 and r.run.sections['website']=='not_available'
    assert not any(e.code=='deadline' for e in r.errors)


def test_no_dispatch_when_deadline_is_near(tmp_path,monkeypatch):
    http=setup(tmp_path,.1);r=row()
    async def fetch(*a,**k):pytest.fail('late optional retry')
    monkeypatch.setattr('signalpost.web.collector.fetch',fetch)
    result=asyncio.run(run({ORG:r},http,{}, {},None,isolate,update))
    assert result['attempted']==0 and r.run.refresh['website_second_pass']['reason']=='retry_window_closed'
    assert not any(e.code=='deadline' for e in r.errors)


def test_slow_retry_cancelled_before_deadline_without_deadline_error(tmp_path,monkeypatch):
    http=setup(tmp_path,.7);r=row()
    async def fetch(*a,**k):await asyncio.sleep(5)
    monkeypatch.setattr('signalpost.web.collector.fetch',fetch)
    result=asyncio.run(run({ORG:r},http,{}, {},None,isolate,update))
    assert time.monotonic()<http.budget.deadline
    assert result['recovered']==0 and r.run.refresh['website_second_pass']['reason']=='second_pass_timeout'
    assert not any(e.code=='deadline' for e in r.errors)


def test_retry_result_must_pass_unchanged_proof_and_veto(tmp_path,monkeypatch):
    from signalpost.web.html import Page
    from signalpost.web.collector import candidate_proof
    from signalpost.web.candidates import Candidate
    from tests.test_recall_step10 import CONTEXT,OTHER
    http=setup(tmp_path);r=row()
    async def fetch(org,envelope,bulk,http,previous,nav,retry_candidates):
        p=Page(('<html><head><title>Example AS</title></head><body><footer>Org nr '+OTHER+'</footer></body></html>').encode(),'https://first.no/')
        proof=candidate_proof(p,org,CONTEXT,Candidate(p.url,'first.no','registry_email'),[],http.config)
        assert proof.level=='REJECT'
        return Section(state='not_available')
    monkeypatch.setattr('signalpost.web.collector.fetch',fetch)
    result=asyncio.run(run({ORG:r},http,{}, {},None,isolate,update))
    assert result['recovered']==0 and r.run.sections['website']=='not_available'


def test_optional_activity_timeout_does_not_erase_proven_website(tmp_path,monkeypatch):
    from signalpost.sources.extract import Source,add
    http=setup(tmp_path,.7);http.config=http.config.model_copy(update={'public_activity':True});r=row()
    async def fetch(org,envelope,bulk,http,previous,nav,retry_candidates):
        section=Section();body=b'Exact organisation number'
        add(section,Source('https://first.no/',body,'a'*64,'2026-11-20T00:00:00Z'),org,'website',
            'official_website',{'identity_level':'VERIFIED','proof_type':'orgnr_on_page'},'/',span=body.decode())
        return section
    async def activity(*args):await asyncio.sleep(5)
    monkeypatch.setattr('signalpost.web.collector.fetch',fetch)
    monkeypatch.setattr('signalpost.web.activity.fetch',activity)
    result=asyncio.run(run({ORG:r},http,{}, {},None,isolate,update))
    assert time.monotonic()<http.budget.deadline
    assert result['recovered']==1 and r.run.sections['website']=='available'
    assert any(c.field=='official_website' for c in r.claims)
    assert not any(e.code=='deadline' for e in r.errors)
