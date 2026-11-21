# Stage BA final combined verification

## Pre-flight and run

Frozen source HEAD: `2d7b3cb343a5927fef47352e9226a9fc95e5864f` (`audit-fixes`). The tracked tree was clean, no `signal-nethra` Python process was running, and C: had about **16.0 GB decimal (14.95 GiB) free**, above the 10 GB threshold. The unseen audit input was `C:\Users\Manish\Downloads\jury-audit\orgnrs.txt`; the frozen 1,000 input SHA-256 is recorded in [measurement.json](measurement.json).

The exact standard-default command was:

```powershell
.\.venv\Scripts\python.exe -u -m signalpost.cli run --organisations bench/inputs/1000-r3/batch.jsonl --output bench/runs/final-ba/envelopes.jsonl --report bench/runs/final-ba/report.json --state-dir bench/runs/final-ba/state --site-dir bench/runs/final-ba/site
```

Fresh state, default config, and site publishing were enabled. The process used no supplied state or prior run. At the end of the run, more than 10 GB remained free.

## Final 1,000 results

| Measure | Result |
|---|---:|
| `run_status` / `success_rate` | `completed` / 1.0 |
| Companies | 1,000 succeeded / 0 failed |
| Crawl (`finalisation.crawl_seconds`) | 1,038.14 s |
| End to end (`end_to_end_runtime_ms`, including site build) | 1,520,578 ms / 1,520.578 s |
| Internal `runtime_ms` | 1,214,625 ms |
| Output finalisation / site build | 177.89 s / 292.66 s |
| HTTP requests / pooled cap | 11,562 / 19,000 (60.85%) |
| Maximum HTTP per company | 40 |
| Deadline hits | 0 |
| Handled / unhandled exceptions | 0 / 0 |
| Warnings / HTTP 429 | none / 1 |

`envelopes.jsonl` is **496,624,523 bytes**, 11.56% of the default **4,294,967,296-byte (4,096 MiB) envelope cap**; `output_limit_exceeded` is false. The site reports **1,032,289,235 bytes**, 5,617 pages and 1,000 company profiles. The envelope cap applies to the envelope output; site bytes are reported separately. Together, envelope and reported site bytes are 1,528,913,758 bytes.

Compared with Stage AP’s 178,669 claims, BA emitted **236,654 claims, an increase of 57,985**. Envelope bytes rose by 91,026,414 (from 405,598,109), and reported site bytes rose by 204,221,414 (from 828,067,821).

### Full family table

Published claims are counted by information view. Views overlap; rows must not be summed. **No family is zero.** TED, AP’s sole zero family, returned 2 companies / 4 claims in BA despite HTTP 202 responses and the configured circuit breaker.

| Family / information type | Companies | Claims |
|---|---:|---:|
| Identity | 1,000 | 48,334 |
| Roles | 997 | 43,250 |
| Accounts | 999 | 105,867 |
| Audit status, per year/scope | 999 | 2,817 |
| Registry-date activity | 997 | 7,714 |
| Previous legal names of subject company | 241 | 324 |
| Historical names including subunits | 302 | 701 |
| Subunit historical names | 210 | 377 |
| Subunits | 773 | 17,664 |
| Group structure | 75 | 119 |
| Signatur | 765 | 765 |
| Prokura | 201 | 201 |
| Registry changes | 1,000 | 12,052 |
| GLEIF | 142 | 736 |
| TED procurement awards | 2 | 4 |
| Wikidata | 13 | 47 |
| Verified official websites | 115 | 115 |
| Public brands | 36 | 36 |
| Social profiles | 62 | 126 |
| News / dated company items | 32 | 115 |
| Hiring | 3 | 3 |
| Research projects | 9 | 17 |
| State aid | 98 | 679 |
| SkatteFUNN | 36 | 89 |
| DiBK central approvals | 14 | 69 |
| Cleaning register | 6 | 6 |
| Workshop approvals | 1 | 2 |
| Related-company declared websites | 14 | 16 |

The broader historical-name view is 302 companies / 701 claims, including 210 / 377 subunit historical names. The separate subject-company previous-name view is 241 / 324.

### 1,100 projection

A linear 1.1x projection gives **1,672.636 s end-to-end** against the 3,600 s default budget, with about 1,927 s headroom, and **12,719 HTTP** (12,718.2 exact) against a 20,900 pooled cap. This is an estimate from one run, not a tail-latency guarantee.

## Unseen-300 batch and precision

The fresh run used the supplied 316-line jury input and retained default duplicate envelopes. It completed with 316 output lines, 310 successful valid companies, **3 invalid inputs**, and 3,174 HTTP requests. The site contains **310 profiles** and skipped all three invalid identifiers. Strict verification found 45,606 claims, 1,285 source blobs and 735 synthesis sentences, with zero unverified synthesis values. See [jury strict-verifier output](jury-strict-verifier.txt).

A separate offline precision sample used the jury audit’s 300 active companies, family stratification and seed 7. **100 correct / 0 wrong; observed precision 100%.** 80 passed exact locator/span/subject-URL checks; the other 20 were checked against their saved source records. **Uniktur has no `public_brand` claim** in the new output. Sample, verdicts, context, source bytes and hash manifest are in [jury-precision](jury-precision/REVIEW.md).

## Final-1,000 verification

- Strict verifier initially passed: **1,000 schema-valid envelopes, 236,654 claims, 6,002 source blobs verified, 2,560 synthesis sentences, zero unverified synthesis values**, exact frozen-cohort membership/order. The mixed jury run initially passed too: 316 lines, 45,606 claims, 1,285 source blobs and 735 synthesis sentences, zero unverified synthesis values. A later repeat attempt could not read one state blob (`107cc604?e40410f6`); the OS returned `OSError(22)` and the path subsequently disappeared. The cause was not established. The initial verification predates the disappearance; see [verifier log](strict-verifier.txt).
- Stage X accuracy: **200/200 correct, 0 wrong, 0 doubtful**; 165 mechanical checks and 35 source-reviewed claims; Wilson 95% lower bound **98.12%**. The self-contained sample and cited source bytes are in [accuracy](accuracy/REPRODUCE.md).
- Attribution: four raw official bulk-URL reuse flags; 791 source-row checks, including four explicitly scoped registered-subunit records; **zero subject mismatches and zero cross-company contamination**. Details: [raw attribution audit](accuracy/attribution.json) and [bulk adjudication](accuracy/bulk-adjudication.json).
- Extract-only reproduction passed with all `bench/runs` opens forbidden. The Stage X sample, hand review, raw attribution checks and bulk-row adjudication reproduced; see [extract-only result](extract-only-reproduction.txt).
- Full suite: **1,857 passed, 0 failed** in 427.76 s. One pytest cache warning noted that the sandbox denied writing `.pytest_cache/v/cache/nodeids`; it did not affect test outcomes. See [test summary](pytest-summary.txt).

The product code remained frozen at AY throughout these measurements. This report records the full run and the self-sufficient accuracy materials; no push was made.
