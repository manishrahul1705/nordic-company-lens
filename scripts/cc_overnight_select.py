"""Streaming selector worker for cc_overnight; ephemeral DuckDB only."""
import gzip,json,sys,time,threading,urllib.request,urllib.error
from pathlib import Path
import duckdb
crawl,path,output,deadline=sys.argv[1],sys.argv[2],Path(sys.argv[3]),float(sys.argv[4])
c=duckdb.connect();timer=None
try:
 c.execute('SET threads=2');c.execute('INSTALL httpfs');c.execute('LOAD httpfs')
 for key,val in [('external_threads','2'),('http_retries','2'),('http_retry_wait_ms','30000'),('http_retry_backoff','2'),('http_timeout','60'),('disable_parquet_prefetching','true'),('prefetch_all_parquet_files','false')]:c.execute(f'SET {key}={val}')
 timer=threading.Timer(max(.1,deadline-time.time()),c.interrupt);timer.daemon=True;timer.start()
 query="""SELECT url,url_host_registered_domain,warc_filename,warc_record_offset,warc_record_length,CAST(fetch_time AS VARCHAR)
 FROM read_parquet(?,hive_partitioning=false)
 WHERE url_host_tld='no' AND fetch_status=200 AND content_mime_detected='text/html'
 AND (url_path='/' OR regexp_matches(url_path,'kontakt|om|om-oss|personvern|about|contact','i'))
 QUALIFY row_number() OVER(PARTITION BY url_host_registered_domain ORDER BY url)<=2"""
 cur=c.execute(query,['https://data.commoncrawl.org/'+path]);count=0
 with output.with_suffix('.part').open('w',encoding='utf8') as f:
  while time.time()<deadline:
   rows=cur.fetchmany(2048)
   if not rows:break
   for u,d,name,offset,length,stamp in rows:
    f.write(json.dumps({'crawl':crawl,'url':u,'domain':d,'filename':name,'offset':str(offset),'length':str(length),'timestamp':stamp,'status':'200','mime':'text/html'},ensure_ascii=False)+'\n');count+=1
  else:raise TimeoutError('Selection cutoff')
 output.with_suffix('.part').replace(output);print('SELECTED',crawl,path,count,flush=True)
finally:
 if timer:timer.cancel()
 c.close()
