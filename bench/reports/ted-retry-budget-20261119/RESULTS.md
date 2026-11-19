# TED retry and runtime budget results

19 November 2026. Branch `audit-fixes`; changes are uncommitted and nothing was pushed.

The fresh-state frozen 1,000-company command completed in **1,744.427 seconds**, versus **2,285 seconds** in the retained slow baseline: **540.573 seconds / 23.66% faster**. All 1,000 envelopes and the offline site were emitted. The current run consumed 48.46% of the new local default, or 72.68% of the old 2,400-second target.

## Historical retry audit, completed before implementation

Across the accessible saved JSON request logs, **zero notices succeeded on a second or third XML attempt**. Six report copies contained TED XML attempts, representing **three distinct request logs** after deduplication. They contain 155 notice observations; 79 notices were retried, with 158 second/third attempts and no recovery. Older summary-only artifacts cannot establish per-attempt outcomes. This is a statement about retained evidence, not a claim that a TED retry can never succeed.

The scan covered saved artifacts in the related Downloads checkouts and Temp/claude snapshots, including 7,347 additional JSON files outside the usual report/metrics/summary names. Paths, copy groups and counts are in [historical-audit.json](historical-audit.json).

## Implementation

- Three notice downloads run concurrently in bounded batches. Each host has a lock around request admission, preserving the existing one-second start spacing. Network I/O and backoff sleeps overlap. Request caps and the shared deadline still apply to every actual attempt.
- **N = 3** consecutive notices exhausting all three attempts with HTTP 202 open the circuit. The rest of the run's notice XML downloads are skipped, with `ted_202_circuit_open` recorded in failure metrics and affected companies' `run.refresh.official_extra.TED_reason`. The source remains `not_available_fetch_failed`, so skipping is never presented as proof of no awards. Responses are applied in stable notice order; at most three notice downloads are in flight.
- Site admission now estimates **0.40 seconds/company**, or **400 seconds at 1,000** and **440 seconds at 1,100**. Calibration includes the measured 273.5/1,000 and 414.41/1,100 builds, rounding above the higher 0.377 seconds/company observation. The new build actually took **362.25 seconds**, below its 400-second estimate. This is an admission estimate, not a hard site execution timeout.
- After the TED implementation, the Config and CLI default was raised to **3,600 seconds**, with comments identifying it as our own safeguard: the competition brief specifies no numeric limit. This does not establish Builderr's actual external timeout. Existing per-input hard ceilings and lower configured limits remain effective.
- **`--no-site`** skips the site, even alongside `--site-dir`. Site generation remains **ON by default**.

## Frozen run timing

| Stage | Slow baseline (s) | Updated run (s) |
|---|---:|---:|
| Collection, including shared sources | 1,821.28 | 1,170.42 |
| Finalization and mandatory output preparation | 174.88 | 198.95 |
| Site generation | 273.50 | 362.25 |
| Startup, report writes and remaining overhead | 15.34 | 12.807 |
| **Whole command** | **2,285.00** | **1,744.427** |

The verifier is a separate command and is excluded from both whole-command times. The report's `runtime_ms` is not the whole-command wall time.

Live TED XML processing took **13.860 seconds**, down from the baseline's **975.422-second XML span**: approximately **961.562 seconds less**. Ten search requests returned HTTP 200, and nine XML attempts returned HTTP 202. Three notices exhausted retries; the breaker then skipped the remaining 76. **Zero TED awards were published**, also zero in the slow baseline.

The complete run saved less than the TED stage because other live work was slower. Non-TED collection increased approximately 310.70 seconds; finalization increased 24.07 seconds and site generation increased 88.75 seconds. Registry completion was 247.48 seconds versus 179.61, and NAV was 134.02 versus 67.19 (overlapping stages, not additive). Live source conditions differ, so the overall reduction is an observed before/after comparison, not a controlled code-only causal measurement.

A separate [controlled outage replay](outage-replay.json) reused the saved 79-notice HTTP statuses and durations with real retry/pacing sleeps. The XML stage took **14.156 seconds**, saving **961.266 seconds** relative to the saved span. It also made nine XML attempts and skipped 76 notices. The replay's discovery responses were synthetic; it is not a full pipeline benchmark.

## Completion, deadline and quality details

- `run_status=completed`; 1,000 envelopes; 1,000 companies successful; 8,953 HTTP requests; zero warnings and zero handled/unhandled exceptions.
- Site available: 1,000 companies, 4,754 pages, 785,646,476 bytes.
- **`deadline_hits=1`**, not zero. It belongs to TENSIO (`922828172`), section `activity`. The existing second website pass recovered its website but reached its **45-second local timeout** while checking an activity URL. The run retained a `deadline` error even though verified registry activity kept the activity section available. This occurred around 1,044 seconds; the global crawl deadline was 3,060 seconds, and collection ended at 1,170.42 seconds. **The global run deadline did not fire.** No counter or error was suppressed or changed by this patch. Details are retained in [measurement.json](measurement.json).
- Tradeoff: opening the breaker can skip later notices that would have become ready. Those notices remain explicitly unchecked; historical zero recovery is evidence for the chosen bound, not proof of no potential coverage cost.

## Validation and reproducibility

- Full suite: **1,533 passed in 466.61 seconds**; [final test output](pytest-final.txt). Reserve arithmetic expectations were updated for the measured site cost. The live 20-company CLI integration allowance was raised from 30 to 90 seconds so the larger honest site reserve fits; site generation was kept enabled.
- Added coverage for circuit opening, a successful notice resetting the consecutive-failure streak, concurrent per-host pacing, concurrent attempt caps, retained retry recovery, CLI defaults and site opt-out.
- `git diff --check` passed. Source hashes matched at the start and end of the frozen run.
- Input SHA-256: `7ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782`.
- Fresh state, no bulk file, default source settings, site ON, default 3,600-second budget. Worktree based on `2e70524`; exact diff saved in [source.patch](source.patch). The retained slow baseline is from `4af8591`; live sources and earlier intervening work may differ.
- Full generated artifacts: `bench/runs/ted-budget-network-20261119/`. [Small measurement summary](measurement.json); [benchmark runner](run_frozen.py); [replay runner](replay_ted_outage.py).
- An initial restricted-network attempt aborted after 21.757 seconds when the identity source was unreachable. It is preserved separately at `bench/runs/ted-budget-20261119/` and excluded from the successful benchmark. The successful run used normal network access.

Independent output verifier: **passed**, exit 0, in **99.666 seconds**, separately from the benchmark. It checked 1,000 envelopes, 165,952 published claims, 4,086 source blobs and 2,537 synthesis sentences, with zero unverified synthesis values. See [verifier output](verifier.txt) and [separate timing](verifier-timing.json). This validates membership/schema/evidence/synthesis integrity; `--require-clean` was not requested because source health includes the explicitly reported local deadline and other unavailable sources.
