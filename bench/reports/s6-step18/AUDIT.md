# Pre-code saved-feed audit

No crawl or new source requests. Saved Step 17 run `20261107T052914870839Z-acaca26`. The pre-code retained-evidence scan covered 13 feed bodies. A complete request-log cross-check then found two more pages (810 subunit updates with no originally eligible claims). All 15 bodies were checked by SHA-256; the original 534-claim threshold decision is unchanged.

| Metric | Count |
|---|---:|
| feed pages | 15 |
| returned event records | 7985 |
| published announcement claims | 2904 |
| published distinct event records | 1945 |
| eligible returned claims before cap | 3438 |
| eligible with cap50 | 3438 |
| companies at existing cap | 86 |
| companies losing eligible claims to cap | 80 |
| observed out of window events | 0 |
| companies with observed out of window events | 0 |
| extra claims from saved feed with cap50 | 534 |

**BUILD B:** 534 additional already-supported claims exceed the 300 threshold. The old cap counts announcement claims, so one raw update record with multiple explicit changed fields can produce multiple claims. Existing IDs are retained.

There were zero observable out-of-window records because the API query itself requested only 24 months. The number excluded in months 25-36 is **unknown**, not zero; it cannot be reconstructed from these saved bytes.

Raw records include 991 explicitly unspecified types. Expanded publication will label those only as an unspecified registry event, never infer a board/financial/business event. Records with no recognised change detail will say only that a registry update was recorded. Major-only briefing selection remains unchanged.

[Counts and all page URLs/hashes](audit.json).
