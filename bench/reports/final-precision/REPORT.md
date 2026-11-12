# Briefing polish and final precision audit

## Final result

Final runtime: `35c43dd3f2c156f3e61fa5601191cdb3fafc1115`, branch `more-websites`. No push. Full suite: **1,297 passed in 311.14 s**. Both final fresh-clone runs exited 0 and emitted 103 envelopes and profiles: 100 valid companies plus three invalid input lines. Independent evidence verification passed for each run. Strict refresh verification **FAILS** on one diagnostic observation; this is not presented as a clean refresh pass.

| Metric | Final run 1 | Final run 2 |
|---|---:|---:|
| Wall seconds per 100 valid companies (+3 invalid) | 111.57 | 106.12 |
| HTTP requests | 904 | 900 |
| HTTP mean / max per valid company | 9.04 / 30 | 9.00 / 30 |
| Websites / social companies | 11 / 6 | 11 / 6 |
| Jobs companies / activity companies | 1 / 100 | 1 / 100 |
| Identity / roles / subunits / accounts available | 100 / 100 / 79 / 99 | 100 / 100 / 79 / 99 |
| GLEIF companies / procurement companies | 3 / 0 | 3 / 0 |
| Distinct facts | 16,810 | 16,810 |
| Company changes / observation changes | 0 / 0 | 0 / 1 |
| Deadlines / site warnings | 0 / 0 | 0 / 0 |

All 103 claim-ID sets and all 103 analyst briefings are identical across the final pair. The observation is org 897051982: a candidate is provisionally accepted before the final group/entity scope guard withholds it again. Its final website remains ambiguous in both runs; no website or company claim is newly published. See `final-code-v2/refresh-diagnosis.json` and the unmodified verifier failure. This diagnostic bookkeeping issue remains open.

## Briefing changes

The template cites an explicit GLEIF direct parent (otherwise ultimate parent) as ?It is owned by <parent> (GLEIF).? It does not derive ownership from names. Supplier/winner procurement awards enter the dated major-event selection alongside registry events and real articles; newest valid date wins deterministically. Buyer claims never become wins. No inferred amount is printed. Registry-only briefings combine supported size/workplace facts into 2?3 concise cited sentences rather than an absent-source checklist. GLEIF identity metadata alone does not make a profile verbose. Citation validation and stable regeneration remain mandatory.

Tests cover direct/ultimate parent, no inferred parent, award winner versus buyer, newest event, sparse profiles and stable regeneration. The random cohort contains no live parent relationship or procurement award, so those new sentences have fixture coverage, not a claim of live award/parent coverage.

## New frozen sample

Seed: **20261112**. Cached official Builderr universe: **411,160** records. Exclusions scan earlier `bench/inputs`, review/benchmark cohorts and release orgnr lists; source datasets and the current audit are excluded from that scan. There are 23,612 conservatively excluded identifier strings and 408,738 eligible valid universe rows. The sorted eligible pool is sampled without replacement. The manifest retains hashes of 796 scanned artifacts. No selected company overlaps the scanned prior cohorts.

Input: `orgnrs.txt`, 100 valid orgnrs plus `NOT-AN-ORGNR`, checksum-invalid `123456789`, and a whitespace-only line. SHA-256: `1819f0d0d68dc6bc3d390511c7d0444ab4d05825f07284369f88e53107b69d8d`. See `selection.json` for exact exclusions and universe hash.

A fresh local clone of the final runtime was installed with `uv sync --frozen`. Both README commands used that clone, identical input, and the same initially empty state. Credential environment variables were stripped without recording values. Exact commands, commits, wall times and exit codes are in `final-code-v2/release-execution.json`. Saved response blobs remain in the ignored clone state; checked source excerpts, hashes and values are retained in the committed ledgers.

## Manual precision review

| Category | Final reviewed items | Correct | Wrong | Doubtful |
|---|---:|---:|---:|---:|
| Every website | 11 | 11 | 0 | 0 |
| Every social profile | 12 (6 companies) | 12 | 0 | 0 |
| Every GLEIF claim | 15 (3 companies) | 15 | 0 | 0 |
| Every procurement award | 0 | 0 | 0 | 0 |
| Every job | 2 (1 company) | 2 | 0 | 0 |
| Random identity claims | 10 | 10 | 0 | 0 |
| Random role claims | 10 | 10 | 0 | 0 |
| Random subunit claims | 10 | 10 | 0 | 0 |
| Random accounts claims | 10 | 10 | 0 | 0 |
| Random registry announcements | 10 | 10 | 0 | 0 |
| Random briefings, sentence by sentence | 21 sentences / 10 briefings | 21 | 0 | 0 |

All special items across both final runs were reviewed, deduplicated by company/field/value. Official JSON locators and verbatim spans were checked against saved blobs and their hashes. Owned-page title, owner identifiers and registered contacts were compared for website/social attribution. Social destination pages were not fetched: the review establishes attribution from saved verified company sources. Each NAV job has the exact registered employer/subunit and valid active dates. GLEIF registeredAs matches the exact orgnr. Annual accounts scope, year, units and numeric values, role identifiers, subunit-parent relationships and registry publication dates were checked. Briefing rounding and comparable-year arithmetic were checked manually. See `final-code-v2/REVIEW.md` and its JSON ledgers for every verdict and proof basis.

## Findings corrected generically

| Initial finding | Verdict | Generic correction / final offline result |
|---|---|---|
| HAVNEGATA 25 AS ? advokatovesen.no | Wrong: adviser staff email did not prove the property company owns the law firm's site | Contact-only rules now require the full legal publisher name, including form, in title/headings/footer. Original saved page fails. Wrong website sentence disappears. |
| RANA IDRETTSKLINIKK AS ? spesialsport.no and Instagram | Doubtful: different current publisher, historical subunit/contact association insufficient | Same publisher corroboration requirement; original saved page fails. Both website and inherited social item withheld. |
| Kristiansund Facebook URL containing spaces | Doubtful/invalid URL | Reject whitespace in decoded profile paths, including percent-encoded whitespace. Legitimate matching accounts retained. |

No company-specific exceptions were added. Regression fixtures cover unrelated publisher phone/email, exact legal publisher positive and literal/encoded profile whitespace. Offline replay with actual default config confirms only the two unsupported original websites lose proof; the other 11 keep their existing proof. Existing phone/email-alone positive tests were intentionally changed to negative expectations to enforce the stricter rule; the phone-evidence localization fixture now includes the required legal publisher heading. Analyst tests now assert combined employee/workplace sentences with both citations. The procurement wording assertion follows the new winner sentence. Named wrong-company regression fixtures/expectations were not relaxed.

## Run history retained

| Runtime | Run 1 seconds / HTTP | Run 2 seconds / HTTP | Websites / social companies | Refresh |
|---|---|---|---|---|
| 0d525ba, initial template audit | 130.70 / 923 | 110.26 / 901 | 13 / 7 | 0 company changes, 3 observations; claim IDs differed |
| 43e058c, generic attribution corrections | 112.89 / 909 | 105.95 / 899 | 11 / 6 | 0 company changes, 1 observation; IDs/briefings stable |
| 35c43dd, final sparse refinement | 111.57 / 904 | 106.12 / 900 | 11 / 6 | 0 company changes, 1 observation; IDs/briefings stable |

Initial wrong/doubtful verdicts and all verifier failures remain retained. Final precision has zero retained wrong/doubtful reviewed items. The one accounts failed state and the one refresh diagnostic observation remain visible; no result was skipped or rewritten to produce a pass.

## Subsequent refresh bookkeeping correction

The historical failure above is preserved. A later final-state bookkeeping replay now passes the unchanged strict verifier with zero company and observation changes; no claims or guard decisions change. See [refresh bookkeeping report](../refresh-bookkeeping/REPORT.md).
