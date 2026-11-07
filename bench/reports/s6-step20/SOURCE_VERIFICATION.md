# Official source verification before implementation

Search engines OFF; only explicitly requested official URLs/APIs used, with no credentials, keys, registration or runtime integration during verification. Starting commit 1627e59c684c2f049ead6c7232d0f03ccb7a3bb2.

| Source | Official owner / reuse | Access and exact match | Decision |
|---|---|---|---|
| GLEIF | Global Legal Entity Identifier Foundation; LEI reference data under CC0 1.0; https://www.gleif.org/en/meta/lei-data-terms-of-use | Anonymous HTTPS API. robots.txt: User-agent *, empty Disallow. Exact entity.registeredAs plus entity.registeredAt=RA000472, checked again in every returned record. Authority endpoint identifies Foretaksregisteret / Bronnoysund Register Centre. | PASS: 32 exact matches in frozen1000 |
| TED | Publications Office of the European Union; procurement notices freely reusable commercially/noncommercially under its legal notice https://ted.europa.eu/en/legal-notice | Official documentation explicitly permits anonymous published-notice queries: https://docs.ted.europa.eu/api/latest/search.html. POST https://api.ted.europa.eu/v3/notices/search; winner-identifier/buyer-identifier and award-only can-standard/can-social supported. API robots 404; ted.europa.eu robots permits public notice XML (private dashboards/internal paths disallowed). Exact XML organisation ID plus winner/buyer role, not names or keyword hits. | PASS; only XML-proven exact award links may publish |
| Doffin | DF?-operated official site; robots allows access | Documented no-key endpoint/clear API reuse terms could not be established. Public app references webclient endpoints but guessed official endpoints returned404. No embedded app key was extracted or used. | DROP: access/terms not sufficiently verified; no scraping fallback |

## Ten benchmark orgnrs, same seeded sample for both APIs

GLEIF batch returned data=[]; TED exact winner/buyer batch returned notices=[], totalNoticeCount=0. These are genuine empty results, not proof of source failure. No company-name matching was used.

| Orgnr | GLEIF exact matches | TED exact notice matches |
|---|---:|---:|
| 922187991 | 0 | 0 |
| 923883819 | 0 | 0 |
| 931338900 | 0 | 0 |
| 928066193 | 0 | 0 |
| 935268796 | 0 | 0 |
| 829363712 | 0 | 0 |
| 918640967 | 0 | 0 |
| 933270610 | 0 | 0 |
| 933001776 | 0 | 0 |
| 936544525 | 0 | 0 |

GLEIF positive control: TENSIO AS / 922828172 returns LEI9845006E55BAA3EWD760, statusACTIVE, legal-formYI42, RA000472, registration2019-12-13 and renewal2027-05-24. Exact 100-orgnr batches over the frozen1000 yield **32 matched companies**, exceeding the 15-company combined threshold without relying on procurement. Filter entity.registeredAt.id was rejected400; the verified API key is filter[entity.registeredAt]. Comma-separated registeredAs values and comma-separated filter[lei] parent lookups were positively tested. No silent unsupported filter is used.

All fields returned include LEI, entity.registeredAs/registeredAt, legal name/status/form, registration.initialRegistrationDate/lastUpdateDate/nextRenewalDate, and explicit relationship/reporting-exception links. Two companies have three explicit direct/ultimate relationship edges. Parent publication requires an ACTIVE returned relationship with matching child and parent LEIs; parent records are deduplicated and batched by returned LEI, with every request charged to the pooled budget. Foreign parent registration IDs are never labelled Norwegian orgnrs; parent orgnr is included only when its own authority is RA000472. Reporting exceptions are not parents.

TED exact-ID cohort queries returned 124 notice rows (including duplicates and non-awards): 74 can-standard, one can-social and other notice types excluded from publication. The tested award-only predicate is notice-type=(can-standard OR can-social). Example official XML https://ted.europa.eu/en/notice/116542-2024/xml contains organisation national IDs, buyer references, tendering-party references and settled contracts with award dates. Publication must follow these links, not assign a notice-wide total value to an unrelated winner. A missing award date or unlinked party is an abstention. Doffin is not needed because TED passed official anonymous-access verification.

API rules: TED anonymous schema limits page sizes/returned fields (250 scroll or pagination notices, field count10000); this implementation will use <=100 notices/page and small fields, complete bounded pagination, fixed official URLs and no authenticated publishing APIs. GLEIF will use <=100 exact input IDs per batch and <=200 records/page. Requests remain bounded by the existing global budget; no source failure may crash a company.

Raw tested responses, official API schema, robots, exact cohort queries and returned records: [source-verification/](source-verification/). GLEIF documentation: https://www.gleif.org/en/lei-data/gleif-api ; TED schema: https://api.ted.europa.eu/api-v3.yaml .
