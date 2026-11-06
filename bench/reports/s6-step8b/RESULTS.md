# S6 Step 8b — transient refresh snapshot retention

**PASS.** Final source revision `1290c34`. The full suite passed **959 tests in 288.34 seconds**. The unchanged strict pairwise verifier passed on two literal README invocations from a fresh clone. Search stayed OFF; application credentials were removed; nothing was pushed.

## Retention behavior

A current timeout, DNS/SERVFAIL, reset/connect or TLS transport failure retains a prior `available`, `not_available` or `ambiguous` section snapshot: its state, all claim IDs (including unavailable section claims), original evidence references and supporting-page metadata. Claims are marked `carried_forward` and dated with `stale_since`.

`run.refresh.stale_sections[section]` records `previous_state`, `attempt_state`, `failed_attempt_at`, `failure_codes` and attempt diagnostics. Current errors remain visible. The classifier reads nested `website_candidates` diagnostics and propagates website transport failures to dependent `website_check_incomplete` activity attempts. Restored sections emit no company or observation change.

First-ever failures remain `failed`. Successful new values and successfully established removals still produce changes. HTTP 404/410/gone on the previous verified domain and refuted ownership are not transient failures. A guessed domain's 404 cannot override another candidate's transient failure when the previous section had no verified website. Strict identity validation cannot restore an available state after its supporting prior claims were removed. Details: [refresh documentation](../../../docs/REFRESH.md).

## Fresh-clone README check

Fresh clone: `bench/cache/s6-step8b-final`, commit `1290c34a148acceb4616247910297c465f247d1b`. `uv sync --frozen` passed. Both invocations had application credential/search/model environment variables removed, including `NAV_API_TOKEN`.

Input: the same 100 checksum-valid BRREG identifiers from Step 8, none in `bench/inputs`, followed by `NOT-AN-ORGNR`, `123456789` and a whitespace-only line. SHA-256: `e42b962027dd5839e6c9b0ba396481421fa7ec07ef9ccf6d82cb898e01848a8b`.

Exact README command, twice with the same state folder and no additional flags on run 2:

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --profiles-output out/profiles.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

| Metric | First command | Same command, same state |
|---|---:|---:|
| Envelopes | 103 | 103 |
| Profiles | 103 | 103 |
| Wall seconds | 235.314 | 224.487 |
| HTTP requests | 1000 | 998 |
| Max HTTP per company | 18 | 18 |
| Company changes | 0 | 0 |
| Observation changes | 0 | 0 |
| Deadline hits / warnings | 0 / 0 | 0 / 0 |

Each invalid line produced one failed output. The automatic `out/state/latest-envelopes.jsonl` snapshot supplied the previous run; neither command used `--previous`. Both complete outputs, profiles, reports, execution metadata and source blobs are retained in the ignored fresh-clone folder.

Strict verification used the repository script without changing it or rewriting output:

```sh
uv run --frozen python scripts/verify_output.py --first validation/run1-envelopes.jsonl --second validation/run2-envelopes.jsonl --state-dir out/state --count 103 --organisations orgnrs.txt --report validation/run2-report.json
```

Result: **103 + 103 lines, valid schema/membership, identical claim IDs, 0 company changes, 0 observation changes**. It checked 7,683 published claims, 337 source blobs, 103 syntheses and 712 cited sentences; zero unverified synthesis values. Run 2 also passed a standalone full evidence verification with the same counts. Both runs stayed within the HTTP/time budget.

The final live pair had no section-state flips and required **zero live stale restorations**. Deterministic tests force the failure cases; the live results do not claim those failures occurred. Machine-readable results: [validation.json](validation.json).

## Tests

Added 29 focused cases in [test_refresh_transient_snapshot.py](../../../tests/test_refresh_transient_snapshot.py): three eligible prior states; nested timeout/DNS/SERVFAIL/NXDOMAIN/reset/TLS failures; dependent activity; claim/evidence retention; attempt timestamps; same-command implicit refresh; first-run honesty; strict identity support removal; successful new values; ownership contradiction; HTTP 404/410/gone; and mixed guessed-404/DNS failures.

Six existing tests required the superseded behavior of setting the website section to failed on a transient refresh. They now require the prior available state and a failed attempt recorded in stale metadata. Non-transient failure and ownership safety tests remain in the full suite.

```sh
uv run --frozen pytest -q --basetemp .pytestroot-step8b-final-1290 -p no:cacheprovider
```

**959 passed in 288.34 seconds.** A workspace temp directory avoids this machine's inaccessible default pytest temp root. Network access was available for the existing registry-backed evaluator tests.

## Commits

- `11f5eb5`: preserve full section snapshots, classify nested transport diagnostics, record stale attempt dates, add regression tests.
- `1290c34`: narrow the guessed-domain 404 exception, preserve strict identity validation, update remaining legacy assertions and documentation.
- The final validation/report commit is reported in the response.

Author and committer: Manish Rahul <manishrahul1705@gmail.com>. Work stayed on main. No push.
