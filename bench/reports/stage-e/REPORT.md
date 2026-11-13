# Stage E final submission verification

**KEEP: all requested gates PASS.** Runtime commit c654406bb5cea9b4ca2f369bd308e62c26dcc10e. Careers earmark state, activity-cap deduction, claiming calls and its dedicated test are removed. Activity's company_cap expression is exactly the pre-Stage-D expression. The pooled19/input ceiling,40/company hard cap, HR Manager support, post-primary careers ordering and all precision/ownership/employer/expiry/scoring rules remain unchanged. Incomplete careers coverage is still reported under the original error codes.

## Frozen 1,000: release comparison

Literal README settings, fresh state, no bulk override, credentials stripped, no search/LLM/paid API. Input SHA-2567ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782. Exit0,1,000 envelopes/1,000 profiles, offline site generated. Baseline is r3-release-final (113/47/2,69articles). Exact command and timing: execution.json; raw output remains ignored at bench/runs/stage-e-live.

| Metric | Release | Stage E | Difference |
|---|---:|---:|---:|
| Websites | 113 | 113 | +0 |
| Social companies | 47 | 47 | +0 |
| Jobs companies | 2 | 2 | +0 |
| Activity companies | 1000 | 1000 | +0 |
| News companies | 7 | 7 | +0 |
| Article claims | 69 | 69 | +0 |
| GLEIF companies | 32 | 32 | +0 |
| TED award companies | 5 | 0 | -5 |
| Facts | 165424 | 165484 | +60 |
| HTTP total | 9281 | 9173 | -108 |
| HTTP mean including shared | 9.281 | 9.173 | -0.108 |
| HTTP max attributed | 40 | 40 | +0 |
| Wall seconds | 1650.17 | 2286.951 | +636.781 |
| Seconds per100 | 165.017 | 228.695 | +63.678 |
| Deadline hits | 0 | 0 | +0 |
| Careers errors | 3 | 6 | +3 |

No warnings/site warnings. Total9,173<=19,000; attributed maximum40. Time includes live source and host delays, notably slow finalization/site generation; there is no causal claim that removing earmarks changed runtime. TED74notices were nominated, but73notice requests returnedHTTP202, twoTED requests timed out;0verified awards published. Raw TED request diagnostics in ted-requests.json. No source acceptance was loosened to preserve old award counts.

| Website proof_type | Companies |
|---|---:|
| orgnr_on_page | 38 |
| jsonld_vatid | 5 |
| registry_declared_name_tier_a | 25 |
| legal_name_without_suffix_and_two_contacts | 9 |
| legal_name_and_registry_contact | 24 |
| unique_no_corroborated | 7 |
| registry_declared_hard_contact_tier_b | 3 |
| registry_phone_on_site | 2 |

## Full website/social gain/loss review

Every gained/lost published URL was compared against release. New company websites0; lost company websites0; gained social profiles0; lost social profiles0. One website alias is replaced:

| Org | Legal name | Gained URL | Lost URL | proof_type | Exact page text | Verdict |
|---|---|---|---|---|---|---|
| 936629466 | CLOSVA AS | https://closva.com | https://www.closva.com | jsonld_vatid | Owned by Closva AS · Org. no. 936 629 466 | correct |

Same registrable domain and exact legal entity. Saved company footer and SHA-256 verified by review extraction; exact spans, URLs, retrieval dates and hashes in new-items.json/review-verdicts.json. lost-items.json records the removed alias and replacement. Review totals1correct/0wrong/0doubtful, no rule narrowing required. This is the full incremental review, not a claim of a new exhaustive audit of every retained fact.

## Careers honesty

Four company_careers_website_budget_exhausted and two company_careers_website_timeout remain visible; careers is not complete. No error renamed/suppressed and no cap bypass. Company-site job candidates/fetch/accept/keep totals are in careers-metrics.json; the two retained jobs remain NAV jobs. Activities keep the original allowance;69article claims recovered from Stage D's62.

## Fresh clone refresh pair

New local clone bench/cache/stage-e-clone, uv sync --frozen, the committed runtimec654406. Frozen100+3 cohort bench/reports/release/orgnrs.txt, initially empty state, literal README command twice against that same state. Credentials stripped. The strict verifier file is unmodified. No retry needed; first pair passes.

| Metric | Run1 | Run2 |
|---|---:|---:|
| Exit | 0 | 0 |
| Envelopes | 103 | 103 |
| HTTP | 713 | 702 |
| Wall seconds | 234.5300647999975 | 223.61068479999085 |
| Company changes | 0 | 0 |
| Observation changes | 0 | 0 |
| Deadline hits | 0 | 0 |

Strict verifier **PASS**, exit0:103lines,8,454published claims,316source blobs verified,103syntheses/242sentences,0unverified synthesis values, identical claim IDs,0company changes/0observations. Original logs/records retained in refresh/.

## Evaluator command variants and tests

All four mocked evaluator commands on bench/inputs/20 pass using real CLI/runner/writers: minimal organisations/output; README; README plus three unknown flags; README without site-dir. Each emits20envelopes/20profiles, nonempty report, index and comparison site. Unknown arguments warn and are recorded. Final targeted rerun5passed16.23s (four cases plus effective settings). Full suite **1,390passed,0failed412.64s**; one earmark-only test removed with the removed implementation. No precision fixture weakened. Existing hard-cap and time tests retained. pytest.txt and evaluator-variants.txt preserve results.

## Documentation and delivery

README.md and SUBMISSION.md now contain measured precision, revision3 changes,19/input and40/company caps, honest careers/TED limitations, Common Crawl13November2026 build/crawls43+39+34/terms/third-party-rights notice, and NAV2026-11-13T00:26:42.872674Z public-feed provenance. Candidate coverage is explicitly not verified-site coverage. No causal timing claim.

All gates in gates.json are true. Normal merge into the existing main clone bench/cache/stage-a-main on top ofcb51ff6; retain parent history including StageA5e16dc4. No push. Unrelated Common Crawl untracked scripts remain untouched and uncommitted.
