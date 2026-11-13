# Nordic Company Lens

Nordic Company Lens researches Norwegian companies using official registries and bounded company-owned sources. It checks company identity, publishes evidence-linked facts and cited template summaries, and can generate searchable offline profiles. The Python import package and console command remain `signalpost`.

## Install

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/). From this repository:

```sh
uv sync --frozen
```

## Official run

For final measured coverage, sources, budgets and limitations, see [SUBMISSION.md](SUBMISSION.md). The Step 22 new random cohort (100 valid organisation numbers plus three invalid lines) passed the fixed-runtime same-command refresh check: 103 outputs per run, zero company changes, zero observation changes and strict verifier exit 0. [Precision review and exact results](bench/reports/s6-step22/SCOREBOARD.md).

The command writes a static offline site to `out/site`. Open `out/site/index.html` directly: search the directory by company name or organisation number, open a company, or compare two or three companies. The comparison URL preserves the selection; share that link together with the generated site folder. Source buttons show captured excerpts, URLs, retrieval dates and reporting periods. No CDN or web server is required. At narrow widths comparison cards stack vertically.

Each company has a deterministic cited analyst briefing, with detailed supporting facts and a three-part account of what it does, changes and remaining gaps. Source and run-metadata citations remain distinct. The same command and state folder automatically use the previous snapshot; transient failed refreshes preserve previous section state, supported claims and original evidence with a dated stale note.

Put one Norwegian organisation number on each line in `orgnrs.txt`, then run this command from the repository root:

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --profiles-output out/profiles.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

Only `--organisations` and `--output` are required. Omitted `--report`, `--profiles-output` and `--site-dir` default to `out/report.json`, `out/profiles.jsonl` and `out/site`. Unknown arguments are ignored with a warning on stderr and recorded in the report; the report's `effective_configuration` records the actual feature settings, limits, NAV mode and source-cost counters.

This is the supported clean-checkout command: it needs no credentials and no `--bulk` file. The runner uses live official BRREG APIs for registry identity, roles, subunits and accounts. The input count is read automatically. Blank lines are retained as invalid input records, so each line produces one envelope and one profile.

Website research, NAV hiring checks, public activity and template synthesis are on by default. There is no search-engine integration; provider cost is $0. Use `--no-websites`, `--no-hiring` or `--no-public-activity` to opt out of those sources. `--expected-count` is optional and is normally unnecessary.

Requests use a pooled global ceiling of 1,900 per 100 distinct normalized input records, with at most 40 attributed to any one company. The default run time limit is 2,400 seconds, also bounded by a hard 24 seconds per distinct normalized input (40 minutes per 100). Lower configured limits remain effective. Careers checks run after primary collection using remaining budget, without earmarking or reducing the activity allowance. Incomplete careers coverage is reported honestly. The shared deadline and 40-request company ceiling still apply. Registry-declared websites require the legal name or hard registry corroboration; sites corroborated only by a contact or role-holder publish a website link without site content. Registered subunit identifiers can establish ownership. Shared domains, conflicting owners, parked pages and directories are withheld. Exact-name-only and contact-only two-signal publication were rejected in the Step 10 audit; guessed domains retain the stronger existing ownership proof.

Verified sites can supply individual active, dated job postings, including linked supported ATS pages. Careers landing pages are not jobs. Feeds and sitemaps discover articles, but each published article needs its own publication date. Registered business addresses are typed separately from workplaces and duplicate addresses are suppressed.

Registry email domains and registered subunit website/email nominations can establish a declared site when the registered name appears in its title, main heading, site-name metadata, logo alt text or footer. Email/subunit declarations require the name; their contact-only trial was rejected after review. The existing direct registry-homepage Tier B rule remains link-only. Accounting/IT/hosting provider mismatches, placeholders, conflicting publishers and shared registry domains are rejected. Exact-name `.no` guesses additionally require registry-wide uniqueness and a registered contact, location or role-holder on the site. Site-linked ATS postings may use the verified company-to-board link chain instead of an employer orgnr; other employers, staffing-agency boards, expired ads and landing pages remain excluded.

Source research requires internet access. The `bench/inputs` files are for reproducible project benchmarks and are not needed for an official run.

## Run

To run the bundled benchmark instead, use its frozen input and registry snapshot and pass an explicit expected count. See [the Step 7 benchmark record](bench/reports/s6-step7/SCOREBOARD.md).

Input accepts plain text with one orgnr per line, JSONL strings/numbers, JSONL objects with an `organisation_number` field, JSON lists, or an object with an `organisation_numbers` list. Identifiers are normalized and checksum-validated. Output preserves input order and duplicates; duplicate companies share research. Invalid inputs retain explicit failed envelopes. Re-running the same command with the same `--state-dir` automatically refreshes against the latest complete snapshot; `--previous prior.jsonl` overrides it. Use `--deduplicate` to request unique output identifiers. See [the exact input/output contract](OUTPUT_CONTRACT.md).

## Outputs

- `out/envelopes.jsonl`: validated company envelopes, with verified claims, evidence, section states and cited summaries. The default shape is `union`; `contract` and `reference` are also supported.
- `out/profiles.jsonl`: separate evaluator-compatible raw profiles from the same verified facts.
- `out/report.json`: membership, source states, errors, requests, budgets, timing and cost.
- `out/site/`: optional static searchable company profiles with evidence excerpts. Open `index.html` locally. Site generation may be skipped if remaining time is insufficient.
- `out/state/` (for the command above): local evidence bodies, caches and progress. Keep the matching state when verifying evidence or carrying facts forward.

Exit zero means output was written for parsed input records. Inspect report warnings and source states: `complete` does not mean every source succeeded. Missing or unavailable facts remain explicit, without invented evidence. Refresh distinguishes supported company changes from source failures and retains original provenance for carried-forward facts.

## Sources and licences

Registry identity, roles, subunits and accounts come from official Brønnøysundregistrene APIs or the supplied registry snapshot. Registry data is attributed under NLOD 2.0. Optional hiring uses the official NAV feed and live detail verification against the exact company or registered subunit. The bundled NAV index is declared discovery metadata; it does not replace live evidence.

Website research follows robots, public-IP, redirect, request and time limits. Published website facts require the documented company-identity proof. Social profile links can be recognised on accepted company pages; social platforms are not fetched. Public activity keeps company-published articles, supported registry updates and exact-party procurement awards separately labelled. Registry updates use the official Enhetsregisteret API, not the robots-disallowed Kunngjøringer HTML service. Bundled SSB KLASS industry titles retain CC BY 4.0 attribution to Statistics Norway.

Feeds and sitemaps nominate news URLs. Website news is published only after fetching an article with a page title, article body and publication date; modification dates are not publication evidence. Registry activity is checked separately.

Code and documentation use the [MIT licence](LICENSE). NAV, company websites and dependencies retain their own terms. See [source policy and dependency licences](docs/SOURCES.md) and [identity rules](docs/IDENTITY_RESOLUTION.md).

Wikidata's CC0 structured data is queried by exact Norwegian organisation number for website nominations and name-matched social identifiers. Website nominations still need live ownership proof; Wikidata failures do not prevent registry or website research. Wikidata social claims identify their item URL and licence.

## Sources, licences and cost

| Source or service | Use in the official run | Licence / access terms | Provider cost |
|---|---|---|---:|
| Brønnøysundregistrene (BRREG) | Company identity, roles, subunits and accounts through the live official API | NLOD 2.0; attribute Brønnøysundregistrene | $0 |
| NAV public job feed | Candidate discovery and live verification of active job details | Public feed; [NAV reuse terms](https://arbeidsplassen.nav.no/vilkar-api) | $0 |
| Wikidata | Supplementary website/social nominations by exact orgnr | CC0; retain item attribution in claim provenance | $0 |
| Company websites | Ownership proof and company-published descriptions, social links and activity | Robots.txt and site access rules are followed; no open licence is inferred | $0 |
| GLEIF | Exact-orgnr LEI facts and explicitly supported parents | [CC0 1.0](https://www.gleif.org/en/meta/lei-data-terms-of-use); anonymous API, RA000472 matching | $0 |
| TED | Exact winner/buyer public procurement awards | [EU Publications Office reuse terms](https://ted.europa.eu/en/legal-notice); anonymous API and public notice XML | $0 |
| Doffin | **Not used** | Supported keyless API/access and reuse terms were not verified | - |
| Kunngjøringer HTML service | **Not used** | w2.brreg.no robots.txt disallows /kunngjoring/; no NLOD grant for this service assumed | - |
| Search engines | No integration | No provider is called | $0 |
| Language models | None; summaries use deterministic templates | No model provider is called | $0 |

No personal NAV credential is required. When `NAV_API_TOKEN` is unset, the runner retrieves NAV's published public token from `https://pam-stilling-feed.nav.no/api/publicToken` and keeps it in memory for that run; it is never logged or written to output or state.

The command has **$0 provider cost**. Compute, storage and network costs are excluded. `--synthesis` accepts `template` (default) or `auto`, which both use templates; `llm` is rejected.

## Final measured coverage

One frozen 1,000-company run of runtime `39a73142` produced **108 verified websites, 44 social companies, 3 jobs companies and 1,000 activity companies**, plus GLEIF facts for 32 companies and TED awards for 6. Registry coverage: identity 1,000, people 997, subunit workplaces 774 and financials 999. Total supported facts: **166,207**. HTTP: **8,589**, mean 8.589/input, maximum 40/company; wall time **1,017.315 seconds**, zero deadlines, 1,000 envelopes/profiles. These are coverage measurements, not an evaluator score or a completeness guarantee. [Final release results and verifier](bench/reports/final-release/RESULTS.md).

## Limitations and checks

Strict identity rules and bounded discovery can miss genuine websites, jobs and activity. Bulk data and the bundled NAV index can age; stale or unusable indexes trigger feed fallback. API failures, robots restrictions, timeouts and budget caps leave explicit incomplete states. Website research has no browser renderer. Scanned PDFs are not used; annual-report PDF discovery was removed after a failed recall trial. Small companies often have no discoverable, provably owned website. Unknown trading names can escape NAV discovery, and name matching alone never proves employer identity. Financial comparisons abstain when entity, period, currency or units are incompatible. Source-reported text is not an independent assessment, and cited templates do not provide general semantic fact verification.

Local coverage and timing measurements are recorded in [SUBMISSION.md](SUBMISSION.md); they are not an official evaluator score. Run `uv run pytest -q` for the offline suite. The [evaluation guide](docs/EVAL.md) documents smoke checks and output verification. See also [schema](docs/DATA_SCHEMA.md), [agent loop](docs/AGENT.md), [refresh](docs/REFRESH.md) and [limitations](docs/LIMITATIONS.md).

Step 13 keeps brand-domain discovery bounded to four actual-use nominations per company, tried only after stronger candidates fail; a brand match never proves ownership. One end-of-run retry may revisit the top three transient-failure candidates within the original pooled caps. Financial output retains every distinct company fiscal year returned, roles include all registered role types, and profiles show distinct typed postal addresses alongside workplaces and business addresses. Dated article publication remains tied to dates on fetched article pages.

Registry announcements use the official, unauthenticated NLOD 2.0 Enhetsregisteret updates API. Explicit returned changes retain their supported field details; records without supported details are labelled only as a recorded update or an explicitly unspecified registry event. Publication date (not inferred effective date), exact orgnr, source excerpts and retrieval evidence are retained. They are labelled "Registry announcement", separately from company-published news. The collector retains at most 50 announcement claims per company within 36 months, deduplicates event/field/value records, and uses a shared acquisition budget of at most two HTTP requests per input, inside the existing pooled cap. Bare or unspecified records never imply a specific business change, and never qualify as a major event in the analyst briefing. Registered subunit events require the retained exact-parent registry proof. Transient failed refreshes retain previous supported announcements as stale with original evidence.

Step 15 bounds legal/subunit-name discovery to eight candidates, with Norwegian-letter spellings and joined/hyphenated .no forms before .com. Candidate DNS is checked before HTTP. Proof-page recovery preserves the previous linked/common-path selection before up to two extra same-host targets, inside the original budgets. Explicit CMS site-owner identifiers can be read from JSON/script/footer data; arbitrary tracking numbers, customer lists and another entity do not prove ownership. Existing publisher/group/parking vetoes and exact-handle social attribution remain unchanged.
