import json
from pathlib import Path
from signalpost.models.envelope import Envelope
from signalpost.sources.blobstore import BlobStore
from signalpost.web.entity_scope import enforce
base=Path('bench/runs/20261107T073418068646Z-42def8c');blobs=BlobStore(base/'state');before=0;lost=[]
for line in (base/'enrichment-continuation/envelopes.jsonl').open(encoding='utf-8'):
 r=json.loads(line)
 if not any(c['field']=='official_website' and c['availability']=='available' for c in r['claims']):continue
 before+=1;row=Envelope.model_validate(r);enforce([row],blobs,None)
 if not any(c.field=='official_website' and c.availability=='available' for c in row.claims):lost.append({'orgnr':row.organisation_number,'name':next(c.value for c in row.claims if c.field=='identity.legal_name')})
result={'before':before,'after':before-len(lost),'withheld':lost,'http_requests':0,'narrowing':'Preserve existing exact-own-orgnr spacing/singular-title normalization. Initial candidate guard incorrectly withheld Control Solutions; corrected and rechecked.'}
Path('bench/reports/s6-step22/frozen-guard-final.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
