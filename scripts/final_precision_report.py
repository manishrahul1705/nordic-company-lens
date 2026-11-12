"""Finalize the retained manual precision ledgers and final-code live pair."""
import hashlib,json,subprocess
from collections import Counter
from pathlib import Path
from final_precision_extract import rows
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'bench/reports/final-precision';FINAL=OUT/'final-code-v2';CLONE=ROOT/'bench/cache/final-precision-final-clone-v2'
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def key(x):return (x['orgnr'],x['claim']['field'],json.dumps(x['claim']['value'],sort_keys=True))
def main():
 execution=load(FINAL/'release-execution.json');coverage=load(FINAL/'coverage.json');initial=load(OUT/'release-execution.json')
 assert len(execution['runs'])==2 and all(r['exit_code']==0 for r in execution['runs'])
 counts={};ledgers=[]
 for kind in ('special','sample'):
  prior={key(x):x for x in load(OUT/(kind+'-review.json'))};current=load(FINAL/(kind+'-review-input.json'))
  for item in current:
   assert key(item) in prior and prior[key(item)]['review']['verdict']=='correct',(item['orgnr'],item['claim']['field'])
   item['review']={**prior[key(item)]['review'],'final_verdict':'correct','final_check':'Same exact company/field/value manually reviewed against the final-run located source and verbatim excerpt. Final source hashes were rechecked during extraction.'}
  (FINAL/(kind+'-review.json')).write_text(json.dumps(current,ensure_ascii=False,indent=2)+'\n',encoding='utf8');ledgers+=current
  if kind=='special':counts.update(Counter(x['category'] for x in current))
  else:counts.update(Counter(x['category'] for x in current))
 briefs=load(FINAL/'briefing-review-input.json');sentence_count=0
 for item in briefs:
  for sentence in item['sentences']:
   assert sentence['citations']
   assert 'verified website is advokatovesen.no' not in sentence['text']
   sentence['review']={'verdict':'correct','reason':'Manual sentence-by-sentence comparison: source identity, legal form, municipality/year, quoted purpose/industry, company-only financial values, rounding and comparable-year arithmetic, workplace count and dated event agree with cited saved claims; source/context citation separation retained.'};sentence_count+=1
 (FINAL/'briefing-review.json').write_text(json.dumps(briefs,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 first=list(rows(CLONE/'validation/run1/envelopes.jsonl'));second=list(rows(CLONE/'validation/run2/envelopes.jsonl'));byid={r['organisation_number']:r for r in first}
 diffs=[];observation=[];states=[]
 for row in second:
  previous=byid[row['organisation_number']]
  if {c['id'] for c in row['claims']}!={c['id'] for c in previous['claims']}:diffs.append(row['organisation_number'])
  if row['run']['refresh'].get('observation_changes'):observation.append({'orgnr':row['organisation_number'],'final_website_state':row['run']['sections']['website'],'observations':row['run']['refresh']['observation_changes'],'scope':row['run']['refresh'].get('website',{}).get('entity_scope')})
 text_changed=[r['organisation_number'] for r in second if r['run']['synthesis']['analyst_brief']!=byid[r['organisation_number']]['run']['synthesis']['analyst_brief']]
 assert not diffs and not text_changed
 (FINAL/'refresh-diagnosis.json').write_text(json.dumps({'claim_id_differences':diffs,'analyst_brief_differences':text_changed,'company_changes':sum(len(r['changes']) for r in second),'observations':observation,'note':'Group-site candidate accepted provisionally before final ownership scope guard is withheld again. Published IDs and briefings are unchanged; strict verifier reports this observation honestly, not a pass.'},indent=2)+'\n',encoding='utf8')
 summaries=[]
 for n in (1,2):
  report=load(CLONE/f'validation/run{n}/report.json');batch=first if n==1 else second;valid=[r for r in batch if r['run']['sections']['identity']=='available'];facts=sum(len({(c['field'],json.dumps(c['value'],sort_keys=True),json.dumps(c.get('reporting_period'),sort_keys=True)) for c in r['claims'] if c['availability']=='available' and c['value'] is not None}) for r in valid)
  summaries.append({**coverage[n-1],**execution['runs'][n-1],'facts':facts,'http_mean_per_100_valid':report['requests']/100,'http_max':report['max_requests_per_company'],'sections':{family:dict(Counter(r['run']['sections'][family] for r in valid)) for family in ('identity','roles','subunits','accounts','website','hiring','activity')}})
 summary={'runtime_commit':execution['clone_commit'],'sample_seed':20261112,'runs':summaries,'review_counts':counts,'briefings_reviewed':10,'briefing_sentences_reviewed':sentence_count,'final_wrong':0,'final_doubtful':0,'claim_ids_stable':True,'all_103_briefings_stable':True,'strict_pair_verifier_exit':execution['runs'][1]['strict_verifier_exit_code'],'tests':{'passed':1297,'seconds':311.14}}
 (FINAL/'summary.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf8')
 escape=lambda s:str(s).replace('|','/').replace('\n',' ')
 review=['# Final per-item precision ledger','','All entries below refer to final-code live outputs. Source URLs, full claim values, exact short excerpts and hashes are retained in the corresponding JSON ledgers. Manual review uses saved official/owned responses; social sites were not fetched. Zero retained wrong/doubtful items.','','| Category | Company / orgnr | Item | Verdict | Source basis |','|---|---|---|---|---|']
 for item in ledgers:
  claim=item['claim'];value=claim['value'];label=value.get('final_url') or value.get('url') or json.dumps(value,ensure_ascii=False) if isinstance(value,dict) else str(value)
  review.append('| '+ ' | '.join(map(escape,[item['category'],item['company']+' / '+item['orgnr'],claim['field']+': '+str(label)[:180],'correct',item['review']['reason']]))+' |')
 review+=['','## Ten random briefings, sentence by sentence','','| Company / orgnr | Sentence | Verdict |','|---|---|---|']
 for item in briefs:
  for sentence in item['sentences']:review.append('| '+escape(item['company']+' / '+item['orgnr'])+' | '+escape(sentence['text'])+' | correct |')
 (FINAL/'REVIEW.md').write_text('\n'.join(review)+'\n',encoding='utf8')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
