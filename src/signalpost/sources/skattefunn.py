"""Exact-subject historical SkatteFUNN approvals; no runtime network access."""
import hashlib
import json
import zipfile
from datetime import datetime, timedelta
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from pathlib import Path

from ..identity.orgnr import valid
from .extract import Section, Source, add

BASE = Path(__file__).resolve().parents[1] / 'data'
CATALOGUE = 'https://data.norge.no/nb/datasets/f82d3d4a-b0f8-3220-83ef-15fbd854c54f/innsendte-soknader-til-skattefunn'
URL = 'https://www.forskningsradet.no/siteassets/skattefunn/tall/skattefunn-innsendte-soknader-2002-2024.xlsx'
LICENCE = 'https://data.norge.no/nlod/en/2.0'
SCHEME = 'SkatteFUNN (R&D tax deduction scheme)'
INDEX_SHA = 'cccfc6d455b958ece0a6d22371192398c20dfce39d93eb912d6dcd1938f7fbd5'


def year(raw):
    return int(raw) if isinstance(raw, str) and len(raw) == 4 and raw.isascii() and raw.isdigit() and 1900 <= int(raw) <= 2200 else None


def decision_date(raw):
    """Source date cells use Excel's 1900 epoch; never use application dates."""
    if not raw or raw == '#N/A':
        return None
    try:
        serial = Decimal(raw)
        if not serial.is_finite() or not 61 <= serial < 110000:
            return None
        return (datetime(1899, 12, 30) + timedelta(days=int(serial))).date().isoformat()
    except (InvalidOperation, TypeError, ValueError, OverflowError):
        return None


def value(cells):
    org = cells.get('Organisasjonsnummer', '')
    project = cells.get('Prosjektnummer', '')
    title = cells.get('Prosjekttittel', '')
    if (not valid(org) or cells.get('Søknad godkjent') != 'JA'
            or cells.get('Søknad avslått') != 'NEI'
            or not project.isascii() or not project.isdigit() or not title.strip()):
        return None
    start, end = year(cells.get('Prosjektets fra-år')), year(cells.get('Prosjektets til-år'))
    if start is not None and end is not None and start > end:
        return None
    return {'project_id': project, 'title': title, 'organisation_number': org,
            'applicant_name': cells.get('Bedriftsnavn'), 'scheme': SCHEME,
            'instrument_type': 'R&D tax deduction', 'approval_status': 'approved',
            'start_year': start, 'end_year': end,
            'decision_date': decision_date(cells.get('Vedtaksdato')),
            'scope': 'Approved R&D tax deduction application; not a grant, cash payment or proof of a claimed deduction.'}


@lru_cache(maxsize=1)
def bundle():
    path = BASE / 'skattefunn_snapshot.zip'
    manifest = json.loads((BASE / 'skattefunn_snapshot_manifest.json').read_text(encoding='utf-8'))
    with path.open('rb') as handle:
        sha = hashlib.file_digest(handle, 'sha256').hexdigest()
    if (sha != INDEX_SHA or sha != manifest['index_sha256']
            or manifest['source_url'] != URL or manifest['licence_url'] != LICENCE
            or manifest['catalogue_url'] != CATALOGUE):
        raise ValueError('SkatteFUNN snapshot provenance/hash mismatch')
    return path, manifest


@lru_cache(maxsize=1)
def archive(path):
    return zipfile.ZipFile(path)


def publish(envelope, blobs):
    org = envelope.organisation_number
    if not valid(org) or envelope.run.sections.get('identity') != 'available':
        return
    envelope.claims = [c for c in envelope.claims if not c.field.startswith('skattefunn.')]
    diagnostic = {'mode': 'bundled_snapshot', 'runtime_http_requests': 0, 'published': 0, 'deduplicated': 0}
    envelope.run.refresh.setdefault('funding_snapshots', {})['skattefunn'] = diagnostic
    try:
        path, manifest = bundle()
        try:
            records = json.loads(archive(path).read(org + '.json'))
        except KeyError:
            records = []
        # Only actually published research claims suppress an approval.
        research_ids = {str(c.value['project_id']) for c in envelope.claims
                        if c.field.startswith('research.') and c.availability == 'available'
                        and c.evidence_ids and isinstance(c.value, dict) and 'project_id' in c.value}
        section = Section()
        for record in records:
            cells = record['source_cells']
            v = value(cells)
            if v is None or v['organisation_number'] != org:
                continue
            if v['project_id'] in research_ids:
                diagnostic['deduplicated'] += 1
                continue
            body = json.dumps(cells, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
            source = Source(URL, body, blobs.put(body), manifest['retrieved_at'],
                'NLOD 2.0; Forskningsrådet; selected XLSX cells (UTF-8 JSON derivation), '
                + record['sheet'] + ' row ' + str(record['source_row'])
                + '; full dataset SHA-256 ' + manifest['dataset_sha256'])
            add(section, source, org, 'funding', 'skattefunn.' + v['project_id'], v, '/',
                method='signalpost.funding.xlsx-selected-row.v1')
            section.claims[-1].reasons.update(label=SCHEME, licence=LICENCE,
                attribution='Forskningsrådet', snapshot='Historical bundled approval; not live-checked')
        envelope.claims.extend(section.claims)
        evidence = {e.id: e for e in envelope.evidence}
        evidence.update({e.id: e for e in section.evidence})
        envelope.evidence = list(evidence.values())
        diagnostic.update(published=len(section.claims), state='available' if section.claims else 'not_established_in_snapshot',
            dataset_sha256=manifest['dataset_sha256'], snapshot_retrieved_at=manifest['retrieved_at'])
    except (OSError, ValueError, KeyError, TypeError, zipfile.BadZipFile) as exc:
        diagnostic.update(state='snapshot_unavailable', error=type(exc).__name__)
