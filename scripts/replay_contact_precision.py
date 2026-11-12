"""Re-evaluate published contacts offline; never rerun ownership proof or fetch."""
import hashlib,json,random,sys
from collections import Counter
from pathlib import Path
from functools import lru_cache
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from signalpost.web.contact_policy import Regions,email_allowed,phone_allowed
from signalpost.web.html import Page
from signalpost.web.policy import domain
ROOT=Path(__file__).resolve().parents[1];RUN=ROOT/'bench/runs/news-contact-live';OUT=ROOT/'bench/reports/contact-precision'

@lru_cache(maxsize=64)
def page(sha,url):
    body=(RUN/'state/blobs'/sha).read_bytes();assert hashlib.sha256(body).hexdigest()==sha
    return Page(body,url)


def main():
    OUT.mkdir(exist_ok=True);before=Counter();after=Counter();decisions=[];company_before=set();company_after=set()
    for line in (RUN/'envelopes.jsonl').open(encoding='utf8'):
        row=json.loads(line);claims={c['field']:c for c in row['claims'] if c['availability']=='available'}
        contacts=[c for c in claims.values() if c['field'].startswith('contact.')]
        if not contacts:continue
        org=row['organisation_number'];company_before.add(org);ev={e['id']:e for e in row['evidence']}
        get=lambda field:claims.get('identity.'+field,{}).get('value')
        context={'name':get('legal_name'),'email':get('registered_email'),'phone':get('registered_phone'),'mobile':get('registered_mobile')}
        proof=claims['official_website'];target=domain(proof['value']['final_url']);regions={}
        for c in contacts:
            kind=c['field'].split('.')[1];before[kind]+=1;kept=False;refs=[]
            for ref in c['evidence_ids']:
                e=ev[ref];p=page(e['content_sha256'],e['source_url']);assert e['claim_span'] in p.raw
                k=(e['content_sha256'],e['source_url'])
                if k not in regions:regions[k]=Regions(p,context)
                accepted=(email_allowed(c['value'],context,target,regions[k]) if kind=='email' else
                          phone_allowed(c['value'],p,context,e['claim_span'],regions[k]) if kind=='phone' else False)
                kept|=accepted;refs.append({**e,'accepted':accepted})
            if kept:after[kind]+=1;company_after.add(org)
            decisions.append({'orgnr':org,'company':context['name'],'field':c['field'],'value':c['value'],
                'registered_email':context['email'],'registered_phone':context['phone'],'registered_mobile':context['mobile'],
                'kept':kept,'reason':'passes publication policy' if kept else 'unregistered non-role/personal email' if kind=='email' else 'unregistered phone outside corporate contact/footer area or inside staff list','evidence':refs})
    lookup={(x['orgnr'],x['field'],json.dumps(x['value'],sort_keys=True)):x for x in decisions}
    old=json.loads((ROOT/'bench/reports/news-contact/contact-review-input.json').read_text(encoding='utf8'));sample=[]
    for x in old:
        c=x['claim'];sample.append(lookup[(x['orgnr'],c['field'],json.dumps(c['value'],sort_keys=True))])
    fresh=random.Random(20261112).sample(sorted((x for x in decisions if x['kept']),key=lambda x:(x['orgnr'],x['field'])),20)
    summary={'source_run':str(RUN.relative_to(ROOT)),'mode':'Offline filtering of existing cited contacts only; no additions, no requests, original artifacts unchanged. The source run contains the rejected news trial; this replay does not reapply news.',
        'before':{'facts':sum(before.values()),'by_type':dict(before),'companies':len(company_before)},
        'after':{'facts':sum(after.values()),'by_type':dict(after),'companies':len(company_after)},
        'removed':len([x for x in decisions if not x['kept']]),'original_sample_kept':sum(x['kept'] for x in sample),'original_sample_removed':sum(not x['kept'] for x in sample),
        'all_noncontact_claims_and_website_proofs':'unchanged: only publication predicates evaluated; no original envelopes rewritten','sample_seed':20261112}
    for name,value in [('summary.json',summary),('decisions.json',decisions),('original-20-recheck.json',sample),('retained-20-review.json',fresh)]:
        (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
