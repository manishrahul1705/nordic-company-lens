"""Recorded SPARQL-shape fixtures are synthetic, not real-company assertions."""
import asyncio
import json
from pathlib import Path

import httpx
import pytest

from signalpost.budget import Budget
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.extract import Section,Source,add
from signalpost.runner import placeholder
from signalpost.models.evidence import utc_now
from signalpost.web.candidates import generate
from signalpost.web.wikidata import fetch_batch,websites,publish_social,parse
from tests.test_registry import config,numbers


BODY=Path('tests/fixtures/wikidata-response.json').read_bytes()
ORG='923609016'


def test_exact_org_query_nominates_but_does_not_verify(tmp_path):
    cfg=config(tmp_path,[ORG],websites=True,wikidata=True);budget=Budget(cfg);blobs=BlobStore(cfg.state_dir)
    requests=[]
    def dispatch(request):
        requests.append(request)
        assert 'wdt:P2333 ?org' in request.url.params['query']
        assert ORG in request.url.params['query']
        assert 'github.com/manishrahul1705/nordic-company-lens' in request.headers['User-Agent']
        return httpx.Response(200,content=BODY)
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(dispatch)) as client:
            return await fetch_batch([ORG],client,cfg,budget,blobs)
    index=asyncio.run(run())
    assert len(requests)==1 and index['metrics']['matched_companies']==1
    assert websites(index,ORG)==['https://example.no/']
    assert '993578843' not in index['records']
    candidate=next(c for c in generate({'wikidata_homepages':websites(index,ORG)}) if c.domain=='example.no')
    assert candidate.origin=='wikidata_website'
    nominations=generate({'name':'Distinctive AS','wikidata_homepages':['https://example.no/']})
    assert nominations[0].origin=='wikidata_website'
    row=placeholder(ORG,'test',utc_now());section=Section()
    add(section,Source('https://data.brreg.no',b'Example AS','a'*64,utc_now()),ORG,'identity','identity.legal_name','Example AS','/')
    row.claims=section.claims
    publish_social(index,ORG,row,blobs)
    social=[c for c in row.claims if c.field.startswith('social_profile.')]
    assert len(social)==1 and social[0].value['url']=='https://www.facebook.com/example'
    assert social[0].value['licence']=='CC0' and social[0].value['item_url'].endswith('/Q123456')
    assert not any(c.field=='official_website' for c in row.claims)
    assert next(e for e in row.evidence if e.id in social[0].evidence_ids).source_class=='wikidata'
    from scripts.accuracy_audit import audit_social_claim
    evidence=next(e for e in row.evidence if e.id in social[0].evidence_ids)
    assert audit_social_claim(ORG,social[0].model_dump(),evidence.model_dump(),BODY.decode(),context={'name':'Example AS'})[0]=='CORRECT'
    assert audit_social_claim('993578843',social[0].model_dump(),evidence.model_dump(),BODY.decode(),context={'name':'Example AS'})[0]=='INCORRECT'
    assert (cfg.state_dir/'wikidata-index.json').exists()


def test_batches_200_and_empty_response_are_cached(tmp_path):
    ns=numbers(201);cfg=config(tmp_path,ns,websites=True,wikidata=True);calls=[]
    def dispatch(request):calls.append(request);return httpx.Response(200,json={'results':{'bindings':[]}})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(dispatch)) as client:
            return await fetch_batch(ns,client,cfg,Budget(cfg),BlobStore(cfg.state_dir))
    index=asyncio.run(run())
    assert len(calls)==2 and index['metrics']['status']=='complete'
    assert len(index['records'])==0


def test_throttled_endpoint_nonfatal_and_stops_further_requests(tmp_path):
    ns=numbers(201);cfg=config(tmp_path,ns,websites=True,wikidata=True);calls=[]
    def dispatch(request):calls.append(request);return httpx.Response(429,headers={'Retry-After':'120'},text='throttled')
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(dispatch)) as client:
            return await fetch_batch(ns,client,cfg,Budget(cfg),BlobStore(cfg.state_dir))
    index=asyncio.run(run())
    assert len(calls)==1 and index['metrics']['errors']==1 and not index['records']


def test_malformed_or_foreign_identity_cannot_inject_candidate():
    data=json.loads(BODY)
    for binding in data['results']['bindings']:binding['item']['value']='https://evil.test/entity/Q123'
    assert parse(json.dumps(data).encode(),{ORG})==[]
    assert parse(b'{"results":{"bindings":[{"org":null,"item":[]}]}}',{ORG})==[]


@pytest.mark.parametrize('failure',['timeout','malformed'])
def test_unavailable_source_does_not_fail_agent_discovery(tmp_path,failure):
    cfg=config(tmp_path,[ORG],websites=True,wikidata=True)
    def dispatch(request):
        if failure=='timeout':raise httpx.ReadTimeout('fixture timeout')
        return httpx.Response(200,text='{invalid')
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(dispatch)) as client:
            return await fetch_batch([ORG],client,cfg,Budget(cfg),BlobStore(cfg.state_dir))
    index=asyncio.run(run())
    assert index['metrics']['status']=='incomplete' and not index['records']
