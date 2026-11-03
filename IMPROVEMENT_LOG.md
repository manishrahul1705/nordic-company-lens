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
