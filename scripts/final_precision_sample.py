"""Fixed-seed Builderr cohort excluding recorded inputs and review artifacts."""
import gzip,hashlib,json,random,re
from pathlib import Path
from signalpost.identity.orgnr import valid
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'bench/reports/final-precision';SEED=20261112

def main():
 excluded=set();manifest=[]
 for base in (ROOT/'bench/inputs',ROOT/'bench/reports'):
  for path in sorted(base.rglob('*')):
   rel=path.relative_to(ROOT)
   if not path.is_file() or any(part in {'raw','final-precision','node_modules'} for part in rel.parts) or path.suffix not in {'.txt','.json','.jsonl','.csv','.md'}:continue
   # Source universes/bulk/indexes are datasets, not earlier reviewed cohorts.
   if path.name in {'candidates.jsonl','shared_identifiers.json','cc_orgnr_index.json'}:continue
   sha=hashlib.sha256();tail=''
   with path.open('rb') as f:
    while block:=f.read(1024*1024):
     sha.update(block);text=tail+block.decode('utf8',errors='replace');excluded.update(re.findall(r'(?<!\d)\d{9}(?!\d)',text));tail=text[-12:]
   manifest.append({'path':str(rel),'sha256':sha.hexdigest(),'bytes':path.stat().st_size})
 for path in (ROOT/'bench/cache').rglob('orgnrs.txt'):
  excluded.update(re.findall(r'(?<!\d)\d{9}(?!\d)',path.read_text(encoding='utf-8-sig',errors='replace')))
 universe=ROOT/'bench/reports/osm-check/raw/universe.jsonl.gz'
 eligible=[];total=0
 with gzip.open(universe,'rt',encoding='utf8') as f:
  for line in f:
   if not line.strip():continue
   total+=1;row=json.loads(line);org=str(row['organisation_number'])
   if valid(org) and org not in excluded:eligible.append(row)
 chosen=random.Random(SEED).sample(sorted(eligible,key=lambda x:x['organisation_number']),100)
 assert not ({r['organisation_number'] for r in chosen}&excluded)
 content='\n'.join([r['organisation_number'] for r in chosen]+['NOT-AN-ORGNR','123456789','   '])+'\n'
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'orgnrs.txt').write_text(content,encoding='utf8',newline='\n')
 (OUT/'selection.json').write_text(json.dumps({'seed':SEED,'universe_source':'https://builderr.ai/signalpost-company-universe-2025.jsonl.gz','cached_universe_sha256':hashlib.sha256(universe.read_bytes()).hexdigest(),'universe_rows':total,'eligible':len(eligible),'excluded_identifier_count':len(excluded),'exclusion_method':'All bench/inputs and earlier non-raw review artifacts, plus cached orgnrs.txt cohorts; official-run artifacts included. Source datasets and CC/OSM candidate indexes excluded from cohort definition.','exclusion_artifacts':manifest,'input_sha256':hashlib.sha256(content.encode()).hexdigest(),'companies':chosen,'invalid_lines':['NOT-AN-ORGNR','123456789','   ']},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'seed':SEED,'universe':total,'excluded':len(excluded),'eligible':len(eligible),'selected':100,'invalid':3,'input_sha256':hashlib.sha256(content.encode()).hexdigest()}))
if __name__=='__main__':main()
