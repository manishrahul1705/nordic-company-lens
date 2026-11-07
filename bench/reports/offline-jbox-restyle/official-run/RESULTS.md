# Literal README command, final offline-site runtime

Fresh local clone of dba197e plus the exact site-only patch; source hashes match the workspace. Release cohort100 valid identifiers plus3 invalid lines; SHA-256 aa4a2176651c8d05c38f97919733a2c4625117eb1f4925036bef8e13dfe49289. Clean state, uv sync --frozen passed, application credential/search environment removed. Both commands identical, same state directory, no --previous:

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --profiles-output out/profiles.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

| Run | Seconds | HTTP | Envelopes/profiles | Company changes | Observation changes |
|---|---:|---:|---:|---:|---:|
| First | 207.047 | 757 | 103/103 | 0 | 0 |
| Refresh | 206.235 | 744 | 103/103 | 0 | 0 |

**Unmodified strict verifier exit0.** Site exports passed in both runs, with zero deadlines and warnings. Source/evidence/citation checks remain unchanged. [Execution](execution.json), [strict result](verification.txt), [site results](site-results.json). No push.
