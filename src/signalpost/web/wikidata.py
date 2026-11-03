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
from .social import matches_profile, company_names, profile_url

ENDPOINT='https://query.wikidata.org/sparql'
AGENT='NordicCompanyLens/2.0 (https://github.com/manishrahul1705/nordic-company-lens)'
PROPERTIES=('P856','P2013','P2003','P4264','P2002','P2397')
PREFIX='http://www.wikidata.org/prop/direct/'


def query(numbers):
    values=' '.join(json.dumps(n) for n in numbers if valid(n))
    properties=' '.join('wdt:'+p for p in PROPERTIES)
    return ('PREFIX wdt: <http://www.wikidata.org/prop/direct/>\n'
            'SELECT ?org ?item ?property ?value WHERE { VALUES ?org { '+values+' } '
            'VALUES ?property { '+properties+' } ?item wdt:P2333 ?org . ?item ?property ?value . }')


def parse(body, numbers):
    bindings=json.loads(body)['results']['bindings']
    if not isinstance(bindings,list):raise ValueError('Invalid bindings')
    output=[]
    for i,b in enumerate(bindings):
        if not isinstance(b,dict):continue
        def value(key):
            cell=b.get(key)
            return cell.get('value','') if isinstance(cell,dict) else ''
        org,item,prop,raw=(value(k) for k in ('org','item','property','value'))
        if org not in numbers or not re.fullmatch(r'https?://www\.wikidata\.org/entity/Q[1-9]\d*',item):continue
        if prop not in {PREFIX+p for p in PROPERTIES} or not isinstance(raw,str):continue
        output.append({'org':org,'item':'https://www.wikidata.org/wiki/'+item.rsplit('/',1)[1],
                       'property':prop.rsplit('/',1)[1],'value':raw,'locator':f'/results/bindings/{i}'})
    return output


async def fetch_batch(numbers, client, config, budget, blobs):
    index={'records':{},'metrics':{'status':'disabled','requests':0,'errors':0,'matched_companies':0,'website_candidates':0,'social_published':0}}
    if not config.websites or not config.wikidata:return index
    metrics=index['metrics'];metrics['status']='complete'
    numbers=sorted(n for n in set(numbers) if valid(n));next_start=0
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
            at=utc_now()
            for record in records:
                record.update(sha=sha,retrieved_at=at)
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
    context={'name':next((c.value for c in envelope.claims if c.field=='identity.legal_name' and c.availability=='available'),''),
             'subunits':[c.value for c in envelope.claims if c.field.startswith('subunits.unit.') and c.availability=='available']}
    names=company_names(context);section=Section()
    existing={c.value.get('url') for c in envelope.claims if c.field.startswith('social_profile.') and c.availability=='available'}
    for record in index['records'].get(org,[]):
        url=social_url(record)
        if not url or url in existing or not matches_profile(url,names):continue
        body=(blobs.directory/record['sha']).read_bytes()
        source=Source(record['item'],body,record['sha'],record['retrieved_at'],'Wikidata SPARQL; CC0')
        add(section,source,org,'website','social_profile.'+digest(url)[:20],
            {'url':url,'platform':domain(url),'source':'Wikidata','licence':'CC0','item_url':record['item']},
            record['locator'],source_class='wikidata',method='signalpost.wikidata.social.v1')
        section.claims[-1].reasons['relationship']='Wikidata exact P2333 organisation number and matching company handle'
        existing.add(url);index['metrics']['social_published']+=1
    envelope.claims.extend(section.claims)
    evidence={e.id:e for e in envelope.evidence};evidence.update({e.id:e for e in section.evidence});envelope.evidence=list(evidence.values())
