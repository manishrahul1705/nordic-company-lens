# Stage AI: first-observation citation

## Diagnosis and fix

At `b23558d611f3359957d97ffbe487b7b46201ef91`, the four-section template emitted “First observation; no earlier run to compare.” and cited `claims[0]`. In the saved 1,000-company run, that was usually `identity.founding_date`, which does not establish first-run status. The three-part company brief already used a `snapshot.refresh` context claim for its equivalent first-observation sentence.

The template now uses “Registered name: <registry legal name>.” on baseline runs, cited to the matching available `identity.legal_name` claim. All 1,000 baseline records have this claim and official-registry evidence. This makes no claim about prior-run history and does not change the validator or verifier. The repeat-run company brief remains unchanged and continues to cite the refresh context claim.

## Offline replay

The replay reads `bench/runs/funding-news-brief-final-20261120` and forbids `socket.connect` and `socket.getaddrinfo`. It made zero HTTP requests. Across 1,000 companies, **1,000 sentences changed**, none were removed, and total seven-section synthesis sentences stayed **15,151 → 15,151**. The strict verifier passed: 1,000 envelopes, 167,975 claims, 5,882 source blobs, zero unverified values. Ten hand reviews, with complete claim and evidence records, are in [hand-review-10.json](hand-review-10.json).

## Base versus Stage AI evaluator tests

The two evaluator tests were run twice at base, then twice with the Stage AI change restored. All eight invocations failed with the same assertion: `scripts/verify_output.py` raised **“Incomplete smoke-test section”**. No failure mentioned synthesis or first-observation wording.

| Test | Base run 1 | Base run 2 | Change run 1 | Change run 2 |
|---|---|---|---|---|
| `test_evaluator_cli_direct_invocation_and_site_generation` | failed; 227 requests, 7,735 ms | failed; 227 requests, 7,172 ms | failed; 227 requests, 7,516 ms | failed; 227 requests, 7,625 ms |
| `test_evaluator_shapes_union_contract_reference` | failed on first (`contract`) shape; 227 requests, 7,609 ms | same; 227 requests, 7,406 ms | same; 227 requests, 7,547 ms | same; 227 requests, 7,407 ms |

Each run reported zero deadline hits and zero warnings. The failure is reproducible at the base and behaves the same with the change. The full suite with the change recorded **1,732 passed and these 2 failed**. Focused synthesis and brief tests passed: **38 passed**. No test or verifier acceptance rule was loosened.
