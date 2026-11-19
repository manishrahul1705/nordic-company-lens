# OpenStreetMap derived data

? OpenStreetMap contributors. `objects.jsonl` and `candidates.jsonl` are derived databases made available under the [Open Data Commons Open Database License 1.0](https://opendatacommons.org/licenses/odbl/1-0/), not repository MIT. [Copyright and attribution](https://www.openstreetmap.org/copyright).

Source: [Geofabrik Norway extract](https://download.geofabrik.de/europe/norway-latest.osm.pbf); retained extract header 2026-11-08T21:21:00Z. `pbf-manifest.json` pins the measured extract. `scripts/osm_extract.py` selects objects tagged `ref:NO:orgnr` and records identifiers, tags and nominated websites; `objects.jsonl` retains invalid numbers too. See README for the candidate filter and exact registry subunit mapping. Br?nn?ysundregistrene mapping data retains NLOD 2.0 terms and attribution.

Kept because `scripts/osm_measure.py` reads `objects.jsonl`, and `scripts/cc_finalize_report.py` uses the candidate dump for the reported overlap. No production-agent OSM integration is implied. Reusers must retain attribution and applicable ODbL obligations.
