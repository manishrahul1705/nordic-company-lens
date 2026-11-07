"""No new source access: exact saved JSON/CSV spans, entity scope and stable IDs."""
import copy,csv,io,json,hashlib
from types import SimpleNamespace
import pytest
from signalpost.sources.extract import Source,Section
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.http import Response
from signalpost.sources import brreg_enhet,bulk_registry,brreg_roller,brreg_underenheter,regnskap
from signalpost.models.evidence import canonical,digest
from signalpost.runner import placeholder,update
from signalpost.profiles import project
ORG='923609016';OTHER='988330752'

def source(data,url='https://data.brreg.no/enhetsregisteret/api/enheter/'+ORG):
    body=json.dumps(data,ensure_ascii=False,separators=(',',':')).encode()
    return Source(url,body,hashlib.sha256(body).hexdigest(),'2026-11-07T00:00:00Z')

def response(data,url):
    s=source(data,url);return Response(s.body,200,s.url,s.retrieved_at,s.sha)

def values(section):return {c.field:c.value for c in section.claims if c.availability=='available'}

def supported(section,body):
    assert len({c.field for c in section.claims})==len(section.claims)
    assert all(e.claim_span in body.decode() and len(e.claim_span)<=300 for e in section.evidence if e.source_class=="official_registry")

def test_identity_json_missing_country_and_explicit_hidden_range():
    raw={'organisasjonsnummer':ORG,'navn':'Example AS','antallAnsatte':'0?4','harRegistrertAntallAnsatte':False,'forretningsadresse':{'landkode':'NO'},'postadresse':{'landkode':'SE'}}
    s=source(raw);section=brreg_enhet.extract(ORG,raw,s);v=values(section)
    assert v['identity.business_address_country_code']=='NO' and v['identity.postal_address_country_code']=='SE'
    assert v['identity.employee_count_disclosure']=='Employee count not published (0?4 employees)'
    assert 'identity.employees' not in v
    supported(section,s.body)
    raw['antallAnsatte']=0
    v=values(brreg_enhet.extract(ORG,raw,source(raw)))
    assert 'identity.employees' not in v and 'identity.employee_count_disclosure' not in v
    assert 'identity.postal_address_country_code' not in values(brreg_enhet.extract(ORG,{'organisasjonsnummer':ORG},source({'organisasjonsnummer':ORG})))

def test_identity_csv_range_and_dates_keep_existing_ids():
    row={'organisasjonsnummer':ORG,'navn':'Example AS','stiftelsesdato':'2001-01-01','forretningsadresse.landkode':'NO','antallAnsatte':'0-4'}
    out=io.StringIO();w=csv.DictWriter(out,fieldnames=list(row));w.writeheader();w.writerow(row)
    s=Source('https://data.brreg.no/enhetsregisteret/api/enheter/lastned/csv',out.getvalue().encode(),'0'*64,'2026-11-07T00:00:00Z')
    a=bulk_registry.extract(ORG,row,s);b=bulk_registry.extract(ORG,row,s)
    assert values(a)['identity.employee_count_disclosure']=='Employee count not published (0?4 employees)'
    assert [c.id for c in a.claims]==[c.id for c in b.claims]
    supported(a,s.body)
    assert values(a)['identity.founding_date']=='2001-01-01'

def test_roles_birth_year_entity_holder_resignation_and_missing():
    role={'type':{'kode':'VARA','beskrivelse':'Varamedlem'},'person':{'navn':{'fornavn':'Test','etternavn':'Person'},'fodselsdato':'1980-04-03','erDoed':False},'avregistrert':True,'tilDato':'2025-01-02'}
    raw={'organisasjonsnummer':ORG,'rollegrupper':[{'type':{'kode':'STYR'},'roller':[role,{'type':{'kode':'REVI'},'enhet':{'navn':['Audit AS'],'organisasjonsnummer':OTHER}}]}]}
    r=response(raw,brreg_enhet.BASE+ORG+'/roller');a=brreg_roller.extract(ORG,r);b=brreg_roller.extract(ORG,r)
    v=values(a);assert any(k.endswith('.birth_year') and value==1980 for k,value in v.items())
    assert any(k.endswith('.resignation_date') and value=='2025-01-02' for k,value in v.items())
    assert any(isinstance(value,dict) and value.get('entity_organisation_number')==OTHER for value in v.values())
    assert sum(k.endswith('.birth_year') for k in v)==1
    assert [c.id for c in a.claims]==[c.id for c in b.claims];supported(a,r.body)
    assert not any('1980-04-03' in str(c.value) for c in a.claims)

def test_subunit_second_industry_history_range_and_missing():
    unit={'organisasjonsnummer':OTHER,'overordnetEnhet':ORG,'navn':'Branch','antallAnsatte':'0-4','oppstartsdato':'2020-01-01','registreringsdatoEnhetsregisteret':'2020-02-01','naeringskode2':{'kode':'01.100','beskrivelse':'Crops'},'historiskeNavn':[{'navn':'Former Branch','fraDato':'2019-01-01','tilDato':'2020-01-01'}]}
    raw={'_embedded':{'underenheter':[unit]},'page':{'totalPages':1}}
    r=response(raw,'https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet='+ORG);a=Section();brreg_underenheter.extract_page(ORG,r,a,0)
    v=values(a);assert v['subunits.detail.'+OTHER+'.secondary_nace']['kode']=='01.100'
    assert v['subunits.unit.'+OTHER]['employees'] is None
    assert v['subunits.detail.'+OTHER+'.start_date']=='2020-01-01'
    assert any('.historical_name.' in k for k in v)
    assert not any(k.endswith('.tertiary_nace') for k in v);supported(a,r.body)

def account(kind='SELSKAP',year=2025,amount=100):
    return {'regnskapstype':kind,'virksomhet':{'organisasjonsnummer':ORG},'regnskapsperiode':{'fraDato':f'{year}-01-01','tilDato':f'{year}-12-31'},'valuta':'NOK','revisjon':{'ikkeRevidertAarsregnskap':False,'fravalgRevisjon':True},'regnkapsprinsipper':{'smaaForetak':True},'resultatregnskapResultat':{'aarsresultat':amount,'driftsresultat':{'driftsinntekter':{'sumDriftsinntekter':amount}},'ekstraordinaerePoster':0}}

def test_accounts_every_returned_year_group_separate_all_amounts_and_stable_ids(tmp_path):
    raw=[account('SELSKAP',2025,100),account('KONSERN',2025,900),account('SELSKAP',2024,50)]
    raw[0]['eiendeler']={'novelReportedNumericField':7}
    r=response(raw,regnskap.URL+ORG);blobs=BlobStore(tmp_path);a=regnskap.extract(ORG,r,blobs);b=regnskap.extract(ORG,r,blobs);v=values(a)
    assert v['accounts.revenue']==100 and v['accounts.consolidated.2025.revenue']==900
    assert v['accounts.history.2024.revenue']==50
    assert v['accounts.statement.2025.small_company'] is True
    assert v['accounts.statement.2025.audit_opt_out'] is True
    assert 'accounts.statement.2025.audited' not in v  # no audited status invented from opt-out/negative flag
    assert v['accounts.additional.2025.extraordinary_items']==0
    assert any(k.startswith('accounts.additional.2025.additional_amount_') and val==7 for k,val in v.items())
    assert [c.id for c in a.claims]==[c.id for c in b.claims]
    # The pre-Step16 revenue identity uses the original reporting inputs.
    raw_period={'fiscal_year':'2025','period_start':'2025-01-01','period_end':'2025-12-31','currency':'NOK','unit':None,'account_type':'SELSKAP'}
    assert next(c.id for c in a.claims if c.field=='accounts.revenue')==digest([ORG,'accounts.revenue',canonical(100),'available',raw_period])
    supported(a,r.body)
    env=placeholder(ORG,'test','2026-11-07T00:00:00Z',('identity','accounts'));update(env,'accounts',a)
    p=project(env);records=p['evidence']['financials']['value']
    assert records['records'][0]['revenue']==100 and records['consolidated_records'][0]['revenue']==900
    assert all(c['family']=='accounts' for c in p['claims_by_section']['financials'])
    assert all(c['reporting_period'] for c in p['claims_by_section']['financials'])

def test_consolidated_only_and_wrong_company_never_become_parent_company_accounts(tmp_path):
    raw=[account('KONSERN')];r=response(raw,regnskap.URL+ORG);section=regnskap.extract(ORG,r,BlobStore(tmp_path))
    assert not any(c.field=='accounts.revenue' and c.availability=='available' for c in section.claims)
    assert values(section)['accounts.consolidated.2025.net_result']==100
    raw[0]['virksomhet']['organisasjonsnummer']=OTHER
    assert not values(regnskap.extract(ORG,response(raw,regnskap.URL+ORG),BlobStore(tmp_path)))


def test_annual_window_rollover_preserves_old_period_claim_ids_and_evidence(tmp_path):
    from signalpost.refresh.diff import apply
    blobs=BlobStore(tmp_path)
    a=placeholder(ORG,'first','2026-11-07T00:00:00Z',('accounts',))
    update(a,'accounts',regnskap.extract(ORG,response([account(year=2024)],regnskap.URL+ORG),blobs))
    apply(a,None,blobs)
    original=next(c for c in a.claims if c.field=='accounts.statement.2024.currency')
    b=placeholder(ORG,'second','2026-11-08T00:00:00Z',('accounts',))
    update(b,'accounts',regnskap.extract(ORG,response([account(year=2025)],regnskap.URL+ORG),blobs))
    apply(b,a.model_dump(mode='json'),blobs)
    retained=next(c for c in b.claims if c.field==original.field)
    assert retained.id==original.id and retained.evidence_ids==original.evidence_ids
    assert retained.carried_forward
    assert not any(c.type=='removed' and c.field.startswith('accounts.statement.') for c in b.changes)
