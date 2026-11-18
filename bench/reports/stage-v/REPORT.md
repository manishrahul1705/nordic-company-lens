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

Full suite (first run): 1,457 passed, 0 failed. After the revision: see below.

## Revision: site rendering, explicit standing basis, repetitions (2026-11-18)

Earlier figures in this report are from the first Stage V run (`bench/runs/stage-v`). The figures below are from the rerun (`bench/runs/stage-v2`), which supersedes them; `measurement.json` and `strict-verifier.txt` now hold the rerun.

**1. Site.** Each company page renders all seven sections (`site.brief_sections_html`) under "Company brief": What it does, How big it is, Who runs it, What changed, Where it operates, How it compares, What we could not establish. Same text, same citations, same order as the output.
- Available claims link to their fact; changes link to the change; a role held at another company links to that company's page; a gap opens the recorded state ("[why]": field and availability, plus claim ID).
- The block is `data-verbatim`, so the site's date reformatting never alters it.
- `site-text-check.json`: on all 1,000 rebuilt pages every sentence of all seven sections appears byte-exact, in output order.
- The site was rebuilt from the run's envelopes with `signalpost site` after the `data-verbatim` fix; synthesis output was unchanged.

**2. Standing wording** now always states the basis: other companies *in this run*, the NACE division and the fiscal year.
- Percentile: "Among the 37 other companies in this run in NACE division 47 with FY2025 accounts, its FY2025 operating revenue of NOK 1,818,468 is higher than 24% of them." The percentage is now the share with strictly lower revenue, rounded down, so it matches "higher than" literally.
- Thin: "Only 8 other companies in this run are in NACE division 85 with FY2025 accounts, fewer than the 10 needed for a comparison, so its FY2025 operating revenue of NOK 7,943,829 is not ranked."
- No comparable company: "No other company in this run is in NACE division 20 with FY2025 accounts, so its FY2025 operating revenue of NOK 2,172,557,410 is not compared."
- Not compared: "Not compared with other companies in this run: the filed annual accounts state no operating revenue figure." Similar wording covers an unspecified or missing NACE code and failed accounts.

**3. Repetitions cleared** (`repetition-check.json`):
- `reach` no longer lists the sole workplace when it is at the business address: 0 cases. One remaining flag is a false positive: business address "6657 Rindal" against a workplace at "Rindal, 6657 Rindal".
- A missing business address is stated only in `not_established`: 6 companies, 0 elsewhere.
- "No separately registered workplaces" moved to `reach`, where it answers "where it operates".
- A domain is named once in the website gap: the declared-homepage line is dropped when the website reason already names that domain. 0 domains named twice.

**National comparison:** every standing sentence names "in this run". 0 sentences in any section use national, country-wide, all-companies or "percentile" wording outside verbatim website quotes.

### Rerun (frozen 1,000, 2026-11-18)

- Exit 0, 1,000 envelopes, 8,896 HTTP requests, 0 warnings.
- **1 deadline hit:** 997790952's activity fetch, during the crawl. That company's activity section is still available, and synthesis runs after the crawl.
- **Strict verifier: PASS** (165,958 published claims, 0 unverified values).
- All seven sections filled for all 1,000 (0 empty), with 0 unresolved citations.
- Standing: 583 percentiles, 141 too thin, 13 with no comparable company in the run, 263 not compared.
- No new HTTP from synthesis: 4,025 registry requests, against 4,028 in the 2026-11-16 control. Totals vary with live TED and website responses.

Rendered pages (`site-pages/`, open `site-pages/c/<org>.html`):

| Case | Org | Company |
|---|---|---|
| percentile | 912823970 | MYNT OG EIENDOM BESSAKER AS |
| percentile | 916729774 | FIKO EIENDOM AS |
| percentile | 918049215 | MENSTAD NÆRINGSPARK AS |
| percentile | 919948493 | SQ URBAN LANDSKAP AS |
| too thin | 991247610 | ROLIDBAKKEN FUS BARNEHAGE AS |
| too thin | 986739874 | AAS BETONG AS |
| no comparable company in the run | 995541432 | WACKER CHEMICALS NORWAY AS |
| not compared: no revenue figure | 917998787 | DRAGEHAUGEN VERDI AS |
| not compared: unspecified NACE | 935180759 | NESSET BLIKK AS |
| not compared: accounts failed | 926077422 | NRP ANAXO NORDIC M2 |

Full suite after the revision: **1460 passed, 0 failed** (`pytest.txt`).
