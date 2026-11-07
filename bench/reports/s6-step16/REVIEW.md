# Step 16 raw-source precision review

40 stratified random new claims, seed 20261107; 10 per family and distinct companies within each family. Category coverage includes rare new fields before random filling. Each stored source body and exact locator was opened; CSV values were checked against header/row mapping, not merely a repeated value in the excerpt. JSON owner/parent scope and all sampled account periods/types were checked.

**40 correct; 0 wrong values; 0 wrong periods.** No sample was dropped or replaced. Automated hash/span/value checks are recorded separately from these manual verdicts.

| # | Org / family | Field label | Fiscal scope | Verdict | Manual finding |
|---:|---|---|---|---|---|
| 1 | 921108249 / identity | Business address country code | not annual accounts | correct | Business country NO matches the business-address column, not the postal address. |
| 2 | 924828099 / identity | Former registered name | not annual accounts | correct | ECOFRIC historical name UN17 CONSULT AS and both 2020 boundaries match this exact orgnr; not a different company. |
| 3 | 998138558 / identity | Postal address country code | not annual accounts | correct | Postal country NO copied separately from the business address. |
| 4 | 995516926 / identity | Registry annotations | not annual accounts | correct | Explicit paategninger=false in the selected CSV column; no missing flag default. |
| 5 | 919931477 / identity | Voluntary VAT registration descriptions | not annual accounts | correct | Exact voluntary-VAT rental description retained; no broader VAT conclusion. |
| 6 | 934929187 / identity | Business address country code | not annual accounts | correct | Business-address country NO at the selected row/column. |
| 7 | 998407257 / identity | Business address country code | not annual accounts | correct | Business-address country NO; no website ownership inference. |
| 8 | 929207157 / identity | Registry annotations | not annual accounts | correct | Explicit registry-annotation flag false; not inferred from missing data. |
| 9 | 971173459 / identity | Business address country code | not annual accounts | correct | Business country NO; the c/o address is not interpreted as a workplace. |
| 10 | 983478999 / identity | Business address country code | not annual accounts | correct | Business country NO for this association, not an inferred operating location. |
| 11 | 922661650 / roles | Birth year | not annual accounts | correct | Knut-Arvid Hellerud, MEDL: 1992 is exactly the year of 1992-03-01. |
| 12 | 921634544 / roles | Registered insolvency administrator | not annual accounts | correct | Adv. Per Ove S?rholt and professional postal address are the registered administrator; not a company workplace. |
| 13 | 979354843 / roles | Registered as deceased | not annual accounts | correct | Rune Lutdal: erDoed=false retained as a registry flag, not an independent life-status investigation. |
| 14 | 952049070 / roles | Birth year | not annual accounts | correct | Harald Otto Osvold, LEDE: 1943 copied from 1943-01-19. |
| 15 | 981508734 / roles | Registered as deceased | not annual accounts | correct | Elisabeth Mar?k St?le: exact false erDoed flag on the selected member record. |
| 16 | 992068434 / roles | Birth year | not annual accounts | correct | Per Arne Jensen, LEDE: 1964 copied from 1964-12-05. |
| 17 | 998349532 / roles | Registered as deceased | not annual accounts | correct | Ola Kellerhals: exact false erDoed flag; no additional role assertion. |
| 18 | 889806192 / roles | Registered as deceased | not annual accounts | correct | Alf Bernt Brekken: erDoed=false is independent of avregistrert=true; no active-director claim added. |
| 19 | 913772431 / roles | Birth year | not annual accounts | correct | Kari Stautland, LEDE: 1960 copied from 1960-07-20. |
| 20 | 995372614 / roles | Registered as deceased | not annual accounts | correct | Arvid Hellesund: exact false erDoed flag from the selected member. |
| 21 | 985204381 / subunits | Former registered name | not annual accounts | correct | ELVEKRAFT AS 2009?2013 is a former name of subunit 985461678, not a historical parent-company assertion. |
| 22 | 980973549 / subunits | Secondary registered industry | not annual accounts | correct | Skogli subunit secondary NACE 55.100/hotel operations is explicitly naeringskode2, not replacement of the primary industry. |
| 23 | 915042759 / subunits | Former registered name | not annual accounts | correct | AHIDANE'S INTERI?R AS and 2015?2024 boundaries belong to subunit 915056415. |
| 24 | 929942167 / subunits | Former registered name | not annual accounts | correct | PALETTEN KINA RESTAURANT and 2008?2015 boundaries belong to subunit 985769915. |
| 25 | 916774028 / subunits | Former registered name | not annual accounts | correct | REIDARS TRAFIKKSKOLE AS and 2012?2016 boundaries belong to subunit 989964631. |
| 26 | 997790952 / subunits | Former registered name | not annual accounts | correct | JOHANNESSEN EIENDOMSUTVIKLING AS and 2012?2013 boundaries belong to subunit 997865456. |
| 27 | 926624717 / subunits | Former registered name | not annual accounts | correct | SHADOWMAKER BJ?RN SOLHEIM and 2020?2021 boundaries belong to subunit 925032247. |
| 28 | 993372277 / subunits | Former registered name | not annual accounts | correct | MONSTAD JOHANNES REKNESKAPSKONTOR and 1995?2008 boundaries belong to subunit 972222720. |
| 29 | 822291082 / subunits | Former registered name | not annual accounts | correct | CASA DI SAGA AS and 2019?July 2026 boundaries belong to subunit 922537607; not an invented rename event. |
| 30 | 990800480 / subunits | Former registered name | not annual accounts | correct | BERGMOEN SNEKKERVERKSTED ANS and 1995?2007 boundaries belong to subunit 971665009. |
| 31 | 991450084 / accounts | Company tax on extraordinary items | SELSKAP / 2023 | correct | Explicit 0.00 extraordinary-tax amount for SELSKAP FY2023, not a missing-value zero; scale remains undeclared. |
| 32 | 922828172 / accounts | Consolidated parent company | KONSERN / 2023 | correct | KONSERN FY2023 morselskap=true for exact orgnr 922828172; kept outside company-only records. |
| 33 | 928350193 / accounts | Company account type | SELSKAP / 2023 | correct | SELSKAP type from the 2023 statement for exact orgnr 928350193. |
| 34 | 984597665 / accounts | Company period start | SELSKAP / 2025 | correct | FY2025 start 2025-01-01 at index 2, with matching 2025-12-31 end. |
| 35 | 934012674 / accounts | Company period start | SELSKAP / 2025 | correct | FY2025 start 2025-01-01 at index 1, with matching 2025-12-31 end. |
| 36 | 964898278 / accounts | Company audit opt out | SELSKAP / 2025 | correct | FY2025 fravalgRevisjon=false at index 3; no audited=true inference. |
| 37 | 921368348 / accounts | Company parent company | SELSKAP / 2025 | correct | FY2025 morselskap=false copied directly; no inferred group structure. |
| 38 | 889806192 / accounts | Company period start | SELSKAP / 2024 | correct | FY2024 start 2024-01-01 at index 1, not mislabeled as the latest year. |
| 39 | 986739874 / accounts | Company presentation plan | SELSKAP / 2023 | correct | FY2023 presentation-plan code store copied verbatim; not interpreted as business activity. |
| 40 | 988384828 / accounts | Company account type | SELSKAP / 2023 | correct | SELSKAP type from the 2023 statement for exact orgnr 988384828. |

Full values, excerpts, URLs, checked dates, locators, periods and source SHA-256: [review-sample.json](review-sample.json). Birth-year extraction is exact date-component selection, not a guessed age. No hidden employee range occurred in the real sample; explicit-range and no-inference cases are covered by tests. Consolidated scale is left undeclared when the source has no unit; no new multiplier or audited status is inferred.

## Supplementary checks

Two additional randomly selected consolidated amounts were inspected: org988810029 FY2025 pre-tax result8754895.00; org968545337 FY2024 inventories1330889.00. Both are KONSERN, with correct exact-parent orgnr/year; no unit multiplier is inferred. The two additional activity URLs are existing-crawler Tensio articles dated2026-02-02 and2026-01-28; article-side datePublished matches, with no dateModified substitution. These explain the live activity-claim increase of2, not a new fact-depth source or discovery rule. All4 supplementary items are correct. [Full supplemental proof](supplemental-review.json).
