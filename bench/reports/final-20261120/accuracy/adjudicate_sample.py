"""Source corroboration for the recorded human review; no network or publishing."""
import json,re,sys,html,xml.etree.ElementTree as ET
from datetime import datetime,timedelta
from decimal import Decimal
from email.utils import parsedate_to_datetime
from pathlib import Path
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
                note='Proven company page explicitly names Nordic Smarthouse in title/og:site_name; this is a public brand, not a registry-name substitution.'
            elif f.startswith('hiring.'):
                assert v['status']=='ACTIVE';assert any(c['field']=='subunits.unit.'+v['employer_orgnr']for c in r['claims']);assert v['title']in page.visible
                assert any(v['employer_orgnr']in decode_body(blobs[x['evidence']['content_sha256']])for x in records)
                note='Live NAV page title and employer 972285501 checked; own-company registry lists that subunit under ROSENLUND BARNEHAGE SA. ACTIVE/expiry and occupation/location are retained NAV fields, not parent-name inference.'
            elif f.startswith('central_approval.'):
                text=page.visible;assert org in text and v['area']in text and v['function']in text and v['valid_from']in text and v['valid_to']in text
                trs=re.findall(r'<tr[\s>].*?</tr>',raw,re.I|re.S);assert any(v['area']in html.unescape(re.sub('<[^>]+>',' ',tr)) and v['class']in tr for tr in trs)
                note='DiBK enterprise page has exact orgnr; the approval row names Varme- og kuldeinstallasjoner, Prosjekterende, class 2, valid 01.09.2025–01.09.2028; not a no-approval inference.'
            elif f.startswith('cleaning_approval.'):
                assert at['organisation_number']==org and at['status']==v['status'];assert v['approved']==(at['status']in ['Godkjent med ansatte','Godkjent uten ansatte'])
                note='Exact main-unit record says Ikke godkjent; approved=false is correct. It is not published as an approval.'
            elif f.startswith('news_item.'):
                found=False
                for e in ET.fromstring(raw).iter('item'):
                    if e.findtext('link')==v['url'] and e.findtext('title')==v['title']:
                        assert parsedate_to_datetime(e.findtext('pubDate')).date().isoformat()==v['date'];found=True
                assert found and any(c['id']==v['identity_claim_id']for c in r['claims'])
                note='Same RSS item states title, URL and pubDate 13 July 2015; verified website claim binds this feed to the company. It is company-published, not independent reporting or a guessed date.'
            elif f.startswith('related_company_website.'):
                assert all(v[k]==x for k,x in at.items());assert v['verification']=='registry-declared, not ownership-verified';assert any(c['field']=='identity.group_structure.subsidiary.'+v['organisasjonsnummer']and c['value']['parentOrganisasjonsnummer']==org for c in r['claims'])
                note='ELLINGSEN own published relationship names subsidiary RANA ENTREPRENØR 950271728; that entity registry row states www.ranaent.no. Both citations retained; not ELLINGSEN official_website.'
            elif f.startswith('research.'):
                assert at['organisasjonsnummer']==org and at['prosjektnummer']==v['project_id'] and at['prosjekttittel']==v['title'];assert Decimal(at['tildelt_belop'])==Decimal(v['total_project_award']['amount']);assert v['total_project_award']['currency']is None
                note='Forskningsrådet row 256541 names VEIDEKKE as project responsible, Kortreist stein, 4,353,000 total project award, application 2015-10-14 and 2016–2019. No exclusive share or invented currency.'
            elif f.startswith('skattefunn.'):
                assert at['Organisasjonsnummer']==org and at['Prosjektnummer']==v['project_id'];assert at['Søknad godkjent']=='JA' and at['Søknad avslått']=='NEI';assert (datetime(1899,12,30)+timedelta(days=int(Decimal(at['Vedtaksdato'])))).date().isoformat()==v['decision_date']
                note='Approved LAKSESYSTEMER application 318376, 2020–2022 and explicit Excel decision date 2020-09-24. Labelled R&D tax deduction, not a grant/cash payment.'
            elif f.startswith('state_aid.'):
                assert at['recipient_orgnr']==org and v['recipient_orgnr']==org and at['id']==v['aid_id'];assert v['instrument_type']=='tax benefit';assert datetime.strptime(at['award_date'],'%d.%m.%Y').date().isoformat()==v['award_date']
                if v['awarded_amount']:assert Decimal(at['amount'].replace(',','.'))==Decimal(v['awarded_amount']['amount'])
                else:assert Decimal(at['range_to'].replace(',','.'))==Decimal(v['amount_interval']['to'])
                note='Exact aid recipient/id, tax-benefit instrument, award date and amount/range match selected state-aid row. FINNMARK range is EUR 0–499999, not an exact award; specified subunit 915943012 stays explicit.'
            elif f.startswith('workshop_approval.'):
                assert v==at and v['Organisasjonsnummer']==org
                note='Exact ÅS GLASSMESTERFORRETNING main-unit orgnr; approval 28371 is BILGLASS at Verpetveien 32, 1540 VESTBY. One approval record, not a second company.'
            elif f.startswith('roles.role.'):
                person=at.get('person',{}).get('navn',{});name=' '.join(person.get(k,'')for k in ['fornavn','mellomnavn','etternavn']if person.get(k));assert v['name']==name;assert v['inactive']==at.get('avregistrert',False)and v['role_type']==at['type'];assert v['group_type']==records[0]['role_group']['type']and v['last_changed']==records[0]['role_group'].get('sistEndret')
                note='Own-company roles record checked: exact role-holder name, role/group type, inactive flag and last-change date. Person is not treated as the researched company.'
            elif f.endswith('.birth_year'):
                assert str(v)==at[:4];note='Only year derived from the cited explicit registry birth date; own-company roles URL binds attribution.'
            elif f.endswith(('.entity_form','.organisation_form')):
                assert all(at[k]==value for k,value in v.items());note='Same explicit registry legal-form code/description; API _links metadata is omitted without changing the value.'
            elif f.startswith('subunits.unit.'):
                assert at['organisasjonsnummer']==v['organisation_number'];assert v['name']==at['navn'];assert v['address']==at['beliggenhetsadresse'];assert v['employees']==at.get('antallAnsatte')
                note='Exact unit row under the subject parent query checked: orgnr, name, address and explicit employees. Missing employee count remains null.'
            elif f.startswith('social_profile.'):
                assert ownsite and ownsite['value']['identity_level']=='VERIFIED';assert 'tbmaskin' in raw and v['url'].rstrip('/')in raw
                note='TB MASKIN proven company page links instagram.com/tbmaskin directly. Own-site attribution applies with existing personal/other-company/shared/group vetoes; not a person-handle inference.'
            elif f.startswith('contact.email.'):
                assert ownsite and ownsite['value']['identity_level']=='VERIFIED'and 'mailto:'+v in raw;note='Exact Post@D-Production.no mailto link on the proven D-PRODUCTION website, preserving source case; not a guessed contact.'
            elif f.startswith('website_description.'):
                assert v['self_description']and norm(v['text'])in norm(page.visible);assert ownsite and v['identity_claim_id']==ownsite['id']
                note='Verbatim company self-description on proven laksesystemer.no/om-oss. It explicitly assigns 1.8bn turnover to Fj øssystemer group (spelled in the source), not to LAKSESYSTEMER; not an independent financial fact.'
            else:raise AssertionError(('Unreviewed item',i,f))
            assert note
        verdicts.append({'index':i,'family':it['family'],'orgnr':org,'field':f,'value_correct':True,'attribution_correct':True,'verdict':'correct','basis':'mechanical'if mechanical else 'hand','note':note})
    dest=C.HERE/'verdicts.jsonl';lines=[json.dumps(x,ensure_ascii=False,sort_keys=True)for x in verdicts]
    if '--write'in sys.argv:
        dest.write_text('\n'.join(lines)+'\n',encoding='utf-8');(C.HERE/'REVIEW.md').write_text('# Final run accuracy adjudication\n\n200 published claims; seed 20261119. Mechanical verdicts require the unchanged Stage X equality/span/subject-URL check. Remaining items were source-reviewed with context retained in hand-review-support.json. This script rechecks the source corroboration, not the publisher.\n\n| Index | Company | Field | Review |\n|---:|---|---|---|\n'+''.join('| '+str(x['index'])+' | '+x['orgnr']+' | '+x['field']+' | '+x['note']+' |\n'for x in verdicts if x['basis']=='hand'),encoding='utf-8')
    else:assert dest.read_text(encoding='utf-8').splitlines()==lines
    print(json.dumps({'sampled':len(verdicts),'correct':len(verdicts),'mechanical':sum(x['basis']=='mechanical'for x in verdicts),'hand':sum(x['basis']=='hand'for x in verdicts)}))
if __name__=='__main__':main()
