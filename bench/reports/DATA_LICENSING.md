# Review-data licensing review ? 20 November 2026

This review inventoried 1515 tracked report files by extension: `{".css": 1, ".csv": 1, ".html": 11, ".js": 1, ".json": 766, ".jsonl": 7, ".md": 146, ".patch": 14, ".png": 253, ".py": 25, ".sh": 1, ".txt": 283, ".woff2": 2, ".xml": 1, ".xz": 2, ".yaml": 1}`. It checked the seven JSONL dumps, the two compressed Stage X extracts, the saved source HTML/XML, generated site assets and existing source notices. This is a provenance/notice review, not a grant of rights over third-party material or a fresh line-by-line accuracy review of every evidence excerpt. Historical reports and test logs retain their measured counts; the latest saved suite is 1,656 passed, linked from README.

| Material | Derivation and terms |
|---|---|
| `osm-check/objects.jsonl`, `osm-check/candidates.jsonl` | Geofabrik OSM extraction; ? OpenStreetMap contributors, [ODbL 1.0](https://opendatacommons.org/licenses/odbl/1-0/). See [adjacent notice](osm-check/NOTICE.md), README and manifests. These are cited measurement inputs and are retained. |
| `cc-proto/candidates.jsonl` | Common Crawl website nominations; CC access terms do not grant blanket rights to crawled content. Registry mappings retain NLOD 2.0; OSM overlap attribution is in its README. |
| `stage-x-accuracy/**/sample.jsonl`, `verdicts.jsonl` | Agent-output samples and our review verdicts; embedded registry facts and website evidence retain source terms in SOURCES. Review annotations do not relicense underlying material. |
| `stage-x-accuracy/extract/{blobs,envelopes}.jsonl.xz` | Compressed output/evidence extracts; compression does not change rights. Original evidence URLs/hashes identify the source; website text remains subject to its original rights. No blanket open-content licence is asserted. |
| `s6-step20/source-verification/doffin-index.html`, `ted-award-example.xml` | Saved official-source verification material; retain source rights and Doffin/TED reuse terms described in SOURCES. Repository MIT applies only to our own contributions. |
| `stage-v/site-pages/` | Generated report HTML/CSS/JS and cited third-party facts; fonts have adjacent `inter-OFL.txt` and `fraunces-OFL.txt` notices. |
| Other JSON, logs, screenshots and reviews | Our measurements/annotations plus source-specific evidence and excerpts; registry NLOD, Wikidata CC0, NAV terms and website rights remain applicable as described in SOURCES. Screenshots do not confer rights to embedded content. |

The competition archive has no licence statement in the saved JSONL. Its derived bundled domain/name indexes have an unresolved upstream redistribution licence; see [SOURCES](../../docs/SOURCES.md). Do not infer NLOD from the archive's registry-like fields or MIT from its location in this repository.

No dump was deleted. The OSM inputs are referenced by measurement code and carry explicit attribution and the direct data-licence link. Report content is not a new production source, and none of these notices authorizes publishing unverified claims.
