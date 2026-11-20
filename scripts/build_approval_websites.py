"""Build deterministic official bulk indexes; raw inputs are never bundled."""
import argparse, csv, gzip, hashlib, io, json
from pathlib import Path
import xml.etree.ElementTree as ET

URLS = {'cleaning': 'https://registerdata.arbeidstilsynet.no/renhold_register.xml',
 'workshop': 'https://pkkvr-finn-godkjent-verksted-backend.atlas.vegvesen.no/export-csv?query=__ALL__',
 'related': 'https://data.brreg.no/enhetsregisteret/api/enheter/lastned/csv'}

def build(cleaning, workshop, registry, retrieved_at, output):
    output=Path(output); output.mkdir(parents=True,exist_ok=True)
    with gzip.open(registry,'rt',encoding='utf-8') as f:
        entities={r['organisasjonsnummer']:{'navn':r['navn'],'hjemmeside':r['hjemmeside']} for r in csv.DictReader(f)}
    root=ET.parse(cleaning).getroot()
    clean={}
    for v in root.findall('Virksomhet'):
        h=v.find('Hovedenhet'); o=h.findtext('Organisasjonsnummer')
        clean[o]={'organisation_number':o,'name':h.findtext('Navn'), 'status':h.findtext('Godkjenningsstatus')}
    workshops={}; rows=list(csv.DictReader(Path(workshop).read_text(encoding='utf-8-sig').splitlines(),delimiter=';',skipinitialspace=True))
    for r in rows:
        o=r['Organisasjonsnummer'].strip()
        if o not in entities: continue
        workshops.setdefault(o,[]).append({k:v.strip() for k,v in r.items()})
    related={o:{'organisasjonsnummer':o,'navn':r['navn'],'hjemmeside':r['hjemmeside']} for o,r in entities.items() if r['hjemmeside'].strip()}
    for kind,path,data,total,generation in [('cleaning',cleaning,clean,len(root.findall('Virksomhet')),root.findtext('Metadata/DatoTidGenerert')),('workshop',workshop,workshops,len(rows),None),('related',registry,related,len(entities),None)]:
        body=gzip.compress(json.dumps(data,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode(),mtime=0)
        (output/(kind+'_official.json.gz')).write_bytes(body)
        m={'source_url':URLS[kind],'retrieved_at':retrieved_at[kind],'source_generation_time':generation,'dataset_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),'dataset_rows':total,'index_sha256':hashlib.sha256(body).hexdigest(),'index_bytes':len(body),'indexed_companies':len(data),'licence':'NLOD 2.0' if kind!='workshop' else 'NLOD','licence_url':'https://data.norge.no/nlod/no/2.0' if kind!='workshop' else 'https://data.norge.no/nlod/no','transformations':['Exact main-unit identifiers only; preserve selected source fields; no inferred dates.','UTF-8 canonical sorted JSON; deterministic gzip mtime=0.'],'source_generation_time_note':'null means the source supplies no generation timestamp'}
        if kind=='workshop':m['main_unit_filter_sha256']=hashlib.sha256(Path(registry).read_bytes()).hexdigest()
        (output/(kind+'_official_manifest.json')).write_text(json.dumps(m,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--cleaning',required=True);p.add_argument('--workshop',required=True);p.add_argument('--registry',required=True);p.add_argument('--retrieved-at',required=True,help='JSON object with cleaning/workshop/related UTC retrieval timestamps');p.add_argument('--output',default='src/signalpost/data');a=p.parse_args();build(a.cleaning,a.workshop,a.registry,json.loads(a.retrieved_at),a.output)
