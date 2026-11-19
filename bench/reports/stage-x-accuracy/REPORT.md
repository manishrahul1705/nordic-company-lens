# Stage X accuracy review

**Result: 200 of 200 sampled published claims correct and attributed to the right
organisation number. 0 wrong, 0 doubtful. Wilson 95% lower bound: 98.1%**, above the 95% bar.
153 items were verified mechanically, 47 by hand.

**Reproducible from a clone.** Everything this review needs is committed under this folder.
`bench/runs/` is not needed:

```sh
uv run --frozen python bench/reports/stage-x-accuracy/reproduce.py         # sample + checks + tallies
uv run --frozen python bench/reports/stage-x-accuracy/attribution_audit.py # cross-company audit
```

Each script exits 0 and prints `OK` only if it reproduces the committed `sample.jsonl`,
`population.json`, `summary.json` and `attribution.json` exactly.

Run: `bench/runs/frozen-repro-20261119`, the frozen 1,000 cohort (`bench/inputs/1000-r3/batch.jsonl`)
on code `4af8591`, using the official command with default concurrency and fresh state. It
emitted 1,000 envelopes, `run_status` completed, 9,374 HTTP requests (at most 40 for one
company), 0 deadline hits and $0 cost, in 2,285 s wall time. Seed: **20261119**. Sample size: 200.

## Committed data

| File | What it is |
|---|---|
| `extract/envelopes.jsonl.xz` (16.3 MB) | Population index. For every envelope: each published claim (id, field, value, evidence ids), the evidence records those claims cite (URL, locator, span, SHA-256), and each synthesis sentence with its cited claim ids |
| `extract/blobs.jsonl.xz` (0.3 MB) | The full cited source bytes for every sampled claim (176 blobs), keyed by SHA-256; each hash is recomputed on load |
| `extract/manifest.json` | Run name and id, blob count, file hashes |
| `population.json` | Family sizes and allocation |
| `sample.jsonl` | The 200 drawn items, with the cited evidence and the mechanical check |
| `verdicts.jsonl` | One verdict per item: correct / wrong / doubtful, basis (mechanical or hand) and the reason |
| `summary.json` | Tallies and the Wilson bound recomputed from `verdicts.jsonl` |
| `attribution.json` | Attribution audit counts and examples |
| `extract.py` | Builds the extract from a full run directory. This is the only step that needs `bench/runs` |

## Method

1. Population: every published claim (`availability == "available"`, excluding `*.section`
   placeholders), plus every synthesis sentence. Each item is assigned to a family; the mapping
   is `family()` in `common.py`.
2. Allocation: each family gets 1 item. The remaining items are split by largest remainder in
   proportion to family size. Within a family, `random.Random(20261119).sample` draws from the
   items sorted by (orgnr, field, id).
3. Mechanical check, per claim, against the cited evidence bytes:
   - the claim span is present in the decoded body;
   - for JSON sources, the value at the cited JSON-pointer locator equals the claim value;
   - the organisation number appears in the source URL or in the located record.
4. Verdicts:
   - **Mechanical (153):** accounts, identity, roles and subunits where the value at the locator
     is identical and the source URL is the organisation's own registry record
     (`/enheter/{orgnr}`, `/regnskap/{orgnr}`, `/underenheter?overordnetEnhet={orgnr}`).
     `reproduce.py` re-asserts every one of these.
   - **Hand (47):** every other item, read against its committed evidence. Each verdict
     records its reason.
     - Batched sources (registry change feed, GLEIF): the record at the locator was confirmed
       to be the company or one of its published subunits, with the same update id and
       timestamp.
     - Roles: name and role type at the locator.
     - Hiring: the ad page title and an employer subunit.
     - Social: the Wikidata P2013 binding for the organisation number.
     - Websites: the org number printed on the page, or the exact legal name after the
       registry-declared domain's redirect.
     - Synthesis: checked against the claims it cites and, for "not found" sentences, against
       the envelope's research record.
5. Attribution audit (`attribution_audit.py`), over all 1,000 envelopes:
   - dangling evidence references;
   - entity-specific registry URLs that name a different number;
   - company-owned page URLs or content hashes cited by more than one envelope;
   - evidence spans labelling an organisation number the envelope does not itself publish.

## Counts

| Family | Population | Sampled | Correct |
|---|---:|---:|---:|
| accounts | 97,416 | 101 | 101 |
| identity | 30,339 | 32 | 32 |
| synthesis (sentences) | 18,164 | 20 | 20 |
| roles | 17,817 | 19 | 19 |
| activity | 12,112 | 13 | 13 |
| subunits | 6,907 | 8 | 8 |
| GLEIF | 736 | 2 | 2 |
| website | 551 | 2 | 2 |
| social | 87 | 1 | 1 |
| brands | 18 | 1 | 1 |
| hiring | 3 | 1 | 1 |
| **Total** | **184,150** | **200** | **200** |

TED published no awards in this run, so it has no family. TED availability varies between live
runs; see SUBMISSION.md.

Wilson score lower bound, 200/200, z = 1.96: n / (n + z²) = 200 / 203.84 = **0.981**.

**Attribution audit:** 1,000 envelopes, 165,986 published claims, 166,431 cited evidence records.
**0 dangling references, 0 registry-URL mismatches, 0 company pages or content hashes reused
across envelopes, 0 foreign organisation-number labels.**

## Limits

- Proportional allocation puts 1 or 2 items in each small family. The bound covers published
  claims as a whole, not each small family on its own.
- The sampled brand ("kanobutikken.no" for HETLY FRITID AS) is correct: it is the title of the
  verified registry-declared site, which names the company. But it is a domain-style name, not
  a strong brand. **Doubtful brands outside the sample:**
  - "Profesjonelt rengjøringsfirma Reneffekt" (RENEFFEKT AS) is a tagline plus the name;
  - "D Production 1" (D-PRODUCTION AS);
  - "Familien Brynildsens legat - brynildsenslegat.no".

  Brands are 18 of 184,150 population items, so they do not move the bound, but brand
  accuracy on its own is lower than the overall figure.
- **Section-placeholder citations.** Several "not found" synthesis sentences (no workplaces, no
  job ads, no registered homepage, website withheld) cite the section's placeholder claim. That
  claim carries the state but no value or reason. The sampled sentences are true, as checked
  against the envelope's research record, but the cited claim alone does not show the stated
  reason.
- **"First observation" citation.** The sentence "First observation; no earlier run to
  compare." is true, but it cites the company's first published claim rather than the
  first-run status. That status is not itself a published claim. This is unchanged from the
  previous review and affects one sentence per company on a first run.

## History: the original review (not reproducible)

`history-final-frozen-20261118/` holds the first Stage X review: its `sample.jsonl`,
`verdicts.jsonl`, `population.json` and the original `sample_and_check.py`. That review reported
200 of 200 correct on `bench/runs/final-frozen-20261118` (code `0ba340c`).

**That source run no longer exists**, and the original draw cannot be reproduced. Its sample
holds only short excerpts of the cited bytes, not the bytes themselves, so its checks cannot be
rerun either. The same is true of the earlier attribution audit
(`bench/reports/attribution-audit-20261118.md`, on `bench/runs/long-label-clean-20261118`). Both
are kept as history only. The review above, built from a committed extract, supersedes them.
