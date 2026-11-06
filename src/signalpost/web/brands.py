"""Bounded actual-use brand nominations; a brand is never identity proof."""
import json
import re
from .candidates import Candidate,legal_name,GENERIC
from .policy import domain,normalize_url,FREE_MAIL,SOCIAL,DIRECTORIES
from .social import compact

GENERIC_BRAND=GENERIC|{'as','asa','avd','avdeling','home','hjem','forside','welcome','official','website','norge','norway','group','gruppen','company','services','kontakt','contact','about','om','oss'}


def labels(name):
    name=re.split(r'\b(?:avd|avdeling)\b',str(name or ''),flags=re.I)[0]
    words=[w for w in legal_name(name).split() if w not in GENERIC_BRAND]
    if not words:return []
    result=[]
    for replacements in [('ae','o','a'),('ae','oe','aa')]:
        terms=[w.replace('æ',replacements[0]).replace('ø',replacements[1]).replace('å',replacements[2]) for w in words]
        for separator in ['', '-']:
            value=separator.join(terms)
            if len(value.replace('-',''))>=5 and re.fullmatch('[a-z0-9-]+',value) and value not in result:result.append(value)
    return result


def actual_names(envelope,context,blobs):
    result=[];legal=compact(legal_name(context.get('name')))
    for c in envelope.claims:
        if c.availability=='available' and c.field.startswith('subunits.unit.') and isinstance(c.value,dict):
            name=c.value.get('name')
            if compact(legal_name(name))!=legal:result.append((name,'registered_subunit',c.evidence_ids))
    refs={ref for c in envelope.claims if c.family=='hiring' and c.availability=='available' for ref in c.evidence_ids}
    if not refs:return result
    allowed={envelope.organisation_number,*[u['orgnr'] for u in context.get('subunits',[])]}
    for e in envelope.evidence:
        if e.id not in refs:continue
        try:
            doc=json.loads((blobs.directory/e.content_sha256).read_bytes());ad=doc.get('ad_content') or doc
            employer=ad.get('employer') or {}
            if str(employer.get('orgnr')) in allowed and employer.get('name'):result.append((employer['name'],'exact_nav_employer',[e.id]))
        except (OSError,ValueError,AttributeError):pass
    return result


def candidates(names,seen):
    """At most four distinct hosts overall, .no before .com."""
    prepared=[(name,origin,refs,labels(name)) for name,origin,refs in names]
    result=[];seen=set(seen);chosen=[]
    for position in range(4):
        for name,origin,refs,variants in prepared:
            if position<len(variants) and not any(v[3]==variants[position] for v in chosen):chosen.append((name,origin,refs,variants[position]))
            if len(chosen)==2:break
        if len(chosen)==2:break
    for suffix in ['no','com']:
        for name,origin,refs,label in chosen:
            host=label+'.'+suffix
            if host in seen or domain('https://'+host) in FREE_MAIL|SOCIAL|DIRECTORIES:continue
            seen.add(host);result.append((Candidate('https://'+host,host,'brand_name'),{'name':name,'source':origin,'evidence_ids':list(refs)}))
            if len(result)==4:return result
    return result
