# Step 20 source precision review

**20 GLEIF field claims, all 3 explicit parent claims and all 20 procurement awards reviewed: zero wrong-company items, zero wrong values or dates.** The twenty GLEIF field claims were selected with seed20261107. All awards were reviewed because there are exactly20; none was replaced.

GLEIF field values were compared with exact raw JSON pointers, including entity.registeredAs and RA000472 for every selected record. LEI registration dates are not company founding dates; next-renewal dates are future source fields, not completed events. Legal-form identifiers are labelled as codes.

| Company | Orgnr | Field | Source value | Verdict |
|---|---|---|---|---|
| BRAAUM INVEST AS | 998473195 | identity.gleif.renewal_date | "2027-05-24T11:42:54Z" | correct |
| BJØRGEN INVEST AS | 919690658 | identity.gleif.legal_form | {"id": "YI42", "other": null} | correct |
| EIDEFOSS VANNKRAFT AS | 923354220 | identity.gleif.registration_date | "2020-01-08T16:15:04Z" | correct |
| TANNLEGE HALVOR I. HOLTAN AS | 914896738 | identity.gleif.registration_date | "2020-03-14T18:29:29Z" | correct |
| OBJECTFRONT AS | 911885875 | identity.gleif.registration_date | "2021-07-05T12:45:57Z" | correct |
| STORHAMARSENTERET AS | 981058771 | identity.gleif.lei | "894500DZ0Z9ELGKQ5U08" | correct |
| LUCKY VIEW AS | 912189465 | identity.gleif.renewal_date | "2027-08-25T13:46:19Z" | correct |
| CHRISTHO AS | 988863262 | identity.gleif.legal_form | {"id": "YI42", "other": null} | correct |
| BJØRNNES AS | 992107294 | identity.gleif.lei | "8945006Q1JJ3K09C3747" | correct |
| H1 CAPITAL AS | 921678851 | identity.gleif.registration_date | "2019-08-02T14:32:00Z" | correct |
| BRAAUM INVEST AS | 998473195 | identity.gleif.legal_form | {"id": "YI42", "other": null} | correct |
| H1 CAPITAL AS | 921678851 | identity.gleif.entity_status | "ACTIVE" | correct |
| DEIGEN HOLDING AS | 992174676 | identity.gleif.renewal_date | "2027-09-18T10:31:39Z" | correct |
| NORTH TRAVEL AS | 935486807 | identity.gleif.legal_form | {"id": "YI42", "other": null} | correct |
| H1 CAPITAL AS | 921678851 | identity.gleif.renewal_date | "2027-11-04T14:10:07Z" | correct |
| KRIMS INVESTMENT AS | 992068434 | identity.gleif.legal_form | {"id": "YI42", "other": null} | correct |
| HAUGSTAD EIENDOM AS | 912507491 | identity.gleif.legal_form | {"id": "YI42", "other": null} | correct |
| GRAVITONIA AS | 998407257 | identity.gleif.renewal_date | "2027-08-24T15:43:06Z" | correct |
| NORDIC CREDIT RATING AS | 917685991 | identity.gleif.legal_form | {"id": "YI42", "other": null} | correct |
| BRAAUM INVEST AS | 998473195 | identity.gleif.lei | "89450029LLHOH7SVPQ33" | correct |

## Explicit parents

| Child | Type | Parent | Parent LEI | Parent Norwegian orgnr | Verdict |
|---|---|---|---|---|---|
| 999536999 | ultimate_parent | emagine Holding ApS | 98450065463AB3C5CE22 | not stated as Norwegian | correct |
| 923354220 | direct_parent | AS EIDEFOSS | 5967007LIEEXZXID2W97 | 911305631 | correct |
| 923354220 | ultimate_parent | AS EIDEFOSS | 5967007LIEEXZXID2W97 | 911305631 | correct |

Every child LEI/start node, parent LEI/end node, ACTIVE relationship type and parent legal-name record was checked. The Danish parent’s registration ID42019887 is not published as a Norwegian orgnr. AS EIDEFOSS911305631 is supported by its own RA000472 record. No parent is inferred from a name or a reporting exception.

## Procurement awards

| Company / orgnr | Notice / contract | Role | Award date | Reported linked-tender amount | Verdict |
|---|---|---|---|---|---|
| VEIDEKKE ENTREPRENØR AS / 984024290 | 418429-2026 / CON-0001 | winner | 2026-06-03 | 4e+08 NOK | correct |
| VEIDEKKE ENTREPRENØR AS / 984024290 | 627000-2026 / CON-0003 | winner | 2025-12-17 | 1.22e+07 NOK | correct |
| LEFDAL INSTALLASJON AS / 968545337 | 69164-2025 / CON-0004 | winner | 2025-01-16 | not stated / not uniquely attributable | correct |
| VEIDEKKE ENTREPRENØR AS / 984024290 | 288858-2025 / CON-0001 | winner | 2025-04-04 | 4.20114e+08 NOK | correct |
| EMAGINE AS / 999536999 | 461448-2025 / CON-0002 | winner | 2025-03-31 | 1.6e+07 NOK | correct |
| PERMOBIL AS / 930239070 | 475312-2026 / CON-0009 | winner | 2026-06-12 | not stated / not uniquely attributable | correct |
| NORDRE FOLLO RENSEANLEGG IKS / 971521570 | 287502-2026 / CON-0001 | buyer | 2026-03-27 | 1 NOK | correct |
| VEIDEKKE ENTREPRENØR AS / 984024290 | 741743-2025 / CON-0001 | winner | 2025-09-25 | 3.9124e+07 NOK | correct |
| VEIDEKKE ENTREPRENØR AS / 984024290 | 320357-2026 / CON-0001 | winner | 2026-04-24 | 6.75e+06 NOK | correct |
| VEIDEKKE ENTREPRENØR AS / 984024290 | 327030-2025 / CON-0001 | winner | 2025-04-28 | 1.10865e+08 NOK | correct |
| VEIDEKKE ENTREPRENØR AS / 984024290 | 434277-2025 / CON-0001 | winner | 2025-05-16 | 1.19e+08 NOK | correct |
| FEIE- OG TILSYNSTJENESTER AS / 993919675 | 341549-2025 / CON-0001 | winner | 2025-05-09 | 8.5296e+06 NOK | correct |
| NORDRE FOLLO RENSEANLEGG IKS / 971521570 | 640353-2025 / CON-0002 | buyer | 2025-09-11 | 1 NOK | correct |
| VEIDEKKE ENTREPRENØR AS / 984024290 | 690844-2026 / CON-0001 | winner | 2026-09-21 | 9.95866e+07 NOK | correct |
| VEIDEKKE ENTREPRENØR AS / 984024290 | 39027-2025 / CON-0002 | winner | 2024-12-18 | not stated / not uniquely attributable | correct |
| LEFDAL INSTALLASJON AS / 968545337 | 295084-2026 / CON-0001 | winner | 2026-03-26 | 1.38217e+08 NOK | correct |
| NORDRE FOLLO RENSEANLEGG IKS / 971521570 | 741466-2024 / CON-0001 | buyer | 2024-11-11 | not stated / not uniquely attributable | correct |
| PERMOBIL AS / 930239070 | 475312-2026 / CON-0007 | winner | 2026-06-12 | not stated / not uniquely attributable | correct |
| NORDRE FOLLO RENSEANLEGG IKS / 971521570 | 640353-2025 / CON-0001 | buyer | 2025-09-11 | 1 NOK | correct |
| VEIDEKKE ENTREPRENØR AS / 984024290 | 198485-2025 / CON-0001 | winner | 2025-03-14 | not stated / not uniquely attributable | correct |

Each award was traced through raw organisation national ID, buyer or tenderer role, tendering party, linked tender and settled contract. Title, buyer names and award date match the XML. Public procurement awards remain separate from company news and registry announcements.

**Amounts use only the unique linked tender for the matched winner, or the single awarded tender when the company is the buyer. Notice-wide totals and amounts for other tenders/winners are never substituted.** Fourteen awards have a stated attributable amount; six have no published amount. Source values of NOK1 are reproduced as reported tender values, not interpreted as actual expenditure or replaced with an invented estimate. No currency conversion or apportionment is made.

The review found the real eForms nested LegalMonetaryTotal layout; the parser and fixture were corrected before final validation. The14 amounts were re-extracted offline from unchanged XML with zero new requests. Pre-correction output bytes remain compressed with SHA256 at the saved continuation’s before-amounts folder. This is an omitted-field repair, not a change to matching/proof rules.

[GLEIF raw pointers and exact identity bindings](GLEIF-review.json), [all parent records and edges](parents-review.json), [all award records, XML party/tender/contract fragments and evidence](tender-review.json), [independent amount/party checks](tender-independent-checks.json), [old/new amount values and IDs](amount-projection.json).

## Website recovery

The only newly available website versus Step18 is KONSEPTBYGG EIENDOM AS970979026: https://konseptbygg.no/kontakt.html explicitly says “Konseptbygg Eiendom AS: NO970979026” (source has spaced digits). The exact saved span is retained in [website-social-delta.json](website-social-delta.json). Correct company; prior run had robots502. There are zero new social URLs. This recovery is live-source variation, not a GLEIF/TED website nomination.