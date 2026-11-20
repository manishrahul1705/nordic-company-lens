# Final run accuracy adjudication

200 published claims; seed 20261119. Mechanical verdicts require the unchanged Stage X equality/span/subject-URL check. Remaining items were source-reviewed with context retained in hand-review-support.json. This script rechecks the source corroboration, not the publisher.

| Index | Company | Field | Review |
|---:|---|---|---|
| 42 | 916729774 | accounts.statement.2024.audit_status | Both explicit audit booleans checked for the cited year; fravalgRevisjon=true means audit_opted_out, not audited. |
| 48 | 924825464 | accounts.statement.2023.audit_status | Both explicit audit booleans checked for the cited year; fravalgRevisjon=true means audit_opted_out, not audited. |
| 62 | 928985407 | accounts.statement.2024.audit_status | Both explicit audit booleans checked for the cited year; fravalgRevisjon=true means audit_opted_out, not audited. |
| 96 | 916099630 | accounts.statement.2024.audit_status | Both explicit audit booleans checked for the cited year; fravalgRevisjon=true means audit_opted_out, not audited. |
| 102 | 989232401 | registry_change.0217edd882ca512824980602 | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 103 | 899100492 | registry_change.1b5b73cb8990c1433a656316 | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 104 | 976886534 | registry_change.322faf8f5e9d1428de8ec7b3 | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 105 | 987454709 | registry_change.f2346136e1478a37003be7a0 | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 106 | 936392946 | registry_change.c9b9beabb1143a0858fbad99 | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 107 | 993312479 | registry_change.73fe491094db054f9bcc8a77 | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 108 | 974527197 | registry_change.7601df31987b7cdc55721245 | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 109 | 968545337 | registry_change.3980fa1a56573816a4545c50 | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 110 | 935809207 | registry_change.feaa69f8931b3dc72af3be3c | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 111 | 927529319 | registry_change.2cd2009b59e92936c1be1543 | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 112 | 950220317 | registry_change.21c7cb6a3e4ec18ff62570e0 | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 113 | 965530819 | registry_change.785afeadae02d144787e4499 | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 114 | 997024311 | registry_change.39c376e75abbf381c9c8bbf0 | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 115 | 993312479 | public_brand | Proven company page explicitly names Nordic Smarthouse in title/og:site_name; this is a public brand, not a registry-name substitution. |
| 118 | 960213912 | hiring.job.a3e96411-9639-48cd-a27b-2e5e4406a3e8 | Live NAV page title and employer 972285501 checked; own-company registry lists that subunit under ROSENLUND BARNEHAGE SA. ACTIVE/expiry and occupation/location are retained NAV fields, not parent-name inference. |
| 151 | 983486703 | central_approval.ed0eb935f97e9480bbbdba4d | DiBK enterprise page has exact orgnr; the approval row names Varme- og kuldeinstallasjoner, Prosjekterende, class 2, valid 01.09.2025–01.09.2028; not a no-approval inference. |
| 152 | 925321419 | cleaning_approval.status | Exact main-unit record says Ikke godkjent; approved=false is correct. It is not published as an approval. |
| 153 | 919276843 | news_item.23532c1eefde44057226 | Same RSS item states title, URL and pubDate 13 July 2015; verified website claim binds this feed to the company. It is company-published, not independent reporting or a guessed date. |
| 163 | 935955033 | related_company_website.subsidiary.950271728 | ELLINGSEN own published relationship names subsidiary RANA ENTREPRENØR 950271728; that entity registry row states www.ranaent.no. Both citations retained; not ELLINGSEN official_website. |
| 164 | 984024290 | research.256541 | Forskningsrådet row 256541 names VEIDEKKE as project responsible, Kortreist stein, 4,353,000 total project award, application 2015-10-14 and 2016–2019. No exclusive share or invented currency. |
| 165 | 821962242 | skattefunn.318376 | Approved LAKSESYSTEMER application 318376, 2020–2022 and explicit Excel decision date 2020-09-24. Labelled R&D tax deduction, not a grant/cash payment. |
| 166 | 928502732 | state_aid.1000314987 | Exact aid recipient/id, tax-benefit instrument, award date and amount/range match selected state-aid row. FINNMARK range is EUR 0–499999, not an exact award; specified subunit 915943012 stays explicit. |
| 167 | 915884482 | state_aid.1000015098 | Exact aid recipient/id, tax-benefit instrument, award date and amount/range match selected state-aid row. FINNMARK range is EUR 0–499999, not an exact award; specified subunit 915943012 stays explicit. |
| 168 | 975962121 | workshop_approval.28371 | Exact ÅS GLASSMESTERFORRETNING main-unit orgnr; approval 28371 is BILGLASS at Verpetveien 32, 1540 VESTBY. One approval record, not a second company. |
| 169 | 987909889 | roles.role.6afa4c08258e9956367af96d.0 | Own-company roles record checked: exact role-holder name, role/group type, inactive flag and last-change date. Person is not treated as the researched company. |
| 171 | 990632901 | roles.role.b5bc2ddfe14e0508263a0dac.0 | Own-company roles record checked: exact role-holder name, role/group type, inactive flag and last-change date. Person is not treated as the researched company. |
| 173 | 924784091 | roles.role.704c434131da0c82b6073c02.0 | Own-company roles record checked: exact role-holder name, role/group type, inactive flag and last-change date. Person is not treated as the researched company. |
| 174 | 971521570 | roles.detail.a794e7a6b123feffd379c1f7.0.birth_year | Only year derived from the cited explicit registry birth date; own-company roles URL binds attribution. |
| 177 | 936441440 | roles.detail.1c4be9cff6739eeff0424c33.0.entity_form | Same explicit registry legal-form code/description; API _links metadata is omitted without changing the value. |
| 178 | 919217081 | roles.role.c854e646cd57faaacaf3b7f9.0 | Own-company roles record checked: exact role-holder name, role/group type, inactive flag and last-change date. Person is not treated as the researched company. |
| 183 | 925201049 | roles.role.47ae072ba1e55538816c119e.0 | Own-company roles record checked: exact role-holder name, role/group type, inactive flag and last-change date. Person is not treated as the researched company. |
| 184 | 917283109 | roles.detail.3c228a0ddd63e952341e8549.0.entity_form | Same explicit registry legal-form code/description; API _links metadata is omitted without changing the value. |
| 185 | 936049192 | roles.role.c2b7298f6152eab28e0521ca.0 | Own-company roles record checked: exact role-holder name, role/group type, inactive flag and last-change date. Person is not treated as the researched company. |
| 188 | 994382217 | roles.role.efbad5c00ae691cdbaf977ef.0 | Own-company roles record checked: exact role-holder name, role/group type, inactive flag and last-change date. Person is not treated as the researched company. |
| 189 | 990012288 | social_profile.126746e2b1c39291086e | TB MASKIN proven company page links instagram.com/tbmaskin directly. Own-site attribution applies with existing personal/other-company/shared/group vetoes; not a person-handle inference. |
| 190 | 823147112 | subunits.detail.823159102.organisation_form | Same explicit registry legal-form code/description; API _links metadata is omitted without changing the value. |
| 192 | 987002808 | subunits.unit.987040912 | Exact unit row under the subject parent query checked: orgnr, name, address and explicit employees. Missing employee count remains null. |
| 197 | 974533537 | subunits.unit.971885688 | Exact unit row under the subject parent query checked: orgnr, name, address and explicit employees. Missing employee count remains null. |
| 198 | 935861144 | contact.email.03a8f9e04ddfee69d6d7 | Exact Post@D-Production.no mailto link on the proven D-PRODUCTION website, preserving source case; not a guessed contact. |
| 199 | 821962242 | website_description.about_paragraph.3c80723c3ec659b1 | Verbatim company self-description on proven laksesystemer.no/om-oss. It explicitly assigns 1.8bn turnover to Fj øssystemer group (spelled in the source), not to LAKSESYSTEMER; not an independent financial fact. |
