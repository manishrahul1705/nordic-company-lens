# Final fresh-clone README check

Fresh local clone of final runtime `45c9494fb603f511fe0a89a2b4b02dea76e4cc40`; `uv sync --frozen` passed. Application credential/search environment stripped; no personal token, search or LLM. Reused release 100 valid + 3 invalid cohort, input SHA-256 `aa4a2176651c8d05c38f97919733a2c4625117eb1f4925036bef8e13dfe49289`.

Same literal command twice, same state directory; no --previous or extra second-run flags:

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --profiles-output out/profiles.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

| Run | Wall seconds | HTTP | Envelopes / profiles | Company changes | Observation changes |
|---|---:|---:|---:|---:|---:|
| First | 204.703 | 757 | 103 / 103 | 0 | 0 |
| Same command, same state | 199.219 | 741 | 103 / 103 | 0 | 0 |

**Unmodified strict verifier exit 0:** identical claim IDs, 8,462 supported claims, 318 checked source blobs, 418 cited primary sentences, zero unverified values. All **103 primary briefing texts are identical** across refresh. All invalid lines retain their own failed result; previous snapshots and original evidence remain in state.

Both site exports were available with no warnings or deadlines; all 100 valid companies have offline pages. [Site and count checks](output-check.json), [execution](execution.json), [strict output](verification.txt). The original local clone and state are retained at `bench/cache/s6-step18-final-official`. No output rewriting, verifier relaxation or repeat pair was used.
