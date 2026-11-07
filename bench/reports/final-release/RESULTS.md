# Final release validation - 7 November 2026

**PASS: final frozen-1000 benchmark, independent verifier and exact local CI commands.** No runtime changes. Measured commit `39a7314299c181187ee1f07af7fa75eaa631ad9c`; one run `20261107T094159020873Z-39a7314`. Search OFF, application credentials stripped, no personal keys, no LLM, provider cost $0, no push.

## Runtime, disk and one frozen run

C: had **10.435 GiB free**, above 5 GiB, before starting. Locked installation passed. Executed `uv run --frozen python scripts/bench_run.py --size 1000` (the PowerShell wrapper's default benchmark command), with the frozen batch/registry and default 40-company request cap. No second 1000 crawl, source continuation or output repair was needed. The runtime, dependencies, tests and workflow files match the pinned commit; only release documents/evidence changed. The execution dirty flag reflects local evidence/scratch directories, not runtime edits. [Disk](pre-run-disk.json), [runtime integrity](runtime-integrity.json), [execution](benchmark-execution.json), [scoreboard](benchmark-scoreboard.json), [metrics](metrics.json).

| Metric | Final measured result |
|---|---:|
| Identity companies | 1,000 |
| People companies | 997 |
| Registered subunit/workplace companies | 774 |
| Financial companies | 999 |
| Verified websites | 108 |
| Social companies | 44 |
| Jobs companies | 3 |
| Activity companies | 1,000 |
| GLEIF companies | 32 |
| TED award companies | 6 |
| Supported facts | 166,207 |
| HTTP total | 8,589 |
| Mean HTTP/input, shared included | 8.589 |
| Mean attributed HTTP/company | 8.449 |
| Shared requests | 140 |
| Maximum HTTP/company | 40 |
| Wall seconds | 1,017.315 |
| Deadlines | 0 |
| Envelopes / profiles | 1,000 / 1,000 |

Configured pooled ceiling: 18,000 HTTP for 1,000 inputs, max 40 attributed/company, default 2,400-second time budget within the hard 24-seconds/input bound. Finalization/output-size limits were respected; no warnings or truncation. Site export passed: 1,002 pages, largest HTML profile 242,744 bytes, within the 250 KB guard. Benchmark and CI overlapped on the same machine, so wall time is a measured release result, not a controlled speed comparison.

Facts by family: identity 31,170; roles 17,806; subunits 6,907; accounts 97,416; website/social/contact/description 810; activity 12,095; hiring 3. GLEIF returned 32 exact-orgnr companies, including supported explicit parent relationships; TED accepted exact-party awards for 6. All 99 optional-source requests returned 200: 14 GLEIF requests, 10 TED API batches and 75 public XML fetches. Parent record lookup batches contained two deduplicated LEIs. [Source statuses](optional-source-statuses.json).

## Availability and limitations

This is coverage, not a promise that every source succeeded or an evaluator score. There is one financial failure, two website failures and four optional hiring failures; every company still has output. All failed-section codes/reasons are retained in [failed sections](failed-sections.json). Financial availability remains 999; no value was invented to fill the failed response.

Compared with the saved Step20 projection (110 websites), two sites are absent here:

- **ISTAD ART SOLUTION NORWAY NUF / 911691248**, pederistad.no: current candidate diagnostics show TierB role-holder proof, then the final entity-scope recheck withholds the link as ambiguous. The removed proof's orphan source body is not present in the final retained state, so its full page cannot be independently re-reviewed from this run; no specific new publisher or transient cause is invented. This is not presented as DNS noise. The earlier saved-evidence regression replay preserved all 110 sites under this runtime.
- **BERGEN VAKTMESTERTJENESTER AS / 990412375**, bnv.no: the current privacy page is rejected by the foreign-organisation-number ownership veto. Guessed alternatives have NXDOMAIN diagnostics. This is a recorded proof/veto outcome, not a claimed transient exemption.

[Exact recorded losses and candidate diagnostics](website-losses.json). No runtime fix, threshold relaxation, recrawl or fabricated restoration was made during this release prep. Final counts 108 are used in both README and submission notes.

## Independent verification

**PASS, exit 0:** 1,000 schema-valid lines; **166,207 supported claims, 4,105 checked source blobs, 5,052 cited primary sentences, zero unverified values**. Detailed synthesis and supporting citation frames are also verified. [Unmodified verifier log](verification.txt).

```sh
uv run --frozen python scripts/verify_output.py --first bench/runs/20261107T094159020873Z-39a7314/envelopes.jsonl --organisations bench/runs/20261107T094159020873Z-39a7314/inputs/batch.jsonl --count 1000 --state-dir bench/runs/20261107T094159020873Z-39a7314/state --report bench/runs/20261107T094159020873Z-39a7314/report.json
```

## Exact CI commands locally

Used a fresh local clone of the same runtime with clean state, application credential/search variables removed. Commands match .github/workflows/ci.yml:

```sh
uv sync --frozen
uv run pytest -q
uv run signalpost run --organisations tests/fixtures/ci20.jsonl --bulk tests/fixtures/ci20.csv --output out/ci20.jsonl --report out/ci20-report.json --expected-count 20 --time-budget-seconds 180
uv run python scripts/verify_output.py --first out/ci20.jsonl --organisations tests/fixtures/ci20.jsonl --count 20 --state-dir state --report out/ci20-report.json --require-clean --clean-sections identity roles accounts subunits
```

All four exited 0. Full suite: **1,244 passed in 386.97 seconds**. Live-20: 20 envelopes, 161 HTTP, 103.297 seconds, zero deadlines/warnings. Scoped verifier: 20 schema-valid lines, 3,663 supported claims, 83 source blobs, 99 cited primary sentences, zero unverified values; **failed_or_stale_sections=[]**. Registry cleanliness was not relaxed; only the workflow's existing optional-source allowance applies. No GitHub action was dispatched. [Exact commands/exits](ci-execution.json), [install](ci-command-1.txt), [full suite](ci-command-2.txt), [live20](ci-command-3.txt), [scoped verifier](ci-command-4.txt), [report](ci20-report.json).

## Documentation and precision sample

README and SUBMISSION now use this run's measured counts, budget caps and limitations. GLEIF is CC0; TED uses EU Publications Office/Commission reuse terms. Doffin is NOT used because supported keyless access/reuse terms were not verified. The w2.brreg.no Kunngjøringer HTML service is NOT used because robots disallows /kunngjoring/; the NLOD Enhetsregisteret updates API remains separate.

The Step 22 NEW random 100+3 precision check is explicitly historical to this release prep, not claimed as another sample selected today. Its fixed-runtime pair passed with zero company changes/observations and strict exit 0. Reviews and generic fixes remain in [Step 22](../s6-step22/SCOREBOARD.md). The same runtime's full frozen replay preserved all 110 sites and every financial value/ID; this final live measurement honestly reports108. No new precision rules were introduced here.

## JBox export input

`C:\Users\Manish\Downloads\nordic-company-lens\bench\runs\20261107T094159020873Z-39a7314\profiles.jsonl`

Exactly 1,000 profiles. Keep the corresponding envelopes, report and state for provenance. Release commit uses Manish Rahul <manishrahul1705@gmail.com>; full hash is reported in the response. No push.
