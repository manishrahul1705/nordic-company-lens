# S6 Step 16 ? fact depth from existing responses

**KEEP: benchmark, precision and final fresh-clone gates pass.** Started from `286089bf34a4b265e4349bd4f32052664bd24ca5`. Search OFF, application credentials stripped, no push. No new sources, HTTP request types or discovery rules.

## Audit before coding

[Every unpublished path, company count and example value](AUDIT.md); [full machine ledger](audit.json). The audit verified **3,996 saved source bodies by SHA-256**. It found **64 unpublished non-transport paths across 1,000 companies**, including **17 paths each present for at least 300 companies**. The stop threshold was therefore met. Another 19 transport/scope paths are listed separately and do not count toward it. Null/empty values are excluded; false and zero remain real values. A field with only one available example is not given an invented second value.

Fields already present inside structured claim values count as published. Most requested identity, role, subunit and company-financial fields were already covered. Missing numeric paths affecting 19 companies were consolidated records. Currency and period had been reporting metadata rather than standalone claims. The audit distinguishes frozen CSV identity rows from already-cited exact-org JSON responses.

## Single frozen-1,000 measurement

Run: `20261107T000025367438Z-42f3cbf`. Measured source: `42f3cbfea39f353fc67b8d0fbdc8f601c85cb2fd`. Baseline: the requested Step 15 run `20261106T183808924157Z-1db7047`, with identical frozen batch and registry bytes. Counts below are available/published claims, excluding absence markers.

| Claim family | Step 15 | Step 16 | Increase |
|---|---:|---:|---:|
| Identity | 28,716 | 31,007 | 2,291 |
| Roles | 11,803 | 17,806 | 6,003 |
| Subunits | 6,527 | 6,907 | 380 |
| Accounts | 62,584 | 97,416 | 34,832 |
| All families | 113,419 | 156,927 | 43,508 |

**43,506 additions are fact-depth claims.** Two more are Tensio article URLs reached by the existing crawler in live responses; they are not a new extraction rule or source. Their titles and article-side publication dates were separately reviewed. [Measured counts](metrics.json).

| Section / budget | Step 15 | Step 16 |
|---|---:|---:|
| Identity companies | 1,000 | 1,000 |
| People companies | 997 | 997 |
| Subunit workplace companies | 774 | 774 |
| Financial companies | 999 | 999 |
| Verified websites | 110 | 110 |
| Social companies | 44 | 44 |
| Jobs companies | 3 | 3 |
| Activity companies | 999 | 999 |
| HTTP total | 8,666 | 8,484 |
| Mean HTTP/input, including shared | 8.666 | 8.484 |
| Mean attributed HTTP/company | 8.626 | 8.443 |
| Shared HTTP | 40 | 41 |
| Max HTTP/company | 40 | 40 |
| Wall seconds | 1,002.110 | 860.443 |
| Deadlines | 0 | 0 |

HTTP fell **2.10%**; the allowed +2% ceiling was 8,839 requests. All 110 prior websites remain present. No warnings or output truncation. The sole financial failure remains **NRP ANAXO NORDIC M2 / 926077422**, whose BRREG response was HTTP 500; no financial values were invented. [Execution](benchmark-execution.json), [raw scoreboard](benchmark-scoreboard.json). C: had **19.188 GiB free** immediately before the run, above the required 5 GiB. [Disk check](pre-benchmark-disk.json).

The requested historical baseline predates the final Step 15 candidate-state corrections, which are already in this task?s starting commit. Those changes and live response variation prevent attributing the 182 fewer requests solely to fact depth. The depth extractors make no transport calls; existing fetch functions and HTTP/time caps remain unchanged. Offline re-extraction used zero HTTP and preserved **every legacy claim ID: zero lost or changed**. [Saved-source projection](saved-projection.json).

## Extraction policy and profiles

- Add only present source attributes, with exact locators/spans and English labels. Publish birth year rather than a full birth-date claim. Registered deceased flags and administrator details remain role-scoped. Former subunit names are not asserted as former parent-company names.
- An explicit source range produces ?Employee count not published (0?4 employees)?; no number is invented. A missing count, zero, or `harRegistrertAntallAnsatte=false` does not by itself prove that range. No explicit range occurred in this real batch; tests cover both explicit ranges and prohibited inference.
- Cover returned numeric financial fields, including extraordinary items, with one selected latest filing per year and account type. Keep company and consolidated records separate. **40 consolidated records** are exposed. Do not infer a new multiplier or ratio; group units remain undeclared where the source omits them.
- Publish per-year currency, period, account type, small-company, audit and reporting flags. Do not invert opt-out or unaudited flags into unsupported audited status. Missing new fields produce no supported claim; existing contract absence markers are retained.
- A rolling annual-response window does not withdraw older supported per-year facts. Retain their original values, IDs, dates and evidence, with a historical-retention note. Returned current-period values can still change normally.
- Preserve the existing `verified_claims` schema. Add a lossless `claims_by_section` index with labels, family and period; company/consolidated financial views stay separate. All **1,000 profiles** were checked against every available envelope claim. [Profile checks](profile-check.json).
- The projected envelope exceeded the former 256 MiB ceiling. Raise only the default output ceiling to **512 MiB**; actual output was **333,789,215 bytes**, with no truncation. HTTP caps remain a pooled 18 per input / 40 max per company; time caps are unchanged.

## Precision review and tests

[40 stratified random new claims](REVIEW.md), ten per family, seed 20261107, distinct companies within each family: **40 correct, zero wrong values, zero wrong periods**. No sample was replaced. [Complete values, excerpts, periods, URLs and SHA-256](review-sample.json). Two further consolidated amounts and both extra Tensio articles were inspected: all four correct. [Supplementary proof](supplemental-review.json).

Independent 1,000-output verifier: **156,927 supported claims, 4,083 source blobs, 9,209 cited sentences, zero unverified values**. [Verification](verification.txt).

Earlier tests identified superseded consolidated/birth-date exclusion expectations and false historical-period removals. These were corrected while preserving company/group separation and the existing refresh assertions. Source `42f3cbf`: **1,194 passed in 364.56 seconds**.

The first official pair exposed two false company-change events in one company: identical 3D SCANDINAVIA description values moved only from apex to `www`. They were not accepted as changing company information. [Initial pair and cause](official-run/initial-alias-failure/RESULTS.md).

The generic refresh-only fix, `352abc0f00ecdcb203cb3d13fe4e1dfe7da323fd`, retains prior description IDs only when full values/reporting inputs are identical on the same verified page through www/apex or standard-scheme aliases. It keeps current evidence. Different text, path, host or identity proof cannot be merged. Focused: **18 passed in 17.15 seconds**; saved diff replay: **zero changes and observations**, with original output untouched. Final full suite: **1,202 passed in 371.40 seconds**. [Final suite](final-full-tests.txt), [saved replay](alias-saved-pair-replay.json).

The fix is after the `previous=None` early return. It cannot affect the measured baseline-mode 1,000 outputs or HTTP count; no second 1,000 run was made.

## Final official check and commits

Fresh clone of final runtime source, literal README command twice on the release 100 + 3 cohort: [exact result](official-run/RESULTS.md). Company/observation counts and the unmodified strict-verifier exit are recorded there. Final local evidence commit/full hash is in the response. Commits use Manish Rahul <manishrahul1705@gmail.com>. No push.

Final literal pair: 103 envelopes/profiles each; 212.031 seconds / 758 HTTP, then 213.546 seconds / 740 HTTP. **Zero company changes, zero observation changes; strict verifier exit 0**, identical IDs, 8,034 supported claims and zero unverified values. No verifier relaxation or source-specific exception.
