"""Individual, dated active job pages linked by the verified company website."""
import re
from collections import deque
from datetime import datetime, timezone, time
from urllib.parse import urlsplit,parse_qs
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

ATS = {'webcruiter.no','webcruiter.com','teamtailor.com','jobylon.com','reachmee.com','recman.no','recman.page','easycruit.com','workday.com','myworkdayjobs.com','myworkdaysite.com','jobbnorge.no','varbi.com','hr-manager.net'}
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


def active_job(page, org, names, allowed, now=None, *, linked_board=False):
    now = now or datetime.now(timezone.utc)
    if re.search(r'stillingen er besatt|no longer accepting|position (?:is |has been )?filled|job (?:is )?closed|vacancy expired',page.visible,re.I):return None
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
    if matched is None:
        if not linked_board:return None
        matches={number for number,name in names.items() if employer_name and legal_name(name)==employer_name}
        if employer_name and not matches:return None
        matched=org if org in matches or not matches else sorted(matches)[0]
    if employer_name:
        raw_name = str(employer.get('legalName') or employer.get('name') or '')
        normalized = lambda name: ' '.join(re.findall(r'\w+',str(name or '').casefold()))
        if re.search(r'\b(?:AS|ASA|AB|Ltd\.?|GmbH|Oy)\s*$',raw_name,re.I) and normalized(raw_name) not in {normalized(n) for n in names.values()}:
            return None
        from .entity_scope import foreign_entity_page
        if foreign_entity_page(page, matched, names.get(matched), check_ids=False):return None
    return {'uuid':str(uuid5(NAMESPACE_URL,page.url)), 'source':'company_site', 'employer_orgnr':matched,
            'status':'ACTIVE','title':title.strip(),'url':page.url,'published':job['datePosted'],'expires':job['validThrough'],
            'matched_via':'verified company website and tenant-scoped linked board' if not identifiers else 'verified website link and exact registered employer',
            'employer_identity_proof':'linked_board' if not identifiers else 'orgnr_on_posting', 'location':job.get('jobLocation'),
            'occupation_categories':None}


def staffing(page):
    return bool(re.search(r'bemanningsbyr[aå]|staffing agency|recruitment agency|on behalf of (?:our|the) client',page.title+' '+page.owner_text[:1800],re.I))


def board_scope(url):
    p=urlsplit(url);host=p.hostname or ''
    if domain(url) not in ATS:return None
    # A named tenant subdomain establishes a board boundary. Shared ATS roots
    # require a non-root path/query and cannot authorize their whole service.
    shared=host in {domain(url),'www.'+domain(url),'candidate.'+domain(url),'apply.'+domain(url),'emp.jobylon.com'} or bool(re.match(r'^(?:web\d+|app|api|secure|jobs|ats)\.',host))
    if not shared:
        return (host,'/',None)
    path=p.path.rstrip('/')
    if not path and not p.query:return None
    segments=[s for s in path.split('/') if s]
    prefix='/'+'/'.join(segments[:2]) if len(segments)>1 else path+'/'
    return (host,prefix,parse_qs(p.query) or None)


def within_board(url,scope):
    if not scope:return False
    host,prefix,query=scope;p=urlsplit(url)
    return p.hostname==host and (p.path==prefix.rstrip('/') or p.path.startswith(prefix)) and (not query or all(parse_qs(p.query).get(k)==v for k,v in query.items()))


async def fetch(envelope, http):
    org=envelope.organisation_number
    proof=next((c for c in envelope.claims if c.field=='official_website' and c.availability=='available'),None)
    result=Section(state='not_applicable')
    if not proof or proof.value.get('content_allowed') is False or proof.value.get('relationship_note')=='group_site':return result
    if any(c.field=='identity.nace1' and isinstance(c.value,dict) and str(c.value.get('kode','')).startswith('78') for c in envelope.claims):return result
    root=domain(proof.value['final_url']);allowed={org};names={org:envelope.run.legal_identity.get('legal_name')}
    # Legal identity metadata is finalized later; use its current source claim.
    names[org]=next((c.value for c in envelope.claims if c.field=='identity.legal_name' and c.availability=='available'),'')
    for c in envelope.claims:
        if c.field.startswith('subunits.unit.') and c.availability=='available':
            number=c.value['organisation_number'];allowed.add(number);names[number]=c.value.get('name')
    queue=deque();seen=set();requests=0;candidate_urls=set();fetched=0;accepted=0
    def nominate(response,page, depth, scope=None, chain=()):
        if staffing(page):return
        for link in page.links:
            url=normalize_url(link.href)
            if not url or url in seen:continue
            host=domain(url)
            next_scope=scope
            require_name=False
            if host in ATS:
                if scope and not within_board(url,scope):
                    if urlsplit(url).hostname!=scope[0] or not re.search(r'/(?:jobs?|stillinger|stilling|positions?|vacancies)/',urlsplit(url).path,re.I):continue
                    require_name=True
                if scope is None:
                    if domain(page.url)!=root:continue
                    next_scope=board_scope(url)
                    if not next_scope:continue
            if host in {root,*ATS} and (CAREERS.search(urlsplit(url).path+' '+link.text) or host in ATS):
                candidate_urls.add(url)
                queue.append((url,depth,next_scope,(*chain,(response,link)),require_name))
    for response,page in http.accepted_pages.get(org,[]):nominate(response,page,0)
    nav_keys={(c.value.get('employer_orgnr'),c.value.get('title','').strip().casefold()) for c in envelope.claims if c.family=='hiring' and c.availability=='available' and isinstance(c.value,dict)}
    while queue and requests<6:
        url,depth,scope,chain,require_name=queue.popleft()
        if url in seen:continue
        seen.add(url);requests+=1
        try:
            response=await http.get(url,org,domain(url),proven={root,*ATS},allow_redirects=True)
            if response.status!=200 or domain(response.url) not in {root,*ATS}:continue
            fetched+=1
            page=Page(response.body,response.url)
            from .round2 import real_page
            if real_page(page,{'name':names[org],'subunits':[{'name':n} for k,n in names.items() if k!=org]}):continue
            if staffing(page):continue
            if scope and not within_board(response.url,scope):
                if not require_name or urlsplit(response.url).hostname!=scope[0]:continue
                declared_jobs=[j for data in page.jsonld for j in objects(data)]
                if len(declared_jobs)!=1 or not isinstance(declared_jobs[0].get('hiringOrganization'),dict) or not (declared_jobs[0]['hiringOrganization'].get('name') or declared_jobs[0]['hiringOrganization'].get('legalName')):continue
            linked=getattr(http.config,'website_linked_board_jobs',True) if hasattr(http,'config') else True
            value=active_job(page,org,names,allowed,linked_board=linked and (scope is not None or domain(response.url)==root))
            if value:accepted+=1
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
                for parent,link in chain:
                    if parent is None:continue
                    support=Section()
                    add(support,response_source(parent),org,'hiring','hiring_link_support',link.href,'/linked-careers',span=link.span,source_class='company_owned',method='signalpost.company_jobs.link.v1')
                    result.evidence.extend(support.evidence);result.claims[-1].evidence_ids.extend(e.id for e in support.evidence)
                nav_keys.add((value['employer_orgnr'],value['title'].casefold()))
            elif depth<2:
                nominate(response,page,depth+1,scope,chain)
        except SourceFailure as exc:
            result.errors.append(Error(section='hiring',code='company_careers_'+exc.code,message='Company careers coverage incomplete'))
            break
    result.state='available' if result.claims else 'failed' if result.errors else 'not_available' if seen else 'not_applicable'
    envelope.run.refresh['company_jobs']={'candidates':len(candidate_urls),'fetched':fetched,'pages_checked':requests,'urls_checked':sorted(seen),'accepted':accepted,'active_posts':len(result.claims),'complete':not queue and not result.errors}
    return result
