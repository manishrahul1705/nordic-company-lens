# S6 Step 12 — final cleanup decision

**ROLLBACK the annual-report PDF lever completely. KEEP only the tested generic guard fixes, plus the requested live-CI verification scope.** No new 1000 crawl, no new fresh-clone crawl, no search, no push during this cleanup.

## A. PDF rollback and saved Step 11 comparison

Removed the annual-PDF nomination module, isolated parser, official document downloader and every call into them. Removed pypdf from pyproject.toml, uv.lock and the installed runtime. The official collector, transport, official HTTP client and dependency files now exactly match Step 11 (`2e7fb3b`). This also removes the Step 12 exact-`.no` transport extension; the optional JS lever was never adopted. The pre-existing scan of already-held non-PDF account text remains unchanged and performs no downloads. [Runtime dependency/module check](cleanup-pdf-removed.json).

The rejected completed Step 12 trial produced **0 PDF candidates**, **291 scanned/empty PDFs** and **555 BRREG 429s**. It is not used to claim kept coverage or performance. The earlier content-negotiation trial was interrupted before final outputs. All existing raw runs are preserved; no new benchmark was started for this decision.

Only the generic guards remain: own-publisher prefixes; legal names split across adjacent footer/heading nodes; comparison-only whitespace/diacritic/damaged-character normalization; own-identifier-backed singular/plural title spelling. Registry values are never rewritten. A damaged-name repair requires the exact publisher-context orgnr; different legal forms, foreign owner identifiers, group/shared sites and placeholder vetoes remain in force. No company-specific runtime exception.

Applied these guards to the **reviewed Step 11 saved snapshot**, using only its retained request bodies. This is an incremental offline policy projection, not a new crawl or remeasured runtime.

| Section / check | Step 11 before | After generic guards |
|---|---:|---:|
| Identity | 1000 | 1000 |
| People | 997 | 997 |
| Subunit workplaces | 774 | 774 |
| Typed location profiles | 997 | 997 |
| Financials | 999 | 999 |
| Websites | **103** | **107** |
| Social available companies | **41** | **43** |
| Jobs | 3 | 3 |
| News/activity | 236 | 236 |
| Previously published claim IDs removed | — | **0** |
| New website links reviewed | — | 4 correct |
| New social URLs reviewed | — | 3 correct |
| Wrong-company additions | — | **0** |

Recovered websites: KN Elektro, Lofotposten, Control Solutions and GS Elektro Gjøvik. KN Elektro contributes one Facebook URL; Control Solutions contributes Facebook and Instagram. [Every item, verdict and ownership explanation](CLEANUP_REVIEW.md), [verbatim excerpts, dates and hashes](cleanup-new-items.json), [complete generic saved-page recheck](cleanup-saved-step11-recheck.json), [counts](cleanup-counts.json). Existing supported Wikidata socials remain unchanged; the real runner emits them after website collection, so the offline helper preserves them too.

**Historical-evidence limitation:** one of the 4017 unique source blobs referenced by the old Step 11 snapshot is now absent: pederistad.no, orgnr 911691248, SHA-256 `58470eb16cd4ccb2b42a170fbc21c405bada197e2071da426d6652f5ddb8c6a9`. Its existing row is preserved unchanged and explicitly excluded from body revalidation. No newer body was fetched or substituted. All other previously published website guard bodies were checked without a new veto. Therefore “zero losses” is the saved-snapshot claim-set comparison, not a claim that all historical evidence was independently revalidated. [Missing-blob inventory](cleanup-missing-step11-blobs.json).

The four affected complete company outputs independently pass the verifier: **552 claims**, **23 source blobs**, **47 cited synthesis sentences**, **0 unverified values**. This covers every newly published website/social item and its associated output. [Verification](cleanup-additions-verification.json).

## B. Live CI

Only live-20 opts into:

```sh
--require-clean --clean-sections identity roles accounts subunits
```

These are registry identity / people / financials / locations. A failed, blocked or stale required registry section still rejects the run; a missing required section also rejects it. The default `--require-clean` remains strict for all enabled sections.

Website (including social), hiring/jobs and activity may honestly be failed, blocked or stale in this scoped live job. The verifier prints `failed_or_stale_sections`, including organisation number, family, current state, stale-attempt metadata and explicit failure codes/messages. Long website candidate diagnostics are summarized to specific failure reason codes rather than flooding the log. [Representative mocked DNS-failure log](cleanup-ci-log-example.json).

Schema, membership/order, source SHA-256, verbatim excerpts, citations/synthesis, output limits and global operational/budget checks remain strict for every section. No failed source is relabelled as successful. The GitHub workflow has not been remotely triggered; this is a local configuration/test fix, with no push.

## Validation and commit

`uv sync --frozen` passed and uninstalled pypdf. Focused cleanup tests: **62 passed**. Full final suite: **1082 passed in 287.74 seconds**. [Full suite](cleanup-full-tests.txt).

Tests cover optional failed/stale handling in all envelope shapes, default strictness, every required registry family, omitted required sections, corrupted evidence rejection, concise reason summaries, split legal names, own-publisher prefixes, own-orgnr-backed variants and AS/AB conflict rejection.

Final cleanup is committed as Manish Rahul <manishrahul1705@gmail.com>; the response gives its commit hash. Prior local trial commits remain in history as rejected experiments; they are not active PDF paths. No push.
