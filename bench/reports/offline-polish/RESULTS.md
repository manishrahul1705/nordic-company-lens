# Offline site polish

Completed the requested presentation changes without changing saved company data, collection, claims or synthesis.

The home hero background spans the viewport while content stays on the 1200 px grid. Navigation has one Search button, Explore, Compare and theme toggle. Company headers have flat metadata pills, a copy button, separate Compare/Watchlist actions, title-case municipalities and true-only red status badges. Avatars skip leading digits and symbols when a letter exists. Dates outside the evidence drawer use day/month/year presentation; raw evidence and source URLs remain unchanged. Source-receipt excerpt fragments omit orphan time suffixes in presentation; the complete original evidence remains available in the drawer. Zero-valued hero metrics are omitted.

Inter (UI) and Fraunces (headings) are shared local WOFF2 assets with SIL OFL 1.1 licence texts and provenance. Latin coverage includes Norwegian characters (æøåÆØÅ). Inter is 28,768 bytes and Fraunces 18,116 bytes: **46,884 bytes combined**, below 250 KB. Both use font-display: swap and system fallback stacks. No CDN or external font request is used.

Cards have the reference radii/shadows, hover lift and 3-degree perspective tilt, disabled under reduced motion. Stat cards have an inner highlight. Company header/avatar gradients use a stable orgnr-derived colour. Charts use forest green for revenue and gold for result.

## Validation

- Focused site suite: **32 passed in 40.26 seconds**.
- Full suite: **1,244 passed in 319.93 seconds**.
- Rebuilt the saved final 1000-company outputs offline: 1,002 primary HTML pages plus 2,702 source receipts. Largest HTML page: **237,872 bytes**, below the unchanged 250 KB guard.
- Exhaustive rendered-text scan: **3,704 HTML pages, zero ISO timestamp fragments** outside raw evidence data. [Scan](timestamp-scan.json).
- Original envelopes, profiles and report hashes are unchanged: [integrity](source-output-integrity.json).
- Playwright checked desktop and 375 px layouts, direct company loading, search, compare, drawer, dark mode, no-JavaScript reading and local font loading. No horizontal overflow, page errors, broken links among 4,602 checked internal links, or external requests. [Browser results](browser-results.json).
- Screenshots: `C:/Users/Manish/Downloads/agent-site-new/polish/`; rebuilt site: `C:/Users/Manish/Downloads/agent-site-new/site/index.html`.

## Fresh-clone pair (not skipped)

Because shared binary font assets and template rendering are included, the fresh-clone check was also run. The clone contained the exact final pending runtime bytes, verified by SHA-256. Locked install passed, application credentials/search settings were stripped, and the literal README command ran twice on the release 100 + 3 cohort with the same state directory and no extra refresh flags.

| Run | Seconds | HTTP | Envelopes / profiles | Company changes | Observation changes |
|---|---:|---:|---:|---:|---:|
| First | 215.678 | 763 | 103 / 103 | 0 | 0 |
| Refresh | 211.353 | 742 | 103 / 103 | 0 | 0 |

**Unmodified strict verifier exit 0:** identical claim IDs, 8,462 supported claims, 316 checked source blobs, 418 cited primary sentences and zero unverified values. Both site exports completed with no warnings or deadlines. [Execution](official-run/execution.json), [verification](official-run/verification.txt).

No live 1000-company crawl was performed. No agent data or site JavaScript asset was changed. Nothing was pushed.
