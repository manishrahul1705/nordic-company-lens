# Stage V: seven-section company brief

Branch `stage-v-brief-sections`, from `revision-4` (701afaa). Synthesis generator version 9.

## What changed

The brief now has seven sections: `what_it_does`, `scale`, `leadership`, `changes`, then the new `reach`, `standing` and `not_established`. Code is in `src/signalpost/synthesis/sections_extra.py` and `cohort.py`, plus models, validator, runner and `scripts/verify_output.py`. Tests: `tests/test_brief_sections_v.py`.

- **reach**: the registered business address; each registered workplace that has an address, with its municipality (up to 5 listed); a count of municipalities when there are several workplaces; and registered roles this company holds at *other companies in the same run*. Those roles are cited through a verbatim copy of the other company's published role claim.
- **standing**: operating revenue (`accounts.revenue`, i.e. `sumDriftsinntekter`) compared with other companies in the run that have the same two-digit NACE division, fiscal year, account type and currency.
  - Percentile = ⌊100 × (below + ½·equal) / N⌋, and the group size N is always stated.
  - With N < 10 the sentence says the comparison is too thin and gives no percentile.
  - With no revenue, or an unspecified or missing NACE code, it says why it isn't compared.
  - Sentences say "registered under NACE division NN"; no NACE code is asserted as activity.
- **not_established**: each gap cites the published *non-available* claim the run recorded for it (for example `website.section`, `hiring.section`, `subunits.units`, `identity.employees`, `accounts.revenue`). Reason wording comes from recorded run state, through the existing `section_reason` / `website_reason` functions and error codes. Items covered:
  - no website proof;
  - a published site recorded as a shared group site;
  - a declared homepage rejected as a shared or group site, with the recorded candidate code;
  - a source that returned nothing;
  - a fetch that failed;
  - employees, NACE code, business address, operating revenue and registered homepage not on record.
- **Change to two original sections:** where `leadership` or `scale` would otherwise be empty, they now carry cited absence wording (the same frame) or the registered roles with their registry role titles. On the frozen 1,000 this applied to 5 `leadership` sections and 1 `scale` section.
- **Validation.**
  - New sections are validated by exact recomputation, and every citation must resolve to a claim of this company or a cohort copy.
  - Absence sentences in the original sections must equal the fixed wording for the cited non-available claim.
  - `verify_output.py` rebuilds the cohort records from every output row and requires them to be equal. A cherry-picked or altered comparable set therefore fails.

## Frozen 1,000 (live, 2026-11-17)

Exit 0, 1,000 envelopes, 0 warnings, 0 deadline hits, 9,353 HTTP requests.

**Strict verifier: PASS** (`strict-verifier.txt`): 165,993 published claims, 4,123 source blobs, 0 unverified values.

| Section | Filled / 1,000 | Empty | Sentences |
|---|---:|---:|---:|
| what_it_does | 1,000 | 0 | 3,646 |
| scale | 1,000 | 0 | 1,256 |
| leadership | 1,000 | 0 | 2,091 |
| changes | 1,000 | 0 | 2,230 |
| reach | 1,000 | 0 | 1,818 |
| standing | 1,000 | 0 | 1,000 |
| not_established | 1,000 | 0 | 3,652 |

- **Citations:** 0 unresolved, across all seven sections.
- **Standing:** 583 percentiles, 154 too thin, 263 not compared (209 with no operating revenue figure in the filed accounts, 50 with an unspecified NACE code, 3 with no NACE code, 1 with failed accounts).

**No new HTTP requests.** Synthesis runs after the last request, and `resynthesize.py` regenerated all 1,000 briefs from saved envelopes with sockets disabled. Registry requests are identical to the same-day revision-4 control of 2026-11-16 (4,028 `data.brreg.no`). Total requests differ (9,353 vs 9,504) only through live TED retries on HTTP 202 and website variation (`measurement.json`).

## Hand review of 15 briefs (`review-briefs.json`)

Each was checked against its envelope. Percentiles and thin counts were recomputed independently from the raw rows, and both role holdings were checked against the holding companies' role claims (REGN, entity 939725709).

**15 correct, 0 wrong.** Wording issues for your review:

1. Most companies' only registered workplace is the company itself at its business address, so `reach` repeats the address on two lines.
2. When no business address is registered, "Business address: none registered." appears in both `reach` (its fallback) and `not_established`.
3. Website wording can overlap: a withheld site and the rejected declared homepage name the same domain (981508734).
4. "0 other companies … (fewer than 10)" reads awkwardly when the group is empty (995541432).
5. Standing compares only within this run's cohort. Its percentile describes position among the run's companies, not the national population.

Full suite: **1,457 passed, 0 failed** (`pytest.txt`).
