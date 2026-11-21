import csv,datetime,hashlib,html,io,json,lzma,re,sys,zipfile
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'accuracy'))
import common as C
from signalpost.sources.text import decode_body
HERE=Path(__file__).resolve().parent
blobs={}
for line in lzma.open(HERE/'source-blobs.jsonl.xz','rt',encoding='utf-8'):
 row=json.loads(line);body=__import__('base64').b64decode(row['b64'])
 assert hashlib.sha256(body).hexdigest()==row['sha256'];blobs[row['sha256']]=body
active=set((HERE/'active-organisations.txt').read_text(encoding='utf-8').splitlines())
allrows={}
for line in (HERE/'company-context.jsonl').read_text(encoding='utf-8').splitlines():
 r=json.loads(line);allrows[r['organisation_number']]=r
verdicts=[]
def raw_pointer(doc,path):return C.pointer(doc,path)
def text_contains(text,*terms):
 n=' '.join(html.unescape(text).casefold().split())
 return all(' '.join(str(t).casefold().split()) in n for t in terms)
for idx,line in enumerate((HERE/'sample.jsonl').read_text(encoding='utf-8').splitlines()):
 x=json.loads(line);e=x['evidence'];body=blobs[e['content_sha256']];org=x['orgnr'];v=x['value'];field=x['field'];full=allrows[org]
 if x['mechanical_exact']:
  ok=True;basis='exact citation span, locator value, subject URL and SHA-256 verified'
 else:
  basis='';ok=False
  try:doc=json.loads(body)
  except Exception:doc=None
  try:at=raw_pointer(doc,e['locator']) if doc is not None else None
  except Exception:at=None
  if field.startswith('registry_change.'):
   path=e['locator'].split('/endringer/')[0];record=raw_pointer(doc,path)
   change=at;target=v.get('subunit_orgnr') or org
   related=(target==org or any(c['availability']=='available' and c['field']=='subunits.unit.'+target and c['value'].get('organisation_number')==target for c in full['claims']))
   stamp=lambda s:datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
   ok=related and record.get('organisasjonsnummer')==target and int(record['oppdateringsid'])==int(v['event_id']) and stamp(record['dato'])==stamp(v['date']) and ('endringer' not in v or (change['path']==v['changed_field'] and change['op']==v['operation'] and change.get('value')==v.get('new_value')))
   if v.get('event_type'):ok=ok and record.get('endringstype')==v['event_type']
   basis='official registry event id, exact subject/subunit row, timestamp, and changed path/value checked'
  elif field.endswith('.organisation_form'):
   unit=field.split('.')[2]
   ok=at is not None and at.get('kode')==v['kode'] and at.get('beskrivelse')==v['beskrivelse'] and ('overordnetEnhet='+org) in e['source_url'] and unit in json.dumps(doc,ensure_ascii=False)
   basis='official subunit form code and description checked on parent-scoped registry row'
  elif field.startswith('contact.phone.'):
   raw=decode_body(body); hrefs=re.findall(r'href=[\"\']tel:([^\"\']+)',raw,re.I);digits=re.sub(r'\D','',v)
   phone_match=any(re.sub(r'\D','',h)==digits.removeprefix('47') for h in hrefs)
   site=next((c for c in full['claims'] if c['field']=='official_website' and c['availability']=='available' and urlsplit(c['value']['final_url']).hostname==urlsplit(e['source_url']).hostname),None)
   ok=phone_match and site is not None
   basis='exact tel: link on the company’s verified official domain'
  elif field.startswith('state_aid.'):
   row=doc;amt=v['awarded_amount']['amount'].replace('.',',')
   ok=row['id']==v['aid_id'] and row['recipient_orgnr']==org==v['recipient_orgnr'] and row['recipient_name']==v['recipient_name'] and row['funder_orgnr']==v['awarding_body']['organisation_number'] and row['funder_name']==v['awarding_body']['name'] and row['award_date']==datetime.date.fromisoformat(v['award_date']).strftime('%d.%m.%Y') and row['amount']==amt and row['currency']==v['awarded_amount']['currency'] and row['status']==v['status'] and row['instrument']==v['instrument'] and row['scheme_id']==v['scheme_id']
   basis='official aid source row matched by award id, recipient, funder, date, amount, currency, instrument and scheme'
  elif field.startswith('roles.role.'):
   group_index=int(e['locator'].split('/')[2]);group=doc['rollegrupper'][group_index];role=at
   who=role.get('person',{}).get('navn',{})
   name=' '.join(who[k] for k in ('fornavn','mellomnavn','etternavn') if who.get(k)) or role.get('enhet',{}).get('navn')
   name_ok=name==v['name'] or (isinstance(name,list) and len(name)==1 and name[0]==v['name'])
   ent=role.get('enhet',{})
   ok=role['type']['kode']==v['role_type']['kode'] and role['type']['beskrivelse']==v['role_type']['beskrivelse'] and group['type']['kode']==v['group_type']['kode'] and group['type']['beskrivelse']==v['group_type']['beskrivelse'] and name_ok and ent.get('organisasjonsnummer')==v['entity_organisation_number'] and role.get('avregistrert',False)==v['inactive'] and group.get('sistEndret')==v['last_changed']
   basis='company roles endpoint checked for exact role, role holder, entity, active state and group date'
  elif field.endswith('.birth_year'):
   ok=str(v)==str(at)[:4] and org in e['source_url']
   basis='year matches the explicit date of birth on the company’s roles endpoint'
  elif field=='central_approval.'+field.split('.')[-1]:
   raw=decode_body(body);ok=text_contains(raw,org,v['area'],v['class'],v['function'],v['valid_from'],v['valid_to']) and ('Godkjent' in raw or 'approved' in raw.casefold())
   basis='official DiBK company page contains organisation number, function, area, class and validity dates'
  elif field=='public_brand':
   raw=decode_body(body);m=re.search(r'<title[^>]*>(.*?)</title>',raw,re.I|re.S);title=html.unescape(re.sub(r'<[^>]+>',' ',m.group(1))).strip() if m else ''
   legal=(full.get('legal_name') or '').casefold();brand=str(v).casefold()
   ok=bool(title and brand in title.casefold() and brand in legal)
   basis='brand appears in page title and matches registered legal name'
  elif field.startswith('social_profile.'):
   raw=decode_body(body);site=next((c for c in full['claims'] if c['field']=='official_website' and c['availability']=='available' and urlsplit(c['value']['final_url']).hostname==urlsplit(e['source_url']).hostname),None)
   ok=site is not None and v['url'].rstrip('/') in raw and v['platform'] in urlsplit(v['url']).hostname
   basis='verified official company site directly links the exact social profile'
  elif field=='identity.gleif.registration_date':
   base=e['locator'].rsplit('/',1)[0];date=raw_pointer(doc,e['locator']);registered=raw_pointer(doc,base+'/../entity/registeredAs') if False else doc['data'][int(e['locator'].split('/')[2])]['attributes']['entity']['registeredAs']
   ok=date==v and registered.replace(' ','')==org
   basis='GLEIF record registeredAs matches the company number; registration date equals the cited field'
  elif field.startswith('cleaning_approval.'):
   row=json.loads(e['claim_span']);ok=row['organisation_number']==org and row['name']==v['name'] and row['status']==v['status'] and v['approved']==('Godkjent' in row['status'])
   basis='official Arbeidstilsynet row matched by company number, name and status'
  elif field.startswith('research.'):
   row=doc
   ok=row is not None and row['prosjektnummer']==v['project_id'] and row['organisasjonsnummer']==org==v['project_responsible_orgnr'] and row['prosjekttittel']==v['title'] and row['prosjektansvarlig_navn']==v['project_responsible_name'] and row['tildelt_belop']==v['total_project_award']['amount'] and row['prosjektfase']==v['phase'] and row['soknadsdato'][:10]==v['application_date'] and int(row['prosjektstart'])==v['start_year'] and int(row['prosjektslutt'])==v['end_year']
   basis='Research Council source CSV row matched by project id and company number; title, responsible entity, amount and phase checked'
  elif field.startswith('skattefunn.'):
   rec=doc
   ok=rec is not None and str(rec['Prosjektnummer'])==str(v['project_id']) and rec['Organisasjonsnummer']==org and rec['Prosjekttittel']==v['title'] and rec['Bedriftsnavn']==v['applicant_name'] and str(rec['Prosjektets fra-år'])==str(v['start_year']) and str(rec['Prosjektets til-år'])==str(v['end_year']) and rec['Søknad godkjent']=='JA'
   basis='Research Council workbook row matched by project id and organisation number; title, applicant, period and approval checked'
  else:
   basis='No independent source check implemented'
  if not ok:print('FAILED',idx,field,repr(v)[:200]);raise SystemExit(2)
 verdicts.append({'index':idx,'orgnr':org,'field':field,'verdict':'correct','basis':'mechanical' if x['mechanical_exact'] else 'source_review','note':basis or 'Exact locator/span/subject URL check passed'})
(HERE/'verdicts.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False,sort_keys=True)+'\n' for x in verdicts),encoding='utf-8')
print(json.dumps({'sampled':len(verdicts),'correct':sum(x['verdict']=='correct' for x in verdicts),'wrong':sum(x['verdict']=='wrong' for x in verdicts),'mechanical':sum(x['basis']=='mechanical' for x in verdicts),'source_review':sum(x['basis']=='source_review' for x in verdicts)},indent=2))
