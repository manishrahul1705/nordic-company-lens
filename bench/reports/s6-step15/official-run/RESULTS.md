# Final-source fresh-clone README pair

Exact source: `5506e98c6e8a6ce98eebbae09e832d0a58dd2b3b`. Fresh local clone, `uv sync --frozen` passed; application credential/search environment removed. Same literal command twice, same state, no extra second-run flags:

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --profiles-output out/profiles.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

Reused release cohort: 100 valid identifiers outside benchmark inputs plus three invalid lines; no claim of a newly sampled cohort. SHA-256: `aa4a2176651c8d05c38f97919733a2c4625117eb1f4925036bef8e13dfe49289`.

| Run | Seconds | HTTP | Envelopes / profiles | Company changes | Observation changes |
|---|---:|---:|---:|---:|---:|
| First | 204.515 | 755 | 103 / 103 | 0 | 0 |
| Same command, same state | 203.141 | 742 | 103 / 103 | 0 | 1 |

**Strict pairwise verifier: FAIL, exit 1, Claim IDs differ.** This is not reported as a passing zero-observation pair. Company 993350990 (1975 STIAN AAGAARD) changed website state from blocked to not_available: the registry-declared domain 1975.no returned HTTP 429 on the first run, then HTTP 404 on the second. Its website.section claim ID changes with the section state; no company fact changes. A successful 404 is allowed to establish absence; the verifier and refresh semantics were not weakened to suppress that observation. [Exact observation](observation-changes.json), [unchanged verifier failure](verification.txt).

Each standalone verifier passes: 103 schema-valid lines, 6104 claims, 318 source blobs, 703 cited sentences, zero unverified values. Each invalid input retains one failed result. Both runs respect HTTP/time limits, with no deadline hits. Snapshots, profiles and original evidence remain in `bench/cache/s6-step15-state-official`; lightweight execution/metrics are retained here. No extra 1000 crawl was run.
