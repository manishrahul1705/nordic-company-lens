import hashlib
import json
import socket
import zipfile

import pytest
from signalpost.sources import skattefunn as S
from signalpost.sources.blobstore import BlobStore
from signalpost.sources.extract import Section, Source, add
from tests.test_funding_snapshots import envelope, ORG


def cells(**changes):
    row = {'Prosjektnummer': '123456', 'Bedriftsnavn': 'Example AS', 'Prosjekttittel': 'Research project',
        'Organisasjonsnummer': ORG, 'Søknad godkjent': 'JA', 'Søknad avslått': 'NEI',
        'Prosjektets fra-år': '2020', 'Prosjektets til-år': '2023', 'Vedtaksdato': '43831.75'}
    row.update(changes)
    return row


@pytest.mark.parametrize('raw,expected', [('', None), ('#N/A', None), ('NaN', None), ('bad', None),
    ('-2', None), ('43831.75', '2020-01-01'), ('43890', '2020-02-29')])
def test_explicit_excel_decision_dates(raw, expected):
    assert S.decision_date(raw) == expected


@pytest.mark.parametrize('patch', [{'Søknad godkjent': 'NEI'}, {'Søknad godkjent': ''},
    {'Søknad avslått': 'JA'}, {'Organisasjonsnummer': '123456789'}, {'Prosjektnummer': ''},
    {'Prosjekttittel': ' '}, {'Prosjektets fra-år': '2024', 'Prosjektets til-år': '2020'}])
def test_only_explicit_uncontradicted_approvals(patch):
    assert S.value(cells(**patch)) is None


def test_years_are_not_inferred_and_tax_deduction_has_no_amount():
    v = S.value(cells(**{'Vedtaksdato': '#N/A', 'Prosjektets fra-år': '45292'}))
    assert v['decision_date'] is None and v['start_year'] is None
    assert v['instrument_type'] == 'R&D tax deduction'
    assert not {'amount', 'grant', 'awarded_amount'} & v.keys()


def install(tmp_path, monkeypatch, rows):
    path = tmp_path / 'bundle.zip'
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr(ORG + '.json', json.dumps([{'sheet': 'Rapport 1', 'source_row': n + 2, 'source_cells': r}
            for n, r in enumerate(rows)]))
    monkeypatch.setattr(S, 'bundle', lambda: (path, {'retrieved_at': '2026-11-20T12:48:21Z', 'dataset_sha256': 'a' * 64}))


def test_offline_exact_matching_evidence_and_idempotence(tmp_path, monkeypatch):
    monkeypatch.setattr(socket, 'socket', lambda *a, **k: pytest.fail('runtime HTTP forbidden'))
    install(tmp_path, monkeypatch, [cells(), cells(**{'Organisasjonsnummer': '981508134'})])
    row = envelope(); blobs = BlobStore(tmp_path / 'state')
    S.publish(row, blobs); S.publish(row, blobs)
    claims = [c for c in row.claims if c.field.startswith('skattefunn.')]
    assert len(claims) == 1 and claims[0].value['organisation_number'] == ORG
    ev = next(e for e in row.evidence if e.id in claims[0].evidence_ids)
    body = blobs.read(ev.content_sha256)
    assert hashlib.sha256(body).hexdigest() == ev.content_sha256 and ev.claim_span in body.decode()
    assert ev.source_url == S.URL and 'Rapport 1 row 2' in ev.source_identifier
    assert row.run.refresh['funding_snapshots']['skattefunn']['runtime_http_requests'] == 0


def test_deduplicates_only_published_research_project_number(tmp_path, monkeypatch):
    install(tmp_path, monkeypatch, [cells()]); row = envelope(); blobs = BlobStore(tmp_path / 'state')
    body = b'{"project_id":"123456"}'; section = Section()
    add(section, Source('https://example.no/source', body, blobs.put(body), '2026-11-20T00:00:00Z'),
        ORG, 'funding', 'research.123456', {'project_id': '123456'}, '/')
    row.claims.extend(section.claims); row.evidence.extend(section.evidence)
    S.publish(row, blobs)
    assert not any(c.field.startswith('skattefunn.') for c in row.claims)
    assert row.run.refresh['funding_snapshots']['skattefunn']['deduplicated'] == 1
    row.claims = []; S.publish(row, blobs)
    assert any(c.field.startswith('skattefunn.') for c in row.claims)


def test_no_identity_no_publication_and_no_absence_claim(tmp_path, monkeypatch):
    install(tmp_path, monkeypatch, [cells()]); row = envelope(); row.run.sections['identity'] = 'failed'
    S.publish(row, BlobStore(tmp_path / 'state'))
    assert not any(c.field.startswith('skattefunn.') for c in row.claims)
    row = envelope('981508134'); S.publish(row, BlobStore(tmp_path / 'state'))
    assert not any(c.field.startswith('skattefunn.') for c in row.claims)


def test_bundle_is_pinned_and_packaged():
    path, m = S.bundle()
    assert path.stat().st_size == m['index_bytes'] and m['dataset_rows'] == 70599
    assert m['indexed_records'] + sum(m['excluded'].values()) == m['dataset_rows']
    assert m['licence_url'] == S.LICENCE and 'HTTP 404 on 2026-11-20' in m['licence_basis']


def test_builder_deterministic_and_drops_ambiguous_duplicate_numbers(tmp_path, monkeypatch):
    from scripts import build_skattefunn_snapshot as B
    source = tmp_path / 'source.xlsx'; source.write_bytes(b'local test workbook')
    rows = [cells(), cells(**{'Prosjektnummer': '222222'}), cells(**{'Prosjektnummer': '222222'})]
    monkeypatch.setattr(B, 'read_rows', lambda p: iter((n + 2, dict(r, **{'Innsendt dato': '43831'})) for n, r in enumerate(rows)))
    a = B.build(source, '2026-11-20T00:00:00Z', tmp_path / 'a')
    b = B.build(source, '2026-11-20T00:00:00Z', tmp_path / 'b')
    assert a == b and a['indexed_records'] == 1 and a['excluded']['ambiguous_duplicate_project_rows'] == 2


def test_xlsx_reader_preserves_error_and_sparse_cells(tmp_path):
    from scripts.build_skattefunn_snapshot import read_rows, COLUMNS
    from xml.sax.saxutils import escape
    columns = COLUMNS + ('Innsendt dato',)
    ns = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    header = ''.join('<c r="' + chr(65 + i) + '1" t="s"><v>' + str(i) + '</v></c>' for i in range(len(columns)))
    # An omitted title is empty, and an Excel error stays #N/A, not a guessed date.
    data = '<c r="A2"><v>123456</v></c><c r="I2" t="e"><v>#N/A</v></c>'
    path = tmp_path / 'fixture.xlsx'
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr('xl/workbook.xml', '<workbook xmlns="' + ns + '"><workbookPr/><sheets><sheet name="Rapport 1"/></sheets></workbook>')
        z.writestr('xl/sharedStrings.xml', '<sst xmlns="' + ns + '">' + ''.join('<si><t>' + escape(c) + '</t></si>' for c in columns) + '</sst>')
        z.writestr('xl/worksheets/sheet1.xml', '<worksheet xmlns="' + ns + '"><sheetData><row r="1">' + header + '</row><row r="2">' + data + '</row></sheetData></worksheet>')
    rows = list(read_rows(path))
    assert rows[0][0] == 2 and rows[0][1]['Prosjektnummer'] == '123456'
    assert rows[0][1]['Vedtaksdato'] == '#N/A' and rows[0][1]['Prosjekttittel'] == ''


def test_changed_bundle_cannot_authorize_claims(tmp_path, monkeypatch):
    (tmp_path / 'skattefunn_snapshot.zip').write_bytes(b'corrupt')
    (tmp_path / 'skattefunn_snapshot_manifest.json').write_text(json.dumps({
        'index_sha256': S.INDEX_SHA, 'source_url': S.URL, 'licence_url': S.LICENCE, 'catalogue_url': S.CATALOGUE}))
    monkeypatch.setattr(S, 'BASE', tmp_path); S.bundle.cache_clear()
    try:
        row = envelope(); S.publish(row, BlobStore(tmp_path / 'state'))
        assert row.run.refresh['funding_snapshots']['skattefunn']['state'] == 'snapshot_unavailable'
        assert not any(c.field.startswith('skattefunn.') for c in row.claims)
    finally:
        S.bundle.cache_clear()


def test_enabled_runner_publishes_skattefunn_without_http(tmp_path, monkeypatch):
    from tests.test_registry import config, execute
    org = '923609016'
    path = tmp_path / 'runner.zip'
    with zipfile.ZipFile(path, 'w') as z:
        z.writestr(org + '.json', json.dumps([{'sheet': 'Rapport 1', 'source_row': 2,
            'source_cells': cells(**{'Organisasjonsnummer': org})}]))
    monkeypatch.setattr(S, 'bundle', lambda: (path, {'retrieved_at': '2026-11-20T12:48:21Z', 'dataset_sha256': 'a' * 64}))
    report, rows = execute(config(tmp_path, [org], funding_snapshots=True))
    assert any(c['field'] == 'skattefunn.123456' for c in rows[0]['claims'])
    assert not any('forskningsradet.no' in r['url'] for r in report['request_log'])
    assert rows[0]['run']['refresh']['funding_snapshots']['skattefunn']['runtime_http_requests'] == 0
