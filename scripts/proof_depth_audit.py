"""Offline proof-depth opportunity audit, using retained corrected-live bodies only."""
import json,re,sys
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import unquote,urlsplit,urldefrag
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from signalpost.web.html import Page
from signalpost.web.policy import domain
from r3_analyze import rows
ROOT=Path(__file__).resolve().parents[1];RUN=ROOT/'bench/runs/r3-corrected-live';OUT=ROOT/'bench/reports/proof-depth'
PATTERN=re.compile(r'salgsbetingelser|kjøpsbetingelser|kjopsbetingelser|kjopsvilkar|kjøpsvilkår|vilkår|vilkar|betingelser|personvern(?:erklæring)?|kontakt(?:-oss)?|om-oss|(?:^|[/\s])om(?:[/\s?#]|$)|impressum|terms|privacy',re.I)
MISSING={'insufficient_owner_proof','name_only','name_without_suffix_insufficient_contacts_or_domain'}
def main():
 report=json.loads((RUN/'report.json').read_text(encoding='utf8'));events=defaultdict(list)
 for event in report['request_log']:
  if event.get('section')=='website' and event.get('status')==200 and not event.get('error') and not event.get('truncated') and event.get('content_sha256') and 'robots.txt' not in event['url']:
   events[event['organisation_number']].append(event)
 eligible=[];reasons=Counter();missing_bodies=0
 for row in rows(RUN/'envelopes.jsonl'):
  if row['run']['sections'].get('website')=='available':continue
  name=next((c['value'] for c in row['claims'] if c['field']=='identity.legal_name'),'')
  attempts=[]
  for error in row['errors']:
   if error['section']=='website' and error['code']=='website_candidates':
    try:attempts+=json.loads(error['message'])
    except ValueError:pass
  for candidate in row['run']['refresh'].get('recall_round2',{}).get('candidates',[]):
   if not candidate.get('fetched') or candidate.get('accepted'):continue
   reason=candidate.get('reason','');reasons[reason]+=1
   if reason not in MISSING:continue
   host=candidate['domain'];same=[a for a in attempts if a.get('domain')==host]
   if any(a.get('level') in {'REJECT','BLOCKED'} for a in same):continue
   # Candidate transport failures are separate from a proof-only failure.
   if any(a.get('reason') in {'website_budget_exhausted','budget_exhausted','deadline','robots','robots_unavailable','http_blocked','block_page','website_tls_error','website_connect_error','website_timeout'} for a in same):continue
   pages=[];links={};seen=set();fetched={urldefrag(e['url'])[0] for e in events[row['organisation_number']]}
   for event in events[row['organisation_number']]:
    if domain(event['url'])!=host:continue
    sha=event['content_sha256'];key=(event['url'],sha)
    if key in seen:continue
    seen.add(key);path=RUN/'state/blobs'/sha
    if not path.exists():missing_bodies+=1;continue
    body=path.read_bytes()
    if not re.search(br'<(?:html|!doctype|body|head|footer)\b',body,re.I):continue
    page=Page(body,event['url']);pages.append({'url':event['url'],'sha256':sha})
    for link in page.links:
     target=urldefrag(link.href)[0]
     if urlsplit(target).scheme not in {'http','https'}:continue
     if domain(target)==host and PATTERN.search(unquote(urlsplit(target).path)+' '+link.text):
      links[target]={'url':target,'text':link.text[:160],'already_fetched':target in fetched}
   if pages:eligible.append({'orgnr':row['organisation_number'],'company':name,'domain':host,'reason':reason,'pages':pages,'matching_links':list(links.values())})
 result={'source_run':str(RUN),'scope':'Companies without an available website; fetched non-accepted candidates with explicit missing-proof reason and no recorded veto/policy/transport/budget failure for that domain. Requires a retained successful HTML page. Links are nominations, not proof.','eligible_candidate_sites':len(eligible),'eligible_companies':len({c['orgnr'] for c in eligible}),'sites_with_matching_links':sum(bool(c['matching_links']) for c in eligible),'companies_with_matching_links':len({c['orgnr'] for c in eligible if c['matching_links']}),'sites_with_unfetched_matching_links':sum(any(not l['already_fetched'] for l in c['matching_links']) for c in eligible),'companies_with_unfetched_matching_links':len({c['orgnr'] for c in eligible if any(not l['already_fetched'] for l in c['matching_links'])}),'missing_retained_bodies':missing_bodies,'diagnostic_reasons_before_filter':dict(reasons),'candidates':eligible}
 OUT.mkdir(parents=True,exist_ok=True);(OUT/'audit.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps({k:v for k,v in result.items() if k!='candidates'},indent=2))
if __name__=='__main__':main()
