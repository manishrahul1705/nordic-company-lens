# Bounded proof-page depth ? KEEP

Branch more-websites; base 51a04b3 plus exact runtime.patch/collector hash in runtime-source.json. No push or protected-branch changes. Exactly one live 1,000-company run, fresh state, frozen input SHA 7ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782, literal README flags/defaults, credentials stripped. Runtime was uncommitted during testing; execution.json records base HEAD, not an already-committed trial.

## Audit before coding

67 retained proof-only candidate sites across 63 companies; **20 sites/20 companies** contain matching own-site links. **8 sites/8 companies** have genuinely unfetched HTTP-page links after removing fragment duplicates/mailto. The initial interim unfetched count 15 was corrected to 8; the requested matching-link count stayed 20. Vetoed/parked/foreign-owner, blocked, transport and budget failure domains are excluded. Exact eligibility and evidence hashes: audit.json. These counts are nomination opportunities, not promised recoveries.

## Change and bounds

Preserve the first three existing follow-up targets/order. If those fail, nominate up to two unseen same-host links from already fetched pages, ranking sales/purchase terms, privacy, contact/imprint, about. Total HTML proof attempts are at most **five including the landing page**; after three original follow-ups only one slot remains. If fewer original targets exist, both added links can fit. Existing fixed fallback remains when there are no extra linked nominations, under the same cap. Stop immediately on newly found VERIFIED proof. Already-proved landing pages retain their original bounded checks and never trigger deeper links. Existing refresh proof counts toward the cap. No new proof types, identity rules, robots bypass or HTTP budget changes. Transport redirects/robots/XML requests retain their existing accounting; the five limit is HTML proof-page attempts, not total HTTP requests.

The old loop could exceed its documented depth; this change makes the total explicit. Every recorded candidate stayed at five or fewer. 25 candidates nominated deeper links; none became accepted through those links. Thus this trial demonstrates bounded behavior but **no incremental website recovery from the deeper links**.

## Live result

| Metric | Requested reference | This run |
|---|---:|---:|
| Websites | 113 | 114 |
| Social companies | 48 | 48 |
| Jobs companies | - | 3 |
| Activity companies | - | 1000 |
| Facts | - | 165614 |
| HTTP total | - | 9150 |
| HTTP mean/input | 18 pooled ceiling | 9.150 |
| HTTP max/company | 40 ceiling | 40 |
| Full wall seconds | - | 1878.250 |
| Amortized seconds per 100 | - | 187.825 |
| Deadline hits | - | 0 |
| Warnings/site warnings | - | 0 / 0 |
| Envelopes/profiles; exit | - | 1000/1000; 0 |

The actual preceding saved corrected-live artifacts contain 112 websites/48 social (not a measured 113 run): compared with those bytes, +2 websites, no website losses, no new social profiles. Requested 113 includes the prior offline bnv correction; it is not claimed as another live baseline. Both gained websites were reviewed, including the gain already explained by that earlier fix.

## Complete new-website review

| Company | Orgnr | URL/proof page | Proof | Verdict | Attribution |
|---|---|---|---|---|---|
| RORLEGGERMESTER TORSTEIN SOLLI AS | 983486703 | https://torsteinsolli.no/personvern | Own footer: Foretaksregisteret 983 486 703 MVA | correct | Existing privacy check timed out previously; now succeeds as page 2. Not new depth. |
| BERGEN VAKTMESTERTJENESTER AS | 990412375 | https://bnv.no/ | Own footer: 990 412 375, registered email/mobile and Eidsvagveien 150 | correct | Prior layout-ID fix in 51a04b3. Not new depth. |

**2/2 correct, 0 wrong, 0 doubtful.** Full exact excerpts/hashes and registry context are in live/website-review.json. No company-specific exceptions. KEEP: bounded implementation and no wrong-company output or coverage drop; do not interpret +1 versus the requested 113 reference as an effect of deeper proof pages.

## Validation and environment

Full suite **1282 passed in 308.02 seconds**; focused suite 162 passed. Seven new depth tests cover fourth/fifth-page proof, maximum five, budget stopping, extra-page foreign-owner veto, no deeper links after proof, priority and same-host filtering. Existing tests unchanged. Source SHA matches the tested and benchmarked patch.

Network sampled 1.190 Mbps on a 585 Mbps link before the run; no evidence of saturation, so Common Crawl worker was left running. At least 62 GiB free. Live sources and background machine load vary; wall timing is not a controlled speed comparison. No output scans overlapped timed publication. Raw outputs/site/state remain ignored under bench/runs/proof-depth-live; only derived reports/short excerpts are committed.
