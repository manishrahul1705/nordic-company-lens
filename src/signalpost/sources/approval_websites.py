"""Exact-identifier bulk approvals and explicitly scoped related registry websites."""
import gzip, hashlib, json
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit
from ..identity.orgnr import valid
from .extract import Source, Section, add
BASE=Path(__file__).resolve().parents[1]/'data'

@lru_cache(maxsize=3)
def bundle(kind):
    body=(BASE/(kind+'_official.json.gz')).read_bytes()
    manifest=json.loads((BASE/(kind+'_official_manifest.json')).read_text(encoding='utf-8'))
    if hashlib.sha256(body).hexdigest()!=manifest['index_sha256']:raise ValueError('Official snapshot hash mismatch')
    return json.loads(gzip.decompress(body)),manifest

def publish(envelope,blobs):
    org=envelope.organisation_number
    if not valid(org) or envelope.run.sections.get('identity')!='available':return
    prefixes=('cleaning_approval.','workshop_approval.','related_company_website.')
    envelope.claims=[c for c in envelope.claims if not c.field.startswith(prefixes)]
    section=Section();diagnostic={'runtime_http_requests':0}
    envelope.run.refresh['approval_websites']=diagnostic
    def emit(kind,key,value,source_row,extra=()):
        _,m=bundle(kind)
        body=json.dumps(source_row,ensure_ascii=False,separators=(',',':')).encode()
        source=Source(m['source_url'],body,blobs.put(body),m['retrieved_at'],
            'Official bulk selected-row JSON derivation; dataset SHA-256 '+m['dataset_sha256'])
        add(section,source,org,'registry_enrichment',key,value,'/',method='signalpost.official-bulk.selected-row.v1')
        section.claims[-1].evidence_ids.extend(extra)
        section.claims[-1].reasons.update(licence=m['licence_url'],snapshot='Bundled historical snapshot; absence is not a negative finding')
    for kind in ('cleaning','workshop','related'):
        data,m=bundle(kind)
        if kind=='cleaning' and org in data:
            r=data[org]
            if r.get('status'):
                emit(kind,'cleaning_approval.status',dict(r,approved=r['status'] in ('Godkjent med ansatte','Godkjent uten ansatte')),r)
        elif kind=='workshop':
            for r in data.get(org,[]):
                number=r.get('Godkjenningsnummer')
                if number and r.get('Organisasjonsnummer')==org:
                    emit(kind,'workshop_approval.'+number,r,r)
        elif kind=='related':
            evidence={e.id:e for e in envelope.evidence}
            for claim in envelope.claims:
                if claim.availability!='available' or not claim.evidence_ids or not all(e in evidence for e in claim.evidence_ids):continue
                if claim.field=='identity.group_structure.parent':
                    relationship='parent';target=claim.value.get('parentOrganisasjonsnummer')
                elif claim.field.startswith('identity.group_structure.subsidiary.'):
                    relationship='subsidiary';target=claim.value.get('organisasjonsnummer')
                    if claim.value.get('parentOrganisasjonsnummer')!=org:continue
                else:continue
                r=data.get(target)
                if not r or target==org or not valid(target):continue
                url=r['hjemmeside'].strip();parsed=urlsplit(url if '://' in url else 'https://'+url)
                if parsed.scheme not in ('https','http') or not parsed.hostname or parsed.username:continue
                emit(kind,'related_company_website.'+relationship+'.'+target,
                    dict(r,relationship=relationship,verification='registry-declared, not ownership-verified'),r,claim.evidence_ids)
    envelope.claims.extend(section.claims)
    evidence={e.id:e for e in envelope.evidence};evidence.update({e.id:e for e in section.evidence});envelope.evidence=list(evidence.values())
    diagnostic['published']=len(section.claims)
