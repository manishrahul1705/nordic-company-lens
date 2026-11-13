# Stage D.1 additive careers trial

**Gate failed; trial not retained or merged.** Articles recovered to69, but careers errors returned at the unchanged40/company ceiling. The unused global pool cannot override that local ceiling. Recommend dropping the careers earmark entirely rather than displacing activity; no further behavioral change was made without a passing gate.

Trial change: removed the deduction of careers_reserves from activity's existing company_cap. The same six-slot target,19/input pool, HR Manager support, post-primary ordering, all time caps and all precision rules were retained. No reserve target was lowered. The updated test verifies activity can consume its original allowance and careers can add requests only within remaining local/global headroom. Full suite:1391passed,0failed659.80s. runtime.patch and trial-tests.patch preserve the tested trial; runtime changes and test/readme changes were restored to Stage D after the failed gate.

Frozen1000 README command, fresh state, credentials stripped, input SHA7ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782. Exit0,1000envelopes/1000profiles, offline site generated. execution.json records base60af47a; the live run used the uncommitted trial patch. Raw outputs remain ignored at bench/runs/stage-d1-live.

| Metric | Stage D | D.1 trial | Difference |
|---|---:|---:|---:|
| Websites | 113 | 113 | +0 |
| Social companies | 47 | 47 | +0 |
| Jobs companies | 2 | 2 | +0 |
| Activity companies | 1000 | 1000 | +0 |
| News companies | 7 | 7 | +0 |
| Article claims | 62 | 69 | +7 |
| Facts | 165471 | 165479 | +8 |
| HTTP total | 9130 | 9193 | +63 |
| HTTP mean | 9.13 | 9.193 | +0.063 |
| HTTP max attributed | 40 | 40 | +0 |
| Wall seconds | 930.541 | 1286.574 | +356.033 |
| Seconds per100 | 93.054 | 128.657 | +35.603 |
| Careers errors | 0 | 4 | +4 |
| Deadline hits | 0 | 0 | +0 |

No warnings. Pool9193<=19000; every company<=40. Wall-time difference includes live network/host/site-generation variation and is not isolated causal evidence.

| proof_type | Websites |
|---|---:|
| orgnr_on_page | 38 |
| jsonld_vatid | 5 |
| registry_declared_name_tier_a | 25 |
| legal_name_without_suffix_and_two_contacts | 9 |
| legal_name_and_registry_contact | 24 |
| unique_no_corroborated | 7 |
| registry_declared_hard_contact_tier_b | 3 |
| registry_phone_on_site | 2 |

## Gate and diagnosis

PASS articles69, websites113, jobs2, deadlines0. **FAIL careers errors0: actual4.** Askoy24(923998012), Skogli Helse og Rehabiliteringssenter(980973549), Tensio(922828172), Bridge Technologies(987002808) each used40 attributed requests before careers could complete. Exact names, errors and checked URLs in careers-errors.json. Company-site funnel37candidates ->30fetched ->0accepted ->0kept; two published jobs remain NAV. Careers failures remain visible, not renamed or suppressed.

No new company website and no new job. One same-domain Closva host alias changed back to www; exact org936629466 owner proof remains in new-items.json. No acceptance rule changed.

The requested zero-careers-errors gate cannot be promised merely from pooled headroom when activity uses the immutable per-company40 ceiling. Articles did recover, so the article-recovery condition itself is satisfied; the separate careers gate prevents retention. Recommendation: drop the earmark, keep19/input, preserve original activity allowance and report any truly incomplete careers coverage honestly. A different allocation or source optimization would need a separate authorized, benchmarked change.

No merge: existing main stayscb51ff6bfa280c5603e06fb3832130f5b6cd8451 in the same bench/cache/stage-a-main clone. No push. Only measurement scripts/reports and this failed-trial log are committed; production behavior is restored to Stage D.
