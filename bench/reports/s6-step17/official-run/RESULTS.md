# Final fresh-clone literal README pair

Fresh local clone of runtime **acaca26eb9f2962161122c53ed5eb0053b7dd52c**. `uv sync --frozen` passed. Application credential/search environment removed; no personal token, search or LLM. The release cohort is reused: 100 valid organisation numbers plus three invalid lines; SHA-256 `aa4a2176651c8d05c38f97919733a2c4625117eb1f4925036bef8e13dfe49289`.

Same literal README command twice, same state directory, no `--previous` or extra second-run flags:

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --profiles-output out/profiles.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

| Run | Seconds | HTTP | Envelopes / profiles | Company changes | Observation changes |
|---|---:|---:|---:|---:|---:|
| First | 211.640 | 756 | 103 / 103 | 0 | 0 |
| Same command, same state | 206.547 | 746 | 103 / 103 | 0 | 0 |

**Unmodified strict pairwise verifier exit 0:** identical claim IDs, 8,034 supported claims, 318 checked source blobs, 416 cited primary briefing sentences, zero unverified values, zero company changes and zero observation changes. Both invocations exited 0, with no deadlines or warnings. Each invalid line retains its own failed result.

All **103 primary briefing texts are identical** between baseline and refresh. Previous snapshots and original evidence remain in `bench/cache/s6-step17-official/out/state`. Detailed legacy synthesis remains independently verified alongside the primary briefings. No verifier relaxation, output rewriting or retry pair was used.

[Execution](execution.json), [strict verifier](verification.txt), [counts/text stability](output-check.json).
