"""Select a fresh BRREG cohort, excluding all recorded benchmark/official identifiers."""
import hashlib,json,random,re,time
from pathlib import Path
import httpx
from signalpost.identity.orgnr import valid

def main():
 root=Path(__file__).resolve().parents[1];out=root/'bench/reports/s6-step22';out.mkdir(parents=True,exist_ok=True)
 excluded=set();files=list((root/'bench/inputs').rglob('*'))+list((root/'bench/reports').rglob('*'))
 files += list((root/'bench/cache').glob('**/orgnrs.txt'))
 for p in files:
  if p.is_file() and p.suffix in {'.txt','.json','.jsonl','.csv','.md'}:
   excluded.update(re.findall(r'(?<!\d)\d{9}(?!\d)',p.read_text(encoding='utf-8-sig',errors='replace')))
 rng=random.SystemRandom();pages=[];records={}
 (out/'selection-source').mkdir(exist_ok=True)
 with httpx.Client(timeout=30) as client:
  base='https://data.brreg.no/enhetsregisteret/api/enheter'
  probe=client.get(base,params={'size':100,'page':0});probe.raise_for_status();total=probe.json()['page']['totalPages']
  for page in rng.sample(range(1,min(total,100)),8):
   response=client.get(base,params={'size':100,'page':page});response.raise_for_status();data=response.json()
   (out/'selection-source'/f'page-{page}.json').write_bytes(response.content)
   rows=data.get('_embedded',{}).get('enheter',[])
   pages.append({'url':str(response.url),'sha256':hashlib.sha256(response.content).hexdigest(),'records':len(rows)})
   for r in rows:
    n=r['organisasjonsnummer']
    if valid(n) and n not in excluded:records[n]=r['navn']
   time.sleep(.2)
 selected=rng.sample(sorted(records),100)
 content='\n'.join(selected+['NOT-AN-ORGNR','123456789','   '])+'\n'
 (out/'orgnrs.txt').write_text(content,encoding='utf-8',newline='\n')
 (out/'selection.json').write_text(json.dumps({'selection':'SystemRandom sample from eight random accessible BRREG pages (page 1..99; API search-result window)','pages':pages,'excluded_identifier_count':len(excluded),'overlap_with_known':len(set(selected)&excluded),'eligible_records':len(records),'input_sha256':hashlib.sha256(content.encode()).hexdigest(),'companies':[{'organisation_number':n,'name':records[n]} for n in selected]},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps({'selected':100,'invalid':3,'eligible':len(records),'excluded':len(excluded),'input_sha256':hashlib.sha256(content.encode()).hexdigest()}))
if __name__=='__main__':main()
