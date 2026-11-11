# Stage 1 result: unavailable (11 November 2026)

Primary endpoint: HTTP 502. Single fallback after 60 seconds: read timeout (client timeout 960 seconds; query timeout 900 seconds). Neither returned usable OSM data. No further query was sent. Universe download succeeded: **411,160 distinct companies**; all org numbers passed mod-11 validation. Official subunit bulk downloaded successfully and has the expected parent field. Raw/bulk files stay ignored; SHA-256 hashes and sizes are in download.json.

OSM object counts, parent coverage, cohort matches, expected matches per 1000 and ownership-proof pass rate are **unmeasured**, represented as null in summary.json. The 20-company live review could not start; empty candidates.jsonl does not mean zero OSM candidates. No successful raw OSM JSON exists to gzip; the initial request code did not retain the primary error body. No request was repeated to retrieve it.

No production code changed. The script now records failed attempts separately and refuses to submit another query when attempts are recorded. Another attempt requires explicit authorization; do not simply delete the attempt ledger. The offline --report-unavailable option rebuilds the unavailable report from local cached files without network calls. Stage 2 was not started.

# OpenStreetMap candidate measurement (Stage 1 only)

OSM data is ODbL 1.0, requiring attribution: © OpenStreetMap contributors; derived candidate data is supplied under ODbL 1.0. https://www.openstreetmap.org/copyright and https://opendatacommons.org/licenses/odbl/1-0/

Overpass is keyless, shared fair-use infrastructure: use modest traffic, respect resource limits and cooldowns. This measurement sends one query to overpass-api.de, with one fallback to overpass.kumi.systems after a 60-second pause on failure, never a tight retry loop. https://dev.overpass-api.de/overpass-doc/en/preface/commons.html

Brønnøysundregistrene subunit and entity data: NLOD 2.0; source https://data.brreg.no/enhetsregisteret/api/dokumentasjon/en/index.html. Subunit-to-parent mapping uses the official complete subunit CSV, not name inference.

Run from this branch/worktree with the repository dependencies installed:

```powershell
uv run python scripts/osm_check.py
```

The script caches raw downloads under `raw/` (ignored), saves OSM JSON gzipped, validates org numbers with the unchanged production mod-11 validator, takes the first semicolon-delimited website value from website / contact:website / url in that order, and maps exact subunit numbers to parent companies. Derived `candidates.jsonl` retains one row per qualifying OSM object, so duplicate sites/companies remain visible. Summary company counts deduplicate parent numbers.

The universe coverage expectation is `1000 * matched distinct parents / distinct universe companies`; it is nomination coverage, not verified website coverage or incremental recovery beyond existing agent sources. Live review samples up to 20 distinct matching parents with seed 20261111 and chooses the first OSM object for each. It fetches current official registry identity/contact data, checks robots, then fetches that one website (redirects followed, no alternate host/path retries), TLS verification enabled. Saved body hashes and proof outcomes are in `live-review.json`; raw bodies are ignored. Unavailable/blocked/failed pages count as non-passes. Ownership uses the existing `proof.score` with origin `osm`, default opt-in proof features OFF, parent identity only and no follow-up pages. This is a proof measurement, not a full collector acceptance or production integration. Website content remains subject to its owners' terms; full bodies are not committed.

Stage 2 Common Crawl is deliberately not started: Stage 1 must first be reported. No production agent code changes, benchmarks, push or workflow dispatch are part of this measurement.
