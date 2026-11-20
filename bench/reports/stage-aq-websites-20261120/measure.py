"""Affected-candidate live replay using real saved registry evidence and all final guards."""
import argparse
import asyncio
from collections import Counter, defaultdict
import json
import os
from pathlib import Path
import sys
import time
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
import httpx
from signalpost.config import Config
from signalpost.budget import Budget
from signalpost.models.envelope import Envelope, CompactProfile
from signalpost.models.shapes import serialize
from signalpost.runner import update
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.http import Http
from signalpost.web import collector, policy
from signalpost.web.candidates import Candidate
from signalpost.web.fetcher import WebsiteHttp
from signalpost.web.social import drop_shared
from signalpost.web.entity_scope import enforce
from signalpost.web.news_items import collect as collect_news
from signalpost.synthesis.cohort import build_index, context
from signalpost.synthesis.template import generate
from scripts.verify_output import verify

HERE = Path(__file__).resolve().parent
BASE = Path('bench/runs/stage-am-live1000')


def counts(rows):
    result = {}
    for label, prefix in [('websites','official_website'), ('brands','public_brand'), ('social','social_profile.'), ('news','news_item.')]:
        found=[(r.organisation_number,c) for r in rows for c in r.claims if c.availability=='available'
               and (c.field==prefix if not prefix.endswith('.') else c.field.startswith(prefix))]
        result[label]={'companies':len({o for o,c in found}),'claims':len(found)}
    return result


def targets_for(row,scope='publisher'):
    if any(c.field=='official_website' and c.availability=='available' for c in row.claims): return []
    name=next((c.value for c in row.claims if c.field=='identity.legal_name'), '')
    attempts=[]
    for e in row.errors:
        if e.code=='website_candidates':
            try: attempts.extend(json.loads(e.message))
            except (ValueError,TypeError): pass
    targets={}
    for a in attempts:
        why=a.get('reason')
        if not (why=='different_legal_entity' and str(name).endswith('FORRETNING AS')) and not (scope=='redirect-trial' and why=='redirect_without_company_identity'):continue
        fetched=next((x for x in attempts if x.get('final_url') and policy.domain(x['final_url'])==a.get('domain')),None)
        url=fetched.get('url') if fetched else a.get('proof_page_url')
        if not url:continue
        candidate=Candidate(url,policy.domain(url),a.get('origin','legal_name_slug'))
        targets[candidate.domain]={'candidate':candidate,'saved_reason':why,'saved_target':a.get('domain')}
    return list(targets.values())


async def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--count',type=int,choices=[100,1000],required=True)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--scope',choices=['publisher','redirect-trial'],default='publisher')
    parser.add_argument('--summary',type=Path)
    args=parser.parse_args(); out=args.output or Path('bench/runs/stage-aq-'+str(args.count));out.mkdir(parents=True,exist_ok=False)
    begin=time.perf_counter()
    rows=[]
    for line in (BASE/'envelopes.jsonl').open(encoding='utf-8'):
        if len(rows)==args.count:break
        rows.append(Envelope.model_validate(json.loads(line)))
    before=counts(rows); original_sites={r.organisation_number for r in rows if any(c.field=='official_website' and c.availability=='available' for c in r.claims)}
    targets={r.organisation_number:targets_for(r,args.scope) for r in rows}; targets={o:t for o,t in targets.items() if t}
    inputs=out/'input.txt';inputs.write_text('\n'.join(r.organisation_number for r in rows),encoding='utf-8')
    cfg=Config(organisations=inputs,output=out/'envelopes.jsonl',report=out/'report.json',state_dir=out/'state',
        websites=True,public_activity=True,website_proof_discovery=True,website_unique_no=True)
    budget=Budget(cfg); blobs=BlobStore(cfg.state_dir)
    # Keep all old request usage: these are additional requests, never a reset cap.
    orgs={r.organisation_number for r in rows}
    saved_report=json.loads((BASE/'report.json').read_text(encoding='utf-8'))
    history=[e for e in saved_report['request_log'] if e['organisation_number'] in orgs or e['organisation_number'].startswith('__')]
    budget.events.extend(history);budget.by_company.update(e['organisation_number'] for e in history);budget.by_host.update(e['host'] for e in history)
    # Actual immutable registry/page bodies, not a synthetic {} stand-in.
    needed={e.content_sha256 for r in rows for e in r.evidence}
    for sha in needed:os.link(BASE/'state/blobs'/sha,blobs.directory/sha)
    diagnostics=[]; locks=defaultdict(asyncio.Lock); slots=asyncio.Semaphore(12)
    owners=defaultdict(set)
    for row in rows:
        for c in row.claims:
            if c.field=='identity.registered_website' and c.availability=='available':owners[policy.domain(str(c.value))].add(row.organisation_number)
    live_begin=time.perf_counter()
    async with httpx.AsyncClient(transport=policy.safe_transport(32),trust_env=False) as client:
        http=WebsiteHttp(client,cfg,budget,blobs);http.registry_http=Http(client,cfg,budget,blobs)
        http.domain_owners=owners
        http.counts.update(Counter(e['organisation_number'] for e in history if e.get('section')=='website'))
        async def one(row):
            org=row.organisation_number
            async with locks[org],slots:
                policy.DNS_ORG.set(org)
                attempted=[]
                for item in targets[org]:
                    section=await collector.fetch(org,row,None,http,retry_candidates=[item['candidate']])
                    update(row,'website',section)
                    attempted.append({'url':item['candidate'].url,'origin':item['candidate'].origin,'saved_reason':item['saved_reason'],
                        'section_state':section.state,'diagnostics':[e.message for e in section.errors]})
                    if any(c.field=='official_website' and c.availability=='available' for c in row.claims):break
                diagnostics.append({'orgnr':org,'attempted':attempted})
        await asyncio.gather(*(one(r) for r in rows if r.organisation_number in targets))
        # Keep every final publication boundary, across all companies in this replay.
        drop_shared(rows,blobs);enforce(rows,blobs,SimpleNamespace(domain_owners=owners))
        gained=[r for r in rows if r.organisation_number not in original_sites and any(c.field=='official_website' and c.availability=='available' for c in r.claims)]
        await asyncio.gather(*(collect_news(r,http,http.accepted_pages.get(r.organisation_number,[])) for r in gained))
        drop_shared(rows,blobs);enforce(rows,blobs,SimpleNamespace(domain_owners=owners))
    live_seconds=time.perf_counter()-live_begin
    new_events=budget.events[len(history):]
    permission=[e for e in new_events if 'Access is denied' in e.get('exception_message','') or 'access permissions' in e.get('exception_message','')]
    if permission:raise RuntimeError('Harness network access denied; invalidate measurement, never report website misses')
    after=counts(rows);cohort=build_index(rows)
    reviews=[]
    with cfg.output.open('w',encoding='utf-8') as f:
        for row in rows:
            row.run.synthesis=generate(row,context(row,cohort))
            row.profile=CompactProfile(organisation_number=row.organisation_number,values={c.field:c.value for c in row.claims},
                evidence_ids=[e.id for e in row.evidence],synthesis=row.run.synthesis)
            c=next((c for c in row.claims if c.field=='official_website' and c.availability=='available'),None)
            if c and row.organisation_number not in original_sites:
                reviews.append({'orgnr':row.organisation_number,'company':next(c.value for c in row.claims if c.field=='identity.legal_name'),
                    'claim':c.model_dump(mode='json'),'evidence':[e.model_dump(mode='json') for e in row.evidence if e.id in c.evidence_ids]})
            f.write(json.dumps(serialize(row,'union'),ensure_ascii=False,separators=(',',':'))+'\n')
    summary={'source':str(BASE),'mode':'saved run plus live affected-candidate fetches only; original requests retained against caps',
        'companies':args.count,'affected_companies':len(targets),'affected_candidates':sum(map(len,targets.values())),
        'before':before,'after':after,'new_verified_sites':len(reviews),'extra_HTTP':len(new_events),
        'new_HTTP_by_error':dict(Counter(e.get('error') or str(e.get('status')) for e in new_events)),
        'max_total_HTTP_per_company':max((budget.by_company[o] for o in orgs),default=0),'pooled_cap':budget.cap,
        'total_requests_including_original':len(budget.events),'isolated_live_addition_seconds':round(live_seconds,3),
        'wall_time_note':'Measured standalone addition stage; not a paired complete-live-run wall-time delta.',
        'strict_verifier':verify(cfg.output,cfg.state_dir,len(rows)), 'total_replay_seconds':round(time.perf_counter()-begin,3)}
    summary['scope']=args.scope
    (args.summary or HERE/('measurement'+str(args.count)+'.json')).write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
    (out/'new-sites.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'diagnostics.json').write_text(json.dumps(diagnostics,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (out/'extra-requests.json').write_text(json.dumps(new_events,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':asyncio.run(main())
