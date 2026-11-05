# S6 Step 6 scoreboard

**Final decision: KEEP steps 1-3; ROLLBACK step 4.** Suffix/two-contact proof is ON by default. Domain/location is OFF. The one-contact ambiguous rescue implementation and its trial switches were removed. Search stayed OFF; credentials were stripped; nothing was pushed.

All runs used the same frozen 1000-company batch and registry bytes. Coverage counts are available companies; shared HTTP requests are excluded from attributed company means and included in amortized means.

| Section / metric | Baseline A | Baseline B | Fixed noise band | Steps 1-3 KEEP | Step 4 alone ROLLBACK | Steps 1-4 ROLLBACK |
|---|---:|---:|---:|---:|---:|---:|
| identity | 1000 | 1000 | 0 | 1000 | 1000 | 1000 |
| people | 997 | 997 | 0 | 997 | 997 | 997 |
| locations | 774 | 774 | 0 | 774 | 774 | 774 |
| financials | 999 | 999 | 0 | 999 | 999 | 999 |
| website | 59 | 57 | 2 | 83 | 87 | 91 |
| social | 30 | 26 | 4 | 39 | 39 | 38 |
| jobs | 3 | 3 | 0 | 3 | 3 | 3 |
| news/activity | 230 | 231 | 1 | 231 | 231 | 231 |
| HTTP requests | 6483 | 6634 | - | 7901 | 7094 | 7487 |
| Max HTTP / company | 18 | 18 | - | 18 | 18 | 18 |
| Mean attributed HTTP / company | 6.449 | 6.600 | - | 7.867 | 7.061 | 7.453 |
| Mean amortized HTTP / company | 6.483 | 6.634 | - | 7.901 | 7.094 | 7.487 |
| Max website HTTP / company | 15 | 15 | - | 15 | 15 | 15 |
| Mean website HTTP / company | 3.444 | 3.595 | - | 4.862 | 4.056 | 4.448 |
| Wall seconds | 818.967 | 673.080 | - | 937.257 | 708.255 | 1218.631 |
| Website request-cap errors | 71 | 86 | - | 113 | 81 | 90 |
| Deadline hits | 0 | 0 | - | 0 | 0 | 0 |
| Wrong-company findings (companies / claims) | not reaudited | not reaudited | - | 0 / 0 | 1 / 4 | 1 / 4 |
| Source commit | 2351e57 | 2351e57 | - | 7dbcd26 | dce6d31 | b296a19 |

The final kept runtime is the measured steps 1-3 implementation restored by `2f7b06e`, followed only by removal of unused rescue configuration/CLI/benchmark switches. The 83/39/231 kept counts come from its recorded run, not a newly claimed rerun after rollback. Work stayed on main; the isolated ablation used a local checkout. Final local report commit is reported in the response.

## Noise band and gate

Observed absolute A/B differences: identity 0, people 0, locations 0, financials 0, website 2, social 4, jobs 0, news/activity 1. These two-run differences are an empirical band, not a statistical confidence interval. Later runs were checked against the higher baseline count per section. A drop is excused only when within this fixed numerical band AND traced to a recorded transient failure outside the changed rule.

Website churn was much larger than the net count difference:18 sites disappeared, 16 appeared, and one changed apex/www authority. Every company, URL and failure reason is listed in [NOISE.md](NOISE.md); exact candidate diagnostics are in [noise/comparison.json](noise/comparison.json). NXDOMAIN, robots/4xx, owner conflicts and request-cap exhaustion were not automatically called transient.

Steps 1-3 had no section drop against either baseline, so no exception was needed. Combined versus steps 1-3 gained8websites but lost1social company. The social drop is numerically within4, but six previously social-available companies disappeared and some have only recorded no_such_domain failures; no blanket transient exemption was granted. The wrong-company gate independently rejects combined. Exact losses: [combined-vs-steps 1-3/social-losses.json](combined-vs-steps 1-3/social-losses.json).

Step 4 alone versus steps 1-3 measured+4websites, 0social and0other-section difference. This is a component ablation, not the final configuration; it independently reproduces the same wrong-company failure. Public source variation remains visible in all comparisons.

## Retained changes

Step 1 enables the existing suffix-free legal name plus two independent registered contact categories by default; domain/location stays OFF. Step 2 retries timeout, reset/refusal or temporaryDNS/SERVFAIL-class failure once after1.5 seconds, with12 seconds for the retry. NXDOMAIN, TLS/certificate failures and4xx responses are not retried. Robots, company and proof requests use the same bounded transport, and an exhausted robots retry cannot be repeated by the enclosing page call.

Step 3 raises the website request ceiling to16, within the existing total-company18 ceiling after official requests. The observed website maximum is15 because ordinary official-source work consumes three requests. For explicitly lower website caps, the existing reserved activity request is preserved without exceeding16. Global HTTP hard ceiling is18 per distinct normalized input (1800 per 100); total time is capped at24 seconds per input (40 minutes per 100), with lower configured limits honored. At 1000, the hard time ceiling is24000 seconds, while the existing default2400-second budget remains the tighter effective limit. Crawl finalization reserves and graceful terminal outputs are retained. All five runs emitted1000 envelopes and1000 profiles with zero deadlines.

## Review and rollback

All differential items were opened from saved company-page evidence and compared for exact-company attribution. SHA-256 and raw evidence-span checks accompanied the review; no social destinations or search were requested.

- [Steps 1-3 review](steps 1-3/REVIEW.md):231 items (32 website proof/URL changes, 22 social URLs, 95 contacts, 74 self-descriptions, 8 brand strings), zero wrong-company findings. Every one of74 description values exactly matches captured metadata/paragraph text. Existing generic titles, placeholder prose and malformed mailto formatting are recorded as source/extraction-quality limitations.
- [Combined incremental review](combined-vs-steps 1-3/REVIEW.md):176 items, 150 correct, 22 unsure, 4 wrong. [Combined versus baselineB](combined/REVIEW.md):308 items, 282 correct, 22 unsure, 4 wrong.
- [Step 4-only review](step4-only/REVIEW.md):283 items, 254 correct, 25 unsure, 4 wrong. Its27 additional semantic items were separately inspected, including7 website-proof variations, 18 description variations and2 own-organisation dated articles.

The definitive wrong-company subject is **ZINZINO AS, 986028269**. Registry contact economy@zinzino.com led the rescue to accept shares@zinzino.com. Its captured investor-relations page explicitly names **ZINZINO AB(PUBL.)** and its Certified Adviser. The shareholder contact and three investor self-descriptions were published under the Norwegian AS. Shared email domain does not establish exact-entity ownership. Both rejected runs show the same failure; the isolated run also landed on the India-language/market path `/site/in/en-gb`, which was not treated as Norwegian identity proof. [Exact wrong-company excerpts and SHA](WRONG_COMPANY.json).

Permobil global-site attribution and other unresolved Zinzino shared-site items remain unsure, not falsely counted as proven wrong legal entities. No per-company allowlist/blacklist or ad-hoc exception was added. Step 4 was reverted in full; its reproducible standalone patch is [step4-only-ablation.patch](step4-only-ablation.patch).

## Validation and commits

Steps 1-3 suite:885 passed in265.53seconds. Rejected combined suite:896 passed in262.63seconds, including11 focused rescue tests. The isolated ablation previously passed869 tests before the final contact-scope clarification; its final helper matches the helper exercised by the combined suite. Final kept suite after removing unused trial switches: **885 passed in 301.89 seconds**; exact commands and earlier validations are recorded in tests.json.

Commits: `7dbcd26` steps 1-3; `b296a19` combined trial; `2f7b06e` step4 rollback. Isolated step4-only source `dce6d31` is locally retained with its full patch. All were authored/committed as Manish Rahul <manishrahul1705@gmail.com>. No push.

Frozen batch SHA-256: `7ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782`; registry SHA-256: `b5b3462dc1a27dbf5383ee91508b6126f6ccf9b3b8c9e190dd31d601413e1850`. Credentials/search settings, exact commands, raw scoreboard, run paths and complete per-company request counts are retained in each stage folder. New evidence files were scanned for credential-shaped values without printing any values; results: credential-check.json.

Step 6 validations and reviews are complete; the final local evidence commit is reported in the response. Step 7 was not started.
