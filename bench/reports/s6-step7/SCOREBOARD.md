# S6 Step 7 scoreboard

Source baseline: Step 6 kept implementation at `fbc7747`; trial: `1fe27a07b80fb048fe70567d960d39957ec335b0`. All benchmark comparisons used the frozen 1000-company input and registry. Search was disabled, and credentials were stripped from benchmark subprocesses. Trial fails the existing keep gate; its runtime changes are rolled back.

| Section | Step 6 baseline | Step 7 trial | A/B noise band | Gate |
|---|---:|---:|---:|---|
| Identity | 1000 | 1000 | 0 | pass |
| People | 997 | 997 | 0 | pass |
| Locations | 774 | 774 | 0 | pass |
| Financials | 999 | 999 | 0 | pass |
| Website | 83 | 79 | 2 | **fail** |
| Social | 39 | 33 | 4 | **fail** |
| Jobs | 3 | 3 | 0 | pass |
| News/activity | 231 | 231 | 1 | pass |
| Wrong-company findings | 0 | 0 | — | pass |

Website fell by 4, exceeding noise band 2; social fell by 6, exceeding noise band 4. Therefore Step 7 is **ROLLBACK** regardless of the zero-wrong review. The group rule suppressed group-source material, including correctly identified group sites; the observed net drops exceed the permitted noise band.

## Validation

- Fresh local clone, no application environment variables, `uv sync --frozen`, then the exact documented README command: exit 0, 100 input rows, 100 envelopes and 100 profiles. Run 1: 857 HTTP requests, 366.98 s. Run 2 on the same state directory: 869 requests, 235.86 s; 780 state blobs (up from 678); 100 outputs. All company-level change markers were unchanged; observation delta reported 18 in the aggregate refresh report. Identical-snapshot and changed-value previous/current semantics are also covered by focused tests.
- Input contract tests cover invalid checksum, absent registry record, blank/whitespace lines, and normalization. Focused trial compliance tests passed (31 tests in the focused suite; budget/fallback tests 30 passed). A full suite on the trial previously reported 915 passed. A later local full-suite attempt was interrupted after repeated integration errors under the restricted network environment; it did not complete and is not counted as a passing run.
- Simulated 100-company all-site-timeout run: exactly 1800 HTTP requests, max 18/company, mean 18, 100 envelopes. Advancing-clock simulation: 435 requests, max 18, mean 4.35, 100 envelopes before graceful time-cap termination. Full-feed fallback simulation: 420 requests under the test's tighter configured cap, 100 envelopes. Hard limits are 1800 requests and 2400 seconds per 100; no output was skipped.
- NAV snapshot built 2026-11-04 remains fresh through 2026-11-30 using the 30-day expiry; full-feed fallback was exercised within the caps. Three baseline jobs reviewed: each is an individual ACTIVE NAV detail URL and employer orgnr is a registered subunit.
- Current website ownership review: all 83 Step 6 websites reviewed against multi-org proof and cross-registry-domain signals; five group sites identified and group-derived social/news/jobs/descriptions withheld in the trial. All website verdicts are listed in `OWNERSHIP_REVIEW.md`. Differential review found 25 new items, 0 wrong, 0 unsure (`comparison/REVIEW.md`).

The 100-company `scripts/bench.ps1 -Size 100` run completed: 100 envelopes, 851 requests, 249.72 s; its small-sample website count is not compared to the 1000-company noise gate. Trial 1000 run: 7982 requests, max 18/company, 1077.81 s, zero deadlines. Score counts: 1000/997/774/999/79/33/3/231.

Commits: baseline `fbc7747`; rejected trial `1fe27a0`; rollback and evidence commits are recorded in the final response. Nothing pushed.
