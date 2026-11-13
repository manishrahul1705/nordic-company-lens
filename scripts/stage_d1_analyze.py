"""Summarize Stage D.1 and extract exact saved evidence for every gain."""
import hashlib,json,sys
from collections import Counter
from pathlib import Path
from r3_analyze import rows,summarize
ROOT=Path(__file__).resolve().parents[1]
NEW=ROOT/'bench/runs/stage-d1-live';OLD=ROOT/'bench/runs/stage-d-live';OUT=ROOT/'bench/reports/stage-d1'
def main():
    a,old=summarize(OLD);b,new=summarize(NEW)
    proof=Counter();funnel=Counter();errors=Counter();new_items=[];lost=[];reserve_sites=[]
    prior={r['organisation_number']:r for r in rows(OLD/'envelopes.jsonl')}
    for row in rows(NEW/'envelopes.jsonl'):
        org=row['organisation_number'];previous=prior[org]
        claims=[c for c in row['claims'] if c['availability']=='available' and c['value'] is not None]
        prev=[c for c in previous['claims'] if c['availability']=='available' and c['value'] is not None]
        funnel['kept']+=sum(c['field'].startswith('hiring.site_job.') for c in claims)
        funnel['all_jobs_kept']+=sum(c['field'].startswith(('hiring.site_job.','hiring.job.')) for c in claims)
        site=next((c for c in claims if c['field']=='official_website'),None)
        if site:proof[site['value']['proof_type']]+=1
        metrics=row['run'].get('refresh',{}).get('company_jobs',{})
        for k in ('candidates','fetched','accepted','active_posts','pages_checked'):funnel[k]+=metrics.get(k,0)
        for e in row['errors']:
            if e['code'].startswith('company_careers_'):errors[e['code']]+=1
        old_urls={c['value'].get('final_url') if c['field']=='official_website' else c['value'].get('url') for c in prev if isinstance(c['value'],dict) and (c['field']=='official_website' or c['family']=='hiring')}
        wanted=[c for c in claims if (c['field']=='official_website' and c['value']['final_url'] not in old_urls) or (c['family']=='hiring' and isinstance(c['value'],dict) and c['value'].get('url') not in old_urls)]
        ev={e['id']:e for e in row['evidence']}
        for claim in wanted:
            record={'orgnr':org,'company':new[org]['company'],'kind':'website' if claim['field']=='official_website' else 'job','claim':claim,'sources':[]}
            for key in claim['evidence_ids']:
                e=ev[key];path=NEW/'state/blobs'/e['content_sha256']
                body=path.read_bytes();assert hashlib.sha256(body).hexdigest()==e['content_sha256']
                assert e['claim_span'] in body.decode('utf8',errors='replace')
                record['sources'].append(e)
            new_items.append(record)
        if old[org]['website'] and not new[org]['website']:lost.append({'orgnr':org,'company':new[org]['company'],'prior':old[org]['website'],'errors':row['errors']})
    article_counts={}
    for label, folder in [('baseline',OLD),('candidate',NEW)]:
        totals=Counter()
        for row in rows(folder/'envelopes.jsonl'):
            articles=[c for c in row['claims'] if c['availability']=='available' and c['field'].startswith('dated_item.')]
            totals['news_companies']+=bool(articles);totals['article_claims']+=len(articles)
        article_counts[label]=totals
    report=json.loads((NEW/'report.json').read_text())
    result={'baseline':a,'candidate':b,'websites_by_proof_type':proof,'jobs_funnel':funnel,'careers_errors':errors,'new_websites':sum(r['kind']=='website' for r in new_items),'new_jobs':sum(r['kind']=='job' for r in new_items),'lost_websites':len(lost),'pooled_limit':report['limits']['hard_max_requests'],'per_100_seconds':b['wall_seconds']/10,'all_attributed_counts_within_40':all(v<=40 for v in Counter(e['organisation_number'] for e in report['request_log'] if e['organisation_number'] in new).values())}
    result['news']=article_counts
    result['gate']={'articles_at_least_69':article_counts['candidate']['article_claims']>=69,
                    'websites_at_least_113':b['websites']>=113,'jobs_at_least_2':b['jobs']>=2,
                    'careers_errors_zero':not errors,'deadline_hits_zero':b['deadline_hits']==0}
    result['gate_pass']=all(result['gate'].values())
    for file,obj in [('summary.json',result),('new-items.json',new_items),('lost-websites.json',lost)]:
        (OUT/file).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
