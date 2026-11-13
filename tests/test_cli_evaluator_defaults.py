"""Mock evaluator exercises the real CLI, pipeline, writers and offline site."""
import json
from pathlib import Path
import httpx
import pytest
from signalpost.cli import main
from signalpost.runner import run as runner_run
from signalpost.budget import SourceFailure
from signalpost.web import policy
from signalpost.sources.nav import NavHttp
from tests.test_registry import handler

INPUT=Path(__file__).resolve().parents[1]/'bench/inputs/20/batch.jsonl'


@pytest.mark.parametrize('mode',['minimal','readme','invented','no_site'])
def test_evaluator_always_writes_all_artifacts(tmp_path,monkeypatch,capsys,mode):
    async def no_domain(*args):raise SourceFailure('no_such_domain')
    async def token(self):return 'synthetic-public-token'
    monkeypatch.setattr(policy,'resolve_public',no_domain)
    monkeypatch.setattr(NavHttp,'public_token',token)
    def respond(request):
        path=request.url.path
        if request.url.host=='data.brreg.no':
            if '/oppdateringer/' in path:
                key='oppdaterteUnderenheter' if path.endswith('underenheter') else 'oppdaterteEnheter'
                return httpx.Response(200,json={'_embedded':{key:[]},'page':{'number':0,'size':1000,'totalPages':0,'totalElements':0}})
            return handler(missing_accounts=False)(request)
        if request.url.host=='query.wikidata.org':return httpx.Response(200,json={'results':{'bindings':[]}})
        if request.url.host=='pam-stilling-feed.nav.no':
            return httpx.Response(200,json={'items':[],'next_url':None,'feed_url':'https://pam-stilling-feed.nav.no/api/v1/feed/11111111-1111-4111-8111-111111111111'})
        if request.url.host=='api.gleif.org':return httpx.Response(200,json={'data':[],'links':{}})
        return httpx.Response(200,json={'results':[],'totalResults':0})
    async def run(config):
        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            return await runner_run(config.model_copy(update={'website_politeness_seconds':0}),client)
    monkeypatch.setattr('signalpost.cli.run',run)
    monkeypatch.chdir(tmp_path)
    args=['run','--organisations',str(INPUT),'--output','out/envelopes.jsonl']
    if mode!='minimal':
        args+=['--profiles-output','out/profiles.jsonl','--report','out/report.json','--state-dir','out/state']
        if mode!='no_site':args+=['--site-dir','out/site']
    unknown=['--invented-flag','--invented-choice=example','--invented-count','3']
    if mode=='invented':args+=unknown
    assert main(args)==0
    for name in ('envelopes.jsonl','profiles.jsonl','report.json','site/index.html','site/compare.html'):
        path=tmp_path/'out'/name
        assert path.is_file() and path.stat().st_size>0,name
    assert len((tmp_path/'out/envelopes.jsonl').read_text(encoding='utf8').splitlines())==20
    assert len((tmp_path/'out/profiles.jsonl').read_text(encoding='utf8').splitlines())==20
    report=json.loads((tmp_path/'out/report.json').read_text(encoding='utf8'))
    effective=report['effective_configuration']
    for name in ('websites','hiring','public_activity','registry_changes','official_extra_sources','website_suffix_contact_proof'):
        assert effective[name] is True
    assert effective['synthesis']['effective_mode']=='template' and effective['synthesis']['llm_calls']==0
    assert effective['request_caps']['pooled']==380 and effective['request_caps']['per_company']==40
    assert effective['search']['queries']==effective['search']['estimated_usd']==0
    assert report['unrecognised_flags']==effective['unrecognised_flags']==(unknown if mode=='invented' else [])
    err=capsys.readouterr().err
    if mode=='invented':
        assert 'warning' in err and '--invented-flag' in err
        assert any('Unrecognised arguments' in w for w in report['warnings'])
    else:assert 'unrecognised arguments' not in err.lower()


def test_effective_configuration_records_disabled_modes(tmp_path):
    from types import SimpleNamespace
    from signalpost.config import Config
    from signalpost.io.report import effective_configuration
    cfg=Config(organisations=tmp_path/'input',output=tmp_path/'output',report=tmp_path/'report',
               websites=False,hiring=False,public_activity=False,registry_changes=False,official_extra_sources=False,
               website_suffix_contact_proof=False,synthesis='auto')
    actual=effective_configuration(cfg,SimpleNamespace(cap=180),{'search':{'queries':0,'estimated_usd':0},'llm':{'calls':0}})
    assert not any(actual[k] for k in ('websites','hiring','public_activity','registry_changes','official_extra_sources','website_suffix_contact_proof'))
    assert actual['nav']=={'index_built_at':None,'mode':'disabled'}
    assert actual['synthesis']=={'requested_mode':'auto','effective_mode':'template','llm_calls':0}
