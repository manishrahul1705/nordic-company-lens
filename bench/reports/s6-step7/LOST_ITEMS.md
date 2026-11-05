# Step 6 items absent from the Step 7 benchmark

The frozen comparison is `comparison/comparison.json`. A website URL changed (not a missing website claim) for NSNL and Styreguiden; those normalized URL replacements are noted after the loss table.

| Type | Company / orgnr | Step 6 item | Classification | Evidence |
|---|---|---|---|---|
| Website | CONTROL SOLUTIONS AS / 926490060 | https://www.control-solutions.no | transient | Candidate diagnostics show `TimeoutError`, DNS-unavailable and website timeout/retry; no group signal. |
| Website | CONPLAN AS / 987895276 | https://www.conplan.no | transient | Candidate diagnostics show DNS-unavailable and timeouts; no group signal. |
| Website | Fusa Mekaniske Industri AS / 811888672 | https://www.fusamek.no | transient | Candidate diagnostics show website timeout/DNS errors; no group signal. |
| Website | 7OCEAN HOLDING AS / 999530095 | https://www.7ocean.no | transient | Candidate diagnostics show website timeout/DNS errors; no group signal. |
| Website | THE LAB RETRIEVER AS / 926065173 | https://thelabretriever.com | transient | Candidate diagnostics show DNS timeout/unavailable; no group signal. |
| Website | STIFTINGA MUSEUMSSENTERET I HORDALAND / 971349743 | https://muho.no | transient | The website claim itself was absent after DNS timeout. The domain also has an independent other registry owner, but group policy withholds social/activity/descriptions, not the website claim; therefore this loss is attributed to the recorded fetch failure. |
| Social | CONTROL SOLUTIONS AS / 926490060 | Facebook `ControlSolutionsAS` | transient | Same company-site fetch timed out; no group/shared-domain evidence. |
| Social | CONTROL SOLUTIONS AS / 926490060 | Instagram `control_solution_as` | transient | Same company-site fetch timed out; no group/shared-domain evidence. |
| Social | CONPLAN AS / 987895276 | Facebook `Conplan-AS` | transient | Website candidate diagnostics show DNS errors/timeouts; no group/shared-domain evidence. |
| Social | Fusa Mekaniske Industri AS / 811888672 | Facebook `fusamek` | transient | Website candidate diagnostics show timeout/DNS errors; no group/shared-domain evidence. |
| Social | THE LAB RETRIEVER AS / 926065173 | Facebook `The-Lab-Retriever` | transient | Website candidate diagnostics show DNS timeout/unavailable; no group/shared-domain evidence. |
| Social | THE LAB RETRIEVER AS / 926065173 | Instagram `thelabretriever` | transient | Website candidate diagnostics show DNS timeout/unavailable; no group/shared-domain evidence. |
| Social | CNC NORWAY AS / 925310492 | Instagram `cncnorwayas` | correctly withheld | Its own captured contact page names another legal entity and orgnr 920224725; recorded as a group-site relationship. |
| Social | SAGA REGNSKAP OG RÅDGIVNING AS / 939725709 | LinkedIn `sagarr` | correctly withheld | The site domain is independently nominated as the registry website for orgnr 986557113; the claim comes from the shared group site. |

Totals: **14 absent URL-level items** (6 website URLs and 8 social profile URLs): **2 correctly withheld, 12 transient, 0 collateral**. No lost item was classified collateral.

Website URL replacements: NSNL changed from `https://www.nsnl.no` to verified `http://www.nsnl.no`; Styreguiden changed from `https://www.styreguiden.no` to verified `https://styreguiden.no`. Both retain the exact legal entity and are not missing website claims.
