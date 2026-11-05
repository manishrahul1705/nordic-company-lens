# Output contract

The `--organisations` input in README.md accepts either of these formats:

- Plain text: one organisation number per line, for example `923609016`.
- JSONL: one organisation number string/number per line, or one JSON object per
  line with the exact field name `organisation_number` (for example
  `{"organisation_number":"923609016"}`).

It also accepts a JSON list or a JSON object with an `organisation_numbers`
list. The command emits exactly one JSONL envelope and one raw profile per
input record, preserving order and duplicates. In plain text and JSONL, blank
or spaces-only lines are invalid records too. A final newline terminates the
last record; an empty file contains zero records. Whitespace within and around
organisation numbers is normalized before checksum validation.

Invalid numbers (including blank strings and invalid checksums) have failed
sections and `invalid_orgnr` errors. A checksum-valid number that the registry
answers with HTTP 404/410 has not_applicable sections and `not_in_registry` /
`identity_unverified` errors. Neither case can inherit prior company facts.
Transport failures remain failed or blocked, never evidence of registry absence.

Output is JSONL in the files passed to `--output` and `--profiles-output`;
console progress is not the data stream. Exit zero means membership was emitted,
not that all sources succeeded. See [schema](docs/DATA_SCHEMA.md) for shapes,
states, evidence and provenance.

Refresh uses the same `--state-dir`. Each complete run atomically saves its
latest envelopes and claims at `latest-envelopes.jsonl` inside that state
folder; the next run uses that snapshot automatically when `--previous` is
omitted. An explicit `--previous` overrides the automatic snapshot. Supported
changes include old and new values and their evidence; an identical snapshot
yields no company changes or observation changes. Evidence blobs stay in the
same state folder for provenance checks.

The hard HTTP ceiling is 18 per distinct normalized input, including retries
and shared NAV requests; duplicates share research. The hard time ceiling is
24 seconds per distinct normalized input (40 minutes per 100), with crawl time
reserved for final output. Lower configured limits apply. Exhaustion produces
explicit incomplete results for all inputs.

The bundled NAV index is discovery metadata, accepted for 30 days after its
unchanged build timestamp (4 November 2026; valid through 30 November). Each
published current job still requires a live ACTIVE, unexpired, single-ad NAV
detail with exact employer or registered-subunit orgnr. Stale index fallback
uses the same global request/time budget; incomplete discovery never proves
absence. No index timestamps or ad expiry dates are extended.
