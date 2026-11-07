import asyncio
import hashlib
import json
from datetime import date
from types import SimpleNamespace

import pytest
from signalpost.sources.official_extra import gleif_extract,parent_extract,award_extract,Fetcher,retain_failed
from signalpost.sources.http import Response
from signalpost.web.candidates import Candidate
from signalpost.web.fetcher import WebsiteHttp
from signalpost.budget import SourceFailure

ORG='923609016'


def response(value,url='https://api.gleif.org/api/v1/lei-records'):
    body=json.dumps(value).encode() if isinstance(value,dict) else value.encode()
    return Response(body,200,url,'2026-11-07T00:00:00Z',hashlib.sha256(body).hexdigest())


def record(org=ORG,ra='RA000472'):
    return {'id':'LEICHILD','attributes':{'lei':'LEICHILD','entity':{'registeredAs':org,'registeredAt':{'id':ra},
        'status':'ACTIVE','legalForm':{'id':'YI42'}},'registration':{'initialRegistrationDate':'2020-01-01','nextRenewalDate':'2027-01-01'}}}


def test_gleif_exact_org_and_authority_stable_ids():
    item=record();r=response({'data':[item]})
    claims=gleif_extract(item,r,'/data/0',ORG).claims
    assert len(claims)==5 and {c.id for c in claims}=={c.id for c in gleif_extract(item,r,'/data/0',ORG).claims}
    assert not gleif_extract(record(ra='RA000170'),r,'/data/0',ORG).claims
    assert not gleif_extract(record(org='999999999'),r,'/data/0',ORG).claims
    item['attributes']['registration']={}
    assert len(gleif_extract(item,r,'/data/0',ORG).claims)==3


def test_parent_requires_explicit_active_edge_and_foreign_id_not_orgnr():
    parent=record('42019887','RA000170');parent['attributes'].update(lei='PARENT')
    parent['attributes']['entity']['legalName']={'name':'Parent ApS'}
    edge={'data':{'attributes':{'relationship':{'startNode':{'id':'LEICHILD'},'endNode':{'id':'PARENT'},
        'type':'IS_DIRECTLY_CONSOLIDATED_BY','status':'ACTIVE'}}}}
    section=parent_extract('LEICHILD','direct-parent',edge,parent,response(edge),response({'data':[parent]}),ORG)
    assert section.claims[0].value['lei']=='PARENT' and 'organisation_number' not in section.claims[0].value
    assert len(section.claims[0].evidence_ids)==2
    edge['data']['attributes']['relationship']['startNode']['id']='SOMEONEELSE'
    assert not parent_extract('LEICHILD','direct-parent',edge,parent,response(edge),response({'data':[parent]}),ORG).claims


def xml(winner=ORG,day='2026-10-01',root='ContractAwardNotice'):
    from signalpost.sources.official_extra import NS
    attrs=' '.join('xmlns:'+k+'="'+v+'"' for k,v in NS.items())
    return f'''<{root} {attrs}><cac:ContractingParty><cac:Party><cac:PartyIdentification><cbc:ID>B</cbc:ID></cac:PartyIdentification></cac:Party></cac:ContractingParty>
    <cac:ProcurementProject><cbc:Name>Bridge maintenance</cbc:Name></cac:ProcurementProject>
    <efac:Organizations><efac:Organization><efac:Company><cac:PartyIdentification><cbc:ID>B</cbc:ID></cac:PartyIdentification><cac:PartyName><cbc:Name>Buyer</cbc:Name></cac:PartyName><cac:PartyLegalEntity><cbc:CompanyID>111111111</cbc:CompanyID></cac:PartyLegalEntity><cac:PostalAddress><cac:Country><cbc:IdentificationCode>NOR</cbc:IdentificationCode></cac:Country></cac:PostalAddress></efac:Company></efac:Organization>
    <efac:Organization><efac:Company><cac:PartyIdentification><cbc:ID>W</cbc:ID></cac:PartyIdentification><cac:PartyName><cbc:Name>Winner</cbc:Name></cac:PartyName><cac:PartyLegalEntity><cbc:CompanyID>{winner}</cbc:CompanyID></cac:PartyLegalEntity><cac:PostalAddress><cac:Country><cbc:IdentificationCode>NOR</cbc:IdentificationCode></cac:Country></cac:PostalAddress></efac:Company></efac:Organization></efac:Organizations>
    <efac:NoticeResult><efac:TenderingParty><cbc:ID>P</cbc:ID><efac:Tenderer><cbc:ID>W</cbc:ID></efac:Tenderer></efac:TenderingParty><efac:LotTender><cbc:ID>T</cbc:ID><efac:TenderingParty><cbc:ID>P</cbc:ID></efac:TenderingParty><cbc:PayableAmount currencyID="NOK">500000</cbc:PayableAmount></efac:LotTender><efac:SettledContract><cbc:ID>C</cbc:ID><cbc:AwardDate>{day}</cbc:AwardDate><efac:LotTender><cbc:ID>T</cbc:ID></efac:LotTender></efac:SettledContract></efac:NoticeResult></{root}>'''


def test_award_exact_role_value_window_and_stable_ids():
    def parse(body,org=ORG):return award_extract(response(body,'https://ted.europa.eu/en/notice/1-2026/xml'),'1-2026',org,date(2026,11,7))
    a=parse(xml());assert len(a.claims)==1
    assert a.claims[0].value['value']==500000 and a.claims[0].value['currency']=='NOK'
    assert a.claims[0].value['matched_role']=='winner'
    assert a.claims[0].id==parse(xml()).claims[0].id
    assert parse(xml(),'111111111').claims[0].value['matched_role']=='buyer'
    assert not parse(xml(winner='999999999')).claims
    assert not parse(xml(root='ContractNotice')).claims
    assert parse(xml(day='2023-11-07')).claims and not parse(xml(day='2023-11-06')).claims
    assert not parse(xml(day='2027-01-01')).claims
    assert not parse(xml().replace('<efac:LotTender><cbc:ID>T</cbc:ID></efac:LotTender>','')).claims


def test_briefing_cites_gleif_and_newest_proven_procurement(tmp_path):
    from tests.test_synthesis import envelope
    from signalpost.synthesis.analyst import generate,validate
    row,_=envelope(tmp_path)
    lei=gleif_extract(record(),response({'data':[record()]}),'/data/0',ORG)
    award=award_extract(response(xml(),'https://ted.europa.eu/en/notice/1-2026/xml'),'1-2026',ORG,date(2026,11,7))
    row.claims+=lei.claims+award.claims;row.evidence+=lei.evidence+award.evidence
    brief=generate(row)
    assert 'registered in GLEIF with LEI LEICHILD' in brief.sentences[0].text
    event=next(s for s in brief.sentences if s.sentence_type=='d')
    assert 'public procurement award dated 1 Oct 2026' in event.text
    assert event.claim_ids==[award.claims[0].id]
    assert validate(brief,row)==generate(row)


@pytest.mark.parametrize('failures,absent', [(['no_such_domain']*4,True),(['website_timeout']*3+['no_such_domain'],False),(['website_tls_error']*4,False)])
def test_only_all_apex_www_nxdomain_proves_absence(failures,absent):
    http=object.__new__(WebsiteHttp);http.attempts={};i=iter(failures)
    async def precheck(*args):pass
    async def get(*args,**kwargs):raise SourceFailure(next(i))
    http.precheck=precheck;http.get=get
    with pytest.raises(SourceFailure) as error:asyncio.run(http.candidate(Candidate('https://example.no','example.no','registry_website'),ORG))
    assert getattr(error.value,'declared_domain_absent',False)==absent


@pytest.mark.parametrize('code,all_absent,state', [('no_such_domain',True,'not_available'),
    ('no_such_domain',False,'failed'),('website_timeout',False,'failed'),
    ('website_tls_error',False,'failed'),('website_connect_error',False,'failed')])
def test_strong_section_absent_only_with_complete_nxdomain_proof(tmp_path,monkeypatch,code,all_absent,state):
    from tests.test_websites import execute_web
    async def candidate(self,*args,**kwargs):
        error=SourceFailure(code)
        error.declared_domain_absent=all_absent
        raise error
    monkeypatch.setattr(WebsiteHttp,'candidate',candidate)
    _,row,_,_=execute_web(tmp_path,monkeypatch)
    assert row['run']['sections']['website']==state
    if all_absent:assert any(e['message']=='declared domain does not exist' for e in row['errors'])


def test_failed_gleif_preserves_previous_claim_and_original_evidence():
    from tests.test_registry_changes import envelope
    old=envelope();section=gleif_extract(record(),response({'data':[record()]}),'/data/0',ORG)
    old.claims+=section.claims;old.evidence+=section.evidence
    row=envelope();row.run.refresh['official_extra']={'gleif':'not_available_fetch_failed'}
    retain_failed(row,old.model_dump(mode='json'))
    assert {c.id for c in row.claims}=={c.id for c in old.claims}
    assert all(c.carried_forward for c in row.claims if c.field.startswith("identity.gleif."))
    assert {e.id for e in row.evidence}=={e.id for e in old.evidence}


def test_only_exact_children_get_parent_lookups_and_parent_leis_are_batched(tmp_path):
    import httpx
    from signalpost.sources.official_extra import collect
    from signalpost.sources.blobstore import BlobStore
    from tests.test_registry_changes import envelope
    from urllib.parse import parse_qs,urlsplit
    events=[]
    class Budget:
        import time
        deadline=time.monotonic()+30
        def reserve(self,url,host,org):
            event={'url':url,'organisation_number':org};events.append(event);return event
    def dispatch(request):
        path=request.url.path
        if request.method=='POST':return httpx.Response(200,json={'notices':[],'totalNoticeCount':0})
        if path.endswith('/direct-parent-relationship'):
            return httpx.Response(200,json={'data':{'attributes':{'relationship':{'startNode':{'id':'LEICHILD'},'endNode':{'id':'PARENT'},'status':'ACTIVE','type':'IS_DIRECTLY_CONSOLIDATED_BY'}}}})
        query=parse_qs(request.url.query.decode())
        if 'filter[lei]' in query:
            assert query['filter[lei]']==['PARENT']
            parent=record('911305631');parent['id']='PARENT';parent['attributes']['lei']='PARENT';parent['attributes']['entity']['legalName']={'name':'Parent AS'}
            return httpx.Response(200,json={'data':[parent],'meta':{'pagination':{'lastPage':1}}})
        child=record();child['relationships']={'direct-parent':{'links':{'relationship-record':'https://api.gleif.org/api/v1/lei-records/LEICHILD/direct-parent-relationship'}}}
        wrong=record('999999999');wrong['relationships']=child['relationships']
        return httpx.Response(200,json={'data':[child,wrong],'meta':{'pagination':{'lastPage':1}}})
    async def go():
        async with httpx.AsyncClient(transport=httpx.MockTransport(dispatch)) as client:
            return await collect({ORG:envelope()},client,Budget(),BlobStore(tmp_path))
    result,metrics=asyncio.run(go())
    assert len([e for e in events if 'filter%5Blei%5D' in e['url']])==1
    assert len([e for e in events if e['url'].endswith('direct-parent-relationship')])==1
    assert metrics['requests']==len(events)==4 and metrics['gleif_companies']==1
    assert result[ORG].claims[-1].value['organisation_number']=='911305631'
    assert all(e['organisation_number']=='__official_extra__' for e in events)


def test_ted_xml_overrides_shared_json_accept_header_and_is_budgeted(tmp_path):
    import httpx,time
    from signalpost.sources.blobstore import BlobStore
    events=[]
    class Budget:
        deadline=time.monotonic()+30
        def reserve(self,url,host,org):
            event={'url':url,'organisation_number':org};events.append(event);return event
    def dispatch(request):
        assert request.headers['Accept']=='application/xml,text/xml'
        return httpx.Response(200,text=xml())
    async def go():
        async with httpx.AsyncClient(headers={'Accept':'application/json'},transport=httpx.MockTransport(dispatch)) as client:
            fetch=Fetcher(client,Budget(),BlobStore(tmp_path),1000)
            r=await fetch.get('https://ted.europa.eu/en/notice/1-2026/xml')
            assert r.status==200 and fetch.calls==1
    asyncio.run(go())
    assert len(events)==1 and events[0]['status']==200


@pytest.mark.parametrize('status',[406,503])
def test_optional_ted_error_never_fails_registry_or_verified_website(tmp_path,monkeypatch,status):
    import httpx
    from tests.test_websites import execute_web,html
    def dispatch(request):
        if request.url.host=='api.gleif.org':
            return httpx.Response(200,json={'data':[],'meta':{'pagination':{'lastPage':1}}})
        if request.url.host=='api.ted.europa.eu':
            return httpx.Response(200,json={'notices':[{'publication-number':'1-2026','notice-type':'can-standard','winner-identifier':[ORG]}],'totalNoticeCount':1})
        if request.url.host=='ted.europa.eu':return httpx.Response(status,text='Optional source unavailable')
        if request.url.path=='/robots.txt':return httpx.Response(200,text='User-agent: *\nAllow: /')
        return httpx.Response(200,text=html())
    report,row,_,_=execute_web(tmp_path,monkeypatch,response=dispatch,official_extra_sources=True)
    assert row['run']['sections']['identity']=='available'
    assert row['run']['sections']['roles']=='available'
    assert row['run']['sections']['subunits'] in {'available','not_available'}
    assert row['run']['sections']['accounts']=='not_available'
    assert row['run']['sections']['website']=='available'
    assert row['run']['refresh']['official_extra']['TED']=='not_available_fetch_failed'
    assert not any(c['field'].startswith('procurement_award.') for c in row['claims'])
    assert report['deadline_hits']==0


def test_failed_ted_fetch_retains_previous_award_and_evidence():
    from tests.test_registry_changes import envelope
    old=envelope();section=award_extract(response(xml(),'https://ted.europa.eu/en/notice/1-2026/xml'),'1-2026',ORG,date(2026,11,7))
    old.claims+=section.claims;old.evidence+=section.evidence
    current=envelope();current.run.refresh['official_extra']={'TED':'not_available_fetch_failed'}
    retain_failed(current,old.model_dump(mode='json'))
    awards=[c for c in current.claims if c.field.startswith('procurement_award.')]
    assert len(awards)==1 and awards[0].id==section.claims[0].id and awards[0].carried_forward
    assert set(awards[0].evidence_ids)<={e.id for e in current.evidence}
