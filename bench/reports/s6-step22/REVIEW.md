# Step 22 precision review

Every published website/social link, GLEIF field and job was reviewed; no TED awards were returned. Seed 2026110722 selected ten claims per requested family and ten briefings without replacement. Every referenced blob was SHA-256 checked and excerpts were checked against raw bytes.

## All website/social/GLEIF/job items

| Company / orgnr | Item | Initial verdict | Final disposition | Source assessment |
|---|---|---|---|---|
| A-Å GRAFISK DESIGN & REKLAME AS / 838492002 | https://a-aa.no | correct | kept | Registered homepage a-aa.no; visible text explicitly names A-Å grafisk design & reklame AS. Exact registry declaration/name match. |
| 7OCEAN AS / 996261824 | https://arbeidsplassen.nav.no/stillinger/stilling/98b843f4-12e1-4b88-a854-15c56b2b4f7d | correct | kept | NAV ACTIVE ad, expiry 10 Nov 2026, title and employer orgnr 996285162 match saved registered subunit of 7OCEAN AS. Individual UUID ad, not landing page. |
| A JONASSEN AS / 877188922 | 549300DFLIZG1W1TYZ31 | correct | kept | Raw GLEIF exact registeredAs 877188922 and RA000472; LEI/status/form/initial registration/next renewal exactly match JSON pointers. Renewal is a future source field, not an accomplished event. |
| A JONASSEN AS / 877188922 | ACTIVE | correct | kept | Raw GLEIF exact registeredAs 877188922 and RA000472; LEI/status/form/initial registration/next renewal exactly match JSON pointers. Renewal is a future source field, not an accomplished event. |
| A JONASSEN AS / 877188922 | {'id': 'YI42', 'other': None} | correct | kept | Raw GLEIF exact registeredAs 877188922 and RA000472; LEI/status/form/initial registration/next renewal exactly match JSON pointers. Renewal is a future source field, not an accomplished event. |
| A JONASSEN AS / 877188922 | 2018-01-05T15:36:00Z | correct | kept | Raw GLEIF exact registeredAs 877188922 and RA000472; LEI/status/form/initial registration/next renewal exactly match JSON pointers. Renewal is a future source field, not an accomplished event. |
| A JONASSEN AS / 877188922 | 2027-01-10T05:39:09Z | correct | kept | Raw GLEIF exact registeredAs 877188922 and RA000472; LEI/status/form/initial registration/next renewal exactly match JSON pointers. Renewal is a future source field, not an accomplished event. |
| 7FJELL TAXI AS / 929910648 | https://arbeidsplassen.nav.no/stillinger/stilling/1aa5c4c2-67ad-46c9-9c47-d596d96250eb | correct | kept | NAV ACTIVE ad, expiry 31 Dec 2026, title and employer orgnr 929928806 match saved registered subunit of 7FJELL TAXI AS. Individual UUID ad. |
| A KLINIKKEN AS / 925622672 | https://a-klinikken.no | correct | kept | Footer contains own orgnr 925622672; Facebook link names A-Klinikken. Akari AS is explicitly a design/hosting supplier credit. |
| A KLINIKKEN AS / 925622672 | https://www.facebook.com/A-Klinikken-158275702602849 | correct | kept | Footer contains own orgnr 925622672; Facebook link names A-Klinikken. Akari AS is explicitly a design/hosting supplier credit. |
| 21-5 / 917357439 | https://www.21-5.no | doubtful | withheld by generic full-publisher-name guard | Doubtful exact-entity attribution: subject is NUF 21-5 at Danish HQ Christianshusvej 187; contact footer identifies 21-5 Norge AS at Nydalsveien 28. Parent-brand/street match does not establish this distinct publisher. Withheld website and derived social/content. |
| 21-5 / 917357439 | https://www.linkedin.com/company/21-5 | doubtful | withheld by generic full-publisher-name guard | Doubtful exact-entity attribution: subject is NUF 21-5 at Danish HQ Christianshusvej 187; contact footer identifies 21-5 Norge AS at Nydalsveien 28. Parent-brand/street match does not establish this distinct publisher. Withheld website and derived social/content. |
| 7FJELL GLASSERVICE AS / 924278137 | https://7fjell-glasservice.no | correct | kept | Contact page names 7Fjell Glasservice AS and matches Breisteinvegen 182A / 5111 Breistein. Facebook and Instagram links are company-specific footer links. |
| 7FJELL GLASSERVICE AS / 924278137 | https://www.facebook.com/7FjellGlasservice | correct | kept | Contact page names 7Fjell Glasservice AS and matches Breisteinvegen 182A / 5111 Breistein. Facebook and Instagram links are company-specific footer links. |
| 7FJELL GLASSERVICE AS / 924278137 | https://www.instagram.com/7fjell_glasserviceas | correct | kept | Contact page names 7Fjell Glasservice AS and matches Breisteinvegen 182A / 5111 Breistein. Facebook and Instagram links are company-specific footer links. |
| 7ANALYTICS AS / 919844523 | https://7analytics.ai | correct | kept | Privacy page explicitly names 7Analytics AS, own orgnr 919844523 and Bergen address. LinkedIn company/7analytics is linked in footer. |
| 7ANALYTICS AS / 919844523 | https://no.linkedin.com/company/7analytics | correct | kept | Privacy page explicitly names 7Analytics AS, own orgnr 919844523 and Bergen address. LinkedIn company/7analytics is linked in footer. |
| A-Å REGNSKAP AS / 918398252 | https://a-aaregnskap.no | correct | kept | Own orgnr 918398252 and A-Å Regnskap AS copyright/footer; supplier Maria of the North is explicitly developer, not publisher. |

## Fifty sampled source facts

| Family | Company / orgnr | Field / value | Verdict | Review |
|---|---|---|---|---|
| identity | 7COLOREDFLOWER STUDIO - VESTBØ / 937820143 | identity.forced_dissolution: false | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| identity | 7FKONSULT AS / 932031353 | identity.employees_reported: true | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| identity | 22 HOLDING NUF / 928330117 | identity.municipality: "OSLO" | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| identity | 2380 INVEST AS / 934153936 | identity.organisation_form: {"_links": {"self": {"href": "https://data.brreg.no/enhetsregisteret/api/organisasjonsformer/AS"}}, "beskrivelse": "Aksjeselskap", "kode": "AS"} | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| identity | ABUVIK AS / 933222101 | identity.registration_date: "2024-03-26" | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| identity | 2.FLEKKEFJORD MS / 994869086 | identity.registered_in_vat: false | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| identity | A-ZYM AS / 993295035 | identity.forced_dissolution: false | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| identity | A. ANDERZÉN AS / 920714935 | identity.municipality: "GRATANGEN" | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| identity | 7ANALYTICS AS / 919844523 | identity.under_liquidation: false | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| identity | A. HAAVE / 929558766 | identity.registered_address: {"adresse": ["Hårstadvegen 41"], "kommune": "SELBU", "kommunenummer": "5032", "land": "Norge", "landkode": "NO", "postnummer": "7580", "poststed": "SELBU"} | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| subunits | 7SENSE AGRITECH AS / 913036999 | subunits.detail.913044487.historical_name.ab8a670daae98f7daa904ee9: {"navn": "7SENSE PRODUCTS AS", "fraDato": "2014-01-08 21:44:05", "tilDato": "2022-06-17 13:25:36"} | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| subunits | 2017-KULLET HEMNES SENTRALSKOLE / 932258935 | subunits.detail.932260689.organisation_form: {"beskrivelse": "Underenhet til ikke-næringsdrivende", "kode": "AAFY"} | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| subunits | A. BEITRUSTEN HOLDING AS / 835226972 | subunits.detail.935228662.start_date: "2025-02-28" | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| subunits | 7FJELL TAXI AS / 929910648 | subunits.detail.929928806.registered_in_vat: false | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| subunits | A JONASSEN AS / 877188922 | subunits.detail.977194520.registered_in_vat: false | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| subunits | 7FJELL GLASSERVICE AS / 924278137 | subunits.detail.924304553.employees_reported: true | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| subunits | 2011-BARN ØVREBØ / 932470004 | subunits.unit.932517256: {"organisation_number": "932517256", "name": "2011-BARN ØVREBØ", "address": {"adresse": ["c/o Ken Arne Skaugerud", "Einerlia 2"], "kommune": "VENNESLA", "kommunenummer": "4223", "land": "Norge", "landkode": "NO", "postnummer": "4715", "poststed": "ØVREBØ"}, "nace": {"beskrivelse": "Aktiviteter i andre medlemsorganisasjoner ellers", "kode": "94.992"}, "employees": null} | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| subunits | 7FJELL GLASSERVICE AS / 924278137 | subunits.detail.924304553.registered_in_vat: false | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| subunits | 7FJELL TAXI AS / 929910648 | subunits.detail.929928806.registered_email: "nezhadarman@gmail.com" | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| subunits | ABW INTERNATIONAL BERGSTUEN-WENNERØD / 981106563 | subunits.unit.934811232: {"organisation_number": "934811232", "name": "ABW INTERNATIONAL BERGSTUEN-WENNERØD", "address": {"adresse": ["Øygardsvegen 110"], "kommune": "PORSGRUNN", "kommunenummer": "4001", "land": "Norge", "landkode": "NO", "postnummer": "3914", "poststed": "PORSGRUNN"}, "nace": {"beskrivelse": "Engroshandel med parfyme og kosmetikk", "kode": "46.450"}, "employees": null} | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| roles | 74 PROSJEKT 1 AS / 926402781 | roles.detail.3a9b5e7fcf2826e878ba219e.0.order: 0 | correct after correction | Exact raw registry locator supports value; source company/subunit scope and period checked. Birth year uses only the source birth-date year. |
| roles | 7FJELL VENTURES AS / 989079417 | roles.detail.87a77bdb9f1f3b035d8e4a30.0.order: 0 | correct after correction | Exact raw registry locator supports value; source company/subunit scope and period checked. Birth year uses only the source birth-date year. |
| roles | A-ZYM AS / 993295035 | roles.detail.6f403014819d98f1a922d882.0.order: 1 | correct after correction | Exact raw registry locator supports value; source company/subunit scope and period checked. Birth year uses only the source birth-date year. |
| roles | 2 ROMERIKE ST GEORGS GILDE / 997071956 | roles.role.f0e070ec88ab65d5b63dbc8d.0: {"role_type": {"_links": {"self": {"href": "https://data.brreg.no/enhetsregisteret/api/roller/rolletyper/MEDL"}}, "beskrivelse": "Styremedlem", "kode": "MEDL"}, "name": "Morten Woldseth", "entity_organisation_number": null, "inactive": false, "group_type": {"_links": {"self": {"href": "https://data.brreg.no/enhetsregisteret/api/roller/rollegruppetyper/STYR"}}, "beskrivelse": "Styre", "kode": "STYR"}, "last_changed": "2026-01-29", "from_date": null} | correct after correction | Exact raw registry locator supports value; source company/subunit scope and period checked. Birth year uses only the source birth-date year. |
| roles | 7SENSE AGRITECH AS / 913036999 | roles.detail.f368bf26d2e02d6e9da83709.0.birth_year: 1967 | correct after correction | Exact raw registry locator supports value; source company/subunit scope and period checked. Birth year uses only the source birth-date year. |
| roles | ABY MOBILITY AS / 938385491 | roles.detail.0be0a55b39548bdf56cb2da5.0.entity_approval_status: "Godkjent regnskapsforetak" | correct after correction | Exact raw registry locator supports value; source company/subunit scope and period checked. Birth year uses only the source birth-date year. |
| roles | 23 DEGREES RENEWABLE LTD / 932188511 | roles.detail.801de2d4bf11bff32cfbeac3.0.order: 0 | correct after correction | Exact raw registry locator supports value; source company/subunit scope and period checked. Birth year uses only the source birth-date year. |
| roles | 7SENSE AGRITECH AS / 913036999 | roles.detail.f368bf26d2e02d6e9da83709.0.order: 1 | correct after correction | Exact raw registry locator supports value; source company/subunit scope and period checked. Birth year uses only the source birth-date year. |
| roles | A KARLSEN & SØNN AS / 841564812 | roles.detail.e9f89adfe6176335bcb07438.0.entity_deleted: false | correct after correction | Exact raw registry locator supports value; source company/subunit scope and period checked. Birth year uses only the source birth-date year. |
| roles | ABUS NORDIC / 813138972 | roles.role.3eec33959b273ab74fd59815.0: {"role_type": {"_links": {"self": {"href": "https://data.brreg.no/enhetsregisteret/api/roller/rolletyper/HFOR"}}, "beskrivelse": "Oppl om foretaket i hjemlandet", "kode": "HFOR"}, "name": ["ABUS-GRUPPEN NORDIC A/S"], "entity_organisation_number": "913139062", "inactive": false, "group_type": {"_links": {"self": {"href": "https://data.brreg.no/enhetsregisteret/api/roller/rollegruppetyper/HFOR"}}, "beskrivelse": "Hovedforetak", "kode": "HFOR"}, "last_changed": "2014-02-06", "from_date": null} | correct after correction | Exact raw registry locator supports value; source company/subunit scope and period checked. Birth year uses only the source birth-date year. |
| accounts | 20TWENTY AS / 925531413 | accounts.history.2024.paid_in_equity: 21930.0 | correct after correction | Value and fiscal period match exact-company BRREG JSON; unrelated unit-calibration citations removed offline, original claim ID/value retained. |
| accounts | 2323 MEDIA AS / 930096393 | accounts.statement.2024.accounting_rules: "regnskapslovenAlminneligRegler" | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| accounts | 7OCEAN AS / 996261824 | accounts.statement.2024.account_type: "SELSKAP" | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| accounts | 7FJELL GLASSERVICE AS / 924278137 | accounts.history.2023.salary_expenses: 823679.0 | correct after correction | Value and fiscal period match exact-company BRREG JSON; unrelated unit-calibration citations removed offline, original claim ID/value retained. |
| accounts | 221 CONSULTING AS / 814968952 | accounts.history.2024.retained_equity: 1004533.0 | correct after correction | Value and fiscal period match exact-company BRREG JSON; unrelated unit-calibration citations removed offline, original claim ID/value retained. |
| accounts | 2323 MEDIA AS / 930096393 | accounts.paid_in_equity: 30000.0 | correct after correction | Value and fiscal period match exact-company BRREG JSON; unrelated unit-calibration citations removed offline, original claim ID/value retained. |
| accounts | 7FJELL TAXI AS / 929910648 | accounts.history.2024.current_liabilities: 144429.0 | correct after correction | Value and fiscal period match exact-company BRREG JSON; unrelated unit-calibration citations removed offline, original claim ID/value retained. |
| accounts | 20TWENTY AS / 925531413 | accounts.history.2023.salary_expenses: 6531167.0 | correct after correction | Value and fiscal period match exact-company BRREG JSON; unrelated unit-calibration citations removed offline, original claim ID/value retained. |
| accounts | 73 HOLDING AS / 933302970 | accounts.statement.2024.account_type: "SELSKAP" | correct after correction | Exact raw registry locator supports value and correct company/subunit/financial period. No missing value inferred. |
| accounts | 2323 MEDIA AS / 930096393 | accounts.history.2023.revenue: 4604240.0 | correct after correction | Value and fiscal period match exact-company BRREG JSON; unrelated unit-calibration citations removed offline, original claim ID/value retained. |
| registry announcements | A. BLOMSTRAND WEB-SIKKERHET / 930809683 | registry_change.83c27213233071cd3133cff4: {"company_orgnr": "930809683", "event_id": 23491881, "date": "2025-12-12T08:30:12.601000Z", "kind": "Registry announcement", "date_source": "registry publication time (not effective date)", "url": "https://data.brreg.no/enhetsregisteret/api/oppdateringer/enheter?oppdateringsid=23491881&size=1&includeChanges=true", "title": "Registered business address changed", "changed_field": "/forretningsadresse/adresse/0", "operation": "replace", "new_value": "Ivan Bjørndals gate 24"} | correct after correction | Exact raw registry locator supports value; company/subunit scope checked. Announcement dates are publication instants (UTC offsets normalized), not effective dates. |
| registry announcements | 7FKONSULT AS / 932031353 | registry_change.d64708a54f215ddd21548186: {"company_orgnr": "932031353", "event_id": 25055563, "date": "2026-08-11T22:07:20.050000Z", "kind": "Registry announcement", "date_source": "registry publication time (not effective date)", "url": "https://data.brreg.no/enhetsregisteret/api/oppdateringer/enheter?oppdateringsid=25055563&size=1&includeChanges=true", "title": "Employee information registration date updated (Enhetsregisteret)", "changed_field": "/registreringsdatoAntallAnsatteEnhetsregisteret", "operation": "replace", "new_value": "2026-08-11"} | correct after correction | Exact raw registry locator supports value; company/subunit scope checked. Announcement dates are publication instants (UTC offsets normalized), not effective dates. |
| registry announcements | 7FJELL TAXI AS / 929910648 | registry_change.9f185e9f126a0abfc032d42d: {"company_orgnr": "929910648", "event_id": 20001927, "date": "2024-12-11T23:09:42.604000Z", "kind": "Registry announcement", "date_source": "registry publication time (not effective date)", "url": "https://data.brreg.no/enhetsregisteret/api/oppdateringer/enheter?oppdateringsid=20001927&size=1&includeChanges=true", "title": "Registry update recorded", "event_type": "Endring"} | correct after correction | Exact raw registry locator supports value; company/subunit scope checked. Announcement dates are publication instants (UTC offsets normalized), not effective dates. |
| registry announcements | 20TWENTY AS / 925531413 | registry_change.d6482c32bcad8d7d394009b5: {"company_orgnr": "925531413", "event_id": 22170965, "date": "2025-10-15T22:08:38.576000Z", "kind": "Registry announcement", "date_source": "registry publication time (not effective date)", "url": "https://data.brreg.no/enhetsregisteret/api/oppdateringer/enheter?oppdateringsid=22170965&size=1&includeChanges=true", "title": "Employee information registration date updated (NAV Aa register)", "changed_field": "/registreringsdatoAntallAnsatteNAVAaregisteret", "operation": "replace", "new_value": "2025-10-10"} | correct after correction | Exact raw registry locator supports value; company/subunit scope checked. Announcement dates are publication instants (UTC offsets normalized), not effective dates. |
| registry announcements | 2 X SKUM VED OG DIV. / 928855287 | registry_change.c3090aff7c56f33a8f51a6a5: {"company_orgnr": "928855287", "event_id": 18440101, "date": "2024-01-01T06:34:50.244000Z", "kind": "Registry announcement", "date_source": "registry publication time (not effective date)", "url": "https://data.brreg.no/enhetsregisteret/api/oppdateringer/enheter?oppdateringsid=18440101&size=1&includeChanges=true", "title": "Registry update recorded", "event_type": "Endring"} | correct after correction | Exact raw registry locator supports value; company/subunit scope checked. Announcement dates are publication instants (UTC offsets normalized), not effective dates. |
| registry announcements | A KAVLI EIENDOM AS / 913343913 | registry_change.d8ee6bda7fd7b3adac43ba37: {"company_orgnr": "913343913", "event_id": 20613941, "date": "2025-04-08T11:52:05.648000Z", "kind": "Registry announcement", "date_source": "registry publication time (not effective date)", "url": "https://data.brreg.no/enhetsregisteret/api/oppdateringer/enheter?oppdateringsid=20613941&size=1&includeChanges=true", "title": "Registry update recorded", "event_type": "Endring"} | correct after correction | Exact raw registry locator supports value; company/subunit scope checked. Announcement dates are publication instants (UTC offsets normalized), not effective dates. |
| registry announcements | A JONASSEN AS / 877188922 | registry_change.9eacb0c77c4e3e4238ed3ac2: {"company_orgnr": "877188922", "event_id": 19642292, "date": "2025-02-12T01:13:09.787000Z", "kind": "Registry announcement", "date_source": "registry publication time (not effective date)", "url": "https://data.brreg.no/enhetsregisteret/api/oppdateringer/underenheter?oppdateringsid=19642292&size=1&includeChanges=true", "title": "Workplace registry update recorded", "subunit_orgnr": "977194520", "event_type": "Endring"} | correct after correction | Exact raw registry locator supports value; company/subunit scope checked. Announcement dates are publication instants (UTC offsets normalized), not effective dates. |
| registry announcements | A KAVLI EIENDOM AS / 913343913 | registry_change.1280aa1ebff2c3804b3f887b: {"company_orgnr": "913343913", "event_id": 21082039, "date": "2025-04-08T12:43:11.186000Z", "kind": "Registry announcement", "date_source": "registry publication time (not effective date)", "url": "https://data.brreg.no/enhetsregisteret/api/oppdateringer/enheter?oppdateringsid=21082039&size=1&includeChanges=true", "title": "Registry update recorded", "event_type": "Endring"} | correct after correction | Exact raw registry locator supports value; company/subunit scope checked. Announcement dates are publication instants (UTC offsets normalized), not effective dates. |
| registry announcements | 7OCEAN AS / 996261824 | registry_change.08e5e859cd32e0e496bd147b: {"company_orgnr": "996261824", "event_id": 21458143, "date": "2026-10-12T22:47:11.417000Z", "kind": "Registry announcement", "date_source": "registry publication time (not effective date)", "url": "https://data.brreg.no/enhetsregisteret/api/oppdateringer/underenheter?oppdateringsid=21458143&size=1&includeChanges=true", "title": "Workplace registry update recorded", "subunit_orgnr": "996285162", "event_type": "Endring"} | correct after correction | Exact raw registry locator supports value; company/subunit scope checked. Announcement dates are publication instants (UTC offsets normalized), not effective dates. |
| registry announcements | 7ERTSEN AS / 989186787 | registry_change.092d0dea6c1a187f8adbc7da: {"company_orgnr": "989186787", "event_id": 25119169, "date": "2026-08-20T18:00:41.608000Z", "kind": "Registry announcement", "date_source": "registry publication time (not effective date)", "url": "https://data.brreg.no/enhetsregisteret/api/oppdateringer/enheter?oppdateringsid=25119169&size=1&includeChanges=true", "title": "Latest submitted annual accounts year updated", "changed_field": "/sisteInnsendteAarsregnskap", "operation": "replace", "new_value": "2025"} | correct after correction | Exact raw registry locator supports value; company/subunit scope checked. Announcement dates are publication instants (UTC offsets normalized), not effective dates. |

## Ten primary briefings

Every sentence below was compared with its cited facts and raw saved support. Absence sentences cite run context, not invented external evidence. All numbers, periods, percentage arithmetic, dates and scope are correct. Other-company calibration links in financial support are removed by the same citation-only correction; no financial value or briefing text is rewritten.

### 933768589

7B HALDORSEN (org. 933768589) is a sole proprietorship in Nordre Follo, registered in 2024, working in business and other management consultancy activities.

Citations: `109d560d3fe60a7a9ae7fb88a617e90592ab24029f3bb6fef301ab7f981bcea5`, `dea164e20a3db6e36c7aef95d71d85eb06ac2d06b8803c2b15ce7132f71b1d7f`, `de14e87f73ba617d2ea776c498b38ac7d2c472e773dd0aa08b7b25751f98d872`, `0ddcb8dbddcf2404cf87d5b4e1497627fdf9cf73fc42c522326708dba03f6b6d`, `594a99d96641e3f4f2e136bcdc12f95cc47be008740dfab0d52fbe7f3a3fde43`, `4f39ff959cb93d3fc897b65571108cde42452ad86b778c03af789d9f2f33773d`. Verdict: correct.

It has one registered workplace, in Nordre Follo.

Citations: `c7d358b42326c0f69a8450159bd06ddb4303d6ba13d6fc42163633f5292a794c`. Verdict: correct.

No company website could be verified.

Citations: `0ea845ad81276f5e16f2853ba57d456227ee27980733c77ad79c1a6a76079148`. Verdict: correct.

Company-only accounts were not available in the checked sources; no active job ads were found in the checked sources.

Citations: `972b814ea72373e71cb7700db5aa557ab41b256cbdd39704c7a8e126d0f32ef4`, `d3f7b0454bf7fd38f573632e4efa4c624cc2d463eca9e75622cdab8a6b52f683`. Verdict: correct.

### 919358556

24 I NORDEN AB (org. 919358556) is a registered entity (legal form UTLA), founded in 2016.

Citations: `70536cdf1e095bffa6a39bf4aac674af756bdffe5b48a77c328bdf6e43db6f9a`, `27588c2d942b1d30f929953c13e2a035f151e855fc94f82a3a8cc53a2cc01f4e`, `f839c7cdd1c256b6eba2b21acd09e615b8276f42486797e8c5647965175786ab`, `dd262e50b70449fbba3faf8f4e68c24e5b613ad8cbdbc6c27cddfd6726a92f16`. Verdict: correct.

No company website could be verified.

Citations: `0a7c5104558419a8e005d468415b9e4695d3c5f8411f00704c1b3e46e7c81443`. Verdict: correct.

Company-only accounts were not available in the checked sources; no active job ads were found in the checked sources.

Citations: `80664a2dc2320b6f02c815150594bfdc6de995310b08d5cf9bce9b12437e9496`, `b9e0831f75b8cc2f99117b5d5419f7694900fa313b913e2e9526a07d0d0f9f0f`. Verdict: correct.

### 926402781

74 PROSJEKT 1 AS (org. 926402781) is a private limited company in Hamar, founded in 2021, working in motion picture, video and television programme production activities.

Citations: `e1b18d5fe6a5f41ed7e0ae230af42c0fa9bfc70963764ba6a5357bc4c7acd98f`, `f23430ca42f02900da15424a86b834c5e1dd085dc9bbfb918cbd5646dea12576`, `cc457d16bbab51b11caf3305e5530414977b796777a4f60f4ee5a053f82327aa`, `7871495401c5653fa1820461d2afcd69930bb07a9d730fb9e4e9d212f39e649d`, `6342b05aa4545f871b6d7a946ad57e510e1b0713c3c4c7433d524b00674b6288`, `e7c8bc2115412fb2b0690ad85921a388518541a339f88352479df6a75605bd75`. Verdict: correct.

In FY2025 it reported a loss of NOK 1,089.

Citations: `3e3b4dc050be92d4d7f03b30226c8fc23b02122661f38b30f624f6c0dc9cb9cb`. Verdict: correct.

It has one registered workplace, in Hamar.

Citations: `e60806dc915f50fd6036e7a3fa7d8c867d5e561a82a870d537fb019640412997`. Verdict: correct.

No company website could be verified.

Citations: `b4d81929aa95878614f52d428035b111c1020dac6248a7358c8f3aab60a5ada3`. Verdict: correct.

No active job ads were found in the checked sources.

Citations: `3a96a79a9e606b2e44bace71985b937e3a0f0453d5fb588b560903ea334b8763`. Verdict: correct.

### 932137046

2012-KULLET E-KLASSEN VED PUS (org. 932137046) is an association in Tønsberg, founded in 2023, working in other activities of other membership organisations.

Citations: `748087c72749545c861f6a39ae550c32e6f20316737eb4f99024996ba6420bed`, `be3418ec655981c784be7fb67fd7863d65bbb8f4edd542e39110a5188817d82c`, `4b685063d41e5f737e7a61c1d2e977c0a77d54f0879899267eb478da78a393ec`, `317261170895091b42996bd662e5da8b7c5c414232a80aabf5e3c565c13ff5e8`, `466db8234be586b1c407883dfbabd591889b456d77c3d47391e754d3d2a2910d`, `86b988b1bbcc11cdd71d20813d69ab135fc393114795ac0fe9371a03faca3dfe`. Verdict: correct.

It has one registered workplace, in Tønsberg.

Citations: `0d3a9f6d6d4719ae87570d9c919084bd11dc7e007334fffbcc8cd3ba03bc837b`. Verdict: correct.

A registry announcement dated 29 Sep 2025 records a registered name change, according to the Brønnøysund Register.

Citations: `c178131b57da41ef01bf5dc902a0fe4d6327578cc4428216cca4bcf5bbfb5a83`. Verdict: correct.

No company website could be verified.

Citations: `484b1e8d5f11ab76990833116c90fbac223b1c02d32de2de786f6121dc57786a`. Verdict: correct.

Company-only accounts were not available in the checked sources; no active job ads were found in the checked sources.

Citations: `dc63c6e9c38cf77a1f0efd72be9736fbfd472e50d66f4ae3741c4dca8c86a4fb`, `28fa3bc1ff1244492e49ad3447c0ce425b6f7a0ee17e14d6ab5f64b963490b36`. Verdict: correct.

### 989115502

A. JENSET HOLDING AS (org. 989115502) is a private limited company in Molde, founded in 2005, working in other captive investment companies.

Citations: `01faeebfe70b6a714cbf77fcceebe7f20bd3662951f77085a5a67b8ebf461e42`, `5420db5b20708f42ab851432fe196a8c5b2ae8b453fd34928afef56e3e598a1e`, `72cbd3951e3e659e3cb30d2bd60a9c976683e0f58ed085dbbf78cb6906b0d182`, `816e7b08b3475b7db19496102db50ce8f8fc573e14defdbae2ac91dbafd867f1`, `b9d5e628e9b9c07169e6a8fabd3142c3aad7a653310d860ea3a95df0b44da9c9`, `74fa0c2ed4c94d0fdd4abca704aedcb3f61804577e238e53478605af2100a3e5`. Verdict: correct.

In FY2025 revenue and annual result were both NOK 0.

Citations: `1b5eb21bef928b06aa3086eecfeaca8cf9ad6ba30a1346f3215379841e2726de`, `e7b43c92ab681f4a7ad29f496ea6cb43a874df55167c99704ad831d0a62c3058`. Verdict: correct.

No company website could be verified.

Citations: `d74a29cb0474dc5d463922fe0205059e5acc69787aaeb48cc223a8be051f94d7`. Verdict: correct.

No active job ads were found in the checked sources.

Citations: `63afdf9c6a7a6db14f7d8eadca22f56066dc7018ce698ce59ff6a84139f2d7c4`. Verdict: correct.

### 936271316

A. BERG INNOVASJON & BÆREKRAFT FORENING (org. 936271316) is an association in Kongsberg, founded in 2025, working in other activities of other membership organisations.

Citations: `21f1adecbb8de93d645e66e41a3747c583086b9ea8890fbe5206aa103be2f076`, `4cdbfbd9de2c250464030c907e92232fab4f0d6a297e3d3f80928bfd4c50f57b`, `88fcc72b3914cd5ed419bd55e5b49ef19c8e52a8ae93edba40fb52689492c01c`, `0a2b0fa46cde1dc942dbc3da12c07d999fd8d65c020d18cbc259a2143703f851`, `cabe59c8b951b1d1787fa2d4d156e7b84e93faa6cffb5bb1b1e75819b9b52168`, `9fb14491638a367202716e8275704d75d9b3c62c02d28fe6d0f3819133e8aa53`. Verdict: correct.

It has one registered workplace, in Kongsberg.

Citations: `57a93009a9a7d86c94c4635a7a946816e588c197a71b49c8929b2f403561fe7b`. Verdict: correct.

No company website could be verified.

Citations: `87ca7a6b34b6d3317933a8c73022bb6a2c19ecbeca3c569f7ee462e29466c968`. Verdict: correct.

Company-only accounts were not available in the checked sources; no active job ads were found in the checked sources.

Citations: `56d0da695aec1e2bcd91744df6ea366ad69cf63a2f12d607796995d483993261`, `957f7f56c6f56d6834552426c2de58259c1af8abe72d4dfe0231ffcd2ac4f3ef`. Verdict: correct.

### 997071956

2 ROMERIKE ST GEORGS GILDE (org. 997071956) is an association in Oslo, founded in 1998, working in other activities of other membership organisations.

Citations: `b91c3b7d5695f969bdded5cc88e8c58e86da8216c66cae297c8b859a59d03ef8`, `e6f57836c8a4345321501d659ea452d8b39ac42c6c5a377a139439e9e02365de`, `67d2e4a74bc45616780fcac9ace2d57d2ce84e0582e53acda9b04c5fbf78d399`, `47ec9e3435c4ba39c5314a368ae3b42a1a890ba6f69b84a2ac48461456e9183f`, `87972654ae04e08343bd3adb4db07b8c9a1844e0b33d45ad58ac9bb24a19aa88`, `5b0bcdb0269cdec166e0847a79f3df424e4674afb870c011aaa9a7f7200b0010`. Verdict: correct.

No company website could be verified.

Citations: `15a90c2f05e7ead175f44d540099675a52b2262c8cd7250804492d94bfa3555e`. Verdict: correct.

Company-only accounts were not available in the checked sources; no active job ads were found in the checked sources.

Citations: `277a7c44f5b80353a39629c9ecfb940611c5511a8993f21ea99ef6a10d9f6d1f`, `d0c4e1fdf11e4522a1728325555c35be955bc37f7aa80d7fa3c6a187ea350466`. Verdict: correct.

### 916629966

2. LIER ST. GEORGS GILDE (org. 916629966) is an association, founded in 1962, working in other activities of other membership organisations.

Citations: `9204e56dfa4e4e07ee1415d2447cb423e25e3e2c834bb7b74666538300f36631`, `2165e18cc57db362acda8b97e5e0545dcaac64002ccde7d0bc9c9a9c5d7e9b78`, `31f97f2207a06677bde6e337ec725ef4879689ec0930846a8814cb3183d1b0b7`, `93c7b3729aa4d0aa41a9aadc0928d0b99833c90f5877dc18095e3c7ca41f19b5`, `390d97455ab442ad36865e9483f8a9e779de5fdda0f741885596b686ec4ff9b0`. Verdict: correct.

No company website could be verified.

Citations: `2b36de747bc7820a7b13dc37e8ee2d5f6808968c46d4111b3de8f460f561cbd2`. Verdict: correct.

Company-only accounts were not available in the checked sources; no active job ads were found in the checked sources.

Citations: `5a45175c11bfaa05366bf650be3adf30a143001054dee6e07efc4d0dfda5ef93`, `f01ad1020b6873b16c7f9752c9170b377b90d3a527c4bfb2df2d79cf705573bf`. Verdict: correct.

### 996687449

7START LTD NUF (org. 996687449) is a Norwegian branch of a foreign enterprise in Lyngdal, registered in 2011, working in computer programming activities.

Citations: `9eded5b95f3a729bf3d872c3dc2b8f9593a07a58054861adac443fbb7a812cc8`, `fe166916c2a2d073a56a0633142f0bba05dc4a6d6dc1e0ae2cd5f6a7eb7f9d6c`, `c54db8f3bb54c24729d6d14a3c611607ca5f6e08b9aa6bfd8eae65a49decc481`, `79d81386e5985b6021819a41d432b8425e2fa3c732d2787d9af9f78a679d784a`, `c436e6a4c3a78621ed40f6224093075a025a4742e9cea16c6e18f046104f18c1`, `a0c4206330b2a4c547366a6d9b45916dbd3ded16ceb57f631e6961a45d0d30d2`. Verdict: correct.

No company website could be verified.

Citations: `f163f13cb1357b61a80c711a70bfcea0ba23b42d0320dcce81f72920dd39741c`. Verdict: correct.

Company-only accounts were not available in the checked sources; no active job ads were found in the checked sources.

Citations: `79f121deacccfca55a1bc0394f18feceda4e933c107d72964c329370d2f27692`, `b20bbcc570e3786ddf9c06f1ecda61e15332f80cfc26c2b7992f8d87cf72588a`. Verdict: correct.

### 985872724

A. BEYER EIENDOM AS (org. 985872724) is a private limited company in Bergen, founded in 2003, working in rental and operating of own or leased real estate.

Citations: `4f95b072e78ef7d8dfbeb0abe93355c1c79e58068f37c5c949f2a8e39c81f4a1`, `416b27575df1ea12e520b11cf2e676639f1e0a6a8509b0767b2d624da182945c`, `764c1408acd7a296adf597810c386aa37a26b5ee1c78d098fdf02eb85376f5f7`, `7475170c857133749a4b0b5e9744b8b13d28dbc27691535576e4da693fec8e31`, `ce3647c9a13ce50e0bd645fca9757f661f8d538b2c6adf6ca3c0cef8a6210fd0`, `d44eb4e729f729c9cda24855577f37ae1fa4f98e53e6e89704dac8155d1dec6a`. Verdict: correct.

In FY2025 it reported revenue of NOK 1.9 million and an annual result of NOK 249,296, revenue rose 1140.2% from 2024.

Citations: `9f9dc3045ea9466abe8a5891f5ca8c4a3c0bb30d691266b4bcd7170930055ec3`, `b7f105aea268c28ef8eeadc6c10ff538f4a189387a0173ea34509e2bb7ffa1e4`, `cc3827902ace49a7f602a7b70e90ffe93d1342fd9de67fe5d1a1b8e577473a75`. Verdict: correct.

It has one registered workplace, in Bergen.

Citations: `5e8b5d6be5a904d880489a91ab1ac0fbe4d691e80193c73e42a42f1b36156ae4`. Verdict: correct.

A registry announcement dated 12 Sep 2025 records a business address change, according to the Brønnøysund Register.

Citations: `f8f0dd8e70044a0f012c882ca32bcbd4bd6f10f78fdd00d030036eee3d7472c6`. Verdict: correct.

No company website could be verified.

Citations: `f28093cd543fbe912b78bbce57f7637261f9516ad2279b3137d97936ea1da335`. Verdict: correct.

No active job ads were found in the checked sources.

Citations: `d13fe6e74b616690baf94fd499f41368f3547133fe5ae3dc67d19a7c77ead155`. Verdict: correct.

## Findings and corrections

Initial doubtful items: two 21-5 website/social items, and seven sampled account claims with unrelated methodological calibration citations. Values and periods in those seven account claims were correct. No positive wrong-company verdict is invented for the international 21-5 relationship; uncertainty triggers withholding.

Generic fix 1 compares a complete footer publisher legal-name core with the complete subject core; a substring such as Example in Example Norge AS is insufficient. Existing own-publisher prefixes and supplier-credit exclusions remain. The final carry-forward guard applies the same check. Five other reviewed sites remain valid.

Generic fix 2 removes other companies? calibration excerpts from account claim citations. Existing empirical unit metadata and all numeric values/claim IDs remain unchanged; exact-company BRREG evidence remains. Forty-two companies are affected by this evidence correction; one additional company by the website guard. All 43 are replayed offline for each saved snapshot, zero HTTP. Eight site-derived claims are withheld, including one website and one social URL.

Final retained review items: zero wrong, zero doubtful. Initial doubtful records and original outputs are preserved, not relabelled as originally correct. [Full ledger](review-ledger.json), [offline replay](offline-replay.json).
