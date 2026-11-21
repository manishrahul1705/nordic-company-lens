# Stage AY — saved-field completeness

All sources below are saved responses. Replay made zero HTTP requests. Counts are available claims, including multiple reporting periods and subunits.

## New claims and verification

| Cohort | Identity | Roles | Accounts | Subunits |
|---|---:|---:|---:|---:|
| jury100 | 2,615 → 4,021 (+1,406) | 1,134 → 2,731 (+1,597) | 4,637 → 4,891 (+254) | 559 → 1,433 (+874) |
| final1000 | 31,241 → 48,334 (+17,093) | 18,783 → 43,250 (+24,467) | 100,233 → 105,867 (+5,634) | 6,907 → 17,664 (+10,757) |

## Brand replay

Unseen 300: 4 existing brands, 2 changes. Frozen 1,000: 19 existing brands, 0 changes. Zero HTTP. All changes:

- `919856807`: "Экскурсионные туры в Норвегию от Uniktur" → null (`https://www.unikturs.com/`)
- `912493865`: "A. Olufsen Ship & Offshore | Haugesund" → "A. Olufsen Ship & Offshore" (`https://aoso.no/`)

The strict saved-source verifier passed on the full 316-row jury output and frozen 1,000. Fifteen new claims across the four families were checked against exact JSON values, source hashes, and verbatim spans in `handchecks.json`. Large replay envelopes were removed after verification to preserve the disk reserve; `stage_ay_offline_replay.py` recreates them from the saved blobs.

All numeric accounts statement leaves were already published. Existing exact claims also cover the identity MVA/registry and employee-count flags, statute date, role birth year, and subunit start dates. New scalar claims split cited address, industry, sector, capital, role metadata, holder entity, and subunit fields out of existing composite values. Filing ID and journal number are source values, not constructed links. Remaining gaps are source metadata, empty containers, subject IDs, or values already represented by an existing composite claim (including person name parts and historical names).

Corrected shared-taxonomy recall: Nordic **29.2621 → 30.0618 / 50**, rank **1 → 1** among 40 measured agents. The ten corrected families and every agent's components are in `corrected-recall.json`. This is a local proxy, not the Builderr board score.

## Exhaustive raw JSON paths

Each row is a normalized JSON leaf path in at least one saved response. `Exact before` means the original output had a claim citing that exact locator; `within composite` means it fell under a cited object claim. Empty containers and response metadata appear too, for completeness. The identical machine-readable inventory is in `field-inventory.json`.

### jury100

#### identity (38 paths without exact publication for at least one company)

| JSON path | Present | Exact before | Within composite |
|---|---:|---:|---:|
| `/_links/self/href` | 100 | 0 | 0 |
| `/aktivitet/*` | 100 | 0 | 100 |
| `/forretningsadresse/adresse/*` | 98 | 0 | 98 |
| `/forretningsadresse/kommunenummer` | 97 | 0 | 97 |
| `/forretningsadresse/land` | 98 | 0 | 98 |
| `/forretningsadresse/postnummer` | 97 | 0 | 97 |
| `/forretningsadresse/poststed` | 98 | 0 | 98 |
| `/frivilligMvaRegistrertBeskrivelser/*` | 3 | 0 | 3 |
| `/historiskeNavn` | 84 | 0 | 0 |
| `/historiskeNavn/*/fraDato` | 16 | 0 | 16 |
| `/historiskeNavn/*/navn` | 16 | 0 | 16 |
| `/historiskeNavn/*/tilDato` | 16 | 0 | 16 |
| `/hjelpeenhetskode/beskrivelse` | 5 | 0 | 5 |
| `/hjelpeenhetskode/kode` | 5 | 0 | 5 |
| `/institusjonellSektorkode/beskrivelse` | 98 | 0 | 98 |
| `/institusjonellSektorkode/kode` | 98 | 0 | 98 |
| `/kapital/antallAksjer` | 46 | 0 | 46 |
| `/kapital/belop` | 47 | 0 | 47 |
| `/kapital/innfortDato` | 47 | 0 | 47 |
| `/kapital/type` | 47 | 0 | 47 |
| `/kapital/valuta` | 47 | 0 | 47 |
| `/naeringskode1/beskrivelse` | 100 | 0 | 100 |
| `/naeringskode1/kode` | 100 | 0 | 100 |
| `/naeringskode2/beskrivelse` | 3 | 0 | 3 |
| `/naeringskode2/kode` | 3 | 0 | 3 |
| `/organisasjonsform/_links/self/href` | 100 | 0 | 100 |
| `/organisasjonsform/beskrivelse` | 100 | 0 | 100 |
| `/organisasjonsform/kode` | 100 | 0 | 100 |
| `/organisasjonsnummer` | 100 | 0 | 0 |
| `/paategninger` | 100 | 8 | 0 |
| `/postadresse/adresse/*` | 12 | 0 | 12 |
| `/postadresse/kommune` | 10 | 0 | 10 |
| `/postadresse/kommunenummer` | 10 | 0 | 10 |
| `/postadresse/land` | 12 | 0 | 12 |
| `/postadresse/postnummer` | 10 | 0 | 10 |
| `/postadresse/poststed` | 12 | 0 | 12 |
| `/respons_klasse` | 100 | 0 | 0 |
| `/vedtektsfestetFormaal/*` | 47 | 0 | 47 |

#### roles (22 paths without exact publication for at least one company)

| JSON path | Present | Exact before | Within composite |
|---|---:|---:|---:|
| `/_links/enhet/href` | 100 | 0 | 0 |
| `/_links/self/href` | 100 | 0 | 0 |
| `/rollegrupper/*/roller/*/avregistrert` | 100 | 0 | 100 |
| `/rollegrupper/*/roller/*/enhet/_links/self/href` | 51 | 0 | 51 |
| `/rollegrupper/*/roller/*/enhet/navn/*` | 51 | 0 | 51 |
| `/rollegrupper/*/roller/*/enhet/organisasjonsform/_links/self/href` | 51 | 0 | 51 |
| `/rollegrupper/*/roller/*/enhet/organisasjonsform/beskrivelse` | 51 | 0 | 51 |
| `/rollegrupper/*/roller/*/enhet/organisasjonsform/kode` | 51 | 0 | 51 |
| `/rollegrupper/*/roller/*/enhet/organisasjonsnummer` | 51 | 0 | 51 |
| `/rollegrupper/*/roller/*/person/navn/etternavn` | 99 | 0 | 99 |
| `/rollegrupper/*/roller/*/person/navn/fornavn` | 99 | 0 | 99 |
| `/rollegrupper/*/roller/*/person/navn/mellomnavn` | 35 | 0 | 35 |
| `/rollegrupper/*/roller/*/type/_links/self/href` | 100 | 0 | 100 |
| `/rollegrupper/*/roller/*/type/beskrivelse` | 100 | 0 | 100 |
| `/rollegrupper/*/roller/*/type/kode` | 100 | 0 | 100 |
| `/rollegrupper/*/roller/*/valgtAv/_links/self/href` | 1 | 0 | 1 |
| `/rollegrupper/*/roller/*/valgtAv/beskrivelse` | 1 | 0 | 1 |
| `/rollegrupper/*/roller/*/valgtAv/kode` | 1 | 0 | 1 |
| `/rollegrupper/*/sistEndret` | 100 | 0 | 0 |
| `/rollegrupper/*/type/_links/self/href` | 100 | 0 | 0 |
| `/rollegrupper/*/type/beskrivelse` | 100 | 0 | 0 |
| `/rollegrupper/*/type/kode` | 100 | 0 | 0 |

#### accounts (12 paths without exact publication for at least one company)

| JSON path | Present | Exact before | Within composite |
|---|---:|---:|---:|
| `/*/egenkapitalGjeld/egenkapital/innskuttEgenkapital` | 2 | 0 | 0 |
| `/*/egenkapitalGjeld/egenkapital/opptjentEgenkapital` | 1 | 0 | 0 |
| `/*/egenkapitalGjeld/gjeldOversikt/kortsiktigGjeld` | 2 | 0 | 0 |
| `/*/egenkapitalGjeld/gjeldOversikt/langsiktigGjeld` | 25 | 0 | 0 |
| `/*/eiendeler/anleggsmidler` | 5 | 0 | 0 |
| `/*/id` | 46 | 0 | 0 |
| `/*/journalnr` | 46 | 0 | 0 |
| `/*/resultatregnskapResultat/driftsresultat/driftsinntekter` | 8 | 0 | 0 |
| `/*/resultatregnskapResultat/driftsresultat/driftskostnad` | 1 | 0 | 0 |
| `/*/resultatregnskapResultat/finansresultat/finansinntekt` | 11 | 0 | 0 |
| `/*/resultatregnskapResultat/finansresultat/finanskostnad` | 9 | 0 | 0 |
| `/*/virksomhet/organisasjonsnummer` | 46 | 0 | 0 |

#### subunits (39 paths without exact publication for at least one company)

| JSON path | Present | Exact before | Within composite |
|---|---:|---:|---:|
| `/_embedded/underenheter/*/_links/overordnetEnhet/href` | 72 | 0 | 72 |
| `/_embedded/underenheter/*/_links/self/href` | 72 | 0 | 72 |
| `/_embedded/underenheter/*/antallAnsatte` | 9 | 0 | 9 |
| `/_embedded/underenheter/*/beliggenhetsadresse/adresse/*` | 72 | 0 | 72 |
| `/_embedded/underenheter/*/beliggenhetsadresse/kommune` | 71 | 0 | 71 |
| `/_embedded/underenheter/*/beliggenhetsadresse/kommunenummer` | 71 | 0 | 71 |
| `/_embedded/underenheter/*/beliggenhetsadresse/land` | 72 | 0 | 72 |
| `/_embedded/underenheter/*/beliggenhetsadresse/landkode` | 72 | 0 | 72 |
| `/_embedded/underenheter/*/beliggenhetsadresse/postnummer` | 71 | 0 | 71 |
| `/_embedded/underenheter/*/beliggenhetsadresse/poststed` | 72 | 0 | 72 |
| `/_embedded/underenheter/*/historiskeNavn` | 58 | 0 | 58 |
| `/_embedded/underenheter/*/historiskeNavn/*/fraDato` | 14 | 0 | 14 |
| `/_embedded/underenheter/*/historiskeNavn/*/navn` | 14 | 0 | 14 |
| `/_embedded/underenheter/*/historiskeNavn/*/tilDato` | 14 | 0 | 14 |
| `/_embedded/underenheter/*/hjelpeenhetskode/beskrivelse` | 2 | 0 | 2 |
| `/_embedded/underenheter/*/hjelpeenhetskode/kode` | 2 | 0 | 2 |
| `/_embedded/underenheter/*/naeringskode1/beskrivelse` | 71 | 0 | 71 |
| `/_embedded/underenheter/*/naeringskode1/kode` | 71 | 0 | 71 |
| `/_embedded/underenheter/*/naeringskode2/beskrivelse` | 2 | 0 | 2 |
| `/_embedded/underenheter/*/naeringskode2/kode` | 2 | 0 | 2 |
| `/_embedded/underenheter/*/navn` | 72 | 0 | 72 |
| `/_embedded/underenheter/*/organisasjonsform/_links/self/href` | 72 | 0 | 72 |
| `/_embedded/underenheter/*/organisasjonsform/beskrivelse` | 72 | 0 | 72 |
| `/_embedded/underenheter/*/organisasjonsform/kode` | 72 | 0 | 72 |
| `/_embedded/underenheter/*/organisasjonsnummer` | 72 | 0 | 72 |
| `/_embedded/underenheter/*/overordnetEnhet` | 72 | 0 | 72 |
| `/_embedded/underenheter/*/postadresse/adresse/*` | 9 | 0 | 9 |
| `/_embedded/underenheter/*/postadresse/kommune` | 9 | 0 | 9 |
| `/_embedded/underenheter/*/postadresse/kommunenummer` | 9 | 0 | 9 |
| `/_embedded/underenheter/*/postadresse/land` | 9 | 0 | 9 |
| `/_embedded/underenheter/*/postadresse/landkode` | 9 | 0 | 9 |
| `/_embedded/underenheter/*/postadresse/postnummer` | 9 | 0 | 9 |
| `/_embedded/underenheter/*/postadresse/poststed` | 9 | 0 | 9 |
| `/_embedded/underenheter/*/respons_klasse` | 72 | 0 | 72 |
| `/_links/self/href` | 100 | 0 | 0 |
| `/page/number` | 100 | 0 | 0 |
| `/page/size` | 100 | 0 | 0 |
| `/page/totalElements` | 100 | 0 | 0 |
| `/page/totalPages` | 100 | 0 | 0 |

### final1000

#### identity (42 paths without exact publication for at least one company)

| JSON path | Present | Exact before | Within composite |
|---|---:|---:|---:|
| `/_links/self/href` | 1000 | 0 | 0 |
| `/aktivitet/*` | 997 | 0 | 997 |
| `/forretningsadresse/adresse` | 4 | 0 | 4 |
| `/forretningsadresse/adresse/*` | 990 | 0 | 990 |
| `/forretningsadresse/kommunenummer` | 990 | 0 | 990 |
| `/forretningsadresse/land` | 994 | 0 | 994 |
| `/forretningsadresse/postnummer` | 990 | 0 | 990 |
| `/forretningsadresse/poststed` | 994 | 0 | 994 |
| `/frivilligMvaRegistrertBeskrivelser/*` | 93 | 0 | 93 |
| `/historiskeNavn` | 759 | 0 | 0 |
| `/historiskeNavn/*/fraDato` | 241 | 0 | 241 |
| `/historiskeNavn/*/navn` | 241 | 0 | 241 |
| `/historiskeNavn/*/tilDato` | 241 | 0 | 241 |
| `/hjelpeenhetskode/beskrivelse` | 76 | 0 | 76 |
| `/hjelpeenhetskode/kode` | 76 | 0 | 76 |
| `/institusjonellSektorkode/beskrivelse` | 969 | 0 | 969 |
| `/institusjonellSektorkode/kode` | 969 | 0 | 969 |
| `/kapital/antallAksjer` | 894 | 0 | 894 |
| `/kapital/belop` | 917 | 0 | 917 |
| `/kapital/fulltInnbetalt` | 12 | 0 | 12 |
| `/kapital/innbetalt` | 12 | 0 | 12 |
| `/kapital/innfortDato` | 917 | 0 | 917 |
| `/kapital/type` | 917 | 0 | 917 |
| `/kapital/valuta` | 917 | 0 | 917 |
| `/naeringskode1/beskrivelse` | 996 | 0 | 996 |
| `/naeringskode1/kode` | 996 | 0 | 996 |
| `/naeringskode2/beskrivelse` | 6 | 0 | 6 |
| `/naeringskode2/kode` | 6 | 0 | 6 |
| `/organisasjonsform/_links/self/href` | 1000 | 0 | 1000 |
| `/organisasjonsform/beskrivelse` | 1000 | 0 | 1000 |
| `/organisasjonsform/kode` | 1000 | 0 | 1000 |
| `/organisasjonsnummer` | 1000 | 0 | 0 |
| `/paategninger` | 997 | 70 | 0 |
| `/postadresse/adresse` | 1 | 0 | 1 |
| `/postadresse/adresse/*` | 206 | 0 | 206 |
| `/postadresse/kommune` | 205 | 0 | 205 |
| `/postadresse/kommunenummer` | 205 | 0 | 205 |
| `/postadresse/land` | 207 | 0 | 207 |
| `/postadresse/postnummer` | 205 | 0 | 205 |
| `/postadresse/poststed` | 207 | 0 | 207 |
| `/respons_klasse` | 1000 | 0 | 0 |
| `/vedtektsfestetFormaal/*` | 962 | 0 | 962 |

#### roles (28 paths without exact publication for at least one company)

| JSON path | Present | Exact before | Within composite |
|---|---:|---:|---:|
| `/_links/enhet/href` | 997 | 0 | 0 |
| `/_links/self/href` | 997 | 0 | 0 |
| `/rollegrupper/*/roller/*/avregistrert` | 997 | 0 | 997 |
| `/rollegrupper/*/roller/*/bostyrer/erDoed` | 3 | 0 | 3 |
| `/rollegrupper/*/roller/*/bostyrer/navn` | 3 | 0 | 3 |
| `/rollegrupper/*/roller/*/bostyrer/postadresse/adresse/*` | 3 | 0 | 3 |
| `/rollegrupper/*/roller/*/bostyrer/postadresse/landkode` | 3 | 0 | 3 |
| `/rollegrupper/*/roller/*/bostyrer/postadresse/postnummer` | 3 | 0 | 3 |
| `/rollegrupper/*/roller/*/bostyrer/postadresse/poststed` | 3 | 0 | 3 |
| `/rollegrupper/*/roller/*/enhet/_links/self/href` | 800 | 0 | 800 |
| `/rollegrupper/*/roller/*/enhet/navn/*` | 800 | 0 | 800 |
| `/rollegrupper/*/roller/*/enhet/organisasjonsform/_links/self/href` | 800 | 0 | 800 |
| `/rollegrupper/*/roller/*/enhet/organisasjonsform/beskrivelse` | 800 | 0 | 800 |
| `/rollegrupper/*/roller/*/enhet/organisasjonsform/kode` | 800 | 0 | 800 |
| `/rollegrupper/*/roller/*/enhet/organisasjonsnummer` | 800 | 0 | 800 |
| `/rollegrupper/*/roller/*/person/navn/etternavn` | 997 | 0 | 997 |
| `/rollegrupper/*/roller/*/person/navn/fornavn` | 997 | 0 | 997 |
| `/rollegrupper/*/roller/*/person/navn/mellomnavn` | 391 | 0 | 391 |
| `/rollegrupper/*/roller/*/type/_links/self/href` | 997 | 0 | 997 |
| `/rollegrupper/*/roller/*/type/beskrivelse` | 997 | 0 | 997 |
| `/rollegrupper/*/roller/*/type/kode` | 997 | 0 | 997 |
| `/rollegrupper/*/roller/*/valgtAv/_links/self/href` | 85 | 0 | 85 |
| `/rollegrupper/*/roller/*/valgtAv/beskrivelse` | 85 | 0 | 85 |
| `/rollegrupper/*/roller/*/valgtAv/kode` | 85 | 0 | 85 |
| `/rollegrupper/*/sistEndret` | 997 | 0 | 0 |
| `/rollegrupper/*/type/_links/self/href` | 997 | 0 | 0 |
| `/rollegrupper/*/type/beskrivelse` | 997 | 0 | 0 |
| `/rollegrupper/*/type/kode` | 997 | 0 | 0 |

#### accounts (13 paths without exact publication for at least one company)

| JSON path | Present | Exact before | Within composite |
|---|---:|---:|---:|
| `/*/egenkapitalGjeld/egenkapital/innskuttEgenkapital` | 51 | 0 | 0 |
| `/*/egenkapitalGjeld/egenkapital/opptjentEgenkapital` | 84 | 0 | 0 |
| `/*/egenkapitalGjeld/gjeldOversikt/kortsiktigGjeld` | 113 | 0 | 0 |
| `/*/egenkapitalGjeld/gjeldOversikt/langsiktigGjeld` | 569 | 0 | 0 |
| `/*/eiendeler/anleggsmidler` | 134 | 0 | 0 |
| `/*/eiendeler/omloepsmidler` | 7 | 0 | 0 |
| `/*/id` | 999 | 0 | 0 |
| `/*/journalnr` | 999 | 0 | 0 |
| `/*/resultatregnskapResultat/driftsresultat/driftsinntekter` | 275 | 0 | 0 |
| `/*/resultatregnskapResultat/driftsresultat/driftskostnad` | 24 | 0 | 0 |
| `/*/resultatregnskapResultat/finansresultat/finansinntekt` | 271 | 0 | 0 |
| `/*/resultatregnskapResultat/finansresultat/finanskostnad` | 296 | 0 | 0 |
| `/*/virksomhet/organisasjonsnummer` | 999 | 0 | 0 |

#### subunits (41 paths without exact publication for at least one company)

| JSON path | Present | Exact before | Within composite |
|---|---:|---:|---:|
| `/_embedded/underenheter/*/_links/overordnetEnhet/href` | 773 | 0 | 773 |
| `/_embedded/underenheter/*/_links/self/href` | 773 | 0 | 773 |
| `/_embedded/underenheter/*/antallAnsatte` | 122 | 0 | 122 |
| `/_embedded/underenheter/*/beliggenhetsadresse/adresse` | 4 | 0 | 4 |
| `/_embedded/underenheter/*/beliggenhetsadresse/adresse/*` | 768 | 0 | 768 |
| `/_embedded/underenheter/*/beliggenhetsadresse/kommune` | 768 | 0 | 768 |
| `/_embedded/underenheter/*/beliggenhetsadresse/kommunenummer` | 768 | 0 | 768 |
| `/_embedded/underenheter/*/beliggenhetsadresse/land` | 771 | 0 | 771 |
| `/_embedded/underenheter/*/beliggenhetsadresse/landkode` | 771 | 0 | 771 |
| `/_embedded/underenheter/*/beliggenhetsadresse/postnummer` | 768 | 0 | 768 |
| `/_embedded/underenheter/*/beliggenhetsadresse/poststed` | 771 | 0 | 771 |
| `/_embedded/underenheter/*/historiskeNavn` | 571 | 0 | 571 |
| `/_embedded/underenheter/*/historiskeNavn/*/fraDato` | 210 | 0 | 210 |
| `/_embedded/underenheter/*/historiskeNavn/*/navn` | 210 | 0 | 210 |
| `/_embedded/underenheter/*/historiskeNavn/*/tilDato` | 210 | 0 | 210 |
| `/_embedded/underenheter/*/hjelpeenhetskode/beskrivelse` | 40 | 0 | 40 |
| `/_embedded/underenheter/*/hjelpeenhetskode/kode` | 40 | 0 | 40 |
| `/_embedded/underenheter/*/naeringskode1/beskrivelse` | 767 | 0 | 767 |
| `/_embedded/underenheter/*/naeringskode1/kode` | 767 | 0 | 767 |
| `/_embedded/underenheter/*/naeringskode2/beskrivelse` | 3 | 0 | 3 |
| `/_embedded/underenheter/*/naeringskode2/kode` | 3 | 0 | 3 |
| `/_embedded/underenheter/*/navn` | 773 | 0 | 773 |
| `/_embedded/underenheter/*/organisasjonsform/_links/self/href` | 773 | 0 | 773 |
| `/_embedded/underenheter/*/organisasjonsform/beskrivelse` | 773 | 0 | 773 |
| `/_embedded/underenheter/*/organisasjonsform/kode` | 773 | 0 | 773 |
| `/_embedded/underenheter/*/organisasjonsnummer` | 773 | 0 | 773 |
| `/_embedded/underenheter/*/overordnetEnhet` | 773 | 0 | 773 |
| `/_embedded/underenheter/*/postadresse/adresse` | 2 | 0 | 2 |
| `/_embedded/underenheter/*/postadresse/adresse/*` | 180 | 0 | 180 |
| `/_embedded/underenheter/*/postadresse/kommune` | 181 | 0 | 181 |
| `/_embedded/underenheter/*/postadresse/kommunenummer` | 181 | 0 | 181 |
| `/_embedded/underenheter/*/postadresse/land` | 182 | 0 | 182 |
| `/_embedded/underenheter/*/postadresse/landkode` | 182 | 0 | 182 |
| `/_embedded/underenheter/*/postadresse/postnummer` | 181 | 0 | 181 |
| `/_embedded/underenheter/*/postadresse/poststed` | 182 | 0 | 182 |
| `/_embedded/underenheter/*/respons_klasse` | 773 | 0 | 773 |
| `/_links/self/href` | 1000 | 0 | 0 |
| `/page/number` | 1000 | 0 | 0 |
| `/page/size` | 1000 | 0 | 0 |
| `/page/totalElements` | 1000 | 0 | 0 |
| `/page/totalPages` | 1000 | 0 | 0 |

## Competitor emitted field lists

Lists show native normalized field names on the same unseen 100, under the corrected family taxonomy. They describe each competitor’s field granularity; they do not imply that a value is independently verified. Full lists are in `competitor-fields.json`.

### ChiaraDeVenuto

- **identity (79):** `address_line`, `aktivitet`, `antallAnsatte`, `bankrupt`, `business_address`, `email`, `employees`, `epostadresse`, `erIKonsern`, `forretningsadresse.adresse`, `forretningsadresse.kommune`, `forretningsadresse.kommunenummer`, `forretningsadresse.land`, `forretningsadresse.landkode`, `forretningsadresse.postnummer`, `forretningsadresse.poststed`, `fravalgRevisjonBeslutningsDato`, `fravalgRevisjonDato`, `frivilligMvaRegistrertBeskrivelser`, `harRegistrertAntallAnsatte`, `hjelpeenhetskode.beskrivelse`, `hjelpeenhetskode.kode`, `hjemmeside`, `incorporation_date`, `industry`, `institusjonellSektorkode.beskrivelse`, `institusjonellSektorkode.kode`, `kapital.antallAksjer`, `kapital.belop`, `kapital.innfortDato`, `kapital.type`, `kapital.valuta`, `konkurs`, `legal_form`, `liquidating`, `maalform`, `mobil`, `municipality`, `naeringskode1.beskrivelse`, `naeringskode1.kode`, `naeringskode2.beskrivelse`, `naeringskode2.kode`, `name`, `navn`, `organisasjonsform.beskrivelse`, `organisasjonsform.kode`, `organisasjonsnummer`, `organisation_number`, `paategninger`, `postadresse.adresse`, `postadresse.kommune`, `postadresse.kommunenummer`, `postadresse.land`, `postadresse.landkode`, `postadresse.postnummer`, `postadresse.poststed`, `postal_address`, `postal_code`, `registreringsdatoAntallAnsatteEnhetsregisteret`, `registreringsdatoForetaksregisteret`, `registreringsdatoFrivilligMerverdiavgiftsregisteret`, `registreringsdatoMerverdiavgiftsregisteret`, `registreringsdatoMerverdiavgiftsregisteretEnhetsregisteret`, `registreringsdatoantallansatteNAVAaregisteret`, `registreringsdatoenhetsregisteret`, `registrertIForetaksregisteret`, `registrertIFrivillighetsregisteret`, `registrertIMvaRegisteret`, `registrertIPartiregisteret`, `registrertIStiftelsesregisteret`, `sisteInnsendteAarsregnskap`, `stiftelsesdato`, `structured_organisations`, `telefon`, `underAvvikling`, `underTvangsavviklingEllerTvangsopplosning`, `vedtektsdato`, `vedtektsfestetFormaal`, `website`
- **roles (1):** `roles`
- **accounts (4):** `classification`, `latest_submitted_accounts`, `legal_form`, `records`
- **subunits (1):** `locations`

### Venky1209

- **identity (81):** `activity`, `aktivitet`, `antallAnsatte`, `bankrupt`, `business_address`, `email_domain`, `employees`, `epostadresse`, `erIKonsern`, `forretningsadresse.adresse`, `forretningsadresse.kommune`, `forretningsadresse.kommunenummer`, `forretningsadresse.land`, `forretningsadresse.landkode`, `forretningsadresse.postnummer`, `forretningsadresse.poststed`, `founded`, `fravalgRevisjonBeslutningsDato`, `fravalgRevisjonDato`, `frivilligMvaRegistrertBeskrivelser`, `harRegistrertAntallAnsatte`, `hjelpeenhetskode.beskrivelse`, `hjelpeenhetskode.kode`, `hjemmeside`, `identity_text_excerpt`, `in_group`, `industry`, `institusjonellSektorkode.beskrivelse`, `institusjonellSektorkode.kode`, `kapital.antallAksjer`, `kapital.belop`, `kapital.innfortDato`, `kapital.type`, `kapital.valuta`, `konkurs`, `legal_form`, `liquidating`, `maalform`, `mobil`, `naeringskode1.beskrivelse`, `naeringskode1.kode`, `naeringskode2.beskrivelse`, `naeringskode2.kode`, `name`, `navn`, `organisasjonsform.beskrivelse`, `organisasjonsform.kode`, `organisasjonsnummer`, `organisation_number`, `paategninger`, `phone`, `postadresse.adresse`, `postadresse.kommune`, `postadresse.kommunenummer`, `postadresse.land`, `postadresse.landkode`, `postadresse.postnummer`, `postadresse.poststed`, `postal_address`, `registreringsdatoAntallAnsatteEnhetsregisteret`, `registreringsdatoForetaksregisteret`, `registreringsdatoFrivilligMerverdiavgiftsregisteret`, `registreringsdatoMerverdiavgiftsregisteret`, `registreringsdatoMerverdiavgiftsregisteretEnhetsregisteret`, `registreringsdatoantallansatteNAVAaregisteret`, `registreringsdatoenhetsregisteret`, `registrertIForetaksregisteret`, `registrertIFrivillighetsregisteret`, `registrertIMvaRegisteret`, `registrertIPartiregisteret`, `registrertIStiftelsesregisteret`, `sisteInnsendteAarsregnskap`, `statutory_purpose`, `stiftelsesdato`, `structured_organisations`, `telefon`, `underAvvikling`, `underTvangsavviklingEllerTvangsopplosning`, `vedtektsdato`, `vedtektsfestetFormaal`, `website`
- **roles (1):** `roles`
- **accounts (4):** `classification`, `latest_submitted_accounts`, `legal_form`, `records`
- **subunits (1):** `locations`

### slightlybroke

- **identity (75):** `aktivitet`, `antallAnsatte`, `bankrupt`, `business_address`, `deleted`, `employees`, `epostadresse`, `erIKonsern`, `forretningsadresse.adresse`, `forretningsadresse.kommune`, `forretningsadresse.kommunenummer`, `forretningsadresse.land`, `forretningsadresse.landkode`, `forretningsadresse.postnummer`, `forretningsadresse.poststed`, `fravalgRevisjonBeslutningsDato`, `fravalgRevisjonDato`, `frivilligMvaRegistrertBeskrivelser`, `harRegistrertAntallAnsatte`, `hjelpeenhetskode.beskrivelse`, `hjelpeenhetskode.kode`, `hjemmeside`, `industry`, `institusjonellSektorkode.beskrivelse`, `institusjonellSektorkode.kode`, `kapital.antallAksjer`, `kapital.belop`, `kapital.innfortDato`, `kapital.type`, `kapital.valuta`, `konkurs`, `legal_form`, `liquidating`, `maalform`, `mobil`, `naeringskode1.beskrivelse`, `naeringskode1.kode`, `naeringskode2.beskrivelse`, `naeringskode2.kode`, `name`, `navn`, `organisasjonsform.beskrivelse`, `organisasjonsform.kode`, `organisasjonsnummer`, `organisation_number`, `paategninger`, `postadresse.adresse`, `postadresse.kommune`, `postadresse.kommunenummer`, `postadresse.land`, `postadresse.landkode`, `postadresse.postnummer`, `postadresse.poststed`, `postal_address`, `registreringsdatoAntallAnsatteEnhetsregisteret`, `registreringsdatoForetaksregisteret`, `registreringsdatoFrivilligMerverdiavgiftsregisteret`, `registreringsdatoMerverdiavgiftsregisteret`, `registreringsdatoMerverdiavgiftsregisteretEnhetsregisteret`, `registreringsdatoantallansatteNAVAaregisteret`, `registreringsdatoenhetsregisteret`, `registrertIForetaksregisteret`, `registrertIFrivillighetsregisteret`, `registrertIMvaRegisteret`, `registrertIPartiregisteret`, `registrertIStiftelsesregisteret`, `sisteInnsendteAarsregnskap`, `stiftelsesdato`, `structured_organisations`, `telefon`, `underAvvikling`, `underTvangsavviklingEllerTvangsopplosning`, `vedtektsdato`, `vedtektsfestetFormaal`, `website`
- **roles (1):** `roles`
- **accounts (4):** `classification`, `latest_submitted_accounts`, `legal_form`, `records`
- **subunits (1):** `locations`

### CVasilopoulos

- **identity (30):** `identity.articles_date`, `identity.auxiliary_unit_code`, `identity.business_register_date`, `identity.employees`, `identity.former_name`, `identity.founded_date`, `identity.in_business_register`, `identity.in_foundation_register`, `identity.in_party_register`, `identity.in_voluntary_register`, `identity.industry`, `identity.institutional_sector`, `identity.language_form`, `identity.legal_form`, `identity.legal_name`, `identity.number_of_shares`, `identity.organisation_number`, `identity.part_of_group`, `identity.registered_activity`, `identity.registered_date`, `identity.share_capital`, `identity.status`, `identity.statutory_purpose`, `identity.vat_registered`, `identity.vat_registered_date`, `identity.vat_registered_in_register_date`, `identity.voluntary_vat_basis`, `identity.voluntary_vat_registered_date`, `identity.website_founded_year`, `website.registry_listed`
- **roles (11):** `leadership.accountant`, `leadership.auditor`, `leadership.board_chair`, `leadership.board_deputy_member`, `leadership.board_member`, `leadership.business_manager`, `leadership.ceo`, `leadership.named_on_website`, `leadership.norwegian_representative`, `leadership.owner`, `leadership.parent_foreign_entity`
- **accounts (32):** `financials.accounting_rules`, `financials.annual_result`, `financials.audited`, `financials.cash_and_bank`, `financials.current_assets`, `financials.current_liabilities`, `financials.equity`, `financials.filed_copy`, `financials.filed_copy_years`, `financials.financial_expenses`, `financials.financial_income`, `financials.fixed_assets`, `financials.inventory`, `financials.investments`, `financials.latest_submitted_year`, `financials.long_term_liabilities`, `financials.net_financial_items`, `financials.operating_expenses`, `financials.operating_result`, `financials.paid_in_equity`, `financials.parent_company_filer`, `financials.profit_before_tax`, `financials.receivables`, `financials.retained_earnings`, `financials.revenue`, `financials.sales_revenue`, `financials.statement_format`, `financials.tax_expense`, `financials.total_assets`, `financials.total_comprehensive_result`, `financials.total_liabilities`, `financials.wage_costs`
- **subunits (7):** `location.business_address`, `location.lei_headquarters_address`, `location.lei_legal_address`, `location.municipality`, `location.opening_hours`, `location.registered_workplace`, `location.website_address`

### AnanthKumar1810

- **identity (26):** `address`, `business_register_date`, `city`, `contact_email`, `contact_mobile`, `contact_phone`, `declared_activity`, `employee_count`, `incorporated_at`, `industry_code`, `industry_description`, `institutional_sector_code`, `institutional_sector_description`, `latest_submitted_accounts_year`, `legal_name`, `mailing_address`, `municipality`, `organisation_form`, `organisation_form_description`, `postal_code`, `registered_at`, `share_capital_nok`, `share_count`, `stated_purpose`, `vat_registered`, `website`
- **roles (1):** `registered_role`
- **accounts (5):** `equity_nok`, `net_result_nok`, `operating_result_nok`, `revenue_nok`, `total_assets_nok`
- **subunits (5):** `address`, `city`, `mailing_address`, `municipality`, `postal_code`

### mstege

- **identity (22):** `business_address`, `contact_email`, `contact_phone`, `former_name`, `founded_date`, `industry`, `legal_form`, `legal_name`, `legal_status`, `municipality`, `organisation_number`, `part_of_group`, `postal_address`, `registered_date`, `registered_employees`, `registered_in`, `registry_email`, `registry_event`, `registry_phone`, `registry_website`, `share_capital`, `stated_purpose`
- **roles (4):** `leader_on_website`, `leadership`, `registered_workplace`, `website_location`
- **accounts (8):** `equity`, `latest_filed_accounts_year`, `net_result`, `operating_result`, `profit_before_tax`, `revenue`, `total_assets`, `total_debt`
- **subunits (0):** none

## Full suite

1,857 passed, 1 warning in 515.48 seconds. The strict verifier results for both cohorts are in `verification.json`.
