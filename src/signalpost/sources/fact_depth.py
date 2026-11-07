"""Additional facts from already fetched registry bodies; no network access."""
import re
from datetime import date
from ..models.evidence import digest, canonical
from .extract import add

IDENTITY_EXTRA={
 'business_address_country_code':('forretningsadresse','landkode'),
 'postal_address_country_code':('postadresse','landkode'),
 'voluntary_vat_descriptions':('frivilligMvaRegistrertBeskrivelser',),
 'registry_annotations':('paategninger',),
}
LABELS={'business_address_country_code':'Business address country code',
 'postal_address_country_code':'Postal address country code','voluntary_vat_descriptions':'Voluntary VAT registration descriptions',
 'registry_annotations':'Registry annotations','birth_year':'Birth year','person_deceased':'Registered as deceased',
 'resignation_date':'Role resignation date','employee_count_disclosure':'Employee count not published (0?4 employees)',
 'secondary_nace':'Secondary registered industry','tertiary_nace':'Third registered industry',
 'historical_name':'Former registered name','insolvency_administrator':'Registered insolvency administrator'}

def label(section,text=None):
    if section.claims:section.claims[-1].reasons['label']=text or LABELS.get(section.claims[-1].field.rsplit('.',1)[-1],section.claims[-1].field.rsplit('.',1)[-1].replace('_',' ').capitalize())

def hidden_range(value):
    return isinstance(value,str) and re.fullmatch(r'\s*0\s*[-??]\s*4(?:\s+(?:ansatte|employees))?\s*',value,re.I) is not None

def disclosure(section,source,org,family,prefix,raw,locator):
    if hidden_range(raw.get('antallAnsatte')):
        add(section,source,org,family,prefix+'.employee_count_disclosure',
            'Employee count not published (0?4 employees)',locator+'/antallAnsatte' if locator else '/antallAnsatte')
        label(section)

def histories(section,source,org,family,prefix,items,locator):
    if not isinstance(items,list):return
    seen=set()
    for i,item in enumerate(items):
        if not isinstance(item,dict) or not item.get('navn'):continue
        value={k:item[k] for k in ('navn','fraDato','tilDato') if item.get(k) is not None}
        key=digest(canonical(value))[:24]
        if key in seen:continue
        seen.add(key)
        add(section,source,org,family,prefix+'.historical_name.'+key,value,locator+'/'+str(i));label(section,'Former registered name')

def identity(section,source,org,raw):
    for name,path in IDENTITY_EXTRA.items():
        value=raw
        for key in path:value=value.get(key) if isinstance(value,dict) else None
        if value is None or value=='':continue
        add(section,source,org,'identity','identity.'+name,value,'/'+'/'.join(path));label(section)
    disclosure(section,source,org,'identity','identity',raw,'')
    histories(section,source,org,'identity','identity',raw.get('historiskeNavn'),'/historiskeNavn')

def birth_year(value):
    if not isinstance(value,str):return None
    try:return date.fromisoformat(value).year
    except ValueError:return None


STATEMENT_META={
 'period_start':('regnskapsperiode','fraDato'),'period_end':('regnskapsperiode','tilDato'),
 'currency':('valuta',),'account_type':('regnskapstype',),'source_unit':('enhet',),
 'unaudited_statement':('revisjon','ikkeRevidertAarsregnskap'),
 'audit_opt_out':('revisjon','fravalgRevisjon'),'audited':('revisjon','revidertAarsregnskap'),
 'small_company':('regnkapsprinsipper','smaaForetak'),
 'accounting_rules':('regnkapsprinsipper','regnskapsregler'),
 'liquidation_accounts':('avviklingsregnskap',),'presentation_plan':('oppstillingsplan',),
 'parent_company':('virksomhet','morselskap'),
 'registered_organisation_form':('virksomhet','organisasjonsform'),
}
EXTRA_AMOUNTS={('resultatregnskapResultat','ekstraordinaerePoster'):'extraordinary_items',
 ('resultatregnskapResultat','skattekostnadEkstraordinaertResultat'):'tax_on_extraordinary_items'}

def numeric_leaves(value,path=()):
    if isinstance(value,dict):
        for key,item in value.items():yield from numeric_leaves(item,path+(key,))
    elif isinstance(value,(int,float)) and not isinstance(value,bool):yield path,value

def accounts(section,org,data,source):
    from .regnskap import PATHS
    from .extract import get
    existing={e.locator for e in section.evidence if e.content_sha256==source.sha}
    indexed=sorted(((i,r) for i,r in enumerate(data) if isinstance(r,dict)),key=lambda pair:(str(get(pair[1],('regnskapsperiode','tilDato')) or ''),str(pair[1].get('journalnr') or ''),pair[0]),reverse=True)
    seen=set()
    for idx,row in indexed:
        if not isinstance(row,dict) or str(get(row,('virksomhet','organisasjonsnummer')))!=org:continue
        kind=row.get('regnskapstype')
        if kind not in {'SELSKAP','KONSERN'}:continue
        end=get(row,('regnskapsperiode','tilDato'))
        try:year=str(date.fromisoformat(end).year)
        except (ValueError,TypeError):continue
        if (kind,year) in seen:continue
        seen.add((kind,year))
        period={'fiscal_year':year,'period_start':get(row,('regnskapsperiode','fraDato')),
                'period_end':end,'currency':row.get('valuta'),'unit':row.get('enhet'),'account_type':kind}
        prefix=f'accounts.consolidated.{year}' if kind=='KONSERN' else f'accounts.statement.{year}'
        scope='Consolidated' if kind=='KONSERN' else 'Company'
        for name,path in STATEMENT_META.items():
            value=get(row,path)
            if value is None:continue
            add(section,source,org,'accounts',prefix+'.'+name,value,f'/{idx}/'+'/'.join(path),reporting=period,effective=end)
            label(section,scope+' '+name.replace('_',' '))
        reverse={path:name for name,path in PATHS.items()}
        for path,value in numeric_leaves(row):
            if not path or path[0] not in {'resultatregnskapResultat','egenkapitalGjeld','eiendeler'}:continue
            loc=f'/{idx}/'+'/'.join(path)
            if loc in existing:continue
            name=reverse.get(path) or EXTRA_AMOUNTS.get(path) or 'additional_amount_'+digest(list(path))[:12]
            field=(prefix+'.'+name) if kind=='KONSERN' else f'accounts.additional.{year}.{name}'
            add(section,source,org,'accounts',field,value,loc,reporting=period,effective=end)
            label(section,scope+' '+('additional reported amount' if name.startswith('additional_amount_') else name.replace('_',' ')))
            if period['unit'] is None:section.claims[-1].reasons['unit']='scale_not_declared_by_source; no consolidated/company calibration inferred'
