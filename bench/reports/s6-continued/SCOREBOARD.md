# S6 continued - 5 November 2026

All numbers are companies with the section available in the frozen 100-company run. Step 2 shows the rejected trial; rollback restored Step 1 code before Step 3a. Baseline is the fresh run at 6163e09, not the historical handoff. All runs used scripts/bench.ps1 -Size 100, identical frozen input hashes, fresh state, search OFF and stripped NAV/search credentials. Nothing pushed.

| Section / result | Baseline | Step 1 | Step 2 trial | Step 3a | Step 3b |
|---|---:|---:|---:|---:|---:|
| identity | 100 | 100 | 100 | 100 | 100 |
| people | 100 | 100 | 100 | 100 | 100 |
| locations | 85 | 85 | 85 | 85 | 85 |
| financials | 100 | 100 | 100 | 100 | 100 |
| website | 10 | 11 | 9 | 11 | 11 |
| social | 4 | 5 | 5 | 5 | 5 |
| jobs | 1 | 1 | 1 | 1 | 1 |
| news/activity | 29 | 29 | 29 | 29 | 29 |
| Decision | baseline | KEEP | ROLLBACK | KEEP | KEEP |
| Wrong-company items | - | 0 / 8 reviewed claims | 0 / 54 reviewed claims | 0 / 6 reviewed claims | 0 / 4 reviewed claims |
| Tests passed | 823 (prior clean-clone check) | 833 | 833 | 840 | 854 |
| New-rule proof precision | - | no new alias-only profiles | no new site proofs | 1/1 | 1/1 |
| Commit | 6163e09 | 53da26f | 2c5c3df | 7d2fa87 | e97824b |
| Wall seconds | 106.393 | 86.132 | 102.537 | 83.778 | 85.540 |
| HTTP requests | 727 | 740 | 739 | 740 | 741 |

Step 1: KN Elektro recovered from baseline DNS failure. The +1 website/+1 social gain is transport variance, not a demonstrated alias-rule gain. The historical handoff already had 11 websites and 5 social companies.

Step 2: websites fell 11 to 9. INDIGOBOOM exhausted its request budget before trying the .com candidate; Rolidbakken FUS had DNS unavailability. Rolled back despite zero wrong-company findings and passing trial tests. The trial and changed test expectations are preserved in step2/trial.patch; no Step 2 runtime change remains.

Step 3a: INDIGOBOOM changed to suffix-free proof using the legal-name domain, registered street, and postcode/city. Precision is 1/1 on the accepted trial proof in the current 100-company sample, not a general precision estimate. All 21 distinct archived suffix-screen excerpts were read, but their original blobs are absent. Automatic approval review rejected a separate live refresh, citing the earlier no-live-web instruction; no fresh/full-page precision is claimed for that historical sample.

Step 3b: Ralston Bau changed to exact-domain/municipality proof, independently confirmed by its retained contact page and exact organisation number. The homepage municipality is a project location, illustrating the weakness of accepting a location anywhere on the site. Four affected claims were reviewed with no wrong-company finding. No new section coverage from Steps 3a or 3b.

Tests and benchmarks exercised each trial working tree; execution.json records its parent commit and dirty state. The commit row identifies the final tested implementation plus evidence, or the rollback record. Reviews use retained primary-source bodies; successful hash checks do not themselves establish factual accuracy.
