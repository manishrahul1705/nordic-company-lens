"""Bounded Common Crawl measurement, never imported by the production agent."""
import concurrent.futures,csv,gzip,hashlib,io,json,random,re,socket,sys,threading,time
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from urllib.parse import urlsplit
import httpx
from osm_check import ROOT,textfile,org,dump
from osm_measure import Live,UA,CONFIG,unit_context
from signalpost.identity.orgnr import valid
from signalpost.web.html import Page
from signalpost.web.policy import domain,normalize_url,DIRECTORIES,SOCIAL,is_directory_record
from signalpost.web.candidates import Candidate
from signalpost.web.collector import candidate_proof,proof_page_targets
OUT=ROOT/'bench/reports/cc-proto';RAW=OUT/'raw';OSM=ROOT/'bench/reports/osm-check'
# Wall-clock deadline is opt-in for bounded measurement runs; normal prototype has no implicit agent effect.
DEADLINE=float(__import__('os').environ.get('CC_MEASUREMENT_DEADLINE','inf'))
LIVE_DEADLINE=float(__import__('os').environ.get('CC_LIVE_DEADLINE',str(DEADLINE+180)))
TERMS='Common Crawl access is subject to its Terms of Use and third-party content rights; do not overload the service; this prototype uses at most two concurrent requests and bounded backoff for 429/503. https://commoncrawl.org/terms-of-use'
PATH=re.compile(r'kontakt|kontakt-oss|om|om-oss|personvern|about|contact',re.I)
LABEL=re.compile(r'(?i)(?:\borg\s*\.?\s*nr\s*\.?|\borganisasjonsnummer|\bforetaksregisteret)\s*[:#.-]?\s*(?:NO\s*)?((?:[0-9][ .\u00a0]*){8}[0-9])(?![0-9])|\bNO\s*((?:[0-9][ .\u00a0]*){8}[0-9])\s*MVA\b')
COUNTERS=Counter();LOCK=threading.Lock();LAST=[0.0];EVENTS=[]

def request(client,url,**kwargs):
 for attempt in range(3):
  if time.time()>=DEADLINE:raise TimeoutError('Measurement deadline reached')
  with LOCK:
   time.sleep(max(0,.2-(time.monotonic()-LAST[0])));LAST[0]=time.monotonic()
  began=time.monotonic()
  try:
   if 'headers' in kwargs and 'Range' in kwargs['headers']:
    with client.stream('GET',url,timeout=min(90,max(.01,DEADLINE-time.time())),**kwargs) as stream:
     if stream.status_code==200:raise ValueError('Server ignored WARC Range; body not read')
     chunks=[]
     expected=kwargs['headers']['Range'].removeprefix('bytes=')
     limit=int(expected.split('-')[1])-int(expected.split('-')[0])+1
     if stream.status_code==206 and not stream.headers.get('Content-Range','').startswith('bytes '+expected+'/'):raise ValueError('Unexpected range header; body not read')
     size=0
     for chunk in stream.iter_bytes():
      if time.time()>=DEADLINE:raise TimeoutError('WARC measurement cutoff reached')
      size+=len(chunk)
      if size>max(limit,65536):raise ValueError('Oversize range response refused')
      chunks.append(chunk)
     content=b''.join(chunks)
     r=httpx.Response(stream.status_code,headers=stream.headers,content=content,request=stream.request)
   else:
    r=client.get(url,timeout=180,**kwargs)
   with LOCK:COUNTERS['http_requests']+=1;COUNTERS['http_bytes']+=len(r.content)
   if r.status_code in {429,503,502,504}:
    wait=max(30*(2**attempt),int(r.headers.get('Retry-After','0')) if r.headers.get('Retry-After','').isdigit() else 0)
    EVENTS.append({'url':str(r.url),'status':r.status_code,'backoff_seconds':wait});dump(OUT/'events.json',EVENTS)
    if attempt<2:
     if time.time()+wait>=DEADLINE:raise TimeoutError('No remaining time for requested backoff')
     time.sleep(wait);continue
   r.raise_for_status();return r
  except httpx.TransportError as e:
   EVENTS.append({'url':url,'error':type(e).__name__,'message':str(e)});dump(OUT/'events.json',EVENTS)
   if attempt==2:raise
   time.sleep(30*(attempt+1))
 raise RuntimeError('request retries exhausted')

def eligible(row):
 p=urlsplit(row['url']);root=domain(row['url'])
 return (p.hostname or '').endswith('.no') and row.get('status')=='200' and row.get('mime')=='text/html' and (p.path in {'','/'} or bool(PATH.search(p.path))) and root not in DIRECTORIES|SOCIAL and not is_directory_record(row['url'])

def numbers(text):
 found={}
 for m in LABEL.finditer(text):
  n=re.sub(r'[^0-9]','',m[1] or m[2])
  if valid(n):found[n]=text[max(0,m.start()-30):max(0,m.start()-30)+120]
 return found

def http_body(member):
 raw=gzip.decompress(member)
 _,sep,response=raw.partition(b'\r\n\r\n')
 if not sep:raise ValueError('No WARC headers')
 headers,sep,body=response.partition(b'\r\n\r\n')
 if not sep or not headers.startswith(b'HTTP/'):raise ValueError('No archived HTTP response')
 if not re.match(rb'HTTP/\S+ 200\b',headers):raise ValueError('Archived response is not HTTP200')
 # Common Crawl may retain transfer/content headers after normalizing payloads.
 # Dechunk only a body that actually starts with an HTTP chunk-size line.
 if b'transfer-encoding: chunked' in headers.lower() and re.match(rb'^[0-9a-fA-F]+(?:;[^\r\n]*)?\r\n',body):
  remaining=body;chunks=[]
  while remaining:
   line,_,remaining=remaining.partition(b'\r\n');size=int(line.split(b';')[0],16)
   if size==0:break
   chunks.append(remaining[:size]);remaining=remaining[size+2:]
  body=b''.join(chunks)
 if b'content-encoding: gzip' in headers.lower() and body.startswith(b'\x1f\x8b'):body=gzip.decompress(body)
 return body

def index_records(client,crawl):
 path=RAW/'selected-cdx.jsonl';metadata_path=OUT/'index-sample.json'
 if path.exists() and metadata_path.exists() and json.loads(metadata_path.read_text(encoding='utf8'))['complete']:
  return [json.loads(x) for x in path.read_text(encoding='utf8').splitlines()],json.loads(metadata_path.read_text(encoding='utf8'))
 params=[('url','*.no/*'),('output','json'),('filter','status:200'),('filter','mime:text/html'),('filter',r'url:^https?://[^/]+/(?:\?.*)?$|^https?://[^/]+/[^?#]*(?:kontakt|kontakt-oss|om|om-oss|personvern|about|contact)[^?#]*(?:\?[^#]*)?$'),('pageSize','1')]
 probe=OUT/'index-probe.json'
 if probe.exists():count=json.loads(json.loads(probe.read_text(encoding='utf8'))['body'])
 else:count=request(client,crawl['cdx-api'],params=params+[('showNumPages','true')]).json()
 count={**count,'pages':count['blocks'],'pageSize':1}
 pages=list(range(count['pages']));random.Random(20261111).shuffle(pages)
 selected=[];per_domain=Counter();seen=set();meta={'count_response':count,'seed':20261111,'page_order':'fixed-seed shuffled CDX pages; each page is one index block','pages_visited':[],'rows_after_server_filters':0,'selected_records':0,'complete':False,'limit':20000,'per_registrable_domain_cap':2,'query_params':params}
 with path.open('w',encoding='utf8') as f:
  for page in pages:
   r=request(client,crawl['cdx-api'],params=params+[('page',str(page))]);rows=[json.loads(x) for x in r.text.splitlines() if x.strip()]
   meta['rows_after_server_filters']+=len(rows);meta['pages_visited'].append(page)
   for row in rows:
    if not eligible(row):continue
    root=domain(row['url']);key=(row['filename'],row['offset'])
    if per_domain[root]>=2 or key in seen:continue
    selected.append(row);per_domain[root]+=1;seen.add(key);f.write(json.dumps(row)+'\n')
    if len(selected)>=20000:break
   meta['selected_records']=len(selected);dump(metadata_path,meta);print('Index page',page,'selected',len(selected),flush=True)
   if len(selected)>=20000:break
   time.sleep(1)
 meta['complete']=True;dump(metadata_path,meta)
 return selected,meta

def unavailable(crawl,error,elapsed):
 summary={'status':'index_unavailable','crawl':crawl,'terms':TERMS,
 'future_in_agent_use':'Any in-agent use would need a bundled index; licensing and third-party content rights are a grey area to decide.',
 'error':str(error),'records_selected':0,'records_fetched':0,'warc_range_MB_downloaded':0,
 'pages_with_orgnr':None,'pairs':None,'distinct_orgnrs':None,'distinct_domains':None,
 'distinct_parent_companies':None,'universe':{'size':411160,'matches':None,'expected_per_1000':None},
 'extrapolation':{'estimate':None,'method':'No eligible CDX records retrieved. Count response measures index blocks, not eligible pages or domains; no coverage extrapolation is possible.'},
 'osm_overlap':None,'bench100_matches':None,'bench100_match_count':None,
 'live_review':{'sample_size':0,'passed':None,'reason':'No CC candidate pairs available; live check not performed.'},
 'wall_seconds':elapsed,'wall_seconds_scope':'Last bounded one-block index attempt including backoff; excludes earlier discovery/five-block probe.',
 'limitations':['No CDX records or WARC ranges were retrieved; zero fetched records is not zero coverage.',
                 'Prototype extraction, joins and live-check pipeline not validated against real WARC data in this run.',
                 'No raw WARC bytes stored; empty candidates file denotes unavailable measurement.']}
 dump(OUT/'summary.json',summary);(OUT/'candidates.jsonl').touch()

def main():
 OUT.mkdir(parents=True,exist_ok=True);RAW.mkdir(exist_ok=True);start=time.monotonic()
 prior=OUT/'summary.json'
 if prior.exists() and json.loads(prior.read_text(encoding='utf8')).get('status')=='index_unavailable' and '--retry-index' not in sys.argv and '--columnar' not in sys.argv:
  raise RuntimeError('Previous bounded index attempts failed; inspect summary before explicitly using --retry-index. No request sent.')
 with httpx.Client(headers={'User-Agent':UA},verify=True,trust_env=False,follow_redirects=False) as client:
  crawl_path=OUT/'crawl.json'
  if crawl_path.exists():crawl=json.loads(crawl_path.read_text(encoding='utf8'))
  else:
   catalog=request(client,'https://index.commoncrawl.org/collinfo.json').json();crawl=max((x for x in catalog if x['id'].startswith('CC-MAIN-')),key=lambda x:x['id']);dump(crawl_path,crawl)
  try:
   if '--columnar' in sys.argv:
    columnar=json.loads((OUT/'columnar-query.json').read_text(encoding='utf8'));records=[row for x in (RAW/'columnar-selected.jsonl').read_text(encoding='utf8').splitlines() if x.strip() for row in [json.loads(x)] if eligible(row)]
    if not records:raise ValueError('No columnar records selected')
    random.Random(20261111).shuffle(records)
    indexmeta={'count_response':{'blocks':300},'pages_visited':columnar['files_queried'],'source':'columnar'}
   else:records,indexmeta=index_records(client,crawl)
  except Exception as e:
   unavailable(crawl,f'{type(e).__name__}: {e}',time.monotonic()-start);raise
  cached=RAW/'warc-results.jsonl';results={}
  if cached.exists():results={x['key']:x for line in cached.read_text(encoding='utf8').splitlines() if line.strip() for x in [json.loads(line)]}
  def fetch(row):
   key=row['filename']+':'+row['offset'];item={'key':key,'url':row['url'],'domain':domain(row['url']),'timestamp':row['timestamp'],'numbers':{}}
   if key in results:
    if results[key].get('compressed_bytes'):results[key]['fetched']=True
    return results[key]
   try:
    offset,length=int(row['offset']),int(row['length'])
    if length>8_000_000:raise ValueError('WARC member exceeds8MB measurement cap')
    r=request(client,'https://data.commoncrawl.org/'+row['filename'],headers={'Range':f'bytes={offset}-{offset+length-1}'})
    if r.status_code!=206 or not r.headers.get('Content-Range','').startswith(f'bytes {offset}-{offset+length-1}/') or len(r.content)!=length:raise ValueError('Exact WARC range not honored')
    item['compressed_bytes']=length;item['fetched']=True;page=Page(http_body(r.content),row['url']);item['numbers']=numbers(' '.join(page.visible.split()));item['fetched']=True
   except Exception as e:item['error']=f'{type(e).__name__}: {e}'
   return item
  # Bounded queue: only two WARC byte ranges in flight; consume/append incrementally.
  with cached.open('a',encoding='utf8') as output,concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
   pending={};iterator=iter(records)
   for _ in range(2):
    row=next(iterator,None)
    if row:pending[pool.submit(fetch,row)]=row
   complete=0
   while pending:
    done,_=concurrent.futures.wait(pending,return_when=concurrent.futures.FIRST_COMPLETED)
    for future in done:
     row=pending.pop(future);item=future.result();complete+=1
     if item['key'] not in results:output.write(json.dumps(item,ensure_ascii=False)+'\n');output.flush();results[item['key']]=item
     if complete%100==0:print('WARC records',complete,'/',len(records),flush=True)
     nextrow=next(iterator,None) if time.time()<DEADLINE else None
     if nextrow:pending[pool.submit(fetch,nextrow)]=nextrow
  dump(OUT/'network.json',dict(COUNTERS))
 items=[results[row['filename']+':'+row['offset']] for row in records if row['filename']+':'+row['offset'] in results];domain_numbers={}
 for row in items:domain_numbers.setdefault(row['domain'],set()).update(row['numbers'])
 excluded={d for d,ns in domain_numbers.items() if len(ns)>=3}
 wanted={n for row in items if row['domain'] not in excluded for n in row['numbers']};parents={};units={}
 csv.field_size_limit(10_000_000)
 with textfile(OSM/'raw/subunits.csv.download') as f:
  sample=f.read(32768);f.seek(0);reader=csv.DictReader(f,dialect=csv.Sniffer().sniff(sample,delimiters=';,\t'))
  for row in reader:
   if row['organisasjonsnummer'] in wanted:
    parent=row['overordnetEnhet'];assert valid(parent);parents[row['organisasjonsnummer']]=parent;units[row['organisasjonsnummer']]=unit_context(row)
 pairs=[]
 for row in items:
  if row['domain'] in excluded:continue
  for n,snippet in row['numbers'].items():pairs.append({'orgnr':n,'parent_orgnr':parents.get(n,n),'is_subunit':n in parents,'domain':row['domain'],'url':row['url'],'crawl_id':crawl['id'],'timestamp':row['timestamp'],'snippet':snippet[:120]})
 with (OUT/'candidates.jsonl').open('w',encoding='utf8') as f:
  for row in pairs:f.write(json.dumps(row,ensure_ascii=False)+'\n')
 with textfile(OSM/'raw/universe.jsonl.gz') as f:universe={org(row):row for line in f if line.strip() for row in [json.loads(line)]}
 parent_set={p['parent_orgnr'] for p in pairs};matched=sorted(parent_set&universe.keys())
 osmpairs=[json.loads(x) for x in (OSM/'candidates.jsonl').read_text(encoding='utf8').splitlines()];osmparents={p['parent_orgnr'] for p in osmpairs}
 batch={org(json.loads(x)) for x in (ROOT/'bench/inputs/100/batch.jsonl').read_text(encoding='utf8').splitlines() if x.strip()}
 sample_blocks=min(indexmeta['count_response']['blocks'],len(indexmeta['pages_visited']));fraction=sample_blocks/indexmeta['count_response']['blocks']
 summary={'status':'live_review_running','crawl':crawl,'terms':TERMS,'future_in_agent_use':'Any in-agent use would need a bundled index; licensing/third-party content rights are a grey area to decide, not authorized by this measurement.','records_selected':len(records),'records_fetched':sum(bool(x.get('fetched')) for x in items),'warc_range_MB_downloaded':sum(x.get('compressed_bytes',0) for x in items)/1e6,'pages_with_orgnr_before_domain_exclusion':sum(bool(x['numbers']) for x in items),'pages_with_orgnr':sum(bool(x['numbers']) and x['domain'] not in excluded for x in items),'excluded_multi_org_domains':sorted(excluded),'pairs':len(pairs),'distinct_orgnrs':len({p['orgnr'] for p in pairs}),'distinct_domains':len({p['domain'] for p in pairs}),'distinct_orgnr_domain_pairs':len({(p['orgnr'],p['domain']) for p in pairs}),'distinct_parent_companies':len(parent_set),'subunit_numbers_mapped':len(parents),'universe':{'size':len(universe),'matches':len(matched),'expected_per_1000':1000*len(matched)/len(universe)},'osm_overlap':{'parent_companies':len(parent_set&osmparents),'new_universe_matches':len(set(matched)-osmparents)},'bench100_matches':sorted(parent_set&batch),'bench100_match_count':len(parent_set&batch),'extrapolation':{'sampled_index_block_fraction':fraction,'naive_full_crawl_universe_matches':min(len(universe),len(matched)/fraction) if fraction else None,'naive_expected_per_1000':min(1000,1000*len(matched)/fraction/len(universe)) if fraction else None,'method':'Scale observed matched parents by total .no CDX blocks / visited blocks (1 per page), cap at universe size. Illustrative only: CDX blocks include noneligible records; two-per-domain cap, final-page truncation and duplicate domains bias this. Not a statistical coverage estimate, no confidence interval; full .no eligible-domain denominator not measured.'},'errors':dict(Counter(x['error'].split(':')[0] for x in items if x.get('error'))),'mapping_limit':'Unmapped numbers are putative parents; no main-entity status inferred.'}
 if '--columnar' in sys.argv:
  summary['index_source']='DuckDB/httpfs columnar Parquet'
  summary['columnar_query']=columnar
  summary['extrapolation']['method']='Illustrative scenario: observed matched parents times300 WARC Parquet files / files queried, capped at universe size. One-file sample may be strongly biased, duplicate parents recur and .no eligible-domain denominator is unknown; not a statistical estimate.'
  summary['extrapolation']['sampled_parquet_file_fraction']=fraction
  summary['extrapolation'].pop('sampled_index_block_fraction',None)
 summary['measurement_incomplete_due_to_deadline']=len(items)<len(records)
 dump(OUT/'summary.json',summary);print('Summary',json.dumps(summary),flush=True)
 selected=random.Random(20261111).sample(matched,min(20,len(matched)));reviewpath=OUT/'live-review.json';reviews=json.loads(reviewpath.read_text(encoding='utf8')) if reviewpath.exists() else [];previous={x['orgnr'] for x in reviews};live=Live()
 def live_deadline(req):
  remaining=LIVE_DEADLINE-time.time()
  if remaining<=0:raise TimeoutError('Live measurement deadline reached')
  req.extensions['timeout']={k:min(30,max(.1,remaining)) for k in ('connect','read','write','pool')}
 live.client.event_hooks['request']=[live_deadline]
 for n in selected:
  if time.time()>LIVE_DEADLINE:break
  if n in previous:continue
  c=next(p for p in pairs if p['parent_orgnr']==n);urlparts=urlsplit(c['url']);url=urlparts.scheme+'://'+urlparts.netloc+'/'
  companyunits=[u for k,u in units.items() if parents[k]==n];context={'name':universe[n]['name'],'subunits':companyunits,'allowed_orgnrs':{n,*[u['orgnr'] for u in companyunits]}}
  item={'orgnr':n,'name':context['name'],'candidate':c,'context':{**context,'allowed_orgnrs':sorted(context['allowed_orgnrs'])},'pages':[],'passes':False};proofs=[];targets=[url]
  for index in range(3):
   if time.time()>LIVE_DEADLINE:
    item['deadline_incomplete']=True;break
   if index>=len(targets):break
   entry={'requested_url':targets[index]};item['pages'].append(entry)
   try:
    status,final,body=live.get(targets[index],c['domain']);entry.update(status=status,url=final)
    if status!=200:raise ValueError('HTTP '+str(status))
    h=hashlib.sha256(body).hexdigest();(RAW/(h+'.html')).write_bytes(body);page=Page(body,final);proof=candidate_proof(page,n,context,Candidate(url,c['domain'],'common_crawl',c['orgnr'] if c['is_subunit'] else None),[],CONFIG);proofs.append(proof)
    entry.update(body_sha256=h,title=page.title,proof=asdict(proof),proof_excerpt=page.proof_span(proof.subject_orgnr or n) or page.name_span(proof.token) or page.span_for(proof.token))
    if index==0:targets.extend(x for x in proof_page_targets(page,final,limit=2) if x not in targets)
   except Exception as e:entry['error']=f'{type(e).__name__}: {e}'
  conflict=any(p.level=='REJECT' and (p.other_orgnrs or p.reason in {'foreign_orgnr','different_legal_entity'}) for p in proofs);item['owner_conflict']=conflict;item['passes']=any(p.level=='VERIFIED' for p in proofs) and not conflict
  reviews.append(item);dump(reviewpath,reviews);dump(OUT/'live-requests.json',live.requests);print('Live review',len(reviews),n,item['passes'],flush=True)
 live.client.close();summary['live_deadline_incomplete_count']=sum(bool(x.get('deadline_incomplete')) for x in reviews);summary.update(status='partial_deadline' if len(items)<len(records) or len(reviews)<len(selected) else 'complete',wall_seconds=time.monotonic()-start,live_review={'seed':20261111,'sample_size':len(reviews),'passed':sum(x['passes'] for x in reviews),'method':'Homepage plus <=2 same-site proof pages; existing candidate_proof and Config unchanged; CC origin is nomination only. Normal UA, robots, >=1s per host, TLS verification, no downgrade; parent legal names plus cached registered subunit contacts, missing parent contacts not inferred. Errors count as non-passes.'});dump(OUT/'summary.json',summary)
if __name__=='__main__':main()
