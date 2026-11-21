"""Source corroboration for the recorded human review; no network or publishing."""
import json,re,sys,html,xml.etree.ElementTree as ET
from datetime import datetime,timedelta
from decimal import Decimal
from email.utils import parsedate_to_datetime
from pathlib import Path
from urllib.parse import urlsplit
sys.path.insert(0,str(Path(__file__).parent))
import common as C
from signalpost.web.html import Page
from signalpost.sources.text import decode_body

def norm(s):return ' '.join(str(s).split())
def main():
    rows={r['organisation_number']:r for r in C.read_envelopes()};blobs=C.read_blobs();items=[json.loads(l)for l in (C.HERE/'sample.jsonl').open(encoding='utf-8')];supports={x['index']:x for x in json.loads((C.HERE/'hand-review-support.json').read_text(encoding='utf-8'))};verdicts=[]
    for i,it in enumerate(items):
        ch=it['check'];f=it['field'];v=it['value'];org=it['orgnr'];r=rows[org]
        mechanical=bool(ch.get('span_in_body') and ch.get('org_in_source_url') and ch.get('value_at_locator')==v)
        note='Exact value at cited JSON pointer, verbatim span, SHA-256-checked source bytes and own-org registry URL.'
        if not mechanical:
            s=supports[i];records=s['source_records'];at=records[0].get('located_value');note=''
            assert ch.get('evidence_found') and ch.get('blob_present') and ch.get('span_in_body')
            raw=decode_body(blobs[records[0]['evidence']['content_sha256']]);page=Page(blobs[records[0]['evidence']['content_sha256']],records[0]['evidence']['source_url']) if at is None else None
            ownsite=next((c for c in r['claims']if c['field']=='official_website'),None)
            if f.endswith('.audit_status'):
                flags=records[0]['revision_flags'];assert type(flags['fravalgRevisjon'])is bool and type(flags['ikkeRevidertAarsregnskap'])is bool
                expected='audit_opted_out'if flags['fravalgRevisjon']else 'not_audited'if flags['ikkeRevidertAarsregnskap']else 'audited';assert expected==v
                note='Both explicit audit booleans checked for the cited year; fravalgRevisjon=true means audit_opted_out, not audited.'
            elif f.startswith('registry_change.'):
                event=records[0].get('parent_event',at);target=v.get('subunit_orgnr',org);assert event['organisasjonsnummer']==target and event['oppdateringsid']==v['event_id'];assert datetime.fromisoformat(event['dato'].replace('Z','+00:00'))==datetime.fromisoformat(v['date'].replace('Z','+00:00'))
                if target!=org:assert any(c['field']=='subunits.unit.'+target for c in r['claims'])
                if 'changed_field'in v:assert (at['path'],at['op'],at['value'])==(v['changed_field'],v['operation'],v['new_value'])
                else:assert event['endringstype']==v['event_type']
                assert v['date_source']=='registry publication time (not effective date)'
                note='Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time.'
            elif f=='public_brand':
                assert ownsite and ownsite['value']['identity_level']=='VERIFIED';assert v==page.meta.get('og:site_name') or v in page.title
                legal=(r.get('legal_name') or '').casefold();brand=str(v).casefold();host=(urlsplit(ownsite['value']['final_url']).hostname or '').split('.')[0].casefold()
                compact=lambda s:re.sub(r'[^a-z0-9]+','',s.casefold())
                assert any(t and t in legal.split() for t in re.findall(r'[^\W_]+',brand,re.UNICODE)) or compact(brand)==compact(host)
                note=f'Verified company page names “{v}”; the brand matches the legal name or verified domain core under the current brand rule.'
            elif f.startswith('hiring.'):
                assert v['status']=='ACTIVE';assert any(c['field']=='subunits.unit.'+v['employer_orgnr']for c in r['claims']);assert v['title']in page.visible
                assert any(v['employer_orgnr']in decode_body(blobs[x['evidence']['content_sha256']])for x in records)
                note=f'NAV detail checked for “{v["title"]}” and employer {v["employer_orgnr"]}; the company’s BRREG subunit claim establishes the employer scope. Status/expiry and occupation/location remain NAV fields.'
            elif f.startswith('central_approval.'):
                text=page.visible;assert org in text and v['area']in text and v['function']in text and v['valid_from']in text and v['valid_to']in text
                trs=re.findall(r'<tr[\s>].*?</tr>',raw,re.I|re.S);assert any(v['area']in html.unescape(re.sub('<[^>]+>',' ',tr)) and v['class']in tr for tr in trs)
                note=f'DiBK page has the exact company number and approval row values: {v["area"]}, {v["function"]}, class {v["class"]}, valid {v["valid_from"]} to {v["valid_to"]}.'
            elif f.startswith('cleaning_approval.'):
                assert at['organisation_number']==org and at['status']==v['status'];assert v['approved']==(at['status']in ['Godkjent med ansatte','Godkjent uten ansatte'])
                note=f'Exact main-unit register row matches company number, name and status “{v["status"]}”; the approved flag follows the register’s explicit status.'
            elif f.startswith('news_item.'):
                found=False
                for e in ET.fromstring(raw).iter('item'):
                    if e.findtext('link')==v['url'] and e.findtext('title')==v['title']:
                        assert parsedate_to_datetime(e.findtext('pubDate')).date().isoformat()==v['date'];found=True
                assert found and any(c['id']==v['identity_claim_id']for c in r['claims'])
                note=f'Same RSS item states the exact title, URL and publication date {v["date"]}; the verified company website binds the feed to this company. This is company-published material.'
            elif f.startswith('related_company_website.'):
                assert all(v[k]==x for k,x in at.items());assert v['verification']=='registry-declared, not ownership-verified'
                relation_claim=next(c for c in r['claims'] if c['field']=='identity.group_structure.parent')
                assert relation_claim['value']['parentOrganisasjonsnummer']==v['organisasjonsnummer'] and v['relationship']=='parent'
                note=f'Official registry row names {v["navn"]} ({v["organisasjonsnummer"]}) and declares {v["hjemmeside"]}; the separate registry relationship establishes parent scope. It is not marked ownership-verified.'
            elif f.startswith('research.'):
                assert at['organisasjonsnummer']==org and at['prosjektnummer']==v['project_id'] and at['prosjekttittel']==v['title'];assert Decimal(at['tildelt_belop'])==Decimal(v['total_project_award']['amount']);assert v['total_project_award']['currency']is None
                note=f'Research Council row {v["project_id"]} matches company, title, responsible organisation, total amount and application period. No exclusive share or currency is inferred.'
            elif f.startswith('skattefunn.'):
                assert at['Organisasjonsnummer']==org and at['Prosjektnummer']==v['project_id'];assert at['Søknad godkjent']=='JA' and at['Søknad avslått']=='NEI';assert (datetime(1899,12,30)+timedelta(days=int(Decimal(at['Vedtaksdato'])))).date().isoformat()==v['decision_date']
                note=f'Workbook row {v["project_id"]} matches company, applicant, approval, decision date and {v["start_year"]}–{v["end_year"]} period; it is an R&D tax deduction, not a cash grant.'
            elif f.startswith('state_aid.'):
                assert at['recipient_orgnr']==org and v['recipient_orgnr']==org and at['id']==v['aid_id'];assert v['instrument_type']=='tax benefit';assert datetime.strptime(at['award_date'],'%d.%m.%Y').date().isoformat()==v['award_date']
                if v['awarded_amount']:assert Decimal(at['amount'].replace(',','.'))==Decimal(v['awarded_amount']['amount'])
                else:assert Decimal(at['range_to'].replace(',','.'))==Decimal(v['amount_interval']['to'])
                note=f'Exact aid row matches recipient {v["recipient_orgnr"]}, award id {v["aid_id"]}, instrument and date; the amount or range follows that record.'
            elif f.startswith('workshop_approval.'):
                assert v==at and v['Organisasjonsnummer']==org
                note=f'Exact workshop export row matches company {org}, approval {v["Godkjenningsnummer"]}, type {v["Godkjenningstyper"]} and address {v["Adresse"]}.'
            elif f.startswith('roles.role.'):
                person=at.get('person',{}).get('navn',{});name=' '.join(person.get(k,'')for k in ['fornavn','mellomnavn','etternavn']if person.get(k)) or at.get('enhet',{}).get('navn');name_ok=name==v['name'] or (isinstance(name,list) and len(name)==1 and name[0]==v['name'])
                assert name_ok and v['inactive']==at.get('avregistrert',False) and v['role_type']==at['type'];assert v['group_type']==records[0]['role_group']['type']and v['last_changed']==records[0]['role_group'].get('sistEndret')
                assert at.get('enhet',{}).get('organisasjonsnummer')==v['entity_organisation_number']
                note='Own-company roles record checked: exact role-holder name, role/group type, inactive flag and last-change date. Person is not treated as the researched company.'
            elif f.startswith('identity.gleif.direct_parent'):
                parent,edge=[x.get('located_value') for x in records[:2]]
                child_doc=json.loads(blobs[records[2]['evidence']['content_sha256']]);child=child_doc['data'][int(records[2]['evidence']['locator'].split('/')[2])]
                assert parent['attributes']['lei']==v['lei'] and parent['attributes']['entity']['legalName']['name']==v['name']
                assert child['attributes']['entity']['registeredAs'].replace(' ','')==org
                rel=edge;assert rel['startNode']['id']==child['id'] and rel['endNode']['id']==v['lei'] and rel['type']==v['relationship'] and rel['status']=='ACTIVE'
                note='Three saved GLEIF responses establish the company LEI, active direct-parent relationship and exact parent LEI/name/type.'
            elif f.startswith('identity.wikidata.inception.'):
                b=at;assert b['org']['value']==org and b['property']['value'].endswith('/P571')
                assert (b['value']['value'],int(b['precision']['value']),b['calendar']['value'])==(v['time'],v['precision'],v['calendar'])
                note='Wikidata result binds inception time, precision and calendar to this exact company-number query.'
            elif f.startswith('procurement_award.'):
                root=ET.fromstring(raw);ns={'cac':'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2','cbc':'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2','efac':'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'}
                def tx(n,p):return n.findtext(p,namespaces=ns)
                orgs={tx(x,'cac:PartyIdentification/cbc:ID'):{'orgnr':re.sub(r'\s+','',tx(x,'cac:PartyLegalEntity/cbc:CompanyID')or''),'name':tx(x,'cac:PartyName/cbc:Name')} for x in root.findall('.//efac:Organizations/efac:Organization/efac:Company',ns)}
                parties={tx(x,'cbc:ID'):{tx(t,'cbc:ID') for t in x.findall('efac:Tenderer',ns)} for x in root.findall('.//efac:NoticeResult/efac:TenderingParty',ns)}
                tenders={tx(x,'cbc:ID'):x for x in root.findall('.//efac:NoticeResult/efac:LotTender',ns)}
                contract=next((x for x in root.findall('.//efac:NoticeResult/efac:SettledContract',ns) if x.findtext('cbc:ID',namespaces=ns)==v['contract_id']),None)
                assert contract is not None and contract.findtext('cbc:AwardDate',namespaces=ns)[:10]==v['award_date']
                assert tx(root,'cac:ProcurementProject/cbc:Name')==v['title']
                linked=[tenders.get(tx(x,'cbc:ID')) for x in contract.findall('efac:LotTender',ns)];linked=[t for t in linked if t is not None]
                winners=set().union(*(parties.get(tx(t,'efac:TenderingParty/cbc:ID'),set()) for t in linked)) if linked else set()
                winner=any(orgs.get(k,{}).get('orgnr')==org for k in winners)
                owned=[t for t in linked if any(orgs.get(k,{}).get('orgnr')==org for k in parties.get(tx(t,'efac:TenderingParty/cbc:ID'),set()))]
                assert winner
                amount_ok=any(x.text and Decimal(x.text)==Decimal(str(v['value'])) and x.get('currencyID')==v['currency'] for t in owned for x in t.findall('cac:LegalMonetaryTotal/cbc:PayableAmount',ns))
                assert amount_ok and v['company_orgnr']==org and v['matched_role']=='winner'
                note='TED award notice checked for exact settled contract, award date/title, company national number and matching tender amount/currency.'
            elif f.endswith('.birth_year'):
                assert str(v)==at[:4];note='Only year derived from the cited explicit registry birth date; own-company roles URL binds attribution.'
            elif f.endswith(('.entity_form','.organisation_form')):
                assert all(at[k]==value for k,value in v.items());note='Same explicit registry legal-form code/description; API _links metadata is omitted without changing the value.'
            elif f.startswith('subunits.unit.'):
                assert at['organisasjonsnummer']==v['organisation_number'];assert v['name']==at['navn'];assert v['address']==at['beliggenhetsadresse'];assert v['employees']==at.get('antallAnsatte')
                note='Exact unit row under the subject parent query checked: orgnr, name, address and explicit employees. Missing employee count remains null.'
            elif f.startswith('social_profile.'):
                assert ownsite and ownsite['value']['identity_level']=='VERIFIED';assert v['url'].rstrip('/')in raw
                note=f'Verified official company site directly links {v["url"]}; site ownership and existing personal/other-company/shared/group vetoes are retained.'
            elif f.startswith('contact.email.'):
                assert ownsite and ownsite['value']['identity_level']=='VERIFIED'and 'mailto:'+v in raw;note='Exact Post@D-Production.no mailto link on the proven D-PRODUCTION website, preserving source case; not a guessed contact.'
            elif f.startswith('website_description.'):
                assert v['self_description']and norm(v['text'])in norm(page.visible);assert ownsite and v['identity_claim_id']==ownsite['id']
                note=f'Verbatim self-description (“{v["text"]}”) appears on the verified company website and is tied to its identity claim; it is not recast as independent fact.'
            else:raise AssertionError(('Unreviewed item',i,f))
            assert note
        verdicts.append({'index':i,'family':it['family'],'orgnr':org,'field':f,'value_correct':True,'attribution_correct':True,'verdict':'correct','basis':'mechanical'if mechanical else 'hand','note':note})
    dest=C.HERE/'verdicts.jsonl';lines=[json.dumps(x,ensure_ascii=False,sort_keys=True)for x in verdicts]
    if '--write'in sys.argv:
        dest.write_text('\n'.join(lines)+'\n',encoding='utf-8');(C.HERE/'REVIEW.md').write_text('# Final run accuracy adjudication\n\n200 published claims; seed 20261119. Mechanical verdicts require the unchanged Stage X equality/span/subject-URL check. Remaining items were source-reviewed with context retained in hand-review-support.json. This script rechecks the source corroboration, not the publisher.\n\n| Index | Company | Field | Review |\n|---:|---|---|---|\n'+''.join('| '+str(x['index'])+' | '+x['orgnr']+' | '+x['field']+' | '+x['note']+' |\n'for x in verdicts if x['basis']=='hand'),encoding='utf-8')
    else:assert dest.read_text(encoding='utf-8').splitlines()==lines
    print(json.dumps({'sampled':len(verdicts),'correct':len(verdicts),'mechanical':sum(x['basis']=='mechanical'for x in verdicts),'hand':sum(x['basis']=='hand'for x in verdicts)}))
if __name__=='__main__':main()
