# Submission notes

Current measurement: **Stage BA, 21 November 2026**, frozen source commit `2d7b3cb343a5927fef47352e9226a9fc95e5864f`. The fresh default run completed all 1,000 companies and the full suite passed: **1,857 passed, 0 failed**. [Complete measurement, precision audit and reproducible evidence](bench/reports/final-ba/RESULTS.md).

## Official command

Requires Python 3.12+ (tested on 3.12 and 3.13), uv and internet access. From a clean checkout, install locked dependencies with `uv sync --frozen`, put organisation numbers in `orgnrs.txt`, then run:

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

**Without uv.** Plain pip works too (tested on Linux with Python 3.13). This installs the agent from `pyproject.toml`; it does not use the lock file, so dependency versions are resolved fresh within the declared ranges:

```sh
python -m venv .venv
.venv/bin/pip install -e .
.venv/bin/signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

The test suite additionally needs the `dev` dependency group (pytest, respx): `.venv/bin/pip install pytest respx`, or `.venv/bin/pip install --group dev` with pip 25.1 or later. `uv sync --frozen` installs both the agent and the dev group from the lock file. On Windows, use `.venv\Scripts\` in place of `.venv/bin/`.

No credentials, bulk file, expected count, LLM or search service are required. NAV's published public token is fetched in memory from `https://pam-stilling-feed.nav.no/api/publicToken`; no personal credential is required or persisted. Provider cost is **$0**; local compute, disk and network are excluded.

## Input and outputs

The command accepts plain text (one orgnr per line), JSONL strings/numbers or objects with `organisation_number`, JSON arrays, and objects with an `organisation_numbers` array. Whitespace is normalized, checksums are checked, input order and duplicates are preserved. Blank/invalid lines each receive a failed envelope (and a failed profile when `--profiles-output` is passed). The expected count is inferred from the input. See [OUTPUT_CONTRACT.md](OUTPUT_CONTRACT.md).

Invalid lines are listed in `invalid_inputs` and counted in `invalid_inputs_count` while `run_status` remains `completed` when all valid distinct inputs succeed; `success_rate` uses only those valid distinct inputs. The site omits invalid-checksum identifiers. A confirmed total identity-network outage exits 3 with a report and stderr warning. `end_to_end_runtime_ms` includes site generation. Verified-site public brands require a legal-name or domain token, at most six words, and a matching script; offline replay changed **0** existing brands in the final 1,000.

- `out/envelopes.jsonl`: one schema-validated envelope per input, with claims, citations, evidence, section states and refresh changes.
- `out/profiles.jsonl`: optional raw profiles, written only when `--profiles-output` is passed.
- `out/report.json`: membership, requests, time, errors, source completeness and cost.
- `out/state/`: captured evidence, caches and automatic previous snapshots. Keep this directory with the outputs.
- `out/site/`: static offline directory, company pages, comparisons and source panels. Open `index.html`; no CDN/server is required. Optional site generation can be skipped if time is exhausted.

Run the **same command again with the same state directory** to refresh automatically; `--previous` is unnecessary. Previous/current supported values are compared, original evidence is retained, and transient failed refreshes preserve previous section state and claims with a dated stale note. They do not count as company changes. First-ever failures remain honest failed states; successful proof of real additions/removals is treated as change. Exit zero means outputs were emitted, not that every source succeeded.

## Sources, licences and costs

| Source | Use | Licence / access | Provider cost |
|---|---|---|---:|
| BRREG | Identity, registered roles, subunits and returned financial years | NLOD 2.0; attribute BrÃ¸nnÃ¸ysundregistrene | $0 |
| NAV public feed and public ad pages | Active individual ads, exact employer/subunit matching; public token obtained at runtime. Job claims cite the anonymous public ad page when it matches the verified ad | NAV public-feed reuse terms; no personal credential | $0 |
| Wikidata | Revision-cited exact-P2333 name, inception, headquarters, industry, employee/revenue time series, website and social identifiers; registry disagreements retained | CC0, item provenance retained | $0 |
| Company websites | Ownership proof, descriptions, social links, dated news, linked active jobs | robots.txt and site access rules; no blanket open licence inferred | $0 |
| SSB KLASS | Bundled industry descriptions | CC BY 4.0 | $0 |
| LLM / search engines | No integration; deterministic cited templates | No provider called | $0 |
| GLEIF | LEI/status/form/dates and explicit direct/ultimate parents | CC0 1.0; anonymous exact orgnr + RA000472 or RA000473 child match, batched parent LEIs | $0 |
| TED | Exact winner/buyer public procurement awards | EU Publications Office legal notice/Commission reuse policy; anonymous published-notice API and public XML | $0 |
| Doffin | **Not used** | Keyless supported API/access and reuse terms not verified | - |
| KunngjÃ¸ringer HTML service | **Not used** | robots.txt disallows /kunngjoring/; service-specific NLOD coverage not verified | - |

See [docs/SOURCES.md](docs/SOURCES.md) and [LICENSE](LICENSE) (code/documentation: MIT). Social destinations are not crawled. A brand/name match alone does not establish company ownership; ambiguous/shared/foreign group sites are withheld. Contact-only direct-registry Tier B sites publish a link without website content.

**DNS fallback.** Bounded public-resolver fallback is name resolution only; it never performs a search. See [source and DNS policy](docs/SOURCES.md).

## Bundled website candidates and registry-backed proof

Common Crawl's bundled `data/cc_orgnr_index.json.gz` is described authoritatively under [Bundled-index provenance](#bundled-index-provenance). Runtime reads it locally by organisation number; it does not query Common Crawl. Domains are candidates only, ranked after registry nominations and before name guesses. Every candidate is fetched live and must pass the existing ownership proof and all applicable directory, parked-page, foreign-owner, group/shared-site, robots, DNS, TLS and request-budget checks. See [Common Crawl Terms of Use](https://commoncrawl.org/terms-of-use) and the third-party rights notice in `data/CC_INDEX_NOTICE.md`; no blanket licence for crawled site content is claimed.

The bundled `data/shared_identifiers.json.gz` counts registered phone/mobile numbers, email domains and distinctive legal-name keys from the official Bronnoysundregistrene entity bulk CSV. Attribution: Bronnoysundregistrene, [NLOD 2.0](https://data.norge.no/nlod/en/2.0). It is read locally, without a runtime registry bulk download. Build hashes and counts are in `data/shared_identifiers_build.json`; the complete gzip is 8,676,502 bytes, above the 3 MB target. Missing keys do not establish uniqueness.

Additional website proof can use the exact registered email visible in text or mailto links only when its non-free-mail domain is registered to exactly one entity; or a registered phone/mobile visible on the page when fewer than five entities register it. Both require a positive count in the snapshot and a nonempty non-placeholder page. The exact legal name, including its legal form, must also identify the publisher in the title, heading or footer; a staff/adviser contact alone is not ownership proof. Name-only masthead and unique-name-domain publication were removed after the R3 precision review exposed namesake and placeholder risks. Existing stronger proofs keep their labels. None of these rules overrides an existing rejection or owner conflict.

Current operational ceilings are specified in [Budgets](#budgets); these additions contain no search-engine, directory, Norid or model-provider requests. There is no search-engine integration.

### Bundled-index provenance

The archived collection was produced by [`cc_overnight.py`](scripts/cc_overnight.py), its [columnar selector](scripts/cc_overnight_select.py), and the [supervisor](scripts/run_cc_overnight.ps1)/[worker](scripts/run_cc_overnight_worker.ps1) launchers. The offline [`build_cc_candidate_index.py`](scripts/build_cc_candidate_index.py) turns those records into the bundled index. The [overnight summary](bench/reports/cc-proto/overnight-summary.json) is an earlier heartbeat, not the final index snapshot. These are historical measurement tools: after `uv sync --frozen`, prepare the ignored official subunit/universe caches described in the scripts; DuckDB/httpfs is installed ephemerally by the selector. The recorded 13 November cutoff is intentionally retained, so invoking the archived launchers now makes no crawl requests. Raw downloads are not bundled or committed.

`data/cc_orgnr_index.json.gz` was built 13 November 2026 from partial archived records in CC-MAIN-2026-43,2026-39 and2026-34. It contains 20,832 candidates for 19,735 parent companies. Access/use is subject to [Common Crawl Terms of Use](https://commoncrawl.org/terms-of-use) and third-party rights; see [the bundled terms/method notice](data/CC_INDEX_NOTICE.md). Official Bronnoysund subunit data (NLOD 2.0) maps branch numbers to parents. **Candidate coverage is not verified-site coverage**: every candidate is fetched and re-verified live under the ownership proof and vetoes.

`src/signalpost/data/nav_index.json.gz` was built 2026-11-13T00:26:42.872674Z from the official public NAV feed using public access (9,296 ads / 5,899 employers). No private credential is required or bundled. The runtime retrieves NAV's published public token in memory, validates the index and live-checks nominated ads; missing, invalid or stale indexes retain the honest full-feed fallback. Source terms and limitations are in [SOURCES.md](docs/SOURCES.md).

### NAV hiring coverage investigation (19 November 2026)

The three hiring companies per frozen 1,000 were checked against a separate live 20-company route investigation, including four audit candidates and all three published companies. The documented feed ignored attempted organisation/employer filters; the retired public-feed path returned 404 with the current token. The current search page returned suffix-free keyword candidates for 9/20 companies, but candidates were not accepted on names alone. Of 39 candidate UUIDs, 29 returned details and ten were unavailable; exact employer and registered-subunit checks verified only the same three companies already published. The JSON search compatibility endpoint was rate-limited for 19/20 probes; those responses remain unknown, not zero ads. This demonstrates that the family was investigated, not that NAV coverage is exhaustive. [Full NAV investigation](bench/reports/nav-live-routes-20-20261119/RESULTS.md), [exact HTTP table](bench/reports/nav-live-routes-20-20261119/HTTP-TABLE.md), [20-company evidence](bench/reports/nav-live-routes-20-20261119/matrix.json).

All three published ads use **registered subunit employer numbers**, not the parent numbers: EIDEFOSS VANNKRAFT AS `923354220` -> `981955234`; ROSENLUND BARNEHAGE SA `960213912` -> `972285501`; NORLANDIA ENGA BARNEHAGE AS `930202894` -> `997453964`. Each mapping came from that parent's verified BRREG subunit record, and the live NAV detail named the same subunit employer. Parent-only queries and keyword hits are not substitutes for this proof.

## Budgets

The pooled HTTP hard cap is 19 per distinct normalized input: 1,900 per 100, with at most 40 attributed to any company and shared calls included globally. The hard time cap is 24 seconds per distinct input (40 minutes per 100), with the default 3,600-second run limit (our own safeguard; the competition brief specifies no numeric limit) and lower configured limits honored. These are tighter than 2,000 HTTP / 45 minutes per 100. Crawl finalization reserves preserve one output per input even when discovery is incomplete. Public DNS fallbacks are bounded and tolerate blocked UDP; end-of-run retries consume the original pool. The envelope output cap (`--max-output-mb`) defaults to 4,096 MiB. It is a local safety ceiling, not an evaluator limit, and remains an enforced ceiling rather than a guarantee against truncation.

## Stage BA final combined measurement

Standard CLI defaults, fresh state, site ON, frozen `bench/inputs/1000-r3/batch.jsonl`, source `2d7b3cb`. **run_status completed; success_rate 1.0 (1,000/1,000)**. Crawl **1,038.14s**; end-to-end **1,520.578s** including site publishing (`end_to_end_runtime_ms=1,520,578`). Output finalisation was 177.89s and the site build was 292.66s. The default envelope output was **496,624,523 bytes / 4,294,967,296-byte cap** (11.56%); the site separately used **1,032,289,235 bytes** and produced 5,617 pages / 1,000 profiles. **11,562 / 19,000 HTTP**, maximum **40 per company**, **0 deadline hits, 0 handled or unhandled exceptions**.

Linear projection for 1,100: **1,672.636s / 3,600s** and approximately **12,719 / 20,900 HTTP**. This is conditional on similar source and network conditions. HTTP ceilings remain **19 pooled per distinct normalized input and 40 attributed per company**, including retries and shared requests globally. Lower configured limits apply.

### Full family table

Counts are published claims in this one run. Rows overlap; do not sum them. All families were nonzero. The total is **236,654 claims**, **57,985 above Stage AP's 178,669**.

| Family / information type | Companies | Claims |
|---|---:|---:|
| Identity | 1,000 | 48,334 |
| Roles | 997 | 43,250 |
| Accounts | 999 | 105,867 |
| Audit status, per year/scope | 999 | 2,817 |
| Registry-date activity | 997 | 7,714 |
| Previous legal names of subject company | 241 | 324 |
| Historical names including subunits | 302 | 701 |
| Subunit historical names | 210 | 377 |
| Subunits | 773 | 17,664 |
| Group structure | 75 | 119 |
| Signatur | 765 | 765 |
| Prokura | 201 | 201 |
| Registry changes | 1,000 | 12,052 |
| GLEIF | 142 | 736 |
| TED procurement awards | 2 | 4 |
| Wikidata structured claims | 13 | 47 |
| Verified official websites | 115 | 115 |
| Public brands | 36 | 36 |
| Social profiles | 62 | 126 |
| News / dated company items | 32 | 115 |
| Hiring | 3 | 3 |
| Research projects | 9 | 17 |
| State aid | 98 | 679 |
| SkatteFUNN | 36 | 89 |
| DiBK central approvals | 14 | 69 |
| Cleaning register | 6 | 6 |
| Workshop approvals | 1 | 2 |
| Related-company declared websites | 14 | 16 |

### Accuracy, attribution and tests

Strict verifier **PASS**: 1,000 schema-valid envelopes, 236,654 claims, 6,002 verified source blobs, 2,560 synthesis sentences and **zero unverified synthesis values**, exact input membership/order. The Stage X stratified 200-claim sample (seed 20261119) was **200/200 correct**, zero wrong/doubtful; **165 mechanical and 35 source-reviewed**; Wilson 95% lower bound **98.12%**.

The unseen-300 fresh run retained 316 output rows, completed 310 valid companies and reported **3 invalid inputs**. Its site has **310 profiles**, with invalid identifiers skipped. A separate jury seed-7 sample of 100 claims, stratified across the 300 active companies, was **100/100 correct** (80 exact mechanical checks, 20 saved-source reviews). **Uniktur has no published brand claim** in this output. The output and checks are in [jury-precision review](bench/reports/final-ba/jury-precision/REVIEW.md).

Attribution audit: four raw shared official bulk-URL flags; 791 exact subject-row checks, including four explicitly scoped registry-subunit rows; **zero subject mismatches and zero cross-company contamination**. Accuracy and attribution reproduce from the committed extract without `bench/runs`: [reproduction instructions](bench/reports/final-ba/accuracy/REPRODUCE.md). The initial strict verification passed; a later repeat could not read one state blob after its path disappeared. [Details](bench/reports/final-ba/strict-verifier.txt).

The full suite passed: **1,857 passed, 0 failed**. One pytest cache warning reported denied permission writing `.pytest_cache/v/cache/nodeids`; it did not affect test outcomes. [Detailed report and logs](bench/reports/final-ba/RESULTS.md).

## Added sources and licences

| Source | Publication / access | Licence or terms |
|---|---|---|
| ForskningsrÃ¥det research projects | Bundled funded-phase snapshot; total project awards, not exclusive company funding | ForskningsrÃ¥det, [NLOD 2.0](https://data.norge.no/nlod/en/2.0); excludes newer Tibi system |
| StÃ¸tteregisteret state aid | Bundled exact-recipient snapshot, actual instrument labels and explicit subunit scope | BrÃ¸nnÃ¸ysundregistrene, [NLOD 2.0](https://data.norge.no/nlod/en/2.0); no parseable robots file, officially published bulk download rather than crawl |
| SkatteFUNN | Bundled approved applications, exact orgnr, deduplicated project numbers; R&D tax deduction scheme, never a cash grant | ForskningsrÃ¥det, [catalogued NLOD 2.0](https://data.norge.no/nb/datasets/f82d3d4a-b0f8-3220-83ef-15fbd854c54f/innsendte-soknader-til-skattefunn); current provider workbook substituted for stale catalogue distribution |
| DiBK central approvals | NACE-gated live enterprise HTML pages; exact orgnr, status, area/class/function and dates | Direktoratet for byggkvalitet attributed; public register access, no HTML factual-reuse prohibition found. API documentation's CC BY 4.0 is not asserted for the HTML site. Robots allows enterprise pages; /api/ and /search never called |
| Cleaning register | Bundled main-unit exact-orgnr statuses; only explicit approved statuses labelled approved | Arbeidstilsynet, [NLOD 2.0](https://data.norge.no/nlod/no/2.0); robots 403, official bulk download only |
| Approved workshops | Bundled main-unit exact-orgnr approval numbers, type/location | Statens vegvesen, [NLOD](https://data.norge.no/nlod/no) (catalogue does not specify version); export-backend robots 404, frontend no disallow; official bulk only |
| Verified-site news | One advertised same-domain resource, at most five dated items; normal robots/pacing/caps | Company-published material, no blanket open licence inferred; exact fetched evidence and date meaning retained |

Research, state aid, SkatteFUNN, cleaning, workshops and related-entity registry website snapshots use **zero runtime HTTP**, retain deterministic manifests/hashes/attribution and do not bundle raw downloads. Related-entity website data is official BRREG [NLOD 2.0](https://data.norge.no/nlod/en/2.0). Full derivation, licence basis, URLs, robots findings and restrictions: [docs/SOURCES.md](docs/SOURCES.md), [DATA_LICENSING.md](DATA_LICENSING.md).

## Proof and synthesis

Registered group relationships, signatur and prokura require explicit company registry records. Accounts audit status uses both explicit boolean fields: opted-out, audited or not-audited; missing/contradictory values are withheld. Explicit registry dates add dated activity without replacing identity claims; historical names retain only source-stated dates.

Social links on a proven company website use that site's ownership evidence without requiring legal-name/handle equality. Personal forms (including LinkedIn /in/), own role-holder handles, other registered-company matches across the full bundled universe (except explicitly related entities), shared/group profiles, share/intent/tracking and platform homepages remain vetoed. Wikidata social claims retain their separate handle-attribution rule. Social platforms are not fetched.

Funding synthesis preserves actual instruments and recipient/subunit scope; research amounts are total project awards. Dated news is labelled published by the company, with lastmod distinguished from publication. No funding match produces no negative funding assertion. Every sentence cites published, evidence-backed claims under the unchanged validator/verifier.

## Known limitations

- TED depends on upstream XML readiness: HTTP 202 opens the breaker with periodic re-probes; **2 companies / 4 awards** in Stage BA; 28 TED requests returned HTTP 202 and the configured circuit breaker skipped further notices. This is limited source coverage, not evidence that no more awards exist.
- Hiring is limited by NAV feed discovery/availability; all three published ads use proved registered-subunit employer numbers. [Route investigation](bench/reports/nav-live-routes-20-20261119/RESULTS.md).
- Websites are verified-only (**115**); bounded discovery, static HTML, robots, transient failures and strict proof can miss genuine sites.
- Related-company websites are **registry-declared, not ownership-verified**, and are not official_website claims.
- SkatteFUNN licence basis is the catalogue's NLOD 2.0 dataset listing; its nov24 distribution returned 404 on 20 November 2026, so the provider's current publication of the same dataset is treated as covered. [Exact basis](docs/SOURCES.md#skattefunn-historical-approvals-bundled-zero-runtime-http).
- Stage AI's baseline **"Registered name"** sentence cites the registry identity claim; it does not assert first observation or absence of prior facts. Repeat-run refresh handling is unchanged.
- Research excludes Tibi; snapshots can age, absence is not proof of no funding/approval, company news is not independent verification, and optional source failure does not invalidate all terminal results.

No LLM, paid API or search-engine scraping is used. Financial scope/currency/period mismatches are not reconciled by guessing. No JavaScript rendering or scanned-PDF extraction is provided. Local antivirus can quarantine retained fetched evidence; historical incidents are recorded in [Stage G](bench/reports/stage-g/defender-evidence.json).
