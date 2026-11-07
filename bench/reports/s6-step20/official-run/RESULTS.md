# Final runtime fresh-clone README pair

Fresh local clone of `34e0a70eaf80e528478e60b9412fdaebaf29d455` at bench/cache/s6-step20-resumed-final; new clean state, no previous interrupted state reused. Application credential/search environment removed. `uv sync --frozen` passed. Release cohort: 100 valid identifiers plus three invalid lines; input SHA-256 `aa4a2176651c8d05c38f97919733a2c4625117eb1f4925036bef8e13dfe49289`.

Both invocations used the literal README command, unchanged:

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --profiles-output out/profiles.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

| Run | Seconds | HTTP | Envelopes / profiles | Company changes | Observation changes |
|---|---:|---:|---:|---:|---:|
| First | 262.579 | 757 | 103 / 103 | 0 | 0 |
| Same command, same state | 210.938 | 742 | 103 / 103 | 0 | 0 |

**Unmodified strict pairwise verifier exit 0.** BRREG, websites, NAV, GLEIF, TED, synthesis and static site ran end to end under the final runtime. Both runs had zero deadlines and no warnings. Each run's GLEIF request and TED API request returned **200**, with no 406. This release sample has no exact eligible TED notices, so it caused no XML fetches; the 75 successful XML fetches are independently recorded in the frozen-1000 enrichment continuation, not falsely attributed to this pair.

[Execution](execution.json), [request statuses and source metrics](request-statuses.json), [strict verifier](verification.txt). The shutdown-affected older pair is preserved separately and is not substituted for this result.
