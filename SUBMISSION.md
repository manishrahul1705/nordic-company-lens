# Submission notes

## Official command

Requires Python 3.12+, uv and internet access. From a clean checkout, install locked dependencies with `uv sync --frozen`, put organisation numbers in `orgnrs.txt`, then run:

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

No credentials, bulk file, expected count, LLM or search service are required. NAV's published public token is fetched in memory from `https://pam-stilling-feed.nav.no/api/publicToken`; no personal credential is required or persisted. Provider cost is **$0**; local compute, disk and network are excluded.

## Qualification evidence

- **[Stage X accuracy review](bench/reports/stage-x-accuracy/REPORT.md):** a 200-claim stratified sample of the final frozen run (seed 20261119), checked against the cited evidence bytes. **200 of 200 correct**, Wilson 95% lower bound **98.1%**, with known limits stated.
- **[Frozen-cohort attribution audit](bench/reports/attribution-audit-20261118.md):** **0 of 1,000 envelopes** contain a claim, evidence record or cited company page attributable to a different organisation number.

## Input and outputs

The command accepts plain text (one orgnr per line), JSONL strings/numbers or objects with `organisation_number`, JSON arrays, and objects with an `organisation_numbers` array. Whitespace is normalized, checksums are checked, input order and duplicates are preserved. Blank/invalid lines each receive a failed envelope (and a failed profile when `--profiles-output` is passed). The expected count is inferred from the input. See [OUTPUT_CONTRACT.md](OUTPUT_CONTRACT.md).

- `out/envelopes.jsonl`: one schema-validated envelope per input, with claims, citations, evidence, section states and refresh changes.
- `out/profiles.jsonl`: optional raw profiles, written only when `--profiles-output` is passed.
- `out/report.json`: membership, requests, time, errors, source completeness and cost.
- `out/state/`: captured evidence, caches and automatic previous snapshots. Keep this directory with the outputs.
- `out/site/`: static offline directory, company pages, comparisons and source panels. Open `index.html`; no CDN/server is required. Optional site generation can be skipped if time is exhausted.

Run the **same command again with the same state directory** to refresh automatically; `--previous` is unnecessary. Previous/current supported values are compared, original evidence is retained, and transient failed refreshes preserve previous section state and claims with a dated stale note. They do not count as company changes. First-ever failures remain honest failed states; successful proof of real additions/removals is treated as change. Exit zero means outputs were emitted, not that every source succeeded.

## Sources, licences and costs

| Source | Use | Licence / access | Provider cost |
|---|---|---|---:|
| BRREG | Identity, registered roles, subunits and returned financial years | NLOD 2.0; attribute Brønnøysundregistrene | $0 |
| NAV public feed and public ad pages | Active individual ads, exact employer/subunit matching; public token obtained at runtime. Job claims cite the anonymous public ad page when it matches the verified ad | NAV public-feed reuse terms; no personal credential | $0 |
| Wikidata | Supplementary exact-orgnr website/social nominations | CC0, item provenance retained | $0 |
| Company websites | Ownership proof, descriptions, social links, dated news, linked active jobs | robots.txt and site access rules; no blanket open licence inferred | $0 |
| SSB KLASS | Bundled industry descriptions | CC BY 4.0 | $0 |
| LLM / search engines | No integration; deterministic cited templates | No provider called | $0 |
| GLEIF | LEI/status/form/dates and explicit direct/ultimate parents | CC0 1.0; anonymous exact orgnr + RA000472 or RA000473 child match, batched parent LEIs | $0 |
| TED | Exact winner/buyer public procurement awards | EU Publications Office legal notice/Commission reuse policy; anonymous published-notice API and public XML | $0 |
| Doffin | **Not used** | Keyless supported API/access and reuse terms not verified | - |
| Kunngjøringer HTML service | **Not used** | robots.txt disallows /kunngjoring/; service-specific NLOD coverage not verified | - |

See [docs/SOURCES.md](docs/SOURCES.md) and [LICENSE](LICENSE) (code/documentation: MIT). Social destinations are not crawled. A brand/name match alone does not establish company ownership; ambiguous/shared/foreign group sites are withheld. Contact-only direct-registry Tier B sites publish a link without website content.

## Bundled website candidates and registry-backed proof

Common Crawl's bundled `data/cc_orgnr_index.json.gz` is described authoritatively under [Bundled-index provenance](#bundled-index-provenance). Runtime reads it locally by organisation number; it does not query Common Crawl. Domains are candidates only, ranked after registry nominations and before name guesses. Every candidate is fetched live and must pass the existing ownership proof and all applicable directory, parked-page, foreign-owner, group/shared-site, robots, DNS, TLS and request-budget checks. See [Common Crawl Terms of Use](https://commoncrawl.org/terms-of-use) and the third-party rights notice in `data/CC_INDEX_NOTICE.md`; no blanket licence for crawled site content is claimed.

The bundled `data/shared_identifiers.json.gz` counts registered phone/mobile numbers, email domains and distinctive legal-name keys from the official Bronnoysundregistrene entity bulk CSV. Attribution: Bronnoysundregistrene, [NLOD 2.0](https://data.norge.no/nlod/en/2.0). It is read locally, without a runtime registry bulk download. Build hashes and counts are in `data/shared_identifiers_build.json`; the complete gzip is 8,676,502 bytes, above the 3 MB target. Missing keys do not establish uniqueness.

Additional website proof can use the exact registered email visible in text or mailto links only when its non-free-mail domain is registered to exactly one entity; or a registered phone/mobile visible on the page when fewer than five entities register it. Both require a positive count in the snapshot and a nonempty non-placeholder page. The exact legal name, including its legal form, must also identify the publisher in the title, heading or footer; a staff/adviser contact alone is not ownership proof. Name-only masthead and unique-name-domain publication were removed after the R3 precision review exposed namesake and placeholder risks. Existing stronger proofs keep their labels. None of these rules overrides an existing rejection or owner conflict.

On a company-verified site, bounded social profile discovery includes header/footer/navigation links, eligible Organization/LocalBusiness sameAs links and actual Facebook page-plugin hrefs, with company/verified-brand name matching still required. Share/intent links, posts, media, events, groups, platform homepages, LinkedIn non-company paths, profile.php, agency/builder/directory handles and hidden plugins are excluded. Shared/path-scoped attribution and cross-company shared-handle suppression remain in place; social platforms are not fetched.

Current operational ceilings are specified in [Budgets](#budgets); these additions contain no search-engine, directory, Norid or model-provider requests. There is no search-engine integration.

### Bundled-index provenance

The archived collection was produced by [`cc_overnight.py`](scripts/cc_overnight.py), its [columnar selector](scripts/cc_overnight_select.py), and the [supervisor](scripts/run_cc_overnight.ps1)/[worker](scripts/run_cc_overnight_worker.ps1) launchers. The offline [`build_cc_candidate_index.py`](scripts/build_cc_candidate_index.py) turns those records into the bundled index. The [overnight summary](bench/reports/cc-proto/overnight-summary.json) is an earlier heartbeat, not the final index snapshot. These are historical measurement tools: after `uv sync --frozen`, prepare the ignored official subunit/universe caches described in the scripts; DuckDB/httpfs is installed ephemerally by the selector. The recorded 13 November cutoff is intentionally retained, so invoking the archived launchers now makes no crawl requests. Raw downloads are not bundled or committed.

`data/cc_orgnr_index.json.gz` was built 13 November 2026 from partial archived records in CC-MAIN-2026-43,2026-39 and2026-34. It contains 20,832 candidates for 19,735 parent companies. Access/use is subject to [Common Crawl Terms of Use](https://commoncrawl.org/terms-of-use) and third-party rights; see [the bundled terms/method notice](data/CC_INDEX_NOTICE.md). Official Bronnoysund subunit data (NLOD 2.0) maps branch numbers to parents. **Candidate coverage is not verified-site coverage**: every candidate is fetched and re-verified live under the ownership proof and vetoes.

`src/signalpost/data/nav_index.json.gz` was built 2026-11-13T00:26:42.872674Z from the official public NAV feed using public access (9,296 ads / 5,899 employers). No private credential is required or bundled. The runtime retrieves NAV's published public token in memory, validates the index and live-checks nominated ads; missing, invalid or stale indexes retain the honest full-feed fallback. Source terms and limitations are in [SOURCES.md](docs/SOURCES.md).

## Budgets

The pooled HTTP hard cap is 19 per distinct normalized input: 1,900 per 100, with at most 40 attributed to any company and shared calls included globally. The hard time cap is 24 seconds per distinct input (40 minutes per 100), with the default 2,400-second run limit and lower configured limits honored. These are tighter than 2,000 HTTP / 45 minutes per 100. Crawl finalization reserves preserve one output per input even when discovery is incomplete. Public DNS fallbacks are bounded and tolerate blocked UDP; end-of-run retries consume the original pool.

### Changes since revision 4

These changes follow the revision 4 merge (`d5139bd`). All of them are included in the [final frozen run](#measured-precision) at code `b0b70cc`.

- **Seven-part company brief, rendered on the site.** The template brief now has seven sections: *What it does*, *How big it is*, *Who runs it*, *What changed*, *Where it operates*, *How it compares* and *What we could not establish*. The offline site renders all seven, with the same cited sentences as the envelope. Every *How it compares* (standing) sentence states its comparison basis in the sentence itself: other companies **in this run only**, the same NACE division, and the same fiscal year of accounts. The division is named by its SSB KLASS title, as the comparison group, never as the company's activity. When there are too few comparables, the sentence says so and does not rank. [verify_output.py](scripts/verify_output.py) recomputes the reach, standing and not-established sections exactly, including the cohort records they use. Code: [sections_extra.py](src/signalpost/synthesis/sections_extra.py), [template.py](src/signalpost/synthesis/template.py), [site.py](src/signalpost/site.py).
- **Gaps view.** Each company has a page titled *What we could not establish, and why*, listing every not-established item with its recorded reason. The run also has a summary page (`gaps.html`), linked from the home page, that counts those reasons across the run. Code: `company_gaps_page` and `run_gaps_page` in [site.py](src/signalpost/site.py).
- **TED identifier matching.** Winner and buyer identifiers in TED notice XML are compared after whitespace-only normalisation, so `923 609 016` matches `923609016`. A complete nine-digit match and a Norwegian country code are still required, with no prefix, substring or name matching. TED's identifier search matches exact strings, so the query sends three spellings of each number: the plain digits, `ddd ddd ddd`, and the observed form with a narrow no-break space (U+202F) after the first group. Code: `ted_query_values` in [official_extra.py](src/signalpost/sources/official_extra.py).
- **DNS label and charset fixes.** A candidate domain label that cannot be IDNA-encoded, such as one over DNS's 63-byte label limit, is now skipped instead of raising an error for that company. Claim span checks now decode the stored body by its declared charset before searching. Previously a correct span on a non-UTF-8 page could fail the check. See the offline [charset replay](bench/reports/charset-replay-20261118/charset-replay.json). Code: [candidates.py](src/signalpost/web/candidates.py), `decode_body` in [text.py](src/signalpost/sources/text.py), [collector.py](src/signalpost/web/collector.py).
- **Social matcher.** A profile is attributed only when its handle's tokens are contained in the company's **registered legal name**, never a trading name, brand or page title. Æ, ø and å are transliterated. A run-together handle may equal the name with or without `as`/`asa`. One-token handles are rejected if shorter than five characters or on the generic-word list. Profiles are recognised on nine platforms: Facebook, Instagram, LinkedIn, X/Twitter, YouTube, TikTok, Threads, Vimeo and Snapchat. Redirects, short links and URLs with credentials are rejected. See the offline [social replay](bench/reports/social-replay-20261118/). Code: [social.py](src/signalpost/web/social.py), [policy.py](src/signalpost/web/policy.py). Tests: [test_social_attribution.py](tests/test_social_attribution.py).
- **Brand rule.** A public brand is published only if it shares at least one token with the legal name or the verified domain. Before comparing, brand, legal name and domain are lowercased, æ/ø/å are transliterated, and legal suffixes and filler words are removed. Leading page words ("Kontaktinformasjon", "Start" and similar) are stripped first, and a brand made only of page words is withheld. On the previous final run this withheld 7 of 26 brands. Six were taglines, descriptions or page words. The seventh, "NKS" for Nordstrand Kulturskole, is probably a genuine acronym and a known loss ([hand review](bench/reports/stage-x-accuracy/brand-token-check.json)). Code: `shares_identity_token` and `strip_page_words` in [collector.py](src/signalpost/web/collector.py). Tests: [test_brand_page_words.py](tests/test_brand_page_words.py).
- **Honest run reporting and identity-outage abort.** `report.json` now opens with `run_status`, `success_rate`, counts of succeeded and failed companies, and source errors by family. A company whose modules all failed at the source is reported as `source_error`, not as complete. **Why the abort exists:** during a network outage, an earlier local run made only 2,007 of about 9,300 expected requests, yet still looked like an ordinary completed run. The abort stops a run in that situation instead of writing 1,000 empty envelopes. If the first 25 identity lookups (`IDENTITY_OUTAGE_SAMPLE`) all fail with network errors or timeouts, new lookups pause. The run then rechecks 3 times, 15 seconds apart, and exits with code 3, naming the unreachable host, only if every recheck also fails. A short startup blip therefore recovers instead of aborting. Code: [runner.py](src/signalpost/runner.py), [report.py](src/signalpost/io/report.py), [cli.py](src/signalpost/cli.py). Tests: [test_identity_outage.py](tests/test_identity_outage.py).

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

**Accuracy.** The [Stage X accuracy review](bench/reports/stage-x-accuracy/REPORT.md) checked a 200-claim stratified sample (seed 20261119) against the cited evidence bytes. All 200 were correct and attributed to the right organisation number. The Wilson 95% lower bound is 98.1%. The [frozen-cohort attribution audit](bench/reports/attribution-audit-20261118.md) found that **0 of 1,000 envelopes** contain a claim, evidence record or cited company page attributable to a different organisation number: 0 dangling evidence references, 0 registry-URL mismatches and 0 company pages reused across envelopes.

Earlier measurements remain available: [Stage S](bench/reports/stage-s/REPORT.md) (code `4788513`, 112 websites, 166,046 supported facts, 1,432 tests) and [Stage Q](bench/reports/stage-q/REPORT.md). The GLEIF identifier correction raised coverage from **32 to 142 companies**, and a review of the 15 newly matched companies found 15 correct, 0 wrong and 0 doubtful ([review](bench/reports/stage-q/review-live.json)). Careers coverage is not complete, and checks that cannot finish within the existing limits remain explicit failures.

## Known limitations

Among the frozen cohort's declared homepages that publish no website, the recorded outcomes are **35 group/shared site, 8 different publisher, 7 DNS failure, 7 fetched-but-no-proof, 2 robots and 7 other; zero malformed, parked or budget**. GLEIF headroom under the supported exact-ID queries is **zero** ([Stage S recall bounds](bench/reports/stage-s/REPORT.md)).

There is **no JavaScript rendering**; static HTML-only sites can be missed. Small-company websites are often absent or cannot be proved to belong to the exact legal entity. Scanned PDFs are not used; annual-report PDF discovery and pypdf were removed after a low-yield, rate-limited trial. Financial depth depends on the years returned by the registry and previously supported historical facts retained on refresh. Company and consolidated accounts stay separate; currencies are not converted. GLEIF covers only exact registered identifiers with LEIs. TED awards require explicit exact-party contract links; legacy or ambiguous notices may be omitted. TED availability varies: across five live runs of the frozen cohort it published 0 to 20 awards covering 0 to 6 companies, with 0% to 93% of TED requests returning HTTP 202; no complete procurement coverage is claimed ([measured range](#measured-precision)). Robots restrictions, blocked network access, API limits, DNS/TLS errors and exhausted budgets cause explicit incomplete/stale states. Jobs/news coverage is bounded, and careers landing pages are never jobs. News claims describe company-published articles, not independently verified events. Templates summarize supported facts and identified run metadata; they do not provide general semantic fact checking.

The template sentence "First observation; no earlier run to compare." is true, but its citation points to the company's first published claim, not to the run's first-run status, which is not itself a published claim. Citing that status would need a context-claim slot in the template output, its validator and the verifier, a structural change not made in this revision. It affects **1,000 sentences across the frozen 1,000**, one per company, since every company there is a first run. The three-part brief's own "First observation" sentence cites the refresh context claim correctly ([Stage X accuracy review](bench/reports/stage-x-accuracy/REPORT.md)).

### Known limitations: local measurement environment

Stage H established that Windows Defender detected the fetched ISTAD homepage as `Program:Script/Wacapew.A!ml` (threat ID `251869`) and successfully quarantined the correctly written run 2 blob on **2026-11-13 at 20:31:06 IST** (detection at 20:30:02). This is local antivirus remediation on the measuring machine, not an application storage/retention defect; no production blob-pruning or deletion path was found. This was the second observed occurrence involving the same page in the measurement history. Defender later also detected the run 1 copy during diagnostic reads. The records establish quarantine, not whether the detection is a true or false positive.

The current final measurement is the [frozen run at `b0b70cc`](#measured-precision), superseding Stage S and the earlier Stage G run selection. The ISTAD quarantine is retained as historical evidence of a local measurement-environment artifact; it does not establish an application storage defect or an effect on a clean environment. Later antivirus action can also affect retained evidence files. See [Defender event evidence](bench/reports/stage-g/defender-evidence.json), especially event 1117: Action Quarantine, successful status, error 0x00000000.

## Verification workflow

[Verify Signalpost](.github/workflows/ci.yml) runs locked installation, the full pytest suite and live-20. Its `--require-clean` verifier remains strict for identity, roles, accounts and subunits. Only optional website/social, hiring and activity failures/stale states are tolerated and summarized with reasons; schema, membership, evidence, citations and global operational checks remain strict. Local release execution is documented in the release report; no GitHub workflow was dispatched and nothing was pushed.

Current validation (code `b0b70cc`): **1,525 tests passed, zero failed**, and the strict verifier passed on the final frozen run ([test log](bench/reports/final-frozen-20261119/pytest.txt), [verifier](bench/reports/final-frozen-20261119/strict-verifier.txt)). Revision 3 / Stage S validation (code `4788513`): **1,432 tests passed, zero failed**, and the Stage S retry recorded zero deadline hits ([Stage S test log](bench/reports/stage-s/pytest.txt)). Revision 4 validation before the later changes: **1,452 tests passed, zero failed** (local run, no committed report). The earlier Stage E fresh-clone refresh pair recorded zero company and observation changes with strict verifier PASS; that historical pair was not rerun in Stage S ([refresh verification](bench/reports/stage-e/refresh/strict-verifier.txt)).

## Previous revisions

The following records describe revision 2 or superseded operational notes. Their values and links are preserved for historical comparison; they are not the current Stage S measurement.

### Revision 2 frozen 1,000-company measurement

Measured the unchanged runtime `39a7314299c181187ee1f07af7fa75eaa631ad9c` once on 7 November 2026: run `20261107T094159020873Z-39a7314`. This frozen benchmark is separate from the fresh random precision sample below.

| Section / metric | Revision 2 |
|---|---:|
| Identity | 1,000 |
| People | 997 |
| Subunit/workplace section | 774 |
| Financials | 999 |
| Verified websites | 108 |
| Social companies | 44 |
| Jobs companies | 3 |
| Activity companies | 1,000 |
| GLEIF companies | 32 |
| TED award companies | 6 |
| Supported facts | 166,207 |
| HTTP total / mean per input / max per company | 8,589 / 8.589 / 40 |
| Wall seconds | 1,017.315 |
| Deadlines | 0 |
| Envelopes / profiles | 1,000 / 1,000 |

Site generation passed without warnings. Counts are measured coverage, not an evaluator score or a claim that every source succeeded. One financial section and four optional hiring sections failed. Websites are 108 rather than the saved Step20 projection's110: ISTAD ART SOLUTION NORWAY NUF is ambiguous after the final ownership recheck; Bergen Vaktmestertjenester's current privacy page fails the exact-company ownership check. These are proof/withholding outcomes, not claimed DNS noise or code changes. [Final results, diagnostics and independent verification](bench/reports/final-release/RESULTS.md).

### Revision 2 fresh random 100-company precision check

Step 22 selected a NEW random sample of 100 valid identifiers outside all known inputs/reports/cohorts, plus three invalid lines. The fixed runtime's literal README command twice emitted **103 envelopes/profiles per run**, **336.360 seconds / 788 HTTP**, then **175.704 seconds / 753 HTTP**. **Zero company changes, zero observation changes, unmodified strict verifier exit 0**; zero unverified values. Final sample coverage: 100 identity, 96 people, 72 subunit workplaces, 42 accounts, 6 websites, 4 social companies, 2 jobs, 100 activity companies, 1 GLEIF company; 8,974 supported facts.

Every website/social/job/GLEIF item, 50 random registry facts and ten briefings were reviewed. A full-footer publisher-name correction rejects a different entity whose name merely contains the subject brand; the existing exact-orgnr spelling normalization is retained. Unrelated companies' calibration excerpts were removed from financial claim citations without changing amounts, periods or claim IDs. The saved frozen-1000 replay kept all 110 websites and all financial values/IDs; verification passed with zero unverified values. The original doubtful .no page was withheld; the replacement .com publisher was checked against the NUF's explicit registered head enterprise. No company-specific exception. [Full precision report](bench/reports/s6-step22/SCOREBOARD.md).

### Revision 2 verification record

The final release executes the exact local workflow commands on the final runtime; the full results and logs are in [final release validation](bench/reports/final-release/RESULTS.md). The Step 22 fixed-runtime fresh pair is separate from the final frozen benchmark. No GitHub workflow was dispatched and nothing was pushed.

Official extra sources need no personal key. All requests, including explicit-parent relationship proofs and batched parent LEIs, count in the existing pool. Doffin is excluded pending verified keyless API/terms; no application key or website scraping is used. See [source terms and matching policy](docs/SOURCES.md).

Revision 2 exact local CI: **1,244 tests passed; live-20 scoped verifier passed**, with zero failed/stale sections and zero unverified values. Independent frozen-1000 verification also passed with zero unverified values. No runtime changes in release prep.

### Earlier bundled-source operational note (superseded by current Budgets)

Operational ceilings are unchanged: at most 40 attributed HTTP requests per company, and a pooled ceiling of 18 requests per distinct normalized input (360 for 20 companies). Lower configured limits still apply. These additions contain no search-engine, directory, Norid or model-provider requests. There is no search-engine integration.
