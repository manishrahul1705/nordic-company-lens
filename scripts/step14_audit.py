"""Audit saved Step14 registry events without further requests."""
import argparse,hashlib,json,random
from collections import Counter
from pathlib import Path
from signalpost.sources.registry_changes import field_label,timestamp,window_start

def rows(path):return [json.loads(l) for l in path.read_text(encoding='utf-8').splitlines()]
def key(r,c):
 v=c['value'];return (r['organisation_number'],v['event_id'],v.get('changed_field'),v.get('subunit_orgnr'))
def main():
 parser=argparse.ArgumentParser();parser.add_argument('run',type=Path);a=parser.parse_args();root=Path(__file__).resolve().parents[1];out=root/'bench/reports/s6-step14';data=rows(a.run/'envelopes.jsonl');old=rows(root/'bench/runs/20261106T125849762180Z-7474c37/envelopes.jsonl')
 previous={key(r,c) for r in old for c in r['claims'] if c['field'].startswith('registry_change.') and c['availability']=='available'}
 events=[(r,c) for r in data for c in r['claims'] if c['field'].startswith('registry_change.') and c['availability']=='available'];new=[x for x in events if key(*x) not in previous]
 distinct=list({(r['organisation_number'],c['value']['event_id']):(r,c) for r,c in new}.values());sample=random.Random(20261106).sample(distinct,min(30,len(distinct)));review=[]
 for r,c in sample:
  v=c['value'];records={e['id']:e for e in r['evidence']};e=next(records[n] for n in c['evidence_ids'] if records[n]['extraction_method']=='registry change feed');body=(a.run/'state/blobs'/e['content_sha256']).read_bytes();assert hashlib.sha256(body).hexdigest()==e['content_sha256'];raw=json.loads(body)
  event=next(x for x in raw['_embedded']['oppdaterteEnheter'] if x['oppdateringsid']==v['event_id']);assert event['organisasjonsnummer']==r['organisation_number']==v['company_orgnr'];assert timestamp(event['dato'])==timestamp(v['date']);assert window_start(timestamp(e['retrieved_at']))<=timestamp(v['date'])<=timestamp(e['retrieved_at']);patch=next(x for x in event['endringer'] if x['path']==v['changed_field'] and x['op']==v['operation']);assert patch.get('value')==v.get('new_value');assert field_label(patch['path'])==v['title'];assert e['claim_span'] in body.decode('utf-8')
  review.append({'organisation_number':r['organisation_number'],'company':next((x['value'] for x in r['claims'] if x['field']=='identity.legal_name'),r['organisation_number']),'claim_id':c['id'],'value':v,'source_url':e['source_url'],'retrieved_at':e['retrieved_at'],'sha256':e['content_sha256'],'claim_span':e['claim_span'],'raw_event':event,'verdict':'pending'})
 (out/'review30.json').write_text(json.dumps(review,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 report=json.loads((a.run/'report.json').read_text(encoding='utf-8'));counts={f:sum(r['run']['sections'].get(f)=='available' for r in data) for f in ['identity','roles','subunits','accounts','activity','hiring']};counts['website']=sum(any(c['field']=='official_website' and c['availability']=='available' for c in r['claims']) for r in data);counts['social']=sum(any(c['field'].startswith(('social_profile.','registry_social.')) and c['availability']=='available' for c in r['claims']) for r in data)
 requests=[x for x in report['request_log'] if '/api/oppdateringer/' in x['url']]
 metrics={'run':str(a.run),'sections':counts,'registry_claims':len(events),'registry_companies':len({r['organisation_number'] for r,c in events}),'new_registry_claims':len(new),'new_registry_companies':len({r['organisation_number'] for r,c in new}),'registry_http':len(requests),'registry_http_statuses':dict(Counter(str(x.get('status')) for x in requests)),'labels':dict(Counter(c['value']['title'] for r,c in events)),'total_http':report['requests'],'max_http_per_company':report.get('max_requests_per_company'),'deadlines':report['deadline_hits'],'warnings':report['warnings']}
 (out/'metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(metrics,ensure_ascii=False));
 for x in review:print(json.dumps({k:x[k] for k in ['organisation_number','company','value','raw_event']},ensure_ascii=False))
if __name__=='__main__':main()
