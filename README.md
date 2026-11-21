# Nordic Company Lens

Current measurement: **Stage BA, 21 November 2026**, frozen source commit `2d7b3cb343a5927fef47352e9226a9fc95e5864f`. The fresh default run completed all 1,000 companies and the full suite passed: **1,857 passed, 0 failed**. [Complete measurement, precision audit and reproducible evidence](bench/reports/final-ba/RESULTS.md).

Nordic Company Lens researches Norwegian companies using official registries and bounded company-owned sources. It checks company identity, publishes evidence-linked facts and cited template summaries, and can generate searchable offline profiles. The Python import package and console command remain `signalpost`.

## Install

Requires Python 3.12+ (tested on 3.12 and 3.13) and [uv](https://docs.astral.sh/uv/). From this repository:

```sh
uv sync --frozen
```

**Without uv.** Plain pip works too (tested on Linux with Python 3.13). This installs the agent from `pyproject.toml`; it does not use the lock file, so dependency versions are resolved fresh within the declared ranges:

```sh
python -m venv .venv
.venv/bin/pip install -e .
.venv/bin/signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

The test suite additionally needs the `dev` dependency group (pytest, respx): `.venv/bin/pip install pytest respx`, or `.venv/bin/pip install --group dev` with pip 25.1 or later. `uv sync --frozen` installs both the agent and the dev group from the lock file. On Windows, use `.venv\Scripts\` in place of `.venv/bin/`.

## Official run

For final measured coverage, sources, budgets and limitations, see [SUBMISSION.md](SUBMISSION.md).

The command writes a static offline site to `out/site`. Open `out/site/index.html` directly: search the directory by company name or organisation number, open a company, or compare two or three companies. The comparison URL preserves the selection; share that link together with the generated site folder. Source buttons show captured excerpts, URLs, retrieval dates and reporting periods. No CDN or web server is required. At narrow widths comparison cards stack vertically.

Each company has a deterministic cited analyst briefing, with detailed supporting facts and a three-part account of what it does, changes and remaining gaps. Source and run-metadata citations remain distinct. The same command and state folder automatically use the previous snapshot; transient failed refreshes preserve previous section state, supported claims and original evidence with a dated stale note.

Put one Norwegian organisation number on each line in `orgnrs.txt`, then run this command from the repository root:

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

Only `--organisations` and `--output` are required. Omitted `--report` and `--site-dir` default to `out/report.json` and `out/site`. Site generation stays on by default; `--no-site` skips it, including when `--site-dir` is supplied. Raw profiles are opt-in: `out/profiles.jsonl` is written only when `--profiles-output` is passed explicitly. Unknown arguments are ignored with a warning on stderr and recorded in the report; the report's `effective_configuration` records the actual feature settings, limits, NAV mode and source-cost counters.

This is the supported clean-checkout command: it needs no credentials and no `--bulk` file. The runner uses live official BRREG APIs for registry identity, roles, subunits and accounts. The input count is read automatically. Blank lines are retained as invalid input records, so each line produces one envelope (and one raw profile when `--profiles-output` is passed).

Malformed lines and invalid checksums retain explicit failed envelopes and appear in `report.json` under `invalid_inputs` and `invalid_inputs_count`; they do not make `run_status` failed. `success_rate` counts valid distinct identifiers only, and the site excludes invalid identifiers. A confirmed total identity-network outage exits 3 and records its warning in the report and stderr, including when a small batch has fewer than 25 live identity lookups. Invalid-only input exits 0. Install `httpx[socks]` support for environments using SOCKS proxy URLs. `runtime_ms` remains the crawl measure; `end_to_end_runtime_ms` includes site generation. Public brands from verified sites require a legal-name or domain token, at most six words, and a matching script. Offline review of the final 1,000 changed **0** existing brands.

Website research, NAV hiring checks, public activity and template synthesis are on by default. There is no search-engine integration; provider cost is $0. Use `--no-websites`, `--no-hiring` or `--no-public-activity` to opt out of those sources. `--expected-count` is optional and is normally unnecessary.

Requests use a pooled global ceiling of 1,900 per 100 distinct normalized input records, with at most 40 attributed to any one company. The default run time limit is 3,600 seconds (our own safeguard; the competition brief specifies no numeric limit), also bounded by a hard 24 seconds per distinct normalized input (40 minutes per 100). Lower configured limits remain effective. Careers checks run after primary collection using remaining budget, without earmarking or reducing the activity allowance. Incomplete careers coverage is reported honestly. The shared deadline and 40-request company ceiling still apply. Registry-declared websites require the legal name or hard registry corroboration; sites corroborated only by a contact or role-holder publish a website link without site content. Registered subunit identifiers can establish ownership. Shared domains, conflicting owners, parked pages and directories are withheld. Exact-name-only and contact-only two-signal publication were rejected in the Step 10 audit; guessed domains retain the stronger existing ownership proof.

Verified sites can supply individual active, dated job postings, including linked supported ATS pages. Careers landing pages are not jobs. Dated items retain the explicit date meaning from the fetched article, feed or index. Registered business addresses are typed separately from workplaces and duplicate addresses are suppressed.

Registry email domains and registered subunit website/email nominations can establish a declared site when the registered name appears in its title, main heading, site-name metadata, logo alt text or footer. Email/subunit declarations require the name; their contact-only trial was rejected after review. The existing direct registry-homepage Tier B rule remains link-only. Accounting/IT/hosting provider mismatches, placeholders, conflicting publishers and shared registry domains are rejected. Exact-name `.no` guesses additionally require registry-wide uniqueness and a registered contact, location or role-holder on the site. Site-linked ATS postings may use the verified company-to-board link chain instead of an employer orgnr; other employers, staffing-agency boards, expired ads and landing pages remain excluded.

Source research requires internet access. The `bench/inputs` files are for reproducible project benchmarks and are not needed for an official run.

## Run

To run the bundled benchmark instead, use its frozen input and registry snapshot and pass an explicit expected count. See [the Step 7 benchmark record](bench/reports/s6-step7/SCOREBOARD.md).

Input accepts plain text with one orgnr per line, JSONL strings/numbers, JSONL objects with an `organisation_number` field, JSON lists, or an object with an `organisation_numbers` list. Identifiers are normalized and checksum-validated. Output preserves input order and duplicates; duplicate companies share research. Invalid inputs retain explicit failed envelopes. Re-running the same command with the same `--state-dir` automatically refreshes against the latest complete snapshot; `--previous prior.jsonl` overrides it. Use `--deduplicate` to request unique output identifiers. See [the exact input/output contract](OUTPUT_CONTRACT.md).

## Outputs

- `out/envelopes.jsonl`: validated company envelopes, with verified claims, evidence, section states and cited summaries. The default shape is `union`; `contract` and `reference` are also supported.
- `out/profiles.jsonl` (only with `--profiles-output`): optional separate raw profiles from the same verified facts. Not required by the output contract.
- `out/report.json`: membership, source states, errors, requests, budgets, timing and cost.
- `out/site/`: optional static searchable company profiles with evidence excerpts. Open `index.html` locally. Site generation may be skipped if remaining time is insufficient.
- `out/state/` (for the command above): local evidence bodies, caches and progress. Keep the matching state when verifying evidence or carrying facts forward.

Exit zero means output was written for parsed input records. Inspect report warnings and source states: `complete` does not mean every source succeeded. Missing or unavailable facts remain explicit, without invented evidence. Refresh distinguishes supported company changes from source failures and retains original provenance for carried-forward facts.

## Sources and licences

Registry identity, roles, subunits and accounts come from official BrÃ¸nnÃ¸ysundregistrene APIs or the supplied registry snapshot. Registry data is attributed under NLOD 2.0. Optional hiring uses the official NAV feed and live detail verification against the exact company or registered subunit. Job claims cite the anonymous public ad page on arbeidsplassen.nav.no where it matches the verified ad; the feed is discovery provenance. The bundled NAV index is declared discovery metadata; it does not replace live evidence.

Website research follows robots, public-IP, redirect, request and time limits. Published website facts require the documented company-identity proof. Social profile links can be recognised on accepted company pages; social platforms are not fetched. Public activity keeps company-published articles, supported registry updates and exact-party procurement awards separately labelled. Registry updates use the official Enhetsregisteret API, not the robots-disallowed KunngjÃ¸ringer HTML service. Bundled SSB KLASS industry titles retain CC BY 4.0 attribution to Statistics Norway.

Bounded news discovery selects one advertised feed, sitemap or news index from a verified homepage. It publishes at most five explicitly dated items without expanding child sitemaps or article links. Publication, update and last-modification dates retain their distinct meanings; registry activity is separate.

Code and documentation use the [MIT licence](LICENSE). NAV, company websites and dependencies retain their own terms. See [source policy and dependency licences](docs/SOURCES.md) and [identity rules](docs/IDENTITY_RESOLUTION.md).

Wikidata's CC0 structured data is queried by exact P2333 organisation number for revision-cited official name, inception, headquarters, industry, employees/revenue with point-in-time qualifiers, website and social identifiers. Registry values prevail where they disagree; disagreements are recorded. Wikidata social identifiers retain the handle attribution test. Website nominations still need live ownership proof; Wikidata failures do not prevent registry or website research. Wikidata social claims identify their item URL and licence.

## Sources, licences and cost

| Source or service | Use in the official run | Licence / access terms | Provider cost |
|---|---|---|---:|
| BrÃ¸nnÃ¸ysundregistrene (BRREG) | Company identity, roles, subunits and accounts through the live official API | NLOD 2.0; attribute BrÃ¸nnÃ¸ysundregistrene | $0 |
| NAV public job feed and public ad pages | Feed: candidate discovery and live verification of active job details. Public ad page: the anonymous citation for each matching job claim | Public feed; [NAV reuse terms](https://arbeidsplassen.nav.no/vilkar-api) | $0 |
| Wikidata | Revision-cited exact-orgnr structured facts and website/social nominations | CC0; retain item attribution in claim provenance | $0 |
| Company websites | Ownership proof and company-published descriptions, social links and activity | Robots.txt and site access rules are followed; no open licence is inferred | $0 |
| GLEIF | Exact-orgnr LEI facts and explicitly supported parents | [CC0 1.0](https://www.gleif.org/en/meta/lei-data-terms-of-use); anonymous API, exact child matches under RA000472 or RA000473 | $0 |
| TED | Exact winner/buyer public procurement awards | [EU Publications Office reuse terms](https://ted.europa.eu/en/legal-notice); anonymous API and public notice XML | $0 |
| Doffin | **Not used** | Supported keyless API/access and reuse terms were not verified | - |
| KunngjÃ¸ringer HTML service | **Not used** | w2.brreg.no robots.txt disallows /kunngjoring/; no NLOD grant for this service assumed | - |
| Search engines | No integration | No provider is called | $0 |
| Language models | None; summaries use deterministic templates | No model provider is called | $0 |

No personal NAV credential is required. When `NAV_API_TOKEN` is unset, the runner retrieves NAV's published public token from `https://pam-stilling-feed.nav.no/api/publicToken` and keeps it in memory for that run; it is never logged or written to output or state.

The command has **$0 provider cost**. Compute, storage and network costs are excluded. `--synthesis` accepts `template` (default) or `auto`, which both use templates; `llm` is rejected.

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
