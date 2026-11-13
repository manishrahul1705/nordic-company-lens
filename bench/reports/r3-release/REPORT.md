# R3 release run - 13 November 2026

Branch **more-websites**, tested runtime **fbe048529bc9816147ed107baf0c55a3ae985506**. No merge, push, tag or main changes. All six stages completed and measured. **Not a fully green test suite:** the unchanged shipped-index test still hard-codes 4 November after the authorized real 13 November NAV rebuild. No expectation was changed to conceal that failure.

## 1. Crawl stopped

Stopped the identified Common Crawl supervisor, worker and descendants; no restart and no further crawl downloads. The worker had resumed beyond the old heartbeat before the explicit stop. Its result file contains **180,059 complete records**, **180,049 successful fetched records**, no duplicate WARC keys and no incomplete trailing bytes. WARC payload bodies were streamed/discarded: these are stored result records, not 180,059 retained WARC bodies.

| Crawl | Records on disk |
|---|---:|
| CC-MAIN-2026-43 | 153,732 |
| CC-MAIN-2026-39 | 25,003 |
| CC-MAIN-2026-34, partial | 1,324 |

The heartbeat `SUMMARY running 178725 12798` printed **records_fetched, universe_matches**. Specifically, `12798` counted distinct mapped parent companies matching the cached Builderr universe after banned-domain exclusions. It was not pages, WARC records, raw organisation numbers or verified websites. `crawl-stop.json` records the stop and source-code interpretation.

## 2. Common Crawl index rebuilt and committed

Commit **41460e1**, Manish Rahul. Builder reads every complete record in the stopped JSONL snapshot, independently of segment completion flags, including the partial 2026-34 records. The existing format, mod-11 validation, labelled snippets, cached official subunit mapping, whole-domain exclusion at 3+ observed orgnrs, newest timestamp per parent/domain, maximum three domains per parent and deterministic sorting are preserved.

| Build metric | Result |
|---|---:|
| Records processed | 180,059 |
| Pages with a labelled valid orgnr, before domain exclusion | 32,608 |
| Unique labelled orgnrs, before exclusion/mapping | 20,529 |
| Excluded domains carrying 3+ distinct valid orgnrs | 79 |
| Parent companies in index | 19,735 |
| Candidate entries | 20,832 |
| Distinct domains | 20,575 |
| Universe candidate matches / universe size | 12,873 / 411,160 |
| Expected matches per 1,000 | 31.309 |
| Compressed bytes | 1,771,479 |

Build: **2026-11-13T00:19:33.469439Z**. Index SHA-256: `44fa7de01004ea7a31bc9031d91708fde202bb23dd2f78cca8e58e862b180299`. Source snapshot SHA-256: `ff805e51508acca894c8ba079ea003d21da86132d1cc8f9ccab15895951cc3a6`. All 30 fixed-seed snippet/mapping checks pass. Re-encoding produces byte-identical gzip; maximum-three and sorted-domain checks pass. Candidate coverage is not verified-site coverage.

Updated `data/CC_INDEX_NOTICE.md` and `data/cc_orgnr_index_build.json` contain the new build counts, crawls, page timestamp ranges and third-party-rights/terms notice. Both cached bulk/universe inputs were reused; no crawl or raw download is committed.

## 3. Public NAV index rebuilt and committed

Commit **fbe0485**, Manish Rahul. **Public token only**, all credential variables stripped; no private token file read and no disk seeding. Real public feed and live details were read; schema and completeness validation pass.

| NAV build metric | Result |
|---|---:|
| Snapshot build timestamp | 2026-11-13T00:26:42.872674Z |
| Active, unexpired indexed ads | 9,296 |
| Employer orgnrs | 5,899 |
| Compressed bytes | 429,720 |
| Failed details | 0 |
| Fresh-fetched ads / disk-seeded ads | 9,296 / 0 |
| Build seconds / requests | 1,467.062 / 10,099 |

Two initial attempts failed before a request: the development builder constructed its Budget from a nonexistent `unused` input, giving it zero budget under the current hard-cap logic. The builder now sizes its development budget from the frozen input via `--organisations`. Production budget/fallback logic is unchanged. The successful run used a fresh checkpoint, public access and no cached ad-body seed. Full request log stays in ignored `bench/cache/r3-release-nav-build`; small provenance is in `nav-summary.json`. No token value was printed or committed.

## 4. Final frozen 1,000 benchmark

Fresh state: `bench/runs/r3-release-final`. Frozen input SHA-256: `7ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782`. README command, with the cohort/output paths substituted:

```sh
uv run --frozen signalpost run --organisations bench/inputs/1000-r3/batch.jsonl --output bench/runs/r3-release-final/envelopes.jsonl --profiles-output bench/runs/r3-release-final/profiles.jsonl --report bench/runs/r3-release-final/report.json --state-dir bench/runs/r3-release-final/state --site-dir bench/runs/r3-release-final/site
```

Credentials stripped from the child environment; no bulk override, LLM, paid API or search integration. Robots and host spacing retained. Request limits: **18,000 pooled / 40 per company**. LLM calls 0, search queries 0, estimated paid cost $0. The search adapter is absent in the fresh clone.

| Metric | Requested 05b2889 baseline | Final release run | Difference |
|---|---:|---:|---:|
| Envelopes / profiles | 1,000 / 1,000 | 1,000 / 1,000 | 0 |
| Exit code | 0 | 0 | n/a |
| Websites | 114 | 113 | -1 |
| Social companies | 48 | 47 | -1 |
| Jobs companies | 3 | 2 | -1 |
| Activity companies | 1,000 | 1,000 | 0 |
| GLEIF companies | 32 | 32 | 0 |
| TED companies | 0 | 5 | +5 |
| News companies / articles | 7 / 67 | 7 / 69 | 0 / +2 |
| Distinct facts | 165,614 | 165,424 | -190 |
| Total HTTP | 9,150 | 9,281 | +131 |
| Mean HTTP / company | 9.150 | 9.281 | +0.131 |
| Max attributed HTTP / company | 40 | 40 | 0 |
| Full wall seconds, including site | 1,878.250 | 1,650.170 | -228.080 |
| Seconds per 100 | 187.825 | 165.017 | -22.808 |
| Deadline hits | 0 | 0 | 0 |
| Warnings / site warnings | 0 / 0 | 0 / 0 | 0 |

The baseline is the retained `proof-depth-live` run corresponding to the measured change committed as 05b2889. Its execution metadata records pre-commit base 51a04b3 plus the retained measured patch; no new baseline was fabricated. Times are live-machine observations, not a controlled speed attribution.

NAV mode: **declared_index**, age 0.230 days, 2 forward-feed pages and 3 detail requests, 6 total NAV requests. NAV total 139.735 s; feed 2.391 s. Feed/details complete, no unchecked candidate companies and no NAV cap hits. Overall hiring still has three failed company-site careers checks (`company_careers_website_budget_exhausted`, Askøy24, Tensio, Bridge Technologies); this is not represented as complete careers coverage. The lost job company 991247610 had an ad expiring `2026-11-13T00:00:00+01:00`, before the refreshed snapshot. Identity 1000 available, roles 993 available/4 failed/3 absent, subunits 774 available/226 absent, accounts 999 available/1 failed. All source states remain visible.

The first benchmark attempt was invalidated by a host pause: elapsed time jumped from 241 s to over 15,000 s. A second attempt wrote data but lost its process during a turn interruption before site/final exit recording. Neither is reported as a successful benchmark. The final detached attempt used a temporary Windows idle-sleep request and completed normally. Both interrupted artifacts remain ignored and their limitations are in `host-interruption.json`; no timing was subtracted or repaired. Source review extraction overlapped part of site writing, so wall-time comparison is not a controlled performance experiment.

### Website composition by proof type

| Proof type | Available websites |
|---|---:|
| orgnr_on_page | 38 |
| jsonld_vatid | 5 |
| registry_declared_name_tier_a | 25 |
| legal_name_without_suffix_and_two_contacts | 9 |
| legal_name_and_registry_contact | 24 |
| unique_no_corroborated | 7 |
| registry_declared_hard_contact_tier_b, link-only | 3 |
| registry_phone_on_site | 2 |
| registry_email_on_site | 0 |
| Total | 113 |

## 5. Complete gain/loss review

**Three gained website URLs reviewed: 3 correct, 0 wrong, 0 doubtful; zero new social profiles.** This is two additional companies plus one host alias. No precision change was needed, so counts after review remain 113 websites / 47 social companies. All exact claim values, proof types, page URLs, snippets and source hashes are in `new-items-reviewed.json`; every gain and loss is listed in [REVIEW.md](REVIEW.md).

| Orgnr | Legal name | URL | Exact proof type | Exact page text / verdict |
|---|---|---|---|---|
| 936629466 | CLOSVA AS | https://www.closva.com | jsonld_vatid | "Owned by Closva AS · Org. no. 936 629 466" - correct; www alias of baseline closva.com |
| 911691248 | ISTAD ART SOLUTION NORWAY NUF | https://www.pederistad.no | registry_declared_hard_contact_tier_b | "peder istad - Nyheter" - correct registry-declared link, corroborated by registered DAGL/LEDE Peder Istad; explicitly link-only (`content_allowed=false`), not an assertion of a printed legal orgnr/ownership proof and no inherited content/social/news |
| 936010695 | SIGMUND OLSEN AGENTUR AS | https://www.soa.no | orgnr_on_page | "Sigmund Olsen Agentur AS", "Org. nr: 936 010 695" - correct, registered street/phone corroborate; cc_index was a candidate only |

Lost company websites: ENSURE IT AS `https://ensure-it.eu` (repeated `website_timeout`), JAR HELSE AS `https://www.jarhelse.no`, and RISIKOKONSULENTEN AS `https://risikokonsulenten.no` (earlier stricter contact-only proof: no full legal name, and no qualifying independent two-contact suffix-free proof). Jar Helse's Facebook and Instagram URLs are the only lost social profiles. Closva's old apex URL is also explicitly listed as a replaced alias, not a lost company. No wrong-company exceptions were added and no ownership rule was weakened to recover a loss.

### Correction respected

All attempted restrictions on the measured suffix-free rule and all related test changes were **restored to their original committed contents before Stage 4**. `restored-rule-audit.json` verifies original file hashes/content. `legal_name_without_suffix_and_two_contacts` remains default-on with its original exact suffix-free name + name-derived domain + two independent registry contacts; nine sites use it in the final output.

Only the existing contact-only `registry_phone_on_site` and `registry_email_on_site` paths require the full legal name including form in title/headings/footer, exactly as instructed. No active `legal_name_masthead` or `unique_legal_name_domain` return rule exists; compatibility strings are not accepting paths. `unique_no_corroborated` needs an exact .no name/domain, independently verified registry uniqueness and registry location/contact/role-holder corroboration, not uniqueness/name alone. Original declared Tier A/B behavior and all foreign/group vetoes are preserved. No general "full name everywhere" tightening remains.

## 6. Fresh-clone refresh determinism

The existing release cohort is **100 valid companies + 3 invalid lines** (`bench/reports/release/orgnrs.txt`), explicitly recorded in `cohorts.json`. It is a separate release smoke/refresh cohort, not a claim that the 1,000-company benchmark was refreshed. Each pair used a new local clone of this branch, `uv sync --frozen`, the literal README command twice, and one initially empty state directory shared only by that pair. Child credentials were stripped. Both rebuilt indexes and shared counts were byte-identical to committed bundles.

The first pair **failed**: registry-activity `timeout` in its first run recovered in the second, producing 100 genuine observation changes and different supported announcement IDs. Company changes were 0. Those observations were not suppressed or relabelled; the failed verifier and artifacts are retained in `refresh/` and `refresh-failure-diagnosis.json`.

A second complete pair, after source recovery, used another **fresh clone and empty state** with no code changes:

| Metric | Run 1 | Refresh run 2 |
|---|---:|---:|
| Exit | 0 | 0 |
| Envelopes | 103 | 103 |
| Wall seconds | 199.256 | 204.514 |
| HTTP | 722 | 714 |
| Company changes | 0 | 0 |
| Observation changes | 0 | 0 |
| Deadlines / warnings | 0 / 0 | 0 / 0 |

**Unmodified strict verifier PASS**, identical claim IDs: 8,454 published claims, 316 source blobs verified, 103 cited briefings / 242 sentences, 0 unverified synthesis values. See `refresh-retry1/execution.json` and `refresh-retry1/strict-verifier.txt`. A healthy-source pair passes the requested gate; the retained outage pair shows that genuine source recovery still records observations honestly.

## Test diagnosis and remaining limitation

The earlier single failure was `test_real_os_process_kill_and_checkpoint_recovery`: its uninterrupted baseline subprocess exceeded 45 seconds before the kill/checkpoint assertions. Concurrent NAV rebuild/Windows network/disk load was present; exact delay breakdown was not captured, so load is a likely contributor, not a proven code cause. The unchanged test passed alone in 98.50 seconds across its three phases, and passed in the final full-suite run.

Final full suite: **1,381 passed, 1 failed in 648.07 s**. The remaining failure is `test_s67_compliance.py::test_shipped_index_valid_through_november_30_without_redating`, which hard-codes `built_at.startswith('2026-11-04')`; the real authorized rebuild is `2026-11-13T00:26:42.872674Z`. The schema/age load for 30 November succeeds. No redating, skipping, weakened assertion or expectation change was used. This old-date assertion remains an open test-maintenance issue; the release is not described as all tests green. `pytest-final.txt` and `test-diagnosis.json` retain the exact evidence.

No runtime proof, scoring, identity, output-format or test changes remain from this release task. The only production artifacts changed are the rebuilt bundled CC and NAV data; the NAV builder budget repair and measurement scripts are development-only. No search engines, directory/Norid sources, paid APIs or LLMs were used. Robots, pooled budget and per-company cap were preserved. No real credentials or raw crawl/bulk/universe downloads were committed. Protected branches are unchanged. No merge or push. Stop here for review.
