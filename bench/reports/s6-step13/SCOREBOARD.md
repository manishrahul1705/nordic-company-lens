# S6 Step 13 — breadth and fact depth

**KEEP under the requested precision gate: zero wrong-company additions. No breadth gain demonstrated by A or B in this sample.** Search OFF, application credentials stripped, no push. The earlier PDF lever remains removed.

One completed frozen-1000 measurement: `20261106T125849762180Z-7474c37`, source `7474c372`. An earlier `073bc14` attempt failed before producing required outputs because article aliases could generate duplicate canonical-URL claim fields. A focused regression reproduced it; canonical final-URL deduplication fixed it. That output-less attempt is preserved and excluded from coverage comparisons. [Excluded attempt](excluded-attempt.json).

## Sections and claim counts

The baseline is Step 12's reviewed saved-evidence projection, **not** a newly crawled current-code baseline. Same frozen batch/registry bytes. The historical missing Istad source blob is disclosed in the baseline record.

| Section | Saved baseline | Completed Step 13 |
|---|---:|---:|
| Identity | 1000 | 1000 |
| People | 997 | 997 |
| Subunit workplaces | 774 | 774 |
| Any typed location profile | 997 | **998** |
| Financials | 999 | 999 |
| Websites | 107 | **105** |
| Social available companies | 43 | **42** |
| Jobs | 3 | 3 |
| News/activity available companies | 236 | 236 |

| Published claim family | Before | After |
|---|---:|---:|
| identity | 28716 | 28716 |
| roles | 11803 | 11803 |
| subunits | 6527 | 6527 |
| accounts | 62584 | 62584 |
| website / social / contacts / self-descriptions | 781 | 782 |
| activity | 610 | **659** |
| hiring | 3 | 3 |
| Total | 111024 | **111074** |

There are **59 new/changed claim values**: nine website-family facts, 49 article URL claims and one official role-record metadata update. The net increase is 50 claims after removed/replaced values. None is falsely counted as a new verified company site. Typed postal locations reuse existing independently supported claims; no duplicate address aliases are added to inflate claim counts. [Counts](counts.json).

## A and B funnel

| Lever | Candidates | Fetched | Accepted | Kept after review |
|---|---:|---:|---:|---:|
| A Actual-use brand domains | 124 | 6 | 0 | 0 |
| B End-of-run transient retry | 35 | 1 | 0 | 0 |

A used at most four nominations per company, after stronger candidates failed. Nomination support: 48 registered-subunit names, four exact-employer NAV names and 72 fetched company-identity names. These are candidate counts, not independent companies. The .no/.com variants remain nominations; a brand match alone never publishes. On the newly nominated brand hosts, 61 website HTTP events were measured; this host-based attribution includes proof/redirect requests and may overlap B. [Fetched cases](brand-fetched-cases.json).

B selected 34 eligible companies; 33 could be attempted and one had exhausted its company request cap. It revisited top-three previously nominated candidates, cleared their DNS entries, disabled an additional transport retry inside the pass and used the original global budget object. It consumed **110 HTTP requests / 95.766 wall seconds** and recovered **0** websites, with zero unexpected retry-task failures. Those requests are included in the overall total, not added to it. Failed retries preserve the original honest failed/blocked result; they do not turn an incomplete check into a successful absence. [Complete per-company retry ledger](funnel.json).

No sub-rule was dropped for wrong-company output. A/B remain bounded requested capabilities, but their usefulness is not established by this run. No extra 1000 parameter trial was run.

## C depth and precision review

- Removed the three-year cap. All distinct exact-company SELSKAP fiscal years returned by the existing account response are supported, with per-year reporting periods; consolidated/group figures are not mixed into company accounts. This sample returned at most three years: 859 companies with three, 60 with two, 80 with one and one with no available statement. A seven-year synthetic test covers the former cap. No extra annual-report downloads or per-year duplicate latest aliases.
- Every registered role type was already extracted. Retained that complete extraction, removed exact duplicate source entries and tested deputy chair/member, auditor, accountant and contact-person codes. Actual output includes NEST, VARA, REVI, REGN and KONT; the website ownership helper remains restricted to director/chair. LAU CAPITAL's one changed source stamp does not count as discovering a new chair.
- Added **217 distinct typed postal locations** to profiles from already published parent/subunit postal claims. A generic PB/Postboks normalization removes the duplicate parent/subunit box. All workplaces remain represented. The extra available location profile is STIFTELSEN MAGNAR LUNDEMO MINNEFOND / 979907168: its registered postal address is at the mayor/Meråker town hall, explicitly labelled postal rather than an operating workplace.
- Removed article discovery/publication item caps while keeping the same article-side date and exact-source rules, pooled request caps and group restrictions. Retained supported partial articles when later checks fail. Canonical redirect aliases are deduplicated. The 49 additions include historical articles and separate language editions; they are article URL claims, not 49 new business events. Safety publications are not assertions that a company attended an incident. An open-application news page is never an ACTIVE job ad.
- Existing verified-social platform extraction remains intact. There are zero new social URLs in this completed run; Snappy's two lost social URLs follow its missing current site proof.

**Every new item was reviewed:** 59 claim values plus 217 typed location entries, all correct attribution, **0 wrong-company**. [Claim-by-claim verdicts](REVIEW.md), [all locations](LOCATIONS_REVIEW.md), [proof excerpts/dates/hashes](new-items.json), [location supporting claim IDs/evidence](new-locations.json), [depth audit](depth-audit.json).

The two lost websites are Istad and Snappy; both fetched successfully but did not survive current proof/guard checks. Neither is attributed to DNS or timeout, and no transient-noise exception is claimed. [Exact loss explanation and diagnostics](LOSSES.md).

## Requests, tests and official command

Completed measurement: **493.126 seconds**, **6869 HTTP**, max **40/company**, mean **6.830 attributed / 6.869 amortized**, 39 shared requests; 1000 envelopes and profiles; **0 deadlines**, no warnings, one website request-cap exhaustion and no output-size limit hit. Global 18,000-request / configured 2400-second limits were respected. C: had **6.418 GiB** free before the completed attempt. [Metrics and exact execution](metrics.json), [disk check](pre-completed-benchmark-check.json).

DNS fallback: 5692 resolver attempts, four recovered domains, 962.995 aggregate seconds, max 9.343 seconds/company. Aggregate concurrent DNS time is not run wall time. NAV's public-token/index/feed path completed seven feed pages and 11 live details; the three jobs remain verified, no personal token needed. Search calls 0, LLM calls 0, cost $0.

Final-source full suite: **1095 passed in 283.75 seconds**. [Full log](validated-full-tests.txt), [canonical/dedup focused tests](canonical-tests.txt). The six earlier minimal-fixture failures and the retired three-year-cap assertion were corrected before the completed measurement; earlier logs remain labelled as build history.

Independent verification: **1000 schema-valid lines**, **111074 supported claims**, **4069 checked source blobs**, **8423 cited synthesis sentences**, **0 unverified values**. [Verifier output](verification.txt).

Fresh-clone literal README command twice, same state and strict pairwise verifier: [official-run result](official-run/RESULTS.md). The final evidence commit records its exact counts and timings. Source commits: `073bc14`, canonical fix `7474c372`; final report commit follows. All authored/committed as Manish Rahul <manishrahul1705@gmail.com>. No push.
