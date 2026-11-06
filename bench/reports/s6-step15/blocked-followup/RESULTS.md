# Speculative access-refusal correction: accepted external observations

**Strict pairwise result: 0 company changes; 2 observation changes caused by live site responses changing between runs; verifier exit 1 (Claim IDs differ). Accepted by the user for the Step 15 commit; no push.**

Focused tests: **127 passed in 18.15 seconds**. Full suite: **1187 passed in 274.26 seconds**. Speculative 429/robots/blocked refusals now remain LOW candidate-not-reachable diagnostics rather than section blocked errors. Strong-source blocked semantics remain unchanged.

Fresh clone of base `5506e98c6e8a6ce98eebbae09e832d0a58dd2b3b`, with exactly the two pending tested files copied in before the conditional commit. [Source SHA-256 manifest](candidate-source.json), [exact pending patch](candidate.patch). Source bytes were checked identical to the workspace after validation. `uv sync --frozen` passed; application credential/search environment stripped. Reused the release cohort (100 valid identifiers plus three invalid lines), SHA `aa4a2176651c8d05c38f97919733a2c4625117eb1f4925036bef8e13dfe49289`.

Same literal command twice, with identical state directory and no extra second-run flags:

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --profiles-output out/profiles.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

| Run | Seconds | HTTP | Envelopes / profiles | Company changes | Observation changes |
|---|---:|---:|---:|---:|---:|
| First | 205.922 | 768 | 103 / 103 | 0 | 0 |
| Same command, same state | 196.344 | 743 | 103 / 103 | 0 | 2 |

Both commands exited 0, with no deadline hits. The strict verifier exited 1; it was not relaxed or substituted with a standalone check.

- **1975 STIAN AAGAARD / 993350990:** website blocked -> not_available. Contrary to the request's premise, `identity.registered_website` is `www.1975.no`; subunit 993367168 also nominates it. This is a strong source. The apex HTTP response was 429 then 404; HTTPS TLS failures and HTTP www 404 occurred in both runs. No company-specific exception was introduced.
- **A1 LIVING AS / 926089056:** website ambiguous -> not_available. Speculative a1living.com redirected to Atom's domain-sale page, first HTTP 200 with insufficient exact-company proof, then HTTP 403. The second run correctly keeps the refusal candidate-scoped; it does not mark the section blocked. No website was published in either run. The existing absence/ambiguity observations remain honest.

[Exact candidate diagnostics and transitions](observation-changes.json), [execution](execution.json), [strict failure](verification.txt). Original state/evidence remains in `bench/cache/s6-step15-blocked-official`. No extra 1000 benchmark was run. The user accepted these two genuine external-response observations for committing Step 15 as is. The strict result remains unchanged; no checks were rerun.
