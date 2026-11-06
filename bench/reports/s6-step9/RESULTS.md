# S6 Step 9 — offline UX and cited company briefs

## Delivered

The official command's static site supports directory search by name or orgnr, company pages, two- or three-company comparison with URL-preserved selection and a copy-link control, and fact source panels with captured excerpts, URLs, retrieval dates and reporting periods. The site opens directly with `file://` and uses bundled scripts, CSS and system fonts. Sharing a comparison requires the recipient to have the generated site folder; it is not a hosted public URL.

States read **Found**, **Not found**, **Couldn't check**, **Withheld**, **Blocked** and **Not applicable**. Failed refreshes retain prior supported facts with explicit stale dates. Missing facts open a panel explaining that no external evidence supports a value. On narrow screens, comparison cards and dense tables stack vertically.

Each output's `run.synthesis.brief` has three short cited parts: `what`, `changes` and `unknowns`. What-it-does sentences reuse validated registry/site fact sentences. Changes display previous → current values, a dated no-change notice, or an explicit first-observation notice. Every missing or stale enabled section has its state and reason. Every sentence includes claim IDs. Snapshot dates, states and reasons cite deterministic `brief.context_claims`, explicitly labeled **Run metadata** rather than external evidence. They do not enter or inflate the source-claim list. Both the writer and independent output verifier recompute the brief's sentences, citations, IDs and metadata; a forged sentence is rejected. The existing detailed synthesis remains available separately.

## Browser checks and screenshots

Playwright used installed Chromium against local file URLs, at **1280 × 900** and **360 × 900**. Checks exercise name/orgnr search, company pages, fact panel loading, two/three-company comparison, comparison link reload and copy-link handling. The audit traverses every generated company page at both widths, asserts document width does not exceed viewport width, and rejects JavaScript errors and HTTP/HTTPS requests. See [browser-check.json](browser-check.json).

An initial all-profile scan caught a mobile overflow on a changed-value page with long registry IDs/JSON. The one-line CSS wrapping fix was retested across all 101 generated profile pages at both widths, including that changed-value diagnostic. Final screenshots are generated from the validated official output rendered with the final site assets.

| Page | Desktop | 360 px |
|---|---|---|
| Directory/search | [1280 px](screenshots/index-1280.png) | [360 px](screenshots/index-360.png) |
| Company profile | [1280 px](screenshots/summary-1280.png) | [360 px](screenshots/summary-360.png) |
| Three-part brief | [1280 px](screenshots/brief-1280.png) | [360 px](screenshots/brief-360.png) |
| Source panel | [1280 px](screenshots/source-1280.png) | [360 px](screenshots/source-360.png) |
| Comparison | [1280 px](screenshots/compare-1280.png) | [360 px](screenshots/compare-360.png) |

Reproduce with Playwright installed in a local tools directory, `NODE_PATH` pointing to its `node_modules`, and optionally `PLAYWRIGHT_CHROMIUM_EXECUTABLE` pointing to an installed Chromium:

```sh
node scripts/verify_site.cjs out/site bench/reports/s6-step9/screenshots
```

## Official fresh-clone command

Source revision: `d8388d6` (all runtime changes, including UTC normalization). A later CSS-only commit `f23451f` adds wrapping for long change records; the final site was regenerated from the verified envelopes with that asset and separately tested in Playwright. The original envelope files are not rewritten for validation.

Fresh local checkout and `uv sync --frozen`; application credential/search/model environment variables removed. Input: the same 100 valid public-BRREG identifiers not in `bench/inputs`, plus three invalid lines, used for Step 8b. Both commands use the same state directory, with no `--previous`:

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --profiles-output out/profiles.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

Final run counts and the strict verifier result are recorded in [validation.json](validation.json). Source blobs, both full outputs, profiles, reports and execution metadata are retained under the ignored `bench/cache/s6-step9-utc/` folder.

| Metric | Initial baseline | Same command, run 2 | Same command, run 3 |
|---|---:|---:|---:|
| Envelopes / profiles | 103 / 103 | 103 / 103 | 103 / 103 |
| Wall seconds | 256.716 | 246.073 | 250.892 |
| HTTP requests | 999 | 1001 | 998 |
| Max HTTP per company | 18 | 18 | 18 |
| Company changes | 0 | 0 | 0 |
| Observation changes | 0 | 1 | 0 |
| Deadline hits / warnings | 0 / 0 | 0 / 0 | 0 / 0 |

**Strict pair 2 → 3: PASS**, 103 outputs in each, identical claim IDs, 0 company changes and 0 observation changes. Both consecutive commands used the literal README command and the same state folder. Verification checked 7,683 published claims, 337 original source blobs, 103 detailed syntheses and 712 cited detailed sentences, plus exact recomputation of every new brief. Run 3 has 203 what-it-does, 103 change-notice and 373 missing/stale-section brief sentences. It also passed standalone full source/evidence verification. Each invalid line retained one failed output. All three runs were within budget; no model calls, search or paid source costs.

The UTC-fixed checkout was invoked three times. Its first pair had zero company changes but one source observation: A-HJORT's initial news timeout recovered to a successful checked absence. The first-ever failed state was preserved honestly; it was not rewritten for the check. [SOURCE_RECOVERY_DIAGNOSTIC.json](SOURCE_RECOVERY_DIAGNOSTIC.json) records that transition. The third identical invocation verified the consecutive unchanged snapshots after recovery.

### BRREG timezone issue found and fixed

The first completed pair at `8c6f89d` reported 16 false changes: the same registry publication instants were returned once as UTC and once as a local offset (for example, `16:00Z` versus `17:00+01:00`). This was not accepted as a successful refresh. [TIMEZONE_DIAGNOSTIC.json](TIMEZONE_DIAGNOSTIC.json) retains the exact differences. Extraction now normalizes the publication instant to UTC before calculating the claim ID; the original response bytes and hash remain the evidence. Tests cover standard and summer offsets and ensure a genuinely different instant remains a different claim. The fresh-clone pair was repeated after this fix.

## Tests and examples

Final full suite: **967 passed in 328.84 seconds**. Tests include three-part citations, dated no-change notices, stale unknowns, exact old/current source sides, invalid/missing citation IDs, forged metadata/text rejected by the verifier and writer, and equivalent registry timestamp offsets. The strict verifier's claim-ID and zero-change assertions were not relaxed.

Two real output summaries with full citation records are in [EXAMPLE_SUMMARIES.md](EXAMPLE_SUMMARIES.md) and [EXAMPLE_SUMMARIES.json](EXAMPLE_SUMMARIES.json).

## Commits and limits

- `84e8f75`: cited briefs, responsive offline site, source/status controls and Playwright audit.
- `8c6f89d`: writer-side brief validation and schema documentation.
- `d8388d6`: stable UTC publication instants and regression tests; expanded browser audit.
- `f23451f`: long changed-value text wraps at narrow widths.
- The final evidence/report commit is listed in the response.

All commits are authored/committed as Manish Rahul <manishrahul1705@gmail.com>. Work stayed on main. Search OFF, no model calls, no paid services, no push. No evaluator points are claimed. Live sources may legitimately change; the report distinguishes source content from run metadata.
