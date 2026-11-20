# Bounded transient website second-pass recovery

## Implementation

Extend the existing end-of-run second pass to not_available websites with a final recorded unreachable-candidate reason of website_timeout, website_connect_error, dns_timeout or dns_unavailable. TLS, robots, definitive no_such_domain and ownership/veto rejections for the same candidate are excluded. A single authority variant returning NXDOMAIN does not override an explicitly transient final candidate summary; DOGLEG had that combination. NORTH GREY's final no_such_domain summary stays excluded.

No new nominations: retain original candidate domain, origin and subunit scope. Existing maximum three candidate nominations/company; one bounded collector pass per original candidate, with immediate transport transient retries disabled. The normal candidate pass still has its existing HTTPS apex/www and HTTP fallback variants; one candidate pass is not guaranteed one HTTP request. An attempted marker prevents another absence-retry dispatch on reentry. The old failed/blocked selection remains unchanged.

The same pooled and 40/company budget object authorizes every HTTP attempt, with normal website caps and host pacing. No budget/cap defaults changed. The unchanged collector and all final shared/social/entity/group/cohort/universe guards determine publication; name alone never proves ownership.

New optional recovery does not dispatch with <=500 ms left. Its existing 45-second/company window ends at least 250 ms before the real crawl deadline. Publication is transactional: failed recovery preserves the original terminal state/claims/errors; a clean proved-site checkpoint is retained before optional activity work, so a later activity timeout cannot erase it or add an envelope deadline error. Timeout reasons stay in retry metadata. No counter semantics, proof rule, validator, verifier or existing test changed.

## Live measurement

Baseline: stage-am-live1000, 1,000 companies. Saved available claims and real evidence were reused; only the new eligible not_available companies ran live through the production safe transport. The original request log/counters were retained. The site-on crawl reserve was retained and the entire saved 1,045.578-second pipeline duration was subtracted from the retry window, conservatively including its finalisation time. This is not a new all-source live run.

Selected **101 companies / 116 original candidates**. Dispatched 100 companies / 114 candidates; the remainder were blocked by their remaining budgets or retry window. [Exact nominations](eligible.json).

Shared production context; conservatively assume selected companies already spent their original 10-second public-DNS fallback allowance. Primary DNS remains enabled. The saved report lacks exact per-company fallback seconds, so this avoids granting a fresh DNS allowance. One preliminary run without that shared conservative DNS context is superseded and not used for the reported final result. A second preliminary run exposed the follow-on optional-activity rollback issue; the final run uses the clean proved-site checkpoint.

| Information | Before | After | Gain |
|---|---:|---:|---:|
| Verified sites | 110 | 113 | +3 |
| Brands | 19 | 19 | +0 |
| Social companies | 60 | 62 | +2 |
| Social claims | 123 | 126 | +3 |
| News companies | 30 | 30 | +0 |
| News claims | 109 | 109 | +0 |

**Extra HTTP: 291.** The second-pass stage itself used 291 requests and 213.078 s; bounded advertised-news requests, if any, account for the remainder. Measured live retry plus final-guard stage: **279.166 s**. Total replay including saved-output processing and strict verification: 406.217 s. These are standalone addition timings, not a paired whole-run wall-time delta.

Replay ordering correction: 31 prior official activity claims were retained from the saved baseline. Production merges registry activity after the second pass; this replay started with it already present. A company-site activity section replacement must not appear to delete those later-merged official facts. The harness now retains them before writing; the already completed live result was corrected offline with socket/DNS access forbidden and strictly reverified. That additional offline correction/verification is not included in the original replay duration above. No live request or acceptance decision was added by this correction.

HTTP including the saved run: 11746/19000; max/company 40/40. Remaining crawl window at replay setup: 1923.140 s; after live work and serialisation: 1595.906 s. **Deadline hits: 0.** Retry metadata reasons: {"completed": 89, "second_pass_timeout": 11, "company_budget_exhausted": 1}. These local retry-window timeouts are distinct from global/envelope deadline hits. No negative website claims are published.

## Named candidates and recovered sites

| Company | Orgnr | Retry result |
|---|---|---|
| TØMRER S. FAGERBEKK AS | 915279082 | proved website; second_pass_timeout |
| DOGLEG AS | 930832707 | proved website; completed |
| SPINELL FRISØR AS | 983520944 | proved website; completed |
| NORTH GREY AS | 934289099 | excluded: definitive no_such_domain |

All recovered sites after final guards:

- TØMRER S. FAGERBEKK AS (915279082): https://www.sfagerbekk.no
- SPINELL FRISØR AS (983520944): https://www.spinellfrisor.no
- DOGLEG AS (930832707): https://dogleg.no

## Hand-review of every recovery

[All recovered claims, exact evidence spans/hashes, registered identity and checked publisher pages](ownership-review.json). Each retained site was reviewed against its own-company proof and registered contacts; no inferred ownership, different-entity page or name-only match was accepted. Final verdicts are recorded per site.

- **TØMRER S. FAGERBEKK AS (915279082)** — https://www.sfagerbekk.no; proof `orgnr_on_page`. Correct: the homepage publisher footer explicitly states NO 915 279 082 MVA, beside Haukdalsveien 180 / 7288 Soknedal. Exact own orgnr, legal title and registry address agree; this is not a customer reference.

- **SPINELL FRISØR AS (983520944)** — https://www.spinellfrisor.no; proof `legal_name_and_registry_contact`. Correct: the page explicitly welcomes visitors to Spinell Frisør AS and publishes the exact registered email post@spinellfrisor.no. The working salon address/phone differ from the registry contact fields, so those are not used as proof. The exact name plus registry email satisfies the unchanged rule; no orgnr is invented.

- **DOGLEG AS (930832707)** — https://dogleg.no; proof `legal_name_without_suffix_and_two_contacts`. Correct: the site identifies its own studio as Dogleg and its footer gives Hegdehaugsveien 3, 0352 Oslo, exactly matching registered street and postcode/city. This uses the unchanged name-plus-two-registry-contact signals, not name alone. No conflicting publisher or foreign orgnr was found.

## Verification

Strict verifier passed 1000 envelopes, 178,640 claims and 5,965 source blobs, with **zero unverified synthesis values**. Every available claim has its retained evidence; verbatim spans and SHA-256 are verified. Failed retry state is preserved and the live measurement asserts no new envelope deadline errors.

Final full suite: **1843 passed, 1 warning in 538.25s (0:08:58)**. Baseline 1,815 tests; 28 new tests. [Full output](pytest.txt). New cases cover all admitted/definitive reasons, candidate veto precedence, one-pass reentry protection, company and pooled caps, near-deadline admission, cancellation before the deadline, unchanged ownership veto and preserving a proved site when optional activity is cancelled. The earlier pre-checkpoint full suite also passed all 1,842 tests.

Raw downloads, bench/runs, caches and pytest temporary directories are not committed. No push.
