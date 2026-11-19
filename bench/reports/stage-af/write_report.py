"""Assemble the final report from completed measurement and review artifacts."""
import json
import math
from pathlib import Path
import re

out = Path(__file__).parent
m = json.loads((out/'measurement.json').read_text(encoding='utf-8'))
v = json.loads((out/'verifier-timing.json').read_text(encoding='utf-8'))
assert v['exit_code'] == 0
assert m['projected_1100']['wall_seconds'] <= 3000
reviews = json.loads((out/'reviewed.json').read_text(encoding='utf-8'))
assert all(len(rows) == 10 and all(r['verdict'] == 'correct' for r in rows) for rows in reviews.values())
test_log = (out/'pytest-after-af.txt').read_text(encoding='utf-8')
tests = re.findall(r'\d+ passed[^\n]*', test_log)[-1]
first = json.loads((out/'initial-measurement/measurement.json').read_text(encoding='utf-8'))
f = m['finalisation']
b = m['baseline_finalisation']
other = m['wall_seconds'] - sum(f[k] for k in ('crawl_seconds','outputs_seconds','site_seconds'))
old_other = 1744.427 - sum(b[k] for k in ('crawl_seconds','outputs_seconds','site_seconds'))
coverage = '\n'.join(f"| {kind} | {m['coverage'][kind]['companies']} | {m['coverage'][kind]['claims']} |" for kind in ('group_structure','signatur','prokura'))
endpoints = '\n'.join(f"| {kind} | {m['new_endpoint_companies_attempted'][kind]} | {m['new_endpoint_requests'][kind]} | `{json.dumps(m['new_endpoint_http_statuses'][kind])}` |" for kind in ('group_structure','signatur','prokura'))
request_projection = math.ceil(m['projected_1100']['requests'])
text = f'''# Stage AF: explicit BRREG relationships and signing rights

19 November 2026. Local branch `audit-fixes`; nothing pushed. NAV route investigation and its SUBMISSION reference were committed locally as `4b5a91e`. Stage AF follows the user's explicit authorization for additional BRREG requests, with group lookups gated on the company's existing registry group flag.

## Measured result and 1,100-company projection

The corrected fresh-state frozen 1,000 run completed in **{m['wall_seconds']:,.3f} seconds**, including the offline site, versus **1,744.427 seconds** previously. Observed difference: **{m['delta_wall_seconds']:+,.3f} seconds**. The source code hashes were unchanged during the run: **{m['source_unchanged_during_run']}**. All 1,000 terminal envelopes and company pages were emitted.

| Metric | Previous 1,000 | Stage AF 1,000 | Projected 1,100 |
|---|---:|---:|---:|
| Complete CLI wall seconds | 1,744.427 | {m['wall_seconds']:,.3f} | {m['projected_1100']['wall_seconds']:,.3f} |
| All HTTP attempts | 8,953 | {m['requests']:,} | approximately {request_projection:,} |
| Pooled ceiling | 19,000 | 19,000 | 20,900 |
| Pooled usage | 47.121% | {m['pooled_percent']:.3f}% | approximately {m['projected_1100']['pooled_percent']:.3f}% |
| Maximum attributed requests/company | 40 | {m['max_attributed_requests_per_company']} | cap remains 40 |

The projection multiplies measured whole-run time and requests by 1.1, assuming the same company/source mix and conditions; it is not a worst-case network guarantee. At the observed 7.5% group-membership rate, 1,100 implies about 83 group lookups plus 2,200 mandate lookups. The wall projection is below the user's **3,000-second stop threshold**, so the stop condition was not triggered. The 3,600-second default remains our own safeguard, not an evaluator-imposed numeric limit.

Using the slower first AF measurement instead gives **{first['wall_seconds']*1.1:,.3f} seconds at 1,100**. That more conservative observed-conditions projection also remains below 3,000 seconds. The site took 520.56 seconds in that first measurement versus {f['site_seconds']:,.2f} in the corrected measurement; the reserve remains calibrated to the slower observation rather than reduced to the fastest build.

The exact attributable source addition is **{sum(m['new_endpoint_requests'].values()):,} BRREG attempts**. The overall request/time difference also includes live-source variation and the TED re-probe, which the retained 1,744-second baseline predates; it is not an isolated causal timing experiment for AF. No acceptance rule was relaxed.

## Coverage and request gate

| New type | Companies with published claims | Published claims |
|---|---:|---:|
{coverage}

Group detail: **{m['group_edges']['parents']['companies']} companies / {m['group_edges']['parents']['claims']} parent claims**, and **{m['group_edges']['subsidiaries']['companies']} companies / {m['group_edges']['subsidiaries']['claims']} subsidiary claims**. These company counts overlap. Each signatur/prokura claim holds the complete registered basis, preserving joint conditions rather than creating independent grants for each person.

| Endpoint | Distinct companies attempted | Actual HTTP attempts | HTTP outcomes |
|---|---:|---:|---|
{endpoints}

Every group request was checked against a freshly extracted, available `identity.part_of_group=true` claim. No unflagged company was queried. Both mandate URLs were attempted for all 1,000 inputs, including deleted records; unavailable responses are recorded as lookup failures, not as proof that no rights exist. Success with no explicit registered basis remains distinct from fetch failure. Detailed state/reason counts are in [measurement.json](measurement.json).

All attempts use the existing BRREG host semaphore, retry policy, global deadline, pooled budget and per-company `Budget.reserve`. Mandatory registry additions run before optional website work can use the 40-request allowance. **{m['companies_at_cap']} companies reached 40**, none exceeded it. This can reduce optional website exploration for capped companies. Measured current existing-family coverage: `{json.dumps(m['existing_coverage_companies'])}` companies.

## Stage timing

| Stage | Previous 1,000 seconds | Stage AF 1,000 seconds |
|---|---:|---:|
| Pipeline collection | {b['crawl_seconds']:,.2f} | {f['crawl_seconds']:,.2f} |
| Mandatory finalization, synthesis, output validation/write | {b['outputs_seconds']:,.2f} | {f['outputs_seconds']:,.2f} |
| Offline site | {b['site_seconds']:,.2f} | {f['site_seconds']:,.2f} |
| Startup/shutdown and other overhead | {old_other:,.3f} | {other:,.3f} |
| Complete command | 1,744.427 | {m['wall_seconds']:,.3f} |
| Independent strict verifier, separately after the command | 213.811 | {v['seconds']:,.3f} |

Internal validation is included in mandatory finalization and was not timed separately. The independent strict verifier is a review step outside CLI wall time. Pipeline sources overlap; sums of new endpoint request durations in measurement.json are request-seconds, not additive wall time.

`deadline_hits={m['deadline_hits']}`; handled section/company exception records **{m['handled_exceptions']}**; unhandled exceptions **{m['unhandled_exceptions']}**; warnings `{json.dumps(m['warnings'])}`. Additional failure details, where any, remain in saved source states and [diagnostics.json](diagnostics.json). The counter's meaning is unchanged: companies with an error whose code is `deadline`. Ordinary HTTP timeouts are not automatically global deadline hits.

TED published **{m['ted_awards_published']} award claims across {m['ted_award_companies']} companies** in this run. Hiring remains **3 companies**, with the subunit attribution and route investigation documented separately in SUBMISSION.

## Proof and citation rules

- Group lookup: `/enhetsregisteret/api/konsernstruktur/{{orgnr}}`, only for entity-flagged group members. The response contains the whole group tree. The requested company must occur exactly once; only its explicitly reported parent or edges with `parentOrganisasjonsnummer` equal to the requested company are published. Group roots, siblings, workplace records and names do not establish a relationship by inference.
- Mandates: public `/fullmakt/enheter/{{orgnr}}/signatur` and `/prokura`. `enhet.organisasjonsnummer` must equal the requested company. Only `signeringsGrunnlag.signaturProkuraRoller` is published. Possible signing roles and interpreted/statutory combinations are excluded. Registered free text, role codes, names and joint/alternative conditions remain together. Birth dates and national identifiers are omitted from claim values.
- Each claim uses normal official-registry evidence: own-company request URL, retrieved time, SHA-256, retained body, JSON pointer, verbatim bounded excerpt, standard evidence/claim IDs. Failed refreshes retain prior supported facts as stale with their original evidence; they do not report a relationship removed because a lookup failed.

The independent AF audit checked **every new claim** against its retained body and pointer, verified explicit company identity/edges, and checked that mandate values omitted no registered wording or conditions. It verified **{m['new_claim_source_hashes_verified']} distinct new-claim source hashes**. [Thirty hand reviews](REVIEW.md) give company, full published value, cited URL/pointer/hash and case-specific reasons; [machine-readable reviews](reviewed.json). All final review values must match those actually inspected before notes are attached.

## Measurement-driven correction and validation

The first Stage AF measurement took **{first['wall_seconds']:,.3f} seconds**, with a **520.56-second site build** against a 400-second estimate. One native `TimeoutError` escaped the new source handler for BNE SKI VESTVEIEN SØR AS (`922723664`), interrupting its later website/hiring/activity work and creating three handled section errors. That output still passed integrity verification, but the failure scope was wrong. See [retained initial measurement](initial-measurement/measurement.json), [timeout trace](initial-measurement/timeout.json) and [initial strict verifier](initial-measurement/strict-verifier.txt).

The handler now records that native timeout only for the affected lookup and continues sibling sources/later company work. A regression test checks failed signatur plus successful prokura. Site admission is now **0.60 seconds/company**, calibrated from 520.56/1,000 with headroom: 600 seconds at 1,000 and 660 at 1,100. The corrected code was rerun with fresh state. The existing mandatory-finalization estimate remains separate from the site estimate; measured finalization is shown above rather than hidden in site time.

Full suite: **{tests}**. [Complete test log](pytest-after-af.txt). Focused extraction/integration/reserve/cap tests also passed (36 tests before the full suite). Strict verifier: **exit 0**, unmodified, checking membership, schema, hashes, verbatim evidence, and synthesis; [output](strict-verifier.txt), [command and timing](verifier-timing.json). As in the baseline, this is strict integrity verification without `--require-clean`, which additionally demands complete optional-source health. No verifier or acceptance rule was changed.

Reproduce with [run_frozen.py](run_frozen.py), then [analyse.py](analyse.py), [verify.py](verify.py), [write_review.py](write_review.py) and this report writer. Fresh artifacts: `bench/runs/stage-af-final-20261119/`; input SHA-256 `7ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782`. Default CLI sources and site ON; no bulk input, no personal credential, no new host, no model calls, and no push.
'''
(out/'RESULTS.md').write_text(text, encoding='utf-8')
print(out/'RESULTS.md')
