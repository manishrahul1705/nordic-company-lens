"""Exact-org-number Wikidata nominations and name-checked CC0 social claims."""
import asyncio
import json
import re
import time
from urllib.parse import quote

import httpx

from ..budget import SourceFailure
from ..identity.orgnr import valid
from ..models.evidence import digest, utc_now
from ..sources.extract import Section, Source, add
from ..workers import offload
from .policy import normalize_url, domain, SOCIAL, DIRECTORIES, FREE_MAIL
from .social import matches_profile, social_company_names, profile_url, context_for_envelope

ENDPOINT='https://query.wikidata.org/sparql'
AGENT='NordicCompanyLens/2.0 (https://github.com/manishrahul1705/nordic-company-lens)'
PROPERTIES=('P1448','P571','P159','P452','P1128','P2139','P856','P2013','P2003','P4264','P2002','P2397')
PREFIX='http://www.wikidata.org/prop/direct/'


def query(numbers):
    values=' '.join(json.dumps(n) for n in numbers if valid(n))
    properties=' '.join('wdt:'+p for p in PROPERTIES)
    return ('PREFIX wdt:<http://www.wikidata.org/prop/direct/> '
            'PREFIX wb:<http://wikiba.se/ontology#> PREFIX schema:<http://schema.org/> '
            'PREFIX pq:<http://www.wikidata.org/prop/qualifier/> '
            'PREFIX pqv:<http://www.wikidata.org/prop/qualifier/value/> '
            'PREFIX rdfs:<http://www.w3.org/2000/01/rdf-schema#> '
            'SELECT ?org ?item ?revision ?property ?statement ?value ?valueLabel '
            '?unit ?currencyCode ?precision ?calendar ?pointInTime ?pointPrecision ?pointCalendar WHERE { '
            'VALUES ?org { '+values+' } VALUES ?property { '+properties+' } '
            '?item wdt:P2333 ?org . '
            '?prop wb:directClaim ?property; wb:claim ?link; wb:statementProperty ?main . '
            '?item ?link ?statement . ?statement a wb:BestRank; ?main ?value . '
            'OPTIONAL { ?item schema:version ?revision } '
            'OPTIONAL { ?value rdfs:label ?valueLabel FILTER(LANG(?valueLabel) IN ("nb","nn","no","en")) } '
            'OPTIONAL { ?prop wb:statementValue ?full . ?statement ?full ?node . '
            'OPTIONAL { ?node wb:quantityUnit ?unit OPTIONAL { ?unit wdt:P498 ?currencyCode } } '
            'OPTIONAL { ?node wb:timePrecision ?precision; wb:timeCalendarModel ?calendar } } '
            'OPTIONAL { ?statement pq:P585 ?pointInTime . '
            'OPTIONAL { ?statement pqv:P585 ?pointNode . '
            '?pointNode wb:timePrecision ?pointPrecision; wb:timeCalendarModel ?pointCalendar } } }')


def parse(body, numbers):
    bindings=json.loads(body)['results']['bindings']
    if not isinstance(bindings,list):raise ValueError('Invalid bindings')
    output=[]
    for i,b in enumerate(bindings):
        if not isinstance(b,dict):continue
        def value(key):
            cell=b.get(key)
            raw=cell.get('value','') if isinstance(cell,dict) else ''
            return raw if isinstance(raw,str) else ''
        org,item,prop,raw=(value(k) for k in ('org','item','property','value'))
        if org not in numbers or not re.fullmatch(r'https?://www\.wikidata\.org/entity/Q[1-9]\d*',item):continue
        if prop not in {PREFIX+p for p in PROPERTIES} or not isinstance(raw,str):continue
        record={'org':org,'item':'https://www.wikidata.org/wiki/'+item.rsplit('/',1)[1],
                'property':prop.rsplit('/',1)[1],'value':raw,'locator':f'/results/bindings/{i}'}
        for key in ('revision','statement','unit','currencyCode','precision','calendar','pointInTime','pointPrecision','pointCalendar','valueLabel'):
            if value(key):record[key]=value(key)
        record['value_type']=b.get('value',{}).get('type')
        record['language']=b.get('value',{}).get('xml:lang')
        record['label_language']=b.get('valueLabel',{}).get('xml:lang')
        output.append(record)
    return output


async def fetch_batch(numbers, client, config, budget, blobs):
    index={'records':{},'metrics':{'status':'disabled','requests':0,'errors':0,'matched_companies':0,'website_candidates':0,'social_published':0}}
    if not config.websites or not config.wikidata:return index
    metrics=index['metrics'];metrics['status']='complete'
    numbers=sorted(n for n in set(numbers) if valid(n));next_start=0
    index['company_states']={org:'not_checked' for org in numbers}
    for offset in range(0,len(numbers),200):
        selected=numbers[offset:offset+200]
        event=None
        try:
            await asyncio.sleep(max(0,next_start-time.monotonic()))
            event=budget.reserve(ENDPOINT,'query.wikidata.org','__wikidata__');event['section']='wikidata';metrics['requests']+=1
            began=time.monotonic();next_start=began+1
            async with asyncio.timeout(min(15,max(.001,budget.deadline-began))):
                async with client.stream('GET',ENDPOINT,params={'query':query(selected),'format':'json'},
                        headers={'User-Agent':AGENT,'Accept':'application/sparql-results+json'},timeout=15,follow_redirects=False) as response:
                    event['status']=response.status_code
                    body=bytearray()
                    async for chunk in response.aiter_bytes():
                        body.extend(chunk)
                        if len(body)>2*1024*1024:raise ValueError('Wikidata body cap')
                    body=bytes(body);sha=await offload(blobs.put,body);event['content_sha256']=sha
                    if response.status_code!=200:
                        metrics['errors']+=1;metrics['status']='incomplete'
                        if response.status_code in {403,429}:break
                        continue
            records=await offload(parse,body,set(selected))
            for org in selected:index['company_states'][org]='checked'
            at=utc_now()
            for record in records:
                record.update(sha=sha,retrieved_at=at,source_url=str(response.url))
                index['records'].setdefault(record['org'],[]).append(record)
        except (SourceFailure,ValueError,KeyError,TypeError,TimeoutError,OSError,httpx.HTTPError):
            metrics['errors']+=1;metrics['status']='incomplete'
            if event is not None:event['error']='wikidata_unavailable'
        finally:
            if event is not None:event['runtime_ms']=round((time.monotonic()-began)*1000)
    metrics['matched_companies']=len(index['records'])
    metrics['website_candidates']=sum(r['property']=='P856' for rs in index['records'].values() for r in rs)
    try:
        await offload((config.state_dir/'wikidata-index.json').write_text,json.dumps(index,indent=2),encoding='utf8')
    except OSError:
        metrics['status']='incomplete';metrics['errors']+=1
    return index


def websites(index, org):
    output=[]
    for record in index['records'].get(org,[]):
        url=normalize_url(record['value']) if record['property']=='P856' else None
        if url and domain(url) not in SOCIAL|DIRECTORIES|FREE_MAIL:output.append(url)
    return list(dict.fromkeys(output))


def social_url(record):
    raw=record['value'].strip()
    roots={'P2013':'https://www.facebook.com/','P2003':'https://www.instagram.com/',
           'P4264':'https://www.linkedin.com/company/','P2002':'https://x.com/',
           'P2397':'https://www.youtube.com/channel/'}
    base=roots.get(record['property'])
    if not base or not raw or '/' in raw or '?' in raw or '#' in raw:return None
    return profile_url(base+quote(raw.lstrip('@'),safe='-_.'))


def publish_social(index, org, envelope, blobs):
    from .wikidata_facts import checked_records, source as result_source, stamp
    context=context_for_envelope(envelope)
    names=social_company_names(context);section=Section()
    existing={c.value.get('url'):c for c in envelope.claims if c.field.startswith('social_profile.') and c.availability=='available'}
    website_links = {str(url).rstrip('/') for url in envelope.run.refresh.get('website', {}).get('observed_social_profiles', [])}
    for record,body in checked_records(index,org,blobs):
        url=social_url(record)
        site_linked = bool(url and any(str(link).rstrip('/') == url.rstrip('/') for link in website_links))
        if record.get('org') != org or not url or (not site_linked and not matches_profile(url,names)):continue
        source=result_source(record,body)
        add(section,source,org,'website','social_profile.'+digest(url)[:20],
            {'url':url,'platform':domain(url),'source':'Wikidata','licence':'CC0','item_url':record['item']},
            record['locator'],source_class='wikidata',method='signalpost.wikidata.social.v1')
        stamp(section,record)
        section.claims[-1].reasons['relationship']=('linked from the verified company website' if site_linked else
            'Wikidata exact P2333 organisation number and matching company handle')
        if url in existing:
            current=existing[url];additional=section.claims.pop()
            current.evidence_ids=list(dict.fromkeys(current.evidence_ids+additional.evidence_ids))
            current.reasons.update({k:v for k,v in additional.reasons.items() if k.startswith('wikidata_')})
            index['metrics']['social_corroborated']=index['metrics'].get('social_corroborated',0)+1
        else:
            existing[url]=section.claims[-1];index['metrics']['social_published']+=1
    envelope.claims.extend(section.claims)
    evidence={e.id:e for e in envelope.evidence};evidence.update({e.id:e for e in section.evidence});envelope.evidence=list(evidence.values())
