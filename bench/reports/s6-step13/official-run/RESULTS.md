# Step 13 fresh-clone official command

Fresh local clone of source **7474c372**, `uv sync --frozen` passed. Application credential/search environment variables were stripped. The exact README command ran twice, unmodified, using the same state directory and no `--previous`:

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --profiles-output out/profiles.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

| Run | Wall seconds | HTTP | Envelopes / profiles | Changes | Observation changes |
|---|---:|---:|---:|---:|---:|
| First literal command | 210.250 | 726 | 103 / 103 | 0 | 0 |
| Same command, same state | 205.594 | 726 | 103 / 103 | 0 | 0 |

Strict pairwise verifier **passed**: **7805 supported claims**, **354 checked source blobs**, **721 cited synthesis sentences**, zero unverified values, identical claim IDs, zero changes and zero observation changes. [Exact verifier output](verification.txt), [execution](execution.json), [first metrics](run1-metrics.json), [refresh metrics](run2-metrics.json).

This reuses the frozen official cohort of 100 valid public-BRREG organisation numbers outside `bench/inputs`, plus three invalid lines. It is not a claimed new random selection. Input SHA-256: `e42b962027dd5839e6c9b0ba396481421fa7ec07ef9ccf6d82cb898e01848a8b`. Invalid inputs retain one failed envelope/profile each. Original evidence and automatic previous snapshots remain in `bench/cache/s6-step13-official`; first-run copies are for verification only, not flags passed to the agent.

Both runs remain within 2000 HTTP / 2700 seconds per 100 and the application's tighter global limits. Search and LLM calls are zero, cost $0. NAV uses its public token in memory when required; no personal credential, PDF downloader or pypdf dependency is present. No push.

Additional official-cohort precision review: [12 dated A-Hjort publications](REVIEW.md), all correct, zero wrong-company items. Exact Norwegian orgnr is present in saved homepage JSON-LD.
