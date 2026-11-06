"""Saved Step15 comparison and proof inventory; no live requests."""
import argparse,hashlib,json
from collections import Counter
from pathlib import Path
from signalpost.web.policy import domain
from signalpost.web.html import Page
from signalpost.web.proof import orgnrs
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'bench/runs/20261106T142139712906Z-29a30a5';OUT=ROOT/'bench/reports/s6-step15'
def rows(p):return [json.loads(l) for l in p.read_text(encoding='utf-8').splitlines()]
def website(r):return next((c for c in r['claims'] if c['field']=='official_website' and c['availability']=='available'),None)
def socials(r):return {c['value']['url']:c for c in r['claims'] if c['availability']=='available' and c['field'].startswith(('social_profile.','registry_social.'))}
def summary(rs):
 d={k:sum(r['run']['sections'].get(k)=='available' for r in rs) for k in ['identity','roles','subunits','accounts','activity','hiring']};d['website']=sum(website(r) is not None for r in rs);d['social']=sum(bool(socials(r)) for r in rs);return d

def main():
 ap=argparse.ArgumentParser();ap.add_argument('run',type=Path);a=ap.parse_args();run=a.run
 old={r['organisation_number']:r for r in rows(BASE/'envelopes.jsonl')};new=rows(run/'envelopes.jsonl');items=[];loss=[];funnel=Counter();accepted=Counter();kept=Counter()
 for r in new:
  org=r['organisation_number'];before=old[org];site=website(r);oldsite=website(before);evidence={e['id']:e for e in r['evidence']};records=r['run']['refresh'].get('recall_round2',{}).get('candidates',[])
  for rec in records:
   lever='E' if rec['origin']=='registry_email' else 'B' if rec['origin'] in {'legal_name_slug','subunit_name_slug'} else 'existing'
   funnel[lever+'_candidates']+=1;funnel[lever+'_fetched']+=bool(rec.get('fetched'));accepted[lever]+=bool(rec.get('accepted'));funnel['C_pages_fetched']+=rec.get('proof_pages_fetched',0)
  additions=[]
  if site and (oldsite is None or site['value']!=oldsite['value']):additions.append(('website',site))
  additions += [('social',c) for url,c in socials(r).items() if url not in socials(before)]
  if oldsite and not site:loss.append({'organisation_number':org,'company':next((c['value'] for c in r['claims'] if c['field']=='identity.legal_name'),org),'previous_site':oldsite['value'],'current_state':r['run']['sections']['website'],'errors':[e for e in r['errors'] if e['section']=='website'],'diagnostics':r['run']['refresh'].get('recall_round2')})
  if site:
   origin=site['value']['candidate_origin'];kept['E' if origin=='registry_email' else 'B' if origin in {'legal_name_slug','subunit_name_slug'} else 'existing']+=1
   if site['value']['proof_type']=='raw_owner_identifier':kept['D']+=1
   if site['value'].get('proof_page_url','').rstrip('/')!=site['value']['final_url'].rstrip('/'):kept['C']+=1
  for kind,c in additions:
   refs=[evidence[i] for i in c['evidence_ids'] if evidence[i]['source_class'] in {'company_owned','wikidata'}];seen=set();proofs=[]
   for e in refs:
    key=(e['source_url'],e['content_sha256'])
    if key in seen:continue
    seen.add(key);body=(run/'state/blobs'/e['content_sha256']).read_bytes();assert hashlib.sha256(body).hexdigest()==e['content_sha256'];p=Page(body,e['source_url']);assert e['claim_span'] in body.decode('utf-8',errors='replace')
    proofs.append({'url':e['source_url'],'sha256':e['content_sha256'],'span':e['claim_span'],'title':p.title,'visible':' '.join(p.visible.split())[:12000],'footer':' '.join(p.footer_parts).strip()[:5000],'owner_orgnrs':sorted(orgnrs(p.owner_text))})
   values={c['field']:c['value'] for c in r['claims'] if c['availability']=='available'}
   items.append({'organisation_number':org,'company':values.get('identity.legal_name'),'kind':kind,'new_company_website':kind=='website' and oldsite is None,'value':c['value'],'previous_value':oldsite['value'] if oldsite and kind=='website' else None,'claim_id':c['id'],'registry':{k:values.get(k) for k in ['identity.registered_website','identity.registered_email','identity.registered_phone','identity.registered_address']},'proofs':proofs,'verdict':'pending'})
 report=json.loads((run/'report.json').read_text(encoding='utf-8'));metrics={'run':str(run),'before':summary(list(old.values())),'after':summary(new),'http':report['requests'],'mean_attributed':report['requests_per_company'],'mean_amortized':report['amortized_requests_per_company'],'max_company':report['max_requests_per_company'],'deadlines':report['deadline_hits'],'warnings':report['warnings'],'funnel':dict(funnel),'accepted_before_final_guard':dict(accepted),'kept_by_lever_overlapping':dict(kept),'new_company_websites':sum(x['new_company_website'] for x in items),'new_social_urls':sum(x['kind']=='social' for x in items),'changed_website_values':sum(x['kind']=='website' and not x['new_company_website'] for x in items)}
 for name,data in [('metrics.json',metrics),('new-items.json',items),('losses.json',loss)]: (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 print(json.dumps(metrics,indent=2));print('review_items',len(items),'losses',len(loss))
if __name__=='__main__':main()
