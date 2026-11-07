# Fixed runtime: fresh clone, clean state, same README command twice

Fresh clone based on b3fe202 plus the exact tested pending patch, copied before execution; final source-file SHA-256 matches workspace and clone. See ../fixed-runtime-source.json and ../final-source-integrity.json. Clean new state; no interrupted or earlier cohort state reused. Application credential/search environment stripped; uv sync --frozen passed. Same NEW Step22 input (100 valid + three invalid lines).

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --profiles-output out/profiles.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

| Run | Seconds | HTTP | Envelopes/profiles | Deadlines | Company changes | Observation changes |
|---|---:|---:|---:|---:|---:|---:|
| First | 336.360 | 788 | 103/103 | 0 | 0 | 0 |
| Same command, same state | 175.704 | 753 | 103/103 | 0 | 0 | 0 |

**Unmodified strict verifier exit0.** Identical claim IDs, zero unverified values. All 100 valid-company briefing texts are identical across refresh; the ten randomly reviewed briefing texts also match the original reviewed versions. Both site exports passed without warnings. Invalid lines retain one failed result each. Runtime includes all fixed collectors, synthesis and site end to end. No verifier relaxation.

The original b3fe202 pair had one unchecked-page observation and strict exit1; it is preserved separately. Only this final fixed-runtime pair is claimed as passing.

[Execution](execution.json), [verifier](verification.txt), [exact coverage](coverage.json).
