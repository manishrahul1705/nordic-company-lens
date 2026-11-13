# Stage M offline-site UX pass

**PASS.** Display-only changes, no research run. Stage G run1's saved envelopes/profiles are unchanged; 1,000 companies rendered, zero warnings, no source/proof/scoring/budget/config/runner changes or dependency/lock changes. Existing editorial colours/fonts/layout language retained. Main before merge is77ecfed, the requested target.

## Audit before editing: first ten seconds, worst first

1. At360px the landing hero and three long example buttons push the headline counts below the first screen. The long input placeholder clips, so the search purpose relies on placeholder text.
2. The company identity hero consumes most of a mobile screen; the briefing starts below the fold.
3. Generic unavailable/withheld paragraphs do not surface the recorded candidate reasons, making deliberate abstention look like unexamined missing data.
4. Website evidence has the exact quote and identity level, but proof_type is not prominently labelled in the source drawer.
5. Mobile Dashboard tab text is clipped (four audited light/dark landing/search screens).

Already working and therefore preserved: legal-name/orgnr search, global / and Ctrl/K shortcuts, offline local fonts, source quotes/URLs/dates, comparison/reload, theme persistence, minimum44px targets and no horizontal scrolling. Audit screens are saved before changes; generated unchanged-site metrics in generation-before.json.

## Changes

- Compact existing mobile hero spacing and example-chip presentation so search, checked date and four headline cards fit without scrolling at360x812. Example chips stay on desktop; no new controls or filtering features.
- Visible Find a company label with / hint and landing autofocus; existing matching and keyboard handlers preserved.
- Smaller mobile company avatar/header and tighter briefing spacing; identity remains first, briefing before detailed sections. Existing what-the-company-does text and every citation remain unchanged.
- A recorded-checks disclosure shows plain explanations only for recognized diagnostic codes actually present in envelope errors/candidate diagnostics. No reason inferred or invented; exact code displayed alongside each label. Unrecognized/unrecorded reasons retain existing fallback text. All original availability states unchanged.
- Both static evidence and interactive drawer explicitly label existing proof_type. One-click drawer still shows the original exact evidence span, URL and dates. No proof type, claim or quote changed.
- Flexible wrapping fixes mobile Dashboard tab clipping; visible focus outline and existing44px targets retained. No JavaScript framework or external dependency added.

## Before / after

| Check | Before | After |
|---|---|---|
| Headline counts above fold at360px | FAIL | PASS |
| Mobile briefing hierarchy | Header dominates | Briefing visible earlier |
| Autofocus / visible search label | Absent | PASS |
| Legal name and orgnr search | PASS | PASS |
| / shortcut | PASS | PASS, visibly documented |
| Recorded withheld reasons | Generic summary | Existing-code disclosure |
| Website proof label + quote in one click | Type buried/unlabelled | PASS |
| Clipped-text audit screens | 4 | 0 |
| Horizontal overflow / overlaps / narrow one-letter wrapping | 0 / 0 / 0 | 0 / 0 / 0 |
| Targets under44px | 0 | 0 |
| Raw JSON / raw ISO timestamps | 0 / 0 | 0 / 0 |
| Broken internal links (index+30profiles) | 0 | 0 |
| External requests / page errors | 0 / 0 | 0 / 0 |
| Compare two companies + reload | PASS | PASS |
| Theme persistence | PASS | PASS |
| Largest HTML | 239,582bytes | 239,582bytes |

Playwright uses file://,1280x900 and360x812,Light andDark. No local server, CDN, analytics or runtime network. Landing/index, Tensio rich profile922828172, Dragehaugen917998787 and sparse/heavily unavailable NRP926077422 profiles, evidence drawers and compare captured. All97before/after PNGs are indexed in SCREENSHOTS.md. Screens include all requested landing/rich/withheld/compare views in both themes/widths.

Additional accessibility checks: one H1 and main landmark per representative page; no unlabelled images or empty unlabelled buttons. Computed contrast of checked visible text on landing and rich profile is>=4.5:1 in both widths/themes (zero failures); focus rings visible. This is a focused automated/browser pass, not a complete WCAG certification. accessibility.json and semantics.json retain exact scope/results.

## Determinism, evidence and size integrity

Two full generations read the same original envelopes, then **all4,726actual generated files were reread and SHA-256 compared: identical**. Envelope SHA9dfd143f31eeee6149d2b242789a87045502b452d4e033d2f2488c6a3de3d705 and profile SHA986cac1eb5f016c352c2cb3c83da5d4bd5fc6e7b1815a2ac8c724548c323a749 unchanged. generation-after.json contains both identical metrics and original hashes. The readback pass was slow; a supplementary writer-boundary check was briefly started but cancelled when the stronger original disk comparison completed. No substituted result or security-setting change.

1,000profile pages+index/compare,2,715receipt pages; every HTML file<250,000bytes. No warning/invalid identifier. compact_profile function AST and PAGE_GATE unchanged; test_very_large_company_compacts_instead_of_failing_the_site passes. Website claim data and sampled directory/profile payloads before/after are byte-identical; only presentation output differs. No claim/value/count/proof/availability/envelope change.

## Tests

Full suite **1,402passed,0failed415.22s**. First suite had two unchanged subprocess timeout failures (5s link-localization and45s process-recovery); both passed independently without modification (2passed82.38s), then the full suite passed. Initial failure log retained.22site tests including fallback passed focused13.19s; two additional tests verify recorded-only reasons, no invented reasons and input immutability. No existing fixture/expectation weakened.

## Deliberately unchanged

No proof, scoring, source, budget, claim serialization or research behavior. No new dependencies or runtime requests. Existing match logic, comparison behavior, states, local fonts, palette, typography, section order and size/compact fallback preserved. No redesign. No fabricated reasons for diagnostics we do not explicitly map. No JBox repository changes: this is the agent-generated offline site only.

## Evidence paths and delivery

- Before landing:`before/360-light-landing-before-search.png` and1280equivalent; before profiles/compare same directory.
- After landing:`after/360-light-landing-before-search.png`; rich:`after/360-light-922828172.png`; sparse/withheld:`after/360-light-926077422.png`; compare:`after/360-light-compare.png`; one-click proof:`after/360-website-proof.png`.
- Full inventory:SCREENSHOTS.md; browser-comparison.json; before/after/audit.json; proof-one-click.json; accessibility.json; semantics.json; generation-before/after.json; scope-integrity.json; pytest.txt.

Commit as Manish Rahul and normal merge into the existing main worktree bench/cache/stage-a-main on top of77ecfed. No push.
