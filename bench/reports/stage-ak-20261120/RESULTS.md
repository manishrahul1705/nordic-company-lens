# Stage AK registry enrichments

Previous names come from enheter JSON historiskeNavn. Abhinav reads it at src/abhikilde/official.py:210 and publishes previous_legal_name at envelope.py:331. Our existing fact_depth.histories already publishes these names and source-provided fraDato and tilDato.

Per-year raw audit booleans were also already published. The new audit_status maps the explicit boolean ikkeRevidertAarsregnskap. Missing or nonboolean values produce no status.

Dated activity retains each original identity claim and cites its evidence. A year-only latest accounts record retains year precision. No filing day is inferred. All extraction uses already acquired data and adds zero HTTP requests.

## Measurements

sample_before
{
  "raw_audit_flags": {
    "companies": 100,
    "claims": 558
  },
  "names": {
    "companies": 34,
    "claims": 96
  }
}

sample_after
{
  "raw_audit_flags": {
    "companies": 100,
    "claims": 558
  },
  "audit_status": {
    "companies": 100,
    "claims": 279
  },
  "dated_registry": {
    "companies": 100,
    "claims": 797
  },
  "names": {
    "companies": 34,
    "claims": 96
  }
}

replay1000
{
  "before": {
    "raw_audit_flags": {
      "companies": 999,
      "claims": 5634
    },
    "previous_names": {
      "companies": 302,
      "claims": 701
    }
  },
  "after": {
    "raw_audit_flags": {
      "companies": 999,
      "claims": 5634
    },
    "audit_status": {
      "companies": 999,
      "claims": 2817
    },
    "registry_dates": {
      "companies": 997,
      "claims": 7714
    },
    "previous_names": {
      "companies": 302,
      "claims": 701
    }
  }
}

retained_overlap
{
  "abhinav": {
    "records_in_retained_ledger": 141,
    "matched": 135
  },
  "kilde": {
    "records_in_retained_ledger": 279,
    "matched": 127
  }
}

The overlap uses the surviving competitor unmatched-fact ledger. Audit cleanup deleted their full runtime outputs, so the full intersection cannot be reconstructed.

## Ten hand checks

- SQ URBAN LANDSKAP AS (919948493) · subunits.detail.818984952.historical_name.3d34ebf482e1b7a8b4d7837c · {"navn": "SQ URBAN LANDSKAP QUILAMBO", "fraDato": "2017-05-11 20:09:14", "tilDato": "2018-03-01 21:11:27"}. Exact source name and any stated dates are retained. [Evidence](https://data.brreg.no/enhetsregisteret/api/underenheter?overordnetEnhet=919948493&size=1000&page=0) Locator /_embedded/underenheter/0/historiskeNavn/0. Verbatim evidence "arRegistrertAntallAnsatte\":true,\"historiskeNavn\":[{\"fraDato\":\"2017-05-11 20:09:14\",\"navn\":\"SQ URBAN LANDSKAP QUILAMBO\",\"tilDato\":\"2018-03-01 21:11:27\"}],\"mobil\":\"92541552\",\"naeringskode1\":{\"beskrivelse\":\"Beplantning av hager og parkanlegg\",\"kode\":\"81.300\"},\"navn\":\"SQ URBAN LANDSKAP AS\",\"oppstartsdat"
- MYKLEBUST MARITIME AS (981508734) · identity.historical_name.29e479ab9b69d7d8b23deca7 · {"navn": "KLEVEN FLORØ HOLDING AS", "fraDato": "2000-02-01 08:24:15", "tilDato": "2001-06-05 10:18:47"}. Exact source name and any stated dates are retained. [Evidence](https://data.brreg.no/enhetsregisteret/api/enheter/981508734) Locator /historiskeNavn/0. Verbatim evidence "rRegistrertAntallAnsatte\":false,\"historiskeNavn\":[{\"fraDato\":\"2000-02-01 08:24:15\",\"navn\":\"KLEVEN FLORØ HOLDING AS\",\"tilDato\":\"2001-06-05 10:18:47\"},{\"fraDato\":\"2001-06-05 10:18:47\",\"navn\":\"KLEVEN HOLDING AS\",\"tilDato\":\"2001-10-10 21:37:03\"},{\"fraDato\":\"2001-10-10 21:37:03\",\"navn\":\"KLEVEN MARITIME A"
- M BERGUM AS (936276075) · identity.historical_name.629ccad167bc46472df6c157 · {"navn": "NFH 250957 AS", "fraDato": "2025-09-30 11:11:38", "tilDato": "2025-12-02 17:15:38"}. Exact source name and any stated dates are retained. [Evidence](https://data.brreg.no/enhetsregisteret/api/enheter/936276075) Locator /historiskeNavn/0. Verbatim evidence "rRegistrertAntallAnsatte\":false,\"historiskeNavn\":[{\"fraDato\":\"2025-09-30 11:11:38\",\"navn\":\"NFH 250957 AS\",\"tilDato\":\"2025-12-02 17:15:38\"}],\"institusjonellSektorkode\":{\"beskrivelse\":\"Private aksjeselskaper mv.\",\"kode\":\"2100\"},\"kapital\":{\"antallAksjer\":3000,\"belop\":30000.00,\"innfortDato\":\"2025-09-30\""
- MYNT OG EIENDOM BESSAKER AS (912823970) · accounts.statement.2025.audit_status · "audited". Explicit boolean at this annual-statement locator supports the status. [Evidence](https://data.brreg.no/regnskapsregisteret/regnskap/912823970) Locator /2/revisjon/ikkeRevidertAarsregnskap. Verbatim evidence "n\":\"store\",\"revisjon\":{\"ikkeRevidertAarsregnskap\":false,\"fravalgRevisjon\":true},\"regnkapsprinsipper\":{\"smaaForetak\":true,\"regnskapsregler\":\"regnskapslovenAlminneligRegler\"},\"egenkapitalGjeld\":{\"sumEgenkapitalGjeld\":3872158.00,\"egenkapital\":{\"sumEgenkapital\":678124.00,\"opptjentEgenkapital\":{\"sumOpptj"
- FIKO EIENDOM AS (916729774) · accounts.statement.2025.audit_status · "audited". Explicit boolean at this annual-statement locator supports the status. [Evidence](https://data.brreg.no/regnskapsregisteret/regnskap/916729774) Locator /2/revisjon/ikkeRevidertAarsregnskap. Verbatim evidence "n\":\"store\",\"revisjon\":{\"ikkeRevidertAarsregnskap\":false,\"fravalgRevisjon\":true},\"regnkapsprinsipper\":{\"smaaForetak\":true,\"regnskapsregler\":\"regnskapslovenAlminneligRegler\"},\"egenkapitalGjeld\":{\"sumEgenkapitalGjeld\":5361875.00,\"egenkapital\":{\"sumEgenkapital\":2384219.00,\"opptjentEgenkapital\":{\"sumOppt"
- DRAGEHAUGEN VERDI AS (917998787) · accounts.statement.2025.audit_status · "audited". Explicit boolean at this annual-statement locator supports the status. [Evidence](https://data.brreg.no/regnskapsregisteret/regnskap/917998787) Locator /2/revisjon/ikkeRevidertAarsregnskap. Verbatim evidence "n\":\"store\",\"revisjon\":{\"ikkeRevidertAarsregnskap\":false,\"fravalgRevisjon\":false},\"regnkapsprinsipper\":{\"smaaForetak\":true,\"regnskapsregler\":\"regnskapslovenAlminneligRegler\"},\"egenkapitalGjeld\":{\"sumEgenkapitalGjeld\":21454758.00,\"egenkapital\":{\"sumEgenkapital\":17140509.00,\"opptjentEgenkapital\":{\"sumO"
- MYNT OG EIENDOM BESSAKER AS (912823970) · registry_dated_activity.founding_date · "2013-11-21". The activity value and citation match the existing identity field, retaining date precision. [Evidence](https://data.brreg.no/enhetsregisteret/api/enheter/912823970) Locator /stiftelsesdato. Verbatim evidence "steInnsendteAarsregnskap\":\"2025\",\"stiftelsesdato\":\"2013-11-21\",\"underAvvikling\":false,\"underTvangsavviklingEllerTvangsopplosning\":false,\"vedtektsdato\":\"2013-11-21\",\"vedtektsfestetFormaal\":[\"Kjøp og salg av mynter, kjøp og salg av eiendom, samt utleie av\",\"eiendom og andre produkter/tjenester som nat"
- FIKO EIENDOM AS (916729774) · registry_dated_activity.founding_date · "2016-02-09". The activity value and citation match the existing identity field, retaining date precision. [Evidence](https://data.brreg.no/enhetsregisteret/api/enheter/916729774) Locator /stiftelsesdato. Verbatim evidence "steInnsendteAarsregnskap\":\"2025\",\"stiftelsesdato\":\"2016-02-09\",\"underAvvikling\":false,\"underTvangsavviklingEllerTvangsopplosning\":false,\"vedtektsdato\":\"2016-02-09\",\"vedtektsfestetFormaal\":[\"Kjøp, salg og utleie av fast eiendom, medvirke i andre selskaper innen\",\"samme virksomhet, samt alt som hører "
- DRAGEHAUGEN VERDI AS (917998787) · registry_dated_activity.founding_date · "2016-10-06". The activity value and citation match the existing identity field, retaining date precision. [Evidence](https://data.brreg.no/enhetsregisteret/api/enheter/917998787) Locator /stiftelsesdato. Verbatim evidence "steInnsendteAarsregnskap\":\"2025\",\"stiftelsesdato\":\"2016-10-06\",\"underAvvikling\":false,\"underTvangsavviklingEllerTvangsopplosning\":false,\"vedtektsdato\":\"2016-10-06\",\"vedtektsfestetFormaal\":[\"Investere i aksjer, verdipapirer, andre selskapsandeler og fast\",\"eiendom, samt det som naturlig står i forbin"
- MENSTAD NÆRINGSPARK AS (918049215) · registry_dated_activity.founding_date · "2016-10-19". The activity value and citation match the existing identity field, retaining date precision. [Evidence](https://data.brreg.no/enhetsregisteret/api/enheter/918049215) Locator /stiftelsesdato. Verbatim evidence "steInnsendteAarsregnskap\":\"2025\",\"stiftelsesdato\":\"2016-10-19\",\"underAvvikling\":false,\"underTvangsavviklingEllerTvangsopplosning\":false,\"vedtektsdato\":\"2025-12-30\",\"vedtektsfestetFormaal\":[\"Kjøp, utvikling og salg av fast eiendom, ytelse av entreprisetjenester\",\"innenfor bygg og anlegg, samt hva som"

## Verification

Fresh default sample100 completed in 289.16 seconds including site rendering (reported pre-site runtime 262.125 seconds), 1,230 HTTP requests and zero deadline hits. Extraction adds zero HTTP requests. The strict verifier passed 100 envelopes and 17,962 claims with zero unverified synthesis values.

The full 1,000 offline replay passed the strict verifier with 177,731 published claims and zero unverified synthesis values. The initial full suite found activity-toggle and refresh-scope regressions. Registry activity now respects the toggle, and refresh restores the derivative from supported current identity before comparison. Existing tests were retained.

Final full suite at the Stage AJ commit plus AK edits passed all 1,747 tests in 482.28 seconds. Both known evaluator network tests passed on this execution.

The original single-flag audit_status mapping in this report is superseded by the [audit precision correction](../stage-ak-audit-fix-20261120/RESULTS.md), which cites both explicit booleans and distinguishes audit_opted_out.
