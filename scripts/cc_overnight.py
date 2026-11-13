"""Unattended, resume-safe CC measurement. No live checks or production changes."""
import concurrent.futures,csv,gzip,json,os,re,sqlite3,subprocess,sys,threading,time,traceback
from datetime import datetime,timezone
from pathlib import Path
import httpx
from cc_proto import ROOT,OUT,RAW,OSM,UA,http_body,numbers,eligible,Page,textfile,org,domain
DEADLINE=datetime(2026,11,13,4,30,tzinfo=timezone.utc).timestamp()
STOP=threading.Event();PAUSE=[0.0];RATE=threading.Lock();CHILD=[None]
DB=RAW/'overnight.sqlite3';RESULTS=RAW/'warc-results.jsonl';STATE=RAW/'overnight-state.json'
def stamp():return datetime.now(timezone.utc).isoformat()
def log(*v):print(stamp(),*v,flush=True)
def connect():
 c=sqlite3.connect(DB,timeout=60);c.execute('PRAGMA busy_timeout=60000');return c
def check():
 if STOP.is_set() or time.time()>=DEADLINE:raise TimeoutError('10:00 IST cutoff')
def wait(seconds):
 if STOP.wait(max(0,min(seconds,DEADLINE-time.time()))):raise TimeoutError('Stopped')
 check()
def request(client,url,headers=None):
 for attempt in range(3):
  check()
  with RATE:pause=PAUSE[0]-time.monotonic()
  if pause>0:wait(pause)
  check()
  try:
   with client.stream('GET',url,headers=headers,timeout=min(60,max(.05,DEADLINE-time.time()))) as r:
    if r.status_code in {429,503,502,504}:
     delay=max(30*(2**attempt),int(r.headers.get('Retry-After','0')) if r.headers.get('Retry-After','').isdigit() else 0)
     with RATE:PAUSE[0]=max(PAUSE[0],time.monotonic()+delay)
     log('BACKOFF',r.status_code,delay,url)
     wait(delay)
     if attempt==2:r.raise_for_status()
     continue
    r.raise_for_status()
    if headers and 'Range'in headers:
     expected=headers['Range'].removeprefix('bytes=')
     if r.status_code!=206 or not r.headers.get('Content-Range','').startswith('bytes '+expected+'/'):raise ValueError('Exact range not honored; body not read')
     limit=int(expected.split('-')[1])-int(expected.split('-')[0])+1
    else:limit=None
    data=[];size=0
    for chunk in r.iter_bytes():
     check();size+=len(chunk)
     if limit is not None and size>limit:raise ValueError('Oversize range')
     data.append(chunk)
    if limit is not None and size!=limit:raise ValueError('Incomplete range')
    return b''.join(data)
  except (httpx.RemoteProtocolError,httpx.ReadError,httpx.ConnectError,httpx.TimeoutException,httpx.TransportError) as error:
   delay=30*(2**attempt)
   log('REQUEST FAILED',type(error).__name__,'attempt',attempt+1,'backoff',delay,url)
   wait(delay)
   if attempt==2:raise
 raise RuntimeError('Retries exhausted')
def initialize(c):
 c.executescript('''PRAGMA journal_mode=WAL;
 CREATE TABLE IF NOT EXISTS selected(key TEXT PRIMARY KEY,crawl TEXT,domain TEXT,payload TEXT);
 CREATE INDEX IF NOT EXISTS selected_domain ON selected(domain);
 CREATE TABLE IF NOT EXISTS results(key TEXT PRIMARY KEY,crawl TEXT,domain TEXT,fetched INTEGER,bytes INTEGER,error TEXT);
 CREATE INDEX IF NOT EXISTS results_domain ON results(domain);
 CREATE TABLE IF NOT EXISTS ids(key TEXT,domain TEXT,orgnr TEXT,PRIMARY KEY(key,orgnr));
 CREATE INDEX IF NOT EXISTS ids_domain ON ids(domain);
 CREATE TABLE IF NOT EXISTS files(crawl TEXT,path TEXT,status TEXT,rows INTEGER DEFAULT 0,PRIMARY KEY(crawl,path));
 CREATE TABLE IF NOT EXISTS crawls(crawl TEXT PRIMARY KEY,status TEXT);
 CREATE TABLE IF NOT EXISTS parents(orgnr TEXT PRIMARY KEY,parent TEXT);
 CREATE TABLE IF NOT EXISTS universe(orgnr TEXT PRIMARY KEY);
 ''')
 if not c.execute('SELECT 1 FROM parents LIMIT 1').fetchone():
  csv.field_size_limit(10000000)
  with textfile(OSM/'raw/subunits.csv.download') as f:
   sample=f.read(32768);f.seek(0);reader=csv.DictReader(f,dialect=csv.Sniffer().sniff(sample,delimiters=';,\t'))
   c.executemany('INSERT OR REPLACE INTO parents VALUES(?,?)',((r['organisasjonsnummer'],r['overordnetEnhet']) for r in reader))
  c.commit()
 if not c.execute('SELECT 1 FROM universe LIMIT 1').fetchone():
  with textfile(OSM/'raw/universe.jsonl.gz') as f:c.executemany('INSERT OR IGNORE INTO universe VALUES(?)',((org(json.loads(line)),)for line in f if line.strip()))
  c.commit()
 # Import the existing frozen selection so remaining selected keys are retained and global caps hold.
 path=RAW/'columnar-selected.jsonl'
 if path.exists():
  with path.open(encoding='utf8') as f:
   for line in f:
    if not line.strip():continue
    r=json.loads(line);key=r['filename']+':'+r['offset']
    if eligible(r):c.execute('INSERT OR IGNORE INTO selected VALUES(?,?,?,?)',(key,'CC-MAIN-2026-43',domain(r['url']),json.dumps(r)))
 if RESULTS.exists():
  with RESULTS.open(encoding='utf8') as f:
   for line in f:
    if not line.strip():continue
    try:r=json.loads(line)
    except ValueError:raise RuntimeError('Truncated results line: inspect before resuming, do not silently discard')
    crawl=(re.search(r'CC-MAIN-\d{4}-\d{2}',r['key'])or[None])[0]or'CC-MAIN-2026-43'
    save_db(c,r,crawl)
 c.commit()
def save_db(c,r,crawl):
 c.execute('INSERT OR REPLACE INTO results VALUES(?,?,?,?,?,?)',(r['key'],crawl,r['domain'],int(bool(r.get('fetched')or r.get('compressed_bytes'))),r.get('compressed_bytes',0),r.get('error')))
 c.execute('DELETE FROM ids WHERE key=?',(r['key'],))
 c.executemany('INSERT OR IGNORE INTO ids VALUES(?,?,?)',((r['key'],r['domain'],n)for n in r.get('numbers',{})))
def summary(status='running'):
 try:
  c=connect();run=json.loads(STATE.read_text(encoding='utf8'));elapsed=time.time()-run['started_epoch']
  rows=c.execute('SELECT crawl,status FROM crawls ORDER BY crawl DESC').fetchall()
  c.execute('CREATE TEMP TABLE banned AS SELECT domain FROM ids GROUP BY domain HAVING count(DISTINCT orgnr)>=3')
  c.execute('CREATE TEMP TABLE kept AS SELECT DISTINCT i.key,i.domain,i.orgnr,coalesce(p.parent,i.orgnr) AS parent FROM ids i LEFT JOIN parents p ON p.orgnr=i.orgnr WHERE i.domain NOT IN(SELECT domain FROM banned)')
  fetched,totalbytes=c.execute('SELECT coalesce(sum(fetched),0),coalesce(sum(bytes),0) FROM results').fetchone()
  pages,ids,domains=c.execute('SELECT count(DISTINCT key),count(DISTINCT orgnr),count(DISTINCT domain)FROM kept').fetchone()
  matches=c.execute('SELECT count(DISTINCT parent)FROM kept WHERE parent IN(SELECT orgnr FROM universe)').fetchone()[0]
  size=c.execute('SELECT count(*)FROM universe').fetchone()[0]
  d={'status':status,'updated_utc':stamp(),'hard_stop_ist':'2026-11-13T10:00:00+05:30','crawls_covered':[{'crawl':a,'status':b}for a,b in rows],'records_selected':c.execute('SELECT count(*)FROM selected').fetchone()[0],'records_processed':c.execute('SELECT count(*)FROM results').fetchone()[0],'records_fetched':fetched,'orgnr_pages':pages,'distinct_orgnrs':ids,'distinct_domains':domains,'universe_size':size,'universe_matches':matches,'expected_per_1000':1000*matches/size if size else None,'successful_range_MB':totalbytes/1e6,'elapsed_seconds':elapsed,'excluded_domains':c.execute('SELECT count(*)FROM banned').fetchone()[0],'parse_or_fetch_errors':c.execute('SELECT count(*)FROM results WHERE error IS NOT NULL').fetchone()[0],'max_concurrent_warc_requests':4,'live_checks':False,'terms':'Common Crawl Terms of Use and third-party rights apply; bounded30/60s backoff; no credentials or paid APIs.','scope':'Cumulative existing plus overnight results, exact cached subunit-parent mapping; pairs are candidates, not verified websites. Unknown parent contacts are not inferred. No WARC bytes stored.','MB_scope':'Successful stored-result range payload bytes, excludes failed/aborted requests and Parquet reads.'}
  c.close();target=OUT/'overnight-summary.json';temp=target.with_suffix('.tmp');temp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf8');temp.replace(target);log('SUMMARY',status,d['records_fetched'],matches)
 except Exception:log('SUMMARY ERROR',traceback.format_exc())
def reporter():
 while not STOP.wait(1800):summary()
def fetch(r):
 key=r['filename']+':'+r['offset'];item={'key':key,'crawl':r.get('crawl'),'domain':domain(r['url']),'url':r['url'],'timestamp':r.get('timestamp'),'numbers':{}}
 try:
  check();offset,length=int(r['offset']),int(r['length'])
  with httpx.Client(headers={'User-Agent':UA},verify=True,trust_env=False,follow_redirects=False) as client:
   body=request(client,'https://data.commoncrawl.org/'+r['filename'],{'Range':f'bytes={offset}-{offset+length-1}'})
  item['compressed_bytes']=length;item['fetched']=True;item['numbers']=numbers(' '.join(Page(http_body(body),r['url']).visible.split()))
 except Exception as e:item['error']=f'{type(e).__name__}: {e}'
 return item
def drain(c,crawl):
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool,RESULTS.open('a',encoding='utf8') as out:
  while time.time()<DEADLINE and not STOP.is_set():
   batch=c.execute('SELECT s.payload FROM selected s LEFT JOIN results r ON r.key=s.key WHERE s.crawl=? AND r.key IS NULL LIMIT 128',(crawl,)).fetchall()
   if not batch:return
   iterator=iter(batch);pending={}
   for _ in range(4):
    row=next(iterator,None)
    if row:pending[pool.submit(fetch,json.loads(row[0]))]=1
   while pending:
    done,_=concurrent.futures.wait(pending,timeout=1,return_when=concurrent.futures.FIRST_COMPLETED)
    for future in done:
     pending.pop(future)
     try:r=future.result()
     except Exception as error:
      log('RECORD WORKER ERROR',type(error).__name__,str(error));continue
     # Do not persist never-started cutoff keys, so a future authorized run may resume them.
     if time.time()<DEADLINE or r.get('compressed_bytes'):
      out.write(json.dumps(r,ensure_ascii=False)+'\n');out.flush();save_db(c,r,crawl);c.commit()
      total=c.execute('SELECT count(*)FROM results').fetchone()[0]
      if total%25==0:log('RECORDS PROCESSED',total,'last',r['domain'],'failed'if r.get('error')else'fetched')
     if time.time()<DEADLINE and not STOP.is_set():
      row=next(iterator,None)
      if row:pending[pool.submit(fetch,json.loads(row[0]))]=1
   if c.execute('SELECT count(*)FROM results').fetchone()[0]%500<128:log('PROGRESS',c.execute('SELECT count(*)FROM results').fetchone()[0])
def select_file(c,crawl,path):
 output=RAW/('overnight-select-'+crawl+'.jsonl')
 for attempt in range(3):
  check();cmd=['uv','run','--no-project','--with','duckdb','python',str(ROOT/'scripts/cc_overnight_select.py'),crawl,path,str(output),str(DEADLINE)]
  log('SELECT',crawl,path,'attempt',attempt+1);child=subprocess.Popen(cmd,cwd=ROOT);CHILD[0]=child
  while child.poll() is None:
   if time.time()>=DEADLINE or STOP.wait(.5):
    subprocess.run(['taskkill','/PID',str(child.pid),'/T','/F'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);raise TimeoutError('Selection cutoff')
  CHILD[0]=None
  if child.returncode==0:break
  if attempt==2:raise RuntimeError('Parquet query failed after bounded retries')
  wait(30*(attempt+1))
 counts=dict(c.execute('SELECT domain,count(*)FROM selected GROUP BY domain').fetchall());n=0
 processed={d for d, in c.execute('SELECT DISTINCT domain FROM results')}
 with output.open(encoding='utf8') as f:
  for line in f:
   r=json.loads(line)
   if not eligible(r):continue
   d=domain(r['url']);key=r['filename']+':'+r['offset']
   if crawl!='CC-MAIN-2026-43' and d in processed:continue
   if counts.get(d,0)>=2 or c.execute('SELECT 1 FROM selected WHERE key=?',(key,)).fetchone():continue
   c.execute('INSERT OR IGNORE INTO selected VALUES(?,?,?,?)',(key,crawl,d,json.dumps(r)));counts[d]=counts.get(d,0)+1;n+=1
 c.execute('INSERT OR REPLACE INTO files VALUES(?,?,?,?)',(crawl,path,'complete',n));c.commit()
def main():
 RAW.mkdir(parents=True,exist_ok=True)
 if time.time()>=DEADLINE:log('Deadline already passed; no request made');return
 run=json.loads(STATE.read_text(encoding='utf8'))if STATE.exists()else{'started_epoch':time.time(),'started_utc':stamp()};STATE.write_text(json.dumps(run,indent=2)+'\n',encoding='utf8')
 required=[OSM/'raw/subunits.csv.download',OSM/'raw/universe.jsonl.gz']
 missing=[str(p.relative_to(ROOT)) for p in required if not p.is_file()]
 if missing:raise SystemExit('Prepare the ignored official input caches first: '+', '.join(missing))
 c=connect();initialize(c);summary();threading.Thread(target=reporter,daemon=True).start()
 try:
  # Resume queued records before optional catalog refresh can delay useful work.
  c.execute('INSERT OR IGNORE INTO crawls VALUES(?,?)',('CC-MAIN-2026-43','running'));c.commit()
  drain(c,'CC-MAIN-2026-43')
  with httpx.Client(headers={'User-Agent':UA},verify=True,trust_env=False,follow_redirects=False)as client:
   catalog_cache=RAW/'overnight-collinfo.json'
   try:
    catalog_body=request(client,'https://index.commoncrawl.org/collinfo.json');catalog=json.loads(catalog_body);catalog_cache.write_bytes(catalog_body)
   except Exception as error:
    log('CATALOG FAILED; continuing cached current crawl',type(error).__name__)
    catalog=json.loads(catalog_cache.read_text(encoding='utf8'))if catalog_cache.exists()else[{'id':'CC-MAIN-2026-43'}]
   crawls=sorted([x['id']for x in catalog if x['id'].startswith('CC-MAIN-')and x['id']<='CC-MAIN-2026-43'],reverse=True)
   for crawl in crawls:
    check();prior=c.execute('SELECT status FROM crawls WHERE crawl=?',(crawl,)).fetchone()
    if prior and prior[0]=='complete':continue
    c.execute('INSERT OR REPLACE INTO crawls VALUES(?,?)',(crawl,'running'));c.commit();summary()
    manifest=RAW/('overnight-'+crawl+'-paths.gz')
    if not manifest.exists():
     try:manifest.write_bytes(request(client,'https://data.commoncrawl.org/crawl-data/'+crawl+'/cc-index-table.paths.gz'))
     except Exception as error:
      log('MANIFEST FAILED',crawl,type(error).__name__)
      fallback=OUT/'columnar-files.json'
      if crawl=='CC-MAIN-2026-43'and fallback.exists():manifest.write_bytes(gzip.compress(('\n'.join(json.loads(fallback.read_text(encoding='utf8'))['paths'])+'\n').encode()))
      else:
       c.execute('INSERT OR REPLACE INTO crawls VALUES(?,?)',(crawl,'manifest_failed'));c.commit();continue
    paths=[p for p in gzip.decompress(manifest.read_bytes()).decode().splitlines()if'/subset=warc/'in p]
    drain(c,crawl)
    old=json.loads((OUT/'columnar-query.json').read_text(encoding='utf8'))if crawl=='CC-MAIN-2026-43' and (OUT/'columnar-query.json').exists() else{}
    for path in paths:
     check();done=c.execute('SELECT status FROM files WHERE crawl=?AND path=?',(crawl,path)).fetchone()
     if done and done[0]=='complete':continue
     if old.get('rows_per_file',{}).get(path)==0:c.execute('INSERT OR REPLACE INTO files VALUES(?,?,?,?)',(crawl,path,'complete',0));c.commit();continue
     try:select_file(c,crawl,path)
     except TimeoutError:raise
     except Exception as error:
      log('FILE FAILED; continuing',path,type(error).__name__,str(error));c.execute('INSERT OR REPLACE INTO files VALUES(?,?,?,?)',(crawl,path,'failed',0));c.commit();continue
     drain(c,crawl)
    drain(c,crawl);check()
    c.execute('INSERT OR REPLACE INTO crawls VALUES(?,?)',(crawl,'complete'));c.commit();summary()
 except TimeoutError:log('HARD STOP / cutoff reached')
 except Exception:log('RUN ERROR',traceback.format_exc())
 finally:
  STOP.set();summary('stopped_deadline'if time.time()>=DEADLINE else'finished_or_error');c.close()
if __name__=='__main__':main()
