# S6 Step 15 - verified website recall

**Precision KEEP; latest strict fresh-clone pair NOT PASSING (0 company / 2 observation changes, exit 1).**

**110 verified websites (+5),44 social-available companies (+2),0wrong-company additions.** SearchOFF, application credentials stripped, no push. Existing ownership/publisher/group/parking vetoes and social handle matching remain unchanged. No company-specific exceptions.

## Pre-code funnel and veto review

[Saved Step14 funnel](FUNNEL.md), [per-company ledger](funnel-company-ledger.json). Initially reported: no candidate184,DNS381,fetch45,robots21,fetched/no-proof103,veto160,budget1. Final audit reconciliation moves four explicit group-site final vetoes from proof-loss to veto: **99no-proof/164veto**, other buckets unchanged. No-candidate+no-proof is283, above the60stop threshold; it was287before correction. [All four corrections](funnel-final-guard-correction.json). This correction does not change runtime rules or the measurement.

The separately requested original160-company veto subset remains preserved:53parked/for-sale,52different publisher,46shared/group,9other,0foreign.com-only primary vetoes. [Full breakdown and20-case manual review](VETO_REVIEW.md): parked10/10correct;publisher9/10correct reasons plus one webshop-supplier-credit misclassification (Motorsyklisten). That case still lacks exact-company proof and has mismatching registry phone/location. Neither category reaches3wrong/10; no narrower veto or company exception was proposed/applied. Foreign.com0 is only this subset, not an assertion about every final group guard.

## Final single frozen1000 run

| Section / metric | Step14 | Step15 |
|---|---:|---:|
| Identity |1000|1000|
| People |997|997|
| Subunit workplaces |774|774|
| Financials |999|999|
| Verified websites |105|110|
| Social-available companies |42|44|
| Social URLs |67|72|
| Jobs |3|3|
| News/activity companies |999|999|
| Activity claims |2964|2965|
| HTTP total |6819|8666|
| Mean attributed HTTP/company |6.779|8.626|
| Mean amortized HTTP/company |6.819|8.666|
| Max HTTP/company |40|40|
| Wall seconds |582.093|1002.110|
| Deadlines |0|0|
| Warnings |0|0|

Run20261106T183808924157Z-1db7047, source **1db70477f679df3e03e29280897e314a43de6485**. Exactly one frozen1000 benchmark, no parameter/replacement crawl. Same input/registry SHA256 asStep14.1000envelopes/profiles emitted. C:6.418GiB immediately before launch, above requested5GiB. The working-tree-dirty flag reflects untracked audit/report/test scratch and later README edits; tested production source was committed and unchanged. [Execution](benchmark-execution.json), [full scoreboard](benchmark-scoreboard.json), [metrics](metrics.json).

Cost of measured recall:1847additionalHTTP requests (+27.1%) and420.017additional wall seconds (+72.2%), still within pooled18mean/40max and default2400seconds. This single combined run is not a causal component ablation; public-source variation remains possible. Existing end-of-run retry attempted49of50eligible companies/59candidates,175HTTP/167.422seconds,0recovered,0unexpected failures; these costs are already included above.

No previously published website is lost: [loss ledger](losses.json). Every one of105baseline sites remains, with the same published website values. No old proof/URL changes are disguised as new company gains.

## Levers and attribution

| Lever / source path | Candidates | Fetched | Accepted before final guard | Kept sites | New company sites |
|---|---:|---:|---:|---:|---:|
| B legal/subunit-name guesses |3877|342|52|51|4|
| E registry-email nominations (existing) |129|70|14|12|0|
| Existing registry/subunit/other nominations |296|79|53|47|1|
| C follow-up proof pages |not a separate domain pool|588pages|not additive|13sites use follow-up winning proof|2of the new B sites|
| D explicit hidden-owner identifier |not separately enumerated|checked locally in fetched bodies|0published proof type|0|0|

Counts include repeated nominations from the bounded end-of-run retry; accepted-before-guard can exceed final kept sites. C overlaps B/E/existing:13is the number of final websites whose winning proof is on a follow-up URL, not13new causal recoveries. The two new follow-up proofs are The Lab Retriever privacy policy and Ecofric terms. They also required the new .com nominations; component gains are not independently claimed. D showed no retained gain in this sample. E and header/footer/JSON-LD social extraction were already present and are regression-covered, not falsely presented as newly implemented discovery sources.

B now allows up to8name candidates, company forms removed, HOLDING removed only when at least2other words remain, Norwegian transliteration and joined/hyphen variants, .no before.com. Every guess is DNS-checked before HTTP; no DNS success is ownership proof. Stronger nominations still go first. D reads only explicitly labelled site-owner identifiers in named CMS JSON/script/footer context; arbitrary tracking values, customer arrays and another legal entity cannot establish ownership. All existing vetoes execute first and final guards still apply.

### Proof-page no-loss correction

The first reduced three-page trial displaced /about and caused a real regression. Restored the previous linked/common/sitemap selection and old ordering, then append at most2new same-host targets without displacing selected old pages. Existing stop-after-proof and pooled limits still apply. **test_about_page_norwegian_entity_support_survives_final_guard was not edited.** Strict replay was not weakened. Optional privacy probing after legacy pages expects https://zephyrsynthetic.no/personvern; added its honest synthetic HTTP404 response and generator entry, SHA-verified. Final focused75passed41.09s; final fullsuite **1124passed286.58s**. Earlier failed build logs remain historical and are not final validation. [Focused](proof-order-tests.txt), [final full suite](preserved-full-tests.txt).

## Complete new-item review

[All five websites and five social URLs with verdicts](REVIEW.md), [proof excerpts/registry values/SHA/URLs](new-items.json):10correct,0wrong,0unsure. No social destinations were fetched.

- ISTAD ART SOLUTION NORWAY NUF911691248: declared pederistad.no plus registered director/chair PederIstad; TierB link only, no content/social/news authorized.
- THE LAB RETRIEVER AS926065173: exact legal name plus1396Billingstad on privacy policy; source street typo is disclosed. Two exact-name footer social links.
- ELEKTROKOMPETANSE AS989916319: exact own orgnr on.com homepage. Some unfinished testimonial text is a source-quality limitation, not another entity or generic parked page.
- ECOFRIC AS924828099: terms/footer exact own orgnr and Norwegian AS. Three company-specific Organization/social links.
- TECTRAP AS920542158: exact own orgnr in.com footer. Its personal LinkedIn/in is not published as company social.

Vokser919653477 remains an explicit limitation: its saved footer link linkedin.com/company/vokser-group is discovered but fails unchanged exact legal/domain/declared-brand handle matching. Saved homepage identifies Vokser AS/Vokser, not Vokser Group. No per-company or suffix-based social relaxation was introduced merely to publish that example.

## Independent verification and fresh-clone pair

Full1000 verifierPASS:1000schema-validlines,113419publishedclaims,4081sourceblobs,9209citedsentences,0unverifiedvalues. [Verifier](verification.txt).

Fresh clone of exact sourcecommit, literal README command twice on the recorded release100nonbench+3invalid cohort, same state/no--previous, credentials stripped: [official-run result](official-run/RESULTS.md). The report records the unchanged strict pairwise exit code and actual company/observation changes. No alternative cohort or relaxed verifier is substituted. Final report commit/fullhash is in the response. Manish Rahul <manishrahul1705@gmail.com>; no push.


## Final speculative-candidate state correction (no new 1000 crawl)

Speculative legal-name/.com and registry-email candidate DNS/TLS/connection/timeout failures are recorded as candidate-not-reachable and do not fail the website section. Registry-declared, Wikidata and previously verified candidates remain strong sources: their unavailable checks still fail honestly. Existing proof, group/publisher vetoes and budgets remain unchanged. Unwrapped SSL transport errors are normalized rather than escaping as section exceptions.

Saved evidence for the **22 newly failed companies** projects to **22 not_available / 0 failed**. No optional proof-page failure occurred in those records. This changes section-state interpretation, not website/social coverage; the sole 1000 measurement above remains source `1db7047`, and was not rerun. No claims, snapshots or historical benchmark outputs were rewritten. [Per-company projection and financial/website failure comparison](FAILURES.md), [machine ledger](speculative-state-projection.json).

The one financial failure is NRP ANAXO NORDIC M2 / 926077422: HTTP 500 on all three attempts in both Step 14 and Step 15, not a newly lost available financial section. Website failed counts measured 49 then 62, comprising 22 newly failed and 9 recovered.

Final correction validation: **107 focused tests passed in 17.13 seconds; 1167 full-suite tests passed in 277.46 seconds**. Regression matrix covers guessed .com/legal-name, registry/subunit email, registry/subunit declared website, Wikidata and previous verified candidates across DNS/NXDOMAIN/TLS/connect/timeout, plus an unwrapped SSL error. Three superseded expectations were updated to the requested candidate-scope policy; no proof/veto assertions were weakened. Source commit `5506e98c6e8a6ce98eebbae09e832d0a58dd2b3b`. [Full-suite log](speculative-full-tests.txt).

Fresh-clone final-source results: 103 outputs each;204.515s/755HTTP then203.141s/742HTTP;0companychanges,1website observation (993350990, blocked->not_available, HTTP429->404). Strictpair exit1; not claimed as passing. Both standalone verifiers pass. No verifier relaxation or additional cohort was used. [Full result](official-run/RESULTS.md).


## Speculative access-refusal follow-up

Speculative legal-name/.com, email and NAV candidates now label robots/blocked/429 refusals as candidate-not-reachable (LOW), without section-level blocked errors. Strong registry-declared, Wikidata and previously verified sources retain blocked semantics. Ownership/publisher vetoes are unchanged. One parametrized regression covers both speculative and strong refusal cases. Focused **127 passed in 18.15 seconds**, full suite **1187 passed in 274.26 seconds**. [Focused log](blocked-focused-tests.txt), [full log](blocked-full-tests.txt).

Correction to the premise: **1975.no is registry-declared**, not speculative. Saved official-run claim `identity.registered_website` is `www.1975.no`; registered subunit 993367168 also nominates it. There is no company-specific reclassification. Its earlier 429->404 observation is preserved in the earlier pair report. The new fresh-clone candidate pair is recorded separately under [blocked follow-up](blocked-followup/RESULTS.md); the two pending files are copied into a fresh clone before the conditional final commit, with exact source hashes and patch retained.

Latest blocked-follow-up pair:103outputs each,205.922s/768HTTP then196.344s/743HTTP,0companychanges/2observations/strict exit1. 1975.no remains registry-declared; A1Living speculative Atom page200->403 changes ambiguous->not_available without blocking. The user subsequently accepted these two genuine external-response observations and authorized committing Step 15 as is, without reruns. [Full conditional-gate result](blocked-followup/RESULTS.md).

Final acceptance: 0 company changes; 2 observation changes caused by changing live responses: 1975.no HTTP429->404, website blocked->not_available; A1 LIVING speculative Atom page HTTP200->403, website ambiguous->not_available. Strict verifier exit1 remains honestly reported. User authorized commit as is; no reruns or push.
