# Jury seed-7 precision review

This is the 100-claim sample from the fresh Stage BA unseen-300 run. It uses the jury audit?s 300 active companies and its family-stratified allocation: one claim per nonempty family first, then repeatedly allocate to the family with the largest population divided by its next allocation, draw sorted claims with `random.Random(7)`, and verify only the saved source bytes. No HTTP was used for selection or adjudication.

## Result

**100 correct / 0 wrong; observed precision 100%.** 80 claims passed exact source locator, verbatim-span, subject URL and SHA-256 checks. The other 20 were checked against their saved underlying registry/source rows, including company ownership or parent scope where applicable. All 100 saved source hashes were verified.

The published Uniktur brand is absent from the unseen-300 envelopes. Its descriptive title yielded no `public_brand` claim.

## Family allocation

| Family | Population claims | Sampled |
|---|---:|---:|
| accounts | 14066 | 31 |
| activity | 2384 | 5 |
| brands | 9 | 1 |
| gleif | 89 | 1 |
| identity | 12054 | 26 |
| other:central_approval | 20 | 1 |
| other:cleaning_approval | 3 | 1 |
| other:registry_dated_activity | 1409 | 3 |
| other:research | 1 | 1 |
| other:skattefunn | 18 | 1 |
| other:state_aid | 63 | 1 |
| roles | 7997 | 17 |
| social | 21 | 1 |
| subunits | 4286 | 9 |
| website | 123 | 1 |

## Reviewed source-backed claims

| # | Company | Field | Check |
|---:|---|---|---|
| 0 | 992686553 | `identity.business_address_country_code` | exact locator/span/subject URL |
| 1 | 913553098 | `accounts.history.2024.financial_expenses` | exact locator/span/subject URL |
| 2 | 975849430 | `identity.business_address.country_name` | exact locator/span/subject URL |
| 3 | 937322569 | `registry_dated_activity.registration_date` | exact locator/span/subject URL |
| 4 | 970290311 | `identity.registration_date` | exact locator/span/subject URL |
| 5 | 979389523 | `identity.statutory_purpose` | exact locator/span/subject URL |
| 6 | 979389523 | `identity.industry1.beskrivelse` | exact locator/span/subject URL |
| 7 | 926862022 | `identity.business_address.country_name` | exact locator/span/subject URL |
| 8 | 926862022 | `registry_change.9d61413c357f1c5f7d23f47b` | official registry event id, exact subject/subunit row, timestamp, and changed path/value checked |
| 9 | 985492182 | `identity.historical_name.562f488722edb8ba93cd9c0a` | exact locator/span/subject URL |
| 10 | 881191822 | `subunits.detail.993650951.start_date` | exact locator/span/subject URL |
| 11 | 980498670 | `subunits.detail.881009072.registered_phone` | exact locator/span/subject URL |
| 12 | 994692429 | `subunits.detail.973771450.organisation_form` | official subunit form code and description checked on parent-scoped registry row |
| 13 | 933519546 | `roles.detail.ad01362e89d17ec1443cec79.0.role_type_kode` | exact locator/span/subject URL |
| 14 | 991044426 | `roles.detail.870af7017db7a65fa1d5760f.0.person_deceased` | exact locator/span/subject URL |
| 15 | 891942842 | `accounts.history.2023.total_liabilities` | exact locator/span/subject URL |
| 16 | 891942842 | `accounts.statement.2023.period_end` | exact locator/span/subject URL |
| 17 | 914131251 | `identity.legal_name` | exact locator/span/subject URL |
| 18 | 969281023 | `identity.part_of_group` | exact locator/span/subject URL |
| 19 | 963351429 | `contact.phone.cadcf3d58070a865bc23` | exact tel: link on the company’s verified official domain |
| 20 | 920965164 | `accounts.history.2023.financial_result` | exact locator/span/subject URL |
| 21 | 921213948 | `identity.business_address.country_name` | exact locator/span/subject URL |
| 22 | 921213948 | `roles.detail.cf552814d37c4ea5a051d5a4.0.holder_form_beskrivelse` | exact locator/span/subject URL |
| 23 | 921213948 | `accounts.history.2024.result_before_tax` | exact locator/span/subject URL |
| 24 | 924439653 | `roles.detail.8114182f61923bacc421f255.0.role_type_kode` | exact locator/span/subject URL |
| 25 | 924977310 | `accounts.history.2024.operating_expenses` | exact locator/span/subject URL |
| 26 | 924977310 | `state_aid.1000133481` | official aid source row matched by award id, recipient, funder, date, amount, currency, instrument and scheme |
| 27 | 918053603 | `identity.registered_address` | exact locator/span/subject URL |
| 28 | 996987728 | `identity.registration_date` | exact locator/span/subject URL |
| 29 | 979735588 | `roles.role.e9f89adfe6176335bcb07438.0` | company roles endpoint checked for exact role, role holder, entity, active state and group date |
| 30 | 976943295 | `identity.under_liquidation` | exact locator/span/subject URL |
| 31 | 976943295 | `accounts.history.2024.total_assets` | exact locator/span/subject URL |
| 32 | 976943295 | `accounts.statement.2023.parent_company` | exact locator/span/subject URL |
| 33 | 922974179 | `subunits.detail.923002936.nav_employee_registration_date` | exact locator/span/subject URL |
| 34 | 830668632 | `accounts.statement.2024.filing_id` | exact locator/span/subject URL |
| 35 | 995390914 | `accounts.history.2024.total_assets` | exact locator/span/subject URL |
| 36 | 996043797 | `accounts.statement.2024.presentation_plan` | exact locator/span/subject URL |
| 37 | 927835398 | `accounts.history.2024.long_term_liabilities` | exact locator/span/subject URL |
| 38 | 928693287 | `registry_dated_activity.registration_date` | exact locator/span/subject URL |
| 39 | 996629325 | `central_approval.7236a3f0d647f67f7f22666c` | official DiBK company page contains organisation number, function, area, class and validity dates |
| 40 | 922018308 | `roles.detail.aa61f54388b6196eae2fd35d.0.role_type_kode` | exact locator/span/subject URL |
| 41 | 928024466 | `identity.registered_capital.antallAksjer` | exact locator/span/subject URL |
| 42 | 928024466 | `accounts.statement.2024.accounting_rules` | exact locator/span/subject URL |
| 43 | 986218912 | `roles.detail.2202ee45fd321cdfa0536a3b.0.birth_year` | year matches the explicit date of birth on the company’s roles endpoint |
| 44 | 986218912 | `registry_dated_activity.registration_date` | exact locator/span/subject URL |
| 45 | 896440292 | `identity.registered_in_party_register` | exact locator/span/subject URL |
| 46 | 896440292 | `roles.detail.d48bfb1894655994f2ffad43.0.order` | exact locator/span/subject URL |
| 47 | 896440292 | `public_brand` | brand appears in page title and matches registered legal name |
| 48 | 980408663 | `identity.registration_date` | exact locator/span/subject URL |
| 49 | 912493865 | `accounts.history.2024.total_comprehensive_result` | exact locator/span/subject URL |
| 50 | 912493865 | `accounts.statement.2024.account_type` | exact locator/span/subject URL |
| 51 | 912493865 | `social_profile.bd1bc61a5af5d8fe421a` | verified official company site directly links the exact social profile |
| 52 | 912493865 | `registry_change.1cdb00a5a8c2d4f211135140` | official registry event id, exact subject/subunit row, timestamp, and changed path/value checked |
| 53 | 974408430 | `roles.group.0.last_changed` | exact locator/span/subject URL |
| 54 | 974408430 | `skattefunn.27074` | Research Council workbook row matched by project id and organisation number; title, applicant, period and approval checked |
| 55 | 920887910 | `accounts.history.2023.equity` | exact locator/span/subject URL |
| 56 | 997710096 | `registry_change.70eca602e49b75f1f7bbdea7` | official registry event id, exact subject/subunit row, timestamp, and changed path/value checked |
| 57 | 937769636 | `roles.group.0.last_changed` | exact locator/span/subject URL |
| 58 | 988578878 | `identity.municipality` | exact locator/span/subject URL |
| 59 | 922182396 | `roles.detail.518c603ba0a4f7b46caa35a3.0.person_deceased` | exact locator/span/subject URL |
| 60 | 938305463 | `accounts.consolidated.2024.receivables` | exact locator/span/subject URL |
| 61 | 938305463 | `accounts.consolidated.2024.financial_result` | exact locator/span/subject URL |
| 62 | 876883112 | `accounts.statement.2023.accounting_rules` | exact locator/span/subject URL |
| 63 | 950725095 | `registry_change.de467b070a4c18b80a5772bd` | official registry event id, exact subject/subunit row, timestamp, and changed path/value checked |
| 64 | 933485102 | `accounts.statement.2024.period_start` | exact locator/span/subject URL |
| 65 | 924421967 | `subunits.detail.924440775.organisation_form` | official subunit form code and description checked on parent-scoped registry row |
| 66 | 924327456 | `accounts.history.2024.operating_result` | exact locator/span/subject URL |
| 67 | 937927258 | `identity.business_address.municipality_code` | exact locator/span/subject URL |
| 68 | 938228698 | `subunits.detail.938419957.beliggenhetsadresse.landkode` | exact locator/span/subject URL |
| 69 | 911956608 | `accounts.statement.2024.registered_organisation_form` | exact locator/span/subject URL |
| 70 | 911956608 | `registry_change.0e2d36e86f649c290f400334` | official registry event id, exact subject/subunit row, timestamp, and changed path/value checked |
| 71 | 981289994 | `subunits.detail.981577329.historical_name.7c63d738d7f9360127ab96c3` | exact locator/span/subject URL |
| 72 | 996510360 | `cleaning_approval.status` | official Arbeidstilsynet row matched by company number, name and status |
| 73 | 921471394 | `identity.employee_count_nav_registration_date` | exact locator/span/subject URL |
| 74 | 917123462 | `identity.language_form` | exact locator/span/subject URL |
| 75 | 922176922 | `identity.employee_count_registration_date` | exact locator/span/subject URL |
| 76 | 916646151 | `roles.detail.b16c6558521cae722865dccc.0.inactive` | exact locator/span/subject URL |
| 77 | 931859137 | `accounts.history.2024.revenue` | exact locator/span/subject URL |
| 78 | 998346916 | `subunits.detail.998375363.postadresse.postnummer` | exact locator/span/subject URL |
| 79 | 979753195 | `accounts.statement.2025.liquidation_accounts` | exact locator/span/subject URL |
| 80 | 934958322 | `identity.postal_address.line.0` | exact locator/span/subject URL |
| 81 | 931831429 | `roles.detail.7a53a41d9eb72246557d4fcf.0.birth_year` | year matches the explicit date of birth on the company’s roles endpoint |
| 82 | 925695033 | `accounts.statement.2024.currency` | exact locator/span/subject URL |
| 83 | 921072406 | `roles.detail.0097a053ad9e7c7e63680be0.0.role_type_kode` | exact locator/span/subject URL |
| 84 | 988162175 | `identity.gleif.registration_date` | GLEIF record registeredAs matches the company number; registration date equals the cited field |
| 85 | 988162175 | `research.296521` | Research Council source CSV row matched by project id and company number; title, responsible entity, amount and phase checked |
| 86 | 931724010 | `identity.institutional_sector.kode` | exact locator/span/subject URL |
| 87 | 927251108 | `accounts.result_before_tax` | exact locator/span/subject URL |
| 88 | 929375084 | `roles.group.0.last_changed` | exact locator/span/subject URL |
| 89 | 913660900 | `identity.part_of_group` | exact locator/span/subject URL |
| 90 | 916455275 | `accounts.statement.2024.audit_opt_out` | exact locator/span/subject URL |
| 91 | 920255329 | `subunits.detail.933890333.beliggenhetsadresse.kommune` | exact locator/span/subject URL |
| 92 | 915980341 | `identity.business_address.postal_code` | exact locator/span/subject URL |
| 93 | 898194612 | `accounts.history.2024.total_comprehensive_result` | exact locator/span/subject URL |
| 94 | 898194612 | `accounts.statement.2025.period_end` | exact locator/span/subject URL |
| 95 | 888126732 | `identity.organisation_form.kode` | exact locator/span/subject URL |
| 96 | 930635308 | `accounts.tax_expense` | exact locator/span/subject URL |
| 97 | 985415528 | `roles.role.539476822018c4cee325a717.0` | company roles endpoint checked for exact role, role holder, entity, active state and group date |
| 98 | 936490514 | `roles.group.1.type_beskrivelse` | exact locator/span/subject URL |
| 99 | 936490514 | `accounts.net_result` | exact locator/span/subject URL |
