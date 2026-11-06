# Final fresh-clone README check

Fresh local clone of **5f1c5e1**, with application credential/search environment variables absent. `uv sync --frozen` passed. The same literal README command ran twice, without modification or `--previous`:

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --profiles-output out/profiles.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

The frozen official cohort contains 100 checksum-valid organisation numbers outside `bench/inputs`, plus three invalid lines. It reuses the previously selected public-BRREG official cohort, rather than claiming a new random selection this turn. Input SHA-256: `e42b962027dd5839e6c9b0ba396481421fa7ec07ef9ccf6d82cb898e01848a8b`.

| Run | Wall seconds | HTTP | Envelopes / profiles | Changes | Observation changes |
|---|---:|---:|---:|---:|---:|
| First literal command | 127.875 | 661 | 103 / 103 | 0 | 0 |
| Same command, same state | 127.438 | 660 | 103 / 103 | 0 | 0 |

The strict pairwise verifier passed: identical claim IDs, 7793 published claims, 342 source blobs verified, 720 cited template sentences, zero unverified values, zero changes and zero observation changes. Original state evidence and automatic previous snapshots remain in the local clone at `bench/cache/s6-step10-final-verified-official`. [Verifier output](verification.txt), [execution](execution.json), [first metrics](run1-metrics.json), [refresh metrics](run2-metrics.json).

Both runs are below 2000 HTTP / 2700 seconds per 100 and the application's tighter limits. Invalid lines each retain one failed result. Paid search and language models remain disabled; NAV's published public token is obtained in memory when needed, without a personal credential.

The pre-rollback trial also passed its own pairwise check, but that was not accepted as validation of the final precision policy. Earlier local checks are retained under their separate cache folders; only the exact final-source pair above is reported as final.

## Synthesis wording and stable citations

The final A-DVENTURES AS brief says:

- “News and activity: not found (no verified company website was found).” Citation `58174e858cbc8d442bdfe38a8d9170573f4c8e8439141db979afca8e31683c49`.
- “Website and social: not found (the website blocks automated access (robots.txt)).” Citation `bbd3619a5cfe76a7d5d041bac921df6d20ed2980f9d5eeccee413cda3042435e`.

These are the **same citation IDs** as the Step 9 examples with raw reason codes. Context values remain unchanged. Timeout/DNS/reset/TLS failures, group/shared sites and ambiguous attribution likewise use plain English; unknown internal codes use a safe sentence rather than leaking a code. Stale sentences retain their failed-attempt date. Writer and independent verifier recompute the same frames; forged text or citations fail tests. [Real wording examples](plain-english-examples.json).
