# S6 Step 19 - saved-evidence coverage audit

**Stopped after the audit at the user's instruction.** Starting commit `7ca9ec7a2adef2b672e9c932a5a48433f0037516`; saved run `20261107T055939048854Z-f02417b`. Search OFF. No live requests, runtime changes, tests, benchmark or push were made for Step 19.

## Counts

| Audit item | Companies / result | Decision |
|---|---:|---|
| Exact-employer/subunit NAV ad homepage not already nominated | 0 companies | Skip |
| Registered subunit homepage not already nominated | 2 companies; 3 homepage records | Below the three-company cutoff; skip |
| Failed strong candidates after excluding access vetoes | 8 companies | 7 NXDOMAIN, 1 timeout; do not build retry |
| Transient timeout opportunity within that group | 1 company | Expected gain at most one; below threshold |
| Verified company site with an ATS-backed careers board | 1 company | Below cutoff; skip |
| Additional company linking to individual FINN job ads | 1 company | Not an ATS board; even combined with the ATS company remains below three |
| NAV forward-feed pages read / available to the saved cursor chain | 8 / 8, recorded complete | No incomplete feed observed |
| Registered subunit organisation numbers in exact matching scope | 823 | Existing matcher already includes them |
| Bundled-index ads matching parent or registered-subunit scope | 3 | All 3 have saved live detail checks; 0 unmatched |
| Distinct saved live NAV detail records | 8 | Includes non-matching employers and inactive candidates; not 8 published ads |

The unfiltered company union is 10 after removing the robots-access veto. The eight-company strong-failure group initially met the numerical group-size cutoff, but seven are NXDOMAIN. Under the user's stop instruction, only one is a plausible longer-timeout recovery, so no lever proceeds. No code was built before the stop.

## Strong-candidate findings

| Company | Orgnr | Strong domain | Saved result |
|---|---|---|---|
| EMAGINE AS | 999536999 | prodataconsult.no | no_such_domain |
| FAST FOOD SERVICE NORGE AS | 981130243 | ffs.no | website_timeout |
| APPSONITE MUSIC AND APPS AS | 997806425 | appsonite.com | no_such_domain |
| NOVA HOUSING AS | 899100492 | smallprint.no | no_such_domain |
| MODULBRYGGEN AS | 921366086 | modulbryggen.no | no_such_domain |
| PROPEL AS | 995612461 | propel.no | no_such_domain |
| BALSFJORD NÆRINGSUTVIKLING AS | 824357552 | balsfjordnu.no | no_such_domain |
| VETERINÆR HEGE FALCK-ANDERSEN AS | 890688012 | hegedyrlege.no | no_such_domain |

REIDARS TRAFIKKSKOLE AS / 916774028 (`reidarstrafikkskole.no`) was initially included by the broad robots-unavailable diagnostic. Its actual robots response was **HTTP 403**, so it is excluded as an access veto. Nothing bypasses or weakens robots policy.

## Homepage and applicant-system findings

The two subunit-homepage companies are PERMOBIL AS / 930239070 (`permobil.no`, subunit 971964855) and SAGA REGNSKAP OG R?DGIVNING AS / 939725709 (`sagaservices.no/sandefjord` and `/skien`, subunits 994022717 and 873992972). These are nominations only, not newly verified websites; existing group/shared/foreign-publisher vetoes would still apply.

SAGA has a Teamtailor-backed board at `https://team.sagarr.no/`. The saved run already checked the board, its jobs list and three individual postings among six careers requests, publishing zero site jobs. Its careers coverage remained incomplete after the six-page budget; no claim that there were no active ads is made. Employee-login and Teamtailor vendor-credit links are not public job boards or ads. LEFDAL INSTALLASJON AS / 968545337 links to two individual FINN ads; this is one additional employer, not three companies. Lofotposten's Amedia careers link belongs to a group, while the other external career-looking links are training information or cookie controls. None establishes an exact-company ACTIVE job.

## NAV completeness and evidence limits

The recorded NAV metrics show a complete eight-page forward refresh from the bundled index cursor, 6,472 feed items, 11 live detail requests for eight distinct saved responses, no unchecked-candidate companies and no cap hit. The bundled index contains 8,554 declarations. Independent exact-org lookup across the 1,000 parents and their 823 registered subunits finds three matching indexed ads, all checked in the saved details. No missing exact-subunit match was found. This does not assert that every NAV ad in existence or every unknown trading name was discovered.

Raw forward-feed page bodies were not retained, so the eight-page completeness statement is supported by the recorded metrics and successful request chain, not a fresh replay of the feed bodies. The index does not contain employer-homepage fields; the homepage audit uses the saved live ad details with exact employer/subunit matches. Existing candidate nomination and subunit matching are already implemented.

One successful company-page response body is absent from the saved state: `https://www.nordicsmarthouse.no/aktuelt`, SHA-256 `7eaa2587a8e9f068ba4d609e50e678d58b39b416c85c7665f7e8677a3501475a`. Its links cannot be re-reviewed from that body. The audit records the gap rather than inventing a zero; even one additional ATS company from this missing page would leave the observed ATS opportunity below three. No replacement crawl was made. Available retained bodies used in the audit were SHA-256 checked.

[Detailed counts, candidates, saved NAV metrics and source hashes](audit.json). [External careers-link classifications](external-careers-links.json).

## Conclusion

**no lever above threshold, no runtime change**

No retry implementation, proof/veto change, benchmark or push. Audit committed as Manish Rahul <manishrahul1705@gmail.com>.
