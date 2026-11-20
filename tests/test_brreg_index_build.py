"""Offline checks for official-source index derivation and provenance failures."""
import csv
import gzip
import hashlib
import json
import pytest
from scripts.brreg_index_data import SOURCE_URL, read_source
from scripts.build_social_company_names import build as names
from scripts.build_registry_domains import build as domains


def fixture(tmp_path, records):
    source=tmp_path/'official.csv.gz'
    with gzip.open(source,'wt',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=['organisasjonsnummer','navn','hjemmeside']);writer.writeheader()
        writer.writerows(records)
    manifest=tmp_path/'download.json'
    manifest.write_text(json.dumps({'source_url':SOURCE_URL,'http_status':200,
        'retrieved_at':'2026-11-20T00:00:00Z',
        'dataset_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}))
    return source,manifest


def test_official_builds_include_all_entities_and_only_shared_domains(tmp_path):
    source,manifest=fixture(tmp_path,[
        {'organisasjonsnummer':'980362779','navn':'RENTHALL AS','hjemmeside':'https://www.example.no/a'},
        {'organisasjonsnummer':'937920040','navn':'HALLMAKER AS','hjemmeside':'https://example.no/b'},
        {'organisasjonsnummer':'914992605','navn':'VALDRESOST AS','hjemmeside':'https://unique.no'},
        {'organisasjonsnummer':'123456789','navn':'INVALID','hjemmeside':'https://example.no'}])
    nm=names(source,manifest,tmp_path/'names.gz',tmp_path/'names.json')
    dm=domains(source,manifest,tmp_path/'domains.gz',tmp_path/'domains.json')
    n=json.loads(gzip.decompress((tmp_path/'names.gz').read_bytes()))
    d=json.loads(gzip.decompress((tmp_path/'domains.gz').read_bytes()))
    assert nm['rows']==3 and nm['dataset_rows']==4 and nm['invalid_orgnr_rows_excluded']==1
    assert len(n['companies'])==3 and d['domains']=={'example.no':['937920040','980362779']}
    assert dm['rows']==1 and dm['website_rows']==3
    assert n['licence_url']=='https://data.norge.no/nlod/en/2.0' and n['credit']=='Br\u00f8nn\u00f8ysundregistrene'
    assert n['source_url']==SOURCE_URL and n['transformations'] and nm['dataset_sha256']==dm['dataset_sha256']


def test_index_builder_refuses_mismatched_dataset_hash(tmp_path):
    source,manifest=fixture(tmp_path,[])
    with source.open('ab') as f:f.write(b'changed')
    with pytest.raises(ValueError,match='hash mismatch'):read_source(source,manifest)


def test_index_builder_refuses_nonofficial_source(tmp_path):
    source,manifest=fixture(tmp_path,[])
    data=json.loads(manifest.read_text());data['source_url']='https://builderr.ai/universe';manifest.write_text(json.dumps(data))
    with pytest.raises(ValueError,match='source URL'):read_source(source,manifest)


def test_index_builder_refuses_duplicate_company_identity(tmp_path):
    row={'organisasjonsnummer':'980362779','navn':'RENTHALL AS','hjemmeside':''}
    source,manifest=fixture(tmp_path,[row,row])
    with pytest.raises(ValueError,match='Duplicate organisation'):read_source(source,manifest)
