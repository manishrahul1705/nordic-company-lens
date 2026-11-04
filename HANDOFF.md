# Handoff — S6 hard-stop wrap-up, 4 November 2026

This handoff is delivered in repository HEAD. Implementation checkpoint after the requested revert: `5a4301307f84a3d551bd818abbbd5a4c2d3fe93d`. It reverts trial `2b97438` and restores the kept Step 3a code. The following documentation-only wrap-up commit contains this file; obtain its exact HEAD with `git rev-parse HEAD` (also reported in chat). Nothing pushed.

| S6 step | Status | Evidence / remaining limitation |
|---|---|---|
| F17 diagnostic correction | KEEP | Retained successful non-robots company body required; no missing-body fetched/no-proof claim. |
| 1 Fresh NAV index | KEEP | Public token, validated complete index; 8554 ads; built 4 Nov; 21-day expiry 25 Nov. Fresh-index hiring-incomplete 73 → 0. |
| 2 Fallback robustness | KEEP | Detail capacity follows remaining time/request capacity; explicit page-cap reporting; incomplete remains honest. Forced-stale 1000: 346.998 s wall, NAV 272.438 s / 663 requests, 69 name-unusable incomplete (not falsely complete). |
| 3a Contact/imprint proof | KEEP | Bounded own contact section inside CMS article, extra proof pages, exact street normalization; complete source review, zero wrong-company, no section drop. |
| 3b Legal suffix absent | reverted / not completed (model capacity interruption) | Unbenchmarked `2b97438` reverted in `5a43013`; no KEEP or coverage claim. |
| 4 TLS/connect recovery | not started | Includes unresolved NSNL plaintext-HTTP publication. |
| S7 Company-site jobs | not started | No S7 implementation or trial. |

## Last measured scoreboards

These are the kept Step 3a benchmarks, not new runs at the revert or wrap-up commit. The revert restores their implementation. Both used search OFF and public NAV credentials only via the benchmark wrapper.

| Metric | 100 companies | 1000 companies |
|---|---:|---:|
| Identity available | 100 | 1000 |
| People available | 100 | 997 |
| Locations available | 85 | 774 |
| Financials available | 100 | 999 |
| Website available | 11 | 75 |
| Social available | 5 | 34 |
| Jobs available | 1 | 3 |
| News/activity available | 29 | 231 |
| Envelopes / exit | 100 / 0 | 1000 / 0 |
| Wall seconds | 56.959 | 273.237 |
| HTTP requests | 751 | 7108 |
| Website budget-exhausted companies | 6 | 65 |
| Hiring incomplete | 0 | 0 |
| NAV mode | declared_index | declared_index |
| NAV seconds / requests | 4.187 / 4 | 28.750 / 7 |
| Deadline hits | 0 | 0 |

Runs: `bench/runs/20261104T081142666432Z-1abf474` and `bench/runs/20261104T081322420645Z-1abf474`. Durable scoreboards and all opened-source reviews: `bench/reports/s6-evidence/3a-100/` and `3a-1000/`. The 1000 review opened all 54 social claims and five changed website proofs: zero wrong-company. Website budget errors increased from 21 to 65 after Step 3a; this cost is unresolved. The lone scale financials failure previously traced to BRREG HTTP 500 for org 926077422 remains unrelated and unfixed.

## Exact next steps

1. Re-run Step 3b as a separate trial/commit: registered name without legal-form suffix, name-derived registrable domain, at least TWO independent registered contact categories (phone, email, street address, postcode+city), no conflicting owner organisation number. Name-only or name plus one contact remains ambiguous. `2b97438` is a reference for the reverted implementation, not an approved result. Full tests, benchmark 100 then 1000, inspect every new website/social/news/job, and log KEEP only with no section available-count drop and zero wrong-company; otherwise revert and log.
2. Step 4: classify TLS/connect causes without equating every ConnectError with a certificate mismatch. Try www/apex with TLS verification on. Permit a single HTTP request only to discover a redirect to valid HTTPS; never publish evidence from plaintext HTTP. **Open issue: NSNL, org 952785052, was published as `http://www.nsnl.no` by the existing fallback in the kept Step 3a run. Attribution passed, transport does not satisfy the TLS requirement. Fix and regression-test this explicitly.** Preserve robots, budgets, ownership/conflict and scope checks. Same 100/1000 gates and complete review.
3. S7: jobs only from verified company careers pages, JSON-LD JobPosting and publicly accessible ATS pages linked from the verified site. Require individual dated, unexpired ads for this exact company; exclude landing pages, open applications/åpen søknad, NAV search links and parent/sister-company jobs. Deduplicate against NAV. Separate tested, benchmarked and reviewed commits under the same gate.
4. S8 synthesis: state what changed and what remains unknown; do not infer availability/completeness or facts absent from verified evidence.
5. S9 offline site UX: assess generated offline pages and usability while preserving output contracts and evidence access.
6. Linux 1000-company run using `.github/workflows/benchmark.yml` (manual workflow, size 1000, uploads bench/runs). No workflow dispatched during wrap-up; publishing/dispatch must respect the continuing no-push instruction and future explicit authorization.
7. Review README, commands, output descriptions, licences, costs and limitations against final code and measured results. Submission deadline: **7 November 2026, 23:59 IST**.

## Commands

Run from `C:\Users\Manish\Downloads\Signalpost-Clean`:

```powershell
uv run pytest -q
.\scripts\bench.ps1 -Size 100
.\scripts\bench.ps1 -Size 1000
```

Linux equivalent:

```bash
bash scripts/bench.sh --size 1000
```

Forced-stale diagnostic (saved original October index; do not re-date it):

```powershell
uv run --frozen python scripts/bench_run.py --size 1000 --nav-index-path bench/cache/s6-nav-build-20261104/stale-original.json.gz
```

The stale artifact is ignored/local; if unavailable, prepare a reproducible stale fixture without altering the production bundle. The normal wrappers use fresh state and evaluator flags with default budgets. Do not use `-Search`.

## Rules and evidence

- Search stays OFF. Benchmark runner strips NAV credentials and paid-search/API keys to match public-token official runs. Never print, log, copy or commit tokens/keys.
- Every change: its own commit, full pytest, 100 and 1000 benchmarks as required, full review of every newly published website/social/news/job. KEEP only with no section available-count drop and **0 wrong-company**; otherwise revert and log. External-root-cause errors must be fixed separately before reapplying a trial.
- Keep TLS verification, robots/politeness, deadline/budget honesty, exact-company ownership and all evaluator flags. Do not claim fallback completeness for unread feed pages or unresolved header names.
- Production runs and reports stay under ignored `bench/runs/` and cache under `bench/cache/`; durable reports are tracked under `bench/reports/`. No audit/scratch folder committed.
- Author and committer: Manish Rahul <manishrahul1705@gmail.com>. **Do not push.**
- Durable copies: `bench/reports/S4_REPORT.md`, `S5_REPORT.md`, `S6_REPORT.md`, `suffix-screen.json`, `proof-sample.json`, and `handoff-next.md`. The copied scratch handoff and historical progress notes are archival; this handoff's final status supersedes their pending-work statements.

Final hard-stop validation after reverting Step 3b: `uv run pytest -q` ? **823 passed in 192.93s**, exit 0. No new benchmark was run during wrap-up. Production code, scripts and tests match the kept Step 3a checkpoint (`4d80529`).
