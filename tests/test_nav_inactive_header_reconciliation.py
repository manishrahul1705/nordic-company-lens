import asyncio

import httpx
import pytest

from signalpost.budget import Budget
from signalpost.runner import placeholder
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.nav import BASE, Index, prefetch, section
from signalpost.sources.nav_cached import Candidates
from tests.test_nav import ORG, UUID, TOKEN
from tests.test_nav_index import artifact
from tests.test_nav_streaming import header, SECOND
from tests.test_registry import config


def test_repeated_inactive_headers_keep_live_closure_complete(tmp_path):
    path, _ = artifact(tmp_path, [])
    cfg = config(tmp_path, [ORG], hiring=True, nav_index_path=path)
    index = Index()
    blobs = BlobStore(cfg.state_dir)
    calls = []

    async def names():
        return {ORG: {'Rareone AS'}}

    names.initial_names = {ORG: {'Rareone AS'}}

    async def response(request):
        if request.url.path == '/api/publicToken':
            return httpx.Response(200, text=TOKEN)
        if '/feedentry/' in request.url.path:
            calls.append(str(request.url))
            return httpx.Response(200, json={'uuid': UUID, 'status': 'INACTIVE'})
        page = request.url.path.rsplit('/', 1)[-1]
        if page == UUID:
            return httpx.Response(200, json={'items': [header(UUID, 'Rareone AS')],
                                           'next_url': BASE + '/api/v1/feed/' + SECOND})

        async def closed():
            while UUID not in index.live_closed:
                await asyncio.sleep(0)

        await asyncio.wait_for(closed(), 2)
        item = header(UUID, 'Rareone AS')
        item['_feed_entry']['status'] = 'INACTIVE'
        item['date_modified'] = '2026-10-29T12:02:13.610343Z' if page == SECOND else '2026-10-29T12:03:04.121191Z'
        return httpx.Response(200, json={
            'items': [item], 'next_url': BASE + '/api/v1/feed/00000000-0000-4000-8000-000000000003'
            if page == SECOND else None})

    async def execute():
        async with httpx.AsyncClient(transport=httpx.MockTransport(response)) as client:
            await prefetch(client, cfg, Budget(cfg), blobs, index, names)

    asyncio.run(execute())
    assert index.complete and index.company_complete(ORG)
    assert UUID in index.live_closed and UUID in index.closure_proofs
    assert len(calls) == 1
    env = placeholder(ORG, 'test', '2026-11-01T00:00:00Z')
    env.run.sections['subunits'] = 'not_available'
    result = section(env, index, blobs)
    assert result.state == 'not_available' and not result.claims and not result.errors


@pytest.mark.parametrize('outstanding', ['pending', 'failed', 'inflight'])
def test_inactive_header_cannot_hide_outstanding_detail(tmp_path, outstanding):
    _, data = artifact(tmp_path, [])
    index = Index(live_closed={UUID})
    state = Candidates(data, index, config(tmp_path, [ORG]), {})
    state.checked[UUID] = 'older'
    if outstanding == 'inflight':
        state.inflight.add(UUID)
    elif outstanding == 'failed':
        state.failed[UUID] = 'older'
    else:
        state.pending[UUID] = ('older', {ORG}, 'forward_feed')
    item = header(UUID, 'Rareone AS')
    item['_feed_entry']['status'] = 'INACTIVE'
    asyncio.run(state.page([item]))
    assert state.checked[UUID] == 'older'
    assert state.checked[UUID] != state.version(UUID)


def test_active_header_requires_new_proof_after_live_closure(tmp_path):
    _, data = artifact(tmp_path, [])
    index = Index(live_closed={UUID}, closed={UUID}, closure_proofs={UUID: ('old proof',)})
    state = Candidates(data, index, config(tmp_path, [ORG]), {})
    state.set_scopes({ORG: {ORG}}, {ORG: {'Rareone AS'}})
    state.checked[UUID] = 'older'
    asyncio.run(state.page([header(UUID, 'Rareone AS')]))
    assert UUID not in index.live_closed and UUID not in index.closure_proofs
    assert UUID in state.pending
    assert state.checked[UUID] != state.version(UUID)


def test_new_inactive_header_is_reconciled_after_inflight_detail_settles(tmp_path):
    _, data = artifact(tmp_path, [])
    state = Candidates(data, Index(live_closed={UUID}), config(tmp_path, [ORG]), {})
    state.checked[UUID] = 'older'
    state.inflight.add(UUID)
    item = header(UUID, 'Rareone AS')
    item['_feed_entry']['status'] = 'INACTIVE'
    asyncio.run(state.page([item]))
    assert not state.reconcile_closed(UUID)
    assert state.checked[UUID] == 'older'
    state.inflight.remove(UUID)
    assert state.reconcile_closed(UUID)
    assert state.checked[UUID] == state.version(UUID)
