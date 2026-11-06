"""Saved Step 13 breadth/depth inventory and before/after metrics. No network."""
import argparse
import json
from collections import Counter
from pathlib import Path
from step11_audit import summarize,rows

BASE=Path('bench/cache/s6-step12-cleanup-step11-recheck')
OUT=Path('bench/reports/s6-step13')


def fact_key(c):return c['field'],json.dumps(c['value'],sort_keys=True,ensure_ascii=False),json.dumps(c.get('reporting_period'),sort_keys=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('run',type=Path);args=parser.parse_args();run=args.run
    before={r['organisation_number']:r for r in rows(BASE/'envelopes.jsonl')};after=rows(run/'envelopes.jsonl')
    profiles_before={r['organisation_number']:r for r in rows(BASE/'profiles.jsonl')}
    profiles_after={r['organisation_number']:r for r in rows(run/'profiles.jsonl')}
    report=json.loads((run/'report.json').read_text(encoding='utf8'))
    preview=json.loads((OUT/'postal-preview.json').read_text(encoding='utf8'))
    reviewed_places={(x['organisation_number'],json.dumps(x['value'],sort_keys=True,ensure_ascii=False)):x for x in preview if x.get('verdict')=='correct'}
    items=[];locations=[];losses=[];social_losses=[];families_before=Counter();families_after=Counter();brand=Counter();second=report.get('website_second_pass',{})
    for old in before.values():families_before.update(c['family'] for c in old['claims'] if c['availability']=='available')
    for row in after:
        org=row['organisation_number'];old=before[org];name=next((c['value'] for c in row['claims'] if c['field']=='identity.legal_name'),org)
        families_after.update(c['family'] for c in row['claims'] if c['availability']=='available')
        oldkeys={fact_key(c) for c in old['claims'] if c['availability']=='available'};evidence={e['id']:e for e in row['evidence']}
        for c in row['claims']:
            if c['availability']!='available' or fact_key(c) in oldkeys:continue
            selected=[];seen=set()
            for ref in c['evidence_ids']:
                e=evidence[ref]
                if c['family']=='website' and e['source_class']=='official_registry' and not any(t in e['locator'] for t in ['navn','name','adresse','address','epost','email','telefon','phone','underenheter']):continue
                key=e['source_url'],e['content_sha256'],e['claim_span']
                if key in seen:continue
                seen.add(key);selected.append({k:e.get(k) for k in ['id','source_url','source_class','content_sha256','claim_span','locator','retrieved_at','reporting_period']})
            items.append({'organisation_number':org,'company':name,'family':c['family'],'field':c['field'],'value':c['value'],'reporting_period':c.get('reporting_period'),'evidence':selected,'verdict':'pending','review':''})
        def places(profile):
            v=profile['evidence']['locations']['value'];return (v or {}).get('locations',[])
        previous={json.dumps(v,sort_keys=True,ensure_ascii=False) for v in places(profiles_before[org])}
        for place in places(profiles_after[org]):
            if json.dumps(place,sort_keys=True,ensure_ascii=False) not in previous:
                reviewed=reviewed_places.get((org,json.dumps(place,sort_keys=True,ensure_ascii=False)),{})
                fields=['identity.registered_address'] if place['type']=='registered_business_address' else ['identity.postal_address'] if place['type']=='registered_postal_address' else ['subunits.detail.'+place['organisation_number']+'.postal_address'] if place['type']=='subunit_postal_address' else ['subunits.unit.'+place['organisation_number']]
                support=[c for c in row['claims'] if c['field'] in fields and c['availability']=='available']
                locations.append({'organisation_number':org,'company':name,'value':place,'supporting_claim_ids':[c['id'] for c in support],
                                  'evidence':[evidence[ref] for c in support for ref in c['evidence_ids']],
                                  'verdict':reviewed.get('verdict','pending'),'review':reviewed.get('review','')})
        oldsite=next((c for c in old['claims'] if c['field']=='official_website' and c['availability']=='available'),None)
        site=next((c for c in row['claims'] if c['field']=='official_website' and c['availability']=='available'),None)
        if oldsite and not site:losses.append({'organisation_number':org,'company':name,'previous':oldsite['value'],'state':row['run']['sections']['website'],'errors':[e for e in row['errors'] if e['section']=='website']})
        def socials(r):return {c['value']['url'] for c in r['claims'] if c['availability']=='available' and c['field'].startswith(('social_profile.','registry_social.'))}
        for url in sorted(socials(old)-socials(row)):
            social_losses.append({'organisation_number':org,'company':name,'url':url,'website_available':site is not None,'errors':[e for e in row['errors'] if e['section']=='website'],'website_refresh':row['run']['refresh'].get('website',{})})
        nominations=row['run']['refresh'].get('brand_candidates',[])
        for candidate in nominations:
            brand['candidates']+=1
            entries=[e for e in row['run']['refresh'].get('recall_round2',{}).get('candidates',[]) if e['origin']=='brand_name' and e['domain']==candidate['domain']]
            brand['fetched']+=any(e.get('fetched') for e in entries)
            brand['accepted']+=bool(site and site['value'].get('candidate_origin')=='brand_name' and any(e.get('accepted') for e in entries))
    def write(name,value):(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    write('new-items.json',items);write('new-locations.json',locations);write('losses.json',losses);write('social-losses.json',social_losses)
    write('counts.json',{'before':summarize(BASE),'after':summarize(run),'published_claims_by_family_before':dict(families_before),'published_claims_by_family_after':dict(families_after),'new_items_by_family':dict(Counter(i['family'] for i in items)),'new_location_items':len(locations)})
    write('funnel.json',{'A':dict(brand),'B':second})
    metrics={k:report[k] for k in ['requests','requests_per_company','amortized_requests_per_company','shared_requests','max_requests_per_company','runtime_ms','deadline_hits','warnings','limits','search','llm','dns_fallback_attempts','dns_fallback_successes','dns_fallback_seconds','dns_fallback_max_seconds_per_company','hiring_prefetch','nav_detail_requests','finalisation']}
    metrics['execution']=json.loads((run/'execution.json').read_text(encoding='utf8'));write('metrics.json',metrics)
    print({'new_items':len(items),'new_locations':len(locations),'counts':summarize(run),'A':dict(brand),'B':{k:v for k,v in second.items() if k!='companies'}},flush=True)


if __name__=='__main__':main()
