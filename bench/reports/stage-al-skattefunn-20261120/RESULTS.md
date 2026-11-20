# Stage AL — SkatteFUNN historical approval snapshot

## Website funnel fix

Committed separately as `92ba52ceefaaa9f6b98252d6d6f368a7555e24fc`: report.json counts published available official_website claims (115 → 114). The two ownership tests were restored to HEAD. Full baseline suite: 1,754 passed, one footer extraction failure; that test then passed twice in isolation (19.18 s and 20.02 s). The commit message records the flake. Both evaluator network tests passed. No acceptance rule changed.

## Source, licence and build

data.norge.no lists the dataset 'Innsendte søknader til SkatteFUNN' (Forskningsrådet) under NLOD 2.0 https://data.norge.no/nb/datasets/f82d3d4a-b0f8-3220-83ef-15fbd854c54f/innsendte-soknader-til-skattefunn. The catalogue's distribution link (nov24.xlsx) returned HTTP 404 on 2026-11-20. We use the provider's current publication of the same dataset, linked from its SkatteFUNN page, and treat it as covered by the dataset's catalogued licence. Attribution: Forskningsrådet, NLOD 2.0.

Source: https://www.forskningsradet.no/siteassets/skattefunn/tall/skattefunn-innsendte-soknader-2002-2024.xlsx

Retrieved 2026-11-20T12:48:21Z; 12,200,263 bytes; SHA-256 `8466f7b7a93bafc036eead0f2f418b8368d47889ab582af3fb4ad18593697cad`.

Workbook: 70,599 data rows in Rapport 1, plus the header. Provider publication label: 2002–2024. Explicit application-date cells span 2002-09-27–2024-11-01; project periods may extend beyond it. No workbook-level conflicting licence or prohibition was found. Project descriptions mentioning patents/licensing/prohibitions are not workbook redistribution terms.

The index contains 52,902 approved records for 18,607 organisations, 8,581,330 bytes (8.18 MiB). Excluded: {"unapproved_or_invalid_explicit_cells": 17675, "ambiguous_duplicate_project_rows": 22}. Duplicate project numbers are excluded entirely. Original title text and selected source cells are preserved. Full raw XLSX is ignored and not committed.

The builder is `scripts/build_skattefunn_snapshot.py`. Rebuilding the actual workbook with the recorded retrieval timestamp reproduced both ZIP and manifest byte-for-byte. The built wheel contains the identical index, manifest and notice, and no raw XLSX/CSV. An initial optional source-distribution build was stopped; the wheel-only build and contents check succeeded.

## Publication rules

Funding snapshots retain their existing default and disable flag. Runtime adds zero HTTP. Require an available registry identity, exact valid applicant orgnr, approved JA and rejected NEI. Never match names, parents or subunits. Publish project number/title, explicit project years, scheme and decision date. Convert Excel decision-date serial cells; missing/#N/A/invalid values remain null, and application dates never substitute for decisions. SkatteFUNN is an R&D tax deduction scheme: no grant, cash amount or claimed deduction is asserted. Historical absence produces no negative claim.

Available published Forskningsrådet research project IDs suppress matching SkatteFUNN IDs. Both replays suppressed zero claims; a separate check also found zero overlaps between these 89 approvals and the current research bundle. An explicit regression test exercises the positive deduplication case. The latest full-1,000 saved baseline itself has no research/state-aid snapshot claims; those families are not retrospectively added by this isolated replay.

Each citation identifies the provider workbook, retrieval timestamp, original sheet/row, full workbook SHA-256, selected-cell JSON SHA-256 and verbatim excerpt. The evidence is labelled a selected-cell derivation, never the original XLSX byte stream. No validator, verifier, model, proof rule or request cap is weakened. No new brief template was added.

## Offline measurements

| Saved cohort | SkatteFUNN companies before → after | SkatteFUNN claims before → after | All published claims before → after | Added HTTP |
|---|---:|---:|---:|---:|
| Frozen 1,000 | 0 → 36 | 0 → 89 | 177,731 → 177,820 | 0 |
| First 100 frozen inputs | 0 → 5 | 0 → 9 | 17,962 → 17,971 | 0 |

The sample membership was checked against the frozen first 100 input rows. All prior published claim IDs remain present. Socket connect and DNS operations were forbidden by an audit hook. The full replay used stage-ak-audit-fix1000; the sample used stage-ak-defaults. The replay durations include loading saved output and strict verification, not a new live runtime benchmark: full 330.792 s; sample 23.451 s.

Strict verifier passed both cohorts: schema, claim citations, blob hashes, verbatim spans and synthesis checks; **zero unverified values**. Full: 177,820 published claims, 5,272 verified blobs, 2,575 synthesis sentences. Sample: 17,971 claims, 575 blobs, 266 sentences. Research/state-aid counts and existing claim IDs are unchanged.

## Ten hand-checks

Each row below was checked against the named original workbook row and its selected evidence cells. Approval is JA, rejection NEI, and applicant orgnr matches exactly in all ten. Numeric decision dates were independently checked with .NET FromOADate; #N/A remained null. All are historical tax deduction approvals, not payments. Full claim IDs, evidence IDs, hashes, verbatim spans, cells and individual correctness notes: [hand-review-10.json](hand-review-10.json).

| Company (orgnr) | Project / title | Period | Decision | Rapport 1 row |
|---|---|---|---|---:|
| OSEBERG ENGINEERING AS (984590881) | 34942 — Utvikling av ny kappe, stable og overføringsprosess for flatbrødproduksjon | 2005–2005 | null (#N/A) | 56085 |
| WACKER CHEMICALS NORWAY AS (995541432) | 254219 — Metall Production - Wacker | 2015–2017 | 2015-10-29 | 32702 |
| AAS BETONG AS (986739874) | 284377 — Betongsteiner til større støttemurer | 2018–2021 | 2018-04-20 | 22299 |
| RALSTON BAU AS (991368000) | 267140 — IDEAL LAB Tøyen Replanted | 2016–2017 | 2016-12-08 | 27970 |
| PRIME CARGO AS (886757972) | 281548 — Utvikling av nytt IT-basert logistikksystem for effektiv håndtering av retursendinger fra netthandel | 2017–2019 | 2017-12-14 | 22963 |
| MULTI PULSE SWEEP INTERNATIONAL AS (976871448) | 198683 — MTI for magnetronradar | 2009–2012 | 2009-12-03 | 47804 |
| HUSFLIDEN HAMAR BUNAD AS (982801559) | 30465 — Produktutvikling - fra kultur til næring | 2004–2005 | 2004-12-10 | 60801 |
| INFLOW MEDIA NORWAY AS (950220317) | 203688 — Edipluss2 | 2010–2012 | 2010-06-24 | 46390 |
| THE ORCHARD AS (980910857) | 223890 — Phonofile Sales and Analytics | 2012–2013 | 2012-12-03 | 41894 |
| ØRSHALL AS (942633475) | 20414 — Utvikling av Letti magasinverktøy | 2002–2002 | 2002-12-04 | 70235 |

OSEBERG project 34942 retains the historical flatbread-process title even though the present legal name suggests engineering: exact orgnr, rather than a guessed name/activity match, binds the record.

## Full suite

Before: 1,755 collected, 1,754 passed, footer flake failed and passed twice in isolation. After: 1778 passed, 1 warning in 538.25s (0:08:58).

New tests: 23, including enabled-runner publication with no source HTTP, approval/subject guards, decision-date edge cases, raw XLSX error/sparse cells, idempotence, project deduplication, corruption withholding and deterministic build.
