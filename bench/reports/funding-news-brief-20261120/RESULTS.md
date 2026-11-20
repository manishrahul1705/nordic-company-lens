# Funding and news in the seven-section brief - 20 November 2026

## Prior work committed first

The initial working tree was checked and contained only the authorized funding/news code, tests, indexes, manifests, notices, docs and reports. Named paths were staged; neither `git add -A` nor raw cache/run/download paths were staged. Both authors are Manish Rahul <manishrahul1705@gmail.com>:

- Funding snapshots: `59b47917b3fa3cd7cafc6c9da45ef1dceed9df62`.
- News items: `fab3653f94536ad29605ce57eac4dedaf40b9f68`.

The working tree was clean after those two commits. Report JSON files are derived measurements/reviews, not raw dataset dumps. CSVs, full downloaded JSON, `bench/cache` and `bench/runs` remain ignored and untracked.

## Finding before synthesis changes

Inspection of sections_extra.py, template.py and company_brief.py found **no funding research/state-aid sentence and no news_item sentence**. Existing activity synthesis only handled its earlier dated_item/registry sources. Existing standing handled the run-local financial comparison. The source claims were published but unused in these brief sentences.

The unchanged validate.py `permitted()` rule requires company-owned activity claims to carry an `identity_claim_id` resolving to the published website proof. Existing news_item values lacked this link even though their evidence already included that proof. The producer now records the explicit ID. In the offline replay, each of the 113 saved news claims gains this link only after checking that the referenced claim is available VERIFIED and its evidence is already attached; its normal value-dependent claim ID is recomputed. Titles, dates, item/source URLs and source evidence are unchanged. No new fact or ownership inference is introduced. Mapping: `news-identity-links.json`.

## New wording

- Standing: one evidence-cited funding sentence per matched company, covering its research projects as **total project awards potentially shared with collaborators**, plus state aid grouped by its actual instrument type. No received/cash/exclusive-share wording. Amounts are not summed or allocated; no unsupported currency is added.
- Legal recipient, registered recipient subunit and any specified recipient subunit remain explicitly distinct. All cited funding IDs are available published claims with evidence.
- Changes: latest one to three news items with title, explicit date and **published by the company** attribution. Sitemap lastmod is a last-modification date; Atom updated is an update date. The three-part presentation brief also uses the same news wording and no longer says no dated news when news_item exists.
- Not established: no funding-gap/no-grants sentence added. Unmatched companies get no funding sentence. Existing not_established output is unchanged.

Every added sentence is explicitly passed through the existing `sentence_error` and generation raises on rejection. **validate.py, its sentence_error rule, verifier and existing tests are unchanged.** Funding standing is also checked through existing exact section recomputation. No new derived-count exception or permitted-word whitelist was introduced. Source guards and acceptance rules are not loosened.

## Offline measurement

Input: `bench/runs/news-items-20261120`; output: `bench/runs/funding-news-brief-final-20261120`. A Python audit hook rejects socket.connect and socket.getaddrinfo during the replay. It reads only saved claims/evidence references and regenerates synthesis: **zero HTTP requests**.

| Metric | Before | After |
|---|---:|---:|
| Seven-section synthesis sentences | **14,970** | **15,151** |
| Standing sentences | 1,000 | 1,103 |
| Changes sentences | 2,229 | 2,307 |
| Not-established sentences | 3,399 | 3,399 |
| Published claims | 167,975 | 167,975 |

**103 companies gained one funding sentence each**. **31 companies gained news sentences, 78 total** (at most three/company). The other five sections are unchanged. Totals count the seven sections, not duplicate three-part/analyst display sentences. `measurement.json` records section counts, offline guard, runtime and unchanged validator hash.

[Five funding and five news hand checks](REVIEW.md), with exact texts and full cited claims in `hand-review-10.json`. Funding examples cover research plus aid, grants, guarantees, tax benefits and the actual subunit-recipient case. News examples preserve the exact publisher's item title/date, including dated template posts, without independent-verification language. No source content was editorially upgraded.

## Validation

Full suite: **1,732 passed**, before **1,716** (+16 focused synthesis cases), in 396.72 seconds. One environment warning: pytest could not write its `.pytest_cache` node ID cache due to permission denied; the suite completed successfully. Tests cover total project amounts, actual instruments, recipient/subunit wording, no funding negative, three-news limit/date semantics, exact evidence citations and unchanged-validator rejection of altered dates/unavailable IDs. No existing test was weakened.

Final unchanged strict verifier: **PASS**, exit zero in 31.629 seconds; 1,000 envelopes, 167,975 claims, 5,882 source blobs, **zero unverified values**. See strict-verifier.txt and verifier-timing.json. Same integrity mode as earlier stages, without the extra optional-source-health --require-clean gate. It verifies the final replay with the original retained news state directory; no response bodies are rewritten or fetched. The prior rendering iteration also passed, but only final output verification is reported as the final result. The strict verifier's `synthesis_sentences` metric counts analyst/rendered primary sentences (2,570), unlike the seven-section totals above; the verifier also recomputes the extra standing/not_established sections and validates the three-part brief.

No full live collection or site build is needed for this offline synthesis change. No push. After successful checks, commit only this integration and report, then stop; no further stage.
