# S6 Step 11 — recall round 2

**KEEP the reviewed name-based nominations, corroborated unique `.no` rule, bounded proof discovery and linked-board jobs capability. Reject the new contact-only email/subunit Tier B extension and the expanded all-role-holder inference.** No company-specific exceptions. Search OFF, application credentials stripped, no push.

Exactly one completed 1000-company benchmark: `20261106T102032689035Z-f774483`, source `f774483`. C: had **14.222 GB** free before launch. Frozen batch and registry hashes match Step 10. The execution marks the working tree dirty because the offline reporting helper changed; runtime source was committed before launch.

| Section | Step 10 final baseline | Step 11 measured trial | Kept saved-evidence projection |
|---|---:|---:|---:|
| Identity | 1000 | 1000 | 1000 |
| People | 997 | 997 | 997 |
| Subunit workplaces | 774 | 774 | 774 |
| Typed location profiles | 997 | 997 | 997 |
| Financials | 999 | 999 | 999 |
| Website | 93 | 108 | **103** |
| Social | 40 | 41 | **41** |
| Jobs | 3 | 3 | **3** |
| News/activity | 235 | 236 | **236** |

The kept column removes five unsupported links from the measured trial using final policy and retained bodies. It is **not a second crawl**, a remeasured final-source timing, or a claim that replacement candidates were tried. There are 14 retained new-company websites and four baseline website losses, giving net +10; five additional existing website proof/URL values changed. The 120+ target is not reached. No other section drops.

## Funnel per rule

| Rule | Candidates | Fetched | Trial accepted | Kept after review |
|---|---:|---:|---:|---:|
| A Registry email domain | 117 | 69 | 15 | 11 |
| B Registered subunit homepage/email | 8 | 5 | 1 | 1 |
| C Exact legal-core `.no` | 713 | 181 | 9 | 9 |
| D Additional proof-page discovery | 79 | 79 | 1 | 1 |
| E Careers / linked ATS URLs | 38 | 38 | 0 | 0 |
| F New-site social/news extraction | 19 | 19 | 4 companies / 7 items | 4 companies / 7 items |

These are overlapping nomination cohorts, not separate causal ablations. A/B include nominations that passed stronger existing orgnr/contact proof; they are not all newly added websites. C counts exact `.no` nominations, including ones that never acquired corroboration. D counts hosts with additional HTML proof fetches; an acceptance requires the selected proof URL to be newly discovered rather than an old fixed path. E counts checked URLs, including cached pages, not unique HTTP requests. F's candidates are trial new-company websites; the five rejected link-only sites supplied no retained social/news. Fourteen of those 19 website links survive review. [Machine-readable funnel](funnel-final.json).

All 29 previously removed unique-name trial sites were rechecked against captured pages and complete saved BRREG name queries. [Individual outcomes](UNIQUE_29.md) and [hashes](unique-29-review.json). The live trial accepted nine C sites; the saved old-page eligibility exercise is not a live result.

## Precision review and rejected sub-rules

[Every new or changed website/social item](REVIEW.md), with [proof excerpts, dates, SHA-256 and verdicts](review-items.json): 24 website values/proofs plus five social URLs; no new job claims. Retained: **24 correct items, zero wrong-company items**. Withheld: GLOA→AS Betongbygg is definitively wrong; INFLOW→Simply.tv, Deigen→Credor, Nordic Production Group→npg.ee and Straumsnes→Ice Drift lack sufficiently resolved exact-entity proof.

Shared registered street/postcode admitted unrelated operating/group businesses. Consequently the whole new contact-only email/subunit declaration extension is removed. Name-based email/subunit Tier A remains. Broadening role proof from registered director/chair to all board members admitted a global site through a shared MEDL; that broadening is removed. Carried-forward snapshots cannot restore either rejected inference. Prefix `AS Betongbygg` is explicitly recognized as a different publisher.

The four baseline website losses are not labelled transient: KN Elektro and Lofotposten encountered an overstrict new footer-string veto; the own-publisher-prefix regression is fixed and tested, but their unmeasured recoveries are not added to 103. Control Solutions has a differing `CONTROL SOLUTION AS` title alongside its own spaced organisation number; the trial abstained. GS Elektro Gjøvik's frozen registry name contains a replacement character and disagrees with the page's legal spelling, so the conservative identity veto remains. These limitations are not counted as proof of another company or hidden inside a noise allowance.

Jobs remain three verified NAV ads. The 38 company-site URLs across 21 companies yielded zero newly proved ACTIVE individual ads. [Every inspected URL and reasons](JOBS.md). HTML-only/undated career postings remain a recall limitation; zero accepted does not mean zero vacancies.

## Requests, time and validation

Measured trial: **513.677 seconds**, **6130 HTTP**, max **33/company**, mean **6.091 attributed / 6.130 amortized**, 39 shared requests; 1000 envelopes and profiles, no deadlines or warnings. Global ceiling 18,000 HTTP / 1000; per-company ceiling 40; configured 2400-second budget remained tighter than the scaled hard limit. Search calls 0, LLM calls 0, cost $0. DNS fallback: 5226 attempts, 10 recovered domains, 1136.219 aggregate seconds, max 9.781 seconds/company. Aggregate concurrent DNS time is not wall time. [Exact metrics and execution](metrics.json).

NAV's bundled index plus complete public feed remained active; 11 live detail requests produced the unchanged three ads. The public token was fetched in memory; no personal credential was provided or committed.

Full suite: **1051 passed in 314.24s**. Focused reviewed-rule suite: **92 passed**; final own-publisher-footer regression suite: **44 passed**. The full-suite process began before the last footer-only adjustment; the final focused suite specifically covers that adjustment. [Full suite](final-full-tests.txt), [reviewed tests](reviewed-tests.txt), [final footer tests](footer-tests.txt).

Independent retained-projection verifier: **1000 lines**, schema valid, **111002 published claims**, **4017 source blobs**, **8415 cited synthesis sentences**, **0 unverified values**. [Verifier output](kept-verification.txt). The measured raw trial also passed schema/evidence verification; that check does not establish attribution precision.

Final-source fresh-clone literal README command, twice with the same state and no `--previous`: [official-run results](official-run/RESULTS.md). Final report commit contains the exact metrics and strict pairwise verification.

Source commits: `f774483` recall trial; `395249c` rejected inference removal and carried-snapshot guard; `d81b45e` own-publisher-prefix regression. Reporting-only commit follows. All authored/committed as Manish Rahul <manishrahul1705@gmail.com>. No push.
