# NAV manual audit

Checked on 2026-11-06 against the public Arbeidsplassen search page with a seeded random sample of 20 companies from benchmark input `20261106T051206156765Z-ed54729` (seed 6). The process had no `NAV_API_TOKEN`. For each legal name, the audit opened the public search page and checked up to eight returned ad pages; only pages with `status=ACTIVE`, unexpired `expires`, and employer orgnr equal to the company or a registered subunit counted as a match.

| Org nr | Company | Search result IDs | Public ad pages checked | Published by run | Active exact-scope ads | Missed |
|---|---|---:|---:|---:|---:|---:|
| 987909889 | BOREA ASSET MANAGEMENT AS | 2 | 2 | 0 | 0 | 0 |
| 935189365 | HESTENES KRAFTVERK AS | 1 | 1 | 0 | 0 | 0 |
| 989232401 | NORE AUTO HOLDING AS | 1 | 1 | 0 | 0 | 0 |
| 910484435 | PAUL BERG EIENDOM AS | 1 | 1 | 0 | 0 | 0 |
| 931745271 | SAMEIET SVILANDVEIEN 108C | 1 | 1 | 0 | 0 | 0 |
| 984470835 | ALSTEN MANAGEMENT AS | 1 | 1 | 0 | 0 | 0 |
| 921678851 | H1 CAPITAL AS | 1 | 1 | 0 | 0 | 0 |
| 831447842 | ALLIANSE PSYKOLOGKLINIKK AS | 1 | 1 | 0 | 0 | 0 |
| 810363142 | BJØRNSTJERNE BJØRNSONSGATE AS | 1 | 1 | 0 | 0 | 0 |
| 915216102 | EPICURE NORWAY AS | 1 | 1 | 0 | 0 | 0 |
| 956329132 | MYHRE INVEST AS | 1 | 1 | 0 | 0 | 0 |
| 935486807 | NORTH TRAVEL AS | 2 | 2 | 0 | 0 | 0 |
| 931011642 | BALANSE BYGG HOLDING AS | 8 | 8 | 0 | 0 | 0 |
| 998990793 | SAMEIET BAKKESTUMPEN | 1 | 1 | 0 | 0 | 0 |
| 984133715 | OSLOBILUTLEIE.NO AS | 1 | 1 | 0 | 0 | 0 |
| 981613171 | CREATI ESTATE AS | 1 | 1 | 0 | 0 | 0 |
| 927409593 | RESSURS ACCOUNTING AS | 7 | 7 | 0 | 0 | 0 |
| 925273422 | OMJ ENTREPRENØR AS | 1 | 1 | 0 | 0 | 0 |
| 985090572 | MUSIKKGARASJEN AS | 1 | 1 | 0 | 0 | 0 |
| 824357552 | BALSFJORD NÆRINGSUTVIKLING AS | 1 | 1 | 0 | 0 | 0 |

**Sample totals:** published 0; manually verified active exact-scope ads 0; missed 0. Search-page UUIDs with 404 or unparseable pages were retained in `NAV_AUDIT.json` and did not count as active ads.

## The three run-level job claims

| Parent company | Registered subunit / employer org nr | Ad | Manual page status | Expires | Verdict |
|---|---:|---|---|---|---|
| ROLIDBAKKEN FUS BARNEHAGE AS (991247610) | 931166492 | [public ad](https://arbeidsplassen.nav.no/stillinger/stilling/bdb50d18-4cdb-485f-a8cf-f861927dd9ca) | ACTIVE | 2026-11-12T23:00:00Z | Correct: exact registered subunit match |
| CL BYGG & EIENDOM AS (917283109) | 998671175 | [public ad](https://arbeidsplassen.nav.no/stillinger/stilling/dc6921ca-b513-40d6-a0b3-937ca398e779) | ACTIVE | 2026-11-08T22:59:59Z | Correct: exact registered subunit match |
| NORLANDIA ENGA BARNEHAGE AS (930202894) | 997453964 | [public ad](https://arbeidsplassen.nav.no/stillinger/stilling/c0349976-bbfc-41f4-a980-b482f06e5f2d) | ACTIVE | 2026-11-25T23:00:00Z | Correct: exact registered subunit match |

The 20-company random sample contained no active exact-scope ads and no missed ads. The three jobs emitted elsewhere in the 1000-company run were each manually checked on their public page; all were active, unexpired, and their employer orgnr exactly matched the registered subunit shown in the run profile.
