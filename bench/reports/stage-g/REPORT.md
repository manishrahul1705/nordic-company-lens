# Stage G: unchanged-runtime decision

**All revised gates PASS.** No wrong/doubtful reviewed item; activity1,000 and deadlines0 in both; full suite1,400passed0failed477.96s. Do not substitute the earlier Stage F absolute website/article gates for the user's revised Stage G gates.

## Probe before benchmarks

Ten deterministic previously202notice URLs, one anonymous XML GET each, then the same ten once after a30s wait (actual per-URL interval approximately67s including orchestration). Both rounds:10HTTP202/0HTTP200, empty bodies. No conversion; retain existing3s/8s,max2retry delays and250TED cap. The probe supports current unavailability of those ten sampled notices, not a claim that all TED notices are permanently unavailable. Raw statuses/timestamps in probe-round1/2.json.

## Two sequential benchmarks

Both use the frozen inputSHA7ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782, fresh state, README command, no bulk override, stripped credentials, no search/LLM/paidAPI. Runtime source/tests/lockfiles match007b34f; per-source hashes verified before each run, no code change between. Exact commands/commits/time in run1/2-execution.json; runtime-identity.json records the report-only HEAD difference.

**Run2 is final**, selected in advance, not the better website count. See NOISE.md and noise-band.json for all metrics in both runs with observed min/max and absolute span.

| Metric | Run1 | Run2 (final) |
|---|---:|---:|
| websites | 113 | 112 |
| social_companies | 47 | 47 |
| jobs | 2 | 2 |
| activity | 1000 | 1000 |
| news_companies | 7 | 7 |
| article_claims | 69 | 69 |
| GLEIF_companies | 32 | 32 |
| TED_companies | 0 | 0 |
| TED_awards | 0 | 0 |
| facts | 165481 | 165481 |
| http_total | 9281 | 9273 |
| http_mean | 9.281 | 9.273 |
| http_max | 40 | 40 |
| seconds_per_100 | 213.6968971800001 | 198.8786416499992 |
| wall_seconds | 2136.968971800001 | 1988.786416499992 |
| deadline_hits | 0 | 0 |

Both exits0,1,000envelopes/1,000profiles,offline sites,zero warnings. Both TED238requests,10HTTP200/228HTTP202,0published awards. All238<=250; retries exhausted remain honest failures. No complete TED coverage claimed.

| Website proof_type | Run1 | Run2 |
|---|---:|---:|
| jsonld_vatid | 5 | 5 |
| legal_name_and_registry_contact | 24 | 24 |
| legal_name_without_suffix_and_two_contacts | 9 | 9 |
| orgnr_on_page | 38 | 38 |
| registry_declared_hard_contact_tier_b | 3 | 2 |
| registry_declared_name_tier_a | 25 | 25 |
| registry_phone_on_site | 2 | 2 |
| unique_no_corroborated | 7 | 7 |

## Full incremental review

Every new website versus retained Stage E reviewed in both runs: ENSURE IT AS/934620011, https://ensure-it.eu, orgnr_on_page, exact saved proof text **ORG.NR. 934 620 011 MVA**. Each source blob hash/excerpt was verified by extraction. Verdict2correct/0wrong/0doubtful (same recovered company in both). It is a recovered company versus Stage E, not merely a URL alias there. All other website memberships are retained baseline sites, except ISTAD withheld in run2. No new wrong/doubtful rule output requiring removal. Both award arrays empty;0awards to review. review-verdicts.json and website-review-pack.json retain exact evidence.

## Signal versus noise limitation

The only inter-run website difference is ISTAD. The homepage HTTP200/hash is identical, but its blob is missing in run2; unchanged role-holder scope guard consequently withholds the link. No recorded homepage network error explains it. Both have the same /om-oss404. This is an **observed missing-evidence storage limitation**, not proven transient transport noise. No article differences. Report it instead of claiming all variance is network noise. Exact diagnostics in istad-diagnostics.json; full band and difference records in NOISE.md/website-article-differences.json. No storage/proof fix is made under this no-rule-change task.

## Merge decision

The revised gates pass independently of absolute website/article counts. Merge exact transport commit007b34f normally into the existing main clone on top ofe57bd74; preserve history, no cherry-pick. Then merge measurement/docs commits. README/SUBMISSION explicitly cite final run2 and both-run band, honestTED202 distribution and missing-evidence issue. No push. No changes to acceptance/scoring/expiry/ownership, tests or lockfiles from007b34f.
