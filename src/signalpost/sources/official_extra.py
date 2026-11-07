"""Anonymous GLEIF and TED, with exact identifiers and pooled request accounting."""
import asyncio
import json
import re
from datetime import date
from urllib.parse import urlencode, urlsplit
import xml.etree.ElementTree as ET

from ..budget import SourceFailure
from ..models.evidence import digest, utc_now
from ..workers import offload
from .extract import Section, add, response_source
from .http import Response

GLEIF='https://api.gleif.org/api/v1/'
TED='https://api.ted.europa.eu/v3/notices/search'
METHOD='signalpost.official_extra.v1'
NS={'cac':'urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2',
    'cbc':'urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2',
    'efac':'http://data.europa.eu/p27/eforms-ubl-extension-aggregate-components/1'}


def gleif_extract(item,response,locator,org):
    section=Section()
    a=item.get('attributes',{});entity=a.get('entity',{})
    if entity.get('registeredAs')!=org or entity.get('registeredAt',{}).get('id')!='RA000472':return section
    fields={'lei':a.get('lei'),'entity_status':entity.get('status'),'legal_form':entity.get('legalForm'),
            'registration_date':a.get('registration',{}).get('initialRegistrationDate'),
            'renewal_date':a.get('registration',{}).get('nextRenewalDate')}
    paths={'lei':'/lei','entity_status':'/entity/status','legal_form':'/entity/legalForm',
           'registration_date':'/registration/initialRegistrationDate','renewal_date':'/registration/nextRenewalDate'}
    for field,value in fields.items():
        if value is not None and value!={}:
            add(section,response_source(response),org,'identity','identity.gleif.'+field,
                value,locator+'/attributes'+paths[field],source_class='GLEIF',method=METHOD)
            section.claims[-1].reasons['label']='GLEIF '+{'lei':'LEI','entity_status':'entity status','legal_form':'legal form code','registration_date':'LEI initial registration date','renewal_date':'LEI next renewal date'}[field]
    return section


def parent_extract(child,kind,edge,parent,edge_response,parent_response,org,locator="/data/0"):
    section=Section();rel=edge.get('data',{}).get('attributes',{}).get('relationship',{})
    a=parent.get('attributes',{});lei=a.get('lei');entity=a.get('entity',{})
    expected='IS_DIRECTLY_CONSOLIDATED_BY' if kind=='direct-parent' else 'IS_ULTIMATELY_CONSOLIDATED_BY'
    if (rel.get('status')!='ACTIVE' or rel.get('type')!=expected or rel.get('startNode',{}).get('id')!=child
            or rel.get('endNode',{}).get('id')!=lei or not lei or not entity.get('legalName',{}).get('name')):return section
    value={'name':entity['legalName']['name'],'lei':lei,'relationship':expected}
    if entity.get('registeredAt',{}).get('id')=='RA000472' and re.fullmatch(r'\d{9}',entity.get('registeredAs','')):
        value['organisation_number']=entity['registeredAs']
    add(section,response_source(parent_response),org,'identity','identity.gleif.'+kind.replace('-','_'),value,
        locator,source_class='GLEIF',method=METHOD)
    section.claims[-1].reasons['label']='GLEIF '+kind.replace('-',' ')
    proof=Section()
    add(proof,response_source(edge_response),org,'identity','support',rel,'/data/attributes/relationship',source_class='GLEIF',method=METHOD)
    section.evidence.extend(proof.evidence);section.claims[0].evidence_ids.extend(e.id for e in proof.evidence)
    return section


def text(node,path):
    el=node.find(path,NS)
    return el.text.strip() if el is not None and el.text else None


def award_extract(response,notice,org,now):
    """Never associate parallel lists of winners, contracts, dates or values."""
    section=Section();root=ET.fromstring(response.body)
    if root.tag.split('}')[-1]!='ContractAwardNotice':return section
    organisations={}
    for company in root.findall('.//efac:Organizations/efac:Organization/efac:Company',NS):
        ident=text(company,'cac:PartyIdentification/cbc:ID')
        national=text(company,'cac:PartyLegalEntity/cbc:CompanyID') or ''
        national=re.sub(r'^NO\s*|\s*MVA$','',national,flags=re.I).replace(' ','')
        country=text(company,'cac:PostalAddress/cac:Country/cbc:IdentificationCode')
        organisations[ident]={'name':text(company,'cac:PartyName/cbc:Name'),'orgnr':national,'country':country}
    buyers={text(p,'cac:Party/cac:PartyIdentification/cbc:ID') for p in root.findall('./cac:ContractingParty',NS)}
    buyer_names=[organisations[x]['name'] for x in sorted(buyers) if x in organisations and organisations[x]['name']]
    buyer_match=any(organisations.get(x,{}).get('orgnr')==org and organisations.get(x,{}).get('country') in {'NOR','NO'} for x in buyers)
    parties={text(p,'cbc:ID'):{text(t,'cbc:ID') for t in p.findall('efac:Tenderer',NS)}
             for p in root.findall('.//efac:NoticeResult/efac:TenderingParty',NS)}
    tenders={text(t,'cbc:ID'):t for t in root.findall('.//efac:NoticeResult/efac:LotTender',NS)}
    title=text(root,'cac:ProcurementProject/cbc:Name')
    try:since=now.replace(year=now.year-3)
    except ValueError:since=now.replace(year=now.year-3,day=28)
    for index,contract in enumerate(root.findall('.//efac:NoticeResult/efac:SettledContract',NS)):
        award_day=text(contract,'cbc:AwardDate')
        try:day=date.fromisoformat((award_day or '')[:10])
        except ValueError:continue
        if not since<=day<=now:continue
        linked=[tenders.get(text(t,'cbc:ID')) for t in contract.findall('efac:LotTender',NS)]
        linked=[t for t in linked if t is not None]
        winners=set().union(*(parties.get(text(t,'efac:TenderingParty/cbc:ID'),set()) for t in linked)) if linked else set()
        winner_match=any(organisations.get(x,{}).get('orgnr')==org and organisations.get(x,{}).get('country') in {'NOR','NO'} for x in winners)
        if not (buyer_match or winner_match) or not title or not buyer_names:continue
        contract_id=text(contract,'cbc:ID')
        if not contract_id:continue
        value={'kind':'Public procurement award','title':title,'buyer':buyer_names,'award_date':day.isoformat(),
               'date':day.isoformat(),'notice_id':notice,'contract_id':contract_id,'company_orgnr':org,
               'matched_role':'winner' if winner_match else 'buyer','url':f'https://ted.europa.eu/en/notice/-/detail/{notice}'}
        # Only a single linked tender amount is attributable, never a notice total.
        if winner_match and len(linked)==1:
            amount=linked[0].find('cbc:PayableAmount',NS)
            if amount is not None and amount.text and amount.get('currencyID'):
                from decimal import Decimal,InvalidOperation
                try:
                    parsed=Decimal(amount.text)
                    if parsed.is_finite():value.update(value=float(parsed),currency=amount.get('currencyID'))
                except InvalidOperation:pass
        add(section,response_source(response),org,'activity','procurement_award.'+digest([notice,contract_id,org])[:24],
            value,'/ContractAwardNotice',span=response.body.decode('utf-8')[:300],source_class='TED',method=METHOD)
        section.claims[-1].reasons['label']='Public procurement award'
        # Separate verbatim spans retain title, national IDs, role references, date
        # and amount without exceeding the contract's 300-character excerpt cap.
        import html
        raw=response.body.decode('utf-8')
        tokens=[title,award_day,contract_id,*buyer_names,org,*sorted(winners),*sorted(buyers)]
        if 'value' in value:tokens+=[str(value['value']).removesuffix('.0'),value['currency']]
        for n,token in enumerate(tokens):
            position=raw.find(html.escape(str(token),quote=False))
            if position<0:continue
            span=raw[max(0,position-50):position+min(240,len(str(token))+80)]
            support=Section()
            add(support,response_source(response),org,'activity','award_support',str(token),
                '/ContractAwardNotice/support/'+str(index)+'/'+str(n),span=span[:300],source_class='TED',method=METHOD)
            section.evidence.extend(support.evidence);section.claims[-1].evidence_ids.extend(e.id for e in support.evidence)
    return section


class Fetcher:
    def __init__(self,client,budget,blobs,count):
        self.client,self.budget,self.blobs=client,budget,blobs
        self.calls=0;self.cap=max(8,min(300,count//2));self.cache={};self.next_start={}
    async def get(self,url,payload=None):
        if url in self.cache and payload is None:return self.cache[url]
        host=urlsplit(url).hostname
        if host not in {'api.gleif.org','api.ted.europa.eu','ted.europa.eu'} or not url.startswith('https://'):raise SourceFailure('extra_url_refused')
        if self.calls>=self.cap:raise SourceFailure('extra_request_cap')
        import time
        delay=max(0,self.next_start.get(host,0)-time.monotonic())
        if delay:await asyncio.sleep(min(delay,max(.001,self.budget.deadline-time.monotonic())))
        self.next_start[host]=time.monotonic()+1
        self.calls+=1;event=self.budget.reserve(url,host,'__official_extra__')
        began=time.monotonic()
        try:
            async with asyncio.timeout(min(15,max(.001,self.budget.deadline-time.monotonic()))):
                r=await self.client.request('POST' if payload else 'GET',url,json=payload,headers={'Accept':'application/xml,text/xml' if host=='ted.europa.eu' else 'application/json'},follow_redirects=False,timeout=15)
                event['status']=r.status_code
                if len(r.content)>4*1024*1024 or r.status_code!=200:raise SourceFailure('extra_http_'+str(r.status_code))
                sha=await offload(self.blobs.put,r.content);event['content_sha256']=sha
                result=Response(r.content,r.status_code,url,utc_now(),sha)
                if payload is None:self.cache[url]=result
                return result
        except Exception as exc:
            event['error']=type(exc).__name__;raise
        finally:event['runtime_ms']=round((time.monotonic()-began)*1000)


async def collect(envelopes,client,budget,blobs):
    """Shared source calls; failure cannot change existing section availability."""
    fetch=Fetcher(client,budget,blobs,len(envelopes));result={o:Section() for o in envelopes}
    states={o:{'gleif':'not_available','TED':'not_available'} for o in envelopes};records={};edges=[]
    orgs=sorted(envelopes)
    for start in range(0,len(orgs),100):
        nums=orgs[start:start+100]
        try:
            url=GLEIF+'lei-records?'+urlencode({'filter[entity.registeredAs]':','.join(nums),'filter[entity.registeredAt]':'RA000472','page[size]':200})
            response=await fetch.get(url);data=json.loads(response.body)
            if data['meta']['pagination']['lastPage']!=1:raise SourceFailure('extra_pagination')
            for index,item in enumerate(data['data']):
                org=item['attributes']['entity']['registeredAs']
                if org not in nums:continue
                section=gleif_extract(item,response,'/data/'+str(index),org)
                if section.claims:
                    result[org].claims+=section.claims;result[org].evidence+=section.evidence;states[org]['gleif']='available';records[org]=item
        except Exception:
            for org in nums:states[org]['gleif']='not_available_fetch_failed'
    # Relationship proof only for exact matches. Parent records batched by LEI.
    for org,item in records.items():
        for kind in ['direct-parent','ultimate-parent']:
            url=item.get('relationships',{}).get(kind,{}).get('links',{}).get('relationship-record')
            if not url:continue
            try:
                response=await fetch.get(url);edge=json.loads(response.body);rel=edge['data']['attributes']['relationship']
                if rel['startNode']['id']==item['id'] and rel['status']=='ACTIVE':edges.append((org,item['id'],kind,edge,response,rel['endNode']['id']))
            except Exception:states[org]['parents']='not_available_fetch_failed'
    parents={}
    leis=sorted({e[-1] for e in edges})
    for start in range(0,len(leis),100):
        try:
            response=await fetch.get(GLEIF+'lei-records?'+urlencode({'filter[lei]':','.join(leis[start:start+100]),'page[size]':200}))
            data=json.loads(response.body)
            if data['meta']['pagination']['lastPage']!=1:continue
            for index,item in enumerate(data['data']):
                if item['id'] in leis:parents[item['id']]=(item,response,'/data/'+str(index))
        except Exception:pass
    for org,child,kind,edge,edge_response,lei in edges:
        if lei not in parents:
            states[org]['parents']='not_available_fetch_failed';continue
        parent,parent_response,locator=parents[lei]
        section=parent_extract(child,kind,edge,parent,edge_response,parent_response,org,locator)
        result[org].claims+=section.claims;result[org].evidence+=section.evidence
        # Retain the child's exact registry/LEI binding alongside relationship proof.
        child_claim=next(c for c in result[org].claims if c.field=='identity.gleif.lei')
        for c in section.claims:c.evidence_ids.extend(child_claim.evidence_ids)
    notices={}
    since=date.today()
    try:since=since.replace(year=since.year-3)
    except ValueError:since=since.replace(year=since.year-3,day=28)
    for start in range(0,len(orgs),100):
        nums=orgs[start:start+100];values='("'+'" OR "'.join(nums)+'")'
        query='(winner-identifier = '+values+' OR buyer-identifier = '+values+') AND notice-type = (can-standard OR can-social) AND publication-date >= '+since.strftime('%Y%m%d')
        try:
            for page in range(1,11):
                response=await fetch.get(TED,{'query':query,'fields':['publication-number','notice-type','winner-identifier','buyer-identifier'],'limit':100,'page':page,'scope':'ALL'})
                data=json.loads(response.body)
                if data.get('timedOut'):raise SourceFailure('extra_query_timeout')
                for item in data['notices']:
                    if item.get('notice-type') not in {'can-standard','can-social'}:continue
                    scope=set(nums)&set(item.get('winner-identifier',[])+item.get('buyer-identifier',[]))
                    if scope:notices.setdefault(item['publication-number'],set()).update(scope)
                if page*100>=data['totalNoticeCount']:break
            else:raise SourceFailure('extra_pagination')
        except Exception:
            for org in nums:states[org]['TED']='not_available_fetch_failed'
    for notice,scope in sorted(notices.items()):
        try:
            response=await fetch.get(f'https://ted.europa.eu/en/notice/{notice}/xml')
            for org in scope:
                section=await offload(award_extract,response,notice,org,date.fromisoformat(response.retrieved_at[:10]))
                result[org].claims+=section.claims;result[org].evidence+=section.evidence
                if section.claims and states[org]['TED']!='not_available_fetch_failed':states[org]['TED']='available'
        except Exception:
            for org in scope:states[org]['TED']='not_available_fetch_failed'
    for org,section in result.items():
        if states[org]['TED']=='not_available_fetch_failed':
            section.claims=[c for c in section.claims if c.family!='activity']
        awards=sorted((c for c in section.claims if c.family=='activity'),key=lambda c:(c.value['date'],c.field),reverse=True)[:10]
        section.claims=[c for c in section.claims if c.family!='activity']+awards
        for source in states[org]:envelopes[org].run.refresh.setdefault('official_extra',{})[source]=states[org][source]
    return result,{'requests':fetch.calls,'gleif_companies':len(records),'parent_LEIs_batched':len(leis),'tender_notices_nominated':len(notices)}


def retain_failed(row,previous):
    if not previous:return
    from ..models.claim import Claim
    from ..models.evidence import Evidence
    data=previous if 'claims' in previous else previous.get('profile',{})
    states=row.run.refresh.get('official_extra',{})
    prefixes=[]
    if states.get('gleif')=='not_available_fetch_failed':prefixes.append('identity.gleif.')
    if states.get('parents')=='not_available_fetch_failed':prefixes+=['identity.gleif.direct_parent','identity.gleif.ultimate_parent']
    if states.get('TED')=='not_available_fetch_failed':prefixes.append('procurement_award.')
    current={c.field for c in row.claims};needed=set()
    for raw in data.get('claims',[]):
        if raw['availability']=='available' and raw['field'].startswith(tuple(prefixes)) and raw['field'] not in current:
            claim=Claim.model_validate(raw);claim.carried_forward=True;claim.stale_since=row.run.completed_at
            row.claims.append(claim);needed.update(claim.evidence_ids)
    known={e.id for e in row.evidence}
    row.evidence.extend(Evidence.model_validate(e) for e in data.get('evidence',[]) if e['id'] in needed-known)
