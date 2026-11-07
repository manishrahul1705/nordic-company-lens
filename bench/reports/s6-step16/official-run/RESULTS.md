# Final-source fresh-clone README check

**PASS: 0 company changes, 0 observation changes; strict pairwise verifier exit 0, identical claim IDs.**

Fresh local clone of `352abc0f00ecdcb203cb3d13fe4e1dfe7da323fd`. `uv sync --frozen` passed. Application credential/search environment variables were removed; NAV?s public token can be obtained in memory without a personal credential. Same literal README command twice, same state directory, no `--previous` or other second-run flags:

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --profiles-output out/profiles.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

Reused the release cohort: 100 valid orgnrs outside benchmark inputs plus three invalid lines. This is not claimed as a new random sample. Input SHA-256: `aa4a2176651c8d05c38f97919733a2c4625117eb1f4925036bef8e13dfe49289`.

| Run | Wall seconds | HTTP | Envelopes / profiles | Company changes | Observation changes |
|---|---:|---:|---:|---:|---:|
| First literal command | 212.031 | 758 | 103 / 103 | 0 | 0 |
| Same command, same state | 213.546 | 740 | 103 / 103 | 0 | 0 |

Both commands exited 0. No deadlines or warnings. Each invalid line produced one failed result. The automatic state snapshot and original evidence remain in `bench/cache/s6-step16-final-official`. The second run is a refresh without an explicit previous-file argument.

The unmodified strict verifier passed: **8,034 supported claims, 318 source blobs, 703 cited sentences, zero unverified values**, identical claim IDs and zero changes/observations. [Verifier](verification.txt), [execution](execution.json), [first metrics](run1-metrics.json), [refresh metrics](run2-metrics.json).

The initial source-42f3cbf pair failed because identical description text moved between apex and www source URLs. It was not accepted as a real company change or hidden. The generic refresh-only correction was tested, replayed against the saved failure without rewriting it, and then validated by this new real pair. [Original failure and cause](initial-alias-failure/RESULTS.md). No extra 1,000-company benchmark was run; the alias correction is unreachable on that run?s `previous=None` path.
