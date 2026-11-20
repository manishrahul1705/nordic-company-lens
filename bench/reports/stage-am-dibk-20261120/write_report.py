"""Write the Stage AM result from retained measurements, not estimates."""
import json
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main():
    full = json.loads((HERE / 'full1000.json').read_text(encoding='utf-8'))
    sample = json.loads((HERE / 'sample100.json').read_text(encoding='utf-8'))
    reviews = json.loads((HERE / 'hand-review-10.json').read_text(encoding='utf-8'))
    confirmed = json.loads((HERE / 'final-selected1000.json').read_text(encoding='utf-8'))
    live = Path('bench/runs/stage-am-live1000')
    terminal = json.loads((live / 'report.json').read_text(encoding='utf-8'))
    assert terminal['site']['state'] == 'available', 'Wait for site completion'
    progress = json.loads((live / 'state/progress.json').read_text(encoding='utf-8'))
    full['end_to_end_wall_seconds'] = (datetime.fromtimestamp((live / 'report.json').stat().st_mtime).astimezone()
        - datetime.fromisoformat(progress['start_time'].replace('Z', '+00:00'))).total_seconds()
    full['site'] = terminal['site']
    (HERE / 'full1000.json').write_text(json.dumps(full, indent=2) + '\n', encoding='utf-8')
    summary = {'full1000': full, 'sample100': {k: v for k,v in sample.items() if k not in {'requests','diagnostics'}},
        'tests': {'before': 1778, 'after': 1806, 'passed': 1806, 'failed': 0, 'seconds': 480.69},
        'final_selected_confirmation': {k:v for k,v in confirmed.items() if k not in {'requests','diagnostics'}},
        'hand_checks': len(reviews), 'no_api_or_search_calls': True}
    (HERE / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n', encoding='utf-8')
    lines = ['# Stage AM — DiBK sentral godkjenning', '',
        '## Live access and terms', '',
        'Checked 2026-11-20. Only the enterprise page supplies runtime data; no API, search, certificate, asset or linked-page requests are made. The shared robots file is fetched once per run and charged to the pool. The audit additionally fetched the homepage and static documentation for terms review, never an API/search endpoint. [Access URLs, timestamps, SHA-256 and robots text](access.json).', '',
        'Robots returned HTTP 200 and explicitly keeps /enterprises/ crawlable. Wildcard disallows: /search, /api/, /municipalities, /counties, /countries, /approval_area_function_types and /approval_area_field_types. Exact enterprise URLs pass robots checks. The request method rejects other paths and never follows redirects.', '',
        'No enterprise-page factual-reuse prohibition was found in the register homepage/footer or published register documentation. DiBK encourages direct or regular lookups rather than permanent storage; this source rechecks live and retains dated audit evidence, not a bundled register snapshot. Static documentation at https://sgregister.dibk.no/apidocs/openapi.yaml states CC BY 4.0 for API data. This does not establish a blanket HTML-page licence, and we do not call that API. Factual claims credit Direktoratet for byggkvalitet, exact URL and retrieval date. Logos/approval marks are not copied; an observation is not a permanently valid approval assurance. See [SOURCES](../../../docs/SOURCES.md).', '',
        '## Gate and implementation', '',
        'Available, non-carried-forward own-registry NACE codes select divisions 41/42/43 and groups 71.1/71.2; no name/activity inference. The saved cohort selects 120/1,000 and 10/sample100. The CLI is default-on with --no-dibk available. Low-level Config remains opt-in like other network-source fixture defaults. Effective configuration records the choice.', '',
        'Each selected company is scheduled immediately after identity verification, in parallel with its remaining crawl. Two host slots and the existing website politeness interval (at least one second, including completion-based spacing) are used. One enterprise attempt, no retries. Pooled 19/input and hard 40/company ceilings are unchanged; normal budget.reserve is used, including the shared robots request. The body is bounded to 2 MiB, and requests respect their timeout and crawl deadline. The final join is bounded to 60 seconds or the remaining crawl deadline; cancellation is diagnostic, not no approval.', '',
        'central_approval.* claims (certification family) require the labelled page orgnr to equal the company exactly. A single actual table row binds function, area and class. Period strings are preserved as DD.MM.YYYY, with explicit date_format. Approved requires the page\'s positive heading and an explicit period covering the retrieval day. Expired requires both an explicit expired heading and elapsed period; uncertain status/dates withhold. Explanatory/duplicate responsive rows are not approvals. 404/not-found is diagnostic only. Each claim has six bounded verbatim evidence spans: identity, period, current/expired statement, function, area, class; all share the original page SHA-256 and URL.', '',
        '## Measurements', '',
        '| Measurement | Sample100 | Frozen 1,000 |', '|---|---:|---:|',
        f"| NACE-selected | {sample['selected']} | {full['selected']} |",
        f"| Companies queried | {sample['enterprise_HTTP']} | {full['companies_queried']} |",
        f"| Companies with approval claims | {sample['companies_with_approvals']} | {full['companies_with_approvals']} |",
        f"| Approval-area claims | {sample['approval_claims']} | {full['approval_claims']} |",
        f"| Added enterprise HTTP | {sample['enterprise_HTTP']} | {full['enterprise_HTTP']} |",
        f"| Shared robots HTTP | {sample['robots_HTTP']} | {full['robots_HTTP']} |",
        f"| Total added HTTP | {sample['HTTP_added']} | {full['HTTP_added']} |", '',
        f"Sample measurement: saved sample replay plus live DiBK requests under the normal budget and safe transport; isolated fetch stage {sample['isolated_fetch_seconds']:.3f} s. It is not a fresh all-source sample crawl. Its strict verifier passed 100 envelopes, {sample['strict_verifier']['published_claims']:,} claims and zero unverified synthesis values. Eight 404s yielded no approval/no-approval claim.", '',
        f"Full measurement: fresh all-source 1,000 run, standard CLI, default workers and time budget, fresh state and site ON. run_status={full['run_status']}; crawl/finalisation runtime {full['crawl_runtime_seconds']:.3f} s; end-to-end wall (pipeline progress start to final report write, including site) {full['end_to_end_wall_seconds']:.3f} s. Total HTTP {full['total_run_HTTP']:,}/{full['pooled_cap']:,}; maximum per input company {full['max_HTTP_per_company']}. Deadline hits {full['deadline_hits']}; handled/unhandled exceptions {full['handled_exceptions']}/{full['unhandled_exceptions']}.", '',
        f"DiBK's first request began at {full['source_first_request_seconds']:.3f} s and its last response completed at {full['source_last_response_seconds']:.3f} s from the run start. The actual unhidden final join wait was **{full['source_tail_wait_seconds']:.6f} s**, below 60 s. Fetch elapsed time is overlapped, not serially added to crawl time. This measures scheduler tail contribution; it is not a causal paired disabled/enabled end-to-end benchmark. Network variability in other sources means the difference from an older whole-run duration cannot all be attributed to DiBK. The deadline/tail guard is additionally covered by regression tests.", '',
        'Full enterprise HTTP statuses: ' + json.dumps(full['HTTP_status_counts']) + '. Approval statuses: ' + json.dumps(full['status_counts']) + '. Diagnostics: ' + json.dumps(full['diagnostics']) + '.', '',
        f"Final timeout-guarded source confirmation: another live DiBK-only replay of the saved full cohort selected {confirmed['selected']} companies, queried {confirmed['enterprise_HTTP']}, published {confirmed['approval_claims']} areas for {confirmed['companies_with_approvals']} companies and used {confirmed['HTTP_added']} HTTP requests. Its isolated source stage took {confirmed['isolated_fetch_seconds']:.3f} s; strict verifier passed with zero unverified values. The all-source live process began before the final timeout-only boundary guards were added; the final confirmation and final 1,806-test suite exercise those guards. A standalone isolated batch waits within the normal crawl deadline; the 60-second cap applies to the production pipeline's final join after parallel crawling, not to the entire source batch duration.", '',
        '### Kilde overlap', '',
        'Both named companies are in sample100 and the full cohort, and both pass the NACE gate. No competitor code was copied.', '',
        '| Company | Orgnr | Sample areas | Full areas |', '|---|---|---:|---:|',
        f"| HAUGESUND ELEKTRISKE FORRETNING AS | 912492575 | 2 | {full['known_Kilde_overlap']['912492575']} |",
        f"| UPPSTAD VVS AVDELING HOVDEN AS | 926698435 | 6 | {full['known_Kilde_overlap']['926698435']} |", '',
        '## Ten hand-checks', '',
        'Each approval below was checked against its exact enterprise page and all six cited source spans. Exact orgnr, explicit status, explicit validity period and the same-row function/area/class support every value. [Full claim IDs, evidence IDs, SHA-256, retrieval times and verbatim spans](hand-review-10.json).', '',
        '| Company / orgnr | Function | Area | Class | Validity as stated | Status |', '|---|---|---|---:|---|---|']
    for x in reviews:
        v = x['claim']['value']
        lines.append(f"| {x['company']} / {x['orgnr']} | {v['function']} | {v['area']} | {v['class']} | {v['valid_from']}–{v['valid_to']} | {v['status']} |")
    lines += ['', '## Verification', '',
        f"Strict verifier passed the full 1,000: {full['strict_verifier']['published_claims']:,} published claims, {full['strict_verifier']['source_blobs_verified']:,} source blobs, **zero unverified synthesis values**. The sample passed separately. Max per-company requests remains <=40; no caps, validator, verifier, acceptance rules or existing tests were loosened.", '',
        'Full final suite: **1,806 passed, zero failures**, 480.69 s (baseline 1,778; +28 source tests). Both evaluator network tests and the footer test passed. [Final output](pytest.txt). An earlier full run before the last four boundary tests also passed all 1,802 tests. Source-specific cases cover exact orgnr, NACE, approved/expired/unclear states, malformed periods, responsive duplicates, robots, budget, 404, pacing, redirect veto and bounded asynchronous completion.', '',
        'No bench/runs, raw page downloads or pytest temporary directories are committed. Reports retain measurements and ten bounded evidence reviews only.', '']
    assert full['source_tail_wait_seconds'] <= 60
    (HERE / 'RESULTS.md').write_text('\n'.join(lines), encoding='utf-8')


if __name__ == '__main__': main()
