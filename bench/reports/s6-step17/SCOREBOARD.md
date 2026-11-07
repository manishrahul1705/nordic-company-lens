# S6 Step 17 - cited analyst briefings

**KEEP: benchmark, precision, full-suite and fresh-clone gates PASS.** Started from `2512bdb2882b03c429690e62f01526bbf85e3c3c`; measured runtime `acaca26eb9f2962161122c53ed5eb0053b7dd52c`. Search OFF, application credentials stripped, no LLM, no new sources or HTTP request types. No push.

## Audit and implementation

The [pre-code audit](AUDIT.md) prints six original summaries (two rich, two medium, two registry-only) and the existing sentence types. The former primary summary concatenated detailed fact sections and included minor updates and baseline boilerplate.

The primary summary now has ordered, deterministic identity, size/trend, footprint, significant-event, online-presence and useful-gap sentences. Missing facts are skipped. English industry names use the existing SSB table; short statutory purposes and article titles remain source-native quotations. Founding dates are labelled founded, not falsely labelled registered. All sentences cite supported claim IDs or explicitly identified run-metadata context for absence and exact input identity. Exact independent template recomputation rejects altered text, numbers, dates and citations.

Only company accounts are used for amounts; consolidated records remain separate. NOK and EUR amounts use the same rounding, with no conversion. Percentage comparisons additionally require the same currency, declared units and comparable full-year periods; zero prior revenue cannot produce a percentage. Three real EUR reporters omit the source scale: their figures explicitly retain that uncertainty and have no inferred percentage. The accounts gap is used only when no supported company-only account exists. Losses use neutral wording; employee counts say as registered.

Company articles take precedence over major registry announcements. Only explicit name/address/capital amount/role/status/merger fields qualify; employee-information dates, latest accounts years and capital-registration dates do not. Registry dates are labelled announcement dates and attributed to the Brønnøysund Register. No forecasts, advice or inferred business events.

**All 9,209 existing detailed synthesis sentences remain present and verified below the briefing as supporting detail. Zero were dropped.** The stored legacy three-part brief also retains its existing validation. Primary briefing text does not include baseline/refresh boilerplate or retrieval dates, so unchanged supported facts produce stable text.

## One frozen-1000 benchmark

Run `20261107T052914870839Z-acaca26`, same frozen cohort and registry bytes as Step 16. [Execution](benchmark-execution.json), [scoreboard](benchmark-scoreboard.json), [budgets](budget-metrics.json).

| Metric | Step 16 | Step 17 |
|---|---:|---:|
| Websites | 110 | 110 |
| Social companies | 44 | 44 |
| Activity companies | 999 | 999 |
| Jobs companies | 3 | 3 |
| Supported facts | 156,927 | 156,927 |
| HTTP total | 8,484 | 8,477 |
| Mean HTTP/input including shared | 8.484 | 8.477 |
| Maximum HTTP/company | 40 | 40 |
| Wall seconds | 860.443 | 586.006 |
| Deadlines | 0 | 0 |
| Detailed synthesis sentences | 9,209 | 9,209 |
| Primary briefing sentences | - | 4,922 |
| Mean primary sentences/company | - | 4.922 |

HTTP fell by seven requests; no transport or discovery code changed. Live timing variation is not claimed as a causal synthesis speedup. There were 1,000 envelopes and profiles, no warnings, zero synthesis rejections/fallbacks and no output truncation. Mean attributed requests: 8.437; shared requests: 40. C: had 16.259 GiB free immediately before the crawl, above 5 GiB. The first wrapper invocation stopped at uv's package-status stderr before starting any crawl; the single actual benchmark then completed normally.

Fact families are unchanged: identity 31,007; roles 17,806; subunits 6,907; accounts 97,416; website family 821; activity 2,967; hiring 3. [Exact summary/claim metrics](summary-metrics.json).

| Sentence type | Companies | Share |
|---|---:|---:|
| a Identity and activity | 1,000 | 100% |
| b Size and trend | 999 | 99.9% |
| c Footprint | 774 | 77.4% |
| d Company article or major registry event | 152 | 15.2% |
| e Online presence | 1,000 | 100% |
| f Useful gap | 997 | 99.7% |

129 summaries have six sentences, 665 have five, 205 have four, and one has three because the missing facts are not padded. Counts use cited sentence frames, not punctuation inside company names or quoted article titles.

## Review and tests

[Thirty reviewed briefings](REVIEW.md), [complete sentence/input/evidence ledger](review-sample.json), [six readable examples, two per group](EXAMPLES.md). Only six companies have website + company article + revenue; all six were reviewed, supplemented by four seeded random selections from the 30 most fact-rich other verified sites. Ten medium and ten registry-only companies were sampled without replacement. Seed 20261107; no sample was replaced. **Zero unsupported statements, zero wrong numbers or dates.**

[Five supplementary cases](supplemental-review.json) check two additional major registry events and all three EUR reporters against their source values, dates and declared/undeclared units. No new source requests were made for review.

Final committed-runtime suite: **1,217 passed in 294.92 seconds**. [Full suite](committed-full-tests.txt), [EUR and focused tests](eur-tests.txt). Earlier failures were old primary-summary display expectations; assertions now check the new briefing while retaining exact industry/source checks in supporting detail. Rich/medium/sparse, loss, missing prior year, minor-only updates, company/consolidated scope, currency, banned wording, citation forgery and stable output are covered.

Independent frozen-1000 verification passed: **1,000 schema-valid lines, 156,927 supported claims, 4,083 verified source blobs, 4,922 cited primary sentences, zero unverified values**. All 9,209 detailed sentences are additionally checked by the verifier. [Unmodified verifier result](verification.txt).

## Fresh-clone pair and commits

The literal README command ran twice in a fresh clone of the measured runtime on the release 100 + 3 cohort and the same state directory: 211.640 seconds / 756 HTTP, then 206.547 seconds / 746 HTTP. Each wrote 103 envelopes and profiles. **Zero company changes, zero observation changes; unmodified strict verifier exit 0. All 103 primary briefing texts are identical across refresh.** There were 8,034 supported claims, 318 verified blobs, 416 cited primary sentences and zero unverified values. [Exact command and result](official-run/RESULTS.md).

Runtime source `acaca26eb9f2962161122c53ed5eb0053b7dd52c`; subsequent changes are report/review tooling and evidence only. All commits authored as Manish Rahul <manishrahul1705@gmail.com>. No push. The final evidence commit hash is reported in the response.
