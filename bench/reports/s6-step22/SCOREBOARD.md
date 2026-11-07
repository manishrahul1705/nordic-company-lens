# S6 Step 22 - fresh-sample precision guard

Started from `b3fe202e8ae6a29ef8085af930d53f167969f918`. Step 21 stop report committed first as `032e09c1`. Search OFF, application credentials stripped, no push. No new discovery source or HTTP request type.

## New cohort

SystemRandom selected eight accessible BRREG search-result pages (page window 1-99), then 100 distinct checksum-valid identifiers from 700 eligible records, excluding 8,279 identifiers found in all existing bench inputs/reports and cached official cohort files. Known-cohort overlap: zero. Added NOT-AN-ORGNR, invalid-checksum 123456789 and a whitespace-only line. This is a sample from the accessible API page window, not a uniform sample of the entire registry.

Input SHA-256: `bfb099ad3ca3a50b6edbd423687dd3dee3012f4ff13f648abf4f8276ffebc8ac`. [Selection, page URLs/hashes and company names](selection.json), [input](orgnrs.txt), [retained raw selection pages](selection-source/).

## Initial pinned-runtime pair

Fresh clone pinned to b3fe202, uv sync --frozen, literal README command twice with the same new state directory:

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --profiles-output out/profiles.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

| Run | Seconds | HTTP | Envelopes/profiles | Deadlines | Company changes | Observations | Strict exit |
|---|---:|---:|---:|---:|---:|---:|---:|
| First | 258.531 | 781 | 103/103 | 0 | 0 | 0 | - |
| Refresh | 390.500 | 765 | 103/103 | 0 | 0 | 1 | 1 |

The one observation concerns 21-5 / 917357439: a retained description's supporting page was not checked as a website page during refresh. This is an unchecked-page observation, **not proven to be a genuine changing external response**. The strict failure is preserved and not presented as a pass. That site's doubtful attribution is independently corrected below. [Original execution/verifier](official-run/), [observation](observation-changes.json), [original output hashes](original-output-hashes.json).

Coverage among 100 valid inputs (both initial runs): identity100, people96, subunit workplaces72, accounts42, websites6, social companies4, jobs2, activity100, GLEIF1 company/5 claims, TED0. Supported facts8,978. Max HTTP/company31 then36; mean7.81 then7.65 per valid company (invalid rows make the per-input mean lower). No warnings/deadlines. The three invalid lines each emitted one failed result. [Exact states](coverage.json).

## Review and narrow fixes

[Item-by-item review](REVIEW.md), [raw source spans/locators/values and sentence citations](review-ledger.json): every website/social link (11 claims), every GLEIF field (5), every job (2), ten random claims each from identity/roles/subunits/accounts/registry announcements (50), and ten primary briefings (40 sentences). No TED award was present to review. All sampled blobs were SHA-256 checked. No sample was replaced.

Two website/social items were initially doubtful: the NUF named 21-5 has a Danish registered HQ, while the site's contact footer names **21-5 Norge AS**, a different full publisher name. A legal-name substring plus the parent's street is insufficient to establish exact-entity publication. The generic footer rule now compares full legal-name cores, not substring containment. Own-publisher prefixes and explicitly credited suppliers remain supported. It also applies during final carried-forward publication checks. Eight derived site claims are withheld, including the website and LinkedIn; the website becomes ambiguous. No company-specific exception.

Seven sampled financial claims had correct amounts/periods and exact BRREG support, but also cited TOMRA/Aker calibration excerpts. Those other-company excerpts describe methodology and cannot support this company's amounts. The generic correction removes them from account claim citations; **all numeric values, existing unit annotations, periods and claim IDs remain unchanged**. Exact-company BRREG evidence remains. No claim value is inferred from calibration data.

Offline replay of affected new-sample companies only: 42 financial companies plus the one website company, 43 per snapshot; zero HTTP. Corrected 2,626 financial claim citations per snapshot. Final sample projection: websites5, social companies3, jobs2, GLEIF1, TED0, activity100; facts8,970. Independent verifier: 103 schema-valid lines, 8,970 supported facts, 328 source blobs, 433 primary sentences, zero unverified values. The initial observation is retained honestly; it was not erased to claim strict success. [Replay](offline-replay.json), [independent verification](offline-verification.txt).

Final retained reviewed items: zero wrong, zero doubtful. The original doubtful verdicts and corrective dispositions remain in the ledger rather than being relabelled as originally correct.

## Frozen-1000 regression replay

The user's pre-commit guard check uses the saved final Step 20 enrichment projection of run `20261107T073418068646Z-42def8c`, with its original state blobs; no crawl.

The first guard draft would have withheld one valid company: CONTROL SOLUTIONS AS / 926490060. Hand inspection confirms its exact orgnr926490060, own contact address and the existing permitted singular/spaced title variant. The guard was narrowed to reuse the existing exact-own-orgnr name normalization, rather than removing that legitimate proof. A generic positive/negative regression covers this case; there is no company allowlist.

**Final footer guard: 110 websites before, 110 after; zero sites withheld.** Every newly withheld-site candidate (one in the first draft) was hand-checked; the corrected rule preserves it. [Initial source review](frozen-guard-review.json), [final all-110 replay](frozen-guard-final.json).

The calibration correction is also replayed across the saved frozen cohort. Exact financial value/ID comparisons, full independent verification and final-runtime fresh-clone results follow below. Original source/output bytes remain retained; no new 1000 crawl.


Frozen citation replay completed: **996 affected financial companies; 63,122 claim citations corrected; zero HTTP**. Compared all 98,162 account-family claims including absence markers: **zero financial value changes, zero financial claim-ID changes, zero reporting-period changes**. All 1,000 companies' complete claim-ID sets are identical. Final supported facts166,222, websites110, social44, activity1,000, jobs3. Independent verifier passed: **1,000 schema-valid lines, 166,222 supported claims, 4,113 source blobs, 5,053 cited primary sentences, zero unverified values**. The two removed blob references are the unrelated calibration fact records; original raw evidence remains preserved. [Identity comparison](frozen-financial-identity.json), [replay ledger](frozen-offline-replay.json), [verifier](frozen-verification.txt).


## Final-runtime tests and live replacement review

Final exact-runtime full suite: **1,244 passed in 339.05 seconds**; focused suite: **35 passed in 1.06 seconds**. Earlier logs retain the first draft's two own-publisher-prefix failures, which were fixed without changing those existing expectations. The initial 1,243-test suite and the intermediate 1,244-test suite are build history; the pinned final suite includes the own-orgnr normalization correction. [Final full suite](pinned-final-full-tests.txt), [focused regressions](guard-final-tests.txt).

The fresh clone is based on b3fe202 with the exact pending fixed-runtime patch copied in before execution (the user requested validation before committing). SHA-256 for every copied source/test/document file is recorded in [source manifest](fixed-runtime-source.json), and the [complete patch](fixed-runtime.patch) is retained. Final workspace/clone bytes are compared again before commit; no claim is made that the uncommitted patch was already in the clone's Git HEAD.

The first fixed live run rejected the doubtful 21-5.no footer and subsequently verified **21-5.com** instead. This new saved page's CONTACT publisher is **21-5 A/S**, Christianshusvej187-189, Denmark; BRREG's explicit HFOR role names **21-5 A/S / 917464456** as this NUF's head enterprise, and the subject's registered street is Christianshusvej187. This is exact registered foreign-enterprise attribution, not reuse of the different Norwegian AS's page. The LinkedIn URL is linked from the verified .com page. Both replacement website/social items were hand-reviewed as correct; no exception or new acceptance rule was added. [Raw footer, registry HFOR record, claims and hashes](fixed-live-delta-review.json). The previous doubtful .no source and its withheld projection remain preserved separately.


## Final fixed-runtime fresh-clone pair

[Literal-command check](fixed-official-run/RESULTS.md): fresh clone plus exact tested source patch, clean new state on the NEW Step22 cohort. **336.360 seconds / 788 HTTP**, then **175.704 seconds / 753 HTTP**; **103 envelopes/profiles each, zero deadlines, zero company changes, zero observation changes; unmodified strict verifier exit0**. All 100 valid-company primary briefing texts are stable. The ten reviewed briefing texts remain unchanged. Source-file hashes match final workspace bytes exactly. [Source integrity](final-source-integrity.json).

No new 1000 crawl was performed. The frozen replay is entirely offline. Final runtime changes are limited to the full-publisher guard (with existing own-orgnr normalization retained) and removing unrelated calibration claim citations, with regressions and documentation. Final commit authored/committed as Manish Rahul <manishrahul1705@gmail.com>; full hash reported in the response. No push.

Final live sample coverage (both fixed-runtime runs): **6 websites, 4 social companies, 2 jobs, 100 activity companies, 1 GLEIF company/5 claims, 0 TED awards; 8,974 supported facts**. People96, subunit workplaces72, accounts42; max HTTP/company31. The correctly matched .com replacement explains why final live coverage exceeds the earlier saved-only projection. Final verifier checked330 blobs and433 primary sentences, with zero unverified values.
