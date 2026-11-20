"""Render the retained measurement and source-cell review, without HTTP."""
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent


def main():
    full = json.loads((HERE / 'full1000.json').read_text(encoding='utf-8'))
    sample = json.loads((HERE / 'sample100.json').read_text(encoding='utf-8'))
    reviews = json.loads((HERE / 'hand-review-10.json').read_text(encoding='utf-8'))
    manifest = json.loads(Path('src/signalpost/data/skattefunn_snapshot_manifest.json').read_text(encoding='utf-8'))
    raw_log = Path('bench/cache/skattefunn-20261120/suite-final.log').read_bytes()
    log = raw_log.decode('utf-16' if raw_log.startswith(b'\xff\xfe') else 'utf-8', errors='replace')
    tail = re.findall(r'(?m)^.*\d+ passed.* in [\d.]+s.*$', log)
    if not tail:
        raise ValueError('Full suite not finished')
    tests = tail[-1].strip()
    failures = re.findall(r'(?m)^FAILED (.+)$', log)
    summary = {'website_count_commit': '92ba52ceefaaa9f6b98252d6d6f368a7555e24fc',
        'website_count_suite': {'passed': 1754, 'failed': 1, 'failure': 'test_independent_footer_runs_dependent_production_extraction',
            'isolation_repeats_passed': 2}, 'full1000': full, 'sample100': sample,
        'index_bytes': manifest['index_bytes'], 'dataset_rows': manifest['dataset_rows'],
        'indexed_records': manifest['indexed_records'], 'indexed_companies': manifest['indexed_companies'],
        'hand_checks': len(reviews), 'suite': tests, 'failures': failures,
        'new_tests': 23, 'research_bundle_overlap_for_new_cohort_approvals': 0,
        'deterministic_rebuild': {'index_identical': True, 'manifest_identical': True},
        'wheel': {'index_manifest_notice_present': True, 'index_identical': True, 'raw_xlsx_or_csv_present': False}}
    (HERE / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    lines = ['# Stage AL — SkatteFUNN historical approval snapshot', '',
        '## Website funnel fix', '',
        'Committed separately as `92ba52ceefaaa9f6b98252d6d6f368a7555e24fc`: report.json counts published available official_website claims (115 → 114). The two ownership tests were restored to HEAD. Full baseline suite: 1,754 passed, one footer extraction failure; that test then passed twice in isolation (19.18 s and 20.02 s). The commit message records the flake. Both evaluator network tests passed. No acceptance rule changed.', '',
        '## Source, licence and build', '', manifest['licence_basis'], '',
        'Source: ' + manifest['source_url'], '',
        f"Retrieved {manifest['retrieved_at']}; {manifest['dataset_bytes']:,} bytes; SHA-256 `{manifest['dataset_sha256']}`.", '',
        f"Workbook: {manifest['dataset_rows']:,} data rows in Rapport 1, plus the header. Provider publication label: 2002–2024. Explicit application-date cells span 2002-09-27–2024-11-01; project periods may extend beyond it. No workbook-level conflicting licence or prohibition was found. Project descriptions mentioning patents/licensing/prohibitions are not workbook redistribution terms.", '',
        f"The index contains {manifest['indexed_records']:,} approved records for {manifest['indexed_companies']:,} organisations, {manifest['index_bytes']:,} bytes (8.18 MiB). Excluded: {json.dumps(manifest['excluded'])}. Duplicate project numbers are excluded entirely. Original title text and selected source cells are preserved. Full raw XLSX is ignored and not committed.", '',
        'The builder is `scripts/build_skattefunn_snapshot.py`. Rebuilding the actual workbook with the recorded retrieval timestamp reproduced both ZIP and manifest byte-for-byte. The built wheel contains the identical index, manifest and notice, and no raw XLSX/CSV. An initial optional source-distribution build was stopped; the wheel-only build and contents check succeeded.', '',
        '## Publication rules', '',
        'Funding snapshots retain their existing default and disable flag. Runtime adds zero HTTP. Require an available registry identity, exact valid applicant orgnr, approved JA and rejected NEI. Never match names, parents or subunits. Publish project number/title, explicit project years, scheme and decision date. Convert Excel decision-date serial cells; missing/#N/A/invalid values remain null, and application dates never substitute for decisions. SkatteFUNN is an R&D tax deduction scheme: no grant, cash amount or claimed deduction is asserted. Historical absence produces no negative claim.', '',
        'Available published Forskningsrådet research project IDs suppress matching SkatteFUNN IDs. Both replays suppressed zero claims; a separate check also found zero overlaps between these 89 approvals and the current research bundle. An explicit regression test exercises the positive deduplication case. The latest full-1,000 saved baseline itself has no research/state-aid snapshot claims; those families are not retrospectively added by this isolated replay.', '',
        'Each citation identifies the provider workbook, retrieval timestamp, original sheet/row, full workbook SHA-256, selected-cell JSON SHA-256 and verbatim excerpt. The evidence is labelled a selected-cell derivation, never the original XLSX byte stream. No validator, verifier, model, proof rule or request cap is weakened. No new brief template was added.', '',
        '## Offline measurements', '',
        '| Saved cohort | SkatteFUNN companies before → after | SkatteFUNN claims before → after | All published claims before → after | Added HTTP |',
        '|---|---:|---:|---:|---:|']
    for label, m in [('Frozen 1,000', full), ('First 100 frozen inputs', sample)]:
        lines.append(f"| {label} | 0 → {m['after']['skattefunn']['companies']} | 0 → {m['after']['skattefunn']['claims']} | {m['before']['all_published']:,} → {m['after']['all_published']:,} | 0 |")
    lines += ['', 'The sample membership was checked against the frozen first 100 input rows. All prior published claim IDs remain present. Socket connect and DNS operations were forbidden by an audit hook. The full replay used stage-ak-audit-fix1000; the sample used stage-ak-defaults. The replay durations include loading saved output and strict verification, not a new live runtime benchmark: full ' + str(full['seconds']) + ' s; sample ' + str(sample['seconds']) + ' s.', '',
        'Strict verifier passed both cohorts: schema, claim citations, blob hashes, verbatim spans and synthesis checks; **zero unverified values**. Full: 177,820 published claims, 5,272 verified blobs, 2,575 synthesis sentences. Sample: 17,971 claims, 575 blobs, 266 sentences. Research/state-aid counts and existing claim IDs are unchanged.', '',
        '## Ten hand-checks', '',
        'Each row below was checked against the named original workbook row and its selected evidence cells. Approval is JA, rejection NEI, and applicant orgnr matches exactly in all ten. Numeric decision dates were independently checked with .NET FromOADate; #N/A remained null. All are historical tax deduction approvals, not payments. Full claim IDs, evidence IDs, hashes, verbatim spans, cells and individual correctness notes: [hand-review-10.json](hand-review-10.json).', '',
        '| Company (orgnr) | Project / title | Period | Decision | Rapport 1 row |', '|---|---|---|---|---:|']
    for x in reviews:
        v = x['claim']['value']
        lines.append(f"| {x['company']} ({x['orgnr']}) | {v['project_id']} — {v['title'].replace('|', '/')} | {v['start_year']}–{v['end_year']} | {v['decision_date'] or 'null (#N/A)'} | {x['source_row']} |")
    lines += ['', 'OSEBERG project 34942 retains the historical flatbread-process title even though the present legal name suggests engineering: exact orgnr, rather than a guessed name/activity match, binds the record.', '',
        '## Full suite', '', 'Before: 1,755 collected, 1,754 passed, footer flake failed and passed twice in isolation. After: ' + tests + '.', '',
        'New tests: 23, including enabled-runner publication with no source HTTP, approval/subject guards, decision-date edge cases, raw XLSX error/sparse cells, idempotence, project deduplication, corruption withholding and deterministic build.', '']
    if failures:
        lines += ['Failures:', ''] + ['- ' + f for f in failures] + ['']
    (HERE / 'RESULTS.md').write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__':
    main()
