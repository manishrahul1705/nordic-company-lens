# Release validation ? new random cohort

**Strict pairwise status: FAIL.** Both commands emitted every line and reported zero company changes, but one failed-to-successful-empty activity recovery changed the section observation and claim ID. This release check does not claim strict refresh stability. No verifier or runtime behavior was relaxed.

## Checkout, selection and exact command

Fresh local clone of `40a32932c0deb9caf55f3c21a6fac43f2a3f6ede`; frozen dependency installation passed. Release changes affect documentation and validation helpers only; production runtime is unchanged. Application credential/search variables were stripped while OS/PATH variables needed to execute the command were retained. No dotenv file or personal credential was supplied.

New sample: SystemRandom selected eight public BRREG pages within the API accessible search-result window (page 1..99, size100), then 100 distinct checksum-valid records from 799 eligible records. Excluded all 6,699 nine-digit identifiers found in bench/inputs, recorded reports and earlier cached official orgnrs.txt inputs. This is a random sample within that accessible window, not a uniform national registry sample. Three invalid lines: NOT-AN-ORGNR, 123456789 and whitespace-only. Input SHA-256: `aa4a2176651c8d05c38f97919733a2c4625117eb1f4925036bef8e13dfe49289`. [Selection URLs and hashes](selection.json), [input](orgnrs.txt).

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --profiles-output out/profiles.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

Same literal command twice, same state folder, no --previous or additional options. Original evidence, both saved snapshots and out/state/latest-envelopes.jsonl remain at bench/cache/s6-release-official.

| Run | Wall seconds | HTTP | Envelopes / profiles | Company changes | Observation changes |
|---|---:|---:|---:|---:|---:|
| 1 | 150.781 | 654 | 103 / 103 | 0 | 0 |
| 2 | 139.516 | 652 | 103 / 103 | 0 | 1 |

Every input line retained its position; all three invalid lines produced failed sections in one envelope and one profile each. No deadlines or warnings. Both runs stayed below 2,000 HTTP / 2,700 seconds per 100 and the tighter application caps (1,854 HTTP for 103 distinct normalized records, default2,400 seconds / hard2,472 seconds).

## Coverage of the 100 valid companies

| Section | Run 1 available | Run 2 available |
|---|---:|---:|
| Identity | 100 | 100 |
| People | 97 | 97 |
| Subunit/workplace | 58 | 58 |
| Financials | 42 | 42 |
| Website | 8 | 8 |
| Social | 3 | 3 |
| Jobs | 0 | 0 |
| News/activity | 31 | 31 |
| Typed location profiles | 96 | 96 |

All registry sections were available or successfully empty: people97/3empty, subunits58/42empty, accounts42/58empty. Website states:8available,84not_available,4ambiguous,3failed,1blocked on both runs. Activity:31available,63not_available,6failed initially;31available,64not_available,5failed on refresh. Jobs were successfully empty for all100, not token-unavailable failures.

## Strict verifier result

Each output independently passed membership, schema, source hashes/spans and cited synthesis verification: **103 lines, 6,001 published claims, 315 blobs, 672 cited sentences, zero unverified values**. The strict pairwise verifier returned exit1: **Claim IDs differ**. Only activity.section for A & A POOL AS (913381742) changed from failed to not_available; there were no supported fact additions/removals and zero company changes. Its initial activity attempt failed, then a successful empty check recovered on refresh. One observation change is intentional current behavior for recovery; the Step8b stale rule applies to a current transient failure, not a previous first-run failure. [Exact difference and errors](pairwise-difference.json), [verifier traceback](verification.txt). No extra reruns or alternate cohort were selected to hide this failed strict pair.

## Failed / blocked sections and reasons

The tables exclude the three intentionally invalid lines. Codes below are diagnostic metadata; product briefs use plain English.

### Run 1

| Company | Section/state | Reasons |
|---|---|---|
| A+ EIENDOM AS (913819365) | website: failed | website_source_unavailable; website_candidates: no_such_domain, transient_transport_retry, website_timeout |
| A+ EIENDOM AS (913819365) | activity: failed | website_check_incomplete |
| 3D FOTO AGDER AS (927397900) | activity: failed | website_check_incomplete |
| 911PARTYPHONE (992402938) | website: failed | website_source_unavailable; website_candidates: no_such_domain |
| 911PARTYPHONE (992402938) | activity: failed | website_check_incomplete |
| 3D-NORD STENHAUG (927078015) | website: failed | website_source_unavailable; website_candidates: no_such_domain |
| 3D-NORD STENHAUG (927078015) | activity: failed | website_check_incomplete |
| A & A POOL AS (913381742) | activity: failed | website_connect_error |
| ABCB AS (921643810) | activity: failed | website_check_incomplete |
| 3DESIGN FALANA (991309926) | website: blocked | robots_unavailable; website_candidates: no_such_domain, robots_unavailable |

### Run 2

| Company | Section/state | Reasons |
|---|---|---|
| A+ EIENDOM AS (913819365) | website: failed | website_source_unavailable; website_candidates: no_such_domain, transient_transport_retry, website_timeout |
| A+ EIENDOM AS (913819365) | activity: failed | website_check_incomplete |
| 3D FOTO AGDER AS (927397900) | activity: failed | website_check_incomplete |
| 911PARTYPHONE (992402938) | website: failed | website_source_unavailable; website_candidates: no_such_domain |
| 911PARTYPHONE (992402938) | activity: failed | website_check_incomplete |
| 3D-NORD STENHAUG (927078015) | website: failed | website_source_unavailable; website_candidates: no_such_domain |
| 3D-NORD STENHAUG (927078015) | activity: failed | website_check_incomplete |
| ABCB AS (921643810) | activity: failed | website_check_incomplete |
| 3DESIGN FALANA (991309926) | website: blocked | robots_unavailable; website_candidates: no_such_domain, robots_unavailable |

## CI and test status

Exact live-20 workflow commands passed locally in the fresh checkout:20 outputs,171 requests,133.329 seconds application time (134.250 seconds process wall),0deadlines; scoped require-clean verifier passed2,421claims/84blobs/170citedsentences. Five optional failures were logged, registry checks remained strict. [Commands and exits](ci20-execution.json), [verifier and failed-section summary](ci20-2.txt). This is a local reproduction, not a claim about a remote Actions run. Nothing was dispatched or pushed.

Initial full suite in the network sandbox:1,093passed/2failed in259.04s. Exact failures: test_evaluator_cli_direct_invocation_and_site_generation and test_evaluator_shapes_union_contract_reference; existing live BRREG CLI checks received ConnectError/network_error for registry roles/subunits/accounts and strict verification rejected those incomplete sections. No product bug or relaxed registry gate was introduced. Network-enabled full suite: **1,095 passed in 267.75 seconds** (exit0). [Final full-suite log](full-tests-network.txt). No runtime, test or workflow changes were required.
