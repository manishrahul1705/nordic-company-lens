# Official approval and related-entity website snapshots

Credit: Arbeidstilsynet (cleaning register), Statens vegvesen (approved workshops), Brønnøysundregistrene (entity website fields).
Cleaning and BRREG: Norwegian Licence for Open Government Data (NLOD) 2.0, https://data.norge.no/nlod/no/2.0 . Workshops: Norsk lisens for offentlige data (NLOD), https://data.norge.no/nlod/no (catalogue does not specify version).

Only derived selected-row indexes and manifests are shipped. Each *_official_manifest.json records the official distribution URL, retrieval timestamp, original SHA-256/row count and source generation timestamp where supplied (otherwise null). The BRREG download is the already acquired official full CSV; workshop main-unit filtering uses the same snapshot. No competition archive data is used.

Build with scripts/build_approval_websites.py and local raw inputs; raw downloads are not committed. JSON keys are sorted, UTF-8 is preserved and gzip mtime is zero. Index hashes are verified at runtime. No runtime network request is made.

Cleaning preserves the exact status. Only Godkjent med ansatte and Godkjent uten ansatte are approved; other statuses remain literal and approved=false. No match produces no claim. No nested cleaning subunit is treated as independently approved. Workshops retain one record per approval number with exact type and address; identifiers not present as main units in the BRREG snapshot are excluded, never reassigned to a parent.

Related websites require an available, evidence-backed group relationship already published in the subject's own record and the related entity's registry hjemmeside. Both evidence sources are cited. These claims are explicitly registry-declared, not ownership-verified, and confer no authority to reuse social, brand or news content. Existing official_website logic is unchanged.

Robots findings from the feasibility scan: registerdata.arbeidstilsynet.no/robots.txt returned 403; www.arbeidstilsynet.no/robots.txt also returned 403. No parseable policy could be established there. We use the officially published bulk download only, not a runtime crawler. The workshop export backend robots returned 404, while its frontend robots had no disallow; it would be inaccurate to report 403 for that backend. Catalogue-host /api/ is disallowed: no catalogue API is used at runtime. All snapshots are historical and absence or an old status does not establish current non-approval.
