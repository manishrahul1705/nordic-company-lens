# OSM website measurement — Geofabrik PBF

Measurement only on `more-websites`; no production-agent, dependency/lockfile or protected-branch changes. No search engines, directories, Norid, credentials or paid APIs used. Common Crawl not started.

## Measured result (11 November 2026)

- PBF: **1,378,571,576 bytes**; header **2026-11-08T21:21:00Z**. SHA-256 in pbf-manifest.json. Native-filter extraction: 64.297 seconds (download excluded).
- Tagged objects: **11,172**; checksum-valid: **11,163**; excluded invalid: **9**.
- Valid orgnr + website: **5,103 objects**; **4,851 (95.06%)** have mapped subunit numbers. Across all valid objects, **9,630 (86.27%)** are mapped subunits.
- Distinct mapped-or-putative parents with a website: **2,330**. Universe intersection: **1,641 / 411,160**; expected nominations per random 1,000: **3.99**. Frozen bench100 matches: **0**.
- Live ownership sample: **4 / 20 pass**; **7** no accepted proof/owner conflict; **9** transport/policy unavailable. Missing parent contacts may undercount contact proof. This is not a verified-coverage extrapolation or production integration.
- Validation: at most homepage plus two proof pages; **58** requests including robots/redirects; observed minimum host spacing **1.0 seconds**; all body hashes passed. No production code, tests or lockfile changes; protected branch refs unchanged.

## Sources and licences

- Geofabrik Norway extract: ODbL 1.0; attribution **© OpenStreetMap contributors**. Source https://download.geofabrik.de/europe/norway-latest.osm.pbf ; licence https://www.openstreetmap.org/copyright and https://opendatacommons.org/licenses/odbl/1-0/ . Derived `objects.jsonl` and `candidates.jsonl` are supplied under ODbL 1.0.
- Brønnøysundregistrene official subunit bulk: NLOD 2.0; credit Brønnøysundregistrene. https://data.brreg.no/enhetsregisteret/api/underenheter/lastned/csv . Exact `overordnetEnhet` mapping; no name-inferred relationships.
- Builderr challenge universe: https://builderr.ai/signalpost-company-universe-2025.jsonl.gz . No licence statement in downloaded JSONL; raw challenge input is not redistributed.

**Any future in-agent use needs a bundled ODbL-licensed index; integration and licensing design remain to be decided.** An OSM website is only a nomination, never ownership proof.

## Reproduce

```powershell
uv run --no-project --with osmium python scripts/osm_extract.py
# Use the existing project environment/dependencies for the unchanged proof imports:
uv run --frozen python scripts/osm_measure.py
```

`osmium` is ephemeral; pyproject.toml and uv.lock are unchanged. The cached PBF is read locally with a native pyosmium key filter; no geometry lookup. All nodes, ways and relations tagged `ref:NO:orgnr` are retained in `objects.jsonl`, including invalid numbers for transparent counting. Main category is the first present key in shop/craft/office/amenity/tourism/leisure/healthcare. Website uses website/contact:website/url priority, taking its first semicolon-delimited value. `candidates.jsonl` includes only checksum-valid nine-digit numbers with websites, retaining one row per OSM object (not deduplicated).

Raw PBF, bulk CSV, universe and live HTML are ignored under `raw/`. The PBF transfer initially ended early; received prefix was retained, date-matched HTTP ranges fetched only missing bytes, and final size checked. `scripts/osm_resume.py` preserves the bounded range recovery procedure. `pbf-manifest.json` records header date, size, SHA-256 and extraction counts. Cached supporting file hashes are in download.json. No further Overpass queries were sent; download.json retains historical outage evidence.

Numbers absent from the current subunit bulk remain unmapped and are treated as putative parent numbers; absence is not proof of current main-entity status. Universe intersection uses exact mapped-or-unmapped parent numbers. Expected matches per 1000 is `1000 * matched distinct parents / 411160`, describing nomination coverage only—not incremental recovery or verified websites. Chain/shared sites and duplicate domains remain in object-level output.

## Bounded live ownership check

20 distinct universe-matched parents, fixed random seed 20261111, first OSM object per parent. Homepage here means the nominated entry URL (including a company/branch path when OSM provides one); up to two same-site proof pages selected with existing proof-page targeting. No alternate-host or path retries. Redirects stay within the same registrable domain and cannot downgrade HTTPS. Known directories/social sites and non-public addresses are refused using existing policy helpers.

Normal project User-Agent from Config; at most one request per second per host, including robots and redirects; robots crawl delays/request rates honored when stricter. Robots are checked before page fetches, with unavailable/disallowed robots recorded as non-passes. TLS verification stays enabled; no credentials or environment proxies used. Request starts/statuses are recorded in live-requests.json. Failures count as non-passes, not as absence of a legitimate company website.

The unchanged `candidate_proof` and current Config defaults evaluate each retained page with origin `osm`, never registry-declared trust. Legal names come from the universe; registered subunit identity/contact data comes from the cached official bulk. Missing parent contacts are not inferred or fetched from other sources, which can undercount name-plus-parent-contact proof. Any checked explicit owner conflict vetoes a pass. This measures ownership proof, not full collector/publication acceptance or a wrong-company audit. Page hashes and localized proof excerpts are in live-review.json; full bodies stay ignored. Existing opt-in proof behavior is not altered.

Historical Overpass measurement: primary HTTP502 and single fallback timeout, no usable response. The Geofabrik result in summary.json supersedes its unmeasured coverage fields. Do not run the old scripts/osm_check.py network entry point; it preserves the exhausted-attempt guard.
