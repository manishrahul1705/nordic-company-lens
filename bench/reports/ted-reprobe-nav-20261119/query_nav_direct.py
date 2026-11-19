"""Read-only measurement of the user-specified legacy NAV endpoint."""
import asyncio,collections,hashlib,json,re,time
from datetime import datetime,timezone
from pathlib import Path
import httpx

out=Path('bench/reports/ted-reprobe-nav-20261119')
raw=Path('out/nav-direct-20261119');raw.mkdir(parents=True,exist_ok=True)
input_path=Path('bench/inputs/1000-r3/batch.jsonl')
orgs=[json.loads(line)['organisation_number'] for line in input_path.read_text().splitlines()]
assert len(orgs)==len(set(orgs))==1000
first=json.loads((out/'first-query.json').read_text());assert first['organisation_number']==orgs[0]
rows=[first];lock=asyncio.Lock();next_start=0.0
started=datetime.now(timezone.utc);began=time.perf_counter()
async def query(client,org):
    global next_start
    async with lock:
        await asyncio.sleep(max(0,next_start-time.monotonic()))
        next_start=time.monotonic()+.25
    url=f'https://arbeidsplassen.nav.no/public-feed/api/v1/ads?orgnr={org}&size=10'
    t=time.perf_counter();row={'organisation_number':org,'url':url}
    try:
        r=await client.get(url)
        row.update(status=r.status_code,content_type=r.headers.get('content-type'),location=r.headers.get('location'),
                   bytes=len(r.content),sha256=hashlib.sha256(r.content).hexdigest())
        if r.status_code==200 and 'json' in r.headers.get('content-type',''):
            data=r.json();(raw/(org+'.json')).write_text(json.dumps(data,ensure_ascii=False),encoding='utf8')
            ads=data if isinstance(data,list) else next((data[k] for k in ['content','ads','results'] if isinstance(data.get(k),list)),None)
            row['ads_count']=len(ads) if ads is not None else None
            row['response_keys']=list(data) if isinstance(data,dict) else None
            if ads is not None:
                row['ads']=[{k:ad.get(k) for k in ['uuid','id','status','expires','employer']} for ad in ads]
        elif r.status_code==429:
            # Respect a shared Retry-After pause, but do not retry or hide its cost.
            retry=r.headers.get('retry-after','60')
            try:delay=max(1,float(retry))
            except ValueError:delay=60
            async with lock:next_start=max(next_start,time.monotonic()+delay)
    except Exception as exc:row.update(status=None,error=type(exc).__name__,message=str(exc))
    row['elapsed_seconds']=round(time.perf_counter()-t,3)
    return row
async def main():
    queue=asyncio.Queue()
    for org in orgs[1:]:queue.put_nowait(org)
    async with httpx.AsyncClient(headers={'Accept':'application/json','User-Agent':'SignalpostAgent/1.0 (+https://github.com/manishrahul1705/nordic-company-lens)'},
        timeout=20,follow_redirects=False,trust_env=False,limits=httpx.Limits(max_connections=4)) as client:
        async def worker():
            while not queue.empty():
                org=queue.get_nowait();row=await query(client,org);rows.append(row)
                with (out/'queries.jsonl').open('a',encoding='utf8') as f:f.write(json.dumps(row)+'\n')
                if len(rows)%100==0:print('queried',len(rows),'statuses',dict(collections.Counter(str(r.get('status')) for r in rows)),flush=True)
        with (out/'queries.jsonl').open('x',encoding='utf8') as f:f.write(json.dumps(first)+'\n')
        await asyncio.gather(*(worker() for _ in range(4)))
    assert len(rows)==1000 and len({r['organisation_number'] for r in rows})==1000
    valid=[r for r in rows if r.get('status')==200 and r.get('ads_count') is not None]
    summary={'input_sha256':hashlib.sha256(input_path.read_bytes()).hexdigest(),'companies_queried':len(rows),
        'status_counts':dict(collections.Counter(str(r.get('status')) for r in rows)),
        'valid_ad_responses':len(valid),'companies_returning_ads':sum(r['ads_count']>0 for r in valid) if len(valid)==1000 else None,
        'observed_positive_ad_responses':sum(r['ads_count']>0 for r in valid),'companies_with_active_ads':None,
        'parent_subunit_behavior':'Not measurable without successful ads payloads and employer-ID analysis',
        'coverage_counts_interpretable':len(valid)==1000,
        'started_at':started.isoformat(),'finished_at':datetime.now(timezone.utc).isoformat(),
        'remaining_999_wall_seconds':round(time.perf_counter()-began,3),
        'first_query_seconds':first['elapsed_seconds'],'concurrency':4,'minimum_start_interval_seconds':.25,
        'retry_attempts':0,'endpoint_requests':1000,'note':'HTTP errors and unsupported payloads are unavailable measurements, never no-ad evidence. First request was preserved from the initial endpoint check.'}
    (out/'nav-measurement.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))
asyncio.run(main())
