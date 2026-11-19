"""Build a withholding-only name index from the pinned local 411,160 corpus."""
import gzip
import hashlib
import json
from pathlib import Path
from signalpost.web.social_universe import ARCHIVE_SHA,CONTENT_SHA,ROWS

source=Path('bench/reports/osm-check/raw/universe.jsonl.gz')
assert hashlib.sha256(source.read_bytes()).hexdigest()==ARCHIVE_SHA
digest=hashlib.sha256();records=[]
with gzip.open(source,'rb') as stream:
    for line in stream:
        digest.update(line);row=json.loads(line)
        records.append([str(row['organisation_number']),row['name']])
assert digest.hexdigest()==CONTENT_SHA and len(records)==ROWS and len(dict(records))==ROWS
payload={'schema_version':1,'purpose':'withholding-only registered-name universe; never ownership or relationship proof',
         'source_url':'https://builderr.ai/signalpost-company-universe-2025.jsonl.gz',
         'archive_sha256':ARCHIVE_SHA,'content_sha256':CONTENT_SHA,'companies':records}
out=Path('data/social_company_names.json.gz')
out.write_bytes(gzip.compress(json.dumps(payload,ensure_ascii=False,separators=(',',':')).encode(),compresslevel=9,mtime=0))
metadata={k:v for k,v in payload.items() if k!='companies'}
metadata.update(rows=ROWS,bytes=out.stat().st_size,index_sha256=hashlib.sha256(out.read_bytes()).hexdigest())
Path('data/social_company_names_build.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
print(json.dumps(metadata,indent=2))
