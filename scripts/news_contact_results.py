"""Retain live metrics and complete saved-source news/contact review inputs."""
import hashlib,json,random,sys
from collections import Counter
from pathlib import Path
from r3_analyze import rows
ROOT=Path(__file__).resolve().parents[1]
OLD=ROOT/'bench/runs/proof-depth-live';NEW=ROOT/'bench/runs/news-contact-live';OUT=ROOT/'bench/reports/news-contact'

def main():
    prior={};metrics=[];news=[];pool=[];sites=[]
    for run in (OLD,NEW):
        counts=Counter();fields=Counter();site_orgs=set();social_orgs=set();contacts=0
        for row in rows(run/'envelopes.jsonl'):
            org=row['organisation_number'];claims=[c for c in row['claims'] if c['availability']=='available' and c['value'] is not None]
            items=[c for c in claims if c['field'].startswith('dated_item.')]
            counts['news_companies']+=bool(items);counts['articles']+=len(items)
            counts['facts']+=len({(c['field'],json.dumps(c['value'],sort_keys=True),json.dumps(c.get('reporting_period'),sort_keys=True)) for c in claims})
            for family,prefix in [('websites',('official_website',)),('social',('social_profile.','registry_social.')),('jobs',('hiring.job.','hiring.site_job.')),('activity',('registry_change.','dated_item.'))]:
                found=any(c['field'].startswith(prefix) for c in claims);counts[family]+=found
                if found and family=='websites':site_orgs.add(org)
                if found and family=='social':social_orgs.add(org)
            contact=[c for c in claims if c['field'].startswith('contact.')]
            counts['contact_companies']+=bool(contact);counts['contact_facts']+=len(contact)
            fields.update(c['field'].split('.')[1] for c in contact)
            counts['envelopes']+=1
            if run==OLD:
                prior[org]={c['field']:c['value'] for c in items}
                continue
            ev={e['id']:e for e in row['evidence']}
            name=next((c['value'] for c in claims if c['field']=='identity.legal_name'),'')
            context={c['field']:c['value'] for c in claims if c['field'].startswith('identity.registered_')}
            def record(c):return {'orgnr':org,'company':name,'claim':c,'registry_contacts':context,'evidence':[ev[k] for k in c['evidence_ids']]}
            for c in items:
                if prior.get(org,{}).get(c['field'])!=c['value']:news.append(record(c))
            pool.extend(record(c) for c in contact)
        report=json.loads((run/'report.json').read_text(encoding='utf8'));execution=json.loads((run/'execution.json').read_text())
        metrics.append({**counts,'contact_types':dict(fields),'http_total':report['requests'],'http_mean':report['requests']/1000,'http_max':report['max_requests_per_company'],'wall_seconds':execution.get('wall_seconds'),'seconds_per_100':execution.get('wall_seconds',0)/10,'deadline_hits':report['deadline_hits'],'warnings':report['warnings'],'exit_code':execution.get('exit_code'),'site_orgs':sorted(site_orgs),'social_orgs':sorted(social_orgs)})
    sampled=random.Random(20261112).sample(sorted(pool,key=lambda x:(x['orgnr'],x['claim']['field'])),min(20,len(pool)))
    for item in news+sampled:
        for e in item['evidence']:
            path=NEW/'state/blobs'/e['content_sha256'];body=path.read_bytes();assert hashlib.sha256(body).hexdigest()==e['content_sha256']
            from signalpost.sources.text import decode_body
            text=decode_body(body);span=e['claim_span'];assert span in text
            pos=text.find(span);e['saved_context']=text[max(0,pos-400):pos+len(span)+600]
    result={'baseline':metrics[0],'trial':metrics[1],'new_or_changed_news_items':len(news),'contact_review_seed':20261112,'lost_websites':sorted(set(metrics[0]['site_orgs'])-set(metrics[1]['site_orgs'])),'lost_social_companies':sorted(set(metrics[0]['social_orgs'])-set(metrics[1]['social_orgs']))}
    for name,value in [('summary.json',result),('news-review-input.json',news),('contact-review-input.json',sampled)]:
        (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in result.items() if k not in ('baseline','trial')},indent=2))
    print(json.dumps([{k:v for k,v in m.items() if k not in ('site_orgs','social_orgs')} for m in metrics],indent=2))
if __name__=='__main__':main()
