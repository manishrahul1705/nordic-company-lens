# Step 14 official-source verification

Verified before implementation: official API docs identify NLOD 2.0, and BRREG licensing states no registration is required. Only official data.brreg.no was queried, without credentials or search.

- API: https://data.brreg.no/enhetsregisteret/api/oppdateringer/enheter
- Documentation/licence: https://data.brreg.no/enhetsregisteret/api/dokumentasjon/en/index.html
- Terms: https://www.brreg.no/en/use-of-data-from-the-bronnoysund-register-centre/datasets-and-api/
- Robots: https://data.brreg.no/robots.txt ? retry returned httpx.RemoteProtocolError: Server disconnected without sending a response. Proceeded under the explicit user instruction; this is not represented as a robots allow response.

First five identifiers in the frozen1000 input were tested. All five returned HTTP200, exact organisation numbers, dates and explicit changes inside the requested24-month window. No missing or unknown change body is expanded into an invented event.

| Orgnr | Date (as returned) | Type | Changed fields |
|---|---|---|---|
| 912823970 | 2026-07-22T20:04:03.789+02:00 | Endring | /sisteInnsendteAarsregnskap |
| 912823970 | 2025-11-13T10:21:27.017+01:00 | Ukjent | (none returned) |
| 912823970 | 2025-08-11T20:02:34.995+02:00 | Endring | (none returned) |
| 912823970 | 2025-05-21T06:05:12.597+02:00 | Endring | (none returned) |
| 916729774 | 2026-05-06T20:02:12.166+02:00 | Endring | /sisteInnsendteAarsregnskap |
| 916729774 | 2025-11-13T10:30:36.631+01:00 | Ukjent | (none returned) |
| 916729774 | 2025-05-29T00:05:53.377+02:00 | Endring | (none returned) |
| 916729774 | 2025-05-28T20:06:11.414+02:00 | Endring | (none returned) |
| 917998787 | 2026-07-09T20:01:26.261+02:00 | Endring | /sisteInnsendteAarsregnskap |
| 917998787 | 2025-11-13T10:33:17.494+01:00 | Ukjent | (none returned) |
| 917998787 | 2025-06-24T20:02:08.848+02:00 | Endring | (none returned) |
| 918049215 | 2026-06-20T14:21:29.051+02:00 | Endring | /sisteInnsendteAarsregnskap |
| 918049215 | 2026-03-31T15:05:12.948+02:00 | Endring | /vedtektsdato, /kapital/innfortDato, /kapital/belop |
| 918049215 | 2025-11-13T10:33:21.774+01:00 | Ukjent | (none returned) |
| 918049215 | 2025-07-28T20:01:49.138+02:00 | Endring | (none returned) |
| 919948493 | 2026-08-12T00:04:54.722+02:00 | Endring | /registreringsdatoAntallAnsatteEnhetsregisteret, /registreringsdatoAntallAnsatteNAVAaregisteret |
| 919948493 | 2026-08-03T20:05:45.942+02:00 | Endring | /sisteInnsendteAarsregnskap |
| 919948493 | 2026-06-12T00:05:09.051+02:00 | Endring | /registreringsdatoAntallAnsatteEnhetsregisteret, /registreringsdatoAntallAnsatteNAVAaregisteret |
| 919948493 | 2025-12-12T00:08:39.542+01:00 | Endring | /registreringsdatoAntallAnsatteEnhetsregisteret, /registreringsdatoAntallAnsatteNAVAaregisteret |
| 919948493 | 2025-11-13T10:37:58.586+01:00 | Ukjent | (none returned) |
| 919948493 | 2025-09-13T17:16:33.361+02:00 | Endring | /registreringsdatoAntallAnsatteEnhetsregisteret, /registreringsdatoAntallAnsatteNAVAaregisteret |
| 919948493 | 2025-06-17T20:04:56.327+02:00 | Endring | (none returned) |
| 919948493 | 2025-05-13T00:30:13.735+02:00 | Endring | (none returned) |
| 919948493 | 2025-02-12T02:14:36.675+01:00 | Endring | (none returned) |

Returned fields: organisasjonsnummer, oppdateringsid, dato (timezone-qualified publication timestamp), endringstype, optional endringer array of JSON-Patch op/path/value, _links.enhet and pagination metadata. No narrative announcement text is returned. Plain-English labels therefore describe only explicit field updates. Latest-accounts-year updates do not prove filing effective date; employee registration dates do not prove headcount changes. Ukjent and bare Endring records without supported fields are skipped. Old Ny records are never published.

The exact URLs, full original JSON bodies and robots error are in [source-check.json](source-check.json). Five/five have an explicit latest-accounts-year update; one also has capital/articles-date updates and one has employee-information registration-date updates. The stop-for-most-empty condition was not triggered.
