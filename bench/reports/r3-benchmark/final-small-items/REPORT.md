# Final R3 small-item checks ? 12 November 2026

Only `more-websites` changed. No push or changes to main/fix-large-company-site.

## Identifier false positives

The generic raw-owner scan masks digits in HTML id/class/data-* and inline-style attribute values, and ignores CSS style-block contents. It parses actual start tags, so JSON strings containing attribute-like text remain unchanged. Offsets and original source bodies stay intact. Hidden footer identifiers and entity-card/fallback number scans use this filtered markup. Visible numbers, metadata and JSON-LD ownership identifiers retain their existing proof/veto behavior.

Regression coverage includes the bnv.no `gap-943737207` pattern, quoted/unquoted layout attributes, CSS, foreign visible/JSON-LD/meta identifiers, real own identifiers, entity cards, split visible digits and JSON preservation. Existing wrong-company fixtures and expectations were not changed.

Offline replay of all four retained bnv.no company pages (home, contact, about, privacy) now returns **VERIFIED / orgnr_on_page**, with no foreign numbers. The formerly rejected privacy body SHA is `076fc28c4cbcfb756b5ebaa3196df6d2c841fe00746c324dae92666fa0ee4d82`. Original saved output/response bytes were not changed. This is an ownership-proof replay, not another live run or a regenerated 1,000-company scoreboard. See [checks.json](checks.json).

## Release timing and index cache

The already-measured fresh-clone release cohort has 100 valid companies plus three invalid lines. Full-command wall time per 100 valid companies:

| Run | Seconds | Minutes | Below 45 minutes |
|---|---:|---:|---|
| 1 | 372.766 | 6.213 | yes |
| 2 | 254.722 | 4.245 | yes |

These are the original measured times, before this cache correction; no new timing run is implied. The previous strict refresh-pair failure remains documented (five newly observed facts after a contact-page timeout recovered; zero company changes).

The two indexes already used an LRU cache, but concurrent first misses could still decode the same file more than once. A lock now surrounds the cached lookup, guaranteeing one initial decode per filename across the four source workers. Both runtime callers use this local loader, and only these two filenames are requested. The 4-entry cache holds both for the process lifetime. Instrumentation of the actual bundled files with 100 calls/four concurrent workers records exactly **one gzip open each**, two cache misses and 98 hits; callers receive the same object per filename. A concurrency regression test also enforces this. No network is used by the loader.

## Istad missing blob: cause found

**Microsoft Defender quarantined the exact homepage blob.** Targeted local Defender Operational events identify hash `204ee52edfc85ec7e08936232092cbc6351b4e8d96534264bd1bb9ca00183012` as `Trojan:Script/Wacatac.H!ml`:

- Event 1116: detection at 2026-11-12 04:53:00 UTC (**10:23:00 IST**).
- Event 1117: successful quarantine at 2026-11-12 04:57:52 UTC (**10:27:52 IST**), action success code 0x00000000.

This reports Defender's classification, not an independent malware determination. [Filtered event metadata](defender-events.json) contains only this blob's matching events. No quarantine restoration or exclusion was performed.

The request log records HTTP 200, a body hash, no error and no truncation. Of 6,607 distinct request body hashes, this is the only missing file ([audit](blob-audit.json)). Production audit found no blob deletion/cleanup path. The runner creates one BlobStore per run; its lock serializes writes. It verifies an existing file or writes/closes it before returning the hash. The 256 MiB limit only bounds the recent-memory cache, never disk writes. The HTTP 2 MiB cap saves a partial blob and reports body_cap instead of returning a successful page; interrupted response chunks are also retained. The only production unlink calls manage progress.json/temporary progress files, not blobs. The R3 runner and unrelated overnight worker contain no state-blob cleanup. **Storage behavior was left unchanged.**

## Validation

**1,275 tests passed in 417.26 seconds** (`uv run --frozen pytest -q`), including 16 new regression cases. Full output is retained in [pytest.txt](pytest.txt). No existing test fixture or expectation was changed. No live crawl was repeated for these small items.
