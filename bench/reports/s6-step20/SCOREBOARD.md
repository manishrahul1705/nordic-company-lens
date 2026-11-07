# S6 Step 20 - official enrichment and declared-domain state

Started from `1627e59c684c2f049ead6c7232d0f03ccb7a3bb2`. Search OFF, application credentials stripped, no personal keys, no push. Final runtime: `34e0a70eaf80e528478e60b9412fdaebaf29d455`.

## Verified sources and implementation

[Source verification](SOURCE_VERIFICATION.md) records official ownership, licence, robots/API rules and ten-company samples. GLEIF is CC0 1.0 and allows anonymous exact registeredAs + RA000472 matching. The ten-company sample had zero matches; the full frozen cohort had 32, meeting the 15-company gate. Parent records are fetched in one deduplicated LEI batch only for explicitly proven ACTIVE parent relationships of exact-orgnr matches. Three parent claims were supported. Foreign registration identifiers are never labelled Norwegian orgnrs.

TED is the EU Publications Office's anonymous published-notice API under its legal notice/Commission reuse policy. Exact winner/buyer IDs and XML settled-contract/tender/party chains are required. Award dates must be within 36 months, maximum ten per company. Doffin was excluded: a supported keyless API and clear access/reuse terms were not verified. No application keys were harvested.

GLEIF claims are labelled GLEIF; awards are labelled Public procurement award, separate from company news and registry announcements. Only a uniquely linked tender amount is published; no notice-wide total is assigned to a winner. Fourteen awards have amounts, six omit them. Three source amounts are literally NOK 1; these are reported tender values, not estimates of expenditure. No conversions or allocations are invented.

A first-ever strong declared-domain check with complete apex/www NXDOMAIN now yields not_available, reason "declared domain does not exist". Mixed failures/timeouts/TLS remain failed. A previously VERIFIED website retains stale supported claims/evidence on refresh NXDOMAIN; its original regression assertion is unchanged. Optional TED 406/503 failures cannot fail registry or website sections; supported prior optional claims carry forward stale.

## Measurement and retained evidence

One completed frozen-1000 crawl: `20261107T073418068646Z-42def8c`, 809.263 seconds and 8,587 HTTP. Its 75 TED XML requests returned 406 because the shared JSON Accept header was inappropriate. This result is preserved, not silently replaced. An earlier stopped incomplete attempt is [excluded](excluded-attempt.json).

The user-approved enrichment-only continuation reused the original pooled budget, request ledger, company caps and deadline. It made 99 additional official-source requests, including 75 XML responses returning 200 after the header repair. No BRREG, NAV or company website crawl was repeated. Source acquisition took 101.516 seconds; the entire continuation including offline export took 286.031 seconds. Cumulative elapsed time was 1,355.541 seconds, including debugging idle time; this is not a pristine final-runtime end-to-end 1000 timing.

The amount parser was then corrected for eForms LegalMonetaryTotal/PayableAmount. Saved XML was re-extracted offline with zero HTTP; 14 compound award values/IDs gained their supported amounts, with the same twenty awards. Pre-correction derived outputs remain compressed with SHA-256. [Amount projection](amount-projection.json), [execution](benchmark-execution.json). Original crawl output hashes remain unchanged: [integrity check](integrity.json).

| Metric | Step 18 | Step 20 final saved projection |
|---|---:|---:|
| GLEIF companies / claims | 0 / 0 | 32 / 163 |
| Explicit parent claims | 0 | 3 |
| Procurement companies / awards | 0 / 0 | 6 / 20 |
| Websites | 109 | 110 |
| Social companies | 44 | 44 |
| Jobs companies | 3 | 3 |
| Activity companies | 1,000 | 1,000 |
| Supported facts | 166,032 | 166,222 |
| Website failed | 8 | 2 |
| Website not_available | 759 | 764 |
| HTTP total | 8,467 | 8,686 |
| Mean HTTP/input | 8.467 | 8.686 |
| Max HTTP/company | 40 | 40 |
| Deadlines | 0 | 0 |

All initial failed XML requests count in 8,686. Increase: 219 requests / 2.59%, below the 9,313 ceiling. There were 198 cumulative optional-source calls across the two phases, within the source cap of 300; the global 18,000 cap remained intact. Each phase used one batch for two parent LEIs, with three relationship-proof requests. Seven declared-absence diagnostics include one company already ambiguous. Six former failed website states became not_available; one former not_available website recovered.

The single newly available website, Konseptbygg Eiendom AS, has its exact orgnr in saved contact-page text. Its previous robots 502 recovered; no enrichment website-nomination rule caused this gain. Zero new social URLs. [Website delta](website-social-delta.json). C: had 7.489 GiB free before the completed crawl, exceeding 5 GiB.

## Precision and validation

[Review](REVIEW.md): 20 seeded GLEIF field claims, all three parent claims and all twenty procurement awards checked against raw records: zero wrong-company items, values or dates. All fourteen amounts were independently checked against linked tender fragments. No sample was replaced. TED API nominations include unmatched/non-award candidates; 75 fetched notices do not mean 75 published awards.

Independent verification: 1,000 schema-valid lines, 166,222 supported facts, 4,115 checked source blobs, 5,053 cited primary sentences, zero unverified values. [Verifier](verification.txt). Non-activity fact families: identity 31,170; roles 17,806; subunits 6,907; accounts 97,416; website 820; hiring 3. Activity claims: 12,100.

The final-runtime suite before shutdown passed 1,239 tests in 288.29 seconds. A shutdown-affected fresh-clone refresh is preserved separately: zero company changes, 97 observation changes, strict exit 1, with 2,659.203 seconds elapsed on run two. It is not accepted as the final refresh check. The resumed validation uses a new clone and new state; its exact results follow in official-run/RESULTS.md.

Source terms are recorded in docs/SOURCES.md and SUBMISSION.md. All commits use Manish Rahul <manishrahul1705@gmail.com>. No push.

Resumed validation: focused tests **18 passed in 4.51 seconds**; full suite **1,239 passed in 390.01 seconds**. The only pending code difference was an offline projection-helper profile mirror repair; production runtime stayed at the final amount-parser commit. [Focused log](resume-focused-tests.txt), [full log](resume-full-tests.txt).

## Final fresh-clone pair

[Exact README pair](official-run/RESULTS.md): 103 envelopes/profiles per run, **262.579 seconds / 757 HTTP**, then **210.938 seconds / 742 HTTP**. **Zero company changes, zero observation changes; strict verifier exit 0**. Both TED API requests returned 200, not 406; this cohort nominated no XML notices. The final runtime ran end to end, with zero warnings/deadlines and successful site exports. The 75 XML 200 responses belong to the bounded 1000 continuation. No verifier relaxation.
