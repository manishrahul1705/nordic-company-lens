# Columnar retry in progress ? 11 November 2026

DuckDB/httpfs selected20,000 records from one nonempty Parquet file (part00129), after129 earlier files returned zero qualifying rows. At most two records per registered domain;12,709 selected domains. The raw selection is ignored. Query/settings and prior timestamp-conversion error are recorded in columnar-query.json.

The user extended WARC work to12:05IST and the hard stop to12:30IST. Archive processing uses at most two concurrent exact byte-range requests, bounded30/60s backoff, and stores no WARC bytes. Successful range counts are separate from parser outcomes;210 early parser failures remain explicitly retained. A fixed-seed shuffle processes as much as fits, then the bounded20-site live review runs. Final results will replace this progress section; the following CDX outage is historical, not the columnar result.

## Historical CDX attempt

# Common Crawl prototype — measurement only

## Result: index unavailable (11 November 2026)

Latest crawl from `index.commoncrawl.org/collinfo.json`: **CC-MAIN-2026-43**, October 2026 (5–18 October). The `.no` count probe succeeded: **2,886 index blocks** (578 pages at five blocks/page). Those are index partitions, not a count of eligible HTML pages, domains or companies.

The five-block record query returned HTTP504. A one-block retry sequence returned HTTP504, waited **30 seconds**, returned HTTP504 again, waited **60 seconds**, then disconnected without a response. One simpler one-block diagnostic also disconnected. No more retries were made. `events.json` preserves observed failures; `index-probe.json` preserves the successful count response. No cause beyond these observed errors is claimed.

**0 CDX records selected, 0 WARC records fetched, 0 MB WARC downloaded.** Company pairs, universe coverage, OSM overlap, bench100 matches, extrapolation and live ownership passes remain **unmeasured (null)**. The empty `candidates.jsonl` means unavailable measurement, not zero discoverable companies. The 20-company live check could not start. `summary.json` wall time describes the last bounded one-block attempt, not the entire development task.

The prototype is syntax-checked and has local exact-label/checksum/WARC-decoding checks; its network extraction/join/review pipeline has **not** been validated against real downloaded WARC records in this run.

## Terms and sources

Common Crawl access is subject to its Terms of Use and third-party content rights; do not overload the service, use at most two concurrent requests and back off on 429/503. https://commoncrawl.org/terms-of-use ; index guidance https://index.commoncrawl.org/ . Free access is not a blanket licence to redistribute crawled website content.

Only Common Crawl index/data endpoints, the cached official Brønnøysundregistrene subunit bulk (NLOD 2.0; credit Brønnøysundregistrene), cached Builderr challenge universe and existing OSM candidate output for the requested overlap comparison are used. No search engines, directory queries, Norid, credentials or paid APIs. Live checks, when candidate records are available, access only candidate company sites. No other crawl is substituted.

**Any in-agent use would need a bundled index; licensing and third-party content rights are a grey area to decide.** This measurement authorizes no production integration or redistribution claim for full pages. Short 120-character source snippets remain subject to the source owners' rights.

## Prototype method

1. Select latest CC-MAIN catalog ID. Query `*.no/*` with status200/HTML and root/contact/about/privacy path filters; repeat the exact filters locally. Visit single CDX blocks in fixed-seed shuffled order, retain at most 20,000 records and two records per registrable domain. Known directory/social domains are excluded without fetching them live.
2. Two-worker bounded queue; only exact indexed `offset/length` HTTP ranges from `data.commoncrawl.org`, requiring HTTP206 and matching Content-Range/length. Reject an ignored range before reading a whole WARC file. Decode gzip member and embedded HTTP response, including chunked/gzipped HTTP bodies; extract visible text with the unchanged Page parser. WARC bytes exist only in memory and are never written to disk. Members above 8 MB are skipped explicitly.
3. Find labelled Org.nr / Org. nr / Organisasjonsnummer / Foretaksregisteret or NO-number-MVA, spaced or compact, validating nine digits and mod-11. Unlabelled phone-like numbers are excluded. Drop all collected pairs from domains with at least three different labelled valid organisation numbers across checked pages; this may exclude genuine multi-entity sites as well as directories/accountants.
4. Join exact subunit numbers to cached `overordnetEnhet`; unmapped numbers are putative parents, not verified main-entity status. Save only identifying candidate metadata and 120-character snippets. Join parent numbers to the 411,160-company cached universe and bench100; compare exact parent-number overlap with OSM candidates.
5. A future successful run reports observed coverage and a clearly labelled *naive scenario*: scale matched parents by total .no index blocks / visited blocks and cap at universe size. Blocks include noneligible records; domain duplication, two-per-domain selection and final-page truncation bias this. It is not a statistical full-crawl estimate; a proper eligible-domain denominator/full scan would be needed. The current failed run has no extrapolation.
6. Fixed seed20261111 samples up to20 matched parents. One homepage plus up to two same-site proof pages, normal project User-Agent, robots and stricter crawl delays/rates, at least one second per host, TLS verification and no HTTPS downgrade. Uses existing candidate_proof/Config unmodified, Common Crawl origin as nomination only, parent legal name plus exact mapped subunit identity/contacts. No archive candidate itself supplies proof. Missing parent contact information is not inferred, so contact-proof pass rates can be conservative. Existing OSM live-check request helpers are reused; this is proof measurement, not full collector publication acceptance.

## Run / safeguards

Use the existing project environment (no pyproject.toml/uv.lock changes):

```powershell
uv run --frozen python scripts/cc_proto.py --retry-index
```

`--retry-index` is an explicit retry gate after this failed run. Inspect failure evidence before invoking; do not schedule a tight loop. At most three attempts per request with 30/60-second backoff (also for 502/504 and transport failures); honor numeric Retry-After if longer. Index calls are sequential; WARC calls at most two concurrent, no live review until WARC work completes. Raw CDX metadata/cache and live HTML are ignored under `bench/reports/cc-proto/raw/`; no WARC archive is cached or committed. Cached subunit/universe files remain in the ignored OSM raw directory. Parsed record results support resuming completed range work without refetching it.

No agent code, tests, pyproject.toml, uv.lock, main or fix-large-company-site changes. No push.
