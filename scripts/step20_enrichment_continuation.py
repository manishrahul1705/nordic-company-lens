"""Repair only optional source acquisition on a preserved measured base.

Never requests a company website, BRREG or NAV. The original files are untouched.
The original request ledger and wall deadline are reused, not reset.
"""
import asyncio
from collections import Counter
from datetime import datetime,timezone
import json
import os
from pathlib import Path
import subprocess
import time
import httpx

from signalpost.budget import Budget,SourceFailure
from signalpost.config import Config
from signalpost.models.envelope import Envelope
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.official_extra import collect
from signalpost.web.policy import safe_transport
from signalpost.runner import finalize
from signalpost.synthesis.service import Service
from signalpost.io.envelope_writer import write
from signalpost.profiles import write as profiles_write
from signalpost.site import generate_site
from scoreboard import build_scoreboard,read_jsonl


async def main():
    base=Path('bench/runs/20261107T073418068646Z-42def8c')
    out=base/'enrichment-continuation';out.mkdir(exist_ok=False)
    report=json.loads((base/'report.json').read_text(encoding='utf-8'))
    execution=json.loads((base/'execution.json').read_text(encoding='utf-8'))
    started=datetime.fromisoformat(execution['started_at'])
    cfg=Config(organisations=base/'inputs/batch.jsonl',output=out/'envelopes.jsonl',report=out/'report.json',
        state_dir=base/'state',profiles_output=out/'profiles.jsonl',site_dir=out/'site',max_requests=18000,time_budget_seconds=2400)
    class ContinuedBudget(Budget):
        def reserve(self,url,host,org):
            if org=='__official_extra__' and self.by_company[org]>=300:raise SourceFailure('extra_request_cap')
            return super().reserve(url,host,org)
    budget=ContinuedBudget(cfg)
    elapsed=(datetime.now(timezone.utc)-started).total_seconds()
    budget.start-=elapsed;budget.deadline-=elapsed
    budget.events=report['request_log'][:]
    budget.by_company=Counter(e['organisation_number'] for e in budget.events)
    budget.by_host=Counter(e['host'] for e in budget.events)
    budget.check()
    envelopes={}
    for line in (base/'envelopes.jsonl').open(encoding='utf-8'):
        row=Envelope.model_validate_json(line);envelopes[row.organisation_number]=row
    before=len(budget.events);phase=time.monotonic();blobs=BlobStore(base/'state')
    async with httpx.AsyncClient(trust_env=False,transport=safe_transport(8,{}),headers={'Accept':'application/json','User-Agent':'SignalpostAgent/1.0'}) as client:
        extra,metrics=await collect(envelopes,client,budget,blobs)
    source_seconds=time.monotonic()-phase
    assert all(e['host'] in {'api.gleif.org','api.ted.europa.eu','ted.europa.eu'} for e in budget.events[before:])
    service=Service()
    for org,row in envelopes.items():
        row.claims=[c for c in row.claims if not c.field.startswith(('identity.gleif.','procurement_award.'))]+extra[org].claims
        row.evidence=list({e.id:e for e in row.evidence+extra[org].evidence}.values())
        if any(c.family=='activity' for c in extra[org].claims):row.run.sections['activity']='available'
        finalize(row,None,blobs,budget,budget.start)
        row.run.synthesis=await service.summarize(row);row.profile.synthesis=row.run.synthesis
    result=list(envelopes.values())
    write(cfg.output,result,'union',blobs,512)
    profiles_write(cfg.profiles_output,result)
    site=generate_site(cfg.output,cfg.site_dir)
    report.update(request_log=budget.events,requests=len(budget.events),
        requests_by_host=dict(budget.by_host),official_extra=metrics,
        shared_requests=sum(e['organisation_number'] not in envelopes for e in budget.events),
        amortized_requests_per_company=len(budget.events)/1000,
        max_requests_per_company=max(budget.by_company[o] for o in envelopes),site={'state':'available',**site})
    report['official_extra_continuation']={'original_requests':before,'additional_requests':len(budget.events)-before,
        'source_seconds':source_seconds,'phase_wall_seconds':time.monotonic()-phase,
        'cumulative_elapsed_seconds':time.monotonic()-budget.start,'original_global_cap':budget.cap,
        'source_requests_cumulative':budget.by_company['__official_extra__'],'source_cap_cumulative':300,
        'original_files_untouched':True,'no_company_source_crawl':True,'reason':'TED XML Accept header406 repair'}
    cfg.report.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    (out/'execution.json').write_text(json.dumps({'commit':source,'base':str(base),'type':'bounded optional-source continuation; not a second company crawl',**report['official_extra_continuation']},indent=2),encoding='utf-8')
    score=build_scoreboard(read_jsonl(cfg.output),report,read_jsonl(cfg.profiles_output),execution={'commit':source,'exit_code':0,'wall_seconds':report['official_extra_continuation']['cumulative_elapsed_seconds']})
    (out/'scoreboard.json').write_text(json.dumps(score,indent=2),encoding='utf-8')
    print(json.dumps(report['official_extra_continuation']),flush=True)


if __name__=='__main__':
    for key in list(os.environ):
        if any(s in key.upper() for s in ('API_KEY','APIKEY','TOKEN','SECRET','CREDENTIAL')) or key.startswith(('SIGNALPOST_SEARCH','SIGNALPOST_LLM')):os.environ.pop(key)
    asyncio.run(main())
