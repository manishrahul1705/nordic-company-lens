# Stage U (revised): whitespace-only TED identifier matching on the live path

Branch `stage-u-ted-whitespace`, from `revision-4` (701afaa). The bundled-snapshot work is parked unmerged on `stage-u-ted-snapshot` (ac9d9da). Its build was stopped at pass 8, with 1,200 notices still pending.

## Change

`src/signalpost/sources/official_extra.py` only. No snapshot file, reader, CLI flag or `effective_configuration` entry is included.

- `ted_orgnr`: an identifier made only of digits and whitespace (any Unicode whitespace) becomes its compact form. It must then be exactly nine digits, or it is rejected. Prefixes such as `NO`, suffixes such as `MVA`, hyphens and short or long numbers never match.
- `ted_nominated` replaces the literal set intersection when the live search nominates notices.
- `ted_query_values` sends each organisation number both plain and as `ddd ddd ddd` in the identifier query.
- `award_extract` now removes all whitespace from the XML `cbc:CompanyID`, where it previously removed only ASCII spaces. Its `NO`/`MVA` stripping is unchanged.

There is no other acceptance change: award types, 36-month window, exact winner or buyer, at most 10 awards, lot-linked amounts only, and the fail-closed rule on fetch failure all stay as they were.

Tests: 11 new in `tests/test_official_extra.py`. Full suite: **1,463 passed, 0 failed** (`pytest.txt`), against 1,452 at revision 4.

## Frozen 1,000 (live)

The full run exited 0 with 1,000 envelopes, 0 warnings and 0 deadline hits. TED search: 10 requests, all HTTP 200. **Nominated 78 notices against Stage S's 76.**

TED was throttling notice XML during this session: 116 of the 167 TED requests returned HTTP 202, and 37 notices failed after retries. The fail-closed rule drops every award of a company with any failed notice. As a result, the live run published 2 awards for 1 company, against Stage S's 20 awards for 6. A TED-only rerun was worse (176 of 207 returned 202). A direct retry of the 3 notices that were never saved also got only 202s. **The live TED count from this session therefore says nothing about the change.**

## Paired offline replay (the clean measurement)

`replay.py` runs the real `official_extra.collect` twice through a mock transport: once with revision-4 code (a git worktree) and once with the branch code. Both get the same saved inputs:
- the 10 saved search responses;
- the saved notice XML (75 of the 78 notices);
- HTTP 202 for the 3 notices with no saved XML (263789-2024, 778400-2026, 69404-2025).

| | revision-4 | branch |
|---|---:|---:|
| Nominated notices | 76 | 78 |
| Awards | 9 | 9 |
| Companies | 4 | 4 |

- **Award claim IDs, values and evidence are identical** between the two code versions.
- The branch's only difference is fetching 170520-2025 and 404734-2025, which publish nothing.
- All 9 replay awards are Stage S awards, matched by claim ID.
- The 11 Stage S awards absent from the replay belong to 984024290 (10) and 999536999 (1). These are exactly the companies whose missing notices fail closed in both versions.

## Recovered notices: hand review

| Notice | Orgnr | Legal name | Role in XML | Identifier text | Published | Verdict |
|---|---|---|---|---|---:|---|
| 170520-2025 | 984024290 | VEIDEKKE ENTREPRENØR AS | unsuccessful tenderer (TEN-0003; CON-0001 settles TEN-0001) | `<cbc:CompanyID schemeID="002">984 024 290</cbc:CompanyID>` | 0 | correct |
| 404734-2025 | 922828172 | TENSIO AS | buyer (1 of 11); neither contract has `cbc:AwardDate` | `<cbc:CompanyID>922 828 172</cbc:CompanyID>` | 0 | correct |
| 94190-2025 | 984024290 | VEIDEKKE ENTREPRENØR AS | unsuccessful tenderer (TEN-0007); no `cbc:AwardDate` | `<cbc:CompanyID schemeID="002">984 024 290</cbc:CompanyID>`, where the first gap is U+202F | 0 | correct |

The live path does not reach 94190-2025: its search identifier mixes U+202F with a normal space, and the query sends only the plain and ASCII-spaced forms. It was reviewed from the parked build's saved XML.

The facts behind each verdict are in `recovered-notice-facts.json` and `review-verdicts.json`.

**Measured effect: +2 nominated notices on the live path, and 0 new published awards on the frozen 1,000.** The change is correct, but its frozen-1,000 coverage gain is zero.

## Other families (live run against Stage S, separate live runs three days apart)

| Family | Stage S | This run |
|---|---:|---:|
| Identity, subunit, role and accounts claims | 31,076 / 6,914 / 17,802 / 97,416 | identical |
| GLEIF companies / claims | 142 / 736 | 142 / 736, same company set |
| Hiring claims | 2 | 2 |
| Registry-change claims | 12,083 | 12,057 |
| Dated items | 69 | 68 |
| Website companies | 112 | 114 |
| Social companies | 47 | 45 |

The registry-change, dated-item, website and social differences don't come from this change. The diff touches only TED nomination and the TED XML identifier comparison. These families are separate live fetches, and the two runs are three days apart. A same-day control run on revision-4 was not made, so this attribution rests on the code path, not on a paired live measurement.

## Same-day control (2026-11-16): gate stopped

The query now also sends `ddd ddd ddd`. TED's identifier search matches exact strings: of the plain, `ddd ddd ddd`, all-U+202F and mixed spellings, only the mixed form `984 024 290` returned 94190-2025.

Revision-4 (701afaa, clean worktree) ran first, then the branch (9f0f610 plus the uncommitted query change), with the same command, fresh state and consecutive sessions. Both exited 0 with 1,000 envelopes, 0 warnings and 0 deadline hits. Counts are in `control-counts.json`; the script is `control.sh`.

| | Stage S | revision-4 | branch |
|---|---:|---:|---:|
| Registry changes | 12,083 | 12,057 | 12,057 |
| Dated items | 69 | 68 | 68 |
| Website companies | 112 | 114 | **113** |
| Social companies | 47 | 45 | 45 |
| TED nominated notices | 76 | 76 | 79 (94190-2025 now in the search results) |
| TED awards | 20 | 0 | 0 |

**Website companies differ between revision-4 and the branch on the same day, so by the agreed rule the gate stops here.** The one company is 980973549 SKOGLI HELSE OG REHABILITERINGSSENTER AS (https://skogli.no, `registry_declared_name_tier_a`). In the branch run, `https://skogli.no/kontakt/` failed with `RemoteProtocolError`, while revision-4 got HTTP 200. Its website section became `ambiguous`. No code on this branch touches website fetching or proof; that is the observed cause, not a verdict.

TED notice XML returned HTTP 202 for almost every notice in both runs (121 and 125 responses), so both published 0 awards. Stage S's website count of 112 comes from its own counter; the 114/113 here come from `family_counts.py` (companies with an available `official_website` claim) and are comparable only with each other.

## Branch rerun (b386540, clean tree)

| | revision-4 | branch | branch rerun |
|---|---:|---:|---:|
| Registry changes | 12,057 | 12,057 | 12,057 |
| Dated items | 68 | 68 | 68 |
| Website companies | 114 | 113 | **114** |
| Social companies | 45 | 45 | 45 |
| Total HTTP requests | 9,504 | 9,493 | 9,526 |
| TED search / notice XML requests | 10 / 121 | 10 / 125 | 10 / 135 |
| Companies at the 40-request cap | 9 | 9 (same set) | 8 (a subset; 980973549 no longer at cap) |

- `https://skogli.no/kontakt/` returned HTTP 200, and 980973549 is again verified at https://skogli.no (`registry_declared_name_tier_a`). The four counts now match revision-4, so the earlier one-company difference was the site's connection reset: drift.
- TED: 79 notices nominated; 29 notice requests returned HTTP 200 and 116 returned 202.
- The rerun's wall time was 80,562 s, but only 307 CPU seconds were used. Requests ended at about 2,032 s, as in the other runs. The host slept during output writing, so the offline site was skipped on the clock budget. Envelopes, profiles and report are complete.

**HTTP budget.** Every TED request is reserved under `__official_extra__`. TED therefore draws on the pooled 19 × inputs ceiling (19,000 here), never on a company's 40-request cap, and it also has its own caps of 300 (GLEIF and TED) and 250 (TED).
- The three-spelling query adds **no search requests**: still one POST per 100-company batch, 10 in every run.
- The extra cost is one notice fetch per newly nominated notice (79 vs 76), plus retries on HTTP 202. Measured on the same day: +4 notice requests.
- No company reached its cap in a branch run without also reaching it in revision-4.

Full suite after the query change: **1,463 passed, 0 failed** (`pytest.txt`). Comparison data: `control-counts.json`, `budget-compare.json`.
