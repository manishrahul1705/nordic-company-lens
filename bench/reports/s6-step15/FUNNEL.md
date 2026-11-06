# Step15 pre-code funnel audit

One mutually exclusive first unsatisfied gate per company, evaluated across all saved candidates rather than stopping at the first guessed domain. No candidates -> nomination loss. Explicit request cap -> budget loss. A parsed candidate without a terminal policy veto -> proof loss. Only rejected candidates/policy veto -> veto. Otherwise robots, non-DNS fetch failure, or DNS-only failure. Mixed-candidate companies are classified by the furthest candidate reaching a gate; a failed early guess does not hide a later fetched candidate.

| First loss point | Companies |
|---|---:|
| no candidate | 184 |
| DNS fail | 381 |
| fetch fail or timeout | 45 |
| robots | 21 |
| fetched but no proof | 103 |
| vetoed | 160 |
| budget exhausted | 1 |

Total without website: 895; verified:105. Stop-condition groups combined:287 (threshold60). HTTP total6819, attributedmean6.779, amortizedmean6.819 including40sharedcalls, max40. Globalcap18average/40company respected. Saved evidence only; no crawl or runtime code change before reporting this audit.

Final evidence reconciliation: four explicit final group-site vetoes had initially been counted as proof losses despite candidate-stage acceptance. Corrected counts are99fetched/no-proof and164vetoed; all other buckets unchanged, gate283stillpasses. The separately requested160-company primary-veto breakdown/review retains its original subset. See funnel-final-guard-correction.json for all four identifiers.
