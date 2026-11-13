# Shared identifier counts

Source: official Bronnoysundregistrene entity bulk CSV, https://data.brreg.no/enhetsregisteret/api/enheter/lastned/csv . Attribution: Bronnoysundregistrene. Data reused under NLOD 2.0: https://data.norge.no/nlod/en/2.0 . Build date, source hash and counts are in shared_identifiers_build.json.

Counts represent registry entities per normalized phone/mobile (eight Norwegian digits; phone and mobile duplicates within a row count once), registered email domain, and distinctive name key. Name keys ASCII-fold the legal name, remove trailing legal forms and the explicitly listed filler words in web/shared_identifiers.py, deduplicate and sort tokens. Missing keys never imply uniqueness. Registry counts are a dated snapshot, not a guarantee of exclusive ownership. Existing ownership vetoes remain authoritative. No raw registry rows or email addresses are bundled.

Rebuild with `python scripts/build_shared_identifiers.py`. The official download is cached under the ignored measurement raw directory; gzip output is deterministic for identical input. No agent network requests are needed to read the counts.

The complete snapshot contains 406,154 phone keys, 92,098 email-domain keys and 1,084,529 name keys. The gzip file is 8,676,502 bytes, above the requested 3 MB target. Every key and exact count is retained; no probabilistic uniqueness approximation is used.
