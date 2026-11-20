# Stage AQ — recover website misses

## Diagnosis first

[Detailed per-company candidate/fetch/proof trace and harness diagnosis](DIAGNOSIS.md). Baseline is the latest saved Stage AM full run, not the earlier 114-site run: it published 110 sites overall and 13 in the first 100. Only three named companies were probed during diagnosis, with 2/4/2 requests respectively (robots and redirects included), below five each.

- **912492575 / haugel.no:** registry-generated, fetch succeeded, rejected `different_legal_entity` because the page omits FORRETNING from its displayed legal name. Sole footer orgnr 912 492 575, street and phone match. Homepage and service-page title components share the same publisher identity. This is the only recovered site.
- **914248906 / indigoboom.com:** both .no/.com were generated; .no already verified from the legal-name core plus registered street and postcode/city. Stop-after-verified prevented a .com fetch. Live .com shows the same registered Oslo address. No missing website coverage, no replacement.
- **982410851 / marun.no:** registry-email candidate; HTTPS TLS validation fails, HTTP returns a 163-byte empty hosting redirect. No orgnr/name/contact evidence. Its .com redirects to unrelated Cristty. Remains withheld.

## Harness correction

The old code already used production safe_transport and trust_env=False. The restricted process reproduces ConnectError on known-good sites with a nested PermissionError WinError 5 / errno 13. The identical transport in a network-authorized process returned 200 on five known-good URLs. Historical requests lacked exception chains, so not every individual old failure can be retrospectively assigned, but their near-uniform results cannot be used as website-quality evidence. [Authorized five-URL check](preflight-authorized.json), [fail-fast restricted check](preflight-restricted.json). No proxy/TLS/DNS/SSRF policy was changed.

The replacement measurement harness records cause chains, stops on permission-denied preflight, uses real saved registry evidence rather than `{}`, preserves original consumed budgets, snapshots baseline counts before mutation and applies existing final guards across the whole cohort. Script: [probe.py](probe.py); [measure.py](measure.py). Network access must be authorized by the execution environment; this is not something a transport flag can safely bypass.

## Final production change

Only web/names.py changes production behavior. A comparison-only repair permits omission of the terminal trading descriptor FORRETNING before AS when the page has the exact sole subject orgnr in publisher/header/footer context, the exact shortened name in both footer and title (or a complete title component), the same AS legal form and no other registered company matching that shortened name in the complete official BRREG universe. A missing/corrupt universe index withholds the repair. Registry facts are never rewritten. No article/customer orgnr or name-only match authorizes it. Conflicting copyright owner, foreign/multiple publisher IDs, different legal form, group/shared-domain and existing final/cohort/universe guards still apply. No cap/budget change and no verifier/validator/test weakening.

The redirect-target expansion was tested with full proof/vetoes and then removed. The initial full trial queried 62 candidate/company-domain pairs across 58 companies, spent 444 extra HTTP and 234.812 s, and recovered zero sites. A subsequent combined trial with the completed publisher-name repair produced only HAUGEL (no redirect-origin recovery). Neither trial is the final cost. The committed collector remains unchanged; no redirect expansion or new subpage path is shipped.

## Final measurements — affected candidates only

Each final run starts from saved Stage AM envelopes, fetches only the affected publisher candidate live and preserves baseline pooled/per-company HTTP usage. There is one affected company in both cohorts. INDIGOBOOM and MARUN receive no final recovery fetch. Normal robots, pacing, TLS, DNS and request caps remain in force. Existing proof-page fetching accounts for all seven additional HTTP requests, including robots/redirects. A new full all-source run was not performed.

| Metric | Sample100 | Frozen 1,000 |
|---|---:|---:|
| Verified sites | 13 → 14 | 110 → 111 |
| Brand claims | 3 → 3 | 19 → 19 |
| Social companies | 6 → 6 | 60 → 60 |
| News companies | 4 → 4 | 30 → 30 |
| Social claims | 10 → 10 | 123 → 123 |
| News claims | 9 → 9 | 109 → 109 |
| Extra HTTP | 7 | 7 |
| Total HTTP including saved usage | 1337/1900 | 11462/19000 |
| Maximum total per-company HTTP | 40 | 40 |
| Isolated addition / final-guard wall seconds | 43.980 | 97.470 |

Wall measurements include live affected-candidate work and final publication guards; loading/serialising/verifying the entire saved cohort is separately included in total_replay_seconds. These are standalone measured addition stages, not a causal paired whole-live-run wall-time delta. Different memory/network/host conditions affect elapsed time even for the same seven HTTP requests. No projected whole-run speed claim is made.

Both strict verifiers pass schema, hashes, verbatim evidence, citations and synthesis with **zero unverified values**. Full: 178636 published claims; sample: 18059.

## Ownership hand-review

**Only one new site exists, so ten new-site hand-checks cannot be supplied. Every new site was checked.** [Full recovered claim/citation and nine explicitly withheld control reviews](ownership-review.json). The controls are not claimed as new sites.

HAUGESUND ELEKTRISKE FORRETNING AS (912492575): `https://www.haugel.no`, proof type `orgnr_on_page`, source `https://www.haugel.no/`. The exact orgnr is in its publisher footer beside the shortened company name, matching registered Skjoldavegen 121 / 5519 HAUGESUND and phone 52717711. The footer ID is the sole publisher identifier; the official registry universe has no different company registered as Haugesund Elektriske AS. Same-page publisher context and independent contacts distinguish this from a customer/project mention. All final guards retain it. No precision-doubtful candidate was published.

Withheld controls: MARUN (empty hosting/unrelated Cristty), VISTNES (Randaberg Regnskap publisher), BNTV (Wemail publisher), ARENA HOLDING and TEROB (HugeDomains), ZM DRIFT (parked Webhuset), GREEN4YOU (HugeDomains), INVENSYS (global Schneider page lacks exact Norwegian subject proof), SUPPLYSYNC (Mixo platform publisher). Their retained diagnostics explain why the redirect expansion was discarded.

## Verification and tests

Final full suite: **1815 passed, 1 warning in 479.34s (0:07:59)**. Baseline was 1,806 tests; nine new focused cases cover exact publisher orgnr, foreign/multiple/missing numbers, another registered company, unavailable universe, legal-form conflicts, conflicting copyright and service-page title components. No existing test was edited.

An earlier suite with the subsequently discarded redirect trial had 1,822 passed and a timing failure in test_deadline_partial_progress (3.063 s against <3 s) while concurrent live work ran. That failure is retained in the audit trail; no deadline/test rule was changed. The intermediate final suite was interrupted when redirect trial code was removed; the result above is the completed final-source suite.

No raw pages, bench/runs, caches or pytest temp directories are staged. No push.
