"""Explicit development-time bulk transfer, never imported by the runtime."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from datetime import datetime,timezone
import urllib.request
from signalpost.sources.funding_snapshots import SOURCES


def download(kind,directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    target=directory/(kind+'.csv');partial=directory/(kind+'.csv.part')
    if target.exists() or partial.exists():raise ValueError('Refusing to overwrite cached transfer')
    url=SOURCES[kind][0];began=time.perf_counter()
    request=urllib.request.Request(url,headers={'User-Agent':'NordicCompanyLens/2.0 (one-off NLOD bulk snapshot)'})
    with urllib.request.urlopen(request,timeout=120) as response,partial.open('wb') as output:
        if response.status!=200 or response.url!=url:raise ValueError('Expected direct official HTTP 200')
        headers={k:response.headers[k] for k in ['content-type','content-length','etag','last-modified'] if k in response.headers}
        while chunk:=response.read(1024*1024):output.write(chunk)
    if partial.stat().st_size!=int(headers.get('content-length',partial.stat().st_size)):
        raise ValueError('Incomplete snapshot transfer; partial file is not usable')
    partial.replace(target)
    with target.open('rb') as f:sha=hashlib.file_digest(f,'sha256').hexdigest()
    metadata={'source_url':url,'retrieved_at':datetime.now(timezone.utc).isoformat(),
        'dataset_sha256':sha,'bytes':target.stat().st_size,'status':200,'final_url':url,
        'headers':headers,'seconds':round(time.perf_counter()-began,3)}
    (directory/(kind+'-download.json')).write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    return metadata


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('kind',choices=SOURCES);p.add_argument('--directory',type=Path,default=Path('bench/cache/funding-snapshots'));a=p.parse_args();print(json.dumps(download(a.kind,a.directory),indent=2))
