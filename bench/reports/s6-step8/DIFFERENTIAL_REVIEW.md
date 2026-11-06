# Differential website and social review

Compared Step 7's 79 website / 33 social output (`1fe27a0`) with benchmark 2 at `1909653`. Manually checked every new or changed item using its captured claim evidence and exact company name. The website changes below were verified by the stated own-orgnr proof or the named legal entity plus registry contact; each new social URL is directly linked from that verified website.

| Company (org nr) | Changed item | Captured proof / link evidence | Verdict |
|---|---|---|---|
| CONTROL SOLUTIONS AS (926490060) | Website `control-solutions.no`; Facebook `ControlSolutionsAS`; Instagram `control_solution_as` | Homepage says `Org.nr 926 490 060`; both social URLs are homepage links | Correct |
| CONPLAN AS (987895276) | Website `conplan.no`; Facebook `Conplan-AS-509721459118772` | Page names Conplan AS; registry-matched address/contact proof; Facebook URL is linked on page | Correct |
| Fusa Mekaniske Industri AS (811888672) | Website `fusamek.no`; Facebook `fusamek` | Page names company; registry contact/address proof; Facebook URL linked on site | Correct |
| 7OCEAN HOLDING AS (999530095) | Website `7ocean.no` | Page says “7ocean Holding AS” and describes its own group management function; candidate is its registry website; proof does not identify another owner | Correct for the holding company |
| THE LAB RETRIEVER AS (926065173) | Website `thelabretriever.com`; Facebook and Instagram | Privacy page names The Lab Retriever AS and registered address; both social URLs linked from homepage | Correct |
| STIFTINGA MUSEUMSSENTERET I HORDALAND (971349743) | Website `muho.no` | Shared site, but proof page explicitly says org nr 971349743 and Museumssenteret i Hordaland | Correct; exact own org nr |
| NUVE AS (936094112) | Website authority changed to `www.nuve.no` | Homepage says `Nuve AS · Org.nr 936 094 112`; same company and proof as Step 7 | Correct; www authority variation |
| NASJONALT SENTER FOR NORDLANDSHEST /LYNGSHEST AS (952785052) | Website upgraded from `http://www.nsnl.no` to HTTPS | Page says `Org.nr.: 952 785 052`; same company and proof as Step 7 | Correct; scheme upgrade |
| NERLAND AUTOSALG AS (951734543) | Step 7 website and two linked social profiles are absent in benchmark 2 | No Step 8 website refresh record was emitted for this org; no evidence supports calling it a DNS/transient failure | Unresolved availability loss; no item is published in Step 8 |
| WULLUM EIENDOM AS (818807562) | Step 7 website `wullumeiendom.no` is withheld | Group/shared-site reason; page had company name and address but no own org nr or registry phone/email | Correctly withheld under Step 8 precision rule |

Counts: 8 new/changed websites (including two authority/scheme updates), 6 new social links, 1 prior website plus its 2 social links absent, and 1 group website withheld. Manual review found 0 wrong-company items among the Step 8 additions/updates. The third benchmark will be compared separately to distinguish run-to-run variation.

## Final-code run-to-run review (benchmark 2 vs 3)

Both full-fallback runs had 83 websites and zero wrong-company findings. Reviewed every website/social difference between their saved claims:

| Company (org nr) | Run-to-run item | Evidence / classification | Verdict |
|---|---|---|---|
| TB MASKIN AS (990012288) | `tbmaskin.no` → `www.tbmaskin.no` | Registry lists `www.tbmaskin.no`; page proof matched legal name, address and phone | Correct authority variation |
| NERLAND AUTOSALG AS (951734543) | Website and two social links return in run 3 | `dodge.no` page names Nerland Autosalg AS and its address; Facebook and Instagram are linked from the verified site | Correct; run 2 had no website record |
| SKAUEN KRISTELIGE SKOLE (977456436) | `delk.no` website appears in run 3 | Proof page has `Org.nr. 977 456 436`; exact school identifier on shared denomination site | Correct; own org nr is explicit |
| NUVE AS (936094112) | `www.nuve.no` → `nuve.no` | Both pages identify Nuve AS, org nr 936 094 112 | Correct authority variation |
| ENSURE IT AS (934620011) | Previously available website absent in run 3 | Candidate diagnostics show `ensure-it.eu` DNS timeout and other candidates `dns_unavailable` | Transient DNS; not a precision rejection |
| STØREN DYREKLINIKK AS (993014591) | Previously available website absent in run 3 | Candidate diagnostics show `dns_unavailable` for the nominated and name candidates | Transient DNS; not a precision rejection |

Run-to-run social section coverage changed by one company (36 to 37); the social noise band is four. The three newly available website/social claims above were manually reviewed and correct; the two absences are traced to DNS failures. No website-count difference and 0 wrong-company findings.
