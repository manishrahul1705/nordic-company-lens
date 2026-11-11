"""One-shot OSM measurement; never imported by the production agent.
Derived candidates: © OpenStreetMap contributors, ODbL 1.0.
"""
import csv, gzip, hashlib, io, json, random, sys, time
from dataclasses import asdict
from pathlib import Path
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser
import httpx
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from signalpost.identity.orgnr import valid
from signalpost.web.html import Page
from signalpost.web.proof import score

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'bench/reports/osm-check'; RAW=OUT/'raw'
UA='NordicCompanyLens-OSMMeasurement/1.0 (+https://github.com/manishrahul1705/nordic-company-lens)'
QUERY='[out:json][timeout:900];area["ISO3166-1"="NO"][admin_level=2]->.a;(nwr["ref:NO:orgnr"](area.a););out tags center;'
BULK='https://data.brreg.no/enhetsregisteret/api/underenheter/lastned/csv'
UNIVERSE='https://builderr.ai/signalpost-company-universe-2025.jsonl.gz'

def dump(path,value):path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def download(client,url,path):
    if path.exists():return {'cached':True,'bytes':path.stat().st_size}
    with client.stream('GET',url,timeout=900) as r:
        r.raise_for_status()
        with path.with_suffix(path.suffix+'.part').open('wb') as f:
            for data in r.iter_bytes():f.write(data)
    path.with_suffix(path.suffix+'.part').rename(path)
    return {'cached':False,'bytes':path.stat().st_size}
def textfile(path):
    f=path.open('rb');magic=f.read(2);f.seek(0)
    return io.TextIOWrapper(gzip.GzipFile(fileobj=f) if magic==b'\x1f\x8b' else f,encoding='utf-8-sig')
def org(row):return str(row.get('organisation_number') or row.get('organisasjonsnummer') or row.get('orgnr') or '')
def unavailable_summary(metadata):
    """Record missing measurements as null; never infer zero coverage from an outage."""
    metadata['files']={}
    for p in RAW.iterdir():
        if p.is_file() and not p.name.endswith('.part'):
            with p.open('rb') as f: digest=hashlib.file_digest(f,'sha256').hexdigest()
            metadata['files'][p.name]={'bytes':p.stat().st_size,'sha256':digest}
    universe=None
    path=RAW/'universe.jsonl.gz'
    if path.exists():
        with textfile(path) as f:
            numbers=[org(json.loads(line)) for line in f if line.strip()]
        universe={'rows':len(numbers),'distinct_companies':len(set(numbers)),
                  'companies_with_osm_website':None,'expected_per_1000':None}
    summary={'status':'blocked_overpass_unavailable','query':QUERY,
             'attribution':'Copyright OpenStreetMap contributors; ODbL 1.0 https://opendatacommons.org/licenses/odbl/1-0/',
             'brreg_licence':'NLOD 2.0; Bronnoysundregistrene',
             'objects_with_orgnr_tag':None,'objects_with_valid_orgnr':None,
             'objects_with_valid_orgnr_and_website':None,'objects_with_subunit_orgnr':None,
             'website_objects_with_subunit_orgnr':None,'distinct_subunit_numbers':None,
             'distinct_parent_companies_with_website':None,'batch100_match_count':None,
             'batch100_matches':None,'universe':universe,
             'live_review':{'sample_size':0,'passed':None,'reason':'No OSM candidates received; review not performed'},
             'overpass_attempts':metadata.get('overpass_attempts',[]),
             'limitations':['No successful OSM response received; no raw OSM JSON available to gzip.',
                            'Empty candidates.jsonl means unavailable measurement, not zero OSM candidates.',
                            'No additional Overpass query or Common Crawl work was performed.']}
    (OUT/'candidates.jsonl').touch()
    dump(OUT/'download.json',metadata);dump(OUT/'summary.json',summary)
    print(json.dumps(summary,indent=2),flush=True)

def run():
    OUT.mkdir(parents=True,exist_ok=True);RAW.mkdir(exist_ok=True)
    began=time.monotonic(); metadata={}; overpass=RAW/'overpass.json.gz'
    with httpx.Client(headers={'User-Agent':UA},follow_redirects=True,verify=True) as client:
        if not overpass.exists():
            ledger=OUT/'download.json'
            if ledger.exists() and json.loads(ledger.read_text(encoding='utf8')).get('overpass_attempts'):
                raise RuntimeError('Recorded Overpass attempts already exhausted; explicit new authorization required before another query')
            attempts=[]
            for i,host in enumerate(['overpass-api.de','overpass.kumi.systems']):
                if i:time.sleep(60)
                attempt={'host':host}
                attempts.append(attempt)
                try:
                    r=client.post('https://'+host+'/api/interpreter',data={'data':QUERY},timeout=960)
                    attempt['status']=r.status_code
                    if r.is_error:
                        with gzip.open(RAW/(host+'-error.txt.gz'),'wb') as f:f.write(r.content)
                    r.raise_for_status(); body=r.content; result=json.loads(body)
                    if result.get('remark'):raise ValueError(result['remark'])
                    with gzip.open(overpass,'wb') as f:f.write(body)
                    metadata['overpass_host']=host;break
                except Exception as e:
                    attempt['error']=f'{type(e).__name__}: {e}'
                    print('Overpass attempt:',attempts[-1],flush=True)
            metadata['overpass_attempts']=attempts
            dump(OUT/'download.json',metadata)
            if not overpass.exists():
                unavailable_summary(metadata)
                return
        data=json.loads(gzip.decompress(overpass.read_bytes()));print('OSM objects',len(data['elements']),flush=True)
        metadata['subunits']=download(client,BULK,RAW/'subunits.csv.download');print('Bulk downloaded',metadata['subunits'],flush=True)
        elements=[];raw_count=0;invalid=0
        for e in data['elements']:
            tags=e.get('tags',{});number=str(tags.get('ref:NO:orgnr','')).strip()
            if number:raw_count+=1
            if not valid(number):invalid+=1;continue
            website=next((str(tags[k]).split(';')[0].strip() for k in ['website','contact:website','url'] if tags.get(k)),None)
            elements.append({'osm_type':e['type'],'osm_id':e['id'],'osm_url':f"https://www.openstreetmap.org/{e['type']}/{e['id']}",'tagged_orgnr':number,'website':website,'osm_name':tags.get('name')})
        wanted={e['tagged_orgnr'] for e in elements}; parents={}
        csv.field_size_limit(10_000_000)
        with textfile(RAW/'subunits.csv.download') as f:
            sample=f.read(32768);f.seek(0);dialect=csv.Sniffer().sniff(sample,delimiters=';,\t')
            reader=csv.DictReader(f,dialect=dialect)
            metadata['subunit_columns']=reader.fieldnames
            for row in reader:
                n=str(row.get('organisasjonsnummer','')).strip()
                if n in wanted:
                    parent=str(row.get('overordnetEnhet') or row.get('overordnetenhet') or '').strip()
                    if not valid(parent):raise ValueError('Missing valid parent in matching subunit row: '+repr(row))
                    parents[n]=parent
        print('Matched subunits',len(parents),flush=True)
        candidates=[]
        for e in elements:
            if e['website']:
                e.update(parent_orgnr=parents.get(e['tagged_orgnr'],e['tagged_orgnr']),is_subunit=e['tagged_orgnr'] in parents)
                candidates.append(e)
        with (OUT/'candidates.jsonl').open('w',encoding='utf8') as f:
            for e in candidates:f.write(json.dumps(e,ensure_ascii=False)+'\n')
        parent_set={e['parent_orgnr'] for e in candidates}
        batch={org(json.loads(line)) for line in (ROOT/'bench/inputs/100/batch.jsonl').read_text(encoding='utf8').splitlines() if line.strip()}
        summary={'query':QUERY,'attribution':'© OpenStreetMap contributors; ODbL 1.0 https://opendatacommons.org/licenses/odbl/1-0/','brreg_licence':'NLOD 2.0; Brønnøysundregistrene','objects_with_orgnr_tag':raw_count,'objects_with_valid_orgnr':len(elements),'invalid_orgnr_objects_excluded':invalid,'objects_with_valid_orgnr_and_website':len(candidates),'objects_with_subunit_orgnr':sum(e['tagged_orgnr'] in parents for e in elements),'website_objects_with_subunit_orgnr':sum(e['is_subunit'] for e in candidates),'distinct_subunit_numbers':len(parents),'distinct_parent_companies_with_website':len(parent_set),'batch100_matches':sorted(batch&parent_set),'batch100_match_count':len(batch&parent_set),'universe':None}
        try:
            metadata['universe']=download(client,UNIVERSE,RAW/'universe.jsonl.gz')
            universe={}
            with textfile(RAW/'universe.jsonl.gz') as f:
                count=0
                for line in f:
                    if line.strip():
                        row=json.loads(line);count+=1;universe[org(row)]=row
            matched=sorted(parent_set&universe.keys())
            summary['universe']={'rows':count,'distinct_companies':len(universe),'companies_with_osm_website':len(matched),'expected_per_1000':1000*len(matched)/len(universe),'method':'1000 times distinct matched parent companies / distinct universe companies; descriptive expectation, not verified coverage'}
            selected=random.Random(20261111).sample(matched,min(20,len(matched)));reviews=[]
            for n in selected:
                item={'orgnr':n,'universe_record':universe[n]}; c=next(e for e in candidates if e['parent_orgnr']==n);item['candidate']=c
                try:
                    r=client.get('https://data.brreg.no/enhetsregisteret/api/enheter/'+n,timeout=30);r.raise_for_status();reg=r.json()
                    address=reg.get('forretningsadresse') or reg.get('postadresse') or {}
                    context={'name':reg.get('navn'),'phone':reg.get('telefon') or reg.get('mobil'),'email':reg.get('epostadresse'),'street':address.get('adresse'),'postcode':address.get('postnummer'),'city':address.get('poststed'),'municipality':address.get('kommune'),'allowed_orgnrs':{n},'subunits':[]}
                    item['registry_context']={k:list(v) if isinstance(v,set) else v for k,v in context.items()}
                    url=c['website'];url=url if urlsplit(url).scheme else 'https://'+url
                    parts=urlsplit(url)
                    if parts.scheme not in {'http','https'}:raise ValueError('unsupported URL scheme')
                    robot_url=parts.scheme+'://'+parts.netloc+'/robots.txt'
                    rr=client.get(robot_url,timeout=20);item['robots_status']=rr.status_code
                    if rr.status_code in {401,403,429} or rr.status_code>=500:raise ValueError('robots unavailable or blocked')
                    if rr.status_code==200:
                        rp=RobotFileParser();rp.parse(rr.text.splitlines())
                        if not rp.can_fetch(UA,url):raise ValueError('robots disallow')
                    time.sleep(1)
                    # Exactly one logical live page fetch; no alternate host/path retries.
                    with client.stream('GET',url,timeout=30) as response:
                        item.update(status=response.status_code,final_url=str(response.url));response.raise_for_status()
                        chunks=[];size=0
                        for chunk in response.iter_bytes():
                            chunks.append(chunk);size+=len(chunk)
                            if size>4_000_000:raise ValueError('page exceeds 4 MB measurement limit')
                    body=b''.join(chunks);h=hashlib.sha256(body).hexdigest();(RAW/(h+'.html')).write_bytes(body)
                    p=score(Page(body,item['final_url']),n,context,'osm',[])
                    item.update(proof=asdict(p),passes=p.level=='VERIFIED',body_sha256=h)
                except Exception as e:item.update(passes=False,error=f'{type(e).__name__}: {e}')
                reviews.append(item);dump(OUT/'live-review.json',reviews)
                print('Review',len(reviews),n,item['passes'],item.get('error',''),flush=True)
            summary['live_review']={'seed':20261111,'sample_size':len(reviews),'passed':sum(x['passes'] for x in reviews),'method':'One candidate (first OSM object) per randomly sampled matching parent; one homepage fetch, redirects followed; robots checked, TLS verified; unchanged proof.score(origin=osm), default feature flags; no followup proof pages or subunit allowance. Errors count as non-passes. This tests proof only, not full production policy/collector acceptance.'}
        except Exception as e:summary['universe_error']=f'{type(e).__name__}: {e}'
        metadata['files']={p.name:{'bytes':p.stat().st_size,'sha256':hashlib.file_digest(p.open('rb'),'sha256').hexdigest()} for p in RAW.iterdir() if p.is_file()}
        summary['wall_seconds']=time.monotonic()-began;dump(OUT/'download.json',metadata);dump(OUT/'summary.json',summary)
        print(json.dumps(summary,ensure_ascii=True,indent=2),flush=True)
if __name__=='__main__':
    if sys.argv[1:]==['--report-unavailable']:
        unavailable_summary(json.loads((OUT/'download.json').read_text(encoding='utf8')))
    else:
        run()
