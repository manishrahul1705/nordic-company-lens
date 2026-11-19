# Twenty-company NAV route investigation

19 November 2026. Read-only investigation on `audit-fixes`. No production code was changed and nothing was pushed. No GitHub reconnection was performed. HTTP requests were made locally; no browser was used for the tests.

**Finding: no tested route demonstrated a working organisation-number filter.** The documented feed works, but ignores the attempted company query parameters. The public search works by keywords and returns employer names without organisation numbers. The legacy public-feed route remains unavailable with the current token.

## Route table

URLs below show the concrete `976645677` request. Every exact per-company URL and status is in [HTTP-TABLE.md](HTTP-TABLE.md) and [matrix.json](matrix.json). All feed and retired-path tests used the current public token in an Authorization bearer header; token values were not saved.

| Route / concrete URL | HTTP results | Ads returned / actual filtering | Employer orgnr in payload |
|---|---|---|---|
| `https://pam-stilling-feed.nav.no/api/v1/feed?orgnr=976645677` | 20/20 HTTP 200 | Same 1,000 feed headers as unfiltered control; orgnr ignored | No, headers only |
| `https://pam-stilling-feed.nav.no/api/v1/feed?employer=976645677` | 20/20 HTTP 200 | Same header IDs; employer ignored | No |
| `https://pam-stilling-feed.nav.no/api/v1/feed/4e7cebfb-1920-485b-8f65-0105797afed5?orgnr=976645677` | 20/20 HTTP 200 | Same specified page; orgnr ignored | No |
| `https://arbeidsplassen.nav.no/stillinger/api/search?orgnr=976645677&size=10` | {'200': 1, '429': 19} | Successful control returned the general job list with unrelated employers; 429s are unavailable | No in the successful search payload |
| `https://arbeidsplassen.nav.no/stillinger?q=976645677&v=6` | 20/20 HTTP 200 | No keyword hits for any of the 20 organisation numbers | No |
| `https://arbeidsplassen.nav.no/stillinger?q=VARD+AS&v=6` | 20/20 HTTP 200 | Legal-name keyword candidates for 5/20 | No |
| `https://arbeidsplassen.nav.no/stillinger?q=VARD&v=6` | 20/20 HTTP 200 | Suffix-free keyword candidates for 9/20, not verified company coverage | No |
| `https://pam-stilling-feed.nav.no/api/v1/feedentry/5cc7591a-a28b-4753-93dd-d1a11200c883` | Three known-published controls: 3/3 HTTP 200. All name candidates: 29/39 HTTP 200; 10/39 HTTP 404 | Ad lookup by UUID; does not accept company IDs as a lookup key | Yes in the 26 readable candidate details |
| `https://arbeidsplassen.nav.no/public-feed/api/v1/ads?orgnr=976645677&size=10` | 20/20 HTTP 404 | HTML error pages, no ad payload, current-token authentication did not restore route | Not applicable |

The JSON search endpoint was rate-limited. Its error cells are not empty ad lists. Each company was attempted once for the main JSON orgnr test; Retry-After: 60 was honored. It is not valid to infer company coverage from either these 429s or the unfiltered HTTP 200. Additional employer and q controls are retained in the request table, with their individual statuses.

## What the current site actually calls

The live `/stillinger` HTML referenced 37 JavaScript chunks. They were downloaded and inspected locally. The query registry in chunk `5527-7d082cd93581c5ab.js`, module 7439, defines `SEARCH_STRING: q` and `URL_VERSION: v`; it has no employer/orgnr query field. Module 37419 in `app/stillinger/(sok)/page-073f93c64247e8cf.js` rebuilds the current pathname plus query string and calls router.replace/router.push. The observed canonical version is `v=6`. Search results are delivered in the page SSR/RSC data.

This build does not contain a direct `/stillinger/api/search` literal in its 37 delivered chunks. Therefore the current client trace supports the page-query route, not a claim that this client directly fetches that JSON URL. The answering JSON compatibility endpoint was tested separately over HTTP. No dedicated employer-number UI filter was found. Asset URLs, hashes, parameter names and module identifiers are in [bundle-inspection.json](bundle-inspection.json). Raw downloaded JS is retained under `out/nav-live-routes-20-20261119/discovery/`.

## Current documented feed routes

The live [OpenAPI specification](https://pam-stilling-feed.nav.no/api/openapi.json), located through the Redoc page named in NAV current documentation, lists exactly `/api/v1/feed`, `/api/v1/feed/{feedPageId}` and `/api/v1/feedentry/{entryId}`. Only `last` is a query parameter on the first-page route. The other routes require UUIDs; conditional-date/ETag headers support feed paging, not employer filtering. The [current documentation](https://navikt.github.io/pam-stilling-feed/) explicitly assigns employer/company filtering to the consumer.

The UUID-detail route was tested with the three known published ad UUIDs and all 39 unique suffix-free name-search candidate UUIDs. Companies with no candidate UUID do not have an organisation-number lookup URL for that route; no UUID was fabricated.

## Twenty-company table

Keyword columns are numbers of ad candidates, not exact employer matches. All page-query cells were HTTP 200. The sample contains the four requested audit companies and all three currently published companies, then fills to 20 in frozen-cohort order; it is intentionally enriched with positives. Number-keyword searches returned zero for all 20. Three extra known-subunit-number searches also returned HTTP 200 with zero hits.

| Organisation | Legal name | Published before | Legal-name keyword ads | Without legal suffix | Number keyword ads | Verified ACTIVE ads | JSON orgnr HTTP | Retired HTTP |
|---|---|---|---:|---:|---:|---:|---|---|
| 976645677 | VARD AS | No | 8 | 9 | 0 | 0 | 200 | 404 |
| 991247610 | ROLIDBAKKEN FUS BARNEHAGE AS | No | 0 | 0 | 0 | 0 | 429 | 404 |
| 922154635 | SKATTEKISTEN AS | No | 0 | 0 | 0 | 0 | 429 | 404 |
| 934500644 | SANDØ AS | No | 4 | 11 | 0 | 0 | 429 | 404 |
| 923354220 | EIDEFOSS VANNKRAFT AS | Yes | 2 | 2 | 0 | 1 | 429 | 404 |
| 960213912 | ROSENLUND BARNEHAGE SA | Yes | 0 | 1 | 0 | 1 | 429 | 404 |
| 930202894 | NORLANDIA ENGA BARNEHAGE AS | Yes | 0 | 1 | 0 | 1 | 429 | 404 |
| 912823970 | MYNT OG EIENDOM BESSAKER AS | No | 0 | 0 | 0 | 0 | 429 | 404 |
| 916729774 | FIKO EIENDOM AS | No | 0 | 0 | 0 | 0 | 429 | 404 |
| 917998787 | DRAGEHAUGEN VERDI AS | No | 0 | 0 | 0 | 0 | 429 | 404 |
| 918049215 | MENSTAD NÆRINGSPARK AS | No | 0 | 0 | 0 | 0 | 429 | 404 |
| 919948493 | SQ URBAN LANDSKAP AS | No | 0 | 0 | 0 | 0 | 429 | 404 |
| 982410851 | MARUN AS | No | 2 | 2 | 0 | 0 | 429 | 404 |
| 981508734 | MYKLEBUST MARITIME AS | No | 0 | 2 | 0 | 0 | 429 | 404 |
| 916049153 | SJØL INVEST AS | No | 49 | 9 | 0 | 0 | 429 | 404 |
| 882749762 | NOTEK HOLDING AS | No | 0 | 0 | 0 | 0 | 429 | 404 |
| 936276075 | M BERGUM AS | No | 0 | 0 | 0 | 0 | 429 | 404 |
| 923472134 | BOLIG 1 HALDEN AS | No | 0 | 2 | 0 | 0 | 429 | 404 |
| 936312055 | ULTRAMAX 8 AS | No | 0 | 0 | 0 | 0 | 429 | 404 |
| 995541432 | WACKER CHEMICALS NORWAY AS | No | 0 | 0 | 0 | 0 | 429 | 404 |

**Comparison with the three published companies:** suffix-free keyword search returned candidates for 9 companies. It produced 39 unique candidate UUIDs: 29 details were readable and 10 returned 404. Only three were current exact employer/subunit matches across the selected companies, the same three ads already published. Other readable records had different employer IDs. Unavailable details remain unresolved, not proof of no ad or a wrong employer. No additional verified company coverage was demonstrated in this tested candidate set.

| Published company parent | Actual employer subunit in live payload | Current ad UUID | Status |
|---|---|---|---|
| 923354220 | 981955234 | `5cc7591a-a28b-4753-93dd-d1a11200c883` | ACTIVE |
| 960213912 | 972285501 | `a3e96411-9639-48cd-a27b-2e5e4406a3e8` | ACTIVE |
| 930202894 | 997453964 | `c0349976-bbfc-41f4-a980-b482f06e5f2d` | ACTIVE |

Affiliations were checked against the verified parent/subunit map retained from the same-day frozen run, not inferred from employer names. Candidate detail evidence is in [candidate-details.json](candidate-details.json). The currently published ads all use subunit employer numbers, which is important for any future direct-query proposal.

## Robots and terms

The live [arbeidsplassen robots.txt](https://arbeidsplassen.nav.no/robots.txt) was HTTP 200 with `User-agent: *` and an empty Disallow directive. The feed host robots.txt returned HTTP 404, with no rules supplied. The documented feed [reuse terms](https://arbeidsplassen.nav.no/vilkar-api) allow free analytical use and republication, conditional on keeping ads updated and removing inactive/deleted ads.

The site [general terms](https://arbeidsplassen.nav.no/vilkar-og-retningslinjer), under employer services, explicitly restrict systematic automated copying without written NAV consent. I did not verify an exception granting production reuse through the undocumented search/HTML route. Permissive robots rules alone are insufficient to establish that permission, and the feed terms should not automatically be extended to the whole search board. The search results include FINN-origin ads; the 10 candidate UUIDs unavailable from the feed were FINN-origin in the page payload. This is also consistent with the feed documentation warning that it does not share Finn vacancies.

## Scope and decision

No supported or demonstrated working organisation-number query was found among these route families. A live keyword search exists, but its candidates lack employer organisation numbers and require UUID-detail validation. The verified result is **3/20 companies**, equal to our three published companies, with unresolved detail failures reported separately. Do not treat keyword hits as verified employers. No implementation change is recommended on this evidence. No extrapolation to the full 1,000-company cohort is made.

The JSON compatibility endpoint rate-limited cells remain unknown; this is an investigation of the tested public routes, not a claim about every possible private/internal NAV endpoint. No production files were changed by this task. Nothing was pushed.

## Evidence

- [Exact request URL/status/payload table](HTTP-TABLE.md)
- [Per-company matrix](matrix.json)
- [Summary](summary.json)
- [Bundle inspection](bundle-inspection.json)
- [Candidate details](candidate-details.json)
- Saved live OpenAPI: `discovery/spec-prod.txt`; robots response snapshots are in `discovery/`; current terms are linked above.
- Full raw response snapshots and downloaded JS were retained locally, not included in this report commit: `out/nav-live-routes-20-20261119/`. Exact URLs, response statuses, payload summaries and hashes are included in the committed evidence.

For three companies, six keyword controls were repeated after a local Windows-default-encoding metadata read corrupted Norwegian letters. Numeric tests were unaffected. The table uses the corrected UTF-8 source names and corrected requests; see `encoding-correction.json` and `corrected-keyword-requests.json`. Detail verification covers suffix-free keyword results, not an exhaustive crawl of every name variation. The legal-name query for 916049153 reported 49 results and was not fully paged.
