# Offline site restyle - JBox design

Base `dba197e66134425d15fee9f85af3fbdc96967b86`. No push. Only site templates/CSS/JS and the existing site-test markup selectors changed. Collection, claims, citation inputs, synthesis wording, envelopes and profiles are unchanged. Original final-run envelopes/profiles/report hashes all match. [Scope](scope-check.json), [input hashes](source-output-integrity.json).

## Presentation

Reviewed the supplied JBox screenshots before implementation. Applied the requested warm light/forest dark variables, system UI and Georgia/Cambria editorial stacks, sticky wordmark navigation, theme persistence before paint via a constant CSP-hashed inline bootstrap, forest lattice hero, source-derived verified-claim stats, searchable/filterable company cards, company header band, cited briefing first, separate GLEIF section, financial chart/table, typed locations, website/social, jobs, separated company-news/registry/procurement headings and missing-section context.

Retained the existing supporting-detail and deferred official-attribute mechanisms. Sources open a right-hand drawer with exact saved quotes, method, URL, retrieval time and reporting period. Without JavaScript, every displayed source control links to bounded static receipt pages; all deferred facts have no-JS receipt links. Receipts can split a very long evidence set across linked pages without dropping any record. Context citations remain explicitly run metadata. Structured objects use labelled fields rather than raw JSON. Registered workplace count uses only supported subunits, excluding postal addresses; Tensio's header and unchanged briefing both show four.

Comparison retains existing four-company capacity and shareable links, with two-company reference styling, accent headers, avatars, dated revenue/result/employees and full detailed comparisons. Existing controls, watchlists, analytics, exports and source-status detail remain accessible. No external font, image, script or CDN. Existing reduced-motion rules are retained and the new motion is disabled by prefers-reduced-motion. Controls/disclosures have 44px minimum targets and visible focus.

## Saved-run offline rebuild

Source: `bench/runs/20261107T094159020873Z-39a7314/envelopes.jsonl`. No crawl. Generated site: `C:\Users\Manish\Downloads\agent-site-new\site`.

- 1,000 company pages, index and comparison:1,002 primary pages; 2,702 additional bounded static receipt pages.
- Every HTML page below 250 KB; largest **236,458 bytes**. The original 250 KB guard is retained and additionally checked for all HTML, not relaxed.
- All **5,052 primary briefing sentence texts** match the original saved sentences exactly. No synthesis recomputation or replacement.
- Full evidence data remains in local company data files. Static receipts add disk use (roughly 754 MB total site); data files are not HTML pages and retain the existing shared supporting-data representation.

[Build metrics](offline-build.json), [briefing preservation](briefing-integrity.json). Earlier iterations hit the size guard: redundant empty drawer containers were removed, and oversized static receipts were split; no information was deleted to pass the guard.

## Browser and tests

Playwright/installed Chromium at **1366x900** and **375x812**, file:// only: index search Tensio, Tensio 922828172 page, evidence drawer, comparison, dark theme and reload. Phone document width never exceeds375px. **140 local file requests, zero external requests, zero page errors**. Internal-link crawl checked **4,603 links across index +20 company pages: zero broken links**. No-JS check shows the full 1,000-company list and opens a readable evidence receipt from Tensio. All HTML sizes independently checked. [Browser result](browser-results.json), [exact browser check](browser-check.py).

Screenshots in `C:\Users\Manish\Downloads\agent-site-new\`: index-search-desktop.png, company-desktop.png, drawer-desktop.png, company-dark.png, compare-desktop.png, index-phone.png, company-phone.png, compare-phone.png, drawer-phone.png.

Focused suite: **28 passed in 6.40 seconds**. Full suite: **1,244 passed in 313.88 seconds**. The test change only replaces the removed empty inline-panel selector with assertions for a real static receipt link/file/anchor, and permits only the exact constant CSP-hashed theme bootstrap. All source/evidence equality, XSS, unsafe-URL and information-presence checks remain. The existing storage-denied theme regression passes unchanged. Earlier selector/action-label failures are build history, not final failures. [Focused tests](final-focused-tests.txt), [full suite](validated-full-tests.txt).

## Fresh clone

Final-source manifest is recorded before validation. A fresh local clone of the base plus the exact three site files runs the literal README command twice on the release 100+3 cohort and a clean state directory; no --previous. Application credential/search environment stripped. Final CSS/JS presentation bytes were copied before the first site export, then remained unchanged. [Source manifest](final-runtime-source.json), [matching source hashes](final-source-integrity.json). The earlier pre-final validation was stopped and is not claimed as final.

Exact pair results follow below. No push. Commit authored/committed as Manish Rahul <manishrahul1705@gmail.com>. Hard stop 18:15 IST; final check time recorded before commit.


## Final fresh-clone result

**PASS:** 207.047 seconds/757 HTTP, then 206.235 seconds/744 HTTP; 103 envelopes/profiles each;**zero company changes, zero observation changes, unmodified strict verifier exit0**. Both new site exports available, zero warnings/deadlines. [Exact command/results](official-run/RESULTS.md).

All final site source hashes match the validated clone. The final saved-run screenshots/browser checks use the same files. No external requests in offline viewing; the separate README commands perform their normal authorized public-source collection. No new 1000 crawl. Only site-generator files and markup-selector tests changed. Completion check is before 18:15 IST; exact UTC/IST timestamp is in completion.json.

Full saved-data comparison also passed: **174,692 claims including absence markers**, **217,283 claim/evidence links** checked across all 1,000 company data files. Claim values, availability, evidence references and every original source-record field match. [Payload integrity](payload-integrity.json).
