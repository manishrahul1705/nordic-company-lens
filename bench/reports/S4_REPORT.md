# S4 benchmark and precision gates

Target not achieved: final accepted website coverage is 8/100, below 25/100. A and B were retained. C and D were reverted under the required zero-wrong-company gate. No pushes.

| Fix | Commit | Decision | Website | Social | Jobs | Activity | Website budget errors | Seconds | HTTP | Tests | Opened/wrong |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| A | `a1aca18` | KEEP | 8 | 4 | 1 | 29 | 27 | 49.994 | 612 | 713 | 10/0 |
| B | `6fe34a3` | KEEP | 8 | 4 | 1 | 29 | 29 | 60.139 | 621 | 727 | 4/0 |
| C | `6085648` | ROLLED BACK | 10 | 7 | 1 | 29 | 22 | 53.378 | 619 | 737 | 6/1 |
| D | `e54da86` | ROLLED BACK | 9 | 5 | 1 | 29 | 8 | 57.891 | 784 | 727 | 2/1 |

All trials emitted 100 envelopes and exited 0, with zero deadline hits and no warnings. Identity/people/locations/financials remained 100/100/85/100. Accepted code final test count: 727. Trial artifacts preserve raw outputs, source blobs and precision-review.json.

A removed all ten baseline website-news claims because each used sitemap lastmod and a URL-derived title without fetched article proof. Activity available fell 30 to 29; all 70 registry event facts remained. No website-news items were kept; ten kept registry activity source records were opened and validated against exact company/subunit IDs. Full removed-item list is in IMPROVEMENT_LOG.md and A/precision-review.json.

B opened all four changed website items, whose exact organisation numbers occur in footer/privacy source bodies. No new social/news items. Coverage stayed flat; budget errors rose 27 to 29.

C opened all six changed items. New exact-company sites were Rolidbakken FUS (991247610), Stoa Autorep (920918204) and KN Elektro (823147112); Stoa and KN had full legal name plus independently matched registry contacts. However https://fus.no/rolidbakken published https://www.facebook.com/Diseth-FUS-barnehage-As-1287226694698749 for Rolidbakken. Its registered subunit is 931166492, also Rolidbakken. The page links a different nursery profile. The whole fix was reverted.

D opened both new items and exposed the same Diseth social mismatch. Despite reducing website budget errors to 8, it was reverted. The budgets remain 6/9. Fixing social attribution is required before safely retaining either coverage trial; no unrequested social fix was made.

## Final Windows 1000-company run

Commit `9fa975e`; exit 0; 1000 envelopes; 311.321s / 2400s (12.97%), HTTP 5676, deadline hits 0, website budget errors 312, warnings [].

| Section | Available | Not available | Failed | Ambiguous | Blocked | Budget | Deadline | Facts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| identity | 1000 | 0 | 0 | 0 | 0 | 0 | 0 | 28737 |
| people | 998 | 2 | 0 | 0 | 0 | 0 | 0 | 11813 |
| locations | 774 | 226 | 0 | 0 | 0 | 0 | 0 | 6527 |
| financials | 999 | 0 | 1 | 0 | 0 | 0 | 0 | 62584 |
| website | 52 | 592 | 277 | 76 | 3 | 0 | 0 | 390 |
| social | 27 | 617 | 277 | 76 | 3 | 0 | 0 | 53 |
| jobs | 3 | 994 | 3 | 0 | 0 | 0 | 0 | 3 |
| news/activity | 230 | 473 | 297 | 0 | 0 | 0 | 0 | 596 |

The final run measures accepted code, not the rejected 14/18 trial. Raw accounts errors and HTTP responses are preserved in scale-diagnosis.json. Ten changed website source proofs were opened and matched to exact company IDs, with zero wrong-company findings in that sample. This is not a full 1000-company manual audit. Elektrokompetanse was a keyword-auditor false positive: its own footer names Elektrokompetanse AS and organisation 989916319 alongside its own logo. The original automated result and manual resolution are retained in precision-review.json. All 596 registry activity facts match the earlier scale run after equivalent timezone formats are normalized. The 33 removed website-news claims used sitemap lastmod; no new website-news items were retained.

The sole accounts failure remains 926077422, NRP ANAXO NORDIC M2. BRREG returned HTTP 500 on three attempts: `Regnskapet inneholder en oppstillingsplan som ikke er stottet (VPFO)`. There were no accounts 429 responses or transport errors. All original 100 companies still have available accounts; the unsupported VPFO case is outside that cohort. No output-limit reductions occurred.

## Git log

```text
2fa8d80 Manish Rahul <manishrahul1705@gmail.com> Record S4 final scale benchmark and precision gate results
9fa975e Manish Rahul <manishrahul1705@gmail.com> Record budget trial rollback after wrong-company source review
868b612 Manish Rahul <manishrahul1705@gmail.com> Revert "Raise default website request budgets to fourteen and eighteen"
e54da86 Manish Rahul <manishrahul1705@gmail.com> Raise default website request budgets to fourteen and eighteen
cad9485 Manish Rahul <manishrahul1705@gmail.com> Record ownership trial rollback after wrong-company source review
3e6e40c Manish Rahul <manishrahul1705@gmail.com> Revert "Require strict complete website ownership proof"
6085648 Manish Rahul <manishrahul1705@gmail.com> Require strict complete website ownership proof
01093bc Manish Rahul <manishrahul1705@gmail.com> Record candidate benchmark and exact-company source review
6fe34a3 Manish Rahul <manishrahul1705@gmail.com> Expand scoped website candidates and DNS hostname discovery
1dda2db Manish Rahul <manishrahul1705@gmail.com> Record website-news precision benchmark and removed items
a1aca18 Manish Rahul <manishrahul1705@gmail.com> Require fetched article publication proof for website news
```
