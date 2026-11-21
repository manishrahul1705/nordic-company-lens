"""Additional facts from already fetched registry bodies; no network access."""
import re
from datetime import date
from ..models.evidence import digest, canonical
from .extract import Section, add

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
    existing={e.locator for e in section.evidence if e.content_sha256==source.sha}
    for address, prefix in (('forretningsadresse','business_address'),('postadresse','postal_address')):
        item=raw.get(address)
        if not isinstance(item,dict):continue
        lines=item.get('adresse')
        if isinstance(lines,list):
            for index,value in enumerate(lines):
                _scalar(section,source,org,'identity',f'identity.{prefix}.line.{index}',value,
                        f'/{address}/adresse/{index}',existing)
        elif isinstance(lines,str):
            _scalar(section,source,org,'identity',f'identity.{prefix}.line.0',lines,
                    f'/{address}/adresse',existing)
        for key,name in (('postnummer','postal_code'),('poststed','postal_town'),
                         ('kommunenummer','municipality_code'),('land','country_name')):
            _scalar(section,source,org,'identity',f'identity.{prefix}.{name}',item.get(key),
                    f'/{address}/{key}',existing)
        if address=='postadresse':
            _scalar(section,source,org,'identity','identity.postal_address.municipality',
                    item.get('kommune'),f'/{address}/kommune',existing)
    for object_key,prefix,keys in (
        ('organisasjonsform','organisation_form',('kode','beskrivelse')),
        ('naeringskode1','industry1',('kode','beskrivelse')),
        ('naeringskode2','industry2',('kode','beskrivelse')),
        ('naeringskode3','industry3',('kode','beskrivelse')),
        ('institusjonellSektorkode','institutional_sector',('kode','beskrivelse')),
        ('hjelpeenhetskode','support_unit_code',('kode','beskrivelse')),
        ('kapital','registered_capital',('belop','antallAksjer','type','bundet','valuta','innbetalt','fulltInnbetalt','innfortDato'))):
        item=raw.get(object_key)
        if not isinstance(item,dict):continue
        for key in keys:
            _scalar(section,source,org,'identity',f'identity.{prefix}.{key}',item.get(key),
                    f'/{object_key}/{key}',existing)


def _scalar(section,source,org,family,field,value,locator,existing,reporting=None,effective=None):
    """Publish a sourced leaf once, without creating null or composite claims."""
    if locator in existing or value is None or value=='' or isinstance(value,(dict,list)):
        return
    add(section,source,org,family,field,value,locator,reporting=reporting,effective=effective)
    existing.add(locator)
    label(section)


def role_group_scalars(section,source,org,group,index):
    existing={e.locator for e in section.evidence if e.content_sha256==source.sha}
    base=f'/rollegrupper/{index}'
    kind=group.get('type') or {}
    for key in ('kode','beskrivelse'):
        _scalar(section,source,org,'roles',f'roles.group.{index}.type_{key}',
                kind.get(key),f'{base}/type/{key}',existing)
    _scalar(section,source,org,'roles',f'roles.group.{index}.last_changed',
            group.get('sistEndret'),f'{base}/sistEndret',existing)


def role_type_scalars(section,source,org,item,group_index,role_index,key,slot):
    existing={e.locator for e in section.evidence if e.content_sha256==source.sha}
    kind=item.get('type') or {}
    base=f'/rollegrupper/{group_index}/roller/{role_index}'
    prefix=f'roles.detail.{key}.{slot}'
    for part in ('kode','beskrivelse'):
        _scalar(section,source,org,'roles',f'{prefix}.role_type_{part}',
                kind.get(part),f'{base}/type/{part}',existing)
    for part,field in (('avregistrert','inactive'),('fraDato','from_date')):
        _scalar(section,source,org,'roles',f'{prefix}.{field}',item.get(part),f'{base}/{part}',existing)
    holder=item.get('enhet') or {}
    if isinstance(holder,dict):
        for part in ('organisasjonsnummer','navn'):
            _scalar(section,source,org,'roles',f'{prefix}.holder_{part}',holder.get(part),
                    f'{base}/enhet/{part}',existing)
        form=holder.get('organisasjonsform') or {}
        if isinstance(form,dict):
            for part in ('kode','beskrivelse'):
                _scalar(section,source,org,'roles',f'{prefix}.holder_form_{part}',form.get(part),
                        f'{base}/enhet/organisasjonsform/{part}',existing)
    elected=item.get('valgtAv') or {}
    if isinstance(elected,dict):
        for part in ('kode','beskrivelse'):
            _scalar(section,source,org,'roles',f'{prefix}.elected_by_{part}',elected.get(part),
                    f'{base}/valgtAv/{part}',existing)


def subunit_scalars(section,source,org,raw,loc,key):
    existing={e.locator for e in section.evidence if e.content_sha256==source.sha}
    prefix=f'subunits.detail.{key}'
    for object_key,fields in (
        ('beliggenhetsadresse',('postnummer','poststed','kommune','kommunenummer','land','landkode')),
        ('postadresse',('postnummer','poststed','kommune','kommunenummer','land','landkode')),
        ('naeringskode1',('kode','beskrivelse')),
        ('naeringskode2',('kode','beskrivelse')),
        ('naeringskode3',('kode','beskrivelse'))):
        item=raw.get(object_key)
        if not isinstance(item,dict):continue
        if object_key.endswith('adresse'):
            lines=item.get('adresse')
            if isinstance(lines,list):
                for index,value in enumerate(lines):
                    _scalar(section,source,org,'subunits',f'{prefix}.{object_key}.line.{index}',
                            value,f'{loc}/{object_key}/adresse/{index}',existing)
            elif isinstance(lines,str):
                _scalar(section,source,org,'subunits',f'{prefix}.{object_key}.line.0',
                        lines,f'{loc}/{object_key}/adresse',existing)
        for part in fields:
            _scalar(section,source,org,'subunits',f'{prefix}.{object_key}.{part}',
                    item.get(part),f'{loc}/{object_key}/{part}',existing)
    if raw.get('harRegistrertAntallAnsatte') is True and not hidden_range(raw.get('antallAnsatte')):
        _scalar(section,source,org,'subunits',f'{prefix}.employees',
                raw.get('antallAnsatte'),f'{loc}/antallAnsatte',existing)
    for object_key in ('organisasjonsform','hjelpeenhetskode'):
        item=raw.get(object_key)
        if isinstance(item,dict):
            for part in ('kode','beskrivelse'):
                _scalar(section,source,org,'subunits',f'{prefix}.{object_key}.{part}',
                        item.get(part),f'{loc}/{object_key}/{part}',existing)

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
        for name,key in (('filing_id','id'),('journal_number','journalnr')):
            _scalar(section,source,org,'accounts',prefix+'.'+name,row.get(key),
                    f'/{idx}/{key}',existing,reporting=period,effective=end)
        unaudited=get(row,('revisjon','ikkeRevidertAarsregnskap'))
        opted_out=get(row,('revisjon','fravalgRevisjon'))
        audited=get(row,('revisjon','revidertAarsregnskap'))
        status = None
        if type(unaudited) is bool and type(opted_out) is bool:
            status = 'audit_opted_out' if opted_out else 'not_audited' if unaudited else 'audited'
            if audited is not None and (type(audited) is not bool or audited != (status == 'audited')):
                status = None
        if status is not None:
            audit_section = Section()
            add(audit_section,source,org,'accounts',prefix+'.audit_status',
                status, f'/{idx}/revisjon/fravalgRevisjon',reporting=period,effective=end)
            claim = audit_section.claims[-1]
            supporting = Section()
            add(supporting,source,org,'accounts','audit_status_support',unaudited,
                f'/{idx}/revisjon/ikkeRevidertAarsregnskap',reporting=period,effective=end)
            known_evidence = {e.id for e in section.evidence}
            section.evidence.extend(e for e in audit_section.evidence + supporting.evidence
                                    if e.id not in known_evidence)
            section.claims.append(claim)
            claim.evidence_ids.extend(e.id for e in supporting.evidence)
            label(section,scope+' explicit audit status')
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
