# Final run accuracy adjudication

200 published claims; seed 20261119. Mechanical verdicts require the unchanged Stage X equality/span/subject-URL check. Remaining items were source-reviewed with context retained in hand-review-support.json. This script rechecks the source corroboration, not the publisher.

| Index | Company | Field | Review |
|---:|---|---|---|
| 3 | 948774402 | accounts.statement.2025.audit_status | Both explicit audit booleans checked for the cited year; fravalgRevisjon=true means audit_opted_out, not audited. |
| 45 | 916188145 | accounts.statement.2025.audit_status | Both explicit audit booleans checked for the cited year; fravalgRevisjon=true means audit_opted_out, not audited. |
| 82 | 912493296 | registry_change.ff09ed06439afc814c52fec3 | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 83 | 986739874 | registry_change.6a16f0114e51bf4b8edb3c84 | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 84 | 926128507 | registry_change.b28de8e6864d54fabe2f717c | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 85 | 987454709 | registry_change.03fd95ee3ff66601de2d34b2 | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 86 | 921206232 | registry_change.48c70ebbd0703c4aa92ebc49 | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 87 | 993452858 | registry_change.d4af448028e471b56b86a491 | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 88 | 965835156 | registry_change.db7cb8de17748a41bae8cb60 | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 89 | 958366620 | registry_change.e63f866d873ab0edacfa8f4a | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 90 | 935794897 | registry_change.bed3f1c305e9d63cf4ca5a38 | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 91 | 924784091 | registry_change.8b62f2080bd7f6cda5124efc | Exact event id, company/registered-subunit number, publication timestamp and operation/value checked in retained event; publication is not effective time. |
| 92 | 991368000 | public_brand | Verified company page names “Ralston Bau”; the brand matches the legal name or verified domain core under the current brand rule. |
| 93 | 984024290 | identity.gleif.direct_parent | Three saved GLEIF responses establish the company LEI, active direct-parent relationship and exact parent LEI/name/type. |
| 95 | 930202894 | hiring.job.c0349976-bbfc-41f4-a980-b482f06e5f2d | NAV detail checked for “Pedagogisk leder 40% vikariat” and employer 997453964; the company’s BRREG subunit claim establishes the employer scope. Status/expiry and occupation/location remain NAV fields. |
| 102 | 980910857 | identity.wikidata.inception.8c5ab64a70a71f01 | Wikidata result binds inception time, precision and calendar to this exact company-number query. |
| 133 | 984024290 | central_approval.54f02191c4fcbc621ae496a7 | DiBK page has the exact company number and approval row values: Murarbeid, Utførende, class 2, valid 20.09.2024 to 20.09.2027. |
| 134 | 935180678 | cleaning_approval.status | Exact main-unit register row matches company number, name and status “Godkjent uten ansatte”; the approved flag follows the register’s explicit status. |
| 135 | 989145509 | news_item.ab957c845ff07fbefcd6 | Same RSS item states the exact title, URL and publication date 2024-12-05; the verified company website binds the feed to this company. This is company-published material. |
| 143 | 931824317 | related_company_website.parent.929283392 | Official registry row names EDGE HOSPITALITY AS (929283392) and declares www.edgeworld.no; the separate registry relationship establishes parent scope. It is not marked ownership-verified. |
| 144 | 984024290 | research.193191 | Research Council row 193191 matches company, title, responsible organisation, total amount and application period. No exclusive share or currency is inferred. |
| 145 | 950220317 | skattefunn.300862 | Workbook row 300862 matches company, applicant, approval, decision date and 2019–2022 period; it is an R&D tax deduction, not a cash grant. |
| 146 | 996979660 | state_aid.1000274643 | Exact aid row matches recipient 996979660, award id 1000274643, instrument and date; the amount or range follows that record. |
| 147 | 994623710 | state_aid.1000265302 | Exact aid row matches recipient 994623710, award id 1000265302, instrument and date; the amount or range follows that record. |
| 148 | 975962121 | workshop_approval.28371 | Exact workshop export row matches company 975962121, approval 28371, type BILGLASS and address Verpetveien 32. |
| 158 | 919217081 | roles.detail.c854e646cd57faaacaf3b7f9.0.birth_year | Only year derived from the cited explicit registry birth date; own-company roles URL binds attribution. |
| 168 | 912492575 | roles.role.ec8d3b3289f614dd8ff0cbd7.0 | Own-company roles record checked: exact role-holder name, role/group type, inactive flag and last-change date. Person is not treated as the researched company. |
| 171 | 990033897 | roles.detail.2df2ed078a3406eeb01731b4.0.entity_form | Same explicit registry legal-form code/description; API _links metadata is omitted without changing the value. |
| 172 | 922069212 | roles.role.20ed7031ad69865b0b8c43e7.0 | Own-company roles record checked: exact role-holder name, role/group type, inactive flag and last-change date. Person is not treated as the researched company. |
| 183 | 995748983 | social_profile.a7b9f9ebca242696aeb1 | Verified official company site directly links https://twitter.com/maaemo; site ownership and existing personal/other-company/shared/group vetoes are retained. |
| 194 | 823568002 | subunits.unit.923634886 | Exact unit row under the subject parent query checked: orgnr, name, address and explicit employees. Missing employee count remains null. |
| 195 | 986610472 | subunits.detail.886613962.organisation_form | Same explicit registry legal-form code/description; API _links metadata is omitted without changing the value. |
| 196 | 929942167 | subunits.detail.985769915.organisation_form | Same explicit registry legal-form code/description; API _links metadata is omitted without changing the value. |
| 198 | 993919675 | procurement_award.b1ea37d59a84c65b19ecdb35 | TED award notice checked for exact settled contract, award date/title, company national number and matching tender amount/currency. |
| 199 | 912829197 | website_description.og_description.5b2d3150e19b4e89 | Verbatim self-description (“cCHANGE is a values-based organization offering transformational processes to create extraordinary results for people and planet.”) appears on the verified company website and is tied to its identity claim; it is not recast as independent fact. |
