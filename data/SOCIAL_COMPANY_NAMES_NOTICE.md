# Official BRREG company-name collision index

Contains data under [NLOD 2.0](https://data.norge.no/nlod/en/2.0) distributed by Brønnøysundregistrene. Source: [official Enhetsregisteret full CSV](https://data.brreg.no/enhetsregisteret/api/enheter/lastned/csv), retrieved 2026-11-20T01:21:14.581183+00:00. Dataset SHA-256: `f3f4f93d2e4c597c15b3d08193d0a055e0bcc788a858b8bec8fcf7e8438f1dba`.

`social_company_names.json.gz` contains all **1,181,598 main-entity organisation-number/name pairs**, with no competition-cohort or legal-form restriction. It replaces the earlier competition-derived 411,160-name index. The full dataset was used; the raw CSV is not distributed. Only organisation numbers and registered names are retained, with whitespace trimming and sorting. Runtime normalization for collisions is unchanged. No contact/person fields from the CSV are retained in the index.

This is a frozen snapshot, not a live registry query. The index is a withholding-only safeguard against social links matching a different registered company. It never establishes ownership, current company status or a corporate relationship. Missing/corrupt data fails closed. Exceptions still require explicit available own-company BRREG subunit, parent or subsidiary claims with proper registry citations; siblings, similar names and website branding do not qualify.

The index is 16,130,532 bytes. `social_company_names_build.json` records the source/retrieval date, dataset and index hashes, source/output row counts, excluded rows, transformations, attribution and licence. `scripts/build_social_company_names.py` rebuilds from the ignored official CSV and download manifest without network access. The index and notice are included in the wheel; runtime makes no dataset download.

Our changes: validate organisation numbers, select the two fields, trim surrounding whitespace, sort by organisation number, serialize JSON and gzip with mtime=0. Registered names are not expanded or inferred. Upstream data retains NLOD 2.0 terms; repository MIT applies to our code/documentation, not a replacement licence over BRREG data.
