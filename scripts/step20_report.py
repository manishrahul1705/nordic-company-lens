"""Saved-run metrics and independently located raw evidence for Step 20."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import random
import shutil
import xml.etree.ElementTree as ET


def pointer(document,path):
    for key in path.strip('/').split('/'):
        key=key.replace('~1','/').replace('~0','~')
        document=document[int(key)] if isinstance(document,list) else document[key]
    return document


def main():
    parser=argparse.ArgumentParser();parser.add_argument('run',type=Path);args=parser.parse_args()
    out=Path('bench/reports/s6-step20');gleif=[];awards=[];parents=[];counts=collections.Counter();states=collections.Counter()
    companies=collections.defaultdict(set);absent=[];source_states=collections.Counter();cache={}
    def body(sha):
        if sha not in cache:
            b=(args.run/'state/blobs'/sha).read_bytes();assert hashlib.sha256(b).hexdigest()==sha;cache[sha]=b
        return cache[sha]
    for line in (args.run/'envelopes.jsonl').open(encoding='utf-8'):
        row=json.loads(line);org=row['organisation_number'];name=next((c['value'] for c in row['claims'] if c['field']=='identity.legal_name' and c['availability']=='available'),org)
        evidence={e['id']:e for e in row['evidence']};states[row['run']['sections'].get('website')]+=1
        source_states.update(k+':'+v for k,v in row['run']['refresh'].get('official_extra',{}).items())
        if any(e['code']=='declared_domain_absent' for e in row['errors']):absent.append({'orgnr':org,'name':name,'state':row['run']['sections']['website'],'metadata':row['run']['refresh'].get('website')})
        for c in row['claims']:
            if c['availability']!='available':continue
            counts[c['family']]+=1
            if not c['field'].startswith(('identity.gleif.','procurement_award.')):continue
            sources=[]
            for eid in c['evidence_ids']:
                e=evidence[eid];b=body(e['content_sha256']);assert e['claim_span'] in b.decode('utf-8')
                sources.append(e)
            item={'orgnr':org,'name':name,'claim':c,'evidence':sources}
            if c['field'].startswith('identity.gleif.'):
                companies['GLEIF'].add(org)
                e=sources[0];d=json.loads(body(e['content_sha256']));raw=pointer(d,e['locator'])
                item['raw_located_value']=raw
                if c['field'].endswith(('direct_parent','ultimate_parent')):
                    item['raw_documents']=[json.loads(body(e['content_sha256'])) for e in sources]
                    parents.append(item)
                else:
                    assert raw==c['value']
                    idx=e['locator'].split('/attributes')[0];record=pointer(d,idx)
                    entity=record['attributes']['entity']
                    assert entity['registeredAs']==org and entity['registeredAt']['id']=='RA000472'
                    item['raw_identity_binding']={'registeredAs':entity['registeredAs'],'registeredAt':entity['registeredAt'],'lei':record['id']}
                    gleif.append(item)
            else:
                companies['TED'].add(org);root=ET.fromstring(body(sources[0]['content_sha256']))
                assert root.tag.split('}')[-1]=='ContractAwardNotice'
                contracts=[];organisations=[];parties=[];tenders=[]
                for el in root.iter():
                    tag=el.tag.split('}')[-1]
                    children={c.tag.split('}')[-1] for c in el}
                    if tag=='SettledContract' and 'AwardDate' in children:contracts.append(ET.tostring(el,encoding='unicode'))
                    if tag=='Company' and 'PartyLegalEntity' in children:organisations.append(ET.tostring(el,encoding='unicode'))
                    if tag=='TenderingParty' and 'Tenderer' in children:parties.append(ET.tostring(el,encoding='unicode'))
                    if tag=='LotTender' and 'TenderingParty' in children:tenders.append(ET.tostring(el,encoding='unicode'))
                item.update(raw_contracts=contracts,raw_organisations=organisations,raw_parties=parties,raw_tenders=tenders)
                awards.append(item)
    rng=random.Random(20261107)
    selected= rng.sample(gleif,min(20,len(gleif)))
    selected_awards=rng.sample(awards,min(20,len(awards)))
    report=json.loads((args.run/'report.json').read_text(encoding='utf-8'));score=json.loads((args.run/'scoreboard.json').read_text(encoding='utf-8'))
    metrics={'run':str(args.run),'GLEIF_companies':len(companies['GLEIF']),'GLEIF_claims':len(gleif)+len(parents),'GLEIF_parent_claims':len(parents),
        'tender_companies':len(companies['TED']),'tender_claims':len(awards),'website_states':states,'declared_absence_companies':len(absent),
        'facts_by_family':counts,'facts':sum(counts.values()),'requests':report['requests'],'max_requests':report['max_requests_per_company'],
        'mean_requests':report['amortized_requests_per_company'],'wall_seconds':score['wall_seconds'],'deadline_hits':report['deadline_hits'],
        'warnings':report['warnings'],'extra_metrics':report.get('official_extra'),'source_states':source_states,
        'extra_requests':[e for e in report['request_log'] if e['organisation_number']=='__official_extra__']}
    for name,value in [('metrics.json',metrics),('GLEIF-review.json',selected),('parents-review.json',parents),('tender-review.json',selected_awards),('declared-absence.json',absent)]:
        (out/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')
    for name in ['scoreboard.json','execution.json']:shutil.copyfile(args.run/name,out/('benchmark-'+name))
    print(json.dumps({k:v for k,v in metrics.items() if k!='extra_requests'},indent=2))


if __name__=='__main__':main()
