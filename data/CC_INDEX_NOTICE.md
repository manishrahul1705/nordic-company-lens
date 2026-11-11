# Common Crawl candidate index notice

Built 2026-11-11 UTC from the completed cached measurement records available at build time (see cc_orgnr_index_build.json for the snapshot hash and byte count).
Source: Common Crawl CC-MAIN-2026-43, October 2026 crawl, 2026-10-05 10:56:23 through 2026-10-18 05:34:47 UTC. Official crawl metadata: https://index.commoncrawl.org/collinfo.json . Only this crawl was present in the snapshot; this is partial crawl coverage, not a complete .no index.

Access and use are subject to the Common Crawl Terms of Use: https://commoncrawl.org/terms-of-use . Crawled material may have separate third-party copyright, database rights and terms; Common Crawl access does not grant a blanket redistribution licence for that material. This index contains minimal labelled organisation-number excerpts, not archived pages. Distribution and future production use require consideration of these rights; this notice is not a rights clearance.

## Method

Run `python scripts/build_cc_candidate_index.py` using the existing ignored measurement caches. No network requests or agent changes are made by this builder. The input snapshot includes all fully written JSONL lines up to its initial byte length, with the last result per WARC key used. Incomplete trailing bytes, if any, are excluded and reported. Records come from HTML HTTP-200 .no pages selected for homepage/contact/about/privacy path patterns, with up to two selected pages per registered domain. This is not a random or exhaustive crawl sample.

Require a labelled, checksum-valid nine-digit Norwegian organisation number in the retained snippet. Exclude the entire registered domain if any processed pages identify three or more different valid organisation numbers, before parent mapping. Failed records are not candidates. Map exact subunit numbers to parents using the cached official Bronnoysundregistrene subunit bulk file (NLOD 2.0, https://data.brreg.no/enhetsregisteret/api/underenheter/lastned/csv). A number absent from that mapping is retained unchanged; absence does not prove main-entity status.

For each parent/domain pair retain the newest archived page timestamp, with deterministic lexical tie-breaking. Retain at most three domains per parent, prioritising newest timestamps, then serialize parents and domains deterministically. Gzip has a fixed zero mtime. Entries retain domain, crawl ID, archived URL, timestamp, observed organisation number and its label snippet (at most 120 characters). The observed number may be a subunit, so it need not equal the parent key. The build report contains counts, snapshot/index hashes and 30 fixed-seed snippet and mapping checks.

**candidates only; every website is re-verified live at run time with the agent's ownership proof**.
This states the requirement for future integration. The measurement branch does not connect this index to the agent, and no live verification is implied by inclusion. Archive mentions may be customers, former owners or stale data. Universe coverage counts candidate matches, not verified website coverage. The cached Builderr universe is used only for the coverage denominator, not as ownership proof.
