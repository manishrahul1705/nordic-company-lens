"""Controlled extraction replay: the same 1,000 companies and saved pages, zero HTTP.

Evidence blobs remain in the immutable Stage AG state directory. No original
envelope, response or report is rewritten.
"""
import hashlib
import json
from pathlib import Path
import time
from collections import Counter,defaultdict
from datetime import datetime,timedelta
from signalpost.models.envelope import Envelope,CompactProfile
from signalpost.models.evidence import digest
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.http import Response
from signalpost.sources.extract import Section
from signalpost.web.html import Page
from signalpost.web.policy import domain
from signalpost.web.social import attributed,observed_profiles,drop_shared,context_for_envelope,profile_key
from signalpost.web.collector import publish
from signalpost.synthesis.cohort import build_index,context as cohort_context
from signalpost.synthesis.template import generate
from signalpost.models.shapes import serialize

base=Path('bench/runs/stage-ag-20261119')
out=Path('bench/runs/social-universe-veto-20261120')
reports=Path(__file__).parent
out.mkdir(parents=True,exist_ok=True)
start=time.perf_counter()
source_hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in Path('src').rglob('*.py')}
report=json.loads((base/'report.json').read_text(encoding='utf-8'))
events=defaultdict(list)
for event in report['request_log']:
    if event.get('status')==200 and event.get('content_sha256'):
        events[event['organisation_number']].append(event)
rows=[];before={};scanned=Counter();candidate_records=[];pages_count=0
blobs=BlobStore(base/'state')
for line in (base/'envelopes.jsonl').open(encoding='utf-8'):
    row=Envelope.model_validate(json.loads(line));org=row.organisation_number
    before[org]={profile_key(c.value['url']):c.model_dump() for c in row.claims
                 if c.field.startswith('social_profile.') and c.availability=='available'}
    proof=next((c for c in row.claims if c.field=='official_website' and c.availability=='available'
                and c.value.get('identity_level')=='VERIFIED'),None)
    if proof:
        context=context_for_envelope(row);section=Section()
        checked=set(row.run.refresh.get('website',{}).get('checked_urls',[]))
        known=set(before[org]);seen=set()
        for event in events[org]:
            url=event['url']
            if url not in checked or url in seen or domain(url)!=domain(proof.value['final_url']):continue
            seen.add(url);raw=(base/'state/blobs'/event['content_sha256']).read_bytes()
            page=Page(raw,url);pages_count+=1
            observed=row.run.refresh.setdefault('website',{}).setdefault('observed_social_profiles',[])
            row.run.refresh['website']['observed_social_profiles']=sorted(set(observed)|observed_profiles(page))
            from signalpost.web.entity_scope import foreign_entity_page
            if foreign_entity_page(page,org,context['name'],check_ids=not bool(proof.value.get('other_orgnrs'))):continue
            retained=next((e.retrieved_at for e in row.evidence if e.content_sha256==event['content_sha256']),None)
            if retained is None:
                began=datetime.fromisoformat(row.run.started_at.replace('Z','+00:00'))
                retained=(began+timedelta(seconds=event['attempt_started']+event.get('runtime_ms',0)/1000)).isoformat().replace('+00:00','Z')
            response=Response(raw,200,url,retained,event['content_sha256'])
            for target,span in attributed(page,proof.value,context).items():
                key=profile_key(target)
                if key in known:continue
                publish(section,response,org,'social_profile.'+digest(target)[:20],
                        {'url':target,'platform':domain(target)},'company-link:'+target,span)
                section.claims[-1].reasons['relationship']='Profile linked on ownership-proven company page; person/cohort/shared/group vetoes apply'
                known.add(key)
                candidate_records.append({'organisation_number':org,'name':context['name'],'url':target,'page':url})
        row.claims.extend(section.claims)
        ev={e.id:e for e in row.evidence};ev.update({e.id:e for e in section.evidence});row.evidence=list(ev.values())
    rows.append(row)
print('Replayed saved pages:',pages_count,'candidate profiles:',len(candidate_records),flush=True)
drop_shared(rows,blobs)
from signalpost.web.entity_scope import enforce
enforce(rows,blobs,{})
cohort=build_index(rows)
changes=[];removed=[];platform_before=defaultdict(set);platform_after=defaultdict(set)
companies_before=defaultdict(set);companies_after=defaultdict(set)
for row in rows:
    org=row.organisation_number
    for old in before[org].values():
        platform=domain(old['value']['url']);platform='x.com' if platform=='twitter.com' else platform
        platform_before[platform].add((org,profile_key(old['value']['url'])));companies_before[platform].add(org)
    current={profile_key(c.value['url']):c for c in row.claims if c.field.startswith('social_profile.') and c.availability=='available'}
    ev={e.id:e for e in row.evidence}
    for key,c in current.items():
        platform=domain(c.value['url']);platform='x.com' if platform=='twitter.com' else platform
        platform_after[platform].add((org,key));companies_after[platform].add(org)
        if key not in before[org]:
            proof=next(c for c in row.claims if c.field=='official_website' and c.availability=='available')
            changes.append({'organisation_number':org,'company':next(c.value for c in row.claims if c.field=='identity.legal_name'),
                            'claim':c.model_dump(),'evidence':[ev[ref].model_dump() for ref in c.evidence_ids],
                            'website_proof':proof.model_dump(),
                            'role_person_names':context_for_envelope(row).get('role_person_names',[])})
    for key,old in before[org].items():
        if key not in current:removed.append({'organisation_number':org,'claim':old})
    row.run.legal_identity={c.field.removeprefix('identity.'):c.value for c in row.claims if c.family=='identity'}
    row.profile=CompactProfile(organisation_number=org,values={c.field:c.value for c in row.claims},evidence_ids=[e.id for e in row.evidence])
    row.run.synthesis=generate(row,cohort_context(row,cohort));row.profile.synthesis=row.run.synthesis
with (out/'envelopes.jsonl').open('w',encoding='utf-8') as output:
    for row in rows:output.write(json.dumps(serialize(row,'union'),ensure_ascii=False,separators=(',',':'))+'\n')
report['replay']={'baseline':str(base),'network_requests_made':0,'same_saved_acquisition_requests':report['requests'],
                  'pages_reprocessed':pages_count,'kind':'Post-collection extraction replay, no HTTP or site rebuild'}
report['replay']['baseline_finalisation']=report.pop('finalisation',{})
report['site']={'state':'skipped','reason':'saved-page extraction replay; offline site not rebuilt'}
(out/'report.json').write_text(json.dumps(report,ensure_ascii=False),encoding='utf-8')
summary={'baseline':str(base),'replay':str(out),'companies':len(rows),'new_http_requests':0,
         'acquisition_requests_before':report['requests'],'acquisition_requests_after':report['requests'],
         'pages_reprocessed':pages_count,'new_profiles':len(changes),'removed_profiles':removed,
         'platforms':{platform:{'before_companies':len(companies_before[platform]),'before_claims':len(platform_before[platform]),
                                'after_companies':len(companies_after[platform]),'after_claims':len(platform_after[platform])}
                      for platform in sorted(set(platform_before)|set(platform_after))},
         'companies_with_social_before':sum(bool(before[org]) for org in before),
         'companies_with_social_after':sum(any(c.field.startswith('social_profile.') and c.availability=='available' for c in row.claims) for row in rows),
         'replay_seconds':round(time.perf_counter()-start,3),'source_sha256':source_hashes}
(reports/'measurement.json').write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding='utf-8')
(reports/'new-profiles.json').write_text(json.dumps(changes,indent=2,ensure_ascii=False),encoding='utf-8')
(reports/'candidate-profiles.json').write_text(json.dumps(candidate_records,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:v for k,v in summary.items() if k not in {'source_sha256','removed_profiles'}},indent=2),flush=True)
