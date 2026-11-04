import asyncio
from types import SimpleNamespace

import httpx

from signalpost.sources.nav_stream import detail_capacity
from signalpost.sources.nav import BASE,Index,prefetch
from signalpost.budget import Budget
from signalpost.sources.blobstore import BlobStore
from tests.test_registry import config
from tests.test_nav import ORG,TOKEN,UUID
from tests.test_nav_streaming import header,ad,warm_scorer


def test_detail_capacity_uses_time_service_rate_and_request_room(tmp_path):
    cfg=config(tmp_path,[ORG],nav_concurrency=4,nav_time_cap_seconds=100)
    budget=SimpleNamespace(deadline=100,cap=2000,events=[{'url':BASE+'/api/v1/feedentry/'+UUID,'runtime_ms':200}])
    index=Index();index.metrics['detail_requests']=1
    assert detail_capacity(cfg,budget,index,0,now=10)==1801
    assert detail_capacity(cfg,budget,index,0,now=90)==201
    budget.cap=8
    assert detail_capacity(cfg,budget,index,0,now=90)==8
    assert detail_capacity(cfg,budget,index,0,now=100)==1


def test_explicit_detail_limit_is_preserved(tmp_path):
    cfg=config(tmp_path,[ORG],nav_max_details=0)
    assert detail_capacity(cfg,SimpleNamespace(),Index(),0,now=0)==0


def test_stale_index_page_cap_is_explicit_and_never_complete(tmp_path):
    warm_scorer()
    from tests.test_nav_index import artifact
    path,_=artifact(tmp_path,[],built_at='2026-01-01T00:00:00Z')
    cfg=config(tmp_path,[ORG],hiring=True,nav_index_path=path,nav_max_pages=1)
    async def names():return {ORG:{'Rareone AS'}}
    def response(request):
        if request.url.path=='/api/publicToken':return httpx.Response(200,text=TOKEN)
        if '/feedentry/' in request.url.path:return httpx.Response(200,json=ad(UUID,ORG))
        return httpx.Response(200,json={'items':[header(UUID,'Rareone AS')],
            'next_url':BASE+'/api/v1/feed/'+UUID,'next_id':UUID})
    async def run():
        index=Index()
        async with httpx.AsyncClient(transport=httpx.MockTransport(response)) as client:
            await prefetch(client,cfg,Budget(cfg),BlobStore(cfg.state_dir),index,names)
        return index
    index=asyncio.run(run())
    assert index.metrics['source_mode']=='full_feed_fallback'
    assert index.metrics['index_fallback_reason']=='index_stale'
    assert index.metrics['page_cap_exceeded'] and index.metrics['page_cap']==1
    assert index.metrics['unread_next_url']==BASE+'/api/v1/feed/'+UUID
    assert not index.complete and not index.metrics['feed_complete']
    assert not index.company_complete(ORG) and 'nav_page_cap' in index.reason
    assert index.ads[ORG][0].value['employer_orgnr']==ORG
