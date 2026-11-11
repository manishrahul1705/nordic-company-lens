"""Download Norway once and locally select orgnr-tagged OSM objects with pyosmium.
Data attribution: \u00a9 OpenStreetMap contributors (ODbL 1.0).
Run: uv run --no-project --with osmium python scripts/osm_extract.py
"""
import hashlib,json,time,urllib.request
from pathlib import Path
import osmium
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'bench/reports/osm-check';RAW=OUT/'raw'
URL='https://download.geofabrik.de/europe/norway-latest.osm.pbf'
CATEGORIES=('shop','craft','office','amenity','tourism','leisure','healthcare')
def main():
 OUT.mkdir(parents=True,exist_ok=True);RAW.mkdir(exist_ok=True)
 pbf=RAW/'norway-latest.osm.pbf';info={};start=time.monotonic()
 if not pbf.exists():
  part=pbf.with_suffix('.pbf.part');offset=part.stat().st_size if part.exists() else 0
  headers={'User-Agent':'SignalpostAgent/1.0 (+https://github.com/manishrahul1705/nordic-company-lens)'}
  url=URL
  if offset:
   saved=json.loads((RAW/'pbf-http-headers.json').read_text())
   url=saved['url'];total=int(saved['headers']['Content-Length'])
   local=osmium.io.Reader(osmium.io.File(str(part),'pbf'));stamp=local.header().get('timestamp');local.close()
   if stamp[:10].replace('-','')[2:] not in url:raise ValueError('Partial snapshot date and range URL do not match')
   headers.update({'Range':f'bytes={offset}-','If-Range':saved['headers']['ETag']})
  req=urllib.request.Request(url,headers=headers)
  with urllib.request.urlopen(req,timeout=180) as r:
   info['http_last_modified']=r.headers.get('Last-Modified');info['content_length']=r.headers.get('Content-Length');info['resolved_url']=r.url;size=offset;last=time.monotonic()
   if offset:
    if r.status!=206 or not r.headers.get('Content-Range','').startswith(f'bytes {offset}-'):raise ValueError('Server did not honor exact range; no bytes appended')
    if int(r.headers['Content-Range'].split('/')[-1])!=total:raise ValueError('Snapshot size changed')
    info['resumed_from_byte']=offset
   else:total=int(info['content_length']) if info['content_length'] else None
   (RAW/'pbf-transfer.json').write_text(json.dumps(info,indent=2))
   with part.open('ab' if offset else 'wb') as f:
    while True:
     chunk=r.read(4*1024*1024)
     if not chunk:break
     f.write(chunk);size+=len(chunk)
     if time.monotonic()-last>30:print(f'Downloaded {size/1e6:.1f} MB',flush=True);last=time.monotonic()
  if total and size!=total:raise ValueError(f'Incomplete PBF download: {size}/{total}; partial retained')
  part.rename(pbf)
 else:
  existing=OUT/'pbf-manifest.json'
  if existing.exists():info=json.loads(existing.read_text(encoding='utf8'))
 with pbf.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
 reader=osmium.io.Reader(str(pbf));header=reader.header()
 info.update(url=URL,bytes=pbf.stat().st_size,sha256=sha,header={k:header.get(k) for k in ['osmosis_replication_timestamp','osmosis_replication_sequence_number','generator','timestamp']},attribution='\u00a9 OpenStreetMap contributors',licence='ODbL 1.0',download_and_hash_seconds=round(time.monotonic()-start,3))
 reader.close();print('PBF',json.dumps(info),flush=True)
 class Filter(osmium.SimpleHandler):
  def __init__(self,output):super().__init__();self.output=output;self.counts={'node':0,'way':0,'relation':0};self.scanned={'node':0,'way':0,'relation':0}
  def keep(self,obj,kind):
   self.scanned[kind]+=1
   number=obj.tags.get('ref:NO:orgnr')
   if number is None:return
   tags={k:obj.tags[k] for k in ['ref:NO:orgnr','name','website','contact:website','url',*CATEGORIES] if k in obj.tags}
   key=next((k for k in CATEGORIES if k in tags),None)
   website=next((tags[k].split(';')[0].strip() for k in ['website','contact:website','url'] if tags.get(k)),None)
   self.output.write(json.dumps({'orgnr':number,'name':tags.get('name'),'website':website,'category':{'key':key,'value':tags[key]} if key else None,'type':kind,'id':obj.id,'tags':tags},ensure_ascii=False)+'\n');self.counts[kind]+=1
  def node(self,obj):self.keep(obj,'node')
  def way(self,obj):self.keep(obj,'way')
  def relation(self,obj):self.keep(obj,'relation')
 with (OUT/'objects.jsonl').open('w',encoding='utf8') as f:
  handler=Filter(f);handler.apply_file(str(pbf),locations=False,filters=[osmium.filter.KeyFilter('ref:NO:orgnr')])
 info.update(extracted_objects=sum(handler.counts.values()),extracted_by_type=handler.counts,matching_callbacks_by_type=handler.scanned,total_seconds=round(time.monotonic()-start,3))
 (OUT/'pbf-manifest.json').write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(info),flush=True)
if __name__=='__main__':main()
