# S6 Step 18 - briefing polish and registry-announcement depth

**KEEP: precision, budget, final full-suite and fresh-clone gates pass. One website loss is a documented HTTP 502 transient within the established noise band; the export regression is fixed and independently rebuilt offline.** Started from `84e1b2d668ce0dc1f9ededcbd707795be766bcac`. Search OFF, application credentials stripped, no new sources, no LLM, no push.

## Pre-code audit and decision

The initial retained-evidence scan established at least **534 additional supported announcement claims**, exceeding the requested 300 threshold, so B proceeded. A complete request-log cross-check subsequently added two otherwise unreferenced pages containing 810 subunit update records, but no additional claims under the old parser. **All 15 saved feed bodies were SHA-256 checked**. Exact corrected totals: 7,985 returned event records; 2,904 published announcement claims representing 1,945 distinct records; 3,438 old-parser eligible claims before the ten-claim cap; 86 companies at the cap, 80 actually losing eligible claims. [Audit and correction](AUDIT.md), [all URLs/hashes and counts](audit.json).

Zero out-of-window records are observable because the old API request filtered at 24 months. The number lost in months 25-36 is **unknown**, not zero; no unsupported historical count is invented.

## Kept changes

Briefings use rose/fell trends and omit percentages rounding to zero, separate registered-employee sentences, comma thousands separators, million formatting from one million, natural-language lists, concise workplace wording and Norwegian-purpose quotation labels. NOK/EUR rounding, declared-unit comparability, loss wording, citation scope and stable IDs are unchanged. No conversion or unsupported numerical inference. A separate employee sentence can take a complete briefing to seven cited sentence frames.

The same official shared BRREG endpoints now request **36 months**, with a **50-announcement-claim safety cap per company**, exact orgnr or retained exact-parent subunit evidence and the existing two-feed-requests-per-input ceiling. All pages are consumed inside the pooled budget. Publication timestamps remain explicitly distinct from effective dates. Existing supported field-change claim IDs are unchanged. Multiple field claims can describe one raw record; claims and distinct records are reported separately.

An update lacking supported field detail says only "Registry update recorded". A record explicitly typed Ukjent says "Registry event recorded (type unspecified)". Exact-parent subunit updates get the corresponding workplace label. Registration/deletion records retain their explicit event type and publication timestamp. These are source-record facts, not inferred business events. **Major-only briefing selection is unchanged**, and generic/unspecified records cannot qualify. Company-published articles remain separate.

## One frozen-1000 run

Measured collection/synthesis runtime `f02417bd`, run `20261107T055939048854Z-f02417b`. Final runtime `45c9494fb603f511fe0a89a2b4b02dea76e4cc40` adds only the export repair described below; it cannot change HTTP, claims or briefing text from the measured run. [Execution](benchmark-execution.json), [raw scoreboard](benchmark-scoreboard.json), [metrics](metrics.json).

| Metric | Step 17 | Step 18 |
|---|---:|---:|
| Registry-announcement claims | 2,904 | 12,017 |
| Company-news claims | 63 | 63 |
| All activity claims | 2,967 | 12,080 |
| Activity companies | 999 | 1,000 |
| Websites | 110 | 109 |
| Social companies | 44 | 44 |
| Jobs companies | 3 | 3 |
| Supported facts | 156,927 | 166,032 |
| HTTP total | 8,477 | 8,467 |
| Mean HTTP/input, shared included | 8.477 | 8.467 |
| Maximum HTTP/company | 40 | 40 |
| Feed HTTP requests | 15 | 16 |
| Wall seconds | 586.006 | 603.319 |
| Deadlines | 0 | 0 |
| Primary cited sentences | 4,922 | 5,048 |

HTTP fell by ten overall; the feed added one request. Sixteen feed requests / 1,000 inputs = **0.016 per input**, below two. The +2% overall ceiling was 8,646 requests. C: had **13.824 GiB free** before the single crawl. There were 1,000 envelopes and profiles, no deadline or output truncation. **All 2,904 old announcement IDs remain**; 9,113 new claims represent 8,827 previously unpublished event records. Counts include generic and explicitly unspecified registry records, not 9,113 newly established business developments.

### Recorded website loss

**KONSEPTBYGG EIENDOM AS / 970979026**, previously verified at `konseptbygg.no`, is now not_available: all HTTPS/HTTP and www/apex **robots.txt requests returned HTTP 502**. No homepage/proof bypass was attempted. Website/social discovery and proof code are unchanged; this company was not touched by the polish or event rules. The one-company loss is within the established two-website noise band and traces to a recorded transient failure. No extra crawl or fabricated restoration was used. [All diagnostics](website-loss.json), [four exact HTTP statuses](website-loss-http.json).

The website family has 813 facts versus 821; other non-activity families are unchanged. Detailed supporting synthesis is 9,208 versus 9,209 because this live failure removes a freshly supported website description. **Zero synthesis sentences were rejected or pruned by the new wording.** Original Step 17 evidence remains retained; a baseline run without a prior snapshot cannot pretend a failed check succeeded.

### Offline export failure and repair

The measured run recorded `site generation failed: ValueError`: Tensio's expanded activity page reached 272,229 bytes, exceeding the existing 250 KB guard. The original scoreboard/warning is preserved. The repair reuses the existing offline supporting-detail mechanism for registry announcements after the first ten; **all announcements, claim anchors, source metadata and evidence remain available**. The 250 KB limit is unchanged.

Rebuilding the exact saved 1,000 envelopes offline succeeded: **1,002 HTML pages**, largest profile **240,599 bytes**. No envelopes, profiles, claims or source bytes were rewritten and no new crawl was run. [Original diagnosis](site-size-diagnosis.json), [successful saved-output rebuild](site-rebuild.json). The measured 603.319 seconds includes the original failed size check; no fabricated corrected end-to-end 1000 timing is claimed. Final-runtime end-to-end export is also exercised by the fresh-clone pair.

## Review, examples and verification

[Twenty distinct new event records and ten random polished briefings](REVIEW.md): **zero wrong-company items, zero unsupported statements, zero wrong numbers or dates**. Seed 20261108; no sampled item replaced. Raw offset timestamps were checked as publication instants against canonical UTC; no effective-date inference. Subunit records were checked against their retained current exact-parent registry records. [Raw feed rows and source evidence](event-review.json), [briefings and cited input facts](briefing-review.json).

[Six new readable example briefings](EXAMPLES.md): Tensio, Feie- og Tilsynstjenester, Reneffekt, Jaki.i, NRP Anaxo Nordic M2 and Gulbis Holding. Every sentence carries its citation IDs.

Independent frozen-1000 verification passed: **1,000 schema-valid lines; 166,032 supported facts; 4,084 source blobs; 5,048 cited primary sentences; zero unverified values**. Detailed synthesis and its retained three-part brief are also checked. [Unmodified verifier](verification.txt).

Tests cover the inclusive 36-month boundary and future rejection, fifty-claim cap/newest ordering/evidence retention, UTC-offset equivalence, stable IDs, explicit versus unspecified record labels, exact-parent subunit scope, zero/rising/falling trends, EUR, employee splitting, list/quote/number wording and all fifty offline source links. The pinned collector runtime passed **1,220 tests in 293.81 seconds**. The final runtime, including the fifty-item offline-export regression, passed **1,221 tests in 283.34 seconds**. [Final full suite](final-full-tests.txt), [export-focused tests](site-final-tests.txt). No guard was weakened.

## Final fresh-clone pair

Fresh clone of final runtime `45c9494fb603f511fe0a89a2b4b02dea76e4cc40`, literal README command twice on the release 100 + 3 cohort, same state directory and no --previous. First: 204.703 seconds / 757 HTTP; refresh: 199.219 seconds / 741 HTTP. Each emitted 103 envelopes and profiles; both site exports passed without warnings or deadlines. **Zero company changes, zero observation changes, unmodified strict verifier exit 0. All 103 primary briefing texts are identical.** The pair verified 8,462 supported claims, 318 source blobs and 418 cited primary sentences with zero unverified values. [Exact command and results](official-run/RESULTS.md).

All commits authored as Manish Rahul <manishrahul1705@gmail.com>. Nothing pushed. The final full evidence commit hash is reported in the response.
