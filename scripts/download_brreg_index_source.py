"""Download official BRREG open data into ignored cache for development-time index builds."""
import argparse
import hashlib
import json
from pathlib import Path
import time
import urllib.request
from datetime import datetime, timezone

SOURCE_URL='https://data.brreg.no/enhetsregisteret/api/enheter/lastned/csv'


def download(directory):
    directory=Path(directory);directory.mkdir(parents=True,exist_ok=True)
    target=directory/'enheter.csv.gz';partial=directory/'enheter.csv.gz.part'
    if target.exists() or partial.exists():raise ValueError('Refusing to overwrite an existing download')
    started=datetime.now(timezone.utc).isoformat();began=time.perf_counter()
    request=urllib.request.Request(SOURCE_URL,headers={
        'User-Agent':'NordicCompanyLens/2.0 (official open-data index build)', 'Accept-Encoding':'gzip'})
    with urllib.request.urlopen(request,timeout=60) as response:
        if response.status!=200 or response.url!=SOURCE_URL:raise ValueError('Expected direct official HTTP 200')
        headers={k:response.headers[k] for k in ['content-length','content-type','content-disposition','last-modified','etag'] if k in response.headers}
        with partial.open('wb') as output:
            while chunk:=response.read(1024*1024):output.write(chunk)
    if int(headers.get('content-length',partial.stat().st_size))!=partial.stat().st_size:
        raise ValueError('Truncated official bulk response')
    with partial.open('rb') as handle:digest=hashlib.file_digest(handle,'sha256').hexdigest()
    partial.replace(target)
    metadata={'source_url':SOURCE_URL,'retrieval_started_at':started,
        'retrieved_at':datetime.now(timezone.utc).isoformat(),'dataset_sha256':digest,
        'download_bytes':target.stat().st_size,'http_status':200,'final_url':SOURCE_URL,
        'response_headers':headers,'seconds':round(time.perf_counter()-began,3)}
    (directory/'download.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    return metadata


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--directory',type=Path,default=Path('bench/cache/official-brreg'))
    args=parser.parse_args();print(json.dumps(download(args.directory),indent=2))
