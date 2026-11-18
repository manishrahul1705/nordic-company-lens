# Stage X accuracy review

**Result: 200 of 200 sampled published claims correct and attributed to the right
organisation number. 0 wrong, 0 doubtful. Wilson 95% lower bound: 98.1%**, above the 95% bar.

Run: `bench/runs/final-frozen-20261118` (frozen 1,000 cohort, code `0ba340c`, standard command,
default concurrency, fresh state). Seed: **20261119**. Sample size: 200.

## Method

1. `python bench/reports/stage-x-accuracy/sample_and_check.py` draws the sample and writes
   `sample.jsonl` and `population.json`. Re-running it with the same run and seed reproduces the
   sample exactly.
2. Population: every published claim (`availability == "available"`, excluding `*.section`
   placeholders), plus every synthesis sentence. Each item is assigned to one of 12 families
   (mapping in the script docstring).
3. Allocation: each family gets 1 item, and the remaining 188 are split by largest remainder in
   proportion to family size. Within a family, `random.Random(20261119).sample` draws from the
   items sorted by (orgnr, field, id).
4. Mechanical check, per claim, against the cited evidence bytes in the run's blob store:
   - the claim span is present in the decoded body;
   - for JSON sources, the value at the cited JSON-pointer locator equals the claim value;
   - the organisation number appears in the source URL or in the located record.
5. Verdicts (`verdicts.jsonl`):
   - **Mechanical (149):** accounts, identity, and roles/subunits where the value at the
     locator is identical and the source URL is that organisation's own registry record
     (`/enheter/{orgnr}`, `/regnskap/{orgnr}`, `/underenheter?overordnetEnhet={orgnr}`).
   - **Hand (51):** every other item, read against its evidence. For batched sources (registry
     change feed, GLEIF), the record at the locator was confirmed to belong to the company, or
     to one of its published subunits. Website, social and brand items were checked on pages
     of the company's VERIFIED website. Hiring employers were checked against the company's
     subunits, and the TED buyer identifier in the notice XML. Synthesis sentences were checked
     against the claims they cite; the cohort counts in standing sentences are rebuilt by
     `scripts/verify_output.py`, which passed for this run.

## Counts

| Family | Population | Sampled | Correct |
|---|---|---|---|
| accounts | 97,416 | 100 | 100 |
| identity | 30,339 | 32 | 32 |
| synthesis (sentences) | 18,135 | 20 | 20 |
| roles | 17,817 | 19 | 19 |
| activity | 12,105 | 13 | 13 |
| subunits | 6,913 | 8 | 8 |
| GLEIF | 736 | 2 | 2 |
| website | 551 | 2 | 2 |
| social | 84 | 1 | 1 |
| brands | 26 | 1 | 1 |
| TED | 9 | 1 | 1 |
| hiring | 3 | 1 | 1 |
| **Total** | | **200** | **200** |

Wilson score lower bound, 200/200, z = 1.96: n / (n + z²) = 200 / 203.84 = **0.981**.

## Limits

- Proportional allocation puts 1 or 2 items in each small family. The bound covers published
  claims as a whole, not each small family on its own.
- **Known error outside the sample:** the brand published for VOKSER AS (919653477) is
  "Digitale løsninger som gir resultater" ("digital solutions that deliver results"), a page
  tagline, not a brand. The page-word rule does not cover leading descriptions; the same is true
  of RENEFFEKT AS. Brands are 26 of 184,134 population items, so this does not move the bound,
  but brand accuracy on its own is lower than the overall figure.
- Two synthesis sentences ("First observation; no earlier run to compare.") are correct, but cite
  an incidental accounts claim. One what-it-does sentence shows the NACE title in Norwegian.
  Neither is wrong.
