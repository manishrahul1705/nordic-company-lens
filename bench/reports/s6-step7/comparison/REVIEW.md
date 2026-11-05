# Step 7 differential review

Manual review of all 25 newly appearing semantic items from the saved 1000-company trial. Exact company identifiers, captured source text, excerpt, URL and body SHA are in `review-items.json`.

| Company | Items reviewed | Verdict | Basis |
|---|---:|---|---|
| X2 WORKS AS (999329969) | 6 | correct | Website footer prints the exact orgnr; descriptions name X2 Works AS or describe that company. |
| NASJONALT SENTER FOR NORDLANDSHEST /LYNGSHEST AS (952785052) | 2 | correct | Exact orgnr is in the captured address block; the description is an operational notice from its page. |
| RENTHALL AS (980362779) | 13 | correct | Page names Renthall AS and matches registry address; descriptions concern hall rentals and contact values are on the same domain. The page mentions a parent, but no parent identity was attributed as this company. |
| STYREGUIDEN AS (988456292) | 2 | correct | Exact orgnr is printed on the page; description describes Styreguiden's services. |
| WULLUM EIENDOM AS (818807562) | 1 | correct website; group content withheld | Verified company page. The invoice page lists multiple entities, so the group publication boundary suppresses descriptive claims. |
| **Total** | **25** | **0 wrong; 0 unsure** | No item attributes another legal entity to the subject company. |

No new social item appeared in the trial. Separate current website review is in `../OWNERSHIP_REVIEW.md` (83 websites). Three published jobs were individually checked in `../baseline-jobs.json`: all are ACTIVE NAV detail records, and each employer orgnr is a registered subunit of the displayed company.
