# TED re-probe, deadline wording, and direct NAV measurement

19 November 2026, branch `audit-fixes`. No push. This report follows the requested order: two fixes, then a read-only NAV measurement. No NAV production code changed, and no full pipeline run was requested or performed this turn.

## 1. TED circuit breaker re-probe

Implemented a re-probe after every **25 actually skipped notices** while the breaker is open. The next notice is fetched alone using the unchanged three-attempt policy. A successful fetch closes the breaker, resets its failure streak and resumes normal batches of three; a failed re-probe leaves it open. Per-host one-second admission spacing, concurrency three for normal batches, request ceilings and shared deadlines are unchanged.

Skipped notices retain `ted_202_circuit_open` in failure metrics. Affected company coverage remains `not_available_fetch_failed`, with that explicit reason, even if the breaker later recovers. Metrics now include the re-probe interval and each probe's result. Separately verified awards found after recovery are retained despite incomplete coverage; previously the final failure-state filter could erase all verified awards for a company that had an earlier skipped/failed notice. Unknown discovery is never evidence of no awards.

For **79 nominated notices**, a fully down service opens after the first three notices, skips 25, probes notice 29, skips 25, probes notice 55, then skips the final 24. That is **two extra probes, six extra HTTP attempts, 22 seconds of backoff**. Each probe can add up to 45 seconds of request execution (three 15-second timeouts), 11 seconds backoff and up to one second of initial pacing: **approximately 57 seconds per probe, or 114 seconds added**, excluding scheduler overhead and subject to existing caps/deadline. Fast HTTP 202 responses incur mainly the 22 seconds of backoff plus response/pacing time, rather than the conservative timeout bound.

For M notices in a sustained outage, the number of probes is `floor(max(M - 3, 0) / 26)` before existing caps/deadline curtail attempts; the 114-second bound is specific to the saved 79-notice workload, not a universal bound for arbitrary batches.

Validation: **58 focused tests passed in 12.31 seconds** ([test output](ted-tests.txt)). These cover circuit opening, failed probes remaining open, a successful probe closing/resuming, retained skipped-state reasons, surviving verified awards after recovery, and the existing pacing/cap/transport tests. The full suite was not rerun this turn; the previous 1,533-test result predates this re-probe change.

## 2. Deadline wording

Updated both `SUBMISSION.md` and `README.md` to describe the latest frozen run accurately: **zero global deadline hits; one local section timeout recorded by `deadline_hits=1`**. TENSIO `922828172` reached the 45-second local second-pass activity timeout. Verified registry activity kept that section **available**, so the timeout did not cost the section. The counter's code and meaning are unchanged. The earlier 1,437-second run and its zero-hit result are explicitly historical, not the latest runtime measurement.

## 3. Direct NAV endpoint measurement ? no implementation change

Requested URL:

`https://arbeidsplassen.nav.no/public-feed/api/v1/ads?orgnr=<orgnr>&size=10`

The 1,000-company sweep was anonymous, with `Accept: application/json` and the project User-Agent. Because the retired API historically required a bearer token, a separate control used NAV's currently published experimental token for company `976645677`: it also returned **HTTP 404 with HTML**. This did not produce an ads response or change the conclusion. No personal credentials were used; token values were not saved in the report artifacts. See [authenticated control](authenticated-control.json).

Queried every distinct company in `bench/inputs/1000-r3/batch.jsonl` exactly once, with no retries. Frozen input SHA-256: `7ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782`. The preserved first probe is included in the 1,000 count, not duplicated.

| Result | Companies |
|---|---:|
| HTTP 404 (HTML page, not an ads response) | 988 |
| HTTP 429 (rate limited) | 12 |
| Usable JSON ads response | 0 |
| At least one ad in NAV | **Unknown / not measurable here** |
| At least one active ad | **Unknown / not measurable here** |

A 404 or 429 is **not** an empty ad list. Therefore this experiment cannot provide a new company-coverage count or a numerical uplift over the **3 published companies** and the user-supplied audit's **at most 7 with any ad**. Zero usable responses must not be reported as zero companies with ads. The measurement summary records the ad counts as null rather than zero.

**The supplied API is retired.** NAV's [official archived public-feed repository](https://github.com/navikt/pam-public-feed#readme) states that public-feed ceased availability on **1 May 2025** and directs consumers to stilling-feed. The [current feed documentation](https://navikt.github.io/pam-stilling-feed/) says consumers must implement employer/company filtering on their side. This explains why the supplied legacy URL is not a usable orgnr search service in the measurement. The claim that a leading entry currently obtains ads from this exact URL could not be corroborated; no inference is made about which alternative endpoint that entry may actually use.

**Parent versus subunit:** not empirically measurable from this endpoint, because no ad/employer payload was returned. It would be unsupported to claim that it expands parent IDs to subunits, or that it searches only parents. A future supported direct query would need explicit tests against known parent/subunit ad pairs. Our current publication path already requires an exact employer orgnr matching the legal entity or a verified registered subunit; names nominate candidates rather than prove publication attribution (`src/signalpost/sources/nav.py`, `section`). A better direct lookup would improve discovery, not replace a name-only publication rule.

**Request cost:** 1,000 endpoint requests, one per company, or **5.263 percentage points of the 19,000-request pool**. Ancillary diagnostics were separate from the 1,000-company sweep: three policy-page requests, two public-token fetches and one authenticated legacy query. An earlier control attempt failed locally before sending headers because the token response includes explanatory text; it was corrected. These are not retries of the cohort sweep. As an additive projection, the earlier 9,275-request run would become **10,275 / 19,000 = 54.08%** instead of 48.82%; the latest 8,953-request run would become **9,953 / 19,000 = 52.38%** instead of 47.12%. Pagination, retries, additional subunit queries or detail checks could cost more. The existing 40-request per-company cap would also need to remain effective.

**Observed acquisition time:** four workers, at least 0.25 seconds between request starts, no redirects followed and no retries. The remaining 999-request sweep took **614.736 seconds**, including rate-limit pauses; the preserved first request took **1.924 seconds** separately. This is not a measured full-pipeline overhead or a contiguous 1,000-query benchmark. Retry-After/default backoff was honored; failed responses remain unavailable observations.

**Robots and terms:** the fetched [robots.txt](https://arbeidsplassen.nav.no/robots.txt) returned HTTP 200 with `User-agent: *` and an empty `Disallow:`, permitting the requested path. The current [NAV feed terms](https://arbeidsplassen.nav.no/vilkar-api) allow free use for statistical/analytical purposes and republication, with obligations to update changed ads and remove inactive/deleted ads; application links must point to the original application function. That permission does not restore a retired route. The archived old-terms link `/vilkar-api-gammel` returned 404, so no separate historical terms text was inferred from it. Policy response bodies, status codes and hashes are saved under [policy/](policy/).

**Decision:** do not switch to this legacy URL. It did not demonstrate materially more than seven companies?or any usable coverage measurement?and no NAV implementation was changed.

## Evidence

- [NAV measurement summary](nav-measurement.json)
- [Per-company request observations](queries.jsonl) (local artifact; no ad/contact data)
- [Read-only query runner](query_nav_direct.py)
- [Separate authenticated control](authenticated-control.json)
- [Initial query](first-query.json) and [its HTML response](first-query-body.txt)
- [Saved robots and terms responses](policy/responses.json)
- [TED focused tests](ted-tests.txt)

`git diff --check` passed. Nothing was pushed.
