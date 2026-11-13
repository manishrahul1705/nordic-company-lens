"""Prepare complete special-source and fixed random precision-review ledgers."""
import hashlib,json,random,sys
from collections import Counter,defaultdict
from functools import lru_cache
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from signalpost.sources.text import decode_body
from signalpost.web.html import Page
from signalpost.web.proof import orgnrs
ROOT=Path(__file__).resolve().parents[1];CLONE=ROOT/'bench/cache/final-precision-clone';OUT=ROOT/'bench/reports/final-precision';SEED=20261112

def rows(p):
 with p.open(encoding='utf8') as f:
  for line in f:
   if line.strip():yield json.loads(line)
@lru_cache(maxsize=32)
def source(sha):
 body=(CLONE/'out/state/blobs'/sha).read_bytes();assert hashlib.sha256(body).hexdigest()==sha
 return decode_body(body)
def evidence(e):
 text=source(e['content_sha256']);assert e['claim_span'] in text
 located=None
 try:
  located=json.loads(text)
  for key in e['locator'].strip('/').split('/'):
   if not key:continue
   key=key.replace('~1','/').replace('~0','~')
   located=located[int(key)] if isinstance(located,list) else located[key]
 except (ValueError,KeyError,TypeError,IndexError):located=None
 return {**e,'located_source_value':located if len(json.dumps(located,ensure_ascii=False))<2200 else str(located)[:1500]}
def main():
 snapshots={n:list(rows(CLONE/f'validation/run{n}/envelopes.jsonl')) for n in (1,2)}
 special={};pools=defaultdict(list);briefs=[];coverage=[]
 for n,batch in snapshots.items():
  counts=Counter();valid=[r for r in batch if r['run']['sections']['identity']=='available']
  for row in valid:
   org=row['organisation_number'];claims=[c for c in row['claims'] if c['availability']=='available' and c['value'] is not None];name=next(c['value'] for c in claims if c['field']=='identity.legal_name');ev={e['id']:e for e in row['evidence']}
   def item(c):
    refs=[ev[x] for x in c['evidence_ids'] if x in ev]
    category='website' if c['field']=='official_website' else 'social' if c['field'].startswith(('social_profile.','registry_social.')) else 'GLEIF' if c['field'].startswith('identity.gleif.') else 'procurement' if c['field'].startswith('procurement_award.') else 'job' if c['field'].startswith(('hiring.job.','hiring.site_job.')) else c['family']
    if category=='website':refs=[e for e in refs if e['source_class']=='company_owned' and e['locator'].startswith('identity-proof:')]
    elif category=='social':refs=([e for e in refs if e['source_class']!='official_registry'] or refs)[:4]
    else:refs=refs[:5]
    record={'run':n,'orgnr':org,'company':name,'category':category,'claim':c,'sources':[evidence(e) for e in refs]}
    if category in {'website','social'}:
     record['registry_contacts']={x['field']:x['value'] for x in claims if x['field'].startswith('identity.registered_') and x['field'] in {'identity.registered_address','identity.registered_phone','identity.registered_mobile','identity.registered_email'}}
     for e in refs:
      if e['source_class']=='company_owned':
       page=Page(source(e['content_sha256']).encode('utf8'),e['source_url']);record['page_title']=page.title;record['owner_numbers']=sorted(orgnrs(page.owner_text));record['saved_page_text']=page.visible[:6500];break
    return record
   for c in claims:
    if c['field']=='official_website' or c['field'].startswith(('social_profile.','registry_social.','identity.gleif.','procurement_award.','hiring.job.','hiring.site_job.')):
     key=(org,c['field'],json.dumps(c['value'],sort_keys=True));record=special.setdefault(key,item(c));record.setdefault('runs',[]).append(n)
    if n==2:
     category= 'registry_announcements' if c['field'].startswith('registry_change.') else c['family']
     if category in {'identity','roles','subunits','accounts','registry_announcements'}:pools[category].append((row,c,item))
   for key,found in [('websites',any(c['field']=='official_website' for c in claims)),('social',any(c['field'].startswith(('social_profile.','registry_social.')) for c in claims)),('jobs',any(c['field'].startswith(('hiring.job.','hiring.site_job.')) for c in claims)),('activity',any(c['family']=='activity' for c in claims)),('GLEIF_companies',any(c['field'].startswith('identity.gleif.') for c in claims)),('procurement_companies',any(c['field'].startswith('procurement_award.') for c in claims))]:counts[key]+=found
  coverage.append({'run':n,'envelopes':len(batch),'valid':len(valid),**counts})
 # Create sample items directly per row; avoid closures retaining the last row.
 samples=[];rng=random.Random(SEED)
 for family,pool in sorted(pools.items()):
  chosen=rng.sample(pool,min(10,len(pool)))
  for row,c,_ in chosen:
   ev={e['id']:e for e in row['evidence']};samples.append({'run':2,'orgnr':row['organisation_number'],'company':next(x['value'] for x in row['claims'] if x['field']=='identity.legal_name'),'category':family,'claim':c,'sources':[evidence(ev[x]) for x in c['evidence_ids'] if x in ev][:4]})
 valid=[r for r in snapshots[2] if r['run']['sections']['identity']=='available']
 for row in rng.sample(sorted(valid,key=lambda r:r['organisation_number']),10):
  claims={c['id']:c for c in row['claims']};ev={e['id']:e for e in row['evidence']};brief=row['run']['synthesis']['analyst_brief'];contexts={c['id']:c for c in brief['context_claims']}
  briefs.append({'orgnr':row['organisation_number'],'company':next(c['value'] for c in row['claims'] if c['field']=='identity.legal_name'),'sentences':[{'text':s['text'],'sentence_type':s['sentence_type'],'citations':[{'claim':claims[cid],'sources':[evidence(ev[e]) for e in claims[cid]['evidence_ids'] if e in ev][:2]} if cid in claims else {'context':contexts[cid]} for cid in s['claim_ids']]} for s in brief['sentences']]})
 for name,value in [('coverage.json',coverage),('special-review-input.json',list(special.values())),('sample-review-input.json',samples),('briefing-review-input.json',briefs)]:
  (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 print(json.dumps({'coverage':coverage,'special_items':dict(Counter(x['category'] for x in special.values())),'samples':dict(Counter(x['category'] for x in samples)),'briefings':len(briefs)},indent=2))
if __name__=='__main__':main()
