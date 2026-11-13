import asyncio
from collections import Counter
import httpx
import pytest
from signalpost.budget import Budget, SourceFailure
from signalpost.sources.blobstore import BlobStore
from signalpost.web.fetcher import WebsiteHttp
from signalpost.web.candidates import generate
from signalpost.web.jobs import board_scope, within_board
from tests.test_registry import config

ORG = '923609016'


def test_apex_www_are_one_nomination():
    items = generate({'name': 'Example AS', 'website': 'https://www.example.no',
                      'email': 'office@example.no', 'nav_homepages': ['https://example.no']})
    assert len([c for c in items if c.domain == 'example.no']) == 1
    assert items[0].origin == 'registry_website'


def test_activity_keeps_original_allowance_and_careers_cap_failure_is_honest(tmp_path):
    async def run():
        cfg = config(tmp_path, [ORG, '982257867', '993578843']).model_copy(update={'website_politeness_seconds': 0})
        budget = Budget(cfg)
        async with httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(200, text='OK'))) as client:
            async def resolve(host, port): return ['8.8.8.8']
            http = WebsiteHttp(client, cfg, budget, BlobStore(tmp_path / 'blobs'), resolver=resolve)
            # Thirty-four HTTP attempts already used; six remain after proof.
            for _ in range(34):
                event = budget.reserve('https://example.no/', 'example.no', ORG)
                event['section'] = 'website'
            http.counts[ORG] = 34
            # Actual robots and redirects use this same raw request accounting.
            for _ in range(6):
                await http.raw('https://example.no/news', ORG, {'example.no'})
            assert budget.by_company[ORG] == 40
            assert len(budget.events) == 40
            with pytest.raises(SourceFailure):
                await http.raw('https://example.no/jobs/2', ORG, {'example.no'})
    asyncio.run(run())


def test_hr_manager_board_remains_tenant_scoped():
    board = 'https://candidate.hr-manager.net/jobs/company/'
    scope = board_scope(board)
    assert scope and within_board(board + 'posting', scope)
    assert not within_board('https://candidate.hr-manager.net/jobs/other/posting', scope)
