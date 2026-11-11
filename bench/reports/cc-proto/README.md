# Common Crawl columnar prototype ? measured partial run

Measurement only, branch `more-websites`. No agent, test, pyproject.toml, uv.lock, main or fix-large-company-site changes. No push. The user extended WARC work to **12:05 IST** and the hard stop to **12:30 IST**, 11 November2026. This run stopped archive work at that cutoff and completed all20 live checks.

## Results

| Metric | Measured result |
|---|---:|
| Crawl | CC-MAIN-2026-43 |
| Selected index records / domains | 20,000 / 12,709 |
| WARC records processed / fetched / parsed | 12,493 / 12,491 / 12,281 |
| Successful WARC range payload MB | 372.058 |
| Pages with labelled valid orgnr, before / after domain exclusion | 2,205 / 2,198 |
| Extraction pairs / distinct orgnr-domain pairs | 2,217 / 1,708 |
| Distinct org numbers / domains | 1,671 / 1,690 |
| Distinct mapped-or-putative parent companies | 1,670 |
| Subunit numbers mapped | 1 |
| Universe matches | 1,141 / 411,160 |
| Observed expected matches per random1,000 companies | 2.775 |
| OSM overlap: all parents / universe parents / domains / exact parent-domain pairs | 8 / 7 / 6 / 6 |
| Universe matches not in OSM candidates | 1,134 |
| Bench100 matches | 0 |
| Live existing ownership proof passes | 13 / 20 |
| Whole-task wall time at report enrichment | 89.76 minutes |

Coverage is **nomination coverage**, not verified website coverage or agent improvement. This is a measured partial snapshot, not a full-crawl result or a guaranteed lower bound: more pages can add candidates or trigger additional three-org domain exclusions. 7,507 selected records were not attempted; two cutoff-time attempts did not complete. The210 early parse errors are retained and reported, not counted as checked no-orgnr pages. Archive normalization handling was fixed in the measurement decoder before subsequent records; earlier failed records were not re-fetched. No WARC bytes were stored.

MB counts successful compressed range payloads; it excludes failed/aborted attempts, HTTP overhead and DuckDB projected-read traffic, which was not instrumented. Wall time includes setup, retries, query attempts, archive processing, live review and report preparation. `network.json` covers only the last resumed archive process, not the entire task; use summary payload totals for the full cached successful-range total. Cache modification at12:05:30 includes a timeout result recorded after a30-second backoff; no further archive retry was issued after the cutoff.

## Columnar sample and extrapolation

The official manifest `https://data.commoncrawl.org/crawl-data/CC-MAIN-2026-43/cc-index-table.paths.gz` listed300 WARC-subset Parquet files. **One nonempty file supplies all20,000 selected rows**: `part-00129-6e44f0dc-08f9-465c-8a7f-b0da44e49f26.c000.zstd.parquet`. Before it,129 files returned zero qualifying rows. This is not a one-request scan or a representative random sample of all `.no` domains. Full paths, query and settings are in columnar-query.json.

DuckDB2.0.0/httpfs read the five requested output fields plus `fetch_time` for provenance and the required predicate columns. Timestamp is cast to text to avoid an optional Python timezone dependency. SQL filters TLDno, HTTP200, detected HTML and root/contact/about/privacy path substrings, then caps rows at two per registered domain and20,000 total. No full Parquet file is persisted. Two threads/external threads, disabled prefetching, long retry/backoff settings; no overlapping WARC phase while DuckDB was querying. The selection was cached and shuffled with seed20261111 for the deadline-limited archive phase.

Illustrative linear scenarios, **not defensible statistical estimates**:

- Project the observed1,141 matched parents to the selected record sample: multiply by20,000/12,493 ? approximately **1,827** matched parents.
- Naively extend that to all300 Parquet files using300/130 probed files ? approximately **4,215** universe companies, or **10.25 per1,000**.

The second scenario treats sequential, mostly zero-match files as exchangeable units even though `.no` data may be clustered, so it is **not a reliable full-`.no` coverage forecast**. No complete eligible `.no` page/domain denominator was measured; duplicate companies, domain cap, limit20,000, partial processing and missing parser outcomes further bias linear scaling. The observed1,141 matches and2.775 per1,000 are the supported measurements; no verified-coverage extrapolation is claimed.

## Extraction and mapping

At most two WARC requests run concurrently. Only indexed exact byte ranges are requested, HTTP206 and Content-Range/length checked; an ignored range is rejected before a whole archive is read. Bounded30/60-second backoff handles429/503 and transport/server failures. Members above8MB are explicit skips. Gzip WARC and embedded HTTP bodies are decoded in memory, including genuine chunked/gzipped payloads and archive-normalized bodies whose old headers remain. Visible text uses the unchanged agent Page parser.

Labelled Org.nr / Org. nr / Organisasjonsnummer / Foretaksregisteret / NO-number-MVA matches require nine digits and mod-11. Unlabelled numbers are excluded. Retain only orgnr/domain/URL/crawl/timestamp/120-character snippet plus exact parent-mapping metadata. Five domains with at least three different valid labelled IDs across checked pages were excluded wholesale: pascal-automasjon.no, propadel.no, regnskapsforere.no, romarheim.no, sandefjordtkd.no. This rule can also exclude genuine multi-entity websites.

Exact subunit-to-parent mapping uses cached official `overordnetEnhet`; absence from the current subunit bulk leaves a putative parent, not proof of main-entity status. Universe and bench100 intersections use exact parent numbers. OSM comparison uses the existing Stage1 candidate output only. Raw CDX selections, source manifests, parsed processing cache and live HTML remain ignored; no WARC byte cache exists.

## Live ownership check

Fixed seed20261111 selects20 universe-matched parent companies. Normal project User-Agent; homepage plus at most two same-site proof pages, robots and stricter crawl delays respected, at least1s per host, public-address checks and TLS verification, no HTTPS downgrade or alternate-host retries. Existing candidate_proof and Config defaults are unchanged. An archive nomination is never registry-declared trust or ownership proof. Missing parent contacts are not inferred; only allowed cached subunit contacts and universe legal names are supplied, so name-plus-parent-contact verification can be undercounted. Root-homepage checks may miss identity evidence confined to a company-specific path. Any checked owner conflict vetoes a pass. This is a proof measurement, not full collector acceptance or an independent wrong-company audit.

**13/20 passed**, all via existing orgnr-on-page proof. Six failed ownership proof or had a conflict; one had a TLS certificate-chain error. `live-review.json` retains URLs, proof types, localized excerpts, hashes and failures. Validation found **81** live requests including robots/redirects, minimum observed same-host spacing **1.0s**, at most three requested pages per site, all saved-body hashes matching. No source/proof limits were relaxed.

| Org number | Homepage | Existing proof |
|---|---|---|
| 984052243 | https://www.pgi.no/ | PASS |
| 930583693 | https://www.qvist-j.no/ | PASS |
| 938555222 | https://i.sjomannskirken.no/ | PASS |
| 920732291 | https://www.skolo.no/ | PASS |
| 985357455 | https://www.retretten.no/ | PASS |
| 934435206 | http://sanne-hauglid.no/ | NO PASS |
| 916848447 | https://www.pengvin.no/ | NO PASS |
| 922794383 | https://skamlost-forlag.no/ | PASS |
| 913625285 | https://www.share50.no/ | PASS |
| 890223222 | https://slottsgulv.no/ | NO PASS |
| 987665440 | https://personskadeadvokaten.no/ | NO PASS |
| 988406120 | https://scenemontage.no/ | PASS |
| 929166507 | https://www.sensrevisjon.no/ | NO PASS |
| 919251484 | https://www.sarkani-eiendom.no/ | PASS |
| 931949918 | https://www.prosess-styring.no/ | NO PASS |
| 957523730 | http://www.salbos.no/ | PASS |
| 917515743 | https://www.partech.no/ | PASS |
| 931084410 | https://www.pegasusbil.no/ | PASS |
| 999529860 | https://russelogo.no/ | PASS |
| 924293462 | https://simien.no/ | NO PASS |

## Sources and terms

Common Crawl access is subject to its Terms of Use and third-party content rights; do not overload the service, use at most two concurrent requests and back off on429/503. https://commoncrawl.org/terms-of-use ; index guidance https://index.commoncrawl.org/ . Free access does not supply a blanket redistribution licence for crawled website content.

Br?nn?ysundregistrene cached official subunit bulk: NLOD2.0, credit Br?nn?ysundregistrene. Builderr cached challenge universe: no licence statement in the JSONL; raw file not redistributed. OSM overlap source: **? OpenStreetMap contributors, ODbL1.0**; only comparison counts are derived here. No search engines, directory queries, Norid, credentials or paid APIs were used. Live access was restricted to candidate sites and their same-site proof/robots pages.

**Any in-agent use would need a bundled index; licensing and third-party content rights are a grey area to decide.** No production integration was performed. Short source snippets remain subject to source rights.

## Reproduce / artifacts

```powershell
uv run --no-project --with duckdb python scripts/cc_columnar.py
# Set fresh Unix UTC cutoff seconds for any explicitly authorized new archive run:
$env:CC_MEASUREMENT_DEADLINE = "<WARC cutoff epoch>"
$env:CC_LIVE_DEADLINE = "<live cutoff epoch>"
uv run --frozen python scripts/cc_proto.py --columnar
uv run --frozen python scripts/cc_finalize_report.py
```

The completed index selection is reused if cached. This record set is crawl-specific and source-file scoped. Query manifest and selected-record hashes, source/proof path, parser history and limits are preserved in reports. `columnar-run.json` records this task's actual start/deadlines; set new run metadata before a separately authorized rerun. Finalizer enrichment is offline and makes no requests. Do not restart archive work merely to extend this result after its cutoff.

No dependency/lockfile edits. Offline parsing, visible-only extraction, checksum rejection, ignored-range/cutoff guards, source hashes, sample caps, live spacing and protected-branch/code checks passed. No full agent test suite or benchmark was run because runtime code was untouched. Previous unsuccessful CDX attempts remain in cdx-summary.json/cdx-events.json; they are historical and superseded by these columnar results. Raw caches and full live HTML are gitignored; no raw Parquet, WARC, bulk or universe files committed. Nothing pushed.
