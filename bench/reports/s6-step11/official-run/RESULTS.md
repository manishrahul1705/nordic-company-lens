# Step 11 final fresh-clone README check

Fresh local clone of **d81b45e**, no application credential/search environment variables, `uv sync --frozen` passed. The literal README command ran twice without modification, using the same state directory and no `--previous`:

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --profiles-output out/profiles.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

| Run | Wall seconds | HTTP requests | Envelopes / profiles | Changes | Observation changes |
|---|---:|---:|---:|---:|---:|
| First command | 156.281 | 650 | 103 / 103 | 0 | 0 |
| Same command, same state | 127.813 | 650 | 103 / 103 | 0 | 0 |

The strict pairwise verifier passed: identical claim IDs, **7793 supported claims**, **342 checked source blobs**, **720 cited synthesis sentences**, **zero unverified values**, zero changes and zero observation changes. [Exact verification](verification.txt), [execution](execution.json), [first metrics](run1-metrics.json), [refresh metrics](run2-metrics.json).

The frozen official cohort is the previously sampled 100 checksum-valid BRREG identifiers outside `bench/inputs`, plus three invalid lines. This is a reused cohort, not a claimed new random sample. Input SHA-256: `e42b962027dd5839e6c9b0ba396481421fa7ec07ef9ccf6d82cb898e01848a8b`. The three invalid lines each retain one failed envelope and profile. Both runs are below the request/time budgets. Search and LLM calls are zero, cost $0; NAV may obtain its published public token in memory, without a personal credential.

Retained original outputs, automatic previous snapshot and evidence are in `bench/cache/s6-step11-official-final`. An earlier pre-footer-regression clone also passed, but it is not substituted for this final-source pair. No push.
