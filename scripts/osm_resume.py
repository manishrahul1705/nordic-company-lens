"""Resume a cached Geofabrik artifact with two disjoint ranges, never a full re-download."""
import concurrent.futures,hashlib,json,shutil,time
from pathlib import Path
import httpx
RAW=Path(__file__).resolve().parents[1]/'bench/reports/osm-check/raw'
def main():
 meta=json.loads((RAW/'pbf-http-headers.json').read_text());total=int(meta['headers']['Content-Length']);target=RAW/'norway-latest.osm.pbf';prefix=target.with_suffix('.pbf.part')
 if target.exists():print('PBF already cached');return
 state=RAW/'pbf-ranges.json'
 if state.exists():plan=json.loads(state.read_text())
 else:
  offset=prefix.stat().st_size;mid=(offset+total)//2
  plan={'url':meta['url'],'etag':meta['headers']['ETag'],'total':total,'prefix_bytes':offset,'ranges':[[offset,mid-1],[mid,total-1]],'started_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime())};state.write_text(json.dumps(plan,indent=2))
 def worker(pair):
  first,last=pair;path=RAW/f'pbf-range-{first}-{last}.part';saved=path.stat().st_size if path.exists() else 0;start=first+saved
  if start>last:return path
  with httpx.Client(trust_env=False,verify=True) as client:
   failures=0
   while start<=last:
    end=min(last,start+8*1024*1024-1)
    headers={'User-Agent':'SignalpostAgent/1.0 (+https://github.com/manishrahul1705/nordic-company-lens)','Range':f'bytes={start}-{end}','If-Range':plan['etag']}
    try:
     with client.stream('GET',plan['url'],headers=headers,timeout=httpx.Timeout(60,connect=20)) as r:
      if r.status_code!=206 or r.headers.get('Content-Range')!=f'bytes {start}-{end}/{total}':raise ValueError('Exact range not honored')
      if r.headers.get('etag')!=plan['etag']:raise ValueError('Snapshot changed')
      with path.open('ab') as f:
       for chunk in r.iter_bytes(65536):f.write(chunk)
     failures=0
    except (httpx.TransportError,httpx.HTTPStatusError) as error:
     failures+=1;print(type(error).__name__, 'retaining received bytes',flush=True)
     if failures>=3:raise
     time.sleep(5*failures)
    new=first+path.stat().st_size
    if new<=start:raise ValueError('No progress')
    start=new
    print(f'Range {first}: cached {path.stat().st_size/1e6:.1f} MB',flush=True)
    time.sleep(0.5)
  if path.stat().st_size!=last-first+1:raise ValueError('Incomplete range retained')
  return path
 with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:paths=list(pool.map(worker,plan['ranges']))
 if prefix.stat().st_size!=plan['prefix_bytes']:raise ValueError('Cached prefix changed')
 with prefix.open('ab') as f:
  for path in paths:
   with path.open('rb') as piece:shutil.copyfileobj(piece,f,1024*1024)
 if prefix.stat().st_size!=total:raise ValueError('Wrong final size')
 prefix.rename(target)
 manifest={'url':'https://download.geofabrik.de/europe/norway-latest.osm.pbf','resolved_url':plan['url'],'http_last_modified':meta['headers']['Last-Modified'],'download_note':'Initial transfer ended early; existing prefix retained and only missing bytes requested via disjoint ranges; no full duplicate download.','download_ranges':plan}
 (RAW.parent/'pbf-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('Complete cached PBF bytes:',total,flush=True)
if __name__=='__main__':main()
