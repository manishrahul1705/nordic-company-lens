"""Measurement-only R3 counts and evidence review extraction."""
import argparse,json
from collections import Counter
from pathlib import Path


def rows(path):
    with path.open(encoding='utf8') as f:
        for line in f:
            if line.strip():yield json.loads(line)


def summarize(run):
    report=json.loads((run/'report.json').read_text(encoding='utf8'))
    execution=json.loads((run/'execution.json').read_text(encoding='utf8'))
    companies={};facts=0;states={};counts=Counter()
    for row in rows(run/'envelopes.jsonl'):
        org=row['organisation_number'];claims=[c for c in row['claims'] if c.get('availability')=='available' and c.get('value') is not None]
        facts+=len({(c['field'],json.dumps(c['value'],sort_keys=True,ensure_ascii=True),json.dumps(c.get('reporting_period'),sort_keys=True)) for c in claims})
        name=next((c['value'] for c in claims if c['field']=='identity.legal_name'),'')
        evidence={e['id']:e for e in row['evidence']}
        def record(c):
            refs=[evidence[e] for e in c['evidence_ids'] if e in evidence]
            if c['field']=='official_website':
                refs=[e for e in refs if e.get('source_class')=='company_owned' and e.get('locator','').startswith('identity-proof:')]
            elif c['field'].startswith('social_profile.'):
                refs=[e for e in refs if e.get('source_class')=='company_owned' and e.get('locator','').startswith('company-link:')]
            else:
                refs=refs[:5]
            return {'value':c['value'],'field':c['field'],'evidence':refs}
        site=next((record(c) for c in claims if c['field']=='official_website'),None)
        social=[record(c) for c in claims if c['field'].startswith(('social_profile.','registry_social.'))]
        jobs=[record(c) for c in claims if c['field'].startswith(('hiring.job.','hiring.site_job.'))]
        activity=[c for c in claims if c.get('family')=='activity']
        for key,items in (('websites',site),('social_companies',social),('jobs',jobs),('activity',activity)):
            counts[key]+=bool(items)
        for family,state in row['run']['sections'].items():states.setdefault(family,Counter())[state]+=1
        companies[org]={'orgnr':org,'company':name,'website':site,'social':social,'jobs':jobs,'sections':row['run']['sections'],'errors':row.get('errors',[]),'website_diagnostics':row['run'].get('refresh',{}).get('website',{}),'candidate_diagnostics':row['run'].get('refresh',{}).get('recall_round2',{}),'registry_contacts':{c['field']:c['value'] for c in claims if c['field'].startswith('identity.registered_')}}
    profile_orgs=[r['organisation_number'] for r in rows(run/'profiles.jsonl')]
    assert profile_orgs==list(companies)
    result={**counts,'facts':facts,'envelopes':len(companies),'profiles':len(profile_orgs),'http_total':report['requests'],'http_mean':report['amortized_requests_per_company'],'http_attributed_mean':report['requests_per_company'],'http_max':report['max_requests_per_company'],'wall_seconds':execution['wall_seconds'],'deadline_hits':report['deadline_hits'],'warnings':report['warnings'],'site_warnings':[w for w in report['warnings'] if 'site' in str(w).lower()],'exit_code':execution['exit_code'],'commit':execution['commit'],'states':states}
    return result,companies


def main():
    p=argparse.ArgumentParser();p.add_argument('--baseline',type=Path,required=True);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args()
    a,old=summarize(args.baseline);b,new=summarize(args.candidate)
    assert set(old)==set(new)
    added=[];lost=[];social=[];changed=[]
    for org,item in new.items():
        prior=old[org]
        if item['website'] and not prior['website']:added.append(item)
        if prior['website'] and not item['website']:lost.append({'baseline':prior,'candidate':item})
        if item['website'] and prior['website'] and item['website']['value']['final_url']!=prior['website']['value']['final_url']:changed.append({'baseline':prior,'candidate':item})
        previous={c['value']['url'] for c in prior['social']}
        additions=[c for c in item['social'] if c['value']['url'] not in previous]
        if additions:social.append({**item,'social':additions,'new_social_company':not prior['social']})
    proof=Counter(c['website']['value']['proof_type'] for c in added)
    source=Counter(c['website']['value'].get('candidate_origin','unknown') for c in added)
    result={'baseline':a,'candidate':b,'new_websites':len(added),'new_social_companies':sum(c['new_social_company'] for c in social),'new_social_profiles':sum(len(c['social']) for c in social),'lost_websites':len(lost),'changed_websites':len(changed),'new_websites_by_proof':proof,'new_websites_by_source':source}
    args.output.mkdir(parents=True,exist_ok=True)
    for name,value in [('summary.json',result),('website-review.json',added),('social-review.json',social),('lost-websites.json',lost),('changed-websites.json',changed)]:
        (args.output/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
