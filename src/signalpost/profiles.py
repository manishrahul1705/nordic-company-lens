"""Reference-runner raw profiles projected only from verified envelope claims."""
import json
import os
from pathlib import Path

MODULES = {'registry_live':'identity', 'financials':'accounts', 'roles':'roles',
           'locations':'subunits', 'website':'website', 'hiring':'hiring', 'activity':'activity'}
STATUS = {'available':'available', 'not_available':'not_found', 'not_applicable':'not_applicable',
          'failed':'source_error', 'ambiguous':'source_error', 'blocked':'blocked'}
IDENTITY = {'organisation_number':None, 'name':'legal_name', 'legal_form':'organisation_form',
            'employees':'employees','bankrupt':'bankrupt','liquidating':'under_liquidation',
            'website':'registered_website','industry':'nace1','business_address':'registered_address',
            'postal_address':'postal_address','latest_submitted_accounts':'latest_submitted_accounts'}
FINANCIAL = {'revenue':'revenue','operating_result':'operating_result','profit_before_tax':'result_before_tax',
             'annual_result':'net_result','assets':'total_assets','equity':'equity','debt':'total_liabilities'}


def project(envelope):
    claims = [c for c in envelope.claims if c.availability == 'available']
    fields = {c.field:c for c in claims}
    def value(field): return fields[field].value if field in fields else None
    registry = {key:value('identity.'+field) if field else None for key,field in IDENTITY.items()}
    if 'identity.legal_name' in fields:
        registry['organisation_number'] = envelope.organisation_number
    form=registry['legal_form']
    if isinstance(form,dict): registry['legal_form']=form.get('kode')
    roles=[]
    for c in claims:
        if not c.field.startswith('roles.role.') or not isinstance(c.value,dict):continue
        v=c.value;role=v.get('role_type') or {};group=v.get('group_type') or {}
        roles.append({'name':v.get('name'),'organisation_number':v.get('entity_organisation_number'),
                      'role_code':role.get('kode'),'role':role.get('beskrivelse'),
                      'group_code':group.get('kode'),'group':group.get('beskrivelse'),
                      'last_changed':v.get('last_changed'),'inactive':v.get('inactive')})
    locations=[]
    for c in claims:
        if not c.field.startswith('subunits.unit.') or not isinstance(c.value,dict):continue
        v=c.value;raw=v.get('raw') or v
        locations.append({'organisation_number':v.get('organisation_number'),'name':v.get('name'), 'type':'workplace',
                          'address':raw.get('beliggenhetsadresse') or raw.get('postadresse') or v.get('address'),
                          'industry':raw.get('naeringskode1') or v.get('nace') or v.get('industry'),
                          'employees':raw.get('antallAnsatte') if 'antallAnsatte' in raw else v.get('employees')})
    from .locations import registered_location
    business = registered_location(envelope.claims)
    if business:
        locations.append({'organisation_number':envelope.organisation_number,'name':'Registered business address',
                          'type':'registered_business_address','address':business.value,'industry':None,'employees':None})
    # Postal addresses are already supported individual registry claims. Expose
    # each distinct place without duplicating a workplace/business address.
    from .locations import address_key
    seen_addresses={address_key(p['address']) for p in locations if address_key(p['address'])}
    postal_locations=[]
    for c in claims:
        parent=c.field=='identity.postal_address'
        branch=c.field.startswith('subunits.detail.') and c.field.endswith('.postal_address')
        if not (parent or branch) or not isinstance(c.value,dict):continue
        key=address_key(c.value)
        if not key or key in seen_addresses:continue
        seen_addresses.add(key)
        postal_locations.append(c)
        number=envelope.organisation_number if parent else c.field.split('.')[2]
        locations.append({'organisation_number':number,'name':'Registered postal address' if parent else 'Subunit postal address',
                          'type':'registered_postal_address' if parent else 'subunit_postal_address','address':c.value,'industry':None,'employees':None})
    account_claims = [c for c in claims if c.family == 'accounts' and not c.field.startswith('accounts.consolidated.')]
    financials = []
    years=sorted({str((c.reporting_period or {}).get('fiscal_year')) for c in account_claims if (c.reporting_period or {}).get('fiscal_year')},reverse=True)
    for y in years:
        selected=[c for c in account_claims if str((c.reporting_period or {}).get('fiscal_year'))==y]
        period=selected[0].reporting_period or {}
        amounts={c.field.rsplit('.',1)[-1]:c.value for c in selected}
        financials.append({'record_id':None,'account_type':period.get('account_type'),
                          'period':{'fraDato':period.get('period_start'),'tilDato':period.get('period_end')},
                          'currency':period.get('currency'),'unit':period.get('unit'),
                          **{key:amounts.get(field) for key,field in FINANCIAL.items()}})
    if len(financials)>=2:
        from .sources.financial_comparability import compare_periods
        comp=compare_periods(financials[0],financials[1],org=envelope.organisation_number,metric='revenue')
        financials[0]['comparability_with_prior']={'comparable':comp.comparable,'reason_codes':comp.reason_codes,'growth_rate':comp.growth_rate,'nominal_change':comp.nominal_change}
    consolidated=[]
    for y in sorted({c.field.split('.')[2] for c in claims if c.field.startswith('accounts.consolidated.')},reverse=True):
        selected=[c for c in claims if c.field.startswith('accounts.consolidated.'+y+'.')]
        period=selected[0].reporting_period or {}
        consolidated.append({'account_type':'KONSERN','period':{'fraDato':period.get('period_start'),'tilDato':period.get('period_end')},
                             'currency':period.get('currency'),'unit':period.get('unit'),
                             **{c.field.split('.',3)[3]:c.value for c in selected}})
    # Include every same-year company amount/statement attribute without mixing group accounts.
    for record in financials:
        year=str((record.get('period') or {}).get('tilDato') or '')[:4]
        for c in account_claims:
            if str((c.reporting_period or {}).get('fiscal_year'))!=year:continue
            if c.field.startswith(('accounts.statement.','accounts.additional.')):record[c.field.split('.',3)[3]]=c.value
            else:record.setdefault(c.field.rsplit('.',1)[-1],c.value)
    website=value('official_website')
    values={'registry_live':registry if registry['organisation_number'] else None,
            'financials':{'records':financials,'consolidated_records':consolidated} if financials or consolidated else None,
            'roles':{'roles':roles} if roles else None,'locations':{'locations':locations} if locations else None,
            'website':website,'hiring':{'jobs':[c.value for c in claims if c.family=='hiring']} or None,
            'activity':{'items':[c.value for c in claims if c.family=='activity']} or None}
    records={e.id:e for e in envelope.evidence};evidence={}
    for module,family in MODULES.items():
        selected=[c for c in claims if c.family==family]
        if module == 'locations' and business:
            selected = selected + [business]
        if module == 'locations':selected=selected+postal_locations
        ids=list(dict.fromkeys(eid for c in selected for eid in c.evidence_ids))
        primary=records[ids[0]] if ids else None
        state=envelope.run.sections.get(family,'not_applicable')
        if module == 'locations' and (business or postal_locations) and state in {'not_available','not_applicable'}:
            state = 'available'
        # No collection zero or empty list is invented when work did not complete.
        payload=values[module] if selected else None
        if not selected and state=='not_available' and module in {'roles','locations','hiring','activity'}:
            payload={ {'roles':'roles','locations':'locations','hiring':'jobs','activity':'items'}[module]:[] }
        evidence[module]={'field':module,'status':STATUS[state],
                          'source_type':primary.source_class if primary else family,
                          'source_class':primary.source_class if primary else family,
                          'source_url':primary.source_url if primary else '',
                          'retrieved_at':primary.retrieved_at if primary else envelope.completed_at,
                          'value':payload,'as_of':None,
                          'note':'Projected from verified claims; section coverage: '+state,
                          'content_sha256':primary.content_sha256 if primary else None,
                          'source_row_key':envelope.organisation_number if primary else None,
                          'effective_at':primary.effective_at if primary else None}
    # Lossless value/provenance index; module views never add facts absent here.
    verified=[{'id':c.id,'field':c.field,'value':c.value,'evidence_ids':c.evidence_ids} for c in claims]
    detailed=[{**v,'family':c.family,'reporting_period':c.reporting_period,'label':c.reasons.get('label',c.field.rsplit('.',1)[-1].replace('_',' ').capitalize())} for v,c in zip(verified,claims)]
    ids={eid for c in claims for eid in c.evidence_ids}
    provenance={eid:records[eid].model_dump(mode='json') for eid in sorted(ids)}
    return {'organisation_number':envelope.organisation_number,'name':value('identity.legal_name'),
            'municipality':value('identity.municipality'),'website':website.get('final_url') if isinstance(website,dict) else None,
            'evidence':evidence,'verified_claims':verified,'claims_by_section':{module:[c for c in detailed if c['family']==family] for module,family in MODULES.items()},'source_records':provenance}


def write(path, envelopes):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    temporary=path.with_name(path.name+'.tmp')
    with temporary.open('w',encoding='utf8',newline='\n') as handle:
        for envelope in envelopes:
            handle.write(json.dumps(project(envelope),ensure_ascii=False,separators=(',',':'),allow_nan=False)+'\n')
        handle.flush();os.fsync(handle.fileno())
    os.replace(temporary,path)
    return {'state':'available','rows':len(envelopes),'bytes':path.stat().st_size}
