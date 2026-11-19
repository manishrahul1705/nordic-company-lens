# Frozen company-name collision index

Source: the competition's public [411,160-company universe](https://builderr.ai/signalpost-company-universe-2025.jsonl.gz), already retained locally for sampling and shared-domain withholding.

`social_company_names.json.gz` contains only organisation numbers and registered-name strings from every row of that pinned snapshot. It is used to **withhold** potentially misattributed social profiles. It is never evidence of website ownership, live company status, or a corporate relationship, and cannot authorize a claim. A missing/corrupt index fails closed.

The corpus is a frozen snapshot, not a current search of all Norwegian registrations. A name absent from this corpus is not asserted to be absent from today's registry. Case, Norwegian-letter transliteration, punctuation/spacing and legal forms are normalized; trailing social qualifiers such as `group`, `gruppen` and `global` are checked as additional full-name keys. There is no substring/fuzzy-name ownership inference.

Relationship exceptions require explicit available own-company BRREG subunit, parent or subsidiary claims with registry citations. Company-name similarity, website branding, a sibling in the same group, and stale carried-forward relationships cannot grant an exception. Other social vetoes remain effective.

Archive SHA-256: `1c89710e5b01f8617e86d09fbdff4a52f2f8dbbba297e74f7164b5984f5a0384`.

Decompressed corpus SHA-256: `b82d6a3e7231d1759a958c282bc4366b80ec2fab8095053d8ed7fa9cd01bc838`.

Build: `python scripts/build_social_company_names.py`, with no network access. Machine-readable provenance, row count, compressed size and index SHA-256 are in `social_company_names_build.json`. The index is included in the distributable wheel; no runtime corpus download occurs. Repository MIT licensing covers code/documentation, not a new licence grant over the upstream dataset.

Upstream licence status: the downloaded competition JSONL contains no licence statement. Its public URL does not establish a general redistribution licence. No upstream MIT or NLOD licence is asserted for this derived index; permission remains unresolved. See `docs/SOURCES.md`.
