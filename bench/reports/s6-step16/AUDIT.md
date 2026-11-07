# Step 16 pre-code saved-response field audit

{"run": "bench\\runs\\20261106T183808924157Z-1db7047", "companies": 1000, "blobs_sha256_verified": 3996, "unpublished_fact_paths": 64, "companies_with_unpublished_facts": 1000, "technical_paths": 19, "threshold_met": true, "note": "Source leaf paths; repeated indices normalized to *. Fields already carried in structured claim values count as published. Reporting-period metadata is distinguished from standalone claims. CSV identity rows were used by this frozen run, not per-company identity JSON. No new requests."}

| Family | Unpublished source path | Companies | Two example values |
|---|---|---:|---|
| accounts | `/*/avviklingsregnskap` | 999 | false; true |
| accounts | `/*/egenkapitalGjeld/egenkapital/innskuttEgenkapital/sumInnskuttEgenkaptial` | 19 | 100000.0; 7932454.0 |
| accounts | `/*/egenkapitalGjeld/egenkapital/opptjentEgenkapital/sumOpptjentEgenkapital` | 19 | 79637000.0; 74347000.0 |
| accounts | `/*/egenkapitalGjeld/egenkapital/sumEgenkapital` | 19 | 79737000.0; 74447000.0 |
| accounts | `/*/egenkapitalGjeld/gjeldOversikt/kortsiktigGjeld/sumKortsiktigGjeld` | 19 | 46278000.0; 33947000.0 |
| accounts | `/*/egenkapitalGjeld/gjeldOversikt/langsiktigGjeld/sumLangsiktigGjeld` | 19 | 2211000.0; 6433000.0 |
| accounts | `/*/egenkapitalGjeld/gjeldOversikt/sumGjeld` | 19 | 48489000.0; 40380000.0 |
| accounts | `/*/egenkapitalGjeld/sumEgenkapitalGjeld` | 19 | 128226000.0; 114827000.0 |
| accounts | `/*/eiendeler/anleggsmidler/sumAnleggsmidler` | 19 | 24068000.0; 55668000.0 |
| accounts | `/*/eiendeler/goodwill` | 9 | 23799315.0; 12932753.0 |
| accounts | `/*/eiendeler/omloepsmidler/sumOmloepsmidler` | 19 | 104159000.0; 59159000.0 |
| accounts | `/*/eiendeler/sumBankinnskuddOgKontanter` | 19 | 42336000.0; 9460000.0 |
| accounts | `/*/eiendeler/sumEiendeler` | 19 | 128226000.0; 114827000.0 |
| accounts | `/*/eiendeler/sumFordringer` | 19 | 59130000.0; 36981000.0 |
| accounts | `/*/eiendeler/sumInvesteringer` | 8 | 68400000.0; 75315285.0 |
| accounts | `/*/eiendeler/sumVarer` | 15 | 2692000.0; 12718000.0 |
| accounts | `/*/oppstillingsplan` | 999 | "store"; "store" |
| accounts | `/*/regnkapsprinsipper/regnskapsregler` | 999 | "regnskapslovenAlminneligRegler"; "forenkletAnvendelseIFRS" |
| accounts | `/*/regnkapsprinsipper/smaaForetak` | 999 | true; false |
| accounts | `/*/regnskapsperiode/fraDato` | 999 | "2023-01-01"; "2024-01-01" |
| accounts | `/*/regnskapsperiode/tilDato` | 999 | "2023-12-31"; "2024-12-31" |
| accounts | `/*/regnskapstype` | 999 | "SELSKAP"; "KONSERN" |
| accounts | `/*/resultatregnskapResultat/aarsresultat` | 19 | 13491000.0; 9210000.0 |
| accounts | `/*/resultatregnskapResultat/driftsresultat/driftsinntekter/salgsinntekter` | 19 | 178248000.0; 137198000.0 |
| accounts | `/*/resultatregnskapResultat/driftsresultat/driftsinntekter/sumDriftsinntekter` | 19 | 179039000.0; 138703000.0 |
| accounts | `/*/resultatregnskapResultat/driftsresultat/driftskostnad/loennskostnad` | 18 | 67892000.0; 63480000.0 |
| accounts | `/*/resultatregnskapResultat/driftsresultat/driftskostnad/sumDriftskostnad` | 19 | 160822000.0; 126680000.0 |
| accounts | `/*/resultatregnskapResultat/driftsresultat/driftsresultat` | 19 | 18216000.0; 12023000.0 |
| accounts | `/*/resultatregnskapResultat/ekstraordinaerePoster` | 2 | -386965.0; 0.0 |
| accounts | `/*/resultatregnskapResultat/finansresultat/finansinntekt/sumFinansinntekter` | 19 | 26000.0; 198000.0 |
| accounts | `/*/resultatregnskapResultat/finansresultat/finanskostnad/annenRentekostnad` | 15 | 8979591.0; 19124113.0 |
| accounts | `/*/resultatregnskapResultat/finansresultat/finanskostnad/sumFinanskostnad` | 19 | 262000.0; 420000.0 |
| accounts | `/*/resultatregnskapResultat/finansresultat/nettoFinans` | 19 | -236000.0; -222000.0 |
| accounts | `/*/resultatregnskapResultat/ordinaertResultatFoerSkattekostnad` | 19 | 17981000.0; 11801000.0 |
| accounts | `/*/resultatregnskapResultat/ordinaertResultatSkattekostnad` | 19 | 4489000.0; 2591000.0 |
| accounts | `/*/resultatregnskapResultat/skattekostnadEkstraordinaertResultat` | 3 | 0.0; 0.0 |
| accounts | `/*/resultatregnskapResultat/totalresultat` | 7 | 21093387.0; -1849937.0 |
| accounts | `/*/revisjon/fravalgRevisjon` | 999 | true; false |
| accounts | `/*/revisjon/ikkeRevidertAarsregnskap` | 999 | false; false |
| accounts | `/*/valuta` | 999 | "NOK"; "EUR" |
| accounts | `/*/virksomhet/morselskap` | 999 | false; true |
| accounts | `/*/virksomhet/organisasjonsform` | 999 | "AS"; "ESEK" |
| identity | `/forretningsadresse.landkode` | 994 | "NO"; "AT" |
| identity | `/frivilligMvaRegistrertBeskrivelser` | 92 | "Utleier av bygg eller anlegg"; "Stille baneanlegg til disposisjon, Utleier av bygg eller anlegg" |
| identity | `/historiskeNavn/*/fraDato` | 1 | "2020-03-24 18:27:39" |
| identity | `/historiskeNavn/*/navn` | 1 | "UN17 CONSULT AS" |
| identity | `/historiskeNavn/*/tilDato` | 1 | "2020-04-22 16:44:44" |
| identity | `/paategninger` | 997 | "false"; "false" |
| identity | `/postadresse.landkode` | 207 | "NO"; "DK" |
| identity | `/respons_klasse` | 3 | "SlettetEnhet"; "SlettetEnhet" |
| roles | `/rollegrupper/*/roller/*/bostyrer/erDoed` | 3 | false; false |
| roles | `/rollegrupper/*/roller/*/bostyrer/navn` | 3 | "Adv. Per Ove Sørholt"; "Adv. Ole Daniel Fuglerud Danbolt" |
| roles | `/rollegrupper/*/roller/*/bostyrer/postadresse/adresse/*` | 3 | "Postboks 233"; "Postboks 37" |
| roles | `/rollegrupper/*/roller/*/bostyrer/postadresse/landkode` | 3 | "NO"; "NO" |
| roles | `/rollegrupper/*/roller/*/bostyrer/postadresse/postnummer` | 3 | "7601"; "3836" |
| roles | `/rollegrupper/*/roller/*/bostyrer/postadresse/poststed` | 3 | "LEVANGER"; "KVITESEID" |
| roles | `/rollegrupper/*/roller/*/person/erDoed` | 997 | false; true |
| roles | `/rollegrupper/*/roller/*/person/fodselsdato` | 997 | "1977-11-17"; "1961-10-17" |
| subunits | `/_embedded/underenheter/*/historiskeNavn/*/fraDato` | 210 | "2017-05-11 20:09:14"; "2015-12-17 15:34:40" |
| subunits | `/_embedded/underenheter/*/historiskeNavn/*/navn` | 210 | "SQ URBAN LANDSKAP QUILAMBO"; "KLEVEN MARITIME AS" |
| subunits | `/_embedded/underenheter/*/historiskeNavn/*/tilDato` | 210 | "2018-03-01 21:11:27"; "2018-09-10 16:34:01" |
| subunits | `/_embedded/underenheter/*/naeringskode2/beskrivelse` | 3 | "Reparasjon og vedlikehold av motorvogner"; "Produksjon av treemballasje" |
| subunits | `/_embedded/underenheter/*/naeringskode2/kode` | 3 | "95.310"; "16.240" |
| subunits | `/_embedded/underenheter/*/respons_klasse` | 774 | "Underenhet"; "Underenhet" |

Transport links/pagination/source IDs and already-output organisation scope are separately listed in audit.json; they do not satisfy the fact threshold. All examples retain exact source URL, locator and verified SHA-256 in that ledger.
