# Stage D: careers allowance and completeness

**KEEP.** Precision, ownership, employer, expiry and scoring rules unchanged. Full suite: **1,391 passed, zero failed in 422.04 seconds**. The initial suite found three old 18-per-input expectations; these were updated to the authorized 19-per-input ceiling. Existing precision fixtures/expectations were not changed or skipped.

## Budget and ordering

The global hard ceiling is now 19 requests per distinct normalized input (1,900/100; 19,000/1,000). Explicit lower limits still apply. The attributed per-company ceiling stays 40. All time caps, finalization reserves, robots, TLS and host spacing remain unchanged. Robots requests, redirects and retries call the same Budget.reserve as ordinary HTTP.

After primary proof succeeds, up to six unused per-company HTTP slots are earmarked for careers. Optional activity cannot spend these slots. No global requests are spent by earmarking. Careers is deferred until primary company tasks, bounded website retries, registry activity and official extra sources finish, and consumes only the remaining pool. This prevents careers from displacing primary proof. It cannot bypass a 40-request ceiling already consumed by proof or an expired global deadline; such failures remain honest.

Apex/www **already cost one nomination**, not two: candidate generation deduplicates by registrable domain; candidate() tries host/transport variants inside that nomination. Each actual HTTP attempt is still charged, including robots and redirects. Regression tests cover deduplication, earmarking, activity isolation, the immutable hard cap and tenant-scoped HR Manager boards.

The existing careers walk follows links from verified accepted pages and supported tenant-scoped ATS boards. HR Manager's hr-manager.net is now included alongside the existing Teamtailor, Webcruiter, Recman and Jobbnorge hosts. Individual-posting acceptance, own publication/expiry dates, employer identity/verified company-to-board chain, staffing exclusion and NAV deduplication are unchanged. AST comparisons of active_job, job_date, staffing, board_scope and within_board are recorded in precision-rules-unchanged.json. No proof or scoring file changed.

## Frozen 1,000 benchmark

README command, fresh state, no bulk argument, default time limits, stripped credential environment, no search/LLM/paid API. Input SHA-256: 7ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782. The live run used the Stage D working-tree patch on b1d7868; execution.json names the base HEAD, while runtime.patch and runtime-source.json preserve the tested changes. The comparison is the requested release run (r3-release-final, 113/47/2), not the earlier R3 baseline.

| Metric | Release | Stage D | Difference |
|---|---:|---:|---:|
| Envelopes | 1000 | 1000 | +0 |
| Websites | 113 | 113 | +0 |
| Social companies | 47 | 47 | +0 |
| Jobs companies | 2 | 2 | +0 |
| Activity companies | 1000 | 1000 | +0 |
| Facts | 165424 | 165471 | +47 |
| HTTP total | 9281 | 9130 | -151 |
| HTTP mean including shared | 9.281 | 9.13 | -0.151 |
| HTTP max attributed | 40 | 40 | +0 |
| Wall seconds | 1650.17 | 930.541 | -719.629 |
| Seconds per 100 | 165.017 | 93.054 | -71.963 |
| Deadline hits | 0 | 0 | +0 |
| Site warnings | 0 | 0 | +0 |

The run exited 0 with 1,000 profiles as well. Total 9,130 <= 19,000 (913 per 100 amortized); every attributed company count <=40; zero deadline hits. These are pooled limits across the whole batch, not separate ceilings for arbitrary 100-company slices. Network/site timing varies between live runs; the timing improvement is measured, not attributed solely to this code change.

Website proof composition:

| proof_type | Companies |
|---|---:|
| orgnr_on_page | 38 |
| jsonld_vatid | 5 |
| registry_declared_name_tier_a | 25 |
| legal_name_without_suffix_and_two_contacts | 9 |
| legal_name_and_registry_contact | 24 |
| unique_no_corroborated | 7 |
| registry_declared_hard_contact_tier_b | 3 |
| registry_phone_on_site | 2 |

## Jobs funnel and the reported failures

Company-site funnel: **38 candidates -> 38 fetched -> 0 accepted -> 0 finally kept**. The two published jobs remain NAV jobs, with no new job URLs. Release fetched 31 of the same 38 nominations. Careers landing pages and unrelated articles are not jobs; no rule was relaxed to convert coverage into job claims.

| Company | Org | Release | Stage D |
|---|---|---|---|
| ASKØY24 AS | 923998012 | 0/2 fetched; website budget exhausted | 2/2 fetched, complete; no valid job |
| TENSIO AS | 922828172 | 0/2 fetched; website budget exhausted | 2/2 fetched, complete; no valid job |
| BRIDGE TECHNOLOGIES CO AS | 987002808 | 0/1 fetched; website budget exhausted | 1/1 fetched, complete; careers landing is not a job |

Careers errors: 3 -> **0**. Hiring section failed: 3 -> **0**, available stays2; remaining998 honestly not_available. Every counted candidate was fetched. Some nominations are news articles with job-related words; they yield no accepted job. Exact nominated URLs and diagnostics are in careers-comparison.json.

News-company coverage stays7; article claims69 ->62, with the same article acceptance rules and a smaller optional-activity allowance after the careers reserve. Facts rise47 overall; roles-source failures4 ->0 reflect the fresh live run. Accounts remains999 available/1 failed in both. No section's available-company count drops.

## Full gain review

No newly covered website company, no lost website company, and **no new job ad**. One URL alias changed:

| Org | Legal name | New URL | proof_type | Exact saved page text | Posting date | Verdict |
|---|---|---|---|---|---|---|
| 936629466 | CLOSVA AS | https://closva.com | jsonld_vatid | Owned by Closva AS · Org. no. 936 629 466 | Not applicable (website) | correct |

Prior URL https://www.closva.com; same registered domain and legal entity. Saved source https://closva.com/, retrieved2026-11-13T08:27:49.961364Z, SHA-256486947f3d09b2300f1968c47f08e4c9d675802e231e09829ffe2bdc6e4941f0c. Ownership text was checked in the retained body and its hash verified. Reviews:1correct/0wrong/0doubtful; new job reviews0 because none exist. No narrowing or rerun is needed. See new-items.json and review-verdicts.json for exact evidence records.

## Delivery

Commit as Manish Rahul and merge normally into the existing main worktree bench/cache/stage-a-main on top of046599d4 (which retains5e16dc4 in its parent chain). Preserve all history. No push. Raw state/output remains ignored in bench/runs/stage-d-live; only small reports/scripts and the implementation are committed.
