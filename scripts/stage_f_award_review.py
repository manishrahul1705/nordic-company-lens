"""Build an exact XML review pack for every published Stage F award."""
import hashlib,json,sys,xml.etree.ElementTree as ET
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from signalpost.sources.official_extra import NS,text
RUN=ROOT/'bench/runs/stage-f-live';OUT=ROOT/'bench/reports/stage-f'
def main():
    reviews=[]
    for line in (RUN/'envelopes.jsonl').open(encoding='utf8'):
        row=json.loads(line);org=row['organisation_number'];name=next((c['value'] for c in row['claims'] if c['field']=='identity.legal_name'),'')
        evidence={e['id']:e for e in row['evidence']}
        for claim in row['claims']:
            if claim['availability']!='available' or not claim['field'].startswith('procurement_award.'):continue
            refs=[evidence[k] for k in claim['evidence_ids'] if evidence[k]['source_class']=='TED']
            primary=refs[0];body=(RUN/'state/blobs'/primary['content_sha256']).read_bytes();assert hashlib.sha256(body).hexdigest()==primary['content_sha256']
            raw=body.decode('utf8');root=ET.fromstring(body);companies=[]
            for company in root.findall('.//efac:Organizations/efac:Organization/efac:Company',NS):
                national=text(company,'cac:PartyLegalEntity/cbc:CompanyID') or ''
                if ''.join(c for c in national if c.isdigit())==org:
                    companies.append(ET.tostring(company,encoding='unicode'))
            contract=next((n for n in root.findall('.//efac:NoticeResult/efac:SettledContract',NS) if text(n,'cbc:ID')==claim['value']['contract_id']),None)
            tenders={text(n,'cbc:ID'):n for n in root.findall('.//efac:NoticeResult/efac:LotTender',NS)}
            linked=[tenders.get(text(n,'cbc:ID')) for n in contract.findall('efac:LotTender',NS)] if contract is not None else []
            parties=root.findall('.//efac:NoticeResult/efac:TenderingParty',NS)
            reviews.append({'orgnr':org,'legal_name':name,'claim':claim,'source':primary,'matching_company_xml':companies,'contract_xml':ET.tostring(contract,encoding='unicode') if contract is not None else None,'linked_tender_xml':[ET.tostring(n,encoding='unicode') for n in linked if n is not None],'tendering_party_xml':[ET.tostring(n,encoding='unicode') for n in parties],'buyer_xml':[ET.tostring(n,encoding='unicode') for n in root.findall('./cac:ContractingParty',NS)],'exact_saved_spans':[e['claim_span'] for e in refs],'verdict':'pending manual review'})
    report=json.loads((RUN/'report.json').read_text());events=[e for e in report['request_log'] if e['host'] in {'api.ted.europa.eu','ted.europa.eu'}]
    metrics={'TED_companies':len({r['orgnr'] for r in reviews}),'awards':len(reviews),'TED_requests':len(events),'TED_status_distribution':dict(Counter(str(e.get('status')) for e in events)),'official_extra':report.get('official_extra')}
    (OUT/'award-review-pack.json').write_text(json.dumps(reviews,ensure_ascii=False,indent=2)+'\n',encoding='utf8');(OUT/'ted-metrics.json').write_text(json.dumps(metrics,indent=2)+'\n');print(json.dumps(metrics,indent=2))
if __name__=='__main__':main()
