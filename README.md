# Nordic Company Lens

Current measurement: **Stage AP, 20 November 2026**, source commit `cede54701d5e50067764f472009b6c830254065a`. All figures below refer to that one fresh frozen 1,000-company run. **1,852 tests: 1,850 passed, two retained failures**. [Complete measurement and validation](bench/reports/final-20261120/RESULTS.md). Historical stage measurements remain in bench/reports and are not the current coverage.

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

Registry identity, roles, subunits and accounts come from official Brønnøysundregistrene APIs or the supplied registry snapshot. Registry data is attributed under NLOD 2.0. Optional hiring uses the official NAV feed and live detail verification against the exact company or registered subunit. Job claims cite the anonymous public ad page on arbeidsplassen.nav.no where it matches the verified ad; the feed is discovery provenance. The bundled NAV index is declared discovery metadata; it does not replace live evidence.

Website research follows robots, public-IP, redirect, request and time limits. Published website facts require the documented company-identity proof. Social profile links can be recognised on accepted company pages; social platforms are not fetched. Public activity keeps company-published articles, supported registry updates and exact-party procurement awards separately labelled. Registry updates use the official Enhetsregisteret API, not the robots-disallowed Kunngjøringer HTML service. Bundled SSB KLASS industry titles retain CC BY 4.0 attribution to Statistics Norway.

Bounded news discovery selects one advertised feed, sitemap or news index from a verified homepage. It publishes at most five explicitly dated items without expanding child sitemaps or article links. Publication, update and last-modification dates retain their distinct meanings; registry activity is separate.

Code and documentation use the [MIT licence](LICENSE). NAV, company websites and dependencies retain their own terms. See [source policy and dependency licences](docs/SOURCES.md) and [identity rules](docs/IDENTITY_RESOLUTION.md).

Wikidata's CC0 structured data is queried by exact P2333 organisation number for revision-cited official name, inception, headquarters, industry, employees/revenue with point-in-time qualifiers, website and social identifiers. Registry values prevail where they disagree; disagreements are recorded. Wikidata social identifiers retain the handle attribution test. Website nominations still need live ownership proof; Wikidata failures do not prevent registry or website research. Wikidata social claims identify their item URL and licence.

## Sources, licences and cost

| Source or service | Use in the official run | Licence / access terms | Provider cost |
|---|---|---|---:|
| Brønnøysundregistrene (BRREG) | Company identity, roles, subunits and accounts through the live official API | NLOD 2.0; attribute Brønnøysundregistrene | $0 |
| NAV public job feed and public ad pages | Feed: candidate discovery and live verification of active job details. Public ad page: the anonymous citation for each matching job claim | Public feed; [NAV reuse terms](https://arbeidsplassen.nav.no/vilkar-api) | $0 |
| Wikidata | Revision-cited exact-orgnr structured facts and website/social nominations | CC0; retain item attribution in claim provenance | $0 |
| Company websites | Ownership proof and company-published descriptions, social links and activity | Robots.txt and site access rules are followed; no open licence is inferred | $0 |
| GLEIF | Exact-orgnr LEI facts and explicitly supported parents | [CC0 1.0](https://www.gleif.org/en/meta/lei-data-terms-of-use); anonymous API, exact child matches under RA000472 or RA000473 | $0 |
| TED | Exact winner/buyer public procurement awards | [EU Publications Office reuse terms](https://ted.europa.eu/en/legal-notice); anonymous API and public notice XML | $0 |
| Doffin | **Not used** | Supported keyless API/access and reuse terms were not verified | - |
| Kunngjøringer HTML service | **Not used** | w2.brreg.no robots.txt disallows /kunngjoring/; no NLOD grant for this service assumed | - |
| Search engines | No integration | No provider is called | $0 |
| Language models | None; summaries use deterministic templates | No model provider is called | $0 |

No personal NAV credential is required. When `NAV_API_TOKEN` is unset, the runner retrieves NAV's published public token from `https://pam-stilling-feed.nav.no/api/publicToken` and keeps it in memory for that run; it is never logged or written to output or state.

The command has **$0 provider cost**. Compute, storage and network costs are excluded. `--synthesis` accepts `template` (default) or `auto`, which both use templates; `llm` is rejected.

## Stage AP final combined measurement

Standard CLI defaults, fresh state, site ON, frozen `bench/inputs/1000-r3/batch.jsonl`, source `cede547`. **run_status completed; success_rate 1.0 (1,000/1,000)**. Crawl **1,075.200s**; end-to-end **1,602.8767692s** (1,602.877s rounded). Finalisation/outputs **137.730s**, site **378.860s**, other overhead **11.0867692s**. **11,653 / 19,000 HTTP**, maximum **40/company**, **0 deadline hits, 0 handled or unhandled exceptions**. Optional-source availability is distinct from terminal success: 868 companies have no source-error flags.

Linear projection for 1,100: **1,763.164s / 3,600s** (1,836.836s headroom) and approximately **12,819 / 20,900 HTTP** (8,081 headroom). This is conditional on similar network/source conditions, including TED's breaker; it is not a tail-latency guarantee. The budget is our own safeguard; the brief specifies no numeric time limit. HTTP ceilings remain **19 pooled per distinct normalized input, 40 attributed per company**, including retries and shared requests globally. Lower configured limits apply.

### Full family table

All counts are published claims in this ONE run. Rows overlap; do not sum them. Accounts/identity/roles contain named subsets.

| Family / information type | Companies | Claims |
|---|---:|---:|
| Identity | 1,000 | 31,241 |
| Roles | 997 | 18,783 |
| Accounts | 999 | 100,233 |
| Audit status, per year/scope | 999 | 2,817 |
| Registry-date activity | 997 | 7,714 |
| Previous legal names of the subject company | 241 | 324 |
| Subunits | 773 | 6,907 |
| Group structure | 75 | 119 |
| Signatur | 765 | 765 |
| Prokura | 201 | 201 |
| Registry changes | 1,000 | 12,055 |
| GLEIF | 142 | 736 |
| TED awards — SOURCE UNAVAILABLE | 0 | 0 |
| Wikidata structured identity/accounts and item claims | 13 | 47 |
| Verified official websites | 114 | 114 |
| Public brands | 19 | 19 |
| Social profiles | 61 | 125 |
| News / explicitly dated company items | 32 | 115 |
| Hiring | 3 | 3 |
| Research projects | 9 | 17 |
| State aid | 98 | 679 |
| SkatteFUNN | 36 | 89 |
| DiBK central approvals | 12 | 62 |
| Cleaning status snapshot | 6 | 6 |
| Workshop approval snapshot | 1 | 2 |
| Related-company registry-declared websites | 14 | 16 |

Total supported published facts: **178,669**. Previous-name counts above are subject-company names; the broader company-plus-subunit view is 302 companies / 701 claims. Approval snapshots combined are seven companies / eight records, including one explicitly not-approved cleaning status. Related-company sites never supply borrowed social, brand or news content.

### Accuracy, attribution and tests

Strict verifier **PASS**: 1,000 schema-valid envelopes, 178,669 claims, 5,993 source blobs, 2,552 synthesis sentences and **zero unverified synthesis values**, exact input membership/order. The Stage X stratified **200-claim** sample (seed 20261119) has **200/200 correct**, zero wrong/doubtful, 156 mechanical and 44 hand-reviewed; **Wilson 95% lower bound 98.12%**. This measures precision of the sample, not recall or an evaluator score.

Attribution: **0 cross-company contamination**; four shared official bulk-URL flags were adjudicated using 791 exact-subject source rows (787 direct and four explicitly labelled, registry-proved recipient-subunit associations), without relaxing the raw audit.

Self-sufficient accuracy and attribution checks reproduce without bench/runs: [commands and extract](bench/reports/final-20261120/accuracy/REPRODUCE.md). The full suite has **1,852 tests: 1,850 passed, two failed**:

- `test_evaluator_shapes_union_contract_reference`: live-network evaluator reference check failed after BRREG oppdateringer ConnectTimeout left activity incomplete.
- `test_independent_footer_runs_dependent_production_extraction`: footer timing flake (`official_website` absent after website deadline); passed twice in isolation. The full-suite failure remains recorded.

The suite is not all green. [Complete test output and diagnosis](bench/reports/final-20261120/RESULTS.md#every-test-failure).

## Added sources and licences

| Source | Publication / access | Licence or terms |
|---|---|---|
| Forskningsrådet research projects | Bundled funded-phase snapshot; total project awards, not exclusive company funding | Forskningsrådet, [NLOD 2.0](https://data.norge.no/nlod/en/2.0); excludes newer Tibi system |
| Støtteregisteret state aid | Bundled exact-recipient snapshot, actual instrument labels and explicit subunit scope | Brønnøysundregistrene, [NLOD 2.0](https://data.norge.no/nlod/en/2.0); no parseable robots file, officially published bulk download rather than crawl |
| SkatteFUNN | Bundled approved applications, exact orgnr, deduplicated project numbers; R&D tax deduction scheme, never a cash grant | Forskningsrådet, [catalogued NLOD 2.0](https://data.norge.no/nb/datasets/f82d3d4a-b0f8-3220-83ef-15fbd854c54f/innsendte-soknader-til-skattefunn); current provider workbook substituted for stale catalogue distribution |
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

- TED depends on upstream XML readiness: HTTP 202 opens the breaker with periodic re-probes; **0 awards** in Stage AP versus **6 companies / 20 awards** in an earlier run, not evidence of no procurement.
- Hiring is limited by NAV feed discovery/availability; all three published ads use proved registered-subunit employer numbers. [Route investigation](bench/reports/nav-live-routes-20-20261119/RESULTS.md).
- Websites are verified-only (**114**); bounded discovery, static HTML, robots, transient failures and strict proof can miss genuine sites.
- Related-company websites are **registry-declared, not ownership-verified**, and are not official_website claims.
- SkatteFUNN licence basis is the catalogue's NLOD 2.0 dataset listing; its nov24 distribution returned 404 on 20 November 2026, so the provider's current publication of the same dataset is treated as covered. [Exact basis](docs/SOURCES.md#skattefunn-historical-approvals-bundled-zero-runtime-http).
- Stage AI's baseline **"Registered name"** sentence cites the registry identity claim; it does not assert first observation or absence of prior facts. Repeat-run refresh handling is unchanged.
- Research excludes Tibi; snapshots can age, absence is not proof of no funding/approval, company news is not independent verification, and optional source failure does not invalidate all terminal results.

No LLM, paid API or search-engine scraping is used. Financial scope/currency/period mismatches are not reconciled by guessing. No JavaScript rendering or scanned-PDF extraction is provided. Local antivirus can quarantine retained fetched evidence; historical incidents are recorded in [Stage G](bench/reports/stage-g/defender-evidence.json).
