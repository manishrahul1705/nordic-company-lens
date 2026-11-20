# Stage AK audit status precision correction

The original 2,817 claims used only ikkeRevidertAarsregnskap and incorrectly marked audit-opted-out statements as audited.

| fravalgRevisjon | ikkeRevidertAarsregnskap | Old claims |
|---|---|---:|
| true | false | 1,693 |
| true | true | 0 |
| false | false | 1,124 |
| Any other pair | | 0 |

Both required fields must be booleans. Opt-out has priority over the unaudited flag, so two true flags mean audit_opted_out. With no opt-out, the unaudited flag distinguishes audited from not_audited. A missing or nonboolean required flag withholds the claim. If the optional explicit revidertAarsregnskap is present but conflicts with the result, the claim is also withheld. Both determining fields are cited.

The brief and synthesis contain no audit-status wording. The site displays claim values directly, so corrected claims supply the corrected status without template edits.

## Full 1,000 offline replay

| Status | Claims | Companies |
|---|---:|---:|
| audit_opted_out | 1693 | 650 |
| audited | 1124 | 392 |
| not_audited | 0 | 0 |

Replay made zero HTTP requests. Existing raw flags are retained.

## Five hand checks

- **MYNT OG EIENDOM BESSAKER AS (912823970), 2025** · audit_opted_out. fravalgRevisjon=true makes the explicit opt-out status correct even though ikkeRevidertAarsregnskap=false. [Source](https://data.brreg.no/regnskapsregisteret/regnskap/912823970)
  - /2/revisjon/fravalgRevisjon · SHA-256 990d355f5acc1fa5df534500df7898ad87bdfe40f38baee571fac77856a9bedb · verbatim "ikkeRevidertAarsregnskap\":false,\"fravalgRevisjon\":true},\"regnkapsprinsipper\":{\"smaaForetak\":true,\"regnskapsregler\":\"regnskapslovenAlminneligRegler\"},\"egenkapitalGjeld\":{\"sumEgenkapitalGjeld\":3872158.00,\"egenkapital\":{\"sumEgenkapital\":678124.00,\"opptjentEgenkapital\":{\"sumOpptjentEgenkapital\":658455.0"
  - /2/revisjon/ikkeRevidertAarsregnskap · SHA-256 990d355f5acc1fa5df534500df7898ad87bdfe40f38baee571fac77856a9bedb · verbatim "n\":\"store\",\"revisjon\":{\"ikkeRevidertAarsregnskap\":false,\"fravalgRevisjon\":true},\"regnkapsprinsipper\":{\"smaaForetak\":true,\"regnskapsregler\":\"regnskapslovenAlminneligRegler\"},\"egenkapitalGjeld\":{\"sumEgenkapitalGjeld\":3872158.00,\"egenkapital\":{\"sumEgenkapital\":678124.00,\"opptjentEgenkapital\":{\"sumOpptj"
- **FIKO EIENDOM AS (916729774), 2025** · audit_opted_out. fravalgRevisjon=true makes the explicit opt-out status correct even though ikkeRevidertAarsregnskap=false. [Source](https://data.brreg.no/regnskapsregisteret/regnskap/916729774)
  - /2/revisjon/fravalgRevisjon · SHA-256 341bcfc71e330c6a374a975187966e95737ae1268df3169657ef6329df16aed0 · verbatim "ikkeRevidertAarsregnskap\":false,\"fravalgRevisjon\":true},\"regnkapsprinsipper\":{\"smaaForetak\":true,\"regnskapsregler\":\"regnskapslovenAlminneligRegler\"},\"egenkapitalGjeld\":{\"sumEgenkapitalGjeld\":5361875.00,\"egenkapital\":{\"sumEgenkapital\":2384219.00,\"opptjentEgenkapital\":{\"sumOpptjentEgenkapital\":2354219"
  - /2/revisjon/ikkeRevidertAarsregnskap · SHA-256 341bcfc71e330c6a374a975187966e95737ae1268df3169657ef6329df16aed0 · verbatim "n\":\"store\",\"revisjon\":{\"ikkeRevidertAarsregnskap\":false,\"fravalgRevisjon\":true},\"regnkapsprinsipper\":{\"smaaForetak\":true,\"regnskapsregler\":\"regnskapslovenAlminneligRegler\"},\"egenkapitalGjeld\":{\"sumEgenkapitalGjeld\":5361875.00,\"egenkapital\":{\"sumEgenkapital\":2384219.00,\"opptjentEgenkapital\":{\"sumOppt"
- **SQ URBAN LANDSKAP AS (919948493), 2025** · audit_opted_out. fravalgRevisjon=true makes the explicit opt-out status correct even though ikkeRevidertAarsregnskap=false. [Source](https://data.brreg.no/regnskapsregisteret/regnskap/919948493)
  - /2/revisjon/fravalgRevisjon · SHA-256 4b50b723cebd82eac6887e492331f39af1eae50e60a13f45e3a4837889f92a96 · verbatim "ikkeRevidertAarsregnskap\":false,\"fravalgRevisjon\":true},\"regnkapsprinsipper\":{\"smaaForetak\":true,\"regnskapsregler\":\"regnskapslovenAlminneligRegler\"},\"egenkapitalGjeld\":{\"sumEgenkapitalGjeld\":1560186.00,\"egenkapital\":{\"sumEgenkapital\":286625.00,\"opptjentEgenkapital\":{\"sumOpptjentEgenkapital\":256625.0"
  - /2/revisjon/ikkeRevidertAarsregnskap · SHA-256 4b50b723cebd82eac6887e492331f39af1eae50e60a13f45e3a4837889f92a96 · verbatim "n\":\"store\",\"revisjon\":{\"ikkeRevidertAarsregnskap\":false,\"fravalgRevisjon\":true},\"regnkapsprinsipper\":{\"smaaForetak\":true,\"regnskapsregler\":\"regnskapslovenAlminneligRegler\"},\"egenkapitalGjeld\":{\"sumEgenkapitalGjeld\":1560186.00,\"egenkapital\":{\"sumEgenkapital\":286625.00,\"opptjentEgenkapital\":{\"sumOpptj"
- **DRAGEHAUGEN VERDI AS (917998787), 2025** · audited. Both flags are explicitly false, supporting audited status. [Source](https://data.brreg.no/regnskapsregisteret/regnskap/917998787)
  - /2/revisjon/fravalgRevisjon · SHA-256 fc277cb31cff1e97477b4001983fb347f9f8c9c0cf064391a979aa7101089686 · verbatim "ikkeRevidertAarsregnskap\":false,\"fravalgRevisjon\":false},\"regnkapsprinsipper\":{\"smaaForetak\":true,\"regnskapsregler\":\"regnskapslovenAlminneligRegler\"},\"egenkapitalGjeld\":{\"sumEgenkapitalGjeld\":21454758.00,\"egenkapital\":{\"sumEgenkapital\":17140509.00,\"opptjentEgenkapital\":{\"sumOpptjentEgenkapital\":8317"
  - /2/revisjon/ikkeRevidertAarsregnskap · SHA-256 fc277cb31cff1e97477b4001983fb347f9f8c9c0cf064391a979aa7101089686 · verbatim "n\":\"store\",\"revisjon\":{\"ikkeRevidertAarsregnskap\":false,\"fravalgRevisjon\":false},\"regnkapsprinsipper\":{\"smaaForetak\":true,\"regnskapsregler\":\"regnskapslovenAlminneligRegler\"},\"egenkapitalGjeld\":{\"sumEgenkapitalGjeld\":21454758.00,\"egenkapital\":{\"sumEgenkapital\":17140509.00,\"opptjentEgenkapital\":{\"sumO"
- **MENSTAD NÆRINGSPARK AS (918049215), 2025** · audited. Both flags are explicitly false, supporting audited status. [Source](https://data.brreg.no/regnskapsregisteret/regnskap/918049215)
  - /2/revisjon/fravalgRevisjon · SHA-256 24c6c13c3377ac15ecd81ff8477ce9ea5221800e254d160f5d710e8e5b3ec491 · verbatim "ikkeRevidertAarsregnskap\":false,\"fravalgRevisjon\":false},\"regnkapsprinsipper\":{\"smaaForetak\":true,\"regnskapsregler\":\"regnskapslovenAlminneligRegler\"},\"egenkapitalGjeld\":{\"sumEgenkapitalGjeld\":93745627.00,\"egenkapital\":{\"sumEgenkapital\":89096956.00,\"opptjentEgenkapital\":{\"sumOpptjentEgenkapital\":-217"
  - /2/revisjon/ikkeRevidertAarsregnskap · SHA-256 24c6c13c3377ac15ecd81ff8477ce9ea5221800e254d160f5d710e8e5b3ec491 · verbatim "n\":\"store\",\"revisjon\":{\"ikkeRevidertAarsregnskap\":false,\"fravalgRevisjon\":false},\"regnkapsprinsipper\":{\"smaaForetak\":true,\"regnskapsregler\":\"regnskapslovenAlminneligRegler\"},\"egenkapitalGjeld\":{\"sumEgenkapitalGjeld\":93745627.00,\"egenkapital\":{\"sumEgenkapital\":89096956.00,\"opptjentEgenkapital\":{\"sumO"

## Verification

Strict verifier passed 1,000 envelopes, 177,731 published claims and 5,183 source blobs with zero unverified synthesis values. Replay used zero HTTP requests.

Full suite passed all 1,754 tests in 542.52 seconds. Both known evaluator network tests passed on this execution.
