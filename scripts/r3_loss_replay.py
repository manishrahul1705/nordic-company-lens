"""Compare ownership decisions using saved live pages under either runtime."""
import argparse,json,sys
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--source-root',type=Path,required=True);a=p.parse_args();root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(a.source_root.resolve()/'src'))
from signalpost.web.html import Page
from signalpost.web.collector import candidate_proof
from signalpost.web.candidates import Candidate


from signalpost.sources.blobstore import BlobStore
from signalpost.models.envelope import Envelope
from signalpost.web.entity_scope import enforce
results=[]
for label in ('r3-baseline','r3-corrected-live'):
 raw=json.loads((root/'bench/cache'/f'r3-loss-{label}-990412375.json').read_text(encoding='utf8'))
 records={}
 for e in raw['evidence']:
  if e['source_class']=='company_owned':records[(e['source_url'],e['content_sha256'])]=e
 # Include rejected proof pages: their request/body record is still retained.
 report=json.loads((root/'bench/runs'/label/'report.json').read_text(encoding='utf8'))
 for e in report['request_log']:
  if e.get('status')==200 and 'bnv.no' in e.get('url','') and 'robots.txt' not in e['url'] and e.get('content_sha256'):
   records[(e['url'],e['content_sha256'])]={'source_url':e['url'],'content_sha256':e['content_sha256']}
 for (url,sha),e in records.items():
  if not ('personvern' in url or url.rstrip('/')=='https://bnv.no'):continue
  path=root/'bench/runs'/label/'state/blobs'/sha
  if not path.exists():continue
  page=Page(path.read_bytes(),url);proof=candidate_proof(page,'990412375',{'name':'BERGEN VAKTMESTERTJENESTER AS'},Candidate(url,'bnv.no','registry_email'),[])
  index=page.raw.find('943737207')
  results.append({'company':'BERGEN VAKTMESTERTJENESTER AS','run':label,'url':url,'sha256':sha,'level':proof.level,'reason':proof.reason,'other_orgnrs':proof.other_orgnrs,'foreign_id_excerpt':page.raw[max(0,index-100):index+100] if index>=0 else None})
# Reconstruct the missing-homepage condition on the baseline's link-only claim.
raw=json.loads((root/'bench/cache/r3-loss-r3-baseline-911691248.json').read_text(encoding='utf8'))
sha='204ee52edfc85ec7e08936232092cbc6351b4e8d96534264bd1bb9ca00183012'
from signalpost.models.evidence import digest
replacement={}
for e in raw['evidence']:
 if e['source_class']=='company_owned':
  prior=e['id'];e['content_sha256']=sha;e['id']=digest([e['source_url'],sha,e['locator'],e['extraction_method']]);replacement[prior]=e['id']
for c in raw['claims']:c['evidence_ids']=[replacement.get(i,i) for i in c['evidence_ids']]
row=Envelope.model_validate(raw)
enforce([row],BlobStore(root/'bench/runs/r3-corrected-live/state'),None)
results.append({'company':'ISTAD ART SOLUTION NORWAY NUF','condition':'Current homepage blob missing on disk despite HTTP 200 request log','sha256':sha,'blob_exists':(root/'bench/runs/r3-corrected-live/state/blobs'/sha).exists(),'website_after_final_guard':any(c.field=='official_website' and c.availability=='available' for c in row.claims),'entity_scope':row.run.refresh.get('website',{}).get('entity_scope')})
print(json.dumps(results,ensure_ascii=True,indent=2))
