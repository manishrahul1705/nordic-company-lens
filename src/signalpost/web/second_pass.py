"""One end-of-run retry of previously nominated transient-failure candidates."""
import asyncio
import json
import time
from .candidates import Candidate
from .policy import DNS_ORG,DNS_FALLBACK_STATE
from ..budget import SourceFailure

TRANSIENT={'website_timeout','website_connect_error','website_tls_error','dns_timeout','dns_servfail','dns_unavailable','website_http_5xx'}


def candidates(row):
    if row.run.sections.get('website') not in {'failed','blocked'}:return []
    diagnostics=[]
    for error in row.errors:
        if error.code=='website_candidates':
            try:diagnostics+=json.loads(error.message)
            except (ValueError,TypeError):pass
    domains={d.get('domain') for d in diagnostics if d.get('reason') in TRANSIENT or d.get('status')==429 or isinstance(d.get('status'),int) and d['status']>=500}
    selected=[]
    for item in row.run.refresh.get('recall_round2',{}).get('candidates',[]):
        if item['domain'] in domains and item['domain'] not in {c.domain for c in selected}:
            selected.append(Candidate('https://'+item['domain'],item['domain'],item['origin'],item.get('subunit_orgnr')))
        if len(selected)==3:break
    return selected


async def run(envelopes,http,bulk,prior,nav_index,isolate,update,*,defer_jobs=False):
    from . import collector
    from .activity import fetch as activity
    from .jobs import fetch as jobs
    from ..sources.extract import Section
    totals={'eligible':0,'attempted':0,'candidates':0,'candidates_fetched':0,'recovered':0,'requests':0,'seconds':0.,'companies':[]}
    began=time.monotonic();before=len(http.budget.events)
    config=http.config
    http.config=config.model_copy(update={'website_transient_retry':False})
    try:
        # Deliberately bounded concurrency; every retry starts after first-pass
        # company tasks finish and remains under the original budget object.
        semaphore=asyncio.Semaphore(8)
        async def retry(org,row,selected):
            async with semaphore:
                DNS_ORG.set(org);meta={'candidates':[c.domain for c in selected],'attempted':False,'recovered':False}
                row.run.refresh['website_second_pass']=meta;totals['companies'].append({'organisation_number':org,'details':meta})
                try:http.budget.check()
                except SourceFailure:meta['reason']='global_budget_or_deadline';return
                if http.budget.by_company[org]>=40:meta['reason']='company_budget_exhausted';return
                old=row.model_copy(deep=True);start=len(http.budget.events);clock=time.monotonic()
                for candidate in selected:
                    for host in (candidate.domain,'www.'+candidate.domain):http.dns_cache.pop(host,None)
                fallback=DNS_FALLBACK_STATE.get()
                if fallback:
                    hosts={h for c in selected for h in (c.domain,'www.'+c.domain)}
                    for key in list(fallback.positive_cache):
                        if key[0]==org and key[1] in hosts:fallback.positive_cache.pop(key,None)
                meta['attempted']=True;totals['attempted']+=1;totals['candidates']+=len(selected)
                offset=len(row.run.refresh.get('recall_round2',{}).get('candidates',[]))
                try:
                    async with asyncio.timeout(min(45,max(.001,http.budget.deadline-time.monotonic()))):
                        await isolate(row,'website',lambda:collector.fetch(org,row,bulk.get(org),http,prior.get(org),nav_index,retry_candidates=selected))
                        recovered=row.run.sections.get('website')=='available'
                        if recovered:
                            meta['recovered']=True;totals['recovered']+=1
                            if config.public_activity:
                                await isolate(row,'activity',lambda:activity(org,row,http,http.accepted_pages.get(org,[])))
                            if config.hiring and not defer_jobs:
                                extra=await jobs(row,http)
                                current=[c for c in row.claims if c.family=='hiring' and c.availability=='available']
                                if extra.claims:update(row,'hiring',Section(state='available',claims=current+extra.claims,evidence=extra.evidence,errors=extra.errors))
                except TimeoutError:meta['reason']='second_pass_timeout'
                except SourceFailure as exc:meta['reason']=exc.code
                finally:
                    entries=row.run.refresh.get('recall_round2',{}).get('candidates',[])[offset:]
                    meta['fetched']=sum(bool(c.get('fetched')) for c in entries);totals['candidates_fetched']+=meta['fetched']
                    meta['requests']=sum(e['organisation_number']==org for e in http.budget.events[start:]);meta['seconds']=round(time.monotonic()-clock,3)
                    # Failed retries must not discard old verified optional facts
                    # or disguise the original failure as a successful absence.
                    if not meta['recovered']:
                        row.claims=old.claims;row.evidence=old.evidence;row.errors=old.errors;row.run.sections=old.run.sections;row.modules=old.modules
        tasks=[]
        for org,row in envelopes.items():
            selected=candidates(row)
            if selected:totals['eligible']+=1;tasks.append(asyncio.create_task(retry(org,row,selected)))
        results=await asyncio.gather(*tasks,return_exceptions=True)
        totals['unexpected_failures']=sum(isinstance(r,Exception) for r in results)
    finally:
        http.config=config;totals['requests']=len(http.budget.events)-before;totals['seconds']=round(time.monotonic()-began,3)
    return totals
