"""Offline sitemap/feed and published contact coverage audit; no requests."""
import json,re,sys
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import urlsplit
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from signalpost.web.policy import domain
from signalpost.web.html import Page
ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'bench/runs/proof-depth-live'
OUT=ROOT/'bench/reports/news-contact'

def main():
    report=json.loads((RUN/'report.json').read_text(encoding='utf8'))
    events=defaultdict(list)
    for event in report['request_log']:
        if event.get('status')==200 and event.get('content_sha256'):
            events[event['organisation_number']].append(event)
    result=[];fields=Counter();companies=Counter();news=0;articles=0
    for line in (RUN/'envelopes.jsonl').open(encoding='utf8'):
        row=json.loads(line)
        items=[c for c in row['claims'] if c['field'].startswith('dated_item.') and c['availability']=='available']
        news+=bool(items);articles+=len(items)
        proof=next((c for c in row['claims'] if c['field']=='official_website' and c['availability']=='available'),None)
        if not proof:continue
        host=domain(proof['value']['final_url']);maps=[];feeds=[];missing=[]
        for event in events[row['organisation_number']]:
            if domain(event['url'])!=host:continue
            path=RUN/'state/blobs'/event['content_sha256']
            if not path.exists():missing.append(event['url']);continue
            body=path.read_bytes();text=body.decode('utf8',errors='replace')
            if urlsplit(event['url']).path.endswith('/robots.txt'):
                maps += re.findall(r'^\s*Sitemap:\s*(\S+)',text,re.I|re.M)
            if urlsplit(event['url']).path.rstrip('/') in {'/sitemap.xml','/sitemap_index.xml'} and re.search(r'<(?:\w+:)?(?:urlset|sitemapindex)\b',text):maps.append(event['url'])
            if urlsplit(event['url']).path.rstrip('/')==urlsplit(proof['value']['final_url']).path.rstrip('/'):
                for tag in re.findall(r'<link\b[^>]*>',text,re.I):
                    if re.search(r'application/(?:rss|atom)\+xml',tag,re.I) and re.search(r'\balternate\b',tag,re.I):feeds.append(tag[:500])
        contacts=[c for c in row['claims'] if c['field'].startswith('contact.') and c['availability']=='available']
        kinds={c['field'].split('.')[1] for c in contacts}
        for c in contacts:fields[c['field'].split('.')[1]]+=1
        companies.update(kinds)
        result.append({'orgnr':row['organisation_number'],'url':proof['value']['final_url'],'sitemaps':sorted(set(maps)),'feeds':sorted(set(feeds)),'contacts':[{'field':c['field'],'value':c['value'],'evidence_ids':c['evidence_ids']} for c in contacts],'missing_bodies':missing})
    summary={'source_run':str(RUN),'verified_websites':len(result),'sitemap_companies':sum(bool(x['sitemaps']) for x in result),'feed_companies':sum(bool(x['feeds']) for x in result),'sitemap_or_feed_companies':sum(bool(x['sitemaps'] or x['feeds']) for x in result),'contact_companies':sum(bool(x['contacts']) for x in result),'contact_fact_counts':dict(fields),'contact_company_counts':dict(companies),'news_companies':news,'articles':articles,'sites':result,'caveat':'Offline exposure counts require a saved robots Sitemap line, successful sitemap XML, or homepage RSS/Atom alternate link. Unfetched endpoints are unknown, not absent.'}
    OUT.mkdir(exist_ok=True);(OUT/'audit.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    print(json.dumps({k:v for k,v in summary.items() if k!='sites'},indent=2))
if __name__=='__main__':main()
