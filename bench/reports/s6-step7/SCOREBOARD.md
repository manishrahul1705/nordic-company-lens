# S6 Step 7 split decision

Baseline is the Step 6 kept implementation at `fbc7747`. Benchmark trial is `1fe27a07b80fb048fe70567d960d39957ec335b0`, using the same frozen 1000-company batch and registry. Search was OFF; benchmark child-process credential variables were stripped.

| Section | Step 6 baseline | Step 7 trial | Difference | Step 7 decision |
|---|---:|---:|---:|---|
| Identity | 1000 | 1000 | 0 | keep |
| People | 997 | 997 | 0 | keep |
| Locations | 774 | 774 | 0 | keep |
| Financials | 999 | 999 | 0 | keep |
| Website | 83 | 79 | -4 | keep group guard; 6 lost URL items reviewed |
| Social | 39 | 33 | -6 | keep group guard; 6 claims reviewed |
| Jobs | 3 | 3 | 0 | keep |
| News/activity | 231 | 231 | 0 | keep |
| Wrong-company findings among differential items | — | 0 | — | pass |

Per the revised precision gate, the group-site guard is **KEEP**: collateral=0, correctly withheld=2, transient=12. All 14 absent URL-level items are documented individually in `LOST_ITEMS.md` with the corresponding timeout/DNS or group evidence. The Step 6→7 count changes include unrelated transients and correctly withheld group claims, so count deltas alone are not used to reject the guard.

Compliance changes A are **KEEP**: input edge cases, blank-line preservation, 30-day NAV index age, timeout/global-cap simulations, clean clone and same-state refresh, and ACTIVE detail-only NAV jobs all pass focused tests. The global hard caps are 18 requests/input and 2400 seconds per 100; simulation emitted 100 outputs for 100 timeouts and used 1800 requests (max/mean 18). The full-feed fallback simulation emitted 100 outputs under its tighter 420-request test cap. No disk cleanup was needed; disk capacity was not the failure cause.

## Test results and exact initial failures

- Final full suite: **915 passed in 277.76s** with public-source integration access and a writable dedicated workspace temp/cache directory.
- Final focused Step 7 suite after splitting A/B tests: **30 passed in 13.36s**.
- Initial fail-fast attempt: 71 passed, then pytest setup errored with `PermissionError: [WinError 5]` scanning the user's `%TEMP%\pytest-of-Manish` directory. Cause was the restricted temp-directory ACL.
- Next sandboxed full attempt: 913 passed, 2 failed. Both were `tests/test_evaluator_cli_and_site.py` smoke tests; BRREG returned `network_error` for roles, subunits, accounts and activity across the 20-company fixture, making sections `failed` and causing `scripts/verify_output.py` to reject incomplete smoke sections. They passed with public-source access and a newly created writable temp directory (2 passed in 22.04s).
- During final test-file split, focused test collection first failed because `tests.test_registry` does not export `OUR`/`OTHER`; corrected imports to `tests.test_websites`, then all 30 focused tests passed.

Clean clone: `uv sync --frozen` and the documented README command succeeded without app env variables, emitting exactly 100 envelopes and profiles. Re-run on the same state directory emitted 100 again, reused state blobs (678→780), reported 100 unchanged companies and zero company changes; aggregate observations reported 18 changed observations. The separate identical-snapshot test reports zero company and observation changes and verifies actual old/current values after a changed role.

Trial 1000 run: 7982 HTTP requests, max 18/company, 1077.81 seconds, zero deadlines. The 100-company `scripts/bench.ps1 -Size 100` trial completed with 100 envelopes, 851 HTTP requests and 249.72 seconds. NAV snapshot built 2026-11-04 remains fresh through 2026-11-30 at the 30-day default; full-feed fallback stays under the global cap.

All 83 current websites were reviewed for exact-company ownership and group signals; review matrix is `OWNERSHIP_REVIEW.md`. Three published jobs were reviewed individually in `baseline-jobs.json`; each is a direct ACTIVE NAV detail ad with an employer orgnr matching a registered subunit. Differential review of 25 new claims found 0 wrong and 0 unsure (`comparison/REVIEW.md`).

Commits: source baseline `fbc7747`; original measured trial `1fe27a0`; superseded initial all-or-nothing revert `c80e95e`; original evidence `0b7c3a4`; compliance A `e56f493`; group guard B `1c3521e`; final lost-item evidence commit follows in Git history. Nothing pushed.
