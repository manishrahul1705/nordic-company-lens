"""Live bounded news discovery on saved verified homepages, preserving acquisition caps."""
import asyncio,json,os,time
from pathlib import Path
from collections import Counter
from urllib.parse import urlsplit,urlunsplit
from urllib.robotparser import RobotFileParser
import httpx
from signalpost.config import Config
from signalpost.budget import Budget
from signalpost.models.envelope import Envelope,CompactProfile
from signalpost.models.shapes import serialize
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.http import Response
from signalpost.web.fetcher import WebsiteHttp
from signalpost.web.html import Page
from signalpost.web.news_items import collect
from signalpost.web.policy import safe_transport
from signalpost.synthesis.cohort import build_index,context
from signalpost.synthesis.template import generate
base=Path('bench/runs/funding-snapshots-final-20261120');original=Path('bench/runs/overnight-all-20261120')
out=Path('bench/runs/news-items-20261120');reports=Path(__file__).parent
if out.exists():raise SystemExit('Refuse reused measurement state')
(out/'state/blobs').mkdir(parents=True)
for p in (base/'state/blobs').iterdir():
 if p.is_file():os.link(p,out/'state/blobs'/p.name)
blobs=BlobStore(out/'state');report=json.loads((base/'report.json').read_text());events=report['request_log']
rows=[Envelope.model_validate(json.loads(l)) for l in (base/'envelopes.jsonl').open(encoding='utf-8')]
cfg=Config(organisations=Path('bench/inputs/1000-r3/batch.jsonl'),output=out/'envelopes.jsonl',report=out/'report.json')
budget=Budget(cfg);budget.events=list(events);budget.by_company.update(e['organisation_number'] for e in events);budget.by_host.update(e['host'] for e in events)
start=time.perf_counter()
async def main():
 async with httpx.AsyncClient(transport=safe_transport(128,{}),trust_env=False) as client:
  http=WebsiteHttp(client,cfg,budget,blobs)
  for e in events:
   org=e['organisation_number']
   if e.get('section')=='website':http.counts[org]=http.counts.get(org,0)+1
   u=e['url'];sha=e.get('content_sha256')
   if urlsplit(u).path=='/robots.txt' and e.get('status') in [200,404,410] and sha:
    raw=blobs.read(sha)
    if raw is not None:
     parser=RobotFileParser(u);parser.parse(raw.decode('utf-8',errors='replace').splitlines() if e['status']==200 else [])
     parts=urlsplit(u);http.robots[urlunsplit((parts.scheme,parts.netloc,'','',''))]=parser
  sem=asyncio.Semaphore(8)
  async def company(row):
   if not any(c.field=='official_website' and c.availability=='available' and c.value.get('identity_level')=='VERIFIED' for c in row.claims):return
   checked=set(row.run.refresh.get('website',{}).get('checked_urls',[]));pages=[];seen=set()
   for e in events:
    if e['organisation_number']!=row.organisation_number or e.get('status')!=200 or e['url'] not in checked or not e.get('content_sha256') or e['url'] in seen:continue
    raw=blobs.read(e['content_sha256'])
    if raw is None:continue
    seen.add(e['url']);r=Response(raw,200,e['url'],row.run.completed_at,e['content_sha256']);pages.append((r,Page(raw,e['url'])))
   async with sem:await collect(row,http,pages)
  await asyncio.gather(*(company(r) for r in rows))
asyncio.run(main());cohort=build_index(rows);published=[];diagnostics=[]
with cfg.output.open('w',encoding='utf-8') as f:
 for row in rows:
  news=[c for c in row.claims if c.field.startswith('news_item.')];published.extend({'orgnr':row.organisation_number,'company':next(c.value for c in row.claims if c.field=='identity.legal_name'),'claim':c.model_dump(mode='json'),'evidence':[e.model_dump(mode='json') for e in row.evidence if e.id in c.evidence_ids]} for c in news)
  if 'news_items' in row.run.refresh:diagnostics.append({'orgnr':row.organisation_number,'company':next(c.value for c in row.claims if c.field=='identity.legal_name'),**row.run.refresh['news_items']})
  row.run.synthesis=generate(row,context(row,cohort));row.profile=CompactProfile(organisation_number=row.organisation_number,values={c.field:c.value for c in row.claims},evidence_ids=[e.id for e in row.evidence]);row.profile.synthesis=row.run.synthesis
  f.write(json.dumps(serialize(row,'union'),ensure_ascii=False,separators=(',',':'))+'\n')
new_events=budget.events[len(events):];summary={'baseline':str(base),'verified_sites':len(diagnostics),'news_companies':len({x['orgnr'] for x in published}),'news_claims':len(published),'additional_http_requests':len(new_events),'states':dict(Counter(d['state'] for d in diagnostics)),'reasons':dict(Counter(d.get('reason') for d in diagnostics if d.get('reason'))),'max_total_company_requests':max(budget.by_company.values()),'pooled_requests':len(budget.events),'measurement_seconds':round(time.perf_counter()-start,3),'scope':'Saved verified homepages and cached robots; live fetch at most one advertised resource; original per-company and pooled usage preserved; not a full live rerun'}
(reports/'measurement.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');(reports/'claims.json').write_text(json.dumps(published,ensure_ascii=False,indent=1),encoding='utf-8');(reports/'diagnostics.json').write_text(json.dumps(diagnostics,ensure_ascii=False,indent=1),encoding='utf-8');(reports/'requests.json').write_text(json.dumps(new_events,ensure_ascii=False,indent=1),encoding='utf-8');report['replay']={'kind':'bounded verified-site news','new_http_requests':len(new_events)};(out/'report.json').write_text(json.dumps(report),encoding='utf-8');print(json.dumps(summary,indent=2))
