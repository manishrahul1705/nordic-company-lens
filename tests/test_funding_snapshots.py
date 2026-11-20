import hashlib
import json
import zipfile
from pathlib import Path
import pytest
from signalpost.sources import funding_snapshots as F
from signalpost.sources.blobstore import BlobStore
from signalpost.runner import placeholder
from signalpost.models.evidence import utc_now

ORG='984024290'


def research(**kw):
    return dict(prosjektnummer='193191',prosjekttittel='Involverende planlegging',organisasjonsnummer=ORG,
        prosjektansvarlig_navn='VEIDEKKE ENTREPRENOR AS',prosjektfase='Avsluttet',tildelt_belop='12385765.0',
        soknadsdato='2008-10-14 00:00:00',prosjektstart='2009',prosjektslutt='2014',**kw)


def aid():
    return dict(id='123',status='Registrert',recipient_orgnr=ORG,recipient_name='Example AS',
        subunit_orgnr='912845575',subunit_name='Unit',funder_orgnr='974761076',funder_name='SKATTEETATEN',
        award_date='31.12.2025',amount='123,45',currency='NOK',range_from='',range_to='',range_currency='',
        instrument='Skatte- eller avgiftsfritak',scheme_id='999')


@pytest.mark.parametrize('phase',['Avslag','Mottatt','Vurderes','unknown'])
def test_research_excludes_unfunded_phases(phase):
    row=research();row['prosjektfase']=phase;assert F.value('research',row) is None


@pytest.mark.parametrize('total',['NaN','Infinity','-1','bad'])
def test_research_rejects_invalid_amounts(total):
    row=research();row['tildelt_belop']=total;assert F.value('research',row) is None


def test_research_preserves_project_total_and_dates_without_award_date_inference():
    v=F.value('research',research());assert v['total_project_award']['amount']=='12385765.0' and v['total_project_award']['currency'] is None
    assert v['application_date']=='2008-10-14' and v['start_year']==2009 and v['end_year']==2014
    assert 'collaborators may share' in v['amount_scope'] and 'award_date' not in v


@pytest.mark.parametrize('instrument,label',[('Tilskudd','grant'),('L\u00e5n','loan'),('Garanti','guarantee'),
    ('Skatte- eller avgiftsfritak','tax benefit'),('Annet','other: Annet')])
def test_state_aid_actual_instrument_and_subunit_are_preserved(instrument,label):
    r=aid();r['instrument']=instrument;v=F.value('state_aid',r)
    assert v['instrument_type']==label and v['recipient_orgnr']==ORG and v['specified_subunit_orgnr']=='912845575'
    assert v['awarded_amount']['amount']=='123.45' and v['award_date']=='2025-12-31'


def test_interval_is_not_exact_amount():
    r=aid();r.update(amount='',range_from='100',range_to='200',range_currency='EUR')
    v=F.value('state_aid',r);assert v['awarded_amount'] is None and v['amount_interval']['to']=='200'


def install(tmp_path,monkeypatch,records):
    def get(kind):
        p=tmp_path/(kind+'.zip')
        if not p.exists():
            with zipfile.ZipFile(p,'w') as z:z.writestr(ORG+'.json',json.dumps(records if kind=='research' else []))
        return p,{'source_url':F.SOURCES[kind][0],'retrieved_at':'2026-11-20T02:01:57Z',
            'dataset_sha256':'a'*64,'credit':'Forskningsradet'}
    monkeypatch.setattr(F,'bundle',get)


def envelope(org=ORG):
    e=placeholder(org,'test',utc_now());e.run.sections['identity']='available';return e


def test_publish_is_offline_exact_subject_and_idempotent(tmp_path,monkeypatch):
    install(tmp_path,monkeypatch,[{'source_row':1,'source_cells':research()}]);e=envelope();blobs=BlobStore(tmp_path/'state')
    F.publish(e,blobs);F.publish(e,blobs)
    c=[c for c in e.claims if c.family=='funding'];assert len(c)==1
    ev=next(x for x in e.evidence if x.id==c[0].evidence_ids[0]);body=blobs.read(ev.content_sha256)
    assert hashlib.sha256(body).hexdigest()==ev.content_sha256 and ev.claim_span in body.decode()
    assert 'selected CSV row' in ev.source_identifier and 'dataset SHA-256' in ev.source_identifier
    assert e.run.refresh['funding_snapshots']['research']['runtime_http_requests']==0


def test_foreign_recipient_cannot_publish_from_wrong_index_bucket(tmp_path,monkeypatch):
    row=research();row['organisasjonsnummer']='981508734';install(tmp_path,monkeypatch,[{'source_row':1,'source_cells':row}])
    e=envelope();F.publish(e,BlobStore(tmp_path/'state'));assert not any(c.family=='funding' for c in e.claims)


def test_registry_identity_failure_blocks_snapshot_publication(tmp_path,monkeypatch):
    install(tmp_path,monkeypatch,[{'source_row':1,'source_cells':research()}]);e=envelope();e.run.sections['identity']='failed'
    F.publish(e,BlobStore(tmp_path/'state'));assert not any(c.family=='funding' for c in e.claims)


def test_no_match_is_not_no_funding(tmp_path,monkeypatch):
    install(tmp_path,monkeypatch,[]);e=envelope();F.publish(e,BlobStore(tmp_path/'state'))
    assert not any(c.family=='funding' for c in e.claims)
    assert e.run.refresh['funding_snapshots']['research']['state']=='not_established_in_snapshot'


def test_missing_bundle_records_failure_not_negative_claim(tmp_path,monkeypatch):
    def fail(kind):raise FileNotFoundError('missing snapshot')
    monkeypatch.setattr(F,'bundle',fail);e=envelope();F.publish(e,BlobStore(tmp_path/'state'))
    assert e.run.refresh['funding_snapshots']['research']['state']=='snapshot_unavailable'
    assert not any(c.family=='funding' for c in e.claims)


def test_site_labels_funding_instrument_and_snapshot_scope(tmp_path,monkeypatch):
    from signalpost.site import fact
    install(tmp_path,monkeypatch,[{'source_row':1,'source_cells':research()}]);e=envelope();F.publish(e,BlobStore(tmp_path/'state'))
    c=next(c for c in e.claims if c.family=='funding');records={x.id:x.model_dump(mode='json') for x in e.evidence}
    html=fact(c.model_dump(mode='json'),records)
    assert 'total project award' in html and 'collaborators may share' in html


def test_corrupt_bundle_cannot_silently_authorize(monkeypatch,tmp_path):
    for kind in F.SOURCES:
        (tmp_path/(kind+'_snapshot.zip')).write_bytes(b'changed')
        (tmp_path/(kind+'_snapshot_manifest.json')).write_text(json.dumps({'index_sha256':'a'*64,'source_url':F.SOURCES[kind][0],'licence_url':F.LICENCE}))
    monkeypatch.setattr(F,'BASE',tmp_path);F.bundle.cache_clear()
    try:
        e=envelope();F.publish(e,BlobStore(tmp_path/'state'))
        assert not any(c.family=='funding' for c in e.claims)
        assert e.run.refresh['funding_snapshots']['state_aid']['state']=='snapshot_unavailable'
    finally:F.bundle.cache_clear()


@pytest.mark.parametrize('proven',[True,False])
def test_recipient_subunit_needs_own_registry_relationship(tmp_path,monkeypatch,proven):
    from signalpost.sources.extract import Section,Source,add
    unit='912845575'
    row=aid();row['recipient_orgnr']=unit
    def get(kind):
        path=tmp_path/(kind+'.zip')
        if not path.exists():
            with zipfile.ZipFile(path,'w') as z:
                z.writestr(unit+'.json',json.dumps([{'source_row':1,'source_cells':row}]) if kind=='state_aid' else '[]')
        return path,{'source_url':F.SOURCES[kind][0],'retrieved_at':'2026-11-20T00:00:00Z','dataset_sha256':'a'*64,'credit':'BRREG'}
    monkeypatch.setattr(F,'bundle',get);e=envelope();section=Section();blobs=BlobStore(tmp_path/'state')
    raw=json.dumps({'organisation_number':unit}).encode();sha=blobs.put(raw)
    url='https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet='+ (ORG if proven else unit)
    add(section,Source(url,raw,sha,utc_now()),ORG,'subunits','subunits.unit.'+unit,{'organisation_number':unit},'/')
    e.claims.extend(section.claims);e.evidence.extend(section.evidence)
    F.publish(e,blobs);claims=[c for c in e.claims if c.family=='funding']
    assert bool(claims)==proven
    if proven:
        assert claims[0].value['recipient_orgnr']==unit and claims[0].value['subject_company_orgnr']==ORG
        assert section.evidence[0].id in claims[0].evidence_ids


def test_bundled_snapshots_match_manifest_and_record_counts():
    for kind in F.SOURCES:
        path,manifest=F.bundle(kind)
        assert path.stat().st_size==manifest['index_bytes']
        assert manifest['indexed_records']>0 and manifest['dataset_rows']>=manifest['indexed_records']
        assert manifest['licence_url']==F.LICENCE and manifest['retrieved_at'].endswith('Z')
        assert 'source_row' in json.loads(zipfile.ZipFile(path).read(zipfile.ZipFile(path).namelist()[0]))[0]


def test_enabled_runner_publishes_bundles_without_http_source_calls(tmp_path):
    from tests.test_registry import config,execute
    from signalpost.config import Config
    cfg=config(tmp_path,['923609016'],funding_snapshots=True)
    assert Config.model_fields['funding_snapshots'].default is True
    report,rows=execute(cfg)
    funding=[c for c in rows[0]['claims'] if c['family']=='funding']
    assert report['effective_configuration']['funding_snapshots'] is True
    assert funding and any(c['field'].startswith('research.') for c in funding)
    assert any(c['field'].startswith('state_aid.') for c in funding)
    assert not any('stotte.brreg.no' in r['url'] or 'raw.githubusercontent.com' in r['url'] for r in report['request_log'])
    assert all(v['runtime_http_requests']==0 for v in rows[0]['run']['refresh']['funding_snapshots'].values())
