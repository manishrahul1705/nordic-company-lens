# Bounded verified-site news measurement - 20 November 2026

Adds only `news_item.*` activity claims, scoped to existing available VERIFIED company websites. At most one advertised same-domain resource is selected; up to five latest explicit-date items are published. No feed path guessing, child-resource/article crawling, cross-domain redirect expansion or source/budget-default changes. Existing dated_item extraction remains unchanged.

## Measurement

The frozen 1,000 saved run after official BRREG indexes and funding snapshots was used: `bench/runs/funding-snapshots-final-20261120`. Already fetched verified homepages and same-domain cached pages/robots were reused. Only the newly selected resources were fetched live with the production WebsiteHttp transport, robots rules, pacing, SSRF/TLS and caps. Original request log usage was preloaded into both pooled/per-company counters and website counts, so the measurement did not obtain a fresh company allowance. This is an incremental saved-homepage/live-resource experiment, not a new full 1,000-company live run.

- Baseline verified sites: **114**. Eligible content-permitted, non-group verified sites examined: **110**; the other four receive no news lookup.
- **31 companies / 113 news_item claims**. Maximum per company: **5**. Date basis: **112 feed publication dates and one page explicit date**.
- **54 additional HTTP requests**, all selected-resource requests; cached robots policies meant zero additional robots HTTP reads here. 51 HTTP 200 and three timeouts.
- Original acquisition HTTP: **11,477 - 11,531**; pooled cap 19,000. Maximum attributed requests/input company: **40**, unchanged. Shared synthetic request buckets are not counted as input companies.
- Incremental measurement wall: **142.144 seconds**, including saved-output parsing, discovery, live resource fetches, synthesis/output serialization. This is not a measured incremental production crawl-time guarantee.
- Published facts: **167,862 - 167,975** (+113). Existing claims are retained. Original saved output/evidence is unchanged; new output is `bench/runs/news-items-20261120` with hard-linked old blobs and new response blobs.

| Outcome | Companies |
|---|---:|
| Published at least one item | 31 |
| No advertised feed/sitemap/news link | 49 |
| No already-fetched homepage | 2 |
| Selected resource has no acceptable explicit-date items | 21 |
| Website request budget exhausted | 4 |
| Website timeout | 3 |

[Every checked company, selected resource and outcome](DISCOVERY.md); machine-readable `diagnostics.json`, `requests.json`, `claims.json`, `measurement.json` and `audit.json` retain exact details. No-match outcomes are diagnostics only, never published no-news placeholders.

## Robots and request findings

**Zero path-specific robots denials in this measurement.** Existing cached robots policies from acquisition were parsed and checked for each selected path, not assumed to cover every path. A new authority would require the normal robots lookup. Tests verify `Disallow: /feed` blocks the feed request, that a shared-pool exhaustion after robots prevents publication, and that a redirect to another registrable domain is never requested.

One selected resource does not guarantee one HTTP transaction: necessary robots reads and bounded same-domain redirect hops consume normal caps. The dedicated fetch path uses the existing `_raw` checks without transient retry or cross-domain redirect expansion. It never follows resource contents to fetch articles, child sitemaps or another candidate. Cached pages avoid a resource request.

## Extraction and evidence

Feed alternate links are preferred over an explicit sitemap reference, then obvious news/nyheter/aktuelt/presse/press links. Only the existing verified registrable domain is allowed. RSS requires title/link/pubDate; Atom uses explicit published or updated timestamps (updates stay labelled updates). HTML extraction requires an article element containing its own headline link and time element; no date is borrowed from another card. Dates support ISO timestamps, RFC feed dates, unambiguous dotted day/month/year and Norwegian/English month names. Future/invalid/incomplete/ambiguous slash dates are withheld. Deduplicate by URL and select the five latest dates.

Sitemaps require an explicit title as well as loc/lastmod; ordinary URL-only sitemaps therefore produce no items. Lastmod is labelled last modification, **not publication**. Sitemap indexes are not expanded, and titles are never invented from URL slugs. JavaScript-only pages and generic cards without article/time markup are outside current coverage. A dated item is a company-published observation, not independent editorial verification; dated default/template posts are not silently turned into inferred business events.

Each claim stores title, explicit date, date meaning, item URL and exact fetched source URL. Normal evidence retains the fetched bytes' SHA-256, retrieval timestamp, localized verbatim excerpt and locator, plus verified-site evidence. These are company-owned sources subject to their original rights, not newly open-licensed data. The final entity-scope guards can still suppress dependent company-owned activity if website acceptance is withdrawn.

## Validation

Thirty focused tests pass: date edge cases, RSS/Atom/sitemap/HTML extraction, title/date requirements, no-discovery, unverified-site refusal, five-item cap, exact retained evidence, robots refusal, shared budget interaction and cross-domain redirect rejection. The existing 1,686-test suite is expanded to **1,716 collected tests**; **full suite: 1,716 passed, one pytest cache-write permission warning, 472.99 seconds**, exit zero. Before: 1,686; after: 1,716 (+30 tests). See pytest.txt and pytest-timing.json. No existing test or cap was loosened.

Strict verifier: **PASS**, exit zero in 147.790 seconds: 1,000 envelopes, 167,975 claims, 5,882 source blobs and zero unverified synthesis values. Same integrity mode as prior stages, without the additional optional-source-health --require-clean gate. The verifier is unchanged and checks the full 1,000-envelope measurement output against retained evidence. Full site was not rebuilt; production site renders news_item under company-published activity through the existing fact renderer.

Implementation, reports and measurements remain uncommitted; no push. Existing funding changes from the preceding authorized task remain in the working tree. This task does not proceed to another stage.
