# Stage K documentation numeric audit

Documentation only. No agent, test, benchmark, index, measured value or original historical link changed. `rg -n "[0-9]" README.md SUBMISSION.md` was inspected; every numeric-bearing line is reproduced below with its source or non-measurement classification. Licence/API/runtime versions and configured limits are not empirical measurements and are identified separately rather than falsely sourced to a benchmark. Existing links were checked as multisets: none removed.

## Measurement source groups checked

- Current run1/run2 counts, facts, request means/maxima and times: committed stage-g/summary.json, noise-band.json and run1/run2-execution.json. Reviews:stage-g/review-verdicts.json. Probe/status counts:stage-g/run1/ted-metrics.json, run2/ted-metrics.json, probe-round1/2.json. Final remains run1.
- Current tests:stage-g/pytest.txt (1400); refresh:stage-e/refresh/strict-verifier.txt (0/0).
- Revision2 frozen cohort:final-release/RESULTS.md (108/44/3/1000,166207facts,8589requests,1017.315seconds,1244tests), plus its committed execution/verification files.
- Revision2 random cohort:s6-step22/SCOREBOARD.md and fixed-official-run/RESULTS.md (103outputs;336.360/788 and175.704/753;coverage and8974facts;50registry claims/ten briefings).
- Index provenance:r3-release/REPORT.md (13November2026 rebuilds,20832candidates/19735parents,9296NAVads/5899employers). Shared counts gzip8676502bytes:r3-benchmark/SCOREBOARD.md.
- Older110website replay/projection:s6-step22/SCOREBOARD.md and final-release/RESULTS.md; preserved as historical, not current coverage.
- Defender IDs/times:stage-g/defender-evidence.json; these are local security events, not agent measurements.

## Items not sourceable as a measured benchmark value

No unsupported empirical measurement was identified. The **3 MB** shared-count target is a historical requested target, not a measured size. Python3.12+, licence numbers (NLOD2.0/CCBY4.0/CC01.0), API/authority IDs, configuration caps, step/revision numbers and command/path digits are specifications or identifiers, not benchmark measurements. The external **2000HTTP/45minutes per100** comparison is a challenge allowance, not measured consumption. No such item was changed or presented as a measurement.

## Every numeric-bearing line

### README.md:7

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/). From this repository:

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### README.md:31

Website research, NAV hiring checks, public activity and template synthesis are on by default. There is no search-engine integration; provider cost is $0. Use `--no-websites`, `--no-hiring` or `--no-public-activity` to opt out of those sources. `--expected-count` is optional and is normally unnecessary.

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### README.md:33

Requests use a pooled global ceiling of 1,900 per 100 distinct normalized input records, with at most 40 attributed to any one company. The default run time limit is 2,400 seconds, also bounded by a hard 24 seconds per distinct normalized input (40 minutes per 100). Lower configured limits remain effective. Careers checks run after primary collection using remaining budget, without earmarking or reducing the activity allowance. Incomplete careers coverage is reported honestly. The shared deadline and 40-request company ceiling still apply. Registry-declared websites require the legal name or hard registry corroboration; sites corroborated only by a contact or role-holder publish a website link without site content. Registered subunit identifiers can establish ownership. Shared domains, conflicting owners, parked pages and directories are withheld. Exact-name-only and contact-only two-signal publication were rejected in the Step 10 audit; guessed domains retain the stronger existing ownership proof.

Source/classification: Configuration/algorithmic or external ceiling, not an empirical measurement; documented in bench/reports/stage-d/REPORT.md, stage-e/REPORT.md, s6-step13 and s6-step15 reports as applicable.

### README.md:43

To run the bundled benchmark instead, use its frozen input and registry snapshot and pass an explicit expected count. See [the Step 7 benchmark record](bench/reports/s6-step7/SCOREBOARD.md).

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### README.md:59

Registry identity, roles, subunits and accounts come from official Brønnøysundregistrene APIs or the supplied registry snapshot. Registry data is attributed under NLOD 2.0. Optional hiring uses the official NAV feed and live detail verification against the exact company or registered subunit. The bundled NAV index is declared discovery metadata; it does not replace live evidence.

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### README.md:61

Website research follows robots, public-IP, redirect, request and time limits. Published website facts require the documented company-identity proof. Social profile links can be recognised on accepted company pages; social platforms are not fetched. Public activity keeps company-published articles, supported registry updates and exact-party procurement awards separately labelled. Registry updates use the official Enhetsregisteret API, not the robots-disallowed Kunngjøringer HTML service. Bundled SSB KLASS industry titles retain CC BY 4.0 attribution to Statistics Norway.

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### README.md:67

Wikidata's CC0 structured data is queried by exact Norwegian organisation number for website nominations and name-matched social identifiers. Website nominations still need live ownership proof; Wikidata failures do not prevent registry or website research. Wikidata social claims identify their item URL and licence.

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### README.md:73

| Brønnøysundregistrene (BRREG) | Company identity, roles, subunits and accounts through the live official API | NLOD 2.0; attribute Brønnøysundregistrene | $0 |

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### README.md:74

| NAV public job feed | Candidate discovery and live verification of active job details | Public feed; [NAV reuse terms](https://arbeidsplassen.nav.no/vilkar-api) | $0 |

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### README.md:75

| Wikidata | Supplementary website/social nominations by exact orgnr | CC0; retain item attribution in claim provenance | $0 |

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### README.md:76

| Company websites | Ownership proof and company-published descriptions, social links and activity | Robots.txt and site access rules are followed; no open licence is inferred | $0 |

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### README.md:77

| GLEIF | Exact-orgnr LEI facts and explicitly supported parents | [CC0 1.0](https://www.gleif.org/en/meta/lei-data-terms-of-use); anonymous API, RA000472 matching | $0 |

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### README.md:78

| TED | Exact winner/buyer public procurement awards | [EU Publications Office reuse terms](https://ted.europa.eu/en/legal-notice); anonymous API and public notice XML | $0 |

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### README.md:80

| Kunngjøringer HTML service | **Not used** | w2.brreg.no robots.txt disallows /kunngjoring/; no NLOD grant for this service assumed | - |

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### README.md:81

| Search engines | No integration | No provider is called | $0 |

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### README.md:82

| Language models | None; summaries use deterministic templates | No model provider is called | $0 |

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### README.md:86

The command has **$0 provider cost**. Compute, storage and network costs are excluded. `--synthesis` accepts `template` (default) or `auto`, which both use templates; `llm` is rejected.

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### README.md:94

Step 13 keeps brand-domain discovery bounded to four actual-use nominations per company, tried only after stronger candidates fail; a brand match never proves ownership. One end-of-run retry may revisit the top three transient-failure candidates within the original pooled caps. Financial output retains every distinct company fiscal year returned, roles include all registered role types, and profiles show distinct typed postal addresses alongside workplaces and business addresses. Dated article publication remains tied to dates on fetched article pages.

Source/classification: Configuration/algorithmic or external ceiling, not an empirical measurement; documented in bench/reports/stage-d/REPORT.md, stage-e/REPORT.md, s6-step13 and s6-step15 reports as applicable.

### README.md:96

Registry announcements use the official, unauthenticated NLOD 2.0 Enhetsregisteret updates API. Explicit returned changes retain their supported field details; records without supported details are labelled only as a recorded update or an explicitly unspecified registry event. Publication date (not inferred effective date), exact orgnr, source excerpts and retrieval evidence are retained. They are labelled "Registry announcement", separately from company-published news. The collector retains at most 50 announcement claims per company within 36 months, deduplicates event/field/value records, and uses a shared acquisition budget of at most two HTTP requests per input, inside the existing pooled cap. Bare or unspecified records never imply a specific business change, and never qualify as a major event in the analyst briefing. Registered subunit events require the retained exact-parent registry proof. Transient failed refreshes retain previous supported announcements as stale with original evidence.

Source/classification: Configuration/algorithmic or external ceiling, not an empirical measurement; documented in bench/reports/stage-d/REPORT.md, stage-e/REPORT.md, s6-step13 and s6-step15 reports as applicable.

### README.md:98

Step 15 bounds legal/subunit-name discovery to eight candidates, with Norwegian-letter spellings and joined/hyphenated .no forms before .com. Candidate DNS is checked before HTTP. Proof-page recovery preserves the previous linked/common-path selection before up to two extra same-host targets, inside the original budgets. Explicit CMS site-owner identifiers can be read from JSON/script/footer data; arbitrary tracking numbers, customer lists and another entity do not prove ownership. Existing publisher/group/parking vetoes and exact-handle social attribution remain unchanged.

Source/classification: Configuration/algorithmic or external ceiling, not an empirical measurement; documented in bench/reports/stage-d/REPORT.md, stage-e/REPORT.md, s6-step13 and s6-step15 reports as applicable.

### README.md:103

Final measurement is **Stage G run 1**, selected after Stage H confirmed local antivirus interference in run 2, on the frozen 1,000-company cohort. It published 113 websites, 47 social companies, 2 jobs companies, 1,000 activity companies, 7 news companies / 69 articles, 32 GLEIF companies and 0 TED awards; 165,481 facts. Run 2 published 112 websites; other listed coverage and fact counts were identical. The observed website range is **112-113**, article range **69-69**. These two observations are not a confidence interval. Full per-metric band and every website/article membership difference are in [Stage G NOISE.md](bench/reports/stage-g/NOISE.md).

Source/classification: bench/reports/stage-g/summary.json; noise-band.json; review-verdicts.json; probe-round1.json; probe-round2.json; run1-execution.json; run2-execution.json.

### README.md:105

Every new website versus Stage E was reviewed in both runs: ENSURE IT AS, exact organisation number 934620011 on the saved page; 2 correct / 0 wrong / 0 doubtful. Neither run published a TED award, so no Stage G awards required review. This is an incremental review, not an exhaustive new precision estimate of all facts. ISTAD was withheld in run 2 after confirmed local Defender quarantine; the Known limitations note below supersedes the earlier open storage-defect wording.

Source/classification: bench/reports/stage-g/defender-evidence.json (event identifiers/timestamps, not benchmark metrics).

### README.md:107

Both runs made 238 TED requests: **10 HTTP 200 / 228 HTTP 202**, with exhausted 3s/8s retries reported honestly. Ten previously not-ready notices also stayed HTTP 202 in both probe rounds after a 30-second wait. TED is currently not serving those sampled XMLs; no complete procurement coverage is claimed. API-returned XML links are used; award identity, date, lot and amount acceptance rules are unchanged.

Source/classification: bench/reports/stage-g/summary.json; noise-band.json; review-verdicts.json; probe-round1.json; probe-round2.json; run1-execution.json; run2-execution.json.

### README.md:109

Run 2 used 9,273 HTTP requests (9.273 including shared requests per company), maximum 40 attributed to one company, and zero deadline hits; wall time 1,988.786 seconds / 198.879 per 100. Run 1 used 9,281 requests, maximum 40, zero deadlines, and 2,136.969 seconds / 213.697 per 100. These are measured live runs, not causal performance claims. Careers coverage is not complete and incomplete checks remain explicit failures. See the [Stage G report](bench/reports/stage-g/REPORT.md) for proof-type counts, source errors and unchanged-code verification.

Source/classification: bench/reports/stage-g/summary.json; noise-band.json; review-verdicts.json; probe-round1.json; probe-round2.json; run1-execution.json; run2-execution.json.

### README.md:113

Stage H established that Windows Defender detected the fetched ISTAD homepage as `Program:Script/Wacapew.A!ml` (threat ID `251869`) and successfully quarantined the correctly written run 2 blob on **2026-11-13 at 20:31:06 IST** (detection at 20:30:02). This is local antivirus remediation on the measuring machine, not an application storage/retention defect; no production blob-pruning or deletion path was found. This was the second observed occurrence involving the same page in the measurement history. Defender later also detected the run 1 copy during diagnostic reads. The records establish quarantine, not whether the detection is a true or false positive.

Source/classification: bench/reports/stage-g/defender-evidence.json (event identifiers/timestamps, not benchmark metrics).

### README.md:115

The final reported measurement is now **[Stage G run 1](bench/reports/stage-g/run1-execution.json)**: **113 websites**, 47 social companies, 2 jobs companies, 1,000 activity companies, 69 articles and 165,481 facts; 9,281 HTTP requests, maximum 40/company, zero deadlines, 2,136.969 seconds. Its published ISTAD result was unaffected at publication; this does not claim its evidence files are immune to later antivirus actions. Run 2 remains fully disclosed with 112 websites and its original timing/counts. This supersedes the earlier advance selection of run 2 because Stage H identified local environmental interference, rather than silently choosing the higher count. No effect on a clean environment is asserted. See [Defender event evidence](bench/reports/stage-g/defender-evidence.json), especially event 1117: Action Quarantine, successful status, error 0x00000000.

Source/classification: bench/reports/stage-g/defender-evidence.json (event identifiers/timestamps, not benchmark metrics).

### README.md:117

### Revision 3 changes

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### README.md:119

The release adds locally bundled Common Crawl candidates and registry shared-identifier counts, bounded deeper ownership pages, strict company-scope filtering, cited contact facts, dated individual-job checks and offline-site improvements. Unknown CLI arguments warn rather than abort; omitted report/profiles/site options receive defaults and effective settings are recorded. The pooled ceiling is 19 HTTP per distinct normalized input (1,900/100), with a hard 40/company maximum including robots, redirects and retries. Lower configured limits remain effective. All time limits are unchanged. Careers runs after primary proof/collection and uses remaining headroom; it has no earmark and does not reduce activity's original allowance. No search-engine integration, paid API or LLM is used. These changes do not claim complete website or careers coverage.

Source/classification: Configuration/algorithmic or external ceiling, not an empirical measurement; documented in bench/reports/stage-d/REPORT.md, stage-e/REPORT.md, s6-step13 and s6-step15 reports as applicable.

### README.md:123

`data/cc_orgnr_index.json.gz` was built 13 November 2026 from partial archived records in CC-MAIN-2026-43,2026-39 and2026-34. It contains 20,832 candidates for 19,735 parent companies. Access/use is subject to [Common Crawl Terms of Use](https://commoncrawl.org/terms-of-use) and third-party rights; see [the bundled terms/method notice](data/CC_INDEX_NOTICE.md). Official Bronnoysund subunit data (NLOD 2.0) maps branch numbers to parents. **Candidate coverage is not verified-site coverage**: every candidate is fetched and re-verified live under the ownership proof and vetoes.

Source/classification: bench/reports/r3-release/REPORT.md (index rebuild dates/counts); data/CC_INDEX_NOTICE.md.

### README.md:125

`src/signalpost/data/nav_index.json.gz` was built 2026-11-13T00:26:42.872674Z from the official public NAV feed using public access (9,296 ads / 5,899 employers). No private credential is required or bundled. The runtime retrieves NAV's published public token in memory, validates the index and live-checks nominated ads; missing, invalid or stale indexes retain the honest full-feed fallback. Source terms and limitations are in [SOURCES.md](docs/SOURCES.md).

Source/classification: bench/reports/r3-release/REPORT.md (index rebuild dates/counts); data/CC_INDEX_NOTICE.md.

### README.md:129

Historical revision 2 results below are retained for comparison, not presented as current coverage.

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### README.md:131

### Revision 2 measured coverage

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### README.md:133

One frozen 1,000-company run of runtime `39a73142` produced **108 verified websites, 44 social companies, 3 jobs companies and 1,000 activity companies**, plus GLEIF facts for 32 companies and TED awards for 6. Registry coverage: identity 1,000, people 997, subunit workplaces 774 and financials 999. Total supported facts: **166,207**. HTTP: **8,589**, mean 8.589/input, maximum 40/company; wall time **1,017.315 seconds**, zero deadlines, 1,000 envelopes/profiles. These are coverage measurements, not an evaluator score or a completeness guarantee. [Final release results and verifier](bench/reports/final-release/RESULTS.md).

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### README.md:135

### Revision 2 precision check

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### README.md:137

The Step 22 new random cohort (100 valid organisation numbers plus three invalid lines) passed the fixed-runtime same-command refresh check: 103 outputs per run, zero company changes, zero observation changes and strict verifier exit 0. [Precision review and exact results](bench/reports/s6-step22/SCOREBOARD.md).

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:5

Requires Python 3.12+, uv and internet access. From a clean checkout, install locked dependencies with `uv sync --frozen`, put organisation numbers in `orgnrs.txt`, then run:

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### SUBMISSION.md:11

No credentials, bulk file, expected count, LLM or search service are required. NAV's published public token is fetched in memory from `https://pam-stilling-feed.nav.no/api/publicToken`; no personal credential is required or persisted. Provider cost is **$0**; local compute, disk and network are excluded.

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### SUBMISSION.md:29

| BRREG | Identity, registered roles, subunits and returned financial years | NLOD 2.0; attribute Brønnøysundregistrene | $0 |

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### SUBMISSION.md:30

| NAV public feed | Active individual ads, exact employer/subunit matching; public token obtained at runtime | NAV public-feed reuse terms; no personal credential | $0 |

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### SUBMISSION.md:31

| Wikidata | Supplementary exact-orgnr website/social nominations | CC0, item provenance retained | $0 |

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### SUBMISSION.md:32

| Company websites | Ownership proof, descriptions, social links, dated news, linked active jobs | robots.txt and site access rules; no blanket open licence inferred | $0 |

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### SUBMISSION.md:33

| SSB KLASS | Bundled industry descriptions | CC BY 4.0 | $0 |

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### SUBMISSION.md:34

| LLM / search engines | No integration; deterministic cited templates | No provider called | $0 |

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### SUBMISSION.md:35

| GLEIF | LEI/status/form/dates and explicit direct/ultimate parents | CC0 1.0; anonymous exact orgnr + RA000472 API, batched parent LEIs | $0 |

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### SUBMISSION.md:36

| TED | Exact winner/buyer public procurement awards | EU Publications Office legal notice/Commission reuse policy; anonymous published-notice API and public XML | $0 |

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### SUBMISSION.md:46

The bundled `data/shared_identifiers.json.gz` counts registered phone/mobile numbers, email domains and distinctive legal-name keys from the official Bronnoysundregistrene entity bulk CSV. Attribution: Bronnoysundregistrene, [NLOD 2.0](https://data.norge.no/nlod/en/2.0). It is read locally, without a runtime registry bulk download. Build hashes and counts are in `data/shared_identifiers_build.json`; the complete gzip is 8,676,502 bytes, above the 3 MB target. Missing keys do not establish uniqueness.

Source/classification: bench/reports/r3-benchmark/SCOREBOARD.md (gzip size); 3 MB is the historical requested target, not a measurement.

### SUBMISSION.md:48

Additional website proof can use the exact registered email visible in text or mailto links only when its non-free-mail domain is registered to exactly one entity; or a registered phone/mobile visible on the page when fewer than five entities register it. Both require a positive count in the snapshot and a nonempty non-placeholder page. The exact legal name, including its legal form, must also identify the publisher in the title, heading or footer; a staff/adviser contact alone is not ownership proof. Name-only masthead and unique-name-domain publication were removed after the R3 precision review exposed namesake and placeholder risks. Existing stronger proofs keep their labels. None of these rules overrides an existing rejection or owner conflict.

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### SUBMISSION.md:56

`data/cc_orgnr_index.json.gz` was built 13 November 2026 from partial archived records in CC-MAIN-2026-43,2026-39 and2026-34. It contains 20,832 candidates for 19,735 parent companies. Access/use is subject to [Common Crawl Terms of Use](https://commoncrawl.org/terms-of-use) and third-party rights; see [the bundled terms/method notice](data/CC_INDEX_NOTICE.md). Official Bronnoysund subunit data (NLOD 2.0) maps branch numbers to parents. **Candidate coverage is not verified-site coverage**: every candidate is fetched and re-verified live under the ownership proof and vetoes.

Source/classification: bench/reports/r3-release/REPORT.md (index rebuild dates/counts); data/CC_INDEX_NOTICE.md.

### SUBMISSION.md:58

`src/signalpost/data/nav_index.json.gz` was built 2026-11-13T00:26:42.872674Z from the official public NAV feed using public access (9,296 ads / 5,899 employers). No private credential is required or bundled. The runtime retrieves NAV's published public token in memory, validates the index and live-checks nominated ads; missing, invalid or stale indexes retain the honest full-feed fallback. Source terms and limitations are in [SOURCES.md](docs/SOURCES.md).

Source/classification: bench/reports/r3-release/REPORT.md (index rebuild dates/counts); data/CC_INDEX_NOTICE.md.

### SUBMISSION.md:62

The pooled HTTP hard cap is 19 per distinct normalized input: 1,900 per 100, with at most 40 attributed to any company and shared calls included globally. The hard time cap is 24 seconds per distinct input (40 minutes per 100), with the default 2,400-second run limit and lower configured limits honored. These are tighter than 2,000 HTTP / 45 minutes per 100. Crawl finalization reserves preserve one output per input even when discovery is incomplete. Public DNS fallbacks are bounded and tolerate blocked UDP; end-of-run retries consume the original pool.

Source/classification: Configuration/algorithmic or external ceiling, not an empirical measurement; documented in bench/reports/stage-d/REPORT.md, stage-e/REPORT.md, s6-step13 and s6-step15 reports as applicable.

### SUBMISSION.md:64

### Revision 3 changes

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### SUBMISSION.md:66

The release adds locally bundled Common Crawl candidates and registry shared-identifier counts, bounded deeper ownership pages, strict company-scope filtering, cited contact facts, dated individual-job checks and offline-site improvements. Unknown CLI arguments warn rather than abort; omitted report/profiles/site options receive defaults and effective settings are recorded. The pooled ceiling is 19 HTTP per distinct normalized input (1,900/100), with a hard 40/company maximum including robots, redirects and retries. Lower configured limits remain effective. All time limits are unchanged. Careers runs after primary proof/collection and uses remaining headroom; it has no earmark and does not reduce activity's original allowance. No search-engine integration, paid API or LLM is used. These changes do not claim complete website or careers coverage.

Source/classification: Configuration/algorithmic or external ceiling, not an empirical measurement; documented in bench/reports/stage-d/REPORT.md, stage-e/REPORT.md, s6-step13 and s6-step15 reports as applicable.

### SUBMISSION.md:70

Final measurement is **Stage G run 1**, selected after Stage H confirmed local antivirus interference in run 2, on the frozen 1,000-company cohort. It published 113 websites, 47 social companies, 2 jobs companies, 1,000 activity companies, 7 news companies / 69 articles, 32 GLEIF companies and 0 TED awards; 165,481 facts. Run 2 published 112 websites; other listed coverage and fact counts were identical. The observed website range is **112-113**, article range **69-69**. These two observations are not a confidence interval. Full per-metric band and every website/article membership difference are in [Stage G NOISE.md](bench/reports/stage-g/NOISE.md).

Source/classification: bench/reports/stage-g/summary.json; noise-band.json; review-verdicts.json; probe-round1.json; probe-round2.json; run1-execution.json; run2-execution.json.

### SUBMISSION.md:72

Every new website versus Stage E was reviewed in both runs: ENSURE IT AS, exact organisation number 934620011 on the saved page; 2 correct / 0 wrong / 0 doubtful. Neither run published a TED award, so no Stage G awards required review. This is an incremental review, not an exhaustive new precision estimate of all facts. ISTAD was withheld in run 2 after confirmed local Defender quarantine; the Known limitations note below supersedes the earlier open storage-defect wording.

Source/classification: bench/reports/stage-g/defender-evidence.json (event identifiers/timestamps, not benchmark metrics).

### SUBMISSION.md:74

Both runs made 238 TED requests: **10 HTTP 200 / 228 HTTP 202**, with exhausted 3s/8s retries reported honestly. Ten previously not-ready notices also stayed HTTP 202 in both probe rounds after a 30-second wait. TED is currently not serving those sampled XMLs; no complete procurement coverage is claimed. API-returned XML links are used; award identity, date, lot and amount acceptance rules are unchanged.

Source/classification: bench/reports/stage-g/summary.json; noise-band.json; review-verdicts.json; probe-round1.json; probe-round2.json; run1-execution.json; run2-execution.json.

### SUBMISSION.md:76

Run 2 used 9,273 HTTP requests (9.273 including shared requests per company), maximum 40 attributed to one company, and zero deadline hits; wall time 1,988.786 seconds / 198.879 per 100. Run 1 used 9,281 requests, maximum 40, zero deadlines, and 2,136.969 seconds / 213.697 per 100. These are measured live runs, not causal performance claims. Careers coverage is not complete and incomplete checks remain explicit failures. See the [Stage G report](bench/reports/stage-g/REPORT.md) for proof-type counts, source errors and unchanged-code verification.

Source/classification: bench/reports/stage-g/summary.json; noise-band.json; review-verdicts.json; probe-round1.json; probe-round2.json; run1-execution.json; run2-execution.json.

### SUBMISSION.md:84

Stage H established that Windows Defender detected the fetched ISTAD homepage as `Program:Script/Wacapew.A!ml` (threat ID `251869`) and successfully quarantined the correctly written run 2 blob on **2026-11-13 at 20:31:06 IST** (detection at 20:30:02). This is local antivirus remediation on the measuring machine, not an application storage/retention defect; no production blob-pruning or deletion path was found. This was the second observed occurrence involving the same page in the measurement history. Defender later also detected the run 1 copy during diagnostic reads. The records establish quarantine, not whether the detection is a true or false positive.

Source/classification: bench/reports/stage-g/defender-evidence.json (event identifiers/timestamps, not benchmark metrics).

### SUBMISSION.md:86

The final reported measurement is now **[Stage G run 1](bench/reports/stage-g/run1-execution.json)**: **113 websites**, 47 social companies, 2 jobs companies, 1,000 activity companies, 69 articles and 165,481 facts; 9,281 HTTP requests, maximum 40/company, zero deadlines, 2,136.969 seconds. Its published ISTAD result was unaffected at publication; this does not claim its evidence files are immune to later antivirus actions. Run 2 remains fully disclosed with 112 websites and its original timing/counts. This supersedes the earlier advance selection of run 2 because Stage H identified local environmental interference, rather than silently choosing the higher count. No effect on a clean environment is asserted. See [Defender event evidence](bench/reports/stage-g/defender-evidence.json), especially event 1117: Action Quarantine, successful status, error 0x00000000.

Source/classification: bench/reports/stage-g/defender-evidence.json (event identifiers/timestamps, not benchmark metrics).

### SUBMISSION.md:90

[Verify Signalpost](.github/workflows/ci.yml) runs locked installation, the full pytest suite and live-20. Its `--require-clean` verifier remains strict for identity, roles, accounts and subunits. Only optional website/social, hiring and activity failures/stale states are tolerated and summarized with reasons; schema, membership, evidence, citations and global operational checks remain strict. Local release execution is documented in the release report; no GitHub workflow was dispatched and nothing was pushed.

Source/classification: Non-measurement identifier/version/command/section reference (Python 3.12, licence versions, CC0, RA000472, API URL, step/revision labels, $0 provider policy, or documented algorithmic limit); not claimed as an empirical benchmark result.

### SUBMISSION.md:92

Current revision 3 validation: **1,400 tests passed, zero failed**; both frozen runs recorded zero deadline hits. The Stage E fresh-clone refresh pair recorded zero company and observation changes with strict verifier PASS. See [Stage G validation](bench/reports/stage-g/REPORT.md) and [Stage E refresh verification](bench/reports/stage-e/refresh/strict-verifier.txt).

Source/classification: bench/reports/stage-g/pytest.txt; bench/reports/stage-e/refresh/strict-verifier.txt.

### SUBMISSION.md:96

The following records describe revision 2 or superseded operational notes. Their values and links are preserved for historical comparison; they are not the current revision 3 measurement.

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:98

### Revision 2 frozen 1,000-company measurement

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:100

Measured the unchanged runtime `39a7314299c181187ee1f07af7fa75eaa631ad9c` once on 7 November 2026: run `20261107T094159020873Z-39a7314`. This frozen benchmark is separate from the fresh random precision sample below.

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:104

| Identity | 1,000 |

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:105

| People | 997 |

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:106

| Subunit/workplace section | 774 |

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:107

| Financials | 999 |

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:108

| Verified websites | 108 |

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:109

| Social companies | 44 |

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:110

| Jobs companies | 3 |

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:111

| Activity companies | 1,000 |

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:112

| GLEIF companies | 32 |

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:113

| TED award companies | 6 |

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:114

| Supported facts | 166,207 |

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:115

| HTTP total / mean per input / max per company | 8,589 / 8.589 / 40 |

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:116

| Wall seconds | 1,017.315 |

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:117

| Deadlines | 0 |

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:118

| Envelopes / profiles | 1,000 / 1,000 |

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:120

Site generation passed without warnings. Counts are measured coverage, not an evaluator score or a claim that every source succeeded. One financial section and four optional hiring sections failed. Websites are 108 rather than the saved Step20 projection's110: ISTAD ART SOLUTION NORWAY NUF is ambiguous after the final ownership recheck; Bergen Vaktmestertjenester's current privacy page fails the exact-company ownership check. These are proof/withholding outcomes, not claimed DNS noise or code changes. [Final results, diagnostics and independent verification](bench/reports/final-release/RESULTS.md).

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:122

### Revision 2 fresh random 100-company precision check

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:124

Step 22 selected a NEW random sample of 100 valid identifiers outside all known inputs/reports/cohorts, plus three invalid lines. The fixed runtime's literal README command twice emitted **103 envelopes/profiles per run**, **336.360 seconds / 788 HTTP**, then **175.704 seconds / 753 HTTP**. **Zero company changes, zero observation changes, unmodified strict verifier exit 0**; zero unverified values. Final sample coverage: 100 identity, 96 people, 72 subunit workplaces, 42 accounts, 6 websites, 4 social companies, 2 jobs, 100 activity companies, 1 GLEIF company and no TED awards; 8,974 supported facts.

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:126

Every website/social/job/GLEIF item, 50 random registry facts and ten briefings were reviewed. A full-footer publisher-name correction rejects a different entity whose name merely contains the subject brand; the existing exact-orgnr spelling normalization is retained. Unrelated companies' calibration excerpts were removed from financial claim citations without changing amounts, periods or claim IDs. The saved frozen-1000 replay kept all 110 websites and all financial values/IDs; verification passed with zero unverified values. The original doubtful .no page was withheld; the replacement .com publisher was checked against the NUF's explicit registered head enterprise. No company-specific exception. [Full precision report](bench/reports/s6-step22/SCOREBOARD.md).

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:128

### Revision 2 verification record

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:130

The final release executes the exact local workflow commands on the final runtime; the full results and logs are in [final release validation](bench/reports/final-release/RESULTS.md). The Step 22 fixed-runtime fresh pair is separate from the final frozen benchmark. No GitHub workflow was dispatched and nothing was pushed.

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:134

Final exact local CI: **1,244 tests passed; live-20 scoped verifier passed**, with zero failed/stale sections and zero unverified values. Independent frozen-1000 verification also passed with zero unverified values. No runtime changes in release prep.

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

### SUBMISSION.md:138

Operational ceilings are unchanged: at most 40 attributed HTTP requests per company, and a pooled ceiling of 18 requests per distinct normalized input (360 for 20 companies). Lower configured limits still apply. These additions contain no search-engine, directory, Norid or model-provider requests. There is no search-engine integration.

Source/classification: bench/reports/final-release/RESULTS.md; bench/reports/s6-step22/SCOREBOARD.md; bench/reports/rules-audit/README.md (superseded caps).

