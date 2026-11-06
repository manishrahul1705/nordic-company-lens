# S6 Step 10 — recall trial and precision gate

**KEEP the tiered nominated-site improvements, recovery, subunit discovery, social/news discovery, typed locations and pooled budget. ROLLBACK unique-name-only acceptance and contact-only two-signal acceptance. Tighten explicit publisher checks.** Search stayed OFF; credential variables were stripped; no push.

One complete 1000-company crawl was run, on `2851a42`. The earlier `3305684` attempt stopped at 635 completed companies and never produced final output; it is excluded from coverage. Its last heartbeat was 08:48:08 UTC and no process remained. No cause beyond process termination was established.

The kept column below applies the final publication guard to that crawl's saved evidence. **It is an offline policy projection, not another measured crawl of the final code.** It tests no replacement candidates. The 120+ target was reached by the rejected trial but **not** by the kept output.

| Section / metric | Baseline | Measured trial | Kept saved-evidence projection | Decision |
|---|---:|---:|---:|---|
| Identity | 1000 | 1000 | 1000 | KEEP |
| People | 997 | 997 | 997 | KEEP |
| Registered subunit coverage | 774 | 774 | 774 | Unchanged |
| Location profiles, including typed business address | 774 | 997 | 997 | KEEP |
| Financials | 999 | 999 | 999 | KEEP |
| Website | 83 | 128 | **95** | Partial KEEP; unsafe rules removed |
| Social | 37 | 49 | **40** | KEEP retained exact-company links |
| Jobs | 3 | 3 | 3 | KEEP strict active/employer proof |
| News/activity | 231 | 236 | **235** | KEEP dated article proof |
| Envelopes / profiles | 1000 / 1000 | 1000 / 1000 | 1000 / 1000 | PASS |
| HTTP requests | 7953 | 6412 | Same saved requests | Within global pool |
| Maximum attributed HTTP per company | 18 | **33** | No new requests | Below 40 |
| Mean attributed HTTP per company | 7.916 | **6.374** | No new requests | 38 shared requests excluded |
| Mean amortized HTTP per company | 7.953 | **6.412** | No new requests | Shared requests included |
| Wall seconds | 1340.399 | **500.986** | Not a new timing measurement | PASS |
| Deadline hits | 0 | 0 | 0 | PASS |
| Wrong-company findings in kept reviewed items | — | Five explicit different-entity companies found | **0** | PASS after rollback |

Baseline: `bench/runs/20261106T055741582104Z-1909653`. Trial: `bench/runs/20261106T085057525871Z-2851a42`. Baseline timing/request figures are retained measurements, not a rerun. [Raw trial scoreboard](benchmark/scoreboard.json), [execution](benchmark/execution.json), [kept metrics](benchmark/kept-metrics.json), [per-company requests](benchmark/requests-by-company.json), [offline suppression list](benchmark/policy-projection.json).

## Precision findings and tiers

The explicit different-entity cases were ALOHA AS → Down The Line AS; NORWEGIAN BUSINESS PAVILIONS AS → Messetjeneste AS; HUSFLIDEN HAMAR BUNAD AS → Husfliden Hamar AS; 7OCEAN HOLDING AS → 7ocean Group AS; and LINDÅS NÆRSENTER AS → Nærsenter Vest AS. The name-only rule also accepted a for-sale page, a server directory/default page and frameset/default placeholders. Straumsnes Utvikling's shared address/email on Ice Drift was insufficient exact-company proof and is withheld.

All 29 unique-name-only websites and all three contact-only two-signal websites were removed, including apparently plausible ones. The corresponding derived social, descriptions, contacts and company-site activity were removed with them. There are no per-company exceptions. Tier B's foreign copyright owner is vetoed; agency credits and a statement about corporate share ownership do not override a site's own publisher identity.

The trial had 25 registry-declared Tier A sites and four Tier B sites; **25 and three** remain. The kept 95 websites comprise 25 declared-name Tier A, 67 existing stronger-proof Tier A and three link-only Tier B. All newly applied declared tiers were reviewed, including existing URLs whose proof changed. Every new social URL was reviewed: 27 trial additions, 13 retained. There are 24 new website companies and 12 baseline website losses, net +12. The retained site/handle review has zero wrong-company findings; this is a finite evidence review, not a guarantee of universal accuracy. [Complete website/social review](REVIEW.md), [source excerpts and hashes](new-items.json).

All 250 new typed address items reuse the exact unchanged parent registry address claim already present in the baseline. They add presentation, not inferred workplaces. Shared/c/o addresses remain explicitly registered addresses. Their individual rows, claim IDs and source locators were checked. [Location review](LOCATION_REVIEW.md), [evidence](new-locations.json).

## Funnel and retained behavior

The diagnosis used only the latest retained 1000-company run, before any new crawl. Of 107 registry-homepage nominations, 80 fetched successfully and 26 passed the old proof; email: 189 nominations, 129 fetched, 31 passed; subunit: 167 domains across 155 companies, 109 fetched, 31 passed; guesses: 10,455 attempted domains, 276 fetched, 43 passed. These overlapping categories must not be added. Old logs support only an observed lower bound on resolution, not a reconstructed DNS-success rate. [Full funnel, reasons and 30 seeded examples](FUNNEL.md).

The audit covered all 83 baseline websites and found 56 unreported URL spellings, including employee accounts, platform credits, groups and duplicates. [Decisions for every observed link](BASELINE_SOCIAL_AUDIT.md).

Requests now share a global ceiling of 18 per distinct normalized input, at most 40 per company, with existing time caps and lower explicit limits preserved. At 1000 the hard request cap is 18,000; the tighter default time budget remains 2400 seconds. DNS recovery retains the bounded 2-second public resolvers, blocked-UDP safety, 10-second per-company fallback cap and metrics: 5385 fallback attempts, 10 domains recovered, 2358.002 aggregate fallback seconds (concurrent across companies; not wall time).

Registry homepage/email, subunit homepage/email and trading names, exact-employer NAV homepages and domains in already-held account text nominate candidates. Company or any registered subunit orgnr can prove ownership. Registry-declared name sites use Tier A; a hard registry contact/role-holder without the name can supply only a Tier B link. Other nominated sites require legal name plus a separate contact category. Nominated transport recovery covers HTTPS/HTTP and apex/www, up to six ownership pages, and one bounded transient retry. Cross-domain redirects require company identity on the destination. Names containing holding/invest/kapital/sameiet/borettslag skip guesses; other guesses are capped at four after stronger candidates fail. The rejected uniqueness lookup is removed, including its extra registry requests.

Social discovery recognizes verified-site JSON-LD and contact/footer/header/social widgets while retaining name/brand, sharing and entity guards. Sitemap and RSS/Atom URLs nominate articles; publication requires a datePublished or time tag on the fetched article itself. Careers/ATS discovery accepts a single dated active JobPosting only with an exact registered employer identifier; a landing page never qualifies. No additional site-job posting passed that strict gate. NAV consumed six forward-feed pages once, made 11 live detail requests and published the same three exact-employer active ads. One publicToken request returned HTTP 200 with credential variables absent; the token stayed in memory. Feed coverage completed.

## Validation and commits

The complete kept-code suite passed **1007 tests in 267.03 seconds**. The subsequent excerpt/DNS-wording polish passed **102 focused tests in 13.17 seconds**. An earlier full run had one live evaluator smoke timeout (20 deadlines in its 30-second invocation); the test passed alone in 14.86 seconds, and the later full run passed. No verifier gate was weakened. [Test causes and history](TESTS.md).

The projected 1000 output passed independent schema, membership, citation and source-blob verification: 110,952 claims, 3992 blobs, 8393 checked template sentences, zero unverified synthesis values. [Verification](kept-verification.txt).

The final source `5f1c5e1` was freshly cloned, `uv sync --frozen` passed, and the literal README command ran twice with the same state and no extra flags. Both emitted 103 envelopes/profiles; strict pairwise verification passed with identical claim IDs, zero changes and zero observation changes. [Exact command, timing and evidence](official-run/RESULTS.md).

Commits, all authored/committed as Manish Rahul <manishrahul1705@gmail.com>: `3305684` implementation and saved funnel; `2851a42` plain-English brief reasons; `d84084b` precision rollback and publisher veto; `99ac0a0` corporate-parent distinction; `5f1c5e1` localized normalized-name excerpts and DNS wording. The final evidence-only commit is reported in the response. Main branch; no push.

Disk checks before both crawl attempts passed: 10.938 GB and 17.039 GB free on C:. No run folders were deleted by this work. Frozen batch SHA-256 `7ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782`; registry `b5b3462dc1a27dbf5383ee91508b6126f6ccf9b3b8c9e190dd31d601413e1850`.
