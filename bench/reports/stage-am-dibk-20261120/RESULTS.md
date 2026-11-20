# Stage AM — DiBK sentral godkjenning

## Live access and terms

Checked 2026-11-20. Only the enterprise page supplies runtime data; no API, search, certificate, asset or linked-page requests are made. The shared robots file is fetched once per run and charged to the pool. The audit additionally fetched the homepage and static documentation for terms review, never an API/search endpoint. [Access URLs, timestamps, SHA-256 and robots text](access.json).

Robots returned HTTP 200 and explicitly keeps /enterprises/ crawlable. Wildcard disallows: /search, /api/, /municipalities, /counties, /countries, /approval_area_function_types and /approval_area_field_types. Exact enterprise URLs pass robots checks. The request method rejects other paths and never follows redirects.

No enterprise-page factual-reuse prohibition was found in the register homepage/footer or published register documentation. DiBK encourages direct or regular lookups rather than permanent storage; this source rechecks live and retains dated audit evidence, not a bundled register snapshot. Static documentation at https://sgregister.dibk.no/apidocs/openapi.yaml states CC BY 4.0 for API data. This does not establish a blanket HTML-page licence, and we do not call that API. Factual claims credit Direktoratet for byggkvalitet, exact URL and retrieval date. Logos/approval marks are not copied; an observation is not a permanently valid approval assurance. See [SOURCES](../../../docs/SOURCES.md).

## Gate and implementation

Available, non-carried-forward own-registry NACE codes select divisions 41/42/43 and groups 71.1/71.2; no name/activity inference. The saved cohort selects 120/1,000 and 10/sample100. The CLI is default-on with --no-dibk available. Low-level Config remains opt-in like other network-source fixture defaults. Effective configuration records the choice.

Each selected company is scheduled immediately after identity verification, in parallel with its remaining crawl. Two host slots and the existing website politeness interval (at least one second, including completion-based spacing) are used. One enterprise attempt, no retries. Pooled 19/input and hard 40/company ceilings are unchanged; normal budget.reserve is used, including the shared robots request. The body is bounded to 2 MiB, and requests respect their timeout and crawl deadline. The final join is bounded to 60 seconds or the remaining crawl deadline; cancellation is diagnostic, not no approval.

central_approval.* claims (certification family) require the labelled page orgnr to equal the company exactly. A single actual table row binds function, area and class. Period strings are preserved as DD.MM.YYYY, with explicit date_format. Approved requires the page's positive heading and an explicit period covering the retrieval day. Expired requires both an explicit expired heading and elapsed period; uncertain status/dates withhold. Explanatory/duplicate responsive rows are not approvals. 404/not-found is diagnostic only. Each claim has six bounded verbatim evidence spans: identity, period, current/expired statement, function, area, class; all share the original page SHA-256 and URL.

## Measurements

| Measurement | Sample100 | Frozen 1,000 |
|---|---:|---:|
| NACE-selected | 10 | 120 |
| Companies queried | 10 | 120 |
| Companies with approval claims | 2 | 14 |
| Approval-area claims | 8 | 69 |
| Added enterprise HTTP | 10 | 120 |
| Shared robots HTTP | 1 | 1 |
| Total added HTTP | 11 | 121 |

Sample measurement: saved sample replay plus live DiBK requests under the normal budget and safe transport; isolated fetch stage 10.484 s. It is not a fresh all-source sample crawl. Its strict verifier passed 100 envelopes, 17,979 claims and zero unverified synthesis values. Eight 404s yielded no approval/no-approval claim.

Full measurement: fresh all-source 1,000 run, standard CLI, default workers and time budget, fresh state and site ON. run_status=completed; crawl/finalisation runtime 1045.578 s; end-to-end wall (pipeline progress start to final report write, including site) 1380.787 s. Total HTTP 11,455/19,000; maximum per input company 40. Deadline hits 0; handled/unhandled exceptions 0/0.

DiBK's first request began at 38.890 s and its last response completed at 173.500 s from the run start. The actual unhidden final join wait was **0.000000 s**, below 60 s. Fetch elapsed time is overlapped, not serially added to crawl time. This measures scheduler tail contribution; it is not a causal paired disabled/enabled end-to-end benchmark. Network variability in other sources means the difference from an older whole-run duration cannot all be attributed to DiBK. The deadline/tail guard is additionally covered by regression tests.

Full enterprise HTTP statuses: {"404": 106, "200": 14}. Approval statuses: {"approved": 69}. Diagnostics: {"not_found": 106, "available": 14}.

Final timeout-guarded source confirmation: another live DiBK-only replay of the saved full cohort selected 120 companies, queried 120, published 69 areas for 14 companies and used 121 HTTP requests. Its isolated source stage took 121.328 s; strict verifier passed with zero unverified values. The all-source live process began before the final timeout-only boundary guards were added; the final confirmation and final 1,806-test suite exercise those guards. A standalone isolated batch waits within the normal crawl deadline; the 60-second cap applies to the production pipeline's final join after parallel crawling, not to the entire source batch duration.

### Kilde overlap

Both named companies are in sample100 and the full cohort, and both pass the NACE gate. No competitor code was copied.

| Company | Orgnr | Sample areas | Full areas |
|---|---|---:|---:|
| HAUGESUND ELEKTRISKE FORRETNING AS | 912492575 | 2 | 2 |
| UPPSTAD VVS AVDELING HOVDEN AS | 926698435 | 6 | 6 |

## Ten hand-checks

Each approval below was checked against its exact enterprise page and all six cited source spans. Exact orgnr, explicit status, explicit validity period and the same-row function/area/class support every value. [Full claim IDs, evidence IDs, SHA-256, retrieval times and verbatim spans](hand-review-10.json).

| Company / orgnr | Function | Area | Class | Validity as stated | Status |
|---|---|---|---:|---|---|
| HAUGESUND ELEKTRISKE FORRETNING AS / 912492575 | Utførende | Installasjon av brannalarmanlegg | 1 | 22.09.2025–22.09.2028 | approved |
| UPPSTAD VVS AVDELING HOVDEN AS / 926698435 | Prosjekterende | Sanitærinstallasjoner | 1 | 07.05.2026–07.05.2029 | approved |
| FJELDE TEKNIKK AS / 931069373 | Utførende | Varme- og kuldeinstallasjoner | 1 | 11.09.2025–11.09.2028 | approved |
| CONPLAN AS / 987895276 | Ansvarlig søker | (for alle typer tiltak) | 3 | 19.06.2026–19.06.2029 | approved |
| TØMRER S. FAGERBEKK AS / 915279082 | Utførende | Tømrerarbeid og montering av trekonstruksjoner | 1 | 23.05.2025–23.05.2028 | approved |
| MURMESTER ANDREAS KAMMEN AS / 928647854 | Ansvarlig søker | (for alle typer tiltak) | 1 | 07.11.2025–07.11.2028 | approved |
| OPPHEIM GRAVEMASKINSTASJON AS / 974533537 | Utførende | Veg- og grunnarbeider | 1 | 17.06.2025–17.06.2028 | approved |
| CL BYGG & EIENDOM AS / 917283109 | Utførende | Tømrerarbeid og montering av trekonstruksjoner | 1 | 11.06.2024–11.06.2027 | approved |
| ESPACE AS / 926338730 | Ansvarlig søker | (for alle typer tiltak) | 2 | 09.01.2024–09.01.2027 | approved |
| LEFDAL INSTALLASJON AS / 968545337 | Prosjekterende | Brannalarmanlegg | 2 | 20.05.2025–20.05.2028 | approved |

## Verification

Strict verifier passed the full 1,000: 178,628 published claims, 5,961 source blobs, **zero unverified synthesis values**. The sample passed separately. Max per-company requests remains <=40; no caps, validator, verifier, acceptance rules or existing tests were loosened.

Full final suite: **1,806 passed, zero failures**, 480.69 s (baseline 1,778; +28 source tests). Both evaluator network tests and the footer test passed. [Final output](pytest.txt). An earlier full run before the last four boundary tests also passed all 1,802 tests. Source-specific cases cover exact orgnr, NACE, approved/expired/unclear states, malformed periods, responsive duplicates, robots, budget, 404, pacing, redirect veto and bounded asynchronous completion.

No bench/runs, raw page downloads or pytest temporary directories are committed. Reports retain measurements and ten bounded evidence reviews only.
