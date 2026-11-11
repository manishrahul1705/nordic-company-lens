# Submission notes

## Official command

Requires Python 3.12+, uv and internet access. From a clean checkout, install locked dependencies with `uv sync --frozen`, put organisation numbers in `orgnrs.txt`, then run:

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --profiles-output out/profiles.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

No credentials, bulk file, expected count, LLM or search service are required. NAV's published public token is fetched in memory from `https://pam-stilling-feed.nav.no/api/publicToken`; no personal credential is required or persisted. Provider cost is **$0**; local compute, disk and network are excluded.

## Input and outputs

The command accepts plain text (one orgnr per line), JSONL strings/numbers or objects with `organisation_number`, JSON arrays, and objects with an `organisation_numbers` array. Whitespace is normalized, checksums are checked, input order and duplicates are preserved. Blank/invalid lines each receive a failed envelope and profile. The expected count is inferred from the input. See [OUTPUT_CONTRACT.md](OUTPUT_CONTRACT.md).

- `out/envelopes.jsonl`: one schema-validated envelope per input, with claims, citations, evidence, section states and refresh changes.
- `out/profiles.jsonl`: matching evaluator-compatible profiles.
- `out/report.json`: membership, requests, time, errors, source completeness and cost.
- `out/state/`: captured evidence, caches and automatic previous snapshots. Keep this directory with the outputs.
- `out/site/`: static offline directory, company pages, comparisons and source panels. Open `index.html`; no CDN/server is required. Optional site generation can be skipped if time is exhausted.

Run the **same command again with the same state directory** to refresh automatically; `--previous` is unnecessary. Previous/current supported values are compared, original evidence is retained, and transient failed refreshes preserve previous section state and claims with a dated stale note. They do not count as company changes. First-ever failures remain honest failed states; successful proof of real additions/removals is treated as change. Exit zero means outputs were emitted, not that every source succeeded.

## Sources, licences and costs

| Source | Use | Licence / access | Provider cost |
|---|---|---|---:|
| BRREG | Identity, registered roles, subunits and returned financial years | NLOD 2.0; attribute Brønnøysundregistrene | $0 |
| NAV public feed | Active individual ads, exact employer/subunit matching; public token obtained at runtime | NAV public-feed reuse terms; no personal credential | $0 |
| Wikidata | Supplementary exact-orgnr website/social nominations | CC0, item provenance retained | $0 |
| Company websites | Ownership proof, descriptions, social links, dated news, linked active jobs | robots.txt and site access rules; no blanket open licence inferred | $0 |
| SSB KLASS | Bundled industry descriptions | CC BY 4.0 | $0 |
| LLM / search engines | No integration; deterministic cited templates | No provider called | $0 |
| GLEIF | LEI/status/form/dates and explicit direct/ultimate parents | CC0 1.0; anonymous exact orgnr + RA000472 API, batched parent LEIs | $0 |
| TED | Exact winner/buyer public procurement awards | EU Publications Office legal notice/Commission reuse policy; anonymous published-notice API and public XML | $0 |
| Doffin | **Not used** | Keyless supported API/access and reuse terms not verified | - |
| Kunngjøringer HTML service | **Not used** | robots.txt disallows /kunngjoring/; service-specific NLOD coverage not verified | - |

See [docs/SOURCES.md](docs/SOURCES.md) and [LICENSE](LICENSE) (code/documentation: MIT). Social destinations are not crawled. A brand/name match alone does not establish company ownership; ambiguous/shared/foreign group sites are withheld. Contact-only direct-registry Tier B sites publish a link without website content.

## Budgets

The pooled HTTP hard cap is 18 per distinct normalized input: 1,800 per 100, with at most 40 attributed to any company and shared calls included globally. The hard time cap is 24 seconds per distinct input (40 minutes per 100), with the default 2,400-second run limit and lower configured limits honored. These are tighter than 2,000 HTTP / 45 minutes per 100. Crawl finalization reserves preserve one output per input even when discovery is incomplete. Public DNS fallbacks are bounded and tolerate blocked UDP; end-of-run retries consume the original pool.

## Final frozen 1,000-company measurement

Measured the unchanged runtime `39a7314299c181187ee1f07af7fa75eaa631ad9c` once on 7 November 2026: run `20261107T094159020873Z-39a7314`. This frozen benchmark is separate from the fresh random precision sample below.

| Section / metric | Final |
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

## Fresh random 100-company precision check

Step 22 selected a NEW random sample of 100 valid identifiers outside all known inputs/reports/cohorts, plus three invalid lines. The fixed runtime's literal README command twice emitted **103 envelopes/profiles per run**, **336.360 seconds / 788 HTTP**, then **175.704 seconds / 753 HTTP**. **Zero company changes, zero observation changes, unmodified strict verifier exit 0**; zero unverified values. Final sample coverage: 100 identity, 96 people, 72 subunit workplaces, 42 accounts, 6 websites, 4 social companies, 2 jobs, 100 activity companies, 1 GLEIF company and no TED awards; 8,974 supported facts.

Every website/social/job/GLEIF item, 50 random registry facts and ten briefings were reviewed. A full-footer publisher-name correction rejects a different entity whose name merely contains the subject brand; the existing exact-orgnr spelling normalization is retained. Unrelated companies' calibration excerpts were removed from financial claim citations without changing amounts, periods or claim IDs. The saved frozen-1000 replay kept all 110 websites and all financial values/IDs; verification passed with zero unverified values. The original doubtful .no page was withheld; the replacement .com publisher was checked against the NUF's explicit registered head enterprise. No company-specific exception. [Full precision report](bench/reports/s6-step22/SCOREBOARD.md).

## Known limitations

There is **no JavaScript rendering**; static HTML-only sites can be missed. Small-company websites are often absent or cannot be proved to belong to the exact legal entity. Scanned PDFs are not used; annual-report PDF discovery and pypdf were removed after a low-yield, rate-limited trial. Financial depth depends on the years returned by the registry and previously supported historical facts retained on refresh. Company and consolidated accounts stay separate; currencies are not converted. GLEIF covers only exact registered identifiers with LEIs. TED awards require explicit exact-party contract links; legacy or ambiguous notices may be omitted. Robots restrictions, blocked network access, API limits, DNS/TLS errors and exhausted budgets cause explicit incomplete/stale states. Jobs/news coverage is bounded, and careers landing pages are never jobs. News claims describe company-published articles, not independently verified events. Templates summarize supported facts and identified run metadata; they do not provide general semantic fact checking.

## Verification workflow

[Verify Signalpost](.github/workflows/ci.yml) runs locked installation, the full pytest suite and live-20. Its `--require-clean` verifier remains strict for identity, roles, accounts and subunits. Only optional website/social, hiring and activity failures/stale states are tolerated and summarized with reasons; schema, membership, evidence, citations and global operational checks remain strict. Local release execution is documented in the release report; no GitHub workflow was dispatched and nothing was pushed.

The final release executes the exact local workflow commands on the final runtime; the full results and logs are in [final release validation](bench/reports/final-release/RESULTS.md). The Step 22 fixed-runtime fresh pair is separate from the final frozen benchmark. No GitHub workflow was dispatched and nothing was pushed.

Official extra sources need no personal key. All requests, including explicit-parent relationship proofs and batched parent LEIs, count in the existing pool. Doffin is excluded pending verified keyless API/terms; no application key or website scraping is used. See [source terms and matching policy](docs/SOURCES.md).

Final exact local CI: **1,244 tests passed; live-20 scoped verifier passed**, with zero failed/stale sections and zero unverified values. Independent frozen-1000 verification also passed with zero unverified values. No runtime changes in release prep.

## Bundled website candidates and registry-backed proof

Common Crawl's bundled `data/cc_orgnr_index.json.gz` is a partial CC-MAIN-2026-43 candidate index (crawl 5–18 October 2026). Runtime reads it locally by organisation number; it does not query Common Crawl. Domains are candidates only, ranked after registry nominations and before name guesses. Every candidate is fetched live and must pass the existing ownership proof and all applicable directory, parked-page, foreign-owner, group/shared-site, robots, DNS, TLS and request-budget checks. See [Common Crawl Terms of Use](https://commoncrawl.org/terms-of-use) and the third-party rights notice in `data/CC_INDEX_NOTICE.md`; no blanket licence for crawled site content is claimed.

The bundled `data/shared_identifiers.json.gz` counts registered phone/mobile numbers, email domains and distinctive legal-name keys from the official Bronnoysundregistrene entity bulk CSV. Attribution: Bronnoysundregistrene, [NLOD 2.0](https://data.norge.no/nlod/en/2.0). It is read locally, without a runtime registry bulk download. Build hashes and counts are in `data/shared_identifiers_build.json`; the complete gzip is 8,676,502 bytes, above the 3 MB target. Missing keys do not establish uniqueness.

Additional website proof can use the exact registered email visible in text or mailto links when its domain is neither free-mail nor registered to five or more entities; or a registered phone/mobile visible on the page when fewer than five entities register it. Both require a positive count in the snapshot. The complete legal name including AS/ASA can establish proof in the page title, a copyright line, or within 150 characters of the registered postcode, without being part of a longer name and without another organisation number on the page. An exact joined or hyphenated legal-name domain under .no can establish proof when all distinctive name tokens appear on the page and that distinctive name key occurs exactly once in the registry snapshot. Existing stronger proofs keep their labels. None of these rules overrides an existing rejection or owner conflict.

On a company-verified site, bounded social profile discovery includes header/footer/navigation links, eligible Organization/LocalBusiness sameAs links and actual Facebook page-plugin hrefs. Share/intent links, posts, media, events, groups, platform homepages, LinkedIn non-company paths, profile.php, agency/builder/directory handles and hidden plugins are excluded. Shared/path-scoped attribution and cross-company shared-handle suppression remain in place; social platforms are not fetched.

Operational ceilings are unchanged: at most 40 attributed HTTP requests per company, and a pooled ceiling of 18 requests per distinct normalized input (360 for 20 companies). Lower configured limits still apply. These additions contain no search-engine, directory, Norid or model-provider requests. There is no search-engine integration.
