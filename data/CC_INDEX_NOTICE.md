# Common Crawl candidate index notice

Built 2026-11-13 UTC from every complete JSONL record on disk, including partially fetched crawl segments (not only completed segments). Source snapshot: 180,059 records, 180,049 successfully fetched records, 32,608 pages with a labelled checksum-valid orgnr, 20,529 unique labelled orgnrs before domain exclusions. No incomplete trailing bytes. Crawls covered: CC-MAIN-2026-43, CC-MAIN-2026-39 and CC-MAIN-2026-34. Partial crawl coverage, not a complete .no index. Archived page timestamp ranges and snapshot hashes are in cc_orgnr_index_build.json.

After exclusions and subunit-parent mapping: 20,832 candidates, 19,735 parent companies, 20,575 domains; gzip 1,771,479 bytes. Universe candidate coverage: 12,873 / 411,160, or 31.309 per 1,000. These are candidate matches, not verified websites. All 30 deterministic snippet/mapping checks pass.

Access and use are subject to the Common Crawl Terms of Use: https://commoncrawl.org/terms-of-use . Crawled material may have separate third-party copyright, database rights and terms; Common Crawl access does not grant a blanket redistribution licence for that material. This index contains minimal labelled organisation-number excerpts, not archived pages. Distribution and future production use require consideration of these rights; this notice is not a rights clearance.

## Method

Run `python scripts/build_cc_candidate_index.py` using the existing ignored measurement caches. No network requests or agent changes are made by this builder. The input snapshot includes all fully written JSONL lines up to its initial byte length, with the last result per WARC key used. Incomplete trailing bytes, if any, are excluded and reported. Records come from HTML HTTP-200 .no pages selected for homepage/contact/about/privacy path patterns, with up to two selected pages per registered domain. This is not a random or exhaustive crawl sample.

Require a labelled, checksum-valid nine-digit Norwegian organisation number in the retained snippet. Exclude the entire registered domain if any processed pages identify three or more different valid organisation numbers, before parent mapping. Failed records are not candidates. Map exact subunit numbers to parents using the cached official Bronnoysundregistrene subunit bulk file (NLOD 2.0, https://data.brreg.no/enhetsregisteret/api/underenheter/lastned/csv). A number absent from that mapping is retained unchanged; absence does not prove main-entity status.

For each parent/domain pair retain the newest archived page timestamp, with deterministic lexical tie-breaking. Retain at most three domains per parent, prioritising newest timestamps, then serialize parents and domains deterministically. Gzip has a fixed zero mtime. Entries retain domain, crawl ID, archived URL, timestamp, observed organisation number and its label snippet (at most 120 characters). The observed number may be a subunit, so it need not equal the parent key. The build report contains counts, snapshot/index hashes and 30 fixed-seed snippet and mapping checks.

**candidates only; every website is re-verified live at run time with the agent's ownership proof**.
The runtime reads this bundled index locally as candidate nominations; inclusion itself is never live verification. Archive mentions may be customers, former owners or stale data. Universe coverage counts candidate matches, not verified website coverage. The cached Builderr universe is used only for the coverage denominator, not as ownership proof.
