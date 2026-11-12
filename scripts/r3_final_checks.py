"""Offline final R3 proof/cache checks; no network or original output rewriting."""
import hashlib,json,time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
from signalpost.web import shared_identifiers as shared
from signalpost.web.html import Page
from signalpost.web.collector import candidate_proof
from signalpost.web.candidates import Candidate
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'bench/reports/r3-benchmark/final-small-items'
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 calls=Counter();original=shared.gzip.open
 def counted(path,*args,**kwargs):
  calls[Path(path).name]+=1
  return original(path,*args,**kwargs)
 shared._bundled.cache_clear();began=time.perf_counter()
 names=['cc_orgnr_index.json.gz','shared_identifiers.json.gz']*50
 with patch.object(shared.gzip,'open',counted):
  with ThreadPoolExecutor(max_workers=4) as pool:loaded=list(pool.map(shared.bundled,names))
 assert calls=={'cc_orgnr_index.json.gz':1,'shared_identifiers.json.gz':1}
 for name in set(names):
  objects=[value for key,value in zip(names,loaded) if key==name]
  assert all(value is objects[0] for value in objects)
 cache={'gzip_opens':dict(calls),'calls':len(names),'concurrent_workers':4,'cache_info':shared._bundled.cache_info()._asdict(),'elapsed_seconds':time.perf_counter()-began,'same_object_per_filename':True}
 report=json.loads((ROOT/'bench/runs/r3-corrected-live/report.json').read_text(encoding='utf8'));proofs=[]
 for event in report['request_log']:
  url=event['url']
  if event.get('organisation_number')!='990412375' or event.get('status')!=200 or 'bnv.no' not in url or 'robots.txt' in url:continue
  sha=event.get('content_sha256');path=ROOT/'bench/runs/r3-corrected-live/state/blobs'/sha
  if not path.exists():continue
  body=path.read_bytes();assert hashlib.sha256(body).hexdigest()==sha
  page=Page(body,url);proof=candidate_proof(page,'990412375',{'name':'BERGEN VAKTMESTERTJENESTER AS'},Candidate(url,'bnv.no','registry_email'),[])
  proofs.append({'url':url,'sha256':sha,'level':proof.level,'proof_type':proof.proof_type,'reason':proof.reason,'other_orgnrs':proof.other_orgnrs})
 assert proofs and all(p['level']=='VERIFIED' for p in proofs)
 result={'mode':'Offline proof replay and local cache instrumentation; not another live benchmark','cache':cache,'bnv_saved_pages':proofs,'bnv_now_passes_ownership':True,'release_wall_seconds_per_100_valid_companies':[372.7661578999978,254.72229920000245],'release_total_lines':103,'release_valid_companies':100,'istad':{'sha256':'204ee52edfc85ec7e08936232092cbc6351b4e8d96534264bd1bb9ca00183012','blob_exists':(ROOT/'bench/runs/r3-corrected-live/state/blobs/204ee52edfc85ec7e08936232092cbc6351b4e8d96534264bd1bb9ca00183012').exists(),'code_deletion_or_write_skip_found':False,'cause':'Microsoft Defender quarantined this exact blob: event 1116 detection and 1117 successful quarantine, Trojan:Script/Wacatac.H!ml. See defender-events.json. No blob deletion or skip path found in production or the R3 measurement runner; storage behavior unchanged.'}}
 (OUT/'checks.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf8');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
