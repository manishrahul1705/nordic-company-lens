"""Official BRREG snapshot name collisions can withhold a profile, never prove ownership."""
import gzip
import hashlib
import json
import re
import threading
from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qs,urlsplit
from .shared_identifiers import folded

DATASET_SHA='f3f4f93d2e4c597c15b3d08193d0a055e0bcc788a858b8bec8fcf7e8438f1dba'
ROWS=1181598
INDEX_SHA='f4d34fa1fe6f564bd241098fe7a00e944c5296d1d1760e0ab7bd668815a5ee38'
LOCK=threading.RLock()
FORMS={'as','asa','ans','da','enk','nuf','sa','ba','ks','iks','sti'}
QUALIFIERS=('gruppen','norway','norge','global','group')


def name_keys(name):
    value=re.sub(r'\ba\s*/\s*s\b','as',folded(name))
    parts=re.findall(r'[a-z0-9]+',value)
    keys={''.join(parts)}
    while parts and parts[-1] in FORMS:parts.pop()
    while parts and parts[0] in FORMS:parts.pop(0)
    keys.add(''.join(parts))
    return keys-{''}


def handle_keys(value):
    keys={value}
    current=value
    while True:
        tail=next((suffix for suffix in QUALIFIERS if current.endswith(suffix) and len(current)>len(suffix)),None)
        if not tail:break
        current=current[:-len(tail)];keys.add(current)
    return keys-{''}


def index():
    with LOCK:return _index()


@lru_cache(maxsize=1)
def _index():
    paths=(Path(__file__).resolve().parents[1]/'data/social_company_names.json.gz',
           Path(__file__).resolve().parents[3]/'data/social_company_names.json.gz')
    try:
        path=next(p for p in paths if p.exists())
        assert hashlib.sha256(path.read_bytes()).hexdigest()==INDEX_SHA
        with gzip.open(path,'rt',encoding='utf-8') as source:data=json.load(source)
        assert data['schema_version']==2 and data['dataset_sha256']==DATASET_SHA
        assert data['source_url']=='https://data.brreg.no/enhetsregisteret/api/enheter/lastned/csv'
        records=data['companies'];assert len(records)==ROWS
        names=dict(records);assert len(names)==ROWS
        keys={}
        for org,name in records:
            for key in name_keys(name):keys.setdefault(key,[]).append(org)
        return {'names':names,'keys':keys,'rows':ROWS,'dataset_sha256':DATASET_SHA,'source_url':data['source_url']}
    except (OSError,ValueError,KeyError,TypeError,AssertionError,StopIteration):
        return None  # Missing/corrupt protection must never silently authorize.


def registered_relations(envelope):
    """Only available, own-company registry relationship claims qualify."""
    org=envelope.organisation_number
    evidence={e.id:e for e in envelope.evidence}
    result={}
    for claim in envelope.claims:
        if claim.availability!='available' or claim.carried_forward or not isinstance(claim.value,dict):continue
        value=claim.value;kind=None;other=None
        if claim.field.startswith('subunits.unit.'):
            kind='subunit';other=value.get('organisation_number')
        elif claim.field=='identity.group_structure.parent':
            kind='parent';other=value.get('parentOrganisasjonsnummer')
        elif claim.field.startswith('identity.group_structure.subsidiary.') and str(value.get('parentOrganisasjonsnummer'))==org:
            kind='subsidiary';other=value.get('organisasjonsnummer')
        if not kind or not re.fullmatch(r'\d{9}',str(other)):continue
        refs=[]
        for ref in claim.evidence_ids:
            e=evidence.get(ref)
            if not e or e.source_class!='official_registry':continue
            p=urlsplit(e.source_url)
            if p.scheme!='https' or p.hostname!='data.brreg.no' or p.username or p.password:continue
            own=(p.path=='/enhetsregisteret/api/underenheter' and parse_qs(p.query).get('overordnetEnhet')==[org]
                 if kind=='subunit' else p.path=='/enhetsregisteret/api/konsernstruktur/'+org)
            if own:refs.append(ref)
        if refs:result[str(other)]={'kind':kind,'claim_id':claim.id,'evidence_ids':refs}
    return result


def assess(url,context):
    from .social_links import handle
    data=index()
    if data is None:return {'state':'withhold','reason':'universe_name_index_unavailable','matches':[]}
    org=context.get('organisation_number')
    if not org:
        # Extraction helper calls without a subject cannot grant exceptions.
        # Publication always rechecks with the envelope's exact orgnr.
        org=''
    matches={}
    for key in handle_keys(handle(url)):
        for other in data['keys'].get(key,[]):matches[other]=data['names'][other]
    relations=context.get('registered_social_relations',{})
    details=[]
    for other,name in sorted(matches.items()):
        if other==org:continue
        relation=relations.get(other)
        details.append({'organisation_number':other,'name':name,'permitted_registry_relationship':relation})
    blocked=[m for m in details if not m['permitted_registry_relationship']]
    return {'state':'withhold' if blocked else 'allow','reason':'other_registered_company' if blocked else None,
            'matches':details,'normalised_handle_keys':sorted(handle_keys(handle(url))),
            'universe_rows':data['rows'],'universe_dataset_sha256':data['dataset_sha256'],'universe_source_url':data['source_url']}
