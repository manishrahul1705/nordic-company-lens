"""Live second-pass-only replay, retaining original request usage and deadline reserve."""
import asyncio
import argparse
from collections import Counter,defaultdict
import hashlib
import json
import os
from pathlib import Path
import sys
import time
from types import SimpleNamespace

sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
import httpx
from signalpost.config import Config
from signalpost.budget import Budget
from signalpost.models.envelope import Envelope,CompactProfile
from signalpost.models.shapes import serialize
from signalpost.runner import isolate,update
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.http import Http
from signalpost.web.fetcher import WebsiteHttp
from signalpost.web import policy
from signalpost.web.second_pass import candidates,run
from signalpost.web.entity_scope import enforce
from signalpost.web.social import drop_shared
from signalpost.web.news_items import collect as news
from signalpost.synthesis.cohort import build_index,context
from signalpost.synthesis.template import generate
from scripts.verify_output import verify

BASE=Path('bench/runs/stage-am-live1000')
OUT=Path('bench/runs/website-second-pass-20261120')
HERE=Path(__file__).resolve().parent


def counts(rows):
    out={}
    for key,prefix in [('sites','official_website'),('brands','public_brand'),('social','social_profile.'),('news','news_item.')]:
        matched=[(r.organisation_number,c) for r in rows for c in r.claims if c.availability=='available'
            and (c.field.startswith(prefix) if prefix.endswith('.') else c.field==prefix)]
        out[key]={'companies':len({o for o,c in matched}),'claims':len(matched)}
    return out


async def main():
    global OUT
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=OUT)
    args=parser.parse_args();OUT=args.output
    started=time.perf_counter();OUT.mkdir(parents=True,exist_ok=False)
    rows=[Envelope.model_validate(json.loads(l)) for l in (BASE/'envelopes.jsonl').open(encoding='utf-8')]
    before=counts(rows); oldsites={r.organisation_number for r in rows if any(c.field=='official_website' and c.availability=='available' for c in r.claims)}
    # Production merges registry activity after second_pass. This saved-run
    # replay already contains it; retain those official claims across the
    # optional company-site activity section replacement.
    official_activity={r.organisation_number:[c for c in r.claims if c.family=='activity' and c.availability=='available'
        and c.evidence_ids and all(next(e for e in r.evidence if e.id==ref).source_class!='company_owned' for ref in c.evidence_ids)] for r in rows}
    eligible={r.organisation_number:r for r in rows if r.run.sections.get('website')=='not_available' and candidates(r)}
    # Production uses one shared DNSFallbackBudget context. The saved report
    # does not retain exact per-company fallback seconds; conservatively treat
    # the original selected companies' 10-second fallback allowance as spent.
    # Primary DNS is still attempted normally; this grants no extra fallback.
    dns_state=policy.DNSFallbackBudget()
    dns_state.elapsed_by_company.update({org:policy.DNS_FALLBACK_COMPANY_CAP_SECONDS for org in eligible})
    policy.DNS_FALLBACK_STATE.set(dns_state)
    nominations={o:[{'url':c.url,'domain':c.domain,'origin':c.origin} for c in candidates(r)] for o,r in eligible.items()}
    (HERE/'eligible.json').write_text(json.dumps(nominations,indent=2)+'\n',encoding='utf-8')
    saved=json.loads((BASE/'report.json').read_text(encoding='utf-8'))
    cfg=Config(organisations=Path('bench/inputs/1000-r3/batch.jsonl'),output=OUT/'envelopes.jsonl',
        report=OUT/'report.json',state_dir=OUT/'state',site_dir=OUT/'site',websites=True,public_activity=True)
    budget=Budget(cfg)
    # Conservative remaining crawl time: subtract the entire saved pipeline
    # duration, including finalisation, from the original 1,000/site-on window.
    budget.deadline-=saved['runtime_ms']/1000
    remaining_at_start=budget.deadline-time.monotonic()
    history=saved['request_log'];budget.events.extend(history)
    budget.by_company.update(e['organisation_number'] for e in history);budget.by_host.update(e['host'] for e in history)
    blobs=BlobStore(cfg.state_dir)
    for sha in {e.content_sha256 for r in rows for e in r.evidence}:os.link(BASE/'state/blobs'/sha,blobs.directory/sha)
    owners=defaultdict(set)
    for r in rows:
        for c in r.claims:
            if c.field=='identity.registered_website' and c.availability=='available':owners[policy.domain(str(c.value))].add(r.organisation_number)
    clock=time.perf_counter()
    async with httpx.AsyncClient(transport=policy.safe_transport(32),trust_env=False) as client:
        http=WebsiteHttp(client,cfg,budget,blobs);http.registry_http=Http(client,cfg,budget,blobs);http.domain_owners=owners
        http.counts.update(Counter(e['organisation_number'] for e in history if e.get('section')=='website'))
        metrics=await run(eligible,http,{}, {},None,isolate,update,defer_jobs=True)
        drop_shared(rows,blobs);enforce(rows,blobs,SimpleNamespace(domain_owners=owners))
        recovered=[r for r in rows if r.organisation_number not in oldsites and any(c.field=='official_website' and c.availability=='available' for c in r.claims)]
        # The normal bounded news collector uses only the recovered site's
        # advertised resource and the same remaining budget. Stop before deadline.
        async def get_news(r):
            remaining=budget.deadline-time.monotonic()-.25
            if remaining<=.25:return
            try:
                async with asyncio.timeout(min(45,remaining)):
                    await news(r,http,http.accepted_pages.get(r.organisation_number,[]))
            except TimeoutError:
                r.run.refresh.setdefault('news_items',{}).update(state='withheld',reason='optional_retry_window_closed')
        await asyncio.gather(*(get_news(r) for r in recovered))
        drop_shared(rows,blobs);enforce(rows,blobs,SimpleNamespace(domain_owners=owners))
    elapsed=time.perf_counter()-clock;events=budget.events[len(history):]
    restored=0
    for r in rows:
        fields={c.field for c in r.claims}
        retained=[c for c in official_activity[r.organisation_number] if c.field not in fields]
        r.claims.extend(retained);restored+=len(retained)
    assert not any('Access is denied' in e.get('exception_message','') for e in events),'Invalid network-denied experiment'
    assert not any(e.code=='deadline' for r in rows for e in r.errors),'Optional retry must not add deadline hits'
    cohort=build_index(rows);reviews=[]
    with cfg.output.open('w',encoding='utf-8') as f:
        for r in rows:
            r.run.synthesis=generate(r,context(r,cohort));r.profile=CompactProfile(organisation_number=r.organisation_number,
                values={c.field:c.value for c in r.claims},evidence_ids=[e.id for e in r.evidence],synthesis=r.run.synthesis)
            site=next((c for c in r.claims if c.field=='official_website' and c.availability=='available'),None)
            if site and r.organisation_number not in oldsites:
                refs={e.id:e for e in r.evidence}
                reviews.append({'orgnr':r.organisation_number,'company':next(c.value for c in r.claims if c.field=='identity.legal_name'),
                    'claim':site.model_dump(mode='json'),'evidence':[refs[x].model_dump(mode='json') for x in site.evidence_ids],
                    'checked_pages':[{'url':p.url,'sha256':response.sha,'title':p.title,
                        'owner_text':p.owner_text[:2500]} for response,p in http.accepted_pages.get(r.organisation_number,[])]})
            f.write(json.dumps(serialize(r,'union'),ensure_ascii=False,separators=(',',':'))+'\n')
    (OUT/'review-candidates.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (OUT/'extra-requests.json').write_text(json.dumps(events,indent=2)+'\n',encoding='utf-8')
    summary={'baseline':str(BASE),'eligible_not_available_companies':len(eligible),'candidate_count':sum(map(len,nominations.values())),
        'before':before,'after':counts(rows),'recovered_sites':[{'orgnr':r['orgnr'],'company':r['company'],'url':r['claim']['value']['final_url']} for r in reviews],
        'extra_HTTP':len(events),'isolated_live_and_final_guard_seconds':round(elapsed,3),'second_pass':metrics,
        'pooled_requests_including_saved':len(budget.events),'pooled_cap':budget.cap,
        'max_company_requests':max(budget.by_company[r.organisation_number] for r in rows),
        'remaining_crawl_seconds_at_start':round(remaining_at_start,3),'remaining_crawl_seconds_after_live':round(budget.deadline-time.monotonic(),3),
        'DNS_fallback_policy':'Shared production context; conservatively assume selected companies already spent their original 10-second public-DNS fallback allowance. Primary DNS remains enabled.',
        'deadline_hits':0,'strict_verifier':verify(cfg.output,cfg.state_dir,len(rows)),
        'prior_official_activity_claims_retained_for_pipeline_order':restored,
        'total_replay_seconds':round(time.perf_counter()-started,3)}
    (HERE/'measurement.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8');print(json.dumps(summary,indent=2))


if __name__=='__main__':asyncio.run(main())
