"""Deterministically index the authorized local XLSX; never download at runtime."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

from signalpost.sources.skattefunn import CATALOGUE, URL, LICENCE, value, decision_date

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
COLUMNS = ('Prosjektnummer', 'Bedriftsnavn', 'Prosjekttittel', 'Organisasjonsnummer',
           'Søknad godkjent', 'Søknad avslått', 'Prosjektets fra-år', 'Prosjektets til-år', 'Vedtaksdato')
LICENCE_BASIS = ("data.norge.no lists the dataset 'Innsendte søknader til SkatteFUNN' (Forskningsrådet) under NLOD 2.0 "
    + CATALOGUE + ". The catalogue's distribution link (nov24.xlsx) returned HTTP 404 on 2026-11-20. "
    "We use the provider's current publication of the same dataset, linked from its SkatteFUNN page, "
    "and treat it as covered by the dataset's catalogued licence. Attribution: Forskningsrådet, NLOD 2.0.")


def read_rows(path):
    with zipfile.ZipFile(path) as z:
        strings = [''.join(t.text or '' for t in x.findall('.//m:t', NS))
                   for x in ET.fromstring(z.read('xl/sharedStrings.xml'))]
        workbook = ET.fromstring(z.read('xl/workbook.xml'))
        if workbook.find('m:workbookPr', NS).get('date1904') in {'1', 'true'}:
            raise ValueError('Unsupported 1904 date epoch')
        sheets = workbook.findall('m:sheets/m:sheet', NS)
        if len(sheets) != 1 or sheets[0].get('name') != 'Rapport 1':
            raise ValueError('Unexpected workbook sheets')
        headers = None
        # Decode cells directly, including Excel error cells, with no formula evaluation.
        with z.open('xl/worksheets/sheet1.xml') as f:
            for _, row in ET.iterparse(f, events=('end',)):
                if row.tag != '{' + NS['m'] + '}row':
                    continue
                cells = {}
                for c in row:
                    raw = c.findtext('m:v', '', NS)
                    if c.get('t') == 's':
                        raw = strings[int(raw)]
                    elif c.get('t') == 'inlineStr':
                        raw = ''.join(t.text or '' for t in c.findall('.//m:t', NS))
                    cells[c.get('r').rstrip('0123456789')] = raw
                if headers is None:
                    headers = cells
                    if not set(COLUMNS + ('Innsendt dato',)) <= set(headers.values()):
                        raise ValueError('Missing required source columns')
                else:
                    yield int(row.get('r')), {name: cells.get(col, '') for col, name in headers.items()}
                row.clear()


def build(path, retrieved_at, output):
    path, output = Path(path), Path(output)
    with path.open('rb') as f:
        sha = hashlib.file_digest(f, 'sha256').hexdigest()
    records = {}; excluded = Counter(); occurrences = Counter(); total = 0; submitted = []
    for n, row in read_rows(path):
        total += 1
        day = decision_date(row.get('Innsendt dato'))
        if day:
            submitted.append(day)
        cells = {k: row[k] for k in COLUMNS}
        v = value(cells)
        if v is None:
            excluded['unapproved_or_invalid_explicit_cells'] += 1
            continue
        key = v['project_id']
        occurrences[key] += 1
        if key not in records:
            records[key] = {'sheet': 'Rapport 1', 'source_row': n, 'source_cells': cells}
    grouped = defaultdict(list)
    for project, record in sorted(records.items()):
        if occurrences[project] > 1:
            excluded['ambiguous_duplicate_project_rows'] += occurrences[project]
            continue
        grouped[record['source_cells']['Organisasjonsnummer']].append(record)
    output.mkdir(parents=True, exist_ok=True)
    dest = output / 'skattefunn_snapshot.zip'
    with zipfile.ZipFile(dest, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for org, rows in sorted(grouped.items()):
            info = zipfile.ZipInfo(org + '.json', date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, json.dumps(rows, ensure_ascii=False, separators=(',', ':')), compresslevel=9)
    manifest = {'schema_version': 1, 'source_url': URL, 'distribution_url': URL,
        'catalogue_url': CATALOGUE, 'provider_page': 'https://www.forskningsradet.no/skattefunn/suksesshistorier/',
        'catalogued_distribution_url': 'https://www.forskningsradet.no/contentassets/3bc989967e0b4225b622ae88ffb7b66f/skattefunn_innsendte_soknader-nov24.xlsx',
        'catalogued_distribution_status': 404, 'catalogued_distribution_checked_on': '2026-11-20',
        'licence': 'NLOD 2.0', 'licence_url': LICENCE, 'licence_basis': LICENCE_BASIS,
        'credit': 'Forskningsrådet', 'retrieved_at': retrieved_at, 'dataset_sha256': sha,
        'dataset_bytes': path.stat().st_size, 'dataset_rows': total,
        'indexed_records': sum(map(len, grouped.values())), 'indexed_companies': len(grouped), 'excluded': dict(excluded),
        'coverage_period': {'provider_publication_label': '2002–2024',
            'workbook_submission_dates_min': min(submitted), 'workbook_submission_dates_max': max(submitted),
            'note': 'Period comes from explicit workbook application-date cells; project periods can extend outside it.'},
        'source_columns': list(COLUMNS), 'index_bytes': dest.stat().st_size,
        'index_sha256': hashlib.sha256(dest.read_bytes()).hexdigest(),
        'transformations': ['Read Rapport 1 XLSX cells, retaining source row number and selected original cell values.',
            'Require exact valid orgnr, approved JA, rejected NEI, project number and nonblank title; exclude duplicate project numbers.',
            'Convert numeric Excel 1900-epoch decision dates to ISO dates; missing/#N/A/invalid date becomes null.',
            'Only explicit four-digit project years; no inferred dates or monetary benefit.',
            'Group by exact applicant orgnr in sorted deterministic ZIP; no raw workbook committed.',
            'Runtime deduplicates against published research project numbers; no subunit/parent/name expansion and zero HTTP.'],
        'limitations': ['Historical approval is not proof of a claimed tax deduction, grant or cash payment.',
            'Absence is not evidence of no approval; newer-system applications are not covered by this historical publication.']}
    (output / 'skattefunn_snapshot_manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return manifest


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('source', type=Path)
    p.add_argument('--retrieved-at', required=True)
    p.add_argument('--output', type=Path, default=Path('src/signalpost/data'))
    a = p.parse_args()
    print(json.dumps(build(a.source, a.retrieved_at, a.output), ensure_ascii=True, indent=2))
