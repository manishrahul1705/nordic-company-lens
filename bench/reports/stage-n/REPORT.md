# Stage N: evidence presentation

Display only, from the unchanged Stage G run 1 envelopes. No agent run or new source requests.

## Audit and changes

Before: the verified-website drawer placed its exact quote below the viewport (top 1,635 px at 360 px; 1,053 px at 1,280 px). It overflowed horizontally on mobile, led with the full value/metadata dump, and repeated adjacent citation chips.

After: a plain-language explanation maps only existing proof types; the exact recorded quote comes first, followed by the source URL and retrieval date. Technical metadata and recorded value fields remain reachable in collapsed Technical details. Supplementary evidence remains in Additional supporting sources. Unknown proof types do not receive invented explanations.

The original citation elements and targets remain intact. Adjacent citations get one Sources control, with every original citation selectable in the same drawer. The tested seven-citation sentence retains all seven sources. Explore and Compare align at 360 px; the landing search placeholder is shorter. Long URLs wrap and have a full-URL copy control.

All eight proof types used by the 113 published websites have explanations. Every published website's first evidence source already matches its recorded proof-page URL; no evidence reordering or extraction changes were needed. Exact quotes retain their captured spelling and markup.

## Verification

Full suite: 1,402 passed, 0 failed (463.86 s). Final site-focused recheck: 24 passed (23.89 s), including the large-company compact fallback.

Open-drawer before/after screenshots and assertions cover 360x812 and 1280x900, light and dark. At 360 px after: quote begins at 184 px, source link ends at 440 px; explanation, quote, URL, retrieval date and Close fit without scrolling. Technical details start closed. Copy control retains the full source URL. Every grouped citation is reachable; header link tops match.

The broader offline regression audit checks search by name/orgnr, profiles, comparison, and internal links from the index plus 30 company pages. No horizontal overflow, clipped text, overlaps, narrow wrapping, undersized tap targets, raw JSON, broken internal links, external requests or JavaScript errors were detected. Its four date-pattern matches are the exact founding-date source value 2020-11-17 in the sparse company's drawer, not ISO timestamps or newly created values.

Both complete 1,000-company generations produced 4,726 byte-identical files, zero warnings, and a largest HTML page of 239,582 bytes. Input envelopes and profiles retained their original SHA-256. Generation/determinism results: see generation-after.json. Scope checks: scope-integrity.json. The payload function, compact fallback and 250,000-byte gate are unchanged. Proof/scoring/source/budget/configuration/lock files are unchanged. Envelopes and profiles are checked for unchanged SHA-256.

## Screenshots

- Before: before/360-light-drawer.png, before/360-dark-drawer.png, before/1280-light-drawer.png, before/1280-dark-drawer.png.
- After: after/360-light-drawer.png, after/360-dark-drawer.png, after/1280-light-drawer.png, after/1280-dark-drawer.png.
- Broader navigation/profile/compare checks: regression/after/.

No dependencies, network calls, evidence rewrites or new proof reasons. No push.
