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
| LLM / paid search | Disabled; deterministic cited templates | No provider called | $0 |
| GLEIF | LEI/status/form/dates and explicit direct/ultimate parents | CC0 1.0; anonymous exact orgnr + RA000472 API, batched parent LEIs | $0 |
| TED | Exact winner/buyer public procurement awards | EU Publications Office legal notice/Commission reuse policy; anonymous published-notice API and public XML | $0 |

See [docs/SOURCES.md](docs/SOURCES.md) and [LICENSE](LICENSE) (code/documentation: MIT). Social destinations are not crawled. A brand/name match alone does not establish company ownership; ambiguous/shared/foreign group sites are withheld. Contact-only direct-registry Tier B sites publish a link without website content.

## Budgets

The pooled HTTP hard cap is 18 per distinct normalized input: 1,800 per 100, with at most 40 attributed to any company and shared calls included globally. The hard time cap is 24 seconds per distinct input (40 minutes per 100), with the default 2,400-second run limit and lower configured limits honored. These are tighter than 2,000 HTTP / 45 minutes per 100. Crawl finalization reserves preserve one output per input even when discovery is incomplete. Public DNS fallbacks are bounded and tolerate blocked UDP; end-of-run retries consume the original pool.

## Final kept 1,000-company measurement

| Section / metric | Final |
|---|---:|
| Identity | 1,000 |
| People | 997 |
| Subunit/workplace section | 774 |
| Financials | 999 |
| Website | 105 |
| Social companies | 42 |
| Jobs | 3 |
| News/activity | 236 |
| Profiles with typed locations | 998 |
| HTTP requests | 6,869 |
| Max / mean attributed requests per company | 40 / 6.830 |
| Wall seconds | 493.126 |

One completed Step 13 measurement of source `7474c372`, frozen 1,000-company batch; all new items reviewed, zero wrong-company findings. An earlier output-less attempt failed on duplicate article redirect aliases and was excluded; generic canonical deduplication was fixed before this measurement. This is a coverage measurement, not an evaluator score. [Step 13 report and review lists](bench/reports/s6-step13/SCOREBOARD.md).

## Fresh random 100-company release check

**Refresh stability: 0 company changes; one activity section (913381742) recovered from a first-run connection error (failed → not_available) and is reported as an observation change by design.** The first command used 654 HTTP / 150.781 seconds, the refresh 652 HTTP / 139.516 seconds; both emitted103 envelopes and profiles. Coverage:100 identity,97 people,58 subunits,42 financials,8 websites,3 social,0 jobs,31 activity and96 typed-location profiles. Each output independently verifies, but the initial failed → not_available recovery means this sample does not meet the strict identical-claim-ID/zero-observation gate.

Results are recorded in [the release validation report](bench/reports/release/RESULTS.md), including the selection procedure, exact source commit, both literal command runs, coverage and failed-section reasons. The sample is new relative to all recorded benchmark and earlier official samples, plus three invalid lines. Strict pairwise verification checks membership, evidence, identical claim IDs, zero changes and zero observation changes.

## Known limitations

There is **no JavaScript rendering**; static HTML-only sites can be missed. Small-company websites are often absent or cannot be proved to belong to the exact legal entity. Scanned PDFs are not used; annual-report PDF discovery and pypdf were removed after a low-yield, rate-limited trial. Only financial years returned by the registry are available. Robots restrictions, blocked network access, API limits, DNS/TLS errors and exhausted budgets cause explicit incomplete/stale states. Jobs/news coverage is bounded, and careers landing pages are never jobs. News claims describe company-published articles, not independently verified events. Templates summarize supported facts and identified run metadata; they do not provide general semantic fact checking.

## Verification workflow

[Verify Signalpost](.github/workflows/ci.yml) runs locked installation, the full pytest suite and live-20. Its `--require-clean` verifier remains strict for identity, roles, accounts and subunits. Only optional website/social, hiring and activity failures/stale states are tolerated and summarized with reasons; schema, membership, evidence, citations and global operational checks remain strict. Local release execution is documented in the release report; no GitHub workflow was dispatched and nothing was pushed.

Release checks: full suite **1,095 passed in267.75s**; exact local live-20 scoped verifier **passed**. The new random strict pair remains **failed**, as detailed above. No runtime feature or precision-rule changes were made in release preparation.

Official extra sources need no personal key. All requests, including explicit-parent relationship proofs and batched parent LEIs, count in the existing pool. Doffin is excluded pending verified keyless API/terms; no application key or website scraping is used. See [source terms and matching policy](docs/SOURCES.md).
