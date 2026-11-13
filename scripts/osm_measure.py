"""Offline PBF/bulk joins and bounded live ownership measurement. Not agent code."""
import csv,hashlib,json,random,socket,time
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from urllib.parse import urlsplit,urljoin
from urllib.robotparser import RobotFileParser
import httpx
from osm_check import ROOT,OUT,RAW,textfile,org,dump
from signalpost.config import Config
from signalpost.identity.orgnr import valid
from signalpost.web.candidates import Candidate
from signalpost.web.collector import candidate_proof,proof_page_targets
from signalpost.web.html import Page
from signalpost.web.policy import domain,normalize_url,validate_url,check_ips

CONFIG=Config(organisations=ROOT/'bench/inputs/100/batch.jsonl',output=RAW/'unused.jsonl',report=RAW/'unused-report.json')
UA=CONFIG.website_user_agent
class Live:
 def __init__(self):
  self.client=httpx.Client(headers={'User-Agent':UA},verify=True,follow_redirects=False,trust_env=False)
  self.last={};self.robots={};self.requests=[];self.delay={}
 def get(self,url,root,robots=False):
  for hop in range(6):
   url=validate_url(url,{root});parts=urlsplit(url);host=parts.hostname
   check_ips([x[4][0] for x in socket.getaddrinfo(host,parts.port or (443 if parts.scheme=='https' else 80),type=socket.SOCK_STREAM)])
   if not robots:self.allow(url,root)
   time.sleep(max(0,self.delay.get(host,1.01)-(time.monotonic()-self.last.get(host,0))))
   self.last[host]=time.monotonic();entry={'url':url,'robots':robots,'at_monotonic':self.last[host]};self.requests.append(entry)
   with self.client.stream('GET',url,timeout=httpx.Timeout(30,connect=15)) as r:
    entry['status']=r.status_code
    if r.is_redirect:
     target=urljoin(url,r.headers['Location'])
     if parts.scheme=='https' and urlsplit(target).scheme!='https':raise ValueError('TLS downgrade refused')
     url=target;continue
    content=[];size=0
    for chunk in r.iter_bytes():
     content.append(chunk);size+=len(chunk)
     if size>4_000_000:raise ValueError('body exceeds 4MB limit')
    return r.status_code,url,b''.join(content)
  raise ValueError('redirect limit')
 def allow(self,url,root):
  parts=urlsplit(url);origin=parts.scheme+'://'+parts.netloc
  if origin not in self.robots:
   status,_,body=self.get(origin+'/robots.txt',root,robots=True)
   if status not in {200,404,410}:raise ValueError('robots unavailable/blocked')
   rp=RobotFileParser();rp.parse(body.decode('utf8',errors='replace').splitlines() if status==200 else [])
   self.robots[origin]=rp
   wait=rp.crawl_delay(UA) or rp.crawl_delay('*') or 0
   rate=rp.request_rate(UA) or rp.request_rate('*')
   self.delay[parts.hostname]=max(1.01,float(wait),rate.seconds/rate.requests if rate else 0)
  if not self.robots[origin].can_fetch(UA,url):raise ValueError('robots disallow')

def unit_context(row):
 prefix='beliggenhetsadresse.'
 street=row.get(prefix+'adresse') or ''
 try:street=json.loads(street) if street.startswith('[') else street
 except ValueError:pass
 return {'orgnr':row['organisasjonsnummer'],'name':row.get('navn'),'email':row.get('epostadresse'),'phone':row.get('telefon') or row.get('mobil'),'website':row.get('hjemmeside'),'address':{'adresse':street,'postnummer':row.get(prefix+'postnummer'),'poststed':row.get(prefix+'poststed'),'kommune':row.get(prefix+'kommune')}}

def main():
 start=time.monotonic()
 objects=[json.loads(line) for line in (OUT/'objects.jsonl').read_text(encoding='utf8').splitlines() if line.strip()]
 valid_objects=[e for e in objects if valid(e['orgnr'].strip())]
 for e in valid_objects:e['orgnr']=e['orgnr'].strip()
 wanted={e['orgnr'] for e in valid_objects};parents={};units={}
 csv.field_size_limit(10_000_000)
 with textfile(RAW/'subunits.csv.download') as f:
  sample=f.read(32768);f.seek(0);reader=csv.DictReader(f,dialect=csv.Sniffer().sniff(sample,delimiters=';,\t'))
  for row in reader:
   if row['organisasjonsnummer'] in wanted:
    parent=row['overordnetEnhet'];assert valid(parent)
    parents[row['organisasjonsnummer']]=parent;units[row['organisasjonsnummer']]=unit_context(row)
 candidates=[]
 for e in valid_objects:
  if e['website']:
   n=e['orgnr'];candidates.append({**e,'tagged_orgnr':n,'parent_orgnr':parents.get(n,n),'is_subunit':n in parents,'osm_url':f"https://www.openstreetmap.org/{e['type']}/{e['id']}"})
 with (OUT/'candidates.jsonl').open('w',encoding='utf8') as f:
  for row in candidates:f.write(json.dumps(row,ensure_ascii=False)+'\n')
 with textfile(RAW/'universe.jsonl.gz') as f:universe={org(row):row for line in f if line.strip() for row in [json.loads(line)]}
 parent_set={c['parent_orgnr'] for c in candidates};matched=sorted(parent_set&universe.keys())
 batch={org(json.loads(line)) for line in (ROOT/'bench/inputs/100/batch.jsonl').read_text(encoding='utf8').splitlines() if line.strip()}
 selected=random.Random(20261111).sample(matched,min(20,len(matched)))
 summary={'status':'live_review_running','source':'Geofabrik Norway PBF','pbf':json.loads((OUT/'pbf-manifest.json').read_text(encoding='utf8')),
 'licences':{'osm':{'licence':'ODbL 1.0','attribution':'\u00a9 OpenStreetMap contributors','url':'https://www.openstreetmap.org/copyright'},'brreg_subunit_bulk':{'licence':'NLOD 2.0','attribution':'Br\u00f8nn\u00f8ysundregistrene','url':'https://data.brreg.no/enhetsregisteret/api/underenheter/lastned/csv'},'builderr_universe':{'licence':'Not stated in downloaded JSONL; challenge input, no redistribution of raw file','url':'https://builderr.ai/signalpost-company-universe-2025.jsonl.gz'}},
 'future_in_agent_use':'Any future in-agent use needs a bundled ODbL-licensed index; integration and licensing design remain to be decided. No production integration performed.',
 'objects_with_orgnr_tag':len(objects),'objects_with_orgnr_and_website_before_checksum':sum(bool(e['website']) for e in objects),'objects_with_valid_orgnr':len(valid_objects),'invalid_orgnr_objects_excluded':len(objects)-len(valid_objects),'objects_with_valid_orgnr_and_website':len(candidates),'objects_with_subunit_orgnr':sum(e['orgnr'] in parents for e in valid_objects),'website_objects_with_subunit_orgnr':sum(c['is_subunit'] for c in candidates),'subunit_share_of_website_objects':sum(c['is_subunit'] for c in candidates)/len(candidates) if candidates else None,'subunit_share_of_valid_objects':sum(e['orgnr'] in parents for e in valid_objects)/len(valid_objects) if valid_objects else None,'distinct_subunit_numbers':len(parents),'distinct_parent_companies_with_website':len(parent_set),'universe':{'distinct_companies':len(universe),'companies_with_osm_website':len(matched),'expected_per_1000':1000*len(matched)/len(universe),'method':'1000 * matched distinct parents / 411160 universe companies; nomination coverage, not verified or incremental agent coverage'},'batch100_match_count':len(batch&parent_set),'batch100_matches':sorted(batch&parent_set),'categories':dict(Counter((c['category'] or {}).get('key','none') for c in candidates))}
 dump(OUT/'summary.json',summary);print('Counts',json.dumps({k:v for k,v in summary.items() if k not in {'pbf','licences'}},ensure_ascii=True),flush=True)
 review_path=OUT/'live-review.json';reviews=json.loads(review_path.read_text(encoding='utf8')) if review_path.exists() else []
 previous={r['orgnr'] for r in reviews};live=Live()
 for n in selected:
  if n in previous:continue
  c=next(c for c in candidates if c['parent_orgnr']==n)
  company_units=[u for unit,u in units.items() if parents[unit]==n]
  context={'name':universe[n]['name'],'subunits':company_units,'allowed_orgnrs':{n,*[u['orgnr'] for u in company_units]}}
  item={'orgnr':n,'name':context['name'],'candidate':c,'context':{**context,'allowed_orgnrs':sorted(context['allowed_orgnrs'])},'pages':[],'passes':False}
  try:
   url=normalize_url(c['website']);root=domain(url) if url else ''
   if not root:raise ValueError('invalid candidate URL')
   # OSM only nominates; never mark it as registry-declared or ownership evidence.
   candidate=Candidate(url,root,'osm',c['tagged_orgnr'] if c['is_subunit'] else None)
   targets=[url];pages=[]
   for index in range(3):
    if index>=len(targets):break
    target=targets[index];record={'requested_url':target};item['pages'].append(record)
    try:
     status,final,body=live.get(target,root);record.update(status=status,url=final)
     if status!=200:raise ValueError('HTTP '+str(status))
     digest=hashlib.sha256(body).hexdigest();(RAW/(digest+'.html')).write_bytes(body)
     page=Page(body,final);proof=candidate_proof(page,n,context,candidate,[],CONFIG);pages.append((page,proof))
     record.update(body_sha256=digest,title=page.title,proof=asdict(proof),proof_excerpt=page.proof_span(proof.subject_orgnr or n) or page.name_span(proof.token) or page.span_for(proof.token))
     if index==0:
      targets.extend(t for t in proof_page_targets(page,final,limit=2) if t not in targets)
    except Exception as e:record['error']=f'{type(e).__name__}: {e}'
   conflicts=any(p.level=='REJECT' and (p.other_orgnrs or p.reason in {'foreign_orgnr','different_legal_entity'}) for _,p in pages)
   item['passes']=any(p.level=='VERIFIED' for _,p in pages) and not conflicts
   item['owner_conflict']=conflicts
  except Exception as e:item['error']=f'{type(e).__name__}: {e}'
  reviews.append(item);dump(review_path,reviews);dump(OUT/'live-requests.json',live.requests)
  print('Reviewed',len(reviews),n,item['passes'],flush=True)
 live.client.close()
 summary['status']='complete';summary['live_review']={'seed':20261111,'sample_size':len(reviews),'passed':sum(r['passes'] for r in reviews),'user_agent':UA,'max_proof_pages':2,'per_host_min_spacing_seconds':1.01,'proof':'Unchanged candidate_proof with current Config defaults, OSM origin (no declaration trust), parent identity plus official mapped subunit identity/contact. Any checked owner conflict vetoes pass.','contact_limit':'Only permitted source files used: parent legal name from universe, registered subunit contacts from cached official bulk. Parent contact data absent from these sources is not inferred; this can undercount name+parent-contact proof.','scope':'One first OSM candidate per randomly sampled parent, homepage plus up to two same-site proof pages, robots and public-address checks, TLS verified, redirects same registrable domain only. HTTP pages explicitly recorded; proof pass is not full collector/publication acceptance. Errors count as non-passes.'}
 summary['mapping_limit']='Numbers absent from cached current subunit bulk remain unmapped and treated as putative parents; no main-entity status is inferred.'
 summary['wall_seconds']=time.monotonic()-start;dump(OUT/'summary.json',summary)
 print('Final',json.dumps(summary['live_review'],ensure_ascii=True),flush=True)
if __name__=='__main__':main()
