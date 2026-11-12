# R3 paired benchmark and complete source review

Latest completed live verification: **112 websites, 48 social companies, 3 jobs companies, 1,000 activity companies** on corrected runtime `81086a9`. [Measured comparison and release refresh result (strict pair FAIL)](#fresh-live-corrected-verification--12-november-2026) below supersede the historical offline projection as the current result.

Runtime under review: main `abc33af` versus candidate `18dde3c`. Precision correction: `7d38baa`. Merge `cdb2d12` includes fix-large-company-site; search-engine removal is `fc26f04`. Nothing pushed; main and fix-large-company-site refs unchanged.

## Input and execution

The existing cached fixed-seed 20261103 Builderr cohort was available on this laptop and frozen as `bench/inputs/1000-r3/batch.jsonl`: 1,000 distinct valid input records, SHA-256 `7ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782`. It was not redrawn. The old Step 20 raw input was not present at its archived path, so byte equality to that specific historical run is not asserted. Both R3 runs use the exact frozen bytes.

At least 10 GiB free was checked before both runs (65,174,331,392 bytes baseline; 63,470,505,984 candidate). Runs were sequential, each with empty state, no bulk CSV and default budgets. Key/token/secret and provider environment variables were stripped. NAV uses the public-token path. Both runs used:

```sh
uv run --frozen signalpost run --organisations bench/inputs/1000-r3/batch.jsonl --output <run>/envelopes.jsonl --profiles-output <run>/profiles.jsonl --report <run>/report.json --state-dir <run>/state --site-dir <run>/site
```

Baseline was an isolated local clone at main abc33af; candidate was more-websites. Frozen installation succeeded. Each run produced exactly one envelope and profile for every input, in input order. Both exited 0. Wall time includes startup, source collection, synthesis, output and site publishing. Sources are live and may vary between sequential runs; this is not an offline controlled network replay.

## Live measurements before precision corrections

| Metric | Main abc33af | Candidate 18dde3c |
|---|---:|---:|
| Websites | 106 | 129 |
| Social companies | 43 | 63 |
| Jobs companies | 3 | 3 |
| Activity companies | 1000 | 1000 |
| Distinct available facts | 165504 | 165680 |
| HTTP total | 9493 | 9545 |
| HTTP mean/input, including shared | 9.493 | 9.545 |
| HTTP max/company | 40 | 40 |
| Wall seconds | 1105.433 | 1095.426 |
| Deadline hits | 0 | 0 |
| Site warnings | none | none |
| All report warnings | none | none |
| Envelopes / profiles | 1000 / 1000 | 1000 / 1000 |

Facts are distinct `(orgnr, field, JSON value, reporting period)` among available non-null claims, not evidence/citation counts. The 3 jobs companies include actual NAV/company-site job records; landing pages do not count.

Raw gains: 23 website companies; 20 social companies and 58 profile additions across 34 companies (including existing social companies). No raw baseline website company was lost. Nuve AS changed apex to www with identical body SHA-256 and exact orgnr proof.

### New websites by proof and source

| Raw proof type | Count |
|---|---:|
| legal_name_and_registry_contact | 1 |
| legal_name_masthead | 7 |
| orgnr_on_page | 3 |
| registry_email_on_site | 1 |
| registry_phone_on_site | 3 |
| unique_legal_name_domain | 8 |

| Raw candidate source | Count |
|---|---:|
| cc_index | 3 |
| legal_name_slug | 18 |
| registry_email | 1 |
| wikidata_website | 1 |

## Hand review and correction

[REVIEW.md](REVIEW.md) lists every company, orgnr, website/profile URL, proof type, verbatim saved excerpt, verdict and reason. JSON ledgers retain hashes and source URLs. Review inspected the original live source bodies and registry context; social platforms were not fetched.

Raw website verdicts: 10 correct, 4 wrong, 9 doubtful. Raw social profile verdicts: 41 correct, 4 wrong, 13 doubtful. Correct means the reviewed source supports company attribution; it is not a universal precision guarantee. Conservative runtime rules may withhold genuine but unproven aliases.

Generic corrections, with no company-specific exceptions:

- Removed name-only legal-masthead and unique-name-domain publication. This prevents punctuation-collapsed namesakes, placeholders and bare app-shell titles from proving ownership.
- Email-only proof now requires the registered non-free-mail domain to occur for exactly one registry entity, not fewer than five. Ice Drift staff email on a domain shared by four entities did not identify Straumsnes Utvikling as site owner.
- Additional contact proofs reject blank bodies and short Her kommer placeholders.
- Restored company/verified-brand handle matching for social profiles. Header/footer/sameAs presence alone cannot authorize founder, artist, sister/group or agency profiles. Facebook plugin support remains, with the same attribution check.

Regression coverage includes placeholders, URL/email repetition, blank shells, shared employee email, unrelated footer handles, plus existing named wrong-company/group/foreign-orgnr tests. The complete suite passes: **1,259 passed in 374.14 s**. The cleanup-only merged revision earlier passed 1,251 tests; only search-specific tests/function were removed then.

## Offline re-derivation after corrections

No third live benchmark was run. `scripts/r3_rederive.py` rechecks hash-verified saved candidate HTML with current proof and social functions. It never makes requests; original outputs are untouched. Retired proofs are withheld unless an existing retained proof can be established from saved pages; website-derived claims and site jobs/articles are conservatively withheld when the site loses proof. Exact-name registry/Wikidata social claims keep the existing direct-match path.

| Offline conservative projection | Count |
|---|---:|
| websites | 107 |
| social_companies | 48 |
| jobs | 3 |
| activity | 1000 |
| facts | 165488 |

Retained reviewed gains: **8 website companies**, **5 new social companies**, **10 new social profiles**. All retained reviewed gains are correct: **0 wrong, 0 doubtful**. Raw candidate 129 websites / 63 social companies becomes an offline conservative 107 / 48; jobs and activity remain 3 / 1000. HTTP and wall time are only the pre-correction live measurements above; they are not measurements of the narrowed runtime.

| Retained new proof | Count |
|---|---:|
| legal_name_and_registry_contact | 1 |
| orgnr_on_page | 3 |
| registry_phone_on_site | 4 |

| Retained new candidate source | Count |
|---|---:|
| cc_index | 3 |
| legal_name_slug | 5 |

### Baseline websites conservatively withheld by the offline projection

These seven were present in both live runs. The offline script does not replay the collector registry-uniqueness recovery or obtain proof pages skipped after the trial early acceptance. Therefore they are listed as projection losses, not claimed as seven measured runtime regressions. A fresh post-correction live run is needed for definitive final coverage/timing. No old evidence is silently carried forward.

| Company | Orgnr | Baseline URL | Baseline proof | Reason |
|---|---|---|---|---|
| FORMOSA AS | 994382217 | https://www.formosa.no | unique_no_corroborated | Trial name-only proof retired; saved candidate pages alone did not reproduce the baseline recovery path. |
| ASKØY24 AS | 923998012 | https://www.askoy24.no | unique_no_corroborated | Trial name-only proof retired; saved candidate pages alone did not reproduce the baseline recovery path. |
| TENSIO AS | 922828172 | https://www.tensio.no | unique_no_corroborated | Trial name-only proof retired; saved candidate pages alone did not reproduce the baseline recovery path. |
| NORTH GREY AS | 934289099 | https://www.northgrey.no | unique_no_corroborated | Trial name-only proof retired; saved candidate pages alone did not reproduce the baseline recovery path. |
| ULSTEIN MINILAGER AS | 922187991 | http://www.ulsteinminilager.no | unique_no_corroborated | Trial name-only proof retired; saved candidate pages alone did not reproduce the baseline recovery path. |
| STILLASFORDEG AS | 924688696 | https://stillasfordeg.no | unique_no_corroborated | Trial name-only proof retired; saved candidate pages alone did not reproduce the baseline recovery path. |
| ANKERMANN AS | 917329435 | https://www.ankermann.no | orgnr_on_page | Trial name-only proof retired; saved candidate pages alone did not reproduce the baseline recovery path. |

The conservative fact total is below baseline because some previously supported site facts are withheld with those sites and social aliases are dropped. This projection does not prove a no-regression coverage gate; no such gate is claimed.

## Cleanup and retained artifacts

No search-engine integration remains. Deleted `src/signalpost/web/search.py`, `tests/test_search.py`, `tests/test_optional_brave.py`, `tests/test_bench_search_environment.py`; removed only its mock test from mixed `tests/test_web.py`, preserving its activity/website tests. Search-only CLI/config/env/benchmark switches and source-document references were removed. `rg -n -i "brave|search_api|api_key" src tests docs README.md SUBMISSION.md` returns no hits. TED structured procurement queries and local offline-site search are unchanged. Compatibility zero-search cost metrics remain constants; no adapter or provider/environment reader remains.

Hard caps unchanged: 40 HTTP/company, pooled 18/distinct input, 2400 s run default. No runtime-specific company exceptions. Source outputs/state/site and isolated baseline checkout are ignored under bench/runs and the raw folder; committed reports contain only derived metadata and short source excerpts. Unrelated pre-existing overnight-worker files are not included.

Reproduction:

```sh
uv run pytest -q
uv run python scripts/r3_analyze.py --baseline bench/runs/r3-baseline --candidate bench/runs/r3-candidate --output bench/reports/r3-benchmark
uv run python scripts/r3_rederive.py
uv run python scripts/r3_review.py
uv run python scripts/r3_finalize_report.py
```

Analyzer recreates the raw review inputs; run review after it to restore the manual verdict ledger. Manual verdicts in r3_review.py document this fixed cohort, never production exceptions. Projection is an analytical lower bound, not new evaluator profiles or a regenerated site.

## Fresh live corrected verification — 12 November 2026

The corrected runtime `81086a9` was run once with the same README command, frozen 1,000-company bytes and defaults, fresh empty state, no bulk and stripped credentials. Exit 0; 1,000 envelopes and profiles; input SHA-256 unchanged. These are live measurements, replacing the earlier projection as the current measured result. No production code changed during this verification.

| Metric | Main `abc33af` | Corrected `81086a9` |
|---|---:|---:|
| Websites | 106 | 112 |
| Social companies | 43 | 48 |
| Jobs companies (NAV or company-site) | 3 | 3 |
| Activity companies | 1000 | 1000 |
| Distinct available facts | 165504 | 165602 |
| HTTP total | 9493 | 9735 |
| HTTP mean/input | 9.493 | 9.735 |
| HTTP max/company | 40 | 40 |
| Wall seconds, full process | 1105.433 | 2052.506 |
| Deadline hits | 0 | 0 |
| Site warnings | none | none |
| All report warnings | none | none |
| Envelopes / profiles | 1,000 / 1,000 | 1,000 / 1,000 |

The full-process wall time includes site construction, output and shutdown, and is higher than the earlier run. `report.runtime_ms` is 1,165.922 s (baseline 806.765 s), before the full site/end-to-end interval; the generated site is 762,927,741 bytes versus 757,791,285. This is not an isolated CPU/network timing experiment: an unrelated pre-existing Common Crawl worker was observed and left untouched, and an initial offline envelope scan overlapped late publication. No speed improvement is claimed. Both source snapshots and all measured timings remain unchanged.

### Baseline websites missing now

Exactly two baseline website companies are missing. Neither loss reproduces as a difference between main and corrected ownership code on the same saved evidence. No R3 regression fix was necessary; existing vetoes were preserved.

| Company | Orgnr | Baseline URL | Reason / replay |
|---|---|---|---|
| ISTAD ART SOLUTION NORWAY NUF | 911691248 | https://www.pederistad.no | Homepage HTTP 200 logged SHA `204ee52e…83012`, but that blob is absent from disk. The final link-only guard cannot read the registered-role-holder proof and withholds it. Reconstructing this missing-file condition on the original link-only claim with valid evidence IDs withholds the site in both runtimes. The cause of file disappearance is unresolved; it is not established as a live-content change or R3 code regression. |
| BERGEN VAKTMESTERTJENESTER AS | 990412375 | https://bnv.no | New privacy-page bytes contain generated HTML `id="gap-943737207"`; the pre-existing raw identifier scan misreads this checksum-valid design ID as `foreign_orgnr`. Baseline privacy bytes lack it. Both main and corrected code accept the old page and reject the new page identically. This is a live-page-triggered pre-existing false positive, left open rather than weakening a veto in this verification. |

The two runtime replay JSON files are identical. They record old/new body hashes and the raw element-ID excerpt; original responses and outputs were not edited. Peder Istad’s missing-body reconstruction is a diagnostic experiment, not a regenerated evaluator envelope.

All seven highlighted sites are present live:

| Company | Orgnr | Current URL | Proof |
|---|---|---|---|
| FORMOSA AS | 994382217 | https://www.formosa.no | unique_no_corroborated |
| ASKØY24 AS | 923998012 | https://www.askoy24.no | unique_no_corroborated |
| TENSIO AS | 922828172 | https://www.tensio.no | unique_no_corroborated |
| NORTH GREY AS | 934289099 | https://www.northgrey.no | unique_no_corroborated |
| ULSTEIN MINILAGER AS | 922187991 | http://www.ulsteinminilager.no | unique_no_corroborated |
| STILLASFORDEG AS | 924688696 | https://stillasfordeg.no | unique_no_corroborated |
| ANKERMANN AS | 917329435 | https://www.ankermann.no | orgnr_on_page |

Heiane Legesenter and Støren Dyreklinikk changed apex to www; the registered domain and ownership rule are unchanged. Støren’s proof body hash is identical. These are not company losses.

### Gains and review gate

Eight gained websites and nine new social profiles (five newly social companies) match exact company/URL entries already reviewed correct in `REVIEW.md`. There were **zero previously unreviewed gains**, zero wrong and zero doubtful inherited items. The current proof excerpts and links are in [gain-review-input.json](live-verification/gain-review-input.json); [review-result.json](live-verification/review-result.json) records the gate. New website proofs: orgnr 3, legal-name-plus-contact 1, registry phone 4. Sources: cc_index 3, legal-name guesses 5. No social platform was fetched.

### Fresh-clone release refresh pair

A new isolated local clone of `81086a9` installed with `uv sync --frozen`, with both bundled gzip indexes present (954,922 and 8,676,502 bytes). It used `bench/reports/release/orgnrs.txt` (103 lines: 100 valid and three invalid inputs), copied to `orgnrs.txt`. The literal README command ran twice against the same new `out/state`; outputs were archived before the second run. Credentials were stripped.

| Run | Exit | Envelopes / profiles | HTTP | Company changes | Observation changes | Strict verifier exit |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 0 | 103 / 103 | 807 | 0 | 0 | 0 |
| 2 | 0 | 103 / 103 | 749 | 0 | 5 | 1 |

**Strict refresh-pair result: FAIL (`Claim IDs differ`), despite zero company changes.** A.U. Bygg AS (993581755) had a TimeoutError on `/kontakt-29389s.html` in run 1 and HTTP 200 on the same page in run 2. Five genuinely newly checked facts (two emails, one phone, two descriptions) produced five observation changes. The homepage bytes and company identity are unchanged. This transient network difference is preserved in [release-diagnosis.json](live-verification/release-diagnosis.json); no retries were run merely to obtain a passing pair. The unmodified verifier checks schemas, exact membership, stored body hashes, verbatim excerpts, synthesis, stable claim IDs and zero company/observation changes. See [execution](live-verification/release-execution.json) and the run verification logs. Both runs separately pass the unmodified schema/evidence verifier; the second standalone check is in `release-run2-evidence-verification.txt`. Only the strict refresh-pair stability check fails. No outputs, verifier assertions or test expectations were changed to make the gate pass.

Full runtime suite: **1,259 passed in 658.85 s** (see [tests.json](live-verification/tests.json)). Measurement-only changes add release/loss replay scripts and extend job counting to include `hiring.site_job.*`, alongside `hiring.job.*`. Neither source runtime nor existing wrong-company tests changed. Main and fix-large-company-site refs remain untouched; nothing pushed.
