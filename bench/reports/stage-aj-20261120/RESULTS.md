# Stage AJ · Shared source scheduling

## Original audit and diagnosis

The original competitor audit’s raw envelopes and request log were deleted as requested. Its retained summary reports 99 activity and 13 website source errors on the last run, with one deadline hit. The earlier audit reported 98 activity source errors. The retained artefacts cannot recover the exact errors or the original three envelopes. [Retained audit](../competitor-gap-20261120/GAPS.md)

The unchanged-HEAD reproduction used the clean detached checkout, the same 100 inputs, 2 workers, a 1,200 s cap and site rendering off. It completed without reproducing the 98/99 activity failures. It left the previously late sources just 36.4 s of crawl time when the first BRREG updates request started.

| Source | Unchanged HEAD reproduction | Conclusion |
|---|---|---|
| Wikidata | One HTTP 200 at 0.281 s. The saved response contained zero SPARQL bindings. | The query already ran early. The same 100 inputs also had zero Wikidata properties in three saved 1,000-company runs. |
| BRREG updates | Two HTTP 200s, first at 983.594 s and last at 987.047 s. | The old scheduler waited until after company work. Both feeds completed in this reproduction. |
| GLEIF | Five HTTP 200s, first at 988.391 s and last at 992.453 s. | The old scheduler left the lookup vulnerable to the crawl deadline. When it ran here, it verified 14 companies. |
| TED | Search returned HTTP 200 at 992.734 s. All nine XML attempts returned HTTP 202. | The API ran. XML did not become available. The breaker withheld the rest. |

These four collectors use live endpoints, with no required untracked or bundled dataset. NAV loaded the shipped index and completed its forward feed in the unchanged run and default Stage AJ run. It checked one candidate and published zero hiring claims.

The first three activity diagnostics in the reproduction were all `no_verified_website` on complete activity sections (912823970, 916729774, 917998787). They do not represent the original source errors. See the full reproduced records in `bench/runs/stage-aj-baseline-reproduction/first-three-activity-diagnostic-envelopes.jsonl`.

## Change

Wikidata, GLEIF and parent-company BRREG changes run before the company crawl. Protected startup allowances come from the existing pooled ceiling. Subunit change requests still wait for verified parent scope. TED retains its existing order relative to the end of the company crawl and uses the same shared cap as GLEIF.

The BRREG change feed retries a transport network error once after 1–2 seconds of jitter. Both attempts count toward the shared source and pooled limits. Timeouts and HTTP status handling on the feed keep their existing one-attempt behavior. No packaging or proof changes were needed.

## Fresh sample100 results

Cells show companies / claims. Both Stage AJ runs used fresh state and site rendering on. The retained original audit published zero for all six listed families.

| Metric | Original audit | Unchanged HEAD reproduction | Stage AJ defaults | Stage AJ 2 workers / 1,200 s |
|---|---:|---:|---:|---:|
| GLEIF | 0 / 0 | 14 / 73 | 14 / 73 | 14 / 73 |
| TED | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Wikidata | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| BRREG changes | 0 / 0 | 100 / 1348 | 100 / 1348 | 100 / 1348 |
| News | 0 / 0 | 4 / 9 | 5 / 10 | 5 / 10 |
| Hiring | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| Reported runtime before site rendering (s) | 1,030.407 | 1,032.797 | 263.828 | 992.219 |
| Requests | 1,201 | 1,237 | 1,240 | 1,232 |
| Deadline hits | 1 | 0 | 0 | 0 |
| Max requests per company | — | 40 | 40 | 40 |
| Activity source errors | 99 | 0 | 0 | 0 |

Progress reached completed at 301.390 s for defaults and 1,027.330 s for 2 workers, including site rendering. Both generated all 100 profiles.

### Error codes and source responses

- **Unchanged HEAD reproduction**. website · website_candidates (100), declared_domain_absent (1); activity · no_verified_website (74), website_check_incomplete (13).
  - Requests · Wikidata · 200 (1); BRREG change feed · 200 (2); GLEIF · 200 (5); TED · 200 (1), 202 (9).
- **Stage AJ defaults**. website · website_candidates (100), declared_domain_absent (1); activity · no_verified_website (74), website_check_incomplete (13).
  - Requests · BRREG change feed · 200 (2); GLEIF · 200 (5); Wikidata · 200 (1); TED · 200 (1), 202 (9).
  - Shared acquisition finished at 4.531 s.
- **Stage AJ 2 workers / 1,200 s**. website · website_candidates (100), declared_domain_absent (1); activity · no_verified_website (74), website_check_incomplete (13).
  - Requests · BRREG change feed · 200 (2); GLEIF · 200 (5); Wikidata · 200 (1); TED · 200 (1), 202 (9).
  - Shared acquisition finished at 4.500 s.

## Verification

- Focused suite · 128 passed.
- Full suite at HEAD plus AJ edits · 1,740 passed and the known `test_evaluator_cli_direct_invocation_and_site_generation` failed. Its 20 activity sections had BRREG timeouts. The other known evaluator network test passed.
- Stage AJ defaults strict verifier · 100 envelopes, 16,959 claims, 0 unverified synthesis values.
- Stage AJ 2 workers / 1,200 s strict verifier · 100 envelopes, 16,959 claims, 0 unverified synthesis values.

No commit was made. The requested nonzero Wikidata gate is unmet with the exact-match rule on this sample.
