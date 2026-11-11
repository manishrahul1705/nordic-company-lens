"""Download once and count distinct registry entities per identifier (NLOD 2.0)."""
import csv, gzip, hashlib, io, json, sys, urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from signalpost.web.shared_identifiers import name_key, phone_key
URL='https://data.brreg.no/enhetsregisteret/api/enheter/lastned/csv'
RAW=ROOT/'bench/reports/cc-proto/raw/entities.csv.download'
RAW.parent.mkdir(parents=True,exist_ok=True)
if not RAW.exists():
    request=urllib.request.Request(URL,headers={'User-Agent':'NordicCompanyLens/2.0 (+https://github.com/manishrahul1705/nordic-company-lens)'})
    with urllib.request.urlopen(request,timeout=900) as response, RAW.with_suffix('.part').open('wb') as out:
        while chunk:=response.read(1024*1024):out.write(chunk)
    RAW.with_suffix('.part').replace(RAW)
csv.field_size_limit(10000000)
f=RAW.open('rb');magic=f.read(2);f.seek(0)
text=io.TextIOWrapper(gzip.GzipFile(fileobj=f) if magic==b'\x1f\x8b' else f,encoding='utf-8-sig')
sample=text.read(32768);text.seek(0)
counts={k:Counter() for k in ('phones','email_domains','name_keys')}
rows=0
for row in csv.DictReader(text,dialect=csv.Sniffer().sniff(sample,delimiters=';,\t')):
    rows+=1
    for number in {phone_key(row.get('telefon')),phone_key(row.get('mobil'))}-{''}: counts['phones'][number]+=1
    email=str(row.get('epostadresse') or '').strip().casefold()
    if '@' in email: counts['email_domains'][email.rsplit('@',1)[1]]+=1
    key=name_key(row.get('navn'))
    if key:counts['name_keys'][key]+=1
text.close()
payload=(json.dumps(counts,sort_keys=True,ensure_ascii=False,separators=(',',':'))+'\n').encode()
path=ROOT/'data/shared_identifiers.json.gz';path.write_bytes(gzip.compress(payload,compresslevel=9,mtime=0))
metadata={'build_utc':datetime.now(timezone.utc).isoformat(),'source':URL,'licence':'NLOD 2.0','attribution':'Bronnoysundregistrene','rows':rows,'gzip_bytes':path.stat().st_size,'source_sha256':hashlib.sha256(RAW.read_bytes()).hexdigest(),'keys':{k:len(v) for k,v in counts.items()}}
(ROOT/'data/shared_identifiers_build.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf8')
print(json.dumps(metadata),flush=True)
