# Stage P ? official-source recall sweep

## GLEIF: confirmed formatting under-match

Official public API measurements on 14 November 2026 (IST), no credentials:

| Query | Total LEI records | Total / 411,160 ? 1,000 |
|---|---:|---:|
| entity.registeredAt = RA000472 | 63,779 | 155.120 |
| entity.legalAddress.country = NO | 66,224 | 161.066 |

These are upper-bound population rates, not measured universe intersections: totals include LEI records outside the challenge universe and potentially non-current registrations. The country query includes different authorities; the authority query includes six records with other legal-address countries (63,773 are NO). They must not be added. Both 32 and 140 per 1,000 are mathematically possible sample rates. A random 100-company sample is not capped at the population mean. The competitor's 140/1,000 (14 in a 100-company sample) is possible; extrapolated as a representative population rate it implies 57,562.4 companies, below both totals. Our old 32/1,000 would imply 13,157.12, but is not an estimate of the ceiling.

Sources: [official GLEIF API](https://www.gleif.org/en/lei-data/gleif-api/), saved exact request URLs/responses in authority.json, country.json and no_ra472.json. Definitions of registeredAs and registeredAt are in the [GLEIF data dictionary](https://www.gleif.org/media/pages/lei-data/access-and-use-lei-data/gleif-data-dictionary/ffc2165423-1765981476/2025-11-18_gleif-data-dictionary_v1.2_final.pdf).

### Direct known-company checks

| Legal name | entity.registeredAs (verbatim) | entity.registeredAt.id | legalAddress.country | entity.status |
|---|---|---|---|---|
| EQUINOR ASA | `923 609 016` | RA000472 | NO | ACTIVE |
| DNB BANK ASA | `984 851 006` | RA000472 | NO | ACTIVE |
| Norsk Hydro ASA | `914 778 271` | RA000472 | NO | ACTIVE |
| TELENOR ASA | `982 463 718` | RA000472 | NO | ACTIVE |
| ORKLA ASA | `910 747 711` | RA000473 | NO | ACTIVE |

See known_large.json. The unspaced lookup for the first three returned no records; their spaced lookup returned all three (known_unfiltered.json / known_spaced.json). The earlier exploratory request also included two incorrect org numbers; those two are not used as negative evidence. Correct Telenor and Orkla identifiers are shown above and in known_large.json.

The official registration-authority records identify RA000472 as Foretaksregisteret / Register of Business Enterprises, and RA000473 as Enhetsregisteret / Central Coordinating Register for Legal Entities. Both belong to Bronnoysund (ra472.json and ra473.json). RA000473 has 2,088 total records (authority473_total.json). Its exclusion can reject legitimate Norwegian records, including Orkla. Adding another authority changes the authority acceptance rule, so that expansion is deliberately not applied in this stage. Three frozen-cohort records remain excluded: EDSVIK INVEST AS (935327423), WACKER CHEMICALS NORWAY AS (995541432), ROTOR REAL 1 AS (926970348).

### Contained fix and isolated measurement

The frozen 1,000 was queried in ten batches for both exact nine-digit and exact `XXX XXX XXX` number spellings, without an authority restriction during diagnosis. All responses fit one page. There are 142 unique exact-number matches, all country NO and entity ACTIVE: 139 RA000472, 3 RA000473. The existing literal check accepts 32. Removing only optional three-digit-group whitespace, retaining RA000472, accepts 139. No evidence in this inspected set requires another identifier field; this is not a claim to have exhaustively audited every Norwegian LEI.

The production fix requests both spellings and normalizes only complete nine-digit or three-group whitespace registration numbers before exact input comparison. Prefixes, punctuation, trailing material, different numbers and other authorities are still rejected. No name matching, legal-status loosening, parent acceptance, website proof or scoring changes.

Identical-response offline replay: **32 ? 139 companies**, **160 ? 695 direct GLEIF claims**, **107 newly matched companies**. Existing claim IDs are identical on the same response. See offline-effect.json, cohort-gleif-matches.json and cohort-0000.json through cohort-0900.json. These direct claims are distinct from any additional relationship claims produced by the full runner.

The first full suite exposed two evaluator-output failures: `ValidationError: Duplicate evidence IDs` (1,410 passed / 2 failed). Increased matching made the existing direct/ultimate-same-parent bookkeeping case reachable. A recorded-response regression reproduced 9 evidence records with only 8 unique IDs. The additional contained correction retains each identical evidence record once; both parent claims and all citations remain. Conflicting records with the same ID raise an explicit source failure. No parent acceptance rule changed. Both previously failing evaluator tests then passed unchanged as part of the 33-test targeted run. The failed suite log is retained as pytest-initial.txt; expectations were not changed.

Final full suite: **1,413 passed, 0 failed in 473.76 seconds**. The affected test set separately passed 33 tests in 98.95 seconds. Existing test functions and expectations are unchanged (scope-integrity.json). Fresh-state 1,000-company runtime measurement is recorded in the close-out below.

## NAV jobs: no matching defect found

Bundled index built `2026-11-13T00:26:42.872674Z`: 9,296 ads, 5,899 distinct employer org numbers. **5,896 are registered subunits** in the cached official Bronnoysund subunit bulk. Comparing raw employer numbers directly with the parent-company universe gives **0 overlap**. After exact subunit ? parent mapping and deduplication, **2,116 universe parent companies** have indexed candidates:

`2,116 / 411,160 ? 1,000 = 5.146415` expected candidate companies per random 1,000, before expiry/live proof. `5,899 / 411,160 ? 1,000 = 14.347213` would mix subunit identifiers with parent companies and is not the correct rate.

Frozen cohort: **0 direct employer-ID matches ? 2 parent-mapped companies with indexed ads ? 1,000 companies with a hiring section attempted ? 2 companies publishing jobs**. Live recorded subunit scopes independently give the same two indexed companies. Both published their indexed ad:

| Parent orgnr | Company | Ad UUID | Outcome |
|---|---|---|---|
| 960213912 | ROSENLUND BARNEHAGE SA | a3e96411-9639-48cd-a27b-2e5e4406a3e8 | Published after HTTP 200 live detail; expires 30 November 2026 |
| 930202894 | NORLANDIA ENGA BARNEHAGE AS | c0349976-bbfc-41f4-a980-b482f06e5f2d | Published after HTTP 200 live detail; expires 26 November 2026 |

There are **zero indexed-candidate companies without a published job** in this cohort, so no indexed loss list is omitted. The report's `indexed_ads=4` is not four distinct jobs: index.ads stores each accepted ad under its employer subunit and parent; its metric sums both lists. It does not establish four unpublished candidates.

The forward-feed name fallback also inspected ROLIDBAKKEN FUS BARNEHAGE AS (991247610), UUID bdb50d18-4cdb-485f-a8cf-f861927dd9ca, employer subunit 931166492. Saved HTTP 200 detail says ACTIVE but `expires=2026-11-13T00:00:00+01:00`, before the run at approximately 14:00 UTC. It was correctly closed as expired, not lost to a matching error. It is not in the shipped active-index candidate set. NAV's check is sources/nav_cached.py, detail(): expiry <= now closes the ad. This exclusion has no family error because a successfully checked expired ad is not a source failure.

Stage G run 1 NAV: declared_index; feed complete, reason complete; three detail requests, seven total requests, 115.484 seconds; zero incomplete companies, cap hits or unchecked candidates; two published companies. Exact saved detail status, expiry and employer fields, source URLs and hashes are in nav-funnel.json. No NAV code changed.

Under a uniform random sample without replacement (N=411,160, K=2,116, n=1,000), the hypergeometric probability of at most two indexed parent companies is 0.1119307. Observing two is compatible with sample variation. The competitor's 10/1,000 extrapolated from one job company in a 100-company sample is also plausible; it does not establish an official-source matching defect here. Candidate presence is an upper opportunity, not a promise that an ad remains active.

## Evaluator path

A new local clone of main `1ea96a0` installed with `uv sync --frozen`. Runtime flags were exactly the requested seven: --organisations, --bulk, --output, --profiles-output, --report, --run-id, --expected-count; no feature, state or site flags. The `uv --frozen` switch is installation control, not an agent flag. Credentials were stripped from the child environment.

Exit **0**, **20 envelopes and 20 profiles**, report and nonempty offline site. Every company state complete; all 20 identities available; every published legal name exactly matches its CSV orgnr/name pair. The CSV SHA-256 equals `bulk_snapshot_sha256`; report registry provenance records 737 csv_cache claims and 2,468 live_verified claims. Thus bulk is honoured; it does not suppress official live roles/subunits/accounts. Site landed at `bench/cache/stage-p-evaluator/out/site/`. Wall 119.016 seconds; 122 HTTP, zero deadlines/warnings. Exact command, files, bytes, hash and identity checks are in evaluator.json. This is the pre-fix command-path control; the formatting patch does not touch CLI/bulk code.

## Scope and decision

Only sources/official_extra.py and additive official-extra tests change runtime/test code. Existing tests are not weakened. RA000473 remains a documented acceptance-rule proposal, not an implemented expansion. No website proof, NAV, scoring, budget, dependency, index or main changes; no push.


## Completed live measurement

Tested code commit: `588f356b3e9d56aa0d641383c4b5f45058370f3c`. Frozen input SHA-256 `7ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782`. Fresh empty state, documented README settings, no bulk override, credentials stripped. The code content was unchanged throughout the run; its commit was created while the run was executing. No new acceptance rules or budget changes.

| Metric | Stage G run 1 release | Stage P corrected live |
|---|---:|---:|
| Envelopes / profiles | 1,000 / 1,000 | 1,000 / 1,000 |
| GLEIF companies | 32 | **139** |
| Direct GLEIF claims | 160 | **695** |
| Websites | 113 | 112 |
| Social companies | 47 | 47 |
| Job companies | 2 | 2 |
| Activity companies | 1,000 | 1,000 |
| News companies / article claims | 7 / 69 | 7 / 69 |
| TED award companies | 0 | 0 |
| Distinct supported facts | 165,481 | 166,042 |
| Total HTTP / mean per input | 9,281 / 9.281 | 9,309 / 9.309 |
| Maximum attributed HTTP/company | 40 | 40 |
| Wall seconds (including finalisation) | 2,136.969 | 1,678.390 |
| Seconds per 100 | 213.697 | 167.839 |
| Deadline hits / warnings | 0 / 0 | 0 / 0 |

Exit 0; **107 gained GLEIF companies, zero GLEIF companies lost**. The gained org numbers, legal names and LEIs are in gleif-published-gains.json. The runtime result confirms the isolated matching measurement. Total fact-count difference is +561: +556 GLEIF claims (+535 direct and +21 relationship claims), +8 activity facts, -3 website-family facts. Accounts, roles, subunits and hiring claim counts are unchanged. This is not a claim that all run differences are caused by the patch.

The only lost website is ENSURE IT AS (934620011): registry candidate ensure-it.eu recorded `website_timeout`; the family recorded `website_source_unavailable` / "A candidate source could not be checked". This primary website collection happens before shared GLEIF collection, and no website code changed. No website acceptance was changed to recover it. No website companies were gained. The exact candidate diagnostics and old published value are retained in unrelated-live-differences.json.

Current NAV: **declared_index**, **69.391 seconds**, **8 requests**, **2 matched/published job companies**, **0 incomplete companies**, reason complete. No NAV fix was justified or applied. GLEIF/TED shared-source metrics: 139 GLEIF companies, 13 parent LEIs batched, 265 requests total; TED 230 requests (15 HTTP 200, 215 HTTP 202), still 0 published awards. TED logic is unchanged. These two live runs were made on different dates/transport conditions; the wall-time difference is not evidence of a causal speed improvement.

Offline site completed for all 1,000 companies: state available, 1,002 landing/profile pages plus 2,734 evidence pages; largest HTML 239,582 bytes; zero warnings. See execution.json and benchmark-comparison.json. Runtime files remain under ignored bench/runs/stage-p-whitespace/.

Final-code clean-clone seven-flag recheck also **PASS**, at commit `588f356b3e9d56aa0d641383c4b5f45058370f3c`. Exit 0; 20 envelopes, 20 profiles, 20 complete companies, all 20 identities available, zero CSV orgnr/legal-name mismatches; bulk SHA-256 matches the report; report and nonempty offline site produced at `bench/cache/stage-p-evaluator-final/out/site/`. No site/state/feature flags were passed. Wall 108.219 seconds, 122 HTTP, zero deadlines/warnings. See evaluator-final.json for the exact command and evidence. This repeats the pre-fix control on the final tested code.
