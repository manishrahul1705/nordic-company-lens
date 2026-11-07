"""Read-only measurement and stratified review sample from the single final run."""
import argparse,csv,hashlib,io,json,random
from collections import Counter
from pathlib import Path
BASE=Path('bench/runs/20261106T183808924157Z-1db7047');OUT=Path('bench/reports/s6-step16');FAMILIES=('identity','roles','subunits','accounts')

def rows(path):
    with path.open(encoding='utf8') as f:
        for line in f:yield json.loads(line)

def key_category(family,field):
    if family=='accounts':return 'consolidated' if field.startswith('accounts.consolidated.') else 'additional' if field.startswith('accounts.additional.') else 'statement'
    if '.historical_name.' in field:return 'historical_name'
    return field.rsplit('.',1)[-1]

def pointer(data,loc):
    for part in loc.strip('/').split('/'):
        if part:data=data[int(part)] if isinstance(data,list) else data[part]
    return data

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);args=p.parse_args();run=args.run
    before=Counter();after=Counter();oldfields={};oldsites={};sites={};social=set();activity=set();pool={f:[] for f in FAMILIES};oldtotal=0;total=0
    for row in rows(BASE/'envelopes.jsonl'):
        org=row['organisation_number'];oldfields[org]={c['field'] for c in row['claims']}
        for c in row['claims']:
            if c['availability']!='available':continue
            oldtotal+=1;before[c['family']]+=1
            if c['field']=='official_website':oldsites[org]=c['value']['final_url']
    for row in rows(run/'envelopes.jsonl'):
        org=row['organisation_number'];ev={e['id']:e for e in row['evidence']}
        for c in row['claims']:
            if c['availability']!='available':continue
            total+=1;after[c['family']]+=1
            if c['field']=='official_website':sites[org]=c['value']['final_url']
            if c['field'].startswith('social_profile.'):social.add(org)
            if c['family']=='activity':activity.add(org)
            if c['family'] in FAMILIES and c['field'] not in oldfields[org]:pool[c['family']].append({'organisation_number':org,'claim':c,'evidence':[ev[eid] for eid in c['evidence_ids']]})
    rng=random.Random(20261107);sample=[]
    for family in FAMILIES:
        candidates=pool[family];rng.shuffle(candidates);selected=[];selectedids=set();selectedorgs=set()
        for category in sorted({key_category(family,r['claim']['field']) for r in candidates}):
            item=next((r for r in candidates if key_category(family,r['claim']['field'])==category and r['organisation_number'] not in selectedorgs),None)
            if item is not None and len(selected)<10:selected.append(item);selectedids.add(item['claim']['id']);selectedorgs.add(item['organisation_number'])
        for item in candidates:
            if len(selected)==10:break
            if item['claim']['id'] in selectedids or item['organisation_number'] in selectedorgs:continue
            selected.append(item);selectedids.add(item['claim']['id']);selectedorgs.add(item['organisation_number'])
        assert len(selected)==10
        for item in selected:
            c=item['claim'];e=item['evidence'][0];body=(run/'state/blobs'/e['content_sha256']).read_bytes();assert hashlib.sha256(body).hexdigest()==e['content_sha256'];assert e['claim_span'] in body.decode('utf8')
            loc=e['locator'];url=e['source_url'];assert url.startswith('https://data.brreg.no/')
            if '/lastned/csv' in url:
                doc=next(csv.DictReader(io.StringIO(body.decode('utf-8-sig'))));raw=doc[loc.split('/column:',1)[1]];assert str(doc['organisasjonsnummer'])==item['organisation_number']
                equivalent=(raw.casefold()=='true')==c['value'] if isinstance(c['value'],bool) else raw==c['value']
            else:
                doc=json.loads(body);raw=pointer(doc,loc);equivalent=(int(str(raw)[:4])==c['value']) if c['field'].endswith('.birth_year') else all(raw.get(k)==v for k,v in c['value'].items()) if '.historical_name.' in c['field'] else raw==c['value']
                if c['family']=='accounts':
                    record=doc[int(loc.split('/')[1])];period=c['reporting_period'];assert str(record['virksomhet']['organisasjonsnummer'])==item['organisation_number'];assert record['regnskapsperiode']['tilDato']==period['period_end'];assert record['regnskapsperiode']['fraDato']==period['period_start'];assert record['regnskapstype']==period['account_type'];assert str(period['fiscal_year'])==period['period_end'][:4]
                elif c['family']=='subunits':assert str(doc['_embedded']['underenheter'][int(loc.split('/')[3])]['overordnetEnhet'])==item['organisation_number']
                elif c['family']=='roles':assert str(doc.get('organisasjonsnummer'))==item['organisation_number'] or doc.get('_links',{}).get('enhet',{}).get('href','').endswith('/'+item['organisation_number'])
            assert equivalent,(c['field'],raw,c['value'])
            item['raw_value']=raw;item['machine_span_value_period_check']='pass';item['verdict']='pending manual review';sample.append(item)
    (OUT/'review-sample.json').write_text(json.dumps({'seed':20261107,'sampling':'Stratified random: 10 claims per family, distinct companies within each family; cover present new-field categories before filling randomly.','items':sample},ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    report=json.loads((run/'report.json').read_text(encoding='utf8'));execution=json.loads((run/'execution.json').read_text(encoding='utf8'));score=json.loads((run/'scoreboard.json').read_text(encoding='utf8'))
    metrics={'run':str(run),'baseline':str(BASE),'claims_before':dict(before),'claims_after':dict(after),'total_before':oldtotal,'total_after':total,'new_fields_by_family':{f:len(v) for f,v in pool.items()},'websites':len(sites),'social_companies':len(social),'activity_companies':len(activity),'jobs':score['sections']['jobs']['states']['available'] if 'jobs' in score['sections'] else sum(1 for row in rows(run/'envelopes.jsonl') if row['run']['sections']['hiring']=='available'),'http':score['http_requests'],'http_baseline':8666,'http_increase_percent':(score['http_requests']/8666-1)*100,'http_cap_2_percent':8839,'wall_seconds':execution['wall_seconds'],'deadlines':report['deadline_hits'],'warnings':report['warnings'],'website_losses':[{'organisation_number':org,'previous_url':url} for org,url in oldsites.items() if org not in sites]}
    request_stats={k:report.get(k) for k in ['requests_per_company','max_requests_per_company','amortized_requests_per_company','shared_requests']}
    metrics['request_stats']=request_stats
    (OUT/'metrics.json').write_text(json.dumps(metrics,ensure_ascii=False,indent=2)+'\n',encoding='utf8');print(json.dumps(metrics))
if __name__=='__main__':main()
