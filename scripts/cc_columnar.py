"""Query only needed CC columnar fields using ephemeral DuckDB/httpfs."""
import json,time,threading,os
from pathlib import Path
import duckdb
import gzip,urllib.request,hashlib
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'bench/reports/cc-proto';RAW=OUT/'raw'
from datetime import datetime,timezone
DEADLINE=float(os.environ.get('CC_COLUMNAR_DEADLINE',str(time.time()+1200)))

def main():
 OUT.mkdir(parents=True,exist_ok=True);RAW.mkdir(exist_ok=True)
 previous=OUT/'columnar-query.json'
 if previous.exists() and (RAW/'columnar-selected.jsonl').exists() and json.loads(previous.read_text(encoding='utf8')).get('status')=='complete':
  print('Using cached complete columnar selection; no request sent.',flush=True);return
 manifest=OUT/'columnar-files.json'
 if not manifest.exists():
  manifest_url='https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-43/cc-index-table.paths.gz'
  req=urllib.request.Request(manifest_url,headers={'User-Agent':'SignalpostAgent/1.0 (+https://github.com/manishrahul1705/nordic-company-lens)'})
  with urllib.request.urlopen(req,timeout=60) as response:body=response.read()
  (RAW/'columnar-paths.gz').write_bytes(body)
  paths=[p for p in gzip.decompress(body).decode().splitlines() if '/subset=warc/' in p]
  manifest.write_text(json.dumps({'source':manifest_url,'sha256':hashlib.sha256(body).hexdigest(),'paths':paths},indent=2)+'\n')
 began=time.monotonic();c=duckdb.connect();settings={};meta={'backend':'DuckDB httpfs','duckdb_version':duckdb.__version__,'concurrency':2,'query_deadline_utc':datetime.fromtimestamp(DEADLINE,timezone.utc).isoformat(),'started_utc':datetime.now(timezone.utc).isoformat(),'files_queried':[],'errors':[]}
 try:
  c.execute('SET threads=2');c.execute('INSTALL httpfs');c.execute('LOAD httpfs')
  for name,value in [('http_retries','2'),('http_retry_wait_ms','30000'),('http_retry_backoff','2'),('http_timeout','60'),('external_threads','2'),('disable_parquet_prefetching','true'),('prefetch_all_parquet_files','false')]:
   try:c.execute(f'SET {name}={value}');settings[name]=value
   except Exception as e:settings[name]='unsupported: '+str(e).splitlines()[0]
  meta['settings']=settings
  timer=threading.Timer(max(1,DEADLINE-time.time()),c.interrupt);timer.daemon=True;timer.start()
  paths=json.loads((OUT/'columnar-files.json').read_text())['paths'];selected=[];counts={}
  previous_path=OUT/'columnar-query.json'
  previous=json.loads(previous_path.read_text()) if previous_path.exists() else {}
  completed_empty={k for k,v in previous.get('rows_per_file',{}).items() if v==0}
  meta['previous_attempt_errors']=previous.get('errors',[])
  meta['files_queried']=list(previous.get('files_queried',[]))
  meta['rows_per_file']={k:0 for k in completed_empty}
  meta['skipped_previously_empty_files']=len(completed_empty)
  for path in paths:
   if path in completed_empty:continue
   if time.time()>DEADLINE:break
   url='https://data.commoncrawl.org/'+path;print('Querying',path,flush=True)
   # fetch_time is required to retain the capture timestamp; filter columns are projected only for predicates.
   sql="""SELECT url,url_host_registered_domain,warc_filename,warc_record_offset,warc_record_length,CAST(fetch_time AS VARCHAR) AS fetch_time
FROM read_parquet(?,hive_partitioning=false)
WHERE url_host_tld='no' AND fetch_status=200 AND content_mime_detected='text/html'
AND (url_path='/' OR regexp_matches(url_path,'kontakt|om|personvern|about|contact','i'))
QUALIFY row_number() OVER (PARTITION BY url_host_registered_domain ORDER BY url) <= 2
LIMIT 20000"""
   meta['sql']=sql;meta['files_queried'].append(path) if path not in meta['files_queried'] else None;(OUT/'columnar-query.json').write_text(json.dumps(meta,indent=2)+'\n')
   rows=c.execute(sql,[url]).fetchall();meta.setdefault('rows_per_file',{})[path]=len(rows)
   for row in rows:
    u,d,f,o,l,t=row
    if counts.get(d,0)>=2:continue
    counts[d]=counts.get(d,0)+1;selected.append({'url':u,'domain':d,'filename':f,'offset':str(o),'length':str(l),'timestamp':t.isoformat() if hasattr(t,'isoformat') else str(t),'status':'200','mime':'text/html'})
    if len(selected)>=20000:break
   print('Selected',len(selected),'from',len(meta['files_queried']),'files',flush=True)
   # A single nonempty file is a valid limited prototype sample; do not sweep all300 files unnecessarily.
   if selected:break
  with (RAW/'columnar-selected.jsonl').open('w',encoding='utf8') as f:
   for row in selected:f.write(json.dumps(row)+'\n')
  meta.update(status='complete',records_selected=len(selected),domains_selected=len(counts),wall_seconds=time.monotonic()-began,sample_scope='First nonempty WARC Parquet file only; not a representative or complete .no crawl sample.')
 except Exception as e:meta.update(status='failed',wall_seconds=time.monotonic()-began);meta['errors'].append(f'{type(e).__name__}: {e}');print(meta['errors'][-1],flush=True)
 finally:
  if 'timer' in locals():timer.cancel()
  c.close()
  (OUT/'columnar-query.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps({k:v for k,v in meta.items() if k not in {'files_queried','rows_per_file','sql'}},indent=2),flush=True)
if __name__=='__main__':main()
