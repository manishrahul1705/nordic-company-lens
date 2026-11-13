"""Two-run measurement band and all website/article membership differences."""
import json,sys,hashlib
from collections import Counter
from pathlib import Path
from r3_analyze import summarize,rows
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'bench/reports/stage-g'
sys.path.insert(0,str(ROOT/'src'))
from signalpost.web.html import Page

def summarize_run(number):
    run=ROOT/f'bench/runs/stage-g-run{number}';summary,companies=summarize(run)
    report=json.loads((run/'report.json').read_text());extra=Counter();proof=Counter();items={};review=[]
    baseline={r['organisation_number']:r for r in rows(ROOT/'bench/runs/stage-e-live/envelopes.jsonl')}
    for row in rows(run/'envelopes.jsonl'):
        org=row['organisation_number'];claims=[c for c in row['claims'] if c['availability']=='available' and c['value'] is not None]
        site=next((c for c in claims if c['field']=='official_website'),None)
        news=[c for c in claims if c['field'].startswith('dated_item.')]
        extra['news_companies']+=bool(news);extra['article_claims']+=len(news)
        extra['GLEIF_companies']+=any(c['field'].startswith('identity.gleif.') for c in claims)
        awards=[c for c in claims if c['field'].startswith('procurement_award.')]
        extra['TED_companies']+=bool(awards);extra['TED_awards']+=len(awards)
        if site:proof[site['value']['proof_type']]+=1
        items[org]={'orgnr':org,'company':companies[org]['company'],'website':site,'articles':news,'errors':row['errors'],'website_diagnostics':row['run']['refresh'].get('recall_round2',{}),'official_extra':row['run']['refresh'].get('official_extra',{})}
        old_sites={c['value']['final_url'] for c in baseline[org]['claims'] if c['field']=='official_website' and c['availability']=='available'}
        if site and site['value']['final_url'] not in old_sites:
            refs={e['id']:e for e in row['evidence']};sources=[]
            for ref in site['evidence_ids']:
                e=refs[ref];body=(run/'state/blobs'/e['content_sha256']).read_bytes();assert hashlib.sha256(body).hexdigest()==e['content_sha256']
                page=Page(body,e['source_url']);assert e['claim_span'] in page.raw
                sources.append({**e,'title':page.title,'owner_text':page.owner_text[:6500]})
            review.append({'run':number,'orgnr':org,'company':companies[org]['company'],'website':site,'sources':sources,'prior_urls':sorted(old_sites),'verdict':'pending'})
    ted=[e for e in report['request_log'] if e['host'] in {'api.ted.europa.eu','ted.europa.eu'}]
    summary.update(extra);summary.update(websites_by_proof_type=proof,TED_requests=len(ted),TED_status_distribution=dict(Counter(str(e.get('status')) for e in ted)),seconds_per_100=summary['wall_seconds']/10)
    return summary,items,report,review

def main():
    results=[summarize_run(n) for n in (1,2)]
    summaries=[r[0] for r in results];differences=[]
    for org in sorted(results[0][1]):
        a,b=(r[1][org] for r in results)
        def site(x):return x['website']['value']['final_url'] if x['website'] else None
        old={c['value']['url']:c for c in a['articles']};new={c['value']['url']:c for c in b['articles']}
        if site(a)==site(b) and old==new:continue
        # First-observed timestamps are not article content differences.
        content=lambda c:json.dumps(c['value'],sort_keys=True)
        removed=[c for u,c in old.items() if u not in new or content(c)!=content(new[u])]
        added=[c for u,c in new.items() if u not in old or content(c)!=content(old[u])]
        if site(a)==site(b) and not removed and not added:continue
        diagnostics=[]
        for n,result in enumerate(results,1):
            row=result[1][org];events=[e for e in result[2]['request_log'] if e['organisation_number']==org and (e.get('error') or e.get('status') is not None and e['status']>=400)]
            errors=[e for e in row['errors'] if e['section'] in {'website','activity'}]
            diagnostics.append({'run':n,'recorded_errors':errors,'failed_http_events':events,'note':'No recorded website/activity error' if not errors and not events else 'Use these recorded diagnostics; do not assume every change is transient.'})
        differences.append({'orgnr':org,'company':a['company'],'website_run1':site(a),'website_run2':site(b),'removed_articles':removed,'added_articles':added,'diagnostics':diagnostics})
    fields=['websites','social_companies','jobs','activity','news_companies','article_claims','GLEIF_companies','TED_companies','TED_awards','facts','http_total','http_mean','http_max','wall_seconds','seconds_per_100','deadline_hits']
    band={k:{'run1':summaries[0][k],'run2':summaries[1][k],'minimum':min(s[k] for s in summaries),'maximum':max(s[k] for s in summaries),'absolute_span':abs(summaries[1][k]-summaries[0][k])} for k in fields}
    for file,value in [('summary.json',{'run1':summaries[0],'run2':summaries[1],'reported_final_run':2}),('noise-band.json',band),('website-article-differences.json',differences),('website-review-pack.json',results[0][3]+results[1][3])]:
        (OUT/file).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps(summaries,indent=2))
if __name__=='__main__':main()
