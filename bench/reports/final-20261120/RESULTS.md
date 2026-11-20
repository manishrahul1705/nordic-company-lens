# Stage AP: final combined exclusive live run — 20 November 2026

The live run completed successfully and the offline site was built. Strict verification, the 200-claim accuracy threshold and attribution adjudication pass. **This is not an all-green validation result: TED published zero awards under HTTP 202 conditions, and the full suite has two retained failures.** No production code, proof rule, verifier or existing test was changed for this measurement. No push.

## First: Stage AS result

Source HEAD: **cede54701d5e50067764f472009b6c830254065a**, branch audit-fixes. [Stage AS report](../stage-as-approvals-related-20261120/RESULTS.md): full1000 cleaning status 6 companies / 6 claims (five approved, one not approved), workshops 1 / 2, related-company websites 14 / 16. Stage AS added nine tests: 1,843 → 1,852; 1,851 passed and one documented footer timing failure, followed by two isolated passes. All three Stage AS types are nonzero in this final live run.

## Exclusive pre-flight and exact command

The signal-nethra session was explicitly paused by the user. Process inventory immediately before launch found no other Python processes. Only this CLI and its interpreter child ran during the measured live run; periodic checks found no signal-nethra Python work. Tests, extract creation and audits began only after CLI exit. This is process observation, not a claim that Windows background services stopped.

HEAD matched cede547. Tracked tree was clean; the only remaining untracked entries were pytest temporary directories. Uncommitted Stage AR/AT measurement reports were preserved under ignored bench/cache/pre-final-20261120 before launch. C: had **12.599 GB free**, above 8 GB. The final output directory did not exist and no state/prior run/cache was supplied. See [preflight.json](preflight.json) and [execution.json](execution.json).

```
.venv/Scripts/python -u -m signalpost.cli run --organisations bench/inputs/1000-r3/batch.jsonl --output bench/runs/final-20261120/envelopes.jsonl --report bench/runs/final-20261120/report.json --state-dir bench/runs/final-20261120/state --site-dir bench/runs/final-20261120/site
```

Only input/output paths are selected. Worker concurrency **64**, host concurrency **10**, run budget **3,600s**, output cap **4,096 MiB**, source flags and proof options retain CLI defaults. Site ON; no supplied bulk, previous state, weak registry-declared proof mode or Stage AT host-list nominations. Fresh state is distinct from the intentionally shipped bundled snapshots.

## Run result

Run id `50ebdada01af423f8ba07f912c9b9d73`; CLI exit **0**; run_status **completed**; success_rate **100%**; **1000 succeeded / 0 failed**; 1,000 terminal envelopes. **11,653 / 19,000 HTTP** (61.33%); maximum **40 per company**; **0 deadline hits**, **0 handled / 0 unhandled exceptions**, no warnings.

Success rate describes successful terminal company results. It does not imply all optional sources returned data: **868 companies have no source-error flags**. Recorded source errors: accounts 1, hiring 4, website 127, identity/roles/subunits/activity 0; overlapping companies and ordinary unavailable sources are not additional failed input rows. TED diagnostics are reported separately below.

| Stage | Seconds |
|---|---:|
| Crawl / collection | 1,075.200 |
| Finalisation and required outputs | 137.730 |
| Offline site build | 378.860 |
| Other process/report overhead | 11.087 |
| End-to-end process wall | 1,602.877 |

The separately reported `runtime_ms` is 1,208,875; the stage markers and external process stopwatch above distinguish crawl from complete wall time. The site is **available**, with **4,885 pages** covering **1,000 companies**, 2,882 evidence pages and 828,067,821 bytes.

The terminal reserve was 30s outputs + 600s site = 630s. Outputs actually took 137.73s, so that component estimate remains low; site took 378.86s and the combined 516.59s stayed within the combined reserve. This report records the estimate discrepancy; it does not change budget.py.

## Every requested family from this one run

Counts are available published claims from the final run's population extract, not substituted from earlier stages. Rows are information views and can overlap: identity/accounts/roles include their named subsets. Do not sum this table as a mutually exclusive total. [measure_extract.py](measure_extract.py) reproduces it from the committed extract with no bench/runs.

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

Approval snapshots combined: **7 companies / 8 status-or-approval records**, comprising five positively approved cleaning companies, one not-approved cleaning company, and one workshop company with two approval numbers. Positive approvals alone are 6 companies / 7 claims. Related-company websites remain registry-declared, not ownership-verified; they do not borrow group social/brand/news content.

Previous names are **241 companies / 324 own-company historical-name claims**. Stage AK's broader 302 / 701 count includes registered-subunit names. This run reproduces that broader total exactly: 302 / 701, of which subunit histories are 210 / 377. These are separate scopes, not a collapse in previous-name extraction. Hiring's three employer matches use registered subunit orgnrs, with parent relationships retained. Wikidata reports 13 matched companies, five requests and zero acquisition errors; its social-derived claims are also included in the Social view.

### Zero-family flag: TED

**TED is the only requested family at zero that was nonzero in its own earlier live-stage report** ([prior combined run](../overnight-all-20261120/RESULTS.md): six companies / twenty awards). Acquisition did run and nominated **79 notices**. There were **25 TED HTTP calls: ten HTTP 200 Search responses and fifteen HTTP 202 XML responses**. The XML calls represent five notices exhausting three attempts each. Three consecutive exhausted notices opened the breaker; two later re-probes also failed with 202. **74 remaining notices were skipped with ted_202_circuit_open**. The XML phase took 38.765s. It did not return any verified award XML.

This is recorded upstream not-ready/HTTP 202 plus the configured breaker, not a global crawl deadline, absent bundled data or a disabled source. No skipped notice is evidence of no awards. The high company success rate must not obscure the lost procurement-family recall. No attempt is made to replace these zeros with earlier-stage awards, rerun the cohort until TED looks healthy, or change the source during this measurement.

## Projection at 1,100 inputs

Linear 1.1x projection: **1,763.164s wall vs 3,600s**, leaving **1,836.836s**; **about 12,819 HTTP vs 20,900**, leaving about 8,081. The request ratio is 61.33% of the pool at either size. No cap is raised.

This is a conditional estimate from one observed run, not a tail-latency guarantee. It includes this run's TED unavailability/breaker behaviour; the fully healthy TED workload was not measured in this combined run. Provider retries, DNS/robots variation, source payloads and the next 100 companies can change both dimensions.

## Checks

- **Strict verifier PASS** on this final run: 1,000 schema-valid envelopes, 178,669 published claims, 5,993 verified source blobs, 2,552 synthesis sentences, **zero unverified synthesis values**, exact frozen-cohort membership/order. [Output](strict-verifier.txt).
- **Accuracy PASS:** 200 published claims, fixed seed 20261119, stratified Stage X allocation/draw and unchanged mechanical/Wilson checks. **200 correct / 0 wrong / 0 doubtful; Wilson 95% lower bound 98.12%**, above 95%. 156 exact mechanical matches, 44 source-reviewed transformations/claims. Synthesis is excluded from the claim-sampling population per this request, and independently strictly verified. That scope choice is explicit in [script provenance](accuracy/script-provenance.json), not an acceptance-rule change.
- **Attribution PASS after documented adjudication:** original raw Stage X audit has zero dangling references, registry mismatches, foreign-number flags and cross-company content-hash reuse. It reports **four reused official bulk URLs**, preserved in attribution.json. Independent SHA-256-checked row verification resolves all **791** source records: 787 direct exact recipients and four explicitly labelled registered-recipient-subunit cases. Actual cross-company contamination **0**. The raw audit host list/checks were not relaxed. See [adjudication](accuracy/bulk-adjudication.json).
- **Extract-only reproduction PASS:** copied report artifacts, no bench/runs directory, with all bench/runs file opens forbidden. Sample, population, source-derived hand-review context, verdicts, raw attribution counts and adjudication all reproduce. [Output](extract-only-reproduction.txt); [commands](accuracy/REPRODUCE.md).
- **Full suite is not clean:** **1,850 passed / 2 failed**, 1,852 total, 609.38s. No tests or production rules were changed. [Complete output](pytest.txt).

### Every test failure

1. `tests/test_evaluator_cli_and_site.py::test_evaluator_shapes_union_contract_reference`: contract shape passed; reference shape failed verify_output.py's “Incomplete smoke-test section” check. BRREG oppdateringer/enheter had a **ConnectTimeout**, producing `activity: failed`, error `timeout`, for all twenty CI fixture companies (first 980597784). The test disables websites/hiring/public activity but keeps live registry changes. Its subunit update request returned 200. This is the documented live-network evaluator test, not a synthesis/first-observation validation failure. Full company/source diagnostics are in [test-failure-diagnostics.json](test-failure-diagnostics.json).
2. `tests/test_footer_ownership.py::test_independent_footer_runs_dependent_production_extraction`: `KeyError: official_website`; its saved envelope records a website `deadline`. This previously documented timing flake subsequently **passed twice in isolation**, 19.99s and 17.59s. Those passes do not erase the failed full-suite observation. [First](footer-isolation-1.txt), [second](footer-isolation-2.txt).

The final 1,000-company run itself has no activity source-error flags, deadline hits or exceptions. That does not turn the two test failures into passes.

## Committed measurement scope

Only this report, scripts/data needed for reproduction, selected source evidence extract, test outputs and the two narrow sample/verdict JSONL ignore exceptions are committed. No full bench/runs, raw bulk downloads, generated site, pytest temporary directories, Stage AR/AT pilot or production-code change is included. The measured source commit remains cede547; the new commit records measurement artifacts only. Do not push.
