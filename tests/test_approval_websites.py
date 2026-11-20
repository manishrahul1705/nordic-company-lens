import gzip, hashlib, json, socket
import pytest
from signalpost.sources import approval_websites as S
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.extract import Section,Source,add
from tests.test_funding_snapshots import envelope as baseline_envelope,ORG
TARGET='981508734'
def envelope():
    e=baseline_envelope();e.claims=[];e.evidence=[];return e

@pytest.mark.parametrize('status,approved',[('Godkjent med ansatte',True),('Godkjent uten ansatte',True),('Ikke godkjent',False),('Søknad under behandling',False),('HMS-kortbestilling under behandling',False)])
def test_exact_cleaning_status(tmp_path,monkeypatch,status,approved):
    e=envelope();blobs=BlobStore(tmp_path)
    def bundle(k):return ({ORG:{'organisation_number':ORG,'name':'Example','status':status}} if k=='cleaning' else {},{'source_url':'https://example.no/bulk','retrieved_at':'2026-11-20T00:00:00Z','dataset_sha256':'a'*64,'licence_url':'https://data.norge.no/nlod/no/2.0'})
    monkeypatch.setattr(S,'bundle',bundle);monkeypatch.setattr(socket,'socket',lambda *a,**k:pytest.fail('network'))
    S.publish(e,blobs);assert len(e.claims)==1;assert e.claims[0].value['status']==status;assert e.claims[0].value['approved'] is approved
    S.publish(e,blobs);assert len(e.claims)==1

def test_bundle_hash_corruption(tmp_path,monkeypatch):
    monkeypatch.setattr(S,'BASE',tmp_path);S.bundle.cache_clear()
    (tmp_path/'cleaning_official.json.gz').write_bytes(gzip.compress(b'{}'))
    (tmp_path/'cleaning_official_manifest.json').write_text(json.dumps({'index_sha256':'bad'}))
    with pytest.raises(ValueError):S.bundle('cleaning')
    S.bundle.cache_clear()

def test_no_match_no_claim_and_invalid_identity(tmp_path):
    e=envelope();S.publish(e,BlobStore(tmp_path));assert not any(c.field.startswith('cleaning_approval.')for c in e.claims)
    e.run.sections['identity']='failed';S.publish(e,BlobStore(tmp_path))

def test_related_requires_published_relationship_and_dual_evidence(tmp_path,monkeypatch):
    e=envelope();blobs=BlobStore(tmp_path);m={'source_url':'https://data.brreg.no/enhetsregisteret/api/enheter/lastned/csv','retrieved_at':'2026-11-20T00:00:00Z','dataset_sha256':'a'*64,'licence_url':'https://data.norge.no/nlod/no/2.0'}
    monkeypatch.setattr(S,'bundle',lambda k:({TARGET:{'organisasjonsnummer':TARGET,'navn':'Related AS','hjemmeside':'example.no'}} if k=='related'else {},m))
    S.publish(e,blobs);assert not e.claims
    sec=Section();body=json.dumps({'parentOrganisasjonsnummer':TARGET}).encode();add(sec,Source('https://data.brreg.no/group',body,blobs.put(body),m['retrieved_at']),ORG,'identity','identity.group_structure.parent',{'parentOrganisasjonsnummer':TARGET},'/')
    e.claims.extend(sec.claims);e.evidence.extend(sec.evidence);S.publish(e,blobs)
    c=e.claims[-1];assert c.field.startswith('related_company_website.');assert len(c.evidence_ids)==2;assert sec.evidence[0].id in c.evidence_ids
    assert c.value['verification']=='registry-declared, not ownership-verified';assert not any(c.field in ('official_website','social_profile','news_item','public_brand')for c in e.claims)

def test_workshop_exact_identifier_and_two_numbers_one_company(tmp_path,monkeypatch):
    e=envelope();m={'source_url':'https://example.no/export','retrieved_at':'2026-11-20T00:00:00Z','dataset_sha256':'a'*64,'licence_url':'https://data.norge.no/nlod/no'}
    rows=[{'Organisasjonsnummer':ORG,'Godkjenningsnummer':str(n),'Godkjenningstyper':'BILGLASS','Adresse':str(n)}for n in (1,2)]+[{'Organisasjonsnummer':TARGET,'Godkjenningsnummer':'3'}]
    monkeypatch.setattr(S,'bundle',lambda k:({ORG:rows} if k=='workshop'else {},m));S.publish(e,BlobStore(tmp_path));assert len(e.claims)==2;assert {c.value['Godkjenningsnummer']for c in e.claims}=={'1','2'}
