"""Read the official, locally downloaded Enhetsregisteret CSV for bundled indexes."""
import csv
import gzip
import hashlib
import json
from pathlib import Path
from signalpost.identity.orgnr import valid

SOURCE_URL = 'https://data.brreg.no/enhetsregisteret/api/enheter/lastned/csv'
LICENCE_URL = 'https://data.norge.no/nlod/en/2.0'
CREDIT = 'Br\u00f8nn\u00f8ysundregistrene'


def read_source(source, download_manifest):
    source = Path(source)
    metadata = json.loads(Path(download_manifest).read_text(encoding='utf-8'))
    with source.open('rb') as handle:
        digest = hashlib.file_digest(handle, 'sha256').hexdigest()
    if metadata['source_url'] != SOURCE_URL or metadata['dataset_sha256'] != digest:
        raise ValueError('Official source URL or downloaded dataset hash mismatch')
    if metadata.get('final_url', SOURCE_URL) != SOURCE_URL or metadata['http_status'] != 200:
        raise ValueError('Expected a successful direct official bulk download')
    records = {}
    rows = invalid = nameless = 0
    with gzip.open(source, 'rt', encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        if not {'organisasjonsnummer', 'navn', 'hjemmeside'} <= set(reader.fieldnames or []):
            raise ValueError('Official CSV is missing required columns')
        for row in reader:
            rows += 1
            org = row['organisasjonsnummer'].strip()
            if not valid(org):
                invalid += 1
                continue
            name = row['navn'].strip()
            if not name:
                nameless += 1
                continue
            if org in records:
                raise ValueError('Duplicate organisation number in official dataset: ' + org)
            records[org] = (name, row['hjemmeside'])
    provenance = {'source_url': SOURCE_URL, 'retrieved_at': metadata['retrieved_at'],
        'dataset_sha256': digest, 'dataset_bytes': source.stat().st_size, 'dataset_rows': rows,
        'source_format': 'gzip-compressed official UTF-8 CSV',
        'invalid_orgnr_rows_excluded': invalid, 'empty_name_rows_excluded': nameless,
        'credit': CREDIT, 'licence': 'NLOD 2.0', 'licence_url': LICENCE_URL}
    return records, provenance


def write_index(destination, payload, manifest_path, **counts):
    destination = Path(destination)
    raw = json.dumps(payload, ensure_ascii=False, separators=(',', ':'), sort_keys=True).encode('utf-8')
    destination.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
    manifest = {k: v for k, v in payload.items() if k not in {'companies', 'domains'}}
    manifest.update(counts, bytes=destination.stat().st_size,
                    index_sha256=hashlib.sha256(destination.read_bytes()).hexdigest())
    Path(manifest_path).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return manifest
