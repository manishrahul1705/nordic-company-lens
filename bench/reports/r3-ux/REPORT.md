# Offline-site UX check ? 12 November 2026

Branch more-websites. Source: latest proof-depth-live 1,000-company generated site, opened directly with file:// in Playwright Chromium. No network/data refresh, no claim changes, no push. CSS/JS only; original envelopes, HTML, site data and evidence payloads remain unchanged.

Test matrix: 375?812 and 1366?900, light/dark. Tensio AS 922828172 (large), Dragehaugen Verdi AS 917998787 (medium profile density), NRP Anaxo Nordic M2 926077422 (sparse, 46 claims). Density labels do not assert employee size.

| Task/check | Before | After |
|---|---|---|
| Search name and orgnr | PASS | PASS |
| Open profile, briefing first, readable sections | PASS | PASS |
| Compare two companies, reload | PASS | PASS |
| Evidence drawer: URL, date, quote, nonempty | PASS | PASS |
| No horizontal scroll | PASS | PASS |
| No overlapping text / one-character wrapping | PASS | PASS |
| Labels not clipped | FAIL: mobile watchlist | PASS |
| All tap targets ?44px | FAIL: legacy 40px floor | PASS |
| No raw JSON / ISO dates by default | FAIL: evidence drawers | PASS |
| Theme retained on reload | PASS | PASS |
| Internal links: index + 30 profiles | PASS | PASS |
| Fully offline, no script errors | PASS | PASS |
| Every HTML page <250 KB | PASS | PASS |

32 task/page screenshots plus 12 scrolled quote screenshots per phase; **44 before + 44 after**. Each screenshot filename identifies viewport/theme/page. Both audit.json files retain detailed results. All boolean judged-task assertions pass in the final browser audit. The original source excerpt disclosure opens, contains the captured text, and closes.

Geometry checks find no horizontal overflow, actual text/control overlaps, clipped text, one-character wrapping or small visible targets after fixes. Screen-reader-only labels are excluded from visual clipping checks. Screenshot review covers mobile profile, index, evidence/quote, comparison and desktop sparse/compare views. This is sampled geometry and visual inspection, not an exhaustive pixel-level guarantee across every company page.

Crawled all internal file/fragment links on the index and 30 profiles: zero broken. No HTTP(S) requests or JS page errors. **Largest HTML is 239,537 bytes across 3,715 HTML files**, unchanged; no page ?250,000 bytes.

## Fixes restricted to failures

- site.css: 44px interaction floor overriding the legacy 40px rule; wrap the watchlist label; reserve evidence-heading space for Close; contain long source URLs.
- site.js: readable retrieval/effective dates in UTC; show an exact matching fact-value substring as the default structured-source quote, with the full original captured excerpt intact in an explicit expandable disclosure. If no exact matching value exists, retain the original quote.
- The explicit Original source excerpt view may intentionally display raw JSON, preserved for forensic inspection; default-view cleanliness checks exclude that user-requested raw view. No evidence or claim value is rewritten.
- Updated only assets/site.css and assets/site.js in the saved generated site. No HTML regeneration or source research was needed.

## Validation

Site/UX/CLI site tests: **32 passed in 199.58 s**. Full suite: **1,282 passed in 472.69 s**, without overlapping this task's browser/site/hash jobs. The first run had 1,280 passed and two existing timing-check failures under concurrent load (forced-deadline elapsed bound and 5-second subprocess timeout); the untouched full suite passed on rerun. Both logs are retained. No tests or assertions were weakened.
