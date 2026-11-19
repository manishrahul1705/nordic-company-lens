# Nordic Company Lens

Nordic Company Lens researches Norwegian companies using official registries and bounded company-owned sources. It checks company identity, publishes evidence-linked facts and cited template summaries, and can generate searchable offline profiles. The Python import package and console command remain `signalpost`.

## Install

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/). From this repository:

```sh
uv sync --frozen
```

## Official run

For final measured coverage, sources, budgets and limitations, see [SUBMISSION.md](SUBMISSION.md).

The command writes a static offline site to `out/site`. Open `out/site/index.html` directly: search the directory by company name or organisation number, open a company, or compare two or three companies. The comparison URL preserves the selection; share that link together with the generated site folder. Source buttons show captured excerpts, URLs, retrieval dates and reporting periods. No CDN or web server is required. At narrow widths comparison cards stack vertically.

Each company has a deterministic cited analyst briefing, with detailed supporting facts and a three-part account of what it does, changes and remaining gaps. Source and run-metadata citations remain distinct. The same command and state folder automatically use the previous snapshot; transient failed refreshes preserve previous section state, supported claims and original evidence with a dated stale note.

Put one Norwegian organisation number on each line in `orgnrs.txt`, then run this command from the repository root:

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

Only `--organisations` and `--output` are required. Omitted `--report` and `--site-dir` default to `out/report.json` and `out/site`. Raw profiles are opt-in: `out/profiles.jsonl` is written only when `--profiles-output` is passed explicitly. Unknown arguments are ignored with a warning on stderr and recorded in the report; the report's `effective_configuration` records the actual feature settings, limits, NAV mode and source-cost counters.

This is the supported clean-checkout command: it needs no credentials and no `--bulk` file. The runner uses live official BRREG APIs for registry identity, roles, subunits and accounts. The input count is read automatically. Blank lines are retained as invalid input records, so each line produces one envelope (and one raw profile when `--profiles-output` is passed).

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
- `out/profiles.jsonl` (only with `--profiles-output`): optional separate raw profiles from the same verified facts. Not required by the output contract.
- `out/report.json`: membership, source states, errors, requests, budgets, timing and cost.
- `out/site/`: optional static searchable company profiles with evidence excerpts. Open `index.html` locally. Site generation may be skipped if remaining time is insufficient.
- `out/state/` (for the command above): local evidence bodies, caches and progress. Keep the matching state when verifying evidence or carrying facts forward.

Exit zero means output was written for parsed input records. Inspect report warnings and source states: `complete` does not mean every source succeeded. Missing or unavailable facts remain explicit, without invented evidence. Refresh distinguishes supported company changes from source failures and retains original provenance for carried-forward facts.

## Sources and licences

Registry identity, roles, subunits and accounts come from official Brønnøysundregistrene APIs or the supplied registry snapshot. Registry data is attributed under NLOD 2.0. Optional hiring uses the official NAV feed and live detail verification against the exact company or registered subunit. Job claims cite the anonymous public ad page on arbeidsplassen.nav.no where it matches the verified ad; the feed is discovery provenance. The bundled NAV index is declared discovery metadata; it does not replace live evidence.

Website research follows robots, public-IP, redirect, request and time limits. Published website facts require the documented company-identity proof. Social profile links can be recognised on accepted company pages; social platforms are not fetched. Public activity keeps company-published articles, supported registry updates and exact-party procurement awards separately labelled. Registry updates use the official Enhetsregisteret API, not the robots-disallowed Kunngjøringer HTML service. Bundled SSB KLASS industry titles retain CC BY 4.0 attribution to Statistics Norway.

Feeds and sitemaps nominate news URLs. Website news is published only after fetching an article with a page title, article body and publication date; modification dates are not publication evidence. Registry activity is checked separately.

Code and documentation use the [MIT licence](LICENSE). NAV, company websites and dependencies retain their own terms. See [source policy and dependency licences](docs/SOURCES.md) and [identity rules](docs/IDENTITY_RESOLUTION.md).

Wikidata's CC0 structured data is queried by exact Norwegian organisation number for website nominations and name-matched social identifiers. Website nominations still need live ownership proof; Wikidata failures do not prevent registry or website research. Wikidata social claims identify their item URL and licence.

## Sources, licences and cost

| Source or service | Use in the official run | Licence / access terms | Provider cost |
|---|---|---|---:|
| Brønnøysundregistrene (BRREG) | Company identity, roles, subunits and accounts through the live official API | NLOD 2.0; attribute Brønnøysundregistrene | $0 |
| NAV public job feed and public ad pages | Feed: candidate discovery and live verification of active job details. Public ad page: the anonymous citation for each matching job claim | Public feed; [NAV reuse terms](https://arbeidsplassen.nav.no/vilkar-api) | $0 |
| Wikidata | Supplementary website/social nominations by exact orgnr | CC0; retain item attribution in claim provenance | $0 |
| Company websites | Ownership proof and company-published descriptions, social links and activity | Robots.txt and site access rules are followed; no open licence is inferred | $0 |
| GLEIF | Exact-orgnr LEI facts and explicitly supported parents | [CC0 1.0](https://www.gleif.org/en/meta/lei-data-terms-of-use); anonymous API, exact child matches under RA000472 or RA000473 | $0 |
| TED | Exact winner/buyer public procurement awards | [EU Publications Office reuse terms](https://ted.europa.eu/en/legal-notice); anonymous API and public notice XML | $0 |
| Doffin | **Not used** | Supported keyless API/access and reuse terms were not verified | - |
| Kunngjøringer HTML service | **Not used** | w2.brreg.no robots.txt disallows /kunngjoring/; no NLOD grant for this service assumed | - |
| Search engines | No integration | No provider is called | $0 |
| Language models | None; summaries use deterministic templates | No model provider is called | $0 |

No personal NAV credential is required. When `NAV_API_TOKEN` is unset, the runner retrieves NAV's published public token from `https://pam-stilling-feed.nav.no/api/publicToken` and keeps it in memory for that run; it is never logged or written to output or state.

The command has **$0 provider cost**. Compute, storage and network costs are excluded. `--synthesis` accepts `template` (default) or `auto`, which both use templates; `llm` is rejected.

## Limitations and checks

Among the frozen cohort's declared homepages that publish no website, the recorded outcomes are **35 group/shared site, 8 different publisher, 7 DNS failure, 7 fetched-but-no-proof, 2 robots and 7 other; zero malformed, parked or budget**. GLEIF headroom under the supported exact-ID queries is **zero** ([Stage S recall bounds](bench/reports/stage-s/REPORT.md)).

TED availability varies: across five live runs of the frozen cohort it published 0 to 20 awards covering 0 to 6 companies, depending on how many requests returned HTTP 202 (0% to 93%). No complete procurement coverage is claimed ([measured range](#measured-precision)).

Strict identity rules and bounded discovery can miss genuine websites, jobs and activity. Bulk data and the bundled NAV index can age; stale or unusable indexes trigger feed fallback. API failures, robots restrictions, timeouts and budget caps leave explicit incomplete states. Website research has no browser renderer. Scanned PDFs are not used; annual-report PDF discovery was removed after a failed recall trial. Small companies often have no discoverable, provably owned website. Unknown trading names can escape NAV discovery, and name matching alone never proves employer identity. Financial comparisons abstain when entity, period, currency or units are incompatible. Source-reported text is not an independent assessment, and cited templates do not provide general semantic fact verification.

Local coverage and timing measurements are recorded in [SUBMISSION.md](SUBMISSION.md); they are not an official evaluator score. Run `uv run pytest -q` for the offline suite. The [evaluation guide](docs/EVAL.md) documents smoke checks and output verification. See also [schema](docs/DATA_SCHEMA.md), [agent loop](docs/AGENT.md), [refresh](docs/REFRESH.md) and [limitations](docs/LIMITATIONS.md).

Step 13 keeps brand-domain discovery bounded to four actual-use nominations per company, tried only after stronger candidates fail; a brand match never proves ownership. One end-of-run retry may revisit the top three transient-failure candidates within the original pooled caps. Financial output retains every distinct company fiscal year returned, roles include all registered role types, and profiles show distinct typed postal addresses alongside workplaces and business addresses. Dated article publication remains tied to dates on fetched article pages.

Registry announcements use the official, unauthenticated NLOD 2.0 Enhetsregisteret updates API. Explicit returned changes retain their supported field details; records without supported details are labelled only as a recorded update or an explicitly unspecified registry event. Publication date (not inferred effective date), exact orgnr, source excerpts and retrieval evidence are retained. They are labelled "Registry announcement", separately from company-published news. The collector retains at most 50 announcement claims per company within 36 months, deduplicates event/field/value records, and uses a shared acquisition budget of at most two HTTP requests per input, inside the existing pooled cap. Bare or unspecified records never imply a specific business change, and never qualify as a major event in the analyst briefing. Registered subunit events require the retained exact-parent registry proof. Transient failed refreshes retain previous supported announcements as stale with original evidence.

Step 15 bounds legal/subunit-name discovery to eight candidates, with Norwegian-letter spellings and joined/hyphenated .no forms before .com. Candidate DNS is checked before HTTP. Proof-page recovery preserves the previous linked/common-path selection before up to two extra same-host targets, inside the original budgets. Explicit CMS site-owner identifiers can be read from JSON/script/footer data; arbitrary tracking numbers, customer lists and another entity do not prove ownership. Existing publisher/group/parking vetoes and exact-handle social attribution remain unchanged.


## Measured precision

The final measurement is the **frozen 1,000-company run at code `b0b70cc`** (`bench/runs/final-frozen-20261119`), using the official command with default concurrency and fresh state. It emitted **1,000 envelopes**, with `run_status` **completed**, success rate 1.0, **0 deadline hits**, **0 handled and 0 unhandled exceptions**, and zero warnings. It used **9,275 HTTP requests** (at most 40 attributed to one company) and **1,437 seconds** of wall time, including site generation.

| Family | Companies | Claims |
|---|---:|---:|
| Website | 113 | 113 |
| Social | 47 | 83 |
| Public brand | 20 | 20 |
| GLEIF | 142 | 736 |
| TED awards | 6 | 20 |
| **Supported facts** (available claims whose evidence all resolves) | | **166,025** |

The strict verifier passed (exit 0, without `--require-clean`): 1,000 lines, schema valid, 166,025 published claims, 4,144 source blobs verified, and 0 unverified synthesis values. The full suite reports **1,525 passed, 0 failed**. Records: [measurement](bench/reports/final-frozen-20261119/measurement.json), [process log](bench/reports/final-frozen-20261119/process.txt), [verifier](bench/reports/final-frozen-20261119/strict-verifier.txt), [test log](bench/reports/final-frozen-20261119/pytest.txt). These are measured live-run results, not causal performance claims or a completeness guarantee.

**TED varies with source availability.** Across five live runs of this cohort, TED published **0 to 20 awards covering 0 to 6 companies**. HTTP 202 means "not ready", and a notice still not ready after the retries is recorded as a source failure. Award counts track how many TED requests returned 202:

| Run | Code | TED requests | HTTP 202 | Awards | Companies |
|---|---|---:|---:|---:|---:|
| [Stage P](bench/reports/stage-p/REPORT.md), 14 Nov | `588f356` | 230 | 215 (93%) | 0 | 0 |
| `final-uvw-under-load`, 18 Nov | Stage V | 113 | 33 (29%) | 7 | 3 |
| `long-label-clean-20261118`, 18 Nov | Stage V | 134 | 65 (49%) | 7 | 3 |
| `final-frozen-20261118`, 18 Nov | `0ba340c` | 97 | 11 (11%) | 9 | 4 |
| `final-frozen-20261119`, 18–19 Nov | `b0b70cc` | 89 | 0 (0%) | 20 | 6 |

Stage P predates the TED whitespace normalisation and the three-spelling query. Its zero reflects 202 responses, not missed matches. No complete procurement coverage is claimed.

**Accuracy.** The [Stage X accuracy review](bench/reports/stage-x-accuracy/REPORT.md) drew a 200-claim stratified sample (seed 20261119) from a fresh frozen 1,000 run on code `4af8591` and checked it against the cited evidence bytes. All 200 were correct and attributed to the right organisation number (153 mechanical, 47 by hand). The Wilson 95% lower bound is 98.1%. The attribution audit over the same run found **0 of 1,000 envelopes** with a claim, evidence record or cited company page attributable to a different organisation number: 0 dangling evidence references, 0 registry-URL mismatches, 0 company pages or content hashes reused across envelopes and 0 foreign organisation-number labels. Both rerun from a committed extract with no `bench/runs` present: `uv run --frozen python bench/reports/stage-x-accuracy/reproduce.py` and `.../attribution_audit.py`.

Earlier measurements remain available: [Stage S](bench/reports/stage-s/REPORT.md) (code `4788513`, 112 websites, 166,046 supported facts, 1,432 tests) and [Stage Q](bench/reports/stage-q/REPORT.md). The GLEIF identifier correction raised coverage from **32 to 142 companies**, and a review of the 15 newly matched companies found 15 correct, 0 wrong and 0 doubtful ([review](bench/reports/stage-q/review-live.json)). Careers coverage is not complete, and checks that cannot finish within the existing limits remain explicit failures.

### Known limitations: local measurement environment

Stage H established that Windows Defender detected the fetched ISTAD homepage as `Program:Script/Wacapew.A!ml` (threat ID `251869`) and successfully quarantined the correctly written run 2 blob on **2026-11-13 at 20:31:06 IST** (detection at 20:30:02). This is local antivirus remediation on the measuring machine, not an application storage/retention defect; no production blob-pruning or deletion path was found. This was the second observed occurrence involving the same page in the measurement history. Defender later also detected the run 1 copy during diagnostic reads. The records establish quarantine, not whether the detection is a true or false positive.

The current final measurement is the [frozen run at `b0b70cc`](#measured-precision), superseding Stage S and the earlier Stage G run selection. The ISTAD quarantine is retained as historical evidence of a local measurement-environment artifact; it does not establish an application storage defect or an effect on a clean environment. Later antivirus action can also affect retained evidence files. See [Defender event evidence](bench/reports/stage-g/defender-evidence.json), especially event 1117: Action Quarantine, successful status, error 0x00000000.

### Changes since revision 4

These changes follow the revision 4 merge (`d5139bd`). All of them are included in the [final frozen run](#measured-precision) at code `b0b70cc`.

- **Seven-part company brief, rendered on the site.** The template brief now has seven sections: *What it does*, *How big it is*, *Who runs it*, *What changed*, *Where it operates*, *How it compares* and *What we could not establish*. The offline site renders all seven, with the same cited sentences as the envelope. Every *How it compares* (standing) sentence states its comparison basis in the sentence itself: other companies **in this run only**, the same NACE division, and the same fiscal year of accounts. The division is named by its SSB KLASS title, as the comparison group, never as the company's activity. When there are too few comparables, the sentence says so and does not rank. [verify_output.py](scripts/verify_output.py) recomputes the reach, standing and not-established sections exactly, including the cohort records they use. Code: [sections_extra.py](src/signalpost/synthesis/sections_extra.py), [template.py](src/signalpost/synthesis/template.py), [site.py](src/signalpost/site.py).
- **Gaps view.** Each company has a page titled *What we could not establish, and why*, listing every not-established item with its recorded reason. The run also has a summary page (`gaps.html`), linked from the home page, that counts those reasons across the run. Code: `company_gaps_page` and `run_gaps_page` in [site.py](src/signalpost/site.py).
- **TED identifier matching.** Winner and buyer identifiers in TED notice XML are compared after whitespace-only normalisation, so `923 609 016` matches `923609016`. A complete nine-digit match and a Norwegian country code are still required, with no prefix, substring or name matching. TED's identifier search matches exact strings, so the query sends three spellings of each number: the plain digits, `ddd ddd ddd`, and the observed form with a narrow no-break space (U+202F) after the first group. Code: `ted_query_values` in [official_extra.py](src/signalpost/sources/official_extra.py).
- **DNS label and charset fixes.** A candidate domain label that cannot be IDNA-encoded, such as one over DNS's 63-byte label limit, is now skipped instead of raising an error for that company. Claim span checks now decode the stored body by its declared charset before searching. Previously a correct span on a non-UTF-8 page could fail the check. See the offline [charset replay](bench/reports/charset-replay-20261118/charset-replay.json). Code: [candidates.py](src/signalpost/web/candidates.py), `decode_body` in [text.py](src/signalpost/sources/text.py), [collector.py](src/signalpost/web/collector.py).
- **Social matcher.** A profile is attributed only when its handle's tokens are contained in the company's **registered legal name**, never a trading name, brand or page title. Æ, ø and å are transliterated. A run-together handle may equal the name with or without `as`/`asa`. One-token handles are rejected if shorter than five characters or on the generic-word list. Profiles are recognised on nine platforms: Facebook, Instagram, LinkedIn, X/Twitter, YouTube, TikTok, Threads, Vimeo and Snapchat. Redirects, short links and URLs with credentials are rejected. See the offline [social replay](bench/reports/social-replay-20261118/). Code: [social.py](src/signalpost/web/social.py), [policy.py](src/signalpost/web/policy.py). Tests: [test_social_attribution.py](tests/test_social_attribution.py).
- **Brand rule.** A public brand is published only if it shares at least one token with the legal name or the verified domain. Before comparing, brand, legal name and domain are lowercased, æ/ø/å are transliterated, and legal suffixes and filler words are removed. Leading page words ("Kontaktinformasjon", "Start" and similar) are stripped first, and a brand made only of page words is withheld. On the previous final run this withheld 7 of 26 brands. Six were taglines, descriptions or page words. The seventh, "NKS" for Nordstrand Kulturskole, is probably a genuine acronym and a known loss ([hand review](bench/reports/stage-x-accuracy/brand-token-check.json)). Code: `shares_identity_token` and `strip_page_words` in [collector.py](src/signalpost/web/collector.py). Tests: [test_brand_page_words.py](tests/test_brand_page_words.py).
- **Honest run reporting and identity-outage abort.** `report.json` now opens with `run_status`, `success_rate`, counts of succeeded and failed companies, and source errors by family. A company whose modules all failed at the source is reported as `source_error`, not as complete. **Why the abort exists:** during a network outage, an earlier local run made only 2,007 of about 9,300 expected requests, yet still looked like an ordinary completed run. The abort stops a run in that situation instead of writing 1,000 empty envelopes. If the first 25 identity lookups (`IDENTITY_OUTAGE_SAMPLE`) all fail with network errors or timeouts, new lookups pause. The run then rechecks 3 times, 15 seconds apart, and exits with code 3, naming the unreachable host, only if every recheck also fails. A short startup blip therefore recovers instead of aborting. Code: [runner.py](src/signalpost/runner.py), [report.py](src/signalpost/io/report.py), [cli.py](src/signalpost/cli.py). Tests: [test_identity_outage.py](tests/test_identity_outage.py).
- **Output cap raised from 512 MiB to 4,096 MiB.** `--max-output-mb` is our own safety ceiling. Neither the evaluation contract, the starter kit nor OUTPUT_CONTRACT.md sets an output size. At 512 MiB, the [1,100-company headroom run](bench/reports/headroom-1100-20261119/headroom.json) wrote 431 MB of envelopes, 80% of the cap, with a largest envelope of 2.31 MB. When the cap is exceeded, the writer reduces the largest envelopes to failure placeholders, which is worse than writing a larger file. 4,096 MiB holds 1,100 envelopes even if every one were as large as the largest measured, so an official-size batch cannot be truncated. Code: [config.py](src/signalpost/config.py), [cli.py](src/signalpost/cli.py), [envelope_writer.py](src/signalpost/io/envelope_writer.py). Test: `test_default_output_cap_cannot_truncate_an_official_1100_batch` in [test_resource_limits.py](tests/test_resource_limits.py).

**Tests that make live network requests.** Three tests contact live public services, so expect them to fail or slow down without a network. The rest of the suite runs offline against fixtures. `test_evaluator_cli_direct_invocation_and_site_generation` and `test_evaluator_shapes_union_contract_reference` in [test_evaluator_cli_and_site.py](tests/test_evaluator_cli_and_site.py) run the CLI on the 20-company `ci20` fixture with websites, hiring and activity turned off. They still reach data.brreg.no, api.gleif.org, api.ted.europa.eu and ted.europa.eu. `test_real_os_process_kill_and_checkpoint_recovery` in [test_nav_process_kill_recovery.py](tests/test_nav_process_kill_recovery.py) starts a full CLI run in a separate process, kills it and resumes it. Its runs reach data.brreg.no, NAV (pam-stilling-feed.nav.no and arbeidsplassen.nav.no), query.wikidata.org and candidate company domains. This list comes from a full-suite run that logged every non-loopback DNS lookup, including lookups in Python subprocesses; no other test made one. How these three behave fully offline was not measured.

### Revision 4 changes

Revision 4 changes presentation and citation only. No proof type, veto, acceptance rule, request or time budget, or source changed, and claim IDs and values are unchanged. The only added network access is one anonymous fetch of each already-verified NAV ad's public page, counted in the existing pooled budget. Revision 4 and the later changes are measured together in the [final frozen run](#measured-precision).

- **Job claims cite the public ad page.** After NAV discovery and verification, each verified ad's public page `https://arbeidsplassen.nav.no/stillinger/stilling/<uuid>` is fetched anonymously and stored verbatim. The job claim then cites that page, with two verbatim spans: the ad title and the employer orgnr. Previously it cited the token-protected feed API entry. The feed entry remains discovery provenance only (`source_identifier`). This is best effort: if the page cannot be fetched, or does not name the same title and employer orgnr as the verified ad, the claim keeps its previous feed-API citation, and the outcome is counted under `public_citations` in the NAV metrics. Code: `attach_public_citations` and `public_citation_spans` in [nav.py](src/signalpost/sources/nav.py), plus [nav_public_page.py](src/signalpost/sources/nav_public_page.py). Tests: `test_public_citation_spans_are_verbatim_and_must_match_the_verified_ad` and `test_feed_verified_ads_cite_the_anonymous_public_page` in [test_nav_index.py](tests/test_nav_index.py), the request-sequence check in [test_nav.py](tests/test_nav.py), and [test_external_integration.py](tests/test_external_integration.py).
- **The brief states what the company does, what changed and what remains unknown.**
  - *Changes* come from dated published events (registry announcements by tier, company articles and TED awards) and from the revenue trend between comparable consecutive company-only years, rather than only from snapshot diffs. Events are shown newest first, one per category, at most three. Bare, unspecified and administrative registry records are never presented as changes. A first run therefore reads "First observation" only when there are no dated events.
  - *Unknowns* are listed with their recorded reasons, such as no ownership proof, a parked or unreachable site, no NAV ads, or no accounts on file.
  - *What it does*: a proven company website's self-description and the registered purpose lead. NACE is stated only as the registered industry code, never as the company's activity.
  - The site renders the same three-part brief as the envelope, and [verify_output.py](scripts/verify_output.py) checks it.
  - Code: [company_brief.py](src/signalpost/synthesis/company_brief.py), [analyst.py](src/signalpost/synthesis/analyst.py), [template.py](src/signalpost/synthesis/template.py), [site.py](src/signalpost/site.py). Tests: [test_brief_revision4.py](tests/test_brief_revision4.py) (tiered events, dated changes replacing "First observation", the three-event cap, purpose before NACE, the website reason for unknowns, matching summary and site, and revenue trend as a cited change), plus updates in [test_company_brief.py](tests/test_company_brief.py) and [test_analyst_brief.py](tests/test_analyst_brief.py).
- **Explicit zero revenue.** A filed revenue of exactly 0 reads "reported no operating revenue (NOK 0)" instead of "reported revenue of NOK 0". Code: [analyst.py](src/signalpost/synthesis/analyst.py). Test: `test_explicit_zero_revenue_is_worded_as_no_operating_revenue` in [test_analyst_brief.py](tests/test_analyst_brief.py).
- **Offline-site fixes.** All of the following are covered by [test_site_revision4.py](tests/test_site_revision4.py) except the two CSS-only changes noted:
  - search accepts organisation numbers typed with spaces, dots or dashes;
  - compare cards use a middle dot instead of the stray `?` separator, and the Remove button has its own grid cell (CSS only, not asserted by a test);
  - the evidence drawer shows the retrieval date and the record locator before the source link;
  - excerpts are marked `data-verbatim`, and dates inside them are never rewritten on the server or in the browser;
  - registry objects render without raw JSON or `_links` objects, and account floats are digit-grouped;
  - the tab title defaults to "Nordic Company Lens", and the home headline leads with what was found;
  - the header brand stays on one line at phone width (CSS only, not asserted by a test).

  Code: [site.py](src/signalpost/site.py), [site.js](src/signalpost/site_assets/site.js), [site.css](src/signalpost/site_assets/site.css).
- **Raw profiles are opt-in.** `profiles.jsonl` is written only when `--profiles-output` is passed. `--report` and `--site-dir` keep their defaults (`out/report.json`, `out/site`). Nothing in the [output contract](OUTPUT_CONTRACT.md) requires profiles. Code: [cli.py](src/signalpost/cli.py). Test: `test_evaluator_always_writes_all_artifacts` in [test_cli_evaluator_defaults.py](tests/test_cli_evaluator_defaults.py) asserts that no profiles file exists unless the flag is passed.

Revision 4 validation on this checkout: **1,452 tests passed, zero failed** (`uv run --frozen pytest -q`). This count comes from a local run and has no committed report.

### Revision 3 changes

Stage S repairs four registry homepage cells with unambiguous `www` separators so they can be parsed as candidates: the measured effect is **4 universe candidates and zero cohort nominations**; no proof rule, veto or name matching changed ([normalization-only measurement](bench/reports/stage-s/REPORT.md#the-four-authorised-syntax-repairs)).

The release adds locally bundled Common Crawl candidates and registry shared-identifier counts, bounded deeper ownership pages, strict company-scope filtering, cited contact facts, dated individual-job checks and offline-site improvements. Unknown CLI arguments warn rather than abort; omitted report/site options receive defaults (profiles are opt-in) and effective settings are recorded. The pooled ceiling is 19 HTTP per distinct normalized input (1,900/100), with a hard 40/company maximum including robots, redirects and retries. Lower configured limits remain effective. All time limits are unchanged. Careers runs after primary proof/collection and uses remaining headroom; it has no earmark and does not reduce activity's original allowance. No search-engine integration, paid API or LLM is used. These changes do not claim complete website or careers coverage.

GLEIF records can store the registration number with whitespace, for example `"923 609 016"`; the previous literal comparison rejected that spelling. Matching now normalises whitespace only and accepts both official Bronnoysund child-record authorities: **RA000472 Foretaksregisteret** and **RA000473 Enhetsregisteret**. An exact complete nine-digit organisation-number match is still required, with no name matching. Parent acceptance rules are unchanged. The measured correction is **32 to 142 companies** (32 to 139 from whitespace normalisation in [Stage P](bench/reports/stage-p/REPORT.md), then 139 to 142 from RA000473 in [Stage Q](bench/reports/stage-q/REPORT.md)); **15 reviewed, 0 wrong, 0 doubtful** ([identifier audit and review](bench/reports/stage-q/REPORT.md)).

### Bundled-index provenance

`data/cc_orgnr_index.json.gz` was built 13 November 2026 from partial archived records in CC-MAIN-2026-43,2026-39 and2026-34. It contains 20,832 candidates for 19,735 parent companies. Access/use is subject to [Common Crawl Terms of Use](https://commoncrawl.org/terms-of-use) and third-party rights; see [the bundled terms/method notice](data/CC_INDEX_NOTICE.md). Official Bronnoysund subunit data (NLOD 2.0) maps branch numbers to parents. **Candidate coverage is not verified-site coverage**: every candidate is fetched and re-verified live under the ownership proof and vetoes.

`src/signalpost/data/nav_index.json.gz` was built 2026-11-13T00:26:42.872674Z from the official public NAV feed using public access (9,296 ads / 5,899 employers). No private credential is required or bundled. The runtime retrieves NAV's published public token in memory, validates the index and live-checks nominated ads; missing, invalid or stale indexes retain the honest full-feed fallback. Source terms and limitations are in [SOURCES.md](docs/SOURCES.md).

## Previous revisions

Historical revision 2 results below are retained for comparison, not presented as current coverage.

### Revision 2 measured coverage

One frozen 1,000-company run of runtime `39a73142` produced **108 verified websites, 44 social companies, 3 jobs companies and 1,000 activity companies**, plus GLEIF facts for 32 companies and TED awards for 6. Registry coverage: identity 1,000, people 997, subunit workplaces 774 and financials 999. Total supported facts: **166,207**. HTTP: **8,589**, mean 8.589/input, maximum 40/company; wall time **1,017.315 seconds**, zero deadlines, 1,000 envelopes/profiles. These are coverage measurements, not an evaluator score or a completeness guarantee. [Final release results and verifier](bench/reports/final-release/RESULTS.md).

### Revision 2 precision check

The Step 22 new random cohort (100 valid organisation numbers plus three invalid lines) passed the fixed-runtime same-command refresh check: 103 outputs per run, zero company changes, zero observation changes and strict verifier exit 0. [Precision review and exact results](bench/reports/s6-step22/SCOREBOARD.md).
