"""Explain release refresh differences from unchanged saved outputs only."""
import json
from pathlib import Path
from r3_analyze import rows
ROOT=Path(__file__).resolve().parents[1];CLONE=ROOT/'bench/cache/r3-corrected-release';OUT=ROOT/'bench/reports/r3-benchmark/live-verification'
def main():
 old={r['organisation_number']:r for r in rows(CLONE/'validation/run1/envelopes.jsonl')};differences=[]
 reports=[json.loads((CLONE/f'validation/run{n}/report.json').read_text(encoding='utf8')) for n in (1,2)]
 for r in rows(CLONE/'validation/run2/envelopes.jsonl'):
  prior=old[r['organisation_number']];before={c['id'] for c in prior['claims']};after={c['id'] for c in r['claims']}
  if before==after:continue
  item={'orgnr':r['organisation_number'],'company':next((c['value'] for c in r['claims'] if c['field']=='identity.legal_name'),''),'observation_changes':r['run']['refresh'].get('observation_changes',[]),'removed_fields':[c['field'] for c in prior['claims'] if c['id'] not in after],'added_claims':[{'field':c['field'],'value':c['value']} for c in r['claims'] if c['id'] not in before],'relevant_requests':[]}
  for n,report in enumerate(reports,1):
   for event in report['request_log']:
    if event['organisation_number']==r['organisation_number'] and 'kontakt' in event['url']:
     item['relevant_requests'].append({'run':n,**{k:event.get(k) for k in ('url','status','error','exception_message','content_sha256')}})
  differences.append(item)
 result={'company_changes':sum(len(r['changes']) for r in rows(CLONE/'validation/run2/envelopes.jsonl')),'strict_pair_status':'FAIL: Claim IDs differ','observation_changes':sum(len(r['run']['refresh'].get('observation_changes',[])) for r in rows(CLONE/'validation/run2/envelopes.jsonl')),'differences':differences,'cause':'A.U. Bygg supporting contact page timed out in run 1, succeeded in run 2. Five newly checked supporting facts are correctly labelled observations; original outputs and strict verifier were not changed.'}
 (OUT/'release-diagnosis.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(result,ensure_ascii=True,indent=2))
if __name__=='__main__':main()
