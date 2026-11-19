import asyncio
import json
from urllib.parse import urlencode
import httpx
import pytest
from signalpost.budget import Budget
from signalpost.models.evidence import utc_now
from signalpost.runner import placeholder
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.extract import Section, Source, add
from signalpost.web.wikidata import ENDPOINT, query, parse, fetch_batch, publish_social
from signalpost.web.wikidata_facts import publish, GREGORIAN
from tests.test_registry import config, numbers

ORG = '923609016'
POINT = {'pointInTime':'2025-12-31T00:00:00Z','pointPrecision':'11','pointCalendar':GREGORIAN}


def binding(prop, value, **extras):
    result = {key:{'type':'literal','value':value} for key,value in {
        'org':ORG,'item':'http://www.wikidata.org/entity/Q123456','revision':'123456789',
        'property':'http://www.wikidata.org/prop/direct/'+prop,
        'statement':'http://www.wikidata.org/entity/statement/Q123456-'+prop,'value':value,**extras}.items()}
    for key in ('item','property','statement'):
        result[key]['type']='uri'
    if prop in {'P159','P452','P856'}:
        result['value']['type']='uri'
    return result


def setup(tmp_path, bindings, registry=()):
    cfg = config(tmp_path,[ORG],websites=True)
    blobs = BlobStore(cfg.state_dir)
    body = json.dumps({'results':{'bindings':bindings}}).encode()
    sha = blobs.put(body)
    records = parse(body,{ORG})
    for record in records:
        record.update(sha=sha,retrieved_at=utc_now(),source_url=ENDPOINT+'?'+urlencode({'query':query([ORG]),'format':'json'}))
    index = {'records':{ORG:records},'metrics':{'social_published':0}}
    row = placeholder(ORG,'test',utc_now())
    section = Section()
    raw = json.dumps({'organisasjonsnummer':ORG,'navn':'Example AS'}).encode()
    source = Source('https://data.brreg.no/enhetsregisteret/api/enheter/'+ORG,raw,blobs.put(raw),utc_now())
    for entry in registry:
        field,value,*period = entry
        add(section,source,ORG,field.split('.')[0],field,value,'/navn',reporting=period[0] if period else None)
    row.claims,row.evidence = section.claims,section.evidence
    return index,row,blobs


def new_claims(row):
    return [c for c in row.claims if '.wikidata.' in c.field]


@pytest.mark.parametrize('prop,value,extras',[
    ('P1448','Example AS',{}),
    ('P571','1980-01-01T00:00:00Z',{'precision':'9','calendar':GREGORIAN}),
    ('P159','http://www.wikidata.org/entity/Q585',{'valueLabel':'Oslo'}),
    ('P452','http://www.wikidata.org/entity/Q862571',{'valueLabel':'telecommunications'}),
    ('P1128','18',{'unit':'http://www.wikidata.org/entity/Q199',**POINT}),
    ('P2139','12345678901234567890.123',{'unit':'http://www.wikidata.org/entity/Q132643','currencyCode':'NOK',**POINT}),
    ('P856','https://example.no/',{}),
])
def test_properties_preserve_result_and_revision(tmp_path,prop,value,extras):
    index,row,blobs = setup(tmp_path,[binding(prop,value,**extras)])
    publish(index,ORG,row,blobs)
    claims = new_claims(row)
    assert len(claims)==1
    claim = claims[0]
    assert claim.reasons['wikidata_property']==prop
    assert claim.reasons['wikidata_revision']=='123456789'
    e = next(e for e in row.evidence if e.id in claim.evidence_ids)
    assert e.source_url.startswith(ENDPOINT+'?query=')
    assert 'title=Q123456&oldid=123456789' in e.source_identifier
    assert e.locator=='/results/bindings/0'
    assert e.claim_span in (blobs.directory/e.content_sha256).read_text(encoding='utf-8')
    if prop=='P2139':
        assert claim.value['amount']==value and claim.value['currency']=='NOK'
        assert claim.value['point_in_time']['precision']==11
    if prop=='P856':
        assert not any(c.field=='official_website' for c in row.claims)


def test_expanded_query_still_uses_five_requests_for_1000(tmp_path):
    ns=numbers(1000);cfg=config(tmp_path,ns,websites=True,wikidata=True);calls=[]
    def response(request):
        calls.append(request)
        assert request.method=='GET' and request.url.host=='query.wikidata.org'
        text=request.url.params['query']
        for prop in ('P1448','P571','P159','P452','P1128','P2139','P856','P2002','P2003','P2013','P4264'):
            assert 'wdt:'+prop in text
        assert 'pq:P585' in text and 'schema:version' in text and 'wb:quantityUnit' in text
        return httpx.Response(200,json={'results':{'bindings':[]}})
    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(response)) as client:
            return await fetch_batch(ns,client,cfg,Budget(cfg),BlobStore(cfg.state_dir))
    result=asyncio.run(run())
    assert len(calls)==result['metrics']['requests']==5


@pytest.mark.parametrize('key,bad', [('org','993578843'),('item','https://www.wikidata.org/wiki/Q999'),
    ('revision','999'),('value','Other AS'),('locator','/results/bindings/9'),('source_url','https://evil.test/'),('sha','0'*64)])
def test_mutable_index_cannot_override_exact_result_identity(tmp_path,key,bad):
    index,row,blobs=setup(tmp_path,[binding('P1448','Example AS')])
    index['records'][ORG][0][key]=bad
    publish(index,ORG,row,blobs)
    assert not new_claims(row)


def test_foreign_result_is_not_published_even_if_index_uses_our_key(tmp_path):
    b=binding('P1448','Foreign AS');b['org']['value']='993578843'
    index,row,blobs=setup(tmp_path,[b])
    assert not index['records'][ORG]
    publish(index,ORG,row,blobs)
    assert not new_claims(row)


@pytest.mark.parametrize('revision',[None,'','0','-1','bad'])
def test_missing_or_invalid_revision_blocks_facts_and_socials(tmp_path,revision):
    b=binding('P1448','Example AS');s=binding('P2013','example')
    for row in (b,s):
        if revision is None:row.pop('revision')
        else:row['revision']['value']=revision
    index,row,blobs=setup(tmp_path,[b,s],[('identity.legal_name','Example AS')])
    publish(index,ORG,row,blobs);publish_social(index,ORG,row,blobs)
    assert not new_claims(row) and not any(c.field.startswith('social_profile.') for c in row.claims)


@pytest.mark.parametrize('prop',['P1128','P2139'])
def test_quantities_require_point_in_time(tmp_path,prop):
    index,row,blobs=setup(tmp_path,[binding(prop,'100',unit='http://www.wikidata.org/entity/Q132643')])
    publish(index,ORG,row,blobs)
    assert not new_claims(row)
    assert row.run.refresh['wikidata']['withheld']


@pytest.mark.parametrize('value',['-1','NaN','Infinity','1.5'])
def test_invalid_employee_counts_fail_closed(tmp_path,value):
    index,row,blobs=setup(tmp_path,[binding('P1128',value,unit='1',**POINT)])
    publish(index,ORG,row,blobs)
    assert not new_claims(row)


@pytest.mark.parametrize('prop,value,extras,registry',[
    ('P1448','Other AS',{},[('identity.legal_name','Example AS')]),
    ('P571','1900-01-01T00:00:00Z',{'precision':'9','calendar':GREGORIAN},[('identity.founding_date','1980-02-03')]),
    ('P856','https://other.no/',{},[('identity.registered_website','https://example.no/')]),
    ('P1128','18',{'unit':'1',**POINT},[('identity.employees',42),('identity.employee_count_nav_registration_date','2025-12-31')]),
    ('P2139','100',{'unit':'http://www.wikidata.org/entity/Q132643','currencyCode':'NOK',**POINT},
     [('accounts.revenue',200,{'currency':'NOK','unit':'NOK','period_start':'2025-01-01','period_end':'2025-12-31','fiscal_year':'2025'})]),
])
def test_registry_wins_disagreement_and_both_evidence_links_are_recorded(tmp_path,prop,value,extras,registry):
    index,row,blobs=setup(tmp_path,[binding(prop,value,**extras)],registry)
    original={c.field:c.value for c in row.claims}
    publish(index,ORG,row,blobs)
    assert not new_claims(row)
    assert {c.field:c.value for c in row.claims}==original
    conflict=row.run.refresh['wikidata']['disagreements'][0]
    assert conflict['property']==prop and conflict['registry_evidence_ids'] and conflict['wikidata_evidence_ids']
    assert set(conflict['wikidata_evidence_ids'])<={e.id for e in row.evidence}


def test_older_employee_measure_is_dated_history_not_a_current_override(tmp_path):
    point={'pointInTime':'2023-01-01T00:00:00Z','pointPrecision':'9','pointCalendar':GREGORIAN}
    index,row,blobs=setup(tmp_path,[binding('P1128','18',unit='1',**point)],
        [('identity.employees',42),('identity.employee_count_nav_registration_date','2026-01-01')])
    publish(index,ORG,row,blobs)
    assert len(new_claims(row))==1
    assert next(c.value for c in row.claims if c.field=='identity.employees')==42
    assert new_claims(row)[0].value['point_in_time']['precision']==9
    assert not row.run.refresh['wikidata']['disagreements']
    assert row.run.refresh['wikidata']['comparisons'][0]['status']=='different_values_different_or_unknown_dates'


def test_year_precision_is_not_invented_day_precision(tmp_path):
    index,row,blobs=setup(tmp_path,[binding('P571','1980-01-01T00:00:00Z',precision='9',calendar=GREGORIAN)],
        [('identity.founding_date','1980-08-22')])
    publish(index,ORG,row,blobs)
    assert len(new_claims(row))==1 and new_claims(row)[0].value['precision']==9
    assert not row.run.refresh['wikidata']['disagreements']


def test_labels_do_not_multiply_headquarters_claims(tmp_path):
    a=binding('P159','http://www.wikidata.org/entity/Q585',valueLabel='Oslo')
    a['valueLabel']['xml:lang']='nb'
    b=json.loads(json.dumps(a));b['valueLabel']['xml:lang']='en'
    index,row,blobs=setup(tmp_path,[b,a])
    publish(index,ORG,row,blobs)
    assert len(new_claims(row))==1 and new_claims(row)[0].value['label_language']=='nb'


def test_existing_social_gets_revision_evidence_without_duplicate_claim(tmp_path):
    index,row,blobs=setup(tmp_path,[binding('P2013','example')],[('identity.legal_name','Example AS')])
    section=Section();body=b'https://www.facebook.com/example'
    src=Source('https://example.no/',body,blobs.put(body),utc_now())
    add(section,src,ORG,'website','social_profile.existing',{'url':body.decode(),'platform':'facebook.com'},'/',source_class='company_owned')
    row.claims.extend(section.claims);row.evidence.extend(section.evidence)
    original_id=section.claims[0].id
    publish_social(index,ORG,row,blobs)
    social=[c for c in row.claims if c.field.startswith('social_profile.')]
    assert len(social)==1 and social[0].id==original_id and len(social[0].evidence_ids)==2
    assert index['metrics']['social_published']==0 and index['metrics']['social_corroborated']==1
    ev=next(e for e in row.evidence if e.source_class=='wikidata')
    from scripts.accuracy_audit import audit_social_claim
    assert audit_social_claim(ORG,social[0].model_dump(),ev.model_dump(),
        (blobs.directory/ev.content_sha256).read_text(encoding='utf-8'),context={'name':'Example AS'})[0]=='CORRECT'


def test_post_refresh_guard_rejects_changed_values_and_keeps_registry(tmp_path):
    from signalpost.web.wikidata_facts import enforce_evidence
    index,row,blobs=setup(tmp_path,[binding('P1448','Example AS')],[('identity.legal_name','Example AS')])
    publish(index,ORG,row,blobs)
    new_claims(row)[0].value['text']='Injected AS'
    enforce_evidence(row,blobs)
    assert not new_claims(row)
    assert row.claims[0].value=='Example AS'


def test_post_refresh_guard_retains_valid_revision_bound_facts(tmp_path):
    from signalpost.web.wikidata_facts import enforce_evidence
    index,row,blobs=setup(tmp_path,[binding('P1448','Example AS')])
    publish(index,ORG,row,blobs)
    new_claims(row)[0].carried_forward=True
    enforce_evidence(row,blobs)
    assert len(new_claims(row))==1


def test_failed_wikidata_refresh_retains_supported_facts_as_stale(tmp_path):
    from signalpost.refresh.diff import apply
    from signalpost.web.wikidata_facts import enforce_evidence
    index,old,blobs=setup(tmp_path,[binding('P1448','Example AS')],[('identity.legal_name','Example AS')])
    old.run.sections={family:'available' for family in old.run.sections};old.errors=[]
    publish(index,ORG,old,blobs)
    row=old.model_copy(deep=True)
    row.claims=[c for c in row.claims if '.wikidata.' not in c.field]
    row.run.refresh={'wikidata':{'state':'not_available_fetch_failed'}}
    apply(row,old.model_dump(),blobs)
    enforce_evidence(row,blobs)
    assert len(new_claims(row))==1 and new_claims(row)[0].carried_forward
    assert not row.changes
