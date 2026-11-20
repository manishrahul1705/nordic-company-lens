# Bundled research projects and state aid ? 20 November 2026

Both sources are now local snapshot indexes with **zero runtime HTTP**. No raw full download is committed. No push. The default runner publishes supported funding observations before refresh comparison, and the offline profile displays them in a separate Research projects and state aid section with normal evidence links.

## State-aid census before publication

The complete validated Støtteregisteret CSV contains **374,307 records**. Before building/publishing state-aid claims, `measure_recipients.py` matched the frozen cohort exactly: **98 / 1,000 legal recipients (9.8%)**, **675 direct-recipient records**. Direct records contain **647 tax benefits, 7 guarantees and 21 grants**. One cohort number appears separately in the specified-recipient-subunit field; that is not treated as another legal-recipient match. No new covered parent company is added through subunit-only recipients. See `recipient-census.json`.

Publication additionally finds **four other records** whose legal recipient is an explicitly registered subunit of an already covered cohort company. Each association cites that parent's own registry subunit claim. These raise published state-aid claims to **679**, still **98 companies**. Legal recipient, specified recipient subunit, and parent company association remain separate fields. All 679 award IDs are distinct. See `subunit-review.json` and `coverage-detail.json`.

## Sources, licence, acquisition and build

Contains data under [NLOD 2.0](https://data.norge.no/nlod/en/2.0) distributed by **Forskningsrådet** and **Brønnøysundregistrene**. Our modifications are selected-column projection, funded/registered filtering, exact organisation-number grouping and UTF-8 JSON/ZIP serialization. Source licence is not replaced by repository MIT.

| Source | Official CSV URL | Retrieved UTC | Dataset bytes | Dataset rows | SHA-256 |
|---|---|---|---:|---:|---|
| Research | https://raw.githubusercontent.com/Forskningsradet/open-data/main/datasets/soknader2/dataset.csv | 2026-11-20T02:01:57.524335Z | 54,010,790 | 88,268 | `5bd7ac2cfca44dfa6cba85bf644b172227fabf25114c28d22fa5a779f9d78485` |
| State aid | https://stotte.brreg.no/nb/oppslag/stoettetildeling/totalbestand/csv | 2026-11-20T02:13:46.546603Z | 341,137,852 | 374,307 | `cb708e62d03decf8e2a31dc60b99c2a2b1ad55985795f282d4f8491964d5e149` |

[Research distribution licence](https://data.norge.no/nb/datasets/349766ba-b5fd-3a04-8d82-77ec8928d6f2/soknader-til-og-innvilgede-prosjekter-fra-forskningsradet); [state-aid distribution licence](https://data.norge.no/nb/datasets/f634a11e-ed9c-30f4-916d-2cb1b7114e64/stotteregisteret). Source and access details are in `docs/SOURCES.md` and the bundled `FUNDING_SNAPSHOTS_NOTICE.md`.

**Robots finding:** stotte.brreg.no serves HTTP 200 HTML at robots.txt, not a parseable robots policy. This is not an explicit Allow directive. The user explicitly authorized one-off acquisition of its officially published NLOD bulk distribution, not crawling. Runtime does not contact it. Research uses its official raw-content CSV host, whose robots.txt returned 404; no Prosjektbanken scraping or certificate bypass occurs.

Acquisition was not literally a single HTTP attempt: the first state-aid JSON transfer ended at 73,674,008 of 536,276,574 declared bytes and failed JSON parsing. It was rejected. A Range probe was ignored (HTTP 200; response closed); metadata HEAD checks established lengths. The CSV alternative completed in 645.933 seconds with its exact declared 341,137,852-byte length and parses fully. Only this CSV is indexed. The research CSV completed once with the expected length/hash. Diagnostics are retained in `download-diagnostics.json`; all raw bytes remain ignored in `bench/cache/aid-snapshots-20261120`.

Development-only reproduction:

```powershell
python scripts/download_funding_snapshot.py research --directory bench/cache/funding-research
python scripts/build_funding_snapshots.py research bench/cache/funding-research/research.csv --download-manifest bench/cache/funding-research/research-download.json
python scripts/download_funding_snapshot.py state_aid --directory bench/cache/funding-state-aid
python scripts/build_funding_snapshots.py state_aid bench/cache/funding-state-aid/state_aid.csv --download-manifest bench/cache/funding-state-aid/state_aid-download.json
```

Downloads refuse overwrite and incomplete lengths. Builders verify the original dataset hash, official URL and successful direct HTTP status from the download manifest, parse strict CSV and reject malformed rows/duplicate IDs. The shipped indexes and manifests pin this retrieved snapshot; rebuilding from a changed upstream file requires deliberate pin and review updates. Runtime validates each bundled index hash against code and manifest, the exact official URL and licence. ZIP directory parsing is cached once per run. No request cap, host pacing, acceptance test or verifier rule is weakened.

## Bundled sizes and publication rules

| Index | Eligible indexed records | Recipient/responsible organisations in index | ZIP bytes | Frozen companies | Published claims |
|---|---:|---:|---:|---:|---:|
| `research_snapshot.zip` | 22,594 | 4,583 | **2,878,963** | **9** | **17** |
| `state_aid_snapshot.zip` | 374,102 | 60,729 | **30,088,648** | **98** | **679** |

The combined bundle size is **32,967,611 bytes**, excluding the small manifests/notice. Both indexes were previously absent, so the package grows by approximately 31.44 MiB. ZIP sizes include selected source-cell evidence, not only normalized values. No API key or runtime HTTP is required, including at 1,100 inputs; these are local indexed reads, not a new live wall-time benchmark.

**Research:** only `Bevilgning` and `Avsluttet` phases. Every published record is bound to the exact project-responsible organisation number. Publish project title/id, total project award, application date, start/end years and Forskningsrådet as funder. **Total project award is not the company's exclusive share or cash received**: partners may share funding. No collaborator allocation or name matching. The CSV has no explicit currency column, so no currency/conversion is invented. Application date is not award-decision date. Missing dates/years remain null; invalid/nonfinite/negative awards are excluded. Of all 31,926 funded-phase rows in the source, 22,594 have the required valid corporate orgnr/value basis; excluded funded rows are not published as corporate facts.

**Tibi limitation:** the provider says the dataset excludes its newer Tibi system, so research coverage is a **lower bound**, not proof that other companies received no support.

**State aid:** only `Registrert` records with valid corporate recipient numbers and explicit instruments; 204 otherwise registered nonqualifying rows and one illegal-aid record are excluded. Publish the original instrument with its English type, amount/currency or reported interval, awarding body, award date and scheme ID. An aid amount/element is not necessarily a loan/guarantee face value or cash received. Unknown instruments retain their original label rather than becoming grants. Personal birth dates and unused columns are not retained.

Published state-aid mix: **651 tax-benefit claims / 86 companies**, **21 grant claims / 13 companies**, **7 guarantee claims / 4 companies** (company sets overlap). The full snapshot also contains loan and other instrument types, tested by extraction tests; none appear as eligible frozen-cohort loan claims. The four registry-subunit additions are tax benefits.

## Proof, citations and refresh

Each claim cites the exact official CSV distribution URL, original data-record ordinal, full dataset hash, retrieval timestamp, and retained **derived selected-cell row extract** through normal evidence IDs, SHA-256 blobs, locator and a named extraction method. This is explicitly a CSV-to-JSON evidence derivation, not a claim that the provider returned JSON. Original selected cell strings are preserved; the runtime computes typed values again. Source column maps and encoding are in the manifest. No full raw download or personal/contact column is included.

No funding is published without an available registry identity. Subunit-recipient associations additionally require available, non-carried-forward own-company registry subunit evidence, which is added to the claim. No parent/sibling/collaborator inference. Snapshot values are historical observations, never described as freshly live-verified. No-match diagnostics say `not_established_in_snapshot`; missing/corrupt indexes say `snapshot_unavailable`, neither creates a zero/no-awards claim. Publication runs before refresh diffing so repeated identical snapshots do not create artificial removals/additions.

## Measured saved-run effect

Baseline: the official-BRREG-index replay `bench/runs/brreg-index-replay-20261120-new` (167,166 claims). New replay: `bench/runs/funding-snapshots-final-20261120`.

- **1,000 envelopes; 167,166 ? 167,862 available claims (+696).**
- **Zero prior claims removed.** Existing registry, website, social, TED, hiring and other facts remain unchanged.
- **103 companies** have at least one funding observation; four occur in both sources.
- **Zero new HTTP requests**. The saved acquisition count remains 11,477; it was not repeated.
- Replay wall: **78.868 seconds**, including loading existing envelopes, enrichment, synthesis regeneration and serializing output. This is not a measured incremental live-run wall cost.
- Fresh replay state hard-links immutable original evidence blobs and adds only its own 696 evidence extracts. The original saved output/evidence is not overwritten. Snapshot-generation/retrieval dates are retained, and replay completion is newly timestamped.
- Full offline site was not rebuilt; funding-aware rendering and package inclusion are checked separately. The source site remains scored/default ON in production; no site-default change was made.

See `measurement.json` and `new-claims.json`.

## Review and validation

[Ten hand reviews per source](REVIEW.md), with full company/value/citation details in `hand-review-20.json`. Research covers all nine companies plus a second project for one company. State aid includes three grants, two guarantees, four direct tax benefits and one subunit-recipient interval. All four actual subunit associations were checked against their own registry citations.

An independent audit rereads the original official CSVs and checks **all 17 research and all 679 state-aid claims** against exact rows, amounts, dates, identities, roles, instruments and original record ordinals. **PASS** (`audit.json`). An initial audit-helper error assumed the funding citation was first; subunit claims can have registry evidence first. The helper was corrected to select the exact CSV URL, without changing claims or weakening any checks.

The unchanged strict integrity verifier **PASS**: 1,000 envelopes, **167,862 claims**, 5,851 source blobs, 2,570 synthesis sentences, **zero unverified values**, 243.337 seconds. Same integrity mode as earlier stages, without the optional `--require-clean` source-health gate. See `strict-verifier.txt` and `verifier-timing.json`.

Final full suite: **1,686 passed, one warning, 461.70 seconds** (wrapper wall 465.528 seconds); exit zero. The warning is pytest cache-write permission denial, not a failed test. See `pytest.txt` and `pytest-timing.json`. Twenty-six funding tests cover extraction, provenance, subunit relationships and enabled-runner zero-HTTP integration. An initial run was interrupted after inefficient per-company ZIP reopening was found; the cache was fixed. A subsequent concurrent suite run failed an existing footer-ownership fixture at its deadline (474 passed before stop); the same fixture passes in isolation in 11.35 seconds without changing its test, time budget or proof rules. A subsequent sequential run reached 1,221 passing tests before a legacy 60 KB fixture output check failed: its synthetic Example AS uses a real organisation number with 96 funding records. Legacy registry fixtures now opt out of undeclared real funding snapshots, matching their existing Wikidata/registry-change isolation; the 60 KB assertion remains unchanged. An enabled-runner integration test separately verifies default-on publication and zero funding HTTP. The final suite passed without concurrent replay/verifier/wheel workload. Earlier logs are retained rather than hidden.

Wheel build succeeds and both ZIP indexes, both manifests and the NLOD notice match the local bytes (`wheel-check.json`). The raw downloads are ignored and not staged. No push; changes remain uncommitted until requested.
