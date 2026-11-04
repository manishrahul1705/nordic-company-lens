# Improvement log

Available counts use canonical scoreboard states, ordered as identity / people /
locations / financials / website / social / jobs / news/activity. A baseline's
before value is not measured. `checked/wrong` must describe its audit scope;
coverage alone is not a wrong-company check. Log every accepted or rolled-back
change against the same frozen cohort, preserving its scoreboard and state.

| Date | Commit | Feature ID | Change | Per-section available before → after | Website budget-exhausted companies | Wrong-company check (checked/wrong) | Decision | Reason |
|---|---|---|---|---|---:|---|---|---|
| 2026-11-04 | `f409645` | BASELINE | Fixed 100-company benchmark; no production changes | not measured → 100/100/85/100/8/4/1/4 | 26 | 100 companies / 0 wrong-company claims (stored-source audit) | KEEP | Frozen reference; 100 envelopes, exit 0; coverage matches comparison D exactly. |
| 2026-11-04 | `ce486e0` | F1 | Separate absent speculative domains from known-source failures | 100/100/85/100/8/4/1/4 → 100/100/85/100/8/4/1/21 | 27 | 17 source items opened / 0 wrong | KEEP | No available-count drops; 692 tests passed; exact-company source review passed. |
| 2026-11-04 | `30976c6` | F8 | Keep complete registry facts available with separate website-news diagnostics | 100/100/85/100/8/4/1/21 → 100/100/85/100/8/4/1/30 | 26 | 9 source items opened / 0 wrong | KEEP | No available-count drops; 696 tests passed; exact-company source review passed. |
| 2026-11-04 | `9e5b7f0` | NAV-INACTIVE | Reconcile settled repeated-INACTIVE headers only with live closure proof | 100/100/85/100/8/4/1/30 → 100/100/85/100/8/4/1/30 | 26 | 1 source items opened / 0 wrong | KEEP | No available-count drops; 702 tests passed; exact-company source review passed. |
| 2026-11-04 | `a1aca18` | S4-A | Require fetched article publication proof; remove ten invalid sitemap news items | 100/100/85/100/8/4/1/30 → 100/100/85/100/8/4/1/29 | 27 | 10 source items / 0 wrong | KEEP | 713 tests passed; 49.994s, 612 HTTP; `bench/runs/20261103T194705253964Z-a1aca18` |
| 2026-11-04 | `6fe34a3` | S4-B | Expand ordered scoped nominations; coverage unchanged under existing HTTP caps | 100/100/85/100/8/4/1/29 → 100/100/85/100/8/4/1/29 | 29 | 4 source items / 0 wrong | KEEP | 727 tests passed; 60.139s, 621 HTTP; `bench/runs/20261103T195713751340Z-6fe34a3` |
| 2026-11-04 | `6085648` | S4-C | Strict ownership trial exposed wrong-company Diseth social link for Rolidbakken FUS; reverted entire fix | 100/100/85/100/8/4/1/29 → 100/100/85/100/10/7/1/29 | 22 | 6 source items / 1 wrong | ROLLED BACK | 737 tests passed; 53.378s, 619 HTTP; `bench/runs/20261103T200935641161Z-6085648` |
| 2026-11-04 | `e54da86` | S4-D | 14/18 caps reduced budget errors but exposed wrong-company Diseth social link; reverted | 100/100/85/100/8/4/1/29 → 100/100/85/100/9/5/1/29 | 8 | 2 source items / 1 wrong | ROLLED BACK | 727 tests passed; 57.891s, 784 HTTP; `bench/runs/20261103T201627607521Z-e54da86` |
| 2026-11-04 | `3c98640` | S5-1 | Require exact company social handles and shared-template scope; drop cross-company profiles | 100/100/85/100/8/4/1/29 → 100/100/85/100/8/3/1/29 | 29 | 3 items / 0 wrong | KEEP | 732 tests; 50.177s, 623 HTTP. Full social review 3/0; two unsupported brand handles removed under explicit precision rule |
| 2026-11-04 | `4cd4892` | S5-2C | Reapply strict ownership C after social root-cause fix | 100/100/85/100/8/3/1/29 → 100/100/85/100/10/5/1/29 | 22 | 8 items / 0 wrong | KEEP | 742 tests; 51.683s, 617 HTTP. All five social items and three website changes reviewed; Diseth absent; no count drops |
| 2026-11-04 | `d41ea10` | S5-1b | Track observed social profiles across verified companies including language-scoped paths | 100/100/85/100/10/5/1/29 → 100/100/85/100/10/5/1/29 | 22 | 5 items / 0 wrong | KEEP | 744 tests; 46.617s, 618 HTTP. All social items reviewed; no count drops |
| 2026-11-04 | `3240e5b` | S5-2D | Reapply 14/18 website caps after social fixes | 100/100/85/100/10/5/1/29 → 100/100/85/100/11/5/1/29 | 2 | 6 items / 0 wrong | KEEP | 744 tests; 50.961s, 745 HTTP. All social items plus new Orje website reviewed; budget errors 22 to 2; no count drops |
| 2026-11-04 | `c1ca5df` | S5-3 | Read-only F17 website-loss table and complete company diagnostics | 100/100/85/100/11/5/1/29 → 100/100/85/100/11/5/1/29 | 2 | 5 items / 0 wrong | KEEP | 744-full+3-analyzer tests; 49.153s, 741 HTTP. No runtime changes; largest missing-site bucket DNS guesses; compare historical scale caps separately |
| 2026-11-04 | `e9ebb73` | S5-4 | Add exact-org batched Wikidata nominations and CC0 name-matched social source | 100/100/85/100/11/5/1/29 → 100/100/85/100/11/5/1/29 | 2 | 5 items / 0 wrong | KEEP | 753 tests; 61.377s, 747 HTTP. HTTP 200 empty bindings for 100; zero matches and no coverage change; all social reviewed |
| 2026-11-04 | `e8f8467` | S5-4-scale | 1000-company checkpoint includes restored C/D and social fixes plus Wikidata | 1000/998/774/999/52/27/3/230 → 1000/998/774/999/73/33/3/232 | 24 | 109 items / 0 wrong | KEEP | 753 tests; 291.317s, 6592 HTTP. All 51 social, 38 changed websites and 20 articles opened; 9 Wikidata matches, 5 CC0 socials, zero WD-origin verified websites; not isolated C/D attribution |
| 2026-11-04 | `66cdb5d` | S5-1c | Revalidate social attribution after refresh and track aliases/all observed contexts | 100/100/85/100/11/5/1/29 → 100/100/85/100/11/5/1/29 | 2 | 5 items / 0 wrong | KEEP | 761 tests; 56.675s, 743 HTTP. All five social items reviewed; no count drops; independent auditor and furthest-stage reporting corrected |
| 2026-11-04 | `18d31aa` | S5-5 | Restrict sameAs to attributable Organization/LocalBusiness records on verified sites | 100/100/85/100/11/5/1/29 → 100/100/85/100/11/5/1/29 | 2 | 5 items / 0 wrong | KEEP | 772 tests; 53.128s, 745 HTTP. All five social items reviewed; existing broad sameAs path tightened; no count drops |

Baseline artifact: `bench/runs/20261103T183536297367Z-f409645/scoreboard.json` (ignored local run; retain or upload the run directory). Measured wall time 47.052 seconds, HTTP requests 610, latest-year accounts 100, deadline hits 0, warnings none. The earlier D run used 609 HTTP requests and 62.081 seconds; this live rerun made 256 website requests versus 255 because connection/redirect fallback outcomes changed. Registry requests stayed 302 and NAV requests stayed 52; no coverage or distinct-fact totals changed.

Counting parity was also verified directly against D's saved outputs for every canonical/exported state and distinct-fact total, not only the five headline counts. The existing offline audit examined 100 companies and 11,053 available claims: 10,983 correct, 0 incorrect, 70 unverifiable activity claims, and 0 wrong-company findings. This is agreement with stored sources, not fresh independent live verification. The output verifier passed membership, schemas, evidence and synthesis checks. GitHub Actions was not dispatched. The benchmark harness was clean at the recorded commit.

F1 evidence: `bench/runs/20261103T184623325670Z-ce486e0/` contains the scoreboard, raw source state, complete newly available item list and opened exact-company proofs in `newly-available-review.json`. Test count: 692.

F8 evidence: `bench/runs/20261103T185130143467Z-30976c6/` contains the scoreboard, raw source state, complete newly available item list and opened exact-company proofs in `newly-available-review.json`. Test count: 696.

NAV-INACTIVE evidence: `bench/runs/20261103T190201769481Z-9e5b7f0/` contains the scoreboard, raw source state, complete newly available item list and opened exact-company proofs in `newly-available-review.json`. Test count: 702.

## S3 Windows scale check

One default-budget 1000-company run at `73d5b5f`: exit 0, 1000 envelopes,
358.241 seconds of the 2400-second budget (14.93%), 5613 HTTP requests of 20000,
zero deadline hits and no warnings. No output-limit reductions occurred.
Available counts: 1000/998/774/999/51/25/3/234. Website budget-exhausted: 303.
The 1000 cohort begins with the frozen 100; all 100 retain available accounts.
The current registry bulk matched 998 inputs; the other two used live fallback.

One accounts failure: `926077422` (NRP ANAXO NORDIC M2, VPFO). All three
accounts attempts returned HTTP 500 with message
`Regnskapet inneholder en oppstillingsplan som ikke er stottet (VPFO)`.
This is an unsupported source-side accounts layout, not a 429 or transport
timeout. Accounts request statuses were 999 × HTTP 200 and 3 × HTTP 500;
no accounts transport errors were recorded. No accounts fix was made.

Artifacts: `bench/runs/20261103T190729469739Z-73d5b5f/scoreboard.json`,
`scale-diagnosis.json`, `S3_REPORT.md`, and the original report/state bodies.
The scale check also retains three incomplete hiring sections; feed coverage
finished, with a detail-cap hit recorded. These were not generically suppressed.

The NAV fix's first live trial exposed an additional in-flight ordering case.
Its final implementation handles settled work at finalization as well as header
arrival. The final benchmark has zero failed hiring sections at 100 companies,
and no new vacancy is published for ARCTIC GRILL. The final suite passed 702 tests.

## S4-A removed website-news items

All ten used sitemap lastmod as a publication date and a URL-derived title, without fetched article proof. No valid website publication claim was removed. The 70 registry activity facts remain unchanged. Ten kept registry activity source records were opened and matched to their exact company/subunit; there were no kept website-news items to open.

- `986739874` https://www.aasbetong.no/aktuelt/nye-blomsterkasser-i-vart-sortiment — sitemap lastmod is not a publication date; title came from URL.
- `986739874` https://www.aasbetong.no/aktuelt/undergang-til-lauvasen-boligfelt — sitemap lastmod is not a publication date; title came from URL.
- `986739874` https://www.aasbetong.no/aktuelt/redi-stottemur-natural — sitemap lastmod is not a publication date; title came from URL.
- `986739874` https://www.aasbetong.no/aktuelt/redi-blomsterurne — sitemap lastmod is not a publication date; title came from URL.
- `986739874` https://www.aasbetong.no/aktuelt/produkter-levert-i-smasekk — sitemap lastmod is not a publication date; title came from URL.
- `986739874` https://www.aasbetong.no/aktuelt/nytt-veikryss-ved-ase-alesund-sykehus — sitemap lastmod is not a publication date; title came from URL.
- `986739874` https://www.aasbetong.no/aktuelt/grunnarbeid-er-avgjorende-for-et-godt-resultat — sitemap lastmod is not a publication date; title came from URL.
- `986739874` https://www.aasbetong.no/aktuelt/aas-prima-terrassehelle — sitemap lastmod is not a publication date; title came from URL.
- `928657523` https://www.vivify.no/nyheter/vivify-bygginnredning-finnmark — sitemap lastmod is not a publication date; title came from URL.
- `928657523` https://www.vivify.no/nyheter/vivify-kjoper-roommejts-i-sverige — sitemap lastmod is not a publication date; title came from URL.

## S4 final scale check

A/B retained; C/D reverted for the Diseth/Rolidbakken wrong-company social item. Target 25/100 not reached; accepted website coverage remains 8/100. Final tests: 727 passed. Final 1000 run `bench/runs/20261103T202127107708Z-9fa975e`: exit 0, 1000 envelopes, 311.321s, 5676 HTTP requests, 0 deadline hits, 312 website budget errors. See ignored `S4_REPORT.md`, scoreboard, raw source state and precision review in that run.

Scale precision scope: ten changed website proof items opened, zero wrong-company findings in that sample; not a full-cohort manual audit. All 596 registry activity facts persisted (equivalent timezone serialization normalized); 33 unsupported sitemap-date news items removed. The one accounts failure is unchanged: BRREG HTTP 500 on three attempts for 926077422, unsupported VPFO layout, with no accounts 429 or transport errors.

S5-1 evidence: `bench/runs/20261103T203539261283Z-3c98640`. Full social and new website/news source list: `s5-review.json`.

Social items rejected by stricter attribution in this step:
- `919653477` https://www.linkedin.com/company/vokser-group — handle does not match a registered company/subunit name.
- `991368000` https://www.instagram.com/studioralstonbau — handle does not match a registered company/subunit name.

S5-2C evidence: `bench/runs/20261103T204015696246Z-4cd4892`. Full social and new website/news source list: `s5-review.json`.

S5-1b evidence: `bench/runs/20261103T204509504774Z-d41ea10`. Full social and new website/news source list: `s5-review.json`.

S5-2D evidence: `bench/runs/20261103T205132975943Z-3240e5b`. Full social and new website/news source list: `s5-review.json`.

S5-3 evidence: `bench/runs/20261103T205448475112Z-c1ca5df`. Full social and new website/news source list: `s5-review.json`.

S5-4 evidence: `bench/runs/20261103T210508740261Z-e9ebb73`. Full social and new website/news source list: `s5-review.json`.

S5-4-scale evidence: `bench/runs/20261103T210757525212Z-e8f8467`. Full social and new website/news source list: `s5-review.json`.

Social items rejected by stricter attribution in this step:
- `919653477` https://www.linkedin.com/company/vokser-group — handle does not match a registered company/subunit name.
- `991368000` https://www.instagram.com/studioralstonbau — handle does not match a registered company/subunit name.
- `936855865` https://www.instagram.com/shopify — handle does not match a registered company/subunit name.
- `990012288` https://www.facebook.com/pages/TB-Maskin-As/455200387968353 — not republished in this run; consult current website/source diagnostics; not itself a wrong-company finding.
- `990012288` https://www.youtube.com/user/thomasbech8 — handle does not match a registered company/subunit name.
- `971349743` https://www.facebook.com/museumssenteret — handle does not match a registered company/subunit name.
- `971349743` https://www.youtube.com/channel/UCjvUaEpHHOTVtcwEljAU_Uw — handle does not match a registered company/subunit name.
- `938092516` https://www.facebook.com/OsloChamber — handle does not match a registered company/subunit name.
- `930166030` https://www.instagram.com/plumposlo — handle does not match a registered company/subunit name.
- `997790952` https://www.facebook.com/HillerenProsjekteringAS — not republished in this run; consult current website/source diagnostics; not itself a wrong-company finding.
- `918486666` https://www.instagram.com/antisink_systems — handle does not match a registered company/subunit name.
- `920358411` https://www.facebook.com/LarsZach — handle does not match a registered company/subunit name.
- `912667758` https://www.instagram.com/eimealt_as — not republished in this run; consult current website/source diagnostics; not itself a wrong-company finding.
- `912667758` https://www.tiktok.com/@eimealt — not republished in this run; consult current website/source diagnostics; not itself a wrong-company finding.
- `971558415` https://www.facebook.com/scenehuset — handle does not match a registered company/subunit name.
- `971558415` https://www.instagram.com/scenehuset — handle does not match a registered company/subunit name.
- `952785052` https://www.facebook.com/nsnl2 — handle does not match a registered company/subunit name.
- `925310492` https://www.facebook.com/bruktemaskinernorge — handle does not match a registered company/subunit name.
- `983485731` https://www.facebook.com/advokatenestorgata2 — not republished in this run; consult current website/source diagnostics; not itself a wrong-company finding.
- `917816328` https://www.instagram.com/geiterygghytta — not republished in this run; consult current website/source diagnostics; not itself a wrong-company finding.
- `917816328` https://www.facebook.com/pages/Geiterygghytta/142069355875460 — not republished in this run; consult current website/source diagnostics; not itself a wrong-company finding.
- `917816328` https://www.facebook.com/turistforeningen — handle does not match a registered company/subunit name.
- `917816328` https://www.instagram.com/turistforeningen — handle does not match a registered company/subunit name.
- `917816328` https://www.youtube.com/@turistforeningen — handle does not match a registered company/subunit name.
- `990342555` https://www.facebook.com/nordstrandkulturskole — not republished in this run; consult current website/source diagnostics; not itself a wrong-company finding.
- `990342555` https://www.instagram.com/nordstrandkulturskole — not republished in this run; consult current website/source diagnostics; not itself a wrong-company finding.
- `939725709` https://www.facebook.com/sagaregnskap — handle does not match a registered company/subunit name.
- `939725709` https://www.linkedin.com/company/sagarr — handle does not match a registered company/subunit name.
- `939725709` https://www.instagram.com/sagaregnskap — handle does not match a registered company/subunit name.

S5-1c evidence: `bench/runs/20261103T212216230863Z-66cdb5d`. Full social and new website/news source list: `s5-review.json`.

S5-5 evidence: `bench/runs/20261103T212841589097Z-18d31aa`. Full social and new website/news source list: `s5-review.json`.

## S5 optional-search preparation ? pending live gate

Prepared code: `2801e02`. Full suite: 793 passed; final focused Brave/environment suite: 27 passed; PowerShell wrapper syntax valid. No live Brave request has been made. Both explicit terminal variables and positive query/cost room are required. The opt-in benchmark supplies at most $0.50 for 100 companies. The normal benchmark strips search credentials.

The user explicitly requested STOP before live testing so they can set SIGNALPOST_SEARCH_PROVIDER=brave and BRAVE_SEARCH_API_KEY in the terminal. The paired 100-company comparison, search KEEP/ROLLBACK decision, and final search-OFF 1000 run are pending that setup. No step-6 KEEP is claimed from mocked tests.

Latest completed 100 free run: `bench/runs/20261103T212841589097Z-18d31aa/`. Latest 1000 checkpoint (before the final refresh/typed-sameAs changes): `bench/runs/20261103T210757525212Z-e8f8467/`, exit 0, 291.317s, 6592 HTTP, no deadline hits, 24 website budget errors; 73 websites and 33 social available. Full item/source reviews are saved in each run. The interim S5 report, full per-step review list and git log are at `bench/runs/20261103T212841589097Z-18d31aa/S5_REPORT.md`.

### F17 latest completed checkpoints

| Exclusive stop reason | 100 | 1000 checkpoint |
|---|---:|---:|
| no candidates generated | 2 | 11 |
| all candidates DNS-missing | 44 | 479 |
| robots or blocked | 6 | 46 |
| fetched but no proof | 16 | 165 |
| proof conflict (other orgnr) | 0 | 43 |
| ambiguous (name-only or competing candidates) | 1 | 28 |
| budget exhausted | 1 | 16 |
| TLS-connect failure | 19 | 139 |
| 2026-11-04 | `0b05b2e` | S5-6-trial | Optional Brave live trial; two false official-directory assignments | 100/100/85/100/10/4/1/29 → 100/100/85/100/13/5/1/29 | 18 | 9 items / 2 wrong | ROLLED BACK | 793 tests; 391.532s, 1512 HTTP. 59 queries, estimated USD 0.295; two directory pages rejected on full review. Existing directory guard root cause will receive a separate regression fix before reapplication. Ralston recovery is transport variance, not search gain. |
| 2026-11-04 | `47a295c` | S5-6-root | Reject two registry-copy directories globally and in independent audit | 100/100/85/100/10/4/1/29 → 100/100/85/100/11/5/1/29 | 2 | 6 items / 0 wrong | KEEP | 776 tests; 546.260s, 1091 HTTP. Four regression cases pass. No available-count drops; five social and one recovered exact-org website reviewed. Ralston recovery is transport variance. Search OFF; estimated cost zero. |
| 2026-11-04 | `e33b951` | S5-6-retrial | Reapplied Brave after first directory guard; LEI record rejected on review | 100/100/85/100/11/5/1/29 → 100/100/85/100/11/4/1/29 | 17 | 6 items / 1 wrong | ROLLED BACK | 797 tests; 469.008s, 1470 HTTP. 61 queries, estimated USD 0.305. One false official attribution: NordLEI record for Giljeholmen. KN Elektro social lost to independent robots/redirect timeouts. Extend ownership guard to LEI records before another reapplication. |
| 2026-11-04 | `44bf7cb` | S5-6-LEI-root | Reject LEI lookup records on known and unlisted provider domains | 100/100/85/100/11/5/1/29 → 100/100/85/100/11/5/1/29 | 2 | 5 items / 0 wrong | KEEP | 780 tests; 344.674s, 1081 HTTP. Eight directory regressions preserve own-company homepages with LEI disclosures. All five social sources reviewed; no available-count drops. Search OFF, zero cost. |
| 2026-11-04 | `87ab7ab` | S5-6-final | Optional Brave behind explicit environment and positive budget gates; reject registry lookup results | 100/100/85/100/11/5/1/29 → 100/100/85/100/11/5/1/29 | 15 | 6 items / 0 wrong | KEEP | 801 tests; 372.803s, 1498 HTTP. 59 queries, all HTTP200; USD 0.295 estimate. Zero additional verified sites/social/news and no available-count drops; all five social plus changed exact-org proof reviewed. Keep default-OFF, not recommended for this cohort. Website budget errors 2 to 15. Failed trials plus final: 179 attempts, USD 0.895 total estimate. |
| 2026-11-04 | `098dc33` | S5-metadata-guard | Ignore malformed social URL metadata without discarding exact site proof | 100/100/85/100/11/5/1/29 → 100/100/85/100/11/5/1/29 | 2 | 5 items / 0 wrong | KEEP | 806 tests; 292.558s, 1090 HTTP. CNC Norway sameAs https://[object Object] reproduced ValueError in observation ledger; five regressions and full suite pass. All five social sources reviewed; no count drops. No NAV/index changes. Search OFF. |
| 2026-11-04 | `c0da0a1` | S5-final-scale | Final 1000-company search-OFF validation after malformed metadata safeguard | 1000/997/774/999/68/29/2/231 → 1000/997/774/999/71/32/2/231 | 23 | 54 items / 0 wrong | VALIDATION | 806 tests; 472.309s, 6989 HTTP. 1000 envelopes, exit zero, 472.309s = 19.68 percent of 2400s, under 1200s. Zero deadlines/exceptions, 6989 HTTP. All 50 social and four changed site proofs reviewed; all 71 sites audited, 0 wrong. NAV stale-index full fallback 363.188s/508 requests; 73 hiring-incomplete companies retained. One accounts VPFO source failure unchanged. Runtime variation is not attributed to NAV changes. |
| 2026-11-04 | `52818c4` | S6-1-100 | Fresh public-token NAV index, 100-company gate | 100/100/85/100/11/5/1/29 → 100/100/85/100/11/5/1/29 | 2 | 6 items / 0 wrong | KEEP | 808 tests; 59.596s, 700 HTTP; NAV declared_index, 4.516s/4 requests, 0 incomplete. NAV incomplete8 to0; no section drop; job and five social sources reviewed. |
| 2026-11-04 | `52818c4` | S6-1-1000 | Fresh public-token NAV index, scale gate | 1000/997/774/999/71/32/2/231 → 1000/997/774/999/72/33/3/231 | 24 | 57 items / 0 wrong | KEEP | 808 tests; 316.499s, 6495 HTTP; NAV declared_index, 34.453s/6 requests, 0 incomplete. NAV incomplete73 to0, declared_index; all52 social,3 jobs and2 changed site proofs reviewed, zero wrong. No section drop. |
| 2026-11-04 | `4407516` | S6-2-100 | Fallback time-based detail budget, normal100 | 100/100/85/100/11/5/1/29 → 100/100/85/100/11/5/1/29 | 2 | 5 items / 0 wrong | KEEP | 811 tests; 55.340s, 694 HTTP; NAV declared_index, 4.500s/4 requests, 0 incomplete. All5 social sources reviewed; no new assignments or count drops. |
| 2026-11-04 | `4407516` | S6-2-stale1000 | Forced-stale fallback stress gate | 1000/997/774/999/71/32/2/231 → 1000/997/774/999/71/32/2/231 | 26 | 51 items / 0 wrong | KEEP | 811 tests; 346.998s, 7143 HTTP; NAV full_feed_fallback, 272.438s/663 requests, 69 incomplete. Original October14 index;299 detail attempts,0 unchecked candidate companies,0 failed ads/cap hits. Incomplete73 to69, all name-unusable, honest nav_name_unusable.346.998s under1200. No section drop versus stale baseline,50 social and1 changed site reviewed. |
| 2026-11-04 | `4407516` | S6-2-1000 | Fallback robustness, normal1000 gate | 1000/997/774/999/72/33/3/231 → 1000/997/774/999/72/33/3/231 | 21 | 52 items / 0 wrong | KEEP | 811 tests; 249.476s, 6482 HTTP; NAV declared_index, 29.203s/6 requests, 0 incomplete. Declared-index normal path unchanged;0 incomplete and no count drops. All52 social sources reviewed. |
| 2026-11-04 | `1abf474` | S6-3a-100 | Bounded own-company contact section and extra proof pages,100 | 100/100/85/100/11/5/1/29 → 100/100/85/100/11/5/1/29 | 6 | 5 items / 0 wrong | KEEP | 823 tests; 56.959s, 751 HTTP; NAV declared_index, 4.187s/4 requests, 0 incomplete. No coverage drops;5social sources checked;website budget errors2to6. |
| 2026-11-04 | `1abf474` | S6-3a-1000 | Saga/contact proof and up to3extra imprint/privacy checks,scale | 1000/997/774/999/72/33/3/231 → 1000/997/774/999/75/34/3/231 | 65 | 59 items / 0 wrong | KEEP | 823 tests; 273.237s, 7108 HTTP; NAV declared_index, 28.750s/7 requests, 0 incomplete. Full54social and5changed site proofs reviewed,0wrong. Net3websites/1social;budget errors21to65. Exact new identities Balder,Eimealt,Saga,7ocean;old NSNL plaintext fallback tracked for Step4. |
| 2026-11-04 | `5a43013` (reverts `2b97438`) | S6-3b | Revert unbenchmarked suffix-absent trial | No benchmark; retained Step 3a results unchanged | not measured | not performed | not completed (model capacity interruption) | User-directed hard-stop wrap-up; no KEEP claim; rerun full 100/1000 gates before reconsidering. |

Candidate-only DNS/connect/timeouts do not prove a real official website is unreachable. Stop buckets are exclusive; budget error totals can overlap other stop states. New nominations address the largest observed gap; bucket sizes are not measured recovery promises.

S5-6-trial evidence: `bench/runs/20261104T051103339719Z-0b05b2e`. Full social and new website/news source list: `s5-review.json`.

S5-6-root evidence: `bench/runs/20261104T052607204480Z-47a295c`. Full social and new website/news source list: `s5-review.json`.

S5-6-retrial evidence: `bench/runs/20261104T054207443662Z-e33b951`. Full social and new website/news source list: `s5-review.json`.

Social items rejected by stricter attribution in this step:
- `823147112` https://www.facebook.com/KN-Elektro-As-104194150969215 — website proof unavailable or source profile no longer published; not asserted wrong-company.

S5-6-LEI-root evidence: `bench/runs/20261104T055653185175Z-44bf7cb`. Full social and new website/news source list: `s5-review.json`.

S5-6-final evidence: `bench/runs/20261104T060955663646Z-87ab7ab`. Full social and new website/news source list: `s5-review.json`.

S5-metadata-guard evidence: `bench/runs/20261104T064156705198Z-098dc33`. Full social and new website/news source list: `s5-review.json`.

S5-final-scale evidence: `bench/runs/20261104T064749747167Z-c0da0a1`. Full social and new website/news source list: `s5-review.json`.

S5 final status (2026-11-04): Steps 1-5 and the guarded default-OFF optional Brave integration are KEEP. Two initial search trials were explicitly withdrawn, with independent directory/LEI ownership guard fixes and rebenchmarks before reapplication. The final paired search benchmark spent an estimated USD 0.295 on 59 successful queries and added zero verified websites/social/activity; all three trials total 179 attempted queries and estimated USD 0.895. No key is printed or stored. The optional integration should remain OFF for this cohort. Website budget diagnostics rise from 2 to 15 when it is enabled.

Final code passed 806 tests. Search-OFF 100 benchmark: 100/100/85/100/11/5/1/29 available, 292.558s, 1090 requests, two website budget errors. Final search-OFF 1000 benchmark: 1000/997/774/999/71/32/2/231 available, 472.309s, 6989 requests, 23 website budget errors, zero deadline hits and zero handled/unhandled exceptions. Raw results, all reviewed URLs/hashes/excerpts, F17 loss tables and git log are in `bench/runs/20261104T064749747167Z-c0da0a1/S5_REPORT.md`; the already-open earlier S5_REPORT.md is refreshed with the same report. Every final social item (50 claims across 32 companies), all 71 website proofs and 11 dated article records were opened; zero wrong-company findings. The independent Elektrokompetanse audit false positive is documented from its own branded exact-org footer. CNC Norway's malformed sameAs failure was reproduced from saved HTML, fixed narrowly and rebenchmarked; its valid Instagram passes, the other company's Facebook is excluded.

NAV freshness finding and proposal only: bundled index built 2026-10-14T04:26:40.758720Z expired at 2026-11-04T04:26:40.758720Z (09:56:40 IST). At the 344.674s free control its age was 21.062644 days; `index_stale` triggered `full_feed_fallback`, NAV 298.421s/394 requests/362 pages. The earlier 53.128s run used `declared_index`, age 20.709732d, NAV 28.891s/52 requests. Final 1000 used unchanged stale index age 21.098021d, full fallback 363.188s/508 requests/363 pages, total 472.309s; feed transport completed but 73 companies remain hiring-incomplete under NAV detail/name completeness rules. No accounts 429s: the only scale 429 was Elkjop robots.txt; the single accounts error remains BRREG HTTP500 unsupported VPFO for 926077422 (three attempts). This is not a measured 1100-company future-date guarantee.

Before submission, propose a fresh no-disk-seed resumable index build into a new checkpoint, require zero failed details and validated schema/counts/cursor/provenance, then review/replace the bundled artifact and test 1100 companies. For later dates, propose completed cursor catch-up from structurally valid stale discovery metadata plus live candidate detail verification; malformed/missing/incomplete indexes must retain honest full-feed fallback. Profile and benchmark the cold path, address growth toward the 512-page cap (363 pages today), preserve politeness/rate-limit/TLS/identity/completeness checks, and require <1200s end-to-end on 1100 companies for fresh/stale/missing/malformed cases. Full proposal and exact timings: `NAV_INDEX_PLAN.md` beside the final report. No index rebuild, age-threshold edit, historical override or fallback optimization was executed in S5. Nothing pushed.

S6 diagnostic correction (2026-11-04): `scripts/website_loss.py` now requires a retained successful HTTP200 non-robots/non-XML company page with no request error/truncation for fetched/no-proof. Missing bodies and failed HTTP responses are a separate no-retained-page bucket. Six targeted tests and the complete 808-test suite pass. Reanalysis only: saved S5 1000 fetched/no-proof changes 154 to 102, with 53 no-retained-page companies; runtime/envelopes unchanged. Corrected tables and original sampled evidence are under `bench/runs/S6-20261104/`. Live Step 1 benchmarks are pending the fresh public-token index build; no coverage gain is claimed for this report-only correction.

S6 Step 1 fresh NAV index build (benchmarks pending): public token, new checkpoint, no disk seeds. Built_at 2026-11-04T07:16:54.150483Z; expiry 2026-11-25T07:16:54.150483Z, covering planned judging through 12 Nov. 8,554 active usable ads, 5,500 employers, zero failed details; compressed 396,394 bytes; 1,303.454s and 9,262 public-source requests for the development build. Full schema/count/cursor/freshness validation passes. No fallback runtime change. Artifact SHA and raw build report saved under bench/runs/S6-20261104 and bench/cache/s6-nav-build-20261104.

S6-1-100 evidence: `bench/runs/20261104T073725872378Z-52818c4`. Full opened source list: `s6-review.json`.

S6-1-1000 evidence: `bench/runs/20261104T073852917844Z-52818c4`. Full opened source list: `s6-review.json`.

S6-2-100 evidence: `bench/runs/20261104T074953456731Z-4407516`. Full opened source list: `s6-review.json`.

S6-2-stale1000 evidence: `bench/runs/20261104T075124281242Z-4407516`. Full opened source list: `s6-review.json`.

S6-2-1000 evidence: `bench/runs/20261104T075735641992Z-4407516`. Full opened source list: `s6-review.json`.

S6-3a-100 evidence: `bench/runs/20261104T081142666432Z-1abf474`. Full opened source list: `s6-review.json`.

S6-3a-1000 evidence: `bench/runs/20261104T081322420645Z-1abf474`. Full opened source list: `s6-review.json`.

S6 hard-stop wrap-up: Steps 1, 2 and 3a KEEP; Step 3b reverted as not completed (model capacity interruption); Step 4 and S7 not started. Durable reports and evidence are in `bench/reports/`.

Open issue for S6 Step 4: NSNL (org 952785052) was published as `http://www.nsnl.no` by the existing plaintext fallback in the Step 3a 1000 benchmark. Exact-company review passed, but plaintext is not valid TLS evidence. Do not treat this as resolved: Step 4 must permit only an HTTP redirect probe to valid HTTPS and never publish plaintext page evidence. No fix was attempted during wrap-up.

Final hard-stop validation after reverting Step 3b: `uv run pytest -q` ? **823 passed in 192.93s**, exit 0. No new benchmark was run during wrap-up. Production code, scripts and tests match the kept Step 3a checkpoint (`4d80529`).
