# News + contact audit ? Part A ROLLED BACK, Part B SKIPPED

Branch `more-websites`; runtime base `77bd52f`. No push or protected-branch changes. Exactly one fresh-state 1,000-company live trial, frozen `bench/inputs/1000-r3/batch.jsonl` (SHA-256 `7ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782`), literal README flags/default budgets, credentials stripped. 45.1 GiB free before launch. Trial code was uncommitted; `runtime-source.json` and `trial.patch` preserve its exact source and tests. All hashes matched before rollback. Raw trial outputs/site/state remain ignored at `bench/runs/news-contact-live`.

## Audit before coding

The latest saved 1,000 run is `bench/runs/proof-depth-live`: 114 available company websites. Saved evidence exposes a sitemap for **88**, a homepage RSS/Atom link for **42**, and either for **91**. Counts require an actual retained robots Sitemap line, successful sitemap XML at `/sitemap.xml` or `/sitemap_index.xml`, or homepage alternate-feed link. Unfetched endpoints are unknown, not absent. Full per-company signals are in `audit.json`. Threshold 15 is exceeded, so Part A was tried.

Existing cited website contacts occur for **104/114** company websites: **204 email claims across 91 companies** (`contact.email.*`) and **149 phone claims across 80 companies** (`contact.phone.*`). No website visiting-address claims were found. Registry registered addresses remain separate typed facts. Because most verified websites already publish contacts, **Part B was skipped**, including address expansion. No new contact rule or staff-email filter was installed.

## The rejected trial

A supplementary path ran only after existing article discovery found no article, and only for a fresh VERIFIED, content-authorized company website. It preferred advertised feeds, otherwise robots/default sitemap links. At most two actual extra HTTP requests included robots, retries and redirects via a scoped ceiling; unchanged pooled/40-per-company limits, robots and spacing still applied. Same-domain entries needed explicit dates in the last 24 months and news-like paths; sitemap titles came from a fetched page, never a slug. Entry snippets cited XML, with a separate page-title citation when needed. Date source remained explicit (`pubDate` or `lastmod`); lastmod was not represented as a proven publication date. No event detail was inferred. Shared-site path/name checks and final scope guards remained in force.

An initial full suite caught an unnecessary extra request when existing article discovery had already succeeded. The trial was corrected to skip supplementation then; that existing test was not weakened. Trial validation then passed **1,312 tests in 372.74 s** (focused 40 passed). Eleven new cases covered positive feed eligibility, foreign/undated/old/product items, dated sitemap requirement, nonverified rejection, existing-news skip and the actual two-request ceiling including robots. Rejected-code tests remain in `trial.patch`; they were removed with the rejected module, without deleting or weakening any pre-existing test.

## One live trial versus last saved run

| Metric | Last saved run | Trial ? NOT KEPT |
|---|---:|---:|
| Envelopes / profiles; exit | 1,000 / 1,000; 0 | 1,000 / 1,000; 0 |
| Websites / social companies | 114 / 48 | 112 / 47 |
| News companies / articles | 7 / 67 | 14 / 78 |
| Jobs / activity companies | 3 / 1,000 | 3 / 1,000 |
| Website contact companies / facts | 104 / 353 | 102 / 350 |
| Contact email / phone facts | 204 / 149 | 202 / 148 |
| Distinct facts | 165,614 | 165,618 |
| HTTP total / mean / max | 9,150 / 9.150 / 40 | 9,346 / 9.346 / 40 |
| Wall seconds, including offline site | 1,878.250 | 1,597.614 |
| Seconds per 100 | 187.825 | 159.761 |
| Deadlines / warnings | 0 / 0 | 0 / 0 |

These are different live runs, not a controlled speed experiment. Lightweight offline review ran while site publication finished; no additional live benchmark was run. `execution.json` records full wall time including publication. `summary.json` retains exact counters and company lists.

The two website losses are JAR HELSE AS (979973969; also its social profiles) and RISIKOKONSULENTEN AS (999516386). Both previously passed phone-only proof. Offline replay of their original saved pages through current rules returns `MEDIUM / name_without_suffix_insufficient_contacts_or_domain`. This comes from the earlier final-precision full legal-publisher corroboration change, not supplementary news; the news path never verifies a website. The stricter proof was not weakened to recover counts. See `lost-website-replay.json`. The raw no-drop requirement also fails against the requested historical baseline.

## Every new news item reviewed

All **11** new/changed items were reviewed against saved entry spans, metadata and fetched titles: **9 correct, 2 wrong, 0 doubtful**. The failures are N?RINGS?KONOMI AS `/linker-og-nyheter` (general links/legal resources) and BORG BIERSTUBE AS `/borg-bierstube-artikler` (multi-article listing). Both are correctly attributed websites but not single news articles. Sitemap date + news-looking path + page title was insufficient. Under the requested rule, **all of Part A was reverted**, including its nine valid additions. No trial news output is presented as a retained improvement. See `NEWS_REVIEW.md` and `news-review.json` for every title, URL, source, date type and verdict.

## Twenty random existing contact facts reviewed

Fixed seed **20261112**, sampling all published website-contact facts. **15 comply** with the requested company-contact policy; **5 fail the personal staff-email exclusion**, although their source excerpts are genuine and belong to the correct company. The five are CONPLAN AS `per.eirik@conplan.no` and `edith@conplan.no`, VS ELEMENT AS `dawit.hurrisa@vselement.no`, IDESTOVA AS `anny@idestova.no`, and STYREGUIDEN AS `vidar@styreguiden.no`. None equals the registered email in the saved registry response. All 20 sampled facts already existed in the baseline; Part A added no contact facts.

This is an **open pre-existing contact-policy issue**, not a zero-error contact audit. Because Part B was explicitly skipped by the audit rule, there was no new contact implementation to revert. Existing contact publication was left unchanged. A future generic staff-email filter needs its own regression tests and review/benchmark before being kept. See `CONTACT_REVIEW.md` and `contact-review.json` for all 20 verdicts and source contexts.

## Final state

Part A: **ROLLED BACK**. Part B: **SKIPPED**. No production code from this task remains. Existing proof rules, news rules and contact behavior are exactly the pre-task runtime. Reports, reproducible measurement scripts and the rejected patch are retained. The restored-code suite was interrupted at 33% when the user authorized the separate contact-email precision fix. Its partial output is retained as `pytest-restored-interrupted.txt`; it is not a passing full-suite result. The completed rejected-trial suite is 1,312 passed. The contact fix will receive its own full suite and offline report.


## Subsequent contact precision fix

The open staff-email issue above is addressed separately in [the contact precision report](../contact-precision/REPORT.md). Its offline re-check removes all five flagged personal emails and both flagged staff-list mobiles. The rejected news feature remains reverted.
