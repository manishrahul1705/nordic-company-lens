# First combined live run ? 20 November 2026

**Resumed and resolved:** the two JSONL review files and narrow ignore exceptions were committed as `95b4f6f`. Both new-review scripts now reproduce from a fresh local clone with no `bench/runs`; see [resumed clone check](clone-check-resumed.json). README and SUBMISSION now report this combined live measurement. The initial stop below is retained as history.

Runtime commit: `f2c7091fd831347ac36306d00ad4699c0c8235d9`, branch audit-fixes. No push. Frozen cohort `bench/inputs/1000-r3/batch.jsonl`, SHA-256 `7ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782` (the authoritative exact hash is in measurement.json). Fresh state, default concurrency (64 workers / 10 host concurrency), default sources, site ON, no supplied bulk, no prior state, no credential variables. Exact command and timestamps are in measurement.json.

`run_status=completed`; exit 0; 1,000 envelopes. **1,309.681 seconds wall**, **11,477 HTTP** (60.405% of 19,000); per-company maximum 40. **0 deadline hits, 0 handled exceptions, 0 unhandled exceptions, no run warnings**. Supported facts = available non-null distinct (company, field, value, reporting period) claims excluding section placeholders: **167,200**. This is not an official competition score.

| Stage | Seconds |
|---|---:|
| Collection / crawl | 814.530 |
| Finalisation / outputs | 140.020 |
| Offline site | 341.330 |
| Other command overhead (wall minus these stages) | 13.801 |
| Total process wall | 1,309.681 |
| Strict verifier, separately timed | 126.840 |

Compared with the previous 1,744-second reference, wall time is 434.319 seconds lower. Live provider conditions vary; this is not a controlled causal estimate. TED was healthy: all 89 TED requests returned HTTP 200, 79 notice nominations, breaker never opened. Linear 1,100-company projection: **1,440.649 seconds and 12,624.7 requests**, 60.405% of the 20,900 pool; projection is conditional on these provider/workload conditions, not a guarantee.

| Family | Companies | Claims |
|---|---:|---:|
| websites | 115 | 115 |
| social | 63 | 129 |
| brands | 19 | 19 |
| gleif | 142 | 736 |
| ted | 6 | 20 |
| hiring | 3 | 3 |
| group_structure | 75 | 119 |
| signatur | 765 | 765 |
| prokura | 201 | 201 |

GLEIF claims include identifiers and associated registry facts; TED count means published winner awards. Hiring remains three ads, each using a registered subunit employer number. Group claims are explicitly stated parent/subsidiary relations, not the group flag. Per-platform social counts and complete diagnostics are in summary.json.

| Wikidata property | Companies with published support | Claims |
|---|---:|---:|
| P1448 | 1 | 1 |
| P571 | 7 | 7 |
| P159 | 13 | 13 |
| P452 | 12 | 12 |
| P1128 | 6 | 6 |
| P2139 | 0 | 0 |
| P856 | 8 | 8 |
| P2002 | 1 | 1 |
| P2003 | 2 | 2 |
| P2013 | 3 | 3 |
| P4264 | 0 | 0 |

Wikidata consumed five HTTP requests. Counts are published claims with exact-row/revision support, including corroborating evidence on existing claims, not all returned values. Registry precedence and disagreement recording remain intact.

Strict integrity verifier: **PASS**, 1,000 envelopes, 167,200 claims, 5,183 source blobs, 2,575 supported synthesis sentences, zero unverified values, 126.84 seconds. Same command semantics as previous stages: without `--require-clean`, which additionally requires complete optional-source health; no verifier rules changed. See strict-verifier.txt and verifier-timing.json.

Full suite: **1,656 passed, one warning, 488.42 seconds** (wrapper wall 490.745). The warning is PytestCacheWarning: permission denied writing `.pytest_cache/v/cache/nodeids`; tests exited zero. No retry or workaround was applied. See pytest.txt.

## New Stage X review

The unchanged committed Stage X extract/reproduce/attribution scripts were copied to accuracy/ with hashes in script-provenance.json. The previous review remains intact. New extract: all 1,000 envelopes, 177 sampled evidence blobs, zero missing blobs. Same seed 20261119, same 200-item sampling procedure and acceptance checks. **200 correct / 0 wrong / 0 doubtful; 147 mechanical and 53 contextual reviews; Wilson 95% lower bound 98.12%.** See accuracy/REVIEW.md, sample.jsonl, verdicts.jsonl and the preserved source extract. This sample is not a census of all new information types.

Attribution audit: 167,838 cited evidence records; **zero** dangling references, registry mismatch, cross-company URL/hash reuse or foreign labelled orgnr. The read-only reproduction and attribution checks both exit zero; logs and verification.json are retained. The separate historical brand_token_check.py hardcodes an older run and is not one of REPORT.md's two clone-reproduction commands; it was not represented as a clone-safe check here.

**Historical stop: initial clone reproduction failed (resolved on resume).** A fresh local clone of report commit `0594a69` had no `bench/runs`. The historical Stage X reproduce.py and attribution_audit.py both passed. The new sample reproduce.py exited 1 with FileNotFoundError for `accuracy/sample.jsonl`. The repository JSONL ignore rule omitted the new `sample.jsonl` and `verdicts.jsonl` from the report commit; they existed only in the original working directory. See clone-check.json for the complete traceback. The new attribution script was not run in the clone after this failure.

At that initial stop, the user's stop-on-failure instruction was followed: no file was force-added, no retry was attempted, and README/SUBMISSION updates were deferred. On explicit resume, narrow .gitignore exceptions included both files; both scripts then passed in a fresh clone without bench/runs. No other review file was missing (excluding generated __pycache__); both 200-row JSONL files and the manifest's extract hashes were checked. The resumed check reproduced 200 correct / 0 wrong / 0 doubtful and all-zero attribution findings across 167,200 claims / 167,838 evidence records. Historical failure details remain in clone-check.json and STOP.json. No runtime code, proof rule, verifier or test was changed on resume.

## Data terms

Original source terms remain applicable: registry NLOD 2.0 with credit to Br?nn?ysundregistrene, Wikidata CC0, NAV/TED terms, and original website rights for saved evidence. Our annotations do not relicense those bytes. See docs/SOURCES.md and bench/reports/DATA_LICENSING.md. The unresolved competition-archive index licence documented there remains unresolved; this run grants no new permission.
