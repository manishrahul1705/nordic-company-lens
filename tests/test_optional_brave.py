import asyncio
import json
from types import SimpleNamespace
import pytest

from signalpost.budget import Budget
from signalpost.web.search import Search,Brave,active_for_search
from tests.test_registry import config
from tests.test_search import Fake,http,active_registry
from tests.test_websites import execute_web

ORG='923609016'
ACTIVE={'name':'Example AS','municipality':'Oslo','active_for_search':True}


@pytest.mark.parametrize('provider,key,enabled',[(None,None,False),(None,'fixture',False),('brave',None,False),('mock','fixture',False),('brave','fixture',True)])
def test_both_explicit_environment_values_required(tmp_path,monkeypatch,provider,key,enabled):
    for name,value in [('SIGNALPOST_SEARCH_PROVIDER',provider),('BRAVE_SEARCH_API_KEY',key)]:
        if value is None:monkeypatch.delenv(name,raising=False)
        else:monkeypatch.setenv(name,value)
    cfg=config(tmp_path,[ORG],max_cost_usd=1)
    search=Search(None,cfg,Budget(cfg))
    assert isinstance(search.provider,Brave)==enabled


@pytest.mark.parametrize('field,value,expected',[
    ('identity.employees',1,True),('identity.employees',0,False),('accounts.revenue',10,True),
    ('accounts.revenue',0,False),('accounts.history.2024.revenue',100,False),('accounts.net_result',100,False)])
def test_only_employees_or_latest_revenue_establish_search_eligibility(field,value,expected):
    row=SimpleNamespace(claims=[SimpleNamespace(field=field,value=value,availability='available')])
    assert active_for_search(row)==expected


def test_inactive_company_and_zero_global_cost_budget_do_not_query(tmp_path):
    for active,budget in [(False,1),(True,0)]:
        cfg=config(tmp_path/str(active),[ORG],max_cost_usd=budget);provider=Fake();search=Search(None,cfg,Budget(cfg),provider)
        assert asyncio.run(search.nominate(ORG,{**ACTIVE,'active_for_search':active},http()))==[]
        assert not provider.calls and search.metrics['queries']==0


def test_verified_website_uses_no_search_query(tmp_path,monkeypatch):
    active_registry(monkeypatch)
    provider=Fake()
    monkeypatch.setenv('BRAVE_SEARCH_API_KEY','synthetic-test-only')
    monkeypatch.setenv('SIGNALPOST_SEARCH_PROVIDER','brave')
    monkeypatch.setattr('signalpost.web.search.Brave',lambda *args:provider)
    report,_,_,_=execute_web(tmp_path,monkeypatch,max_cost_usd=1)
    assert report['search']['queries']==0 and not provider.calls


def test_search_nomination_with_foreign_owner_is_rejected(tmp_path,monkeypatch):
    from tests.test_websites import html
    active_registry(monkeypatch)
    monkeypatch.setenv('BRAVE_SEARCH_API_KEY','synthetic-test-only')
    monkeypatch.setenv('SIGNALPOST_SEARCH_PROVIDER','brave')
    monkeypatch.setattr('signalpost.web.search.Brave',lambda *args:Fake())
    monkeypatch.setattr('signalpost.web.collector.generate',lambda context:[])
    report,row,_,_=execute_web(tmp_path,monkeypatch,body=html('Org nr 993578843'),website=None,max_cost_usd=1)
    assert report['search']['queries']==1
    assert not any(c['field']=='official_website' and c['availability']=='available' for c in row['claims'])


def test_results_are_five_safe_domains_and_provider_errors_are_sanitized(tmp_path):
    class Provider:
        async def search(self,query,timeout):
            return [{'url':u} for u in ['https://[invalid','https://data.brreg.no/company','https://nrk.no/article','https://amazon.com/shop','https://proff.no/company','https://facebook.com/example',
                'https://utdanning.no/bedrift/926698435/',
                'https://www.vat-validation.com/company',
                'https://nordlei.no/lei/254900XUQRFIPTZYQ539/giljeholmen-as',
                'https://unlisted-provider.no/lei/254900XUQRFIPTZYQ539/company']]+[
                {'url':'https://other-lookup.no/company','title':'Example AS - LEI lookup'},
                {'url':'https://other-vat.no/company','description':'VAT number checker'},
                *[{'url':'https://candidate'+str(i)+'.no/'} for i in range(8)]]
    cfg=config(tmp_path,[ORG],max_cost_usd=1);search=Search(None,cfg,Budget(cfg),Provider())
    candidates=asyncio.run(search.nominate(ORG,ACTIVE,http()))
    assert len(candidates)==5 and all(c.domain.startswith('candidate') for c in candidates)
    class Failure:
        async def search(self,query,timeout):raise RuntimeError('fixture-private-marker')
    budget=Budget(cfg);search=Search(None,cfg,budget,Failure())
    assert not asyncio.run(search.nominate(ORG,ACTIVE,http()))
    assert 'fixture-private-marker' not in json.dumps([search.metrics,budget.events])


def test_search_has_only_ten_extra_dns_checks_and_keeps_public_ip_filter(tmp_path):
    from signalpost.budget import SourceFailure
    from signalpost.web.candidates import Candidate
    from signalpost.web.fetcher import WebsiteHttp
    from signalpost.sources.blobstore import BlobStore
    async def public(host,port=443):return ['93.184.216.34']
    cfg=config(tmp_path,[ORG],websites=True)
    async def check():
        crawler=WebsiteHttp(None,cfg,Budget(cfg),BlobStore(cfg.state_dir),public)
        crawler.dns_counts[ORG]=64
        with pytest.raises(SourceFailure):
            await crawler.precheck(Candidate('https://free.no/','free.no','legal_name_slug'),ORG)
        for i in range(10):
            await crawler.precheck(Candidate(f'https://candidate{i}.no/',f'candidate{i}.no','search_brave'),ORG)
        with pytest.raises(SourceFailure):
            await crawler.precheck(Candidate('https://eleventh.no/','eleventh.no','search_brave'),ORG)
        assert crawler.dns_counts[ORG]==74
        async def private(host,port=443):return ['127.0.0.1']
        crawler.resolver=private
        with pytest.raises(SourceFailure) as error:
            await crawler.precheck(Candidate('https://private.no/','private.no','search_brave'),'993578843')
        assert error.value.code=='ssrf'
    asyncio.run(check())
