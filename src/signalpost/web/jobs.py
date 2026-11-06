"""Individual, dated active job pages linked by the verified company website."""
import re
from collections import deque
from datetime import datetime, timezone, time
from urllib.parse import urlsplit
from uuid import uuid5, NAMESPACE_URL
from ..budget import SourceFailure
from ..models.envelope import Error
from ..models.evidence import digest
from ..sources.extract import Section, add, response_source
from ..sources.nav import timestamp
from .html import Page, json_values
from .policy import domain, normalize_url
from .candidates import legal_name
from .proof import orgnrs

ATS = {'webcruiter.no','webcruiter.com','teamtailor.com','jobylon.com','reachmee.com','recman.no','recman.page','easycruit.com'}
CAREERS = re.compile(r'karrier|career|ledige|stillinger|vacanc|job(?:s|b|ber)?(?:/|$|[-_])|work-with-us|recruit|positions?', re.I)


def job_date(value, expiry=False):
    parsed = timestamp(value)
    if parsed is None and re.fullmatch(r'\d{4}-\d{2}-\d{2}', str(value or '')):
        try:
            day = datetime.fromisoformat(value).date()
            parsed = datetime.combine(day, time.max if expiry else time.min, timezone.utc)
        except ValueError:
            pass
    return parsed


def objects(value):
    if isinstance(value,list):
        for v in value:yield from objects(v)
    elif isinstance(value,dict):
        types=value.get('@type',[])
        if 'JobPosting' in (types if isinstance(types,list) else [types]):yield value
        for v in value.values():
            if isinstance(v,(list,dict)):yield from objects(v)


def active_job(page, org, names, allowed, now=None):
    now = now or datetime.now(timezone.utc)
    jobs=[job for body in page.jsonld for job in objects(body)]
    # A multi-ad landing/search page never establishes a single active vacancy.
    if len(jobs)!=1:return None
    job=jobs[0]
    title=job.get('title');posted=job_date(job.get('datePosted'));expires=job_date(job.get('validThrough'), expiry=True)
    if not isinstance(title,str) or not title.strip() or posted is None or expires is None or posted>now or expires<=now:return None
    if str(job.get('status','ACTIVE')).upper() not in {'ACTIVE','OPEN','PUBLISHED'}:return None
    declared=normalize_url(job.get('url') or page.url)
    if declared and (urlsplit(declared).netloc,urlsplit(declared).path.rstrip('/')) != (urlsplit(page.url).netloc,urlsplit(page.url).path.rstrip('/')):return None
    employer=job.get('hiringOrganization') or {}
    if not isinstance(employer,dict):return None
    identifiers=set()
    for key in ('identifier','taxID','vatID'):
        for value in json_values(employer,key):
            identifiers |= orgnrs(str(value))
    if identifiers - allowed:return None
    matched=next(iter(identifiers & allowed),None)
    employer_name=legal_name(employer.get('legalName') or employer.get('name'))
    # Preserve the NAV precision gate on ATS pages too: a registered name is
    # discovery metadata, never a substitute for the exact employer identifier.
    if matched is None:return None
    if employer_name:
        raw_name = str(employer.get('legalName') or employer.get('name') or '')
        normalized = lambda name: ' '.join(re.findall(r'\w+',str(name or '').casefold()))
        if re.search(r'\b(?:AS|ASA|AB|Ltd\.?|GmbH|Oy)\s*$',raw_name,re.I) and normalized(raw_name) not in {normalized(n) for n in names.values()}:
            return None
        from .entity_scope import foreign_entity_page
        if foreign_entity_page(page, matched, names.get(matched), check_ids=False):return None
    return {'uuid':str(uuid5(NAMESPACE_URL,page.url)), 'source':'company_site', 'employer_orgnr':matched,
            'status':'ACTIVE','title':title.strip(),'url':page.url,'published':job['datePosted'],'expires':job['validThrough'],
            'matched_via':'verified website link and exact registered employer', 'location':job.get('jobLocation'),
            'occupation_categories':None}


async def fetch(envelope, http):
    org=envelope.organisation_number
    proof=next((c for c in envelope.claims if c.field=='official_website' and c.availability=='available'),None)
    result=Section(state='not_applicable')
    if not proof or proof.value.get('content_allowed') is False or proof.value.get('relationship_note')=='group_site':return result
    root=domain(proof.value['final_url']);allowed={org};names={org:envelope.run.legal_identity.get('legal_name')}
    # Legal identity metadata is finalized later; use its current source claim.
    names[org]=next((c.value for c in envelope.claims if c.field=='identity.legal_name' and c.availability=='available'),'')
    for c in envelope.claims:
        if c.field.startswith('subunits.unit.') and c.availability=='available':
            number=c.value['organisation_number'];allowed.add(number);names[number]=c.value.get('name')
    queue=deque();seen=set();requests=0
    def nominate(page, depth):
        for link in page.links:
            url=normalize_url(link.href)
            if not url or url in seen:continue
            host=domain(url)
            if host in {root,*ATS} and (CAREERS.search(urlsplit(url).path+' '+link.text) or host in ATS and domain(page.url)!=host):queue.append((url,depth))
    for _,page in http.accepted_pages.get(org,[]):nominate(page,0)
    nav_keys={(c.value.get('employer_orgnr'),c.value.get('title','').strip().casefold()) for c in envelope.claims if c.family=='hiring' and c.availability=='available' and isinstance(c.value,dict)}
    while queue and requests<6:
        url,depth=queue.popleft()
        if url in seen:continue
        seen.add(url);requests+=1
        try:
            response=await http.get(url,org,domain(url),proven={root,*ATS},allow_redirects=True)
            if response.status!=200 or domain(response.url) not in {root,*ATS}:continue
            page=Page(response.body,response.url)
            value=active_job(page,org,names,allowed)
            if value and (value['employer_orgnr'],value['title'].casefold()) not in nav_keys:
                source=response_source(response)
                add(result,source,org,'hiring','hiring.site_job.'+digest(page.url)[:20],value,'/JobPosting',span=page.span_for(value['title']),source_class='company_owned',method='signalpost.company_jobs.v1')
                # Date fields can be far apart; each is separately localized.
                for key in ('published','expires'):
                    support=Section()
                    add(support,source,org,'hiring','job_date',value[key],'/JobPosting/'+key,span=page.span_for(value[key]),source_class='company_owned',method='signalpost.company_jobs.v1')
                    result.evidence.extend(support.evidence);result.claims[-1].evidence_ids.extend(e.id for e in support.evidence)
                result.evidence.extend(e for e in envelope.evidence if e.id in proof.evidence_ids)
                result.claims[-1].evidence_ids.extend(proof.evidence_ids)
                nav_keys.add((value['employer_orgnr'],value['title'].casefold()))
            elif depth<2:
                nominate(page,depth+1)
        except SourceFailure as exc:
            result.errors.append(Error(section='hiring',code='company_careers_'+exc.code,message='Company careers coverage incomplete'))
            break
    result.state='available' if result.claims else 'failed' if result.errors else 'not_available' if seen else 'not_applicable'
    envelope.run.refresh['company_jobs']={'pages_checked':requests,'urls_checked':sorted(seen),'active_posts':len(result.claims),'complete':not queue and not result.errors}
    return result
