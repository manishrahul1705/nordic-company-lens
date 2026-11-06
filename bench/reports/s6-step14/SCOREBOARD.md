# S6 Step 14 - official registry announcements

KEEP:30 randomly selected distinct new events reviewed against exact official source records,30correct,0wrong-company. SearchOFF; no personal credentials; no push. Optional NAV homepage discovery was not changed.

## Official source and scope

Verified before implementation: the official Enhetsregisteret updates API is NLOD2.0, no registration. [Five-orgnr dates/types/changed fields, licence and robots result](SOURCE.md), [exact URLs and original responses](source-check.json). Robots retry disconnected; proceeded under the explicit user instruction, not a fabricated allow response. Allfive orgnrs returned usable explicit changes, so the most-empty stop condition did not apply.

Reused the existing registry-change batch collector. New supported fields are latest submitted annual accounts year, registered articles date, capital registration date and the two employee-information registration dates. Existing name/address/capital/subunit events remain supported. Unknown/bare updates and unsupported fields are skipped; no board event is invented. Date is registry publication time, explicitly not inferred effective date. No narrative announcement text is returned by this API.

Envelopes use registry_change.* and kind="Registry announcement"; raw profiles preserve the same distinct kind, separate from dated company-page items. Static fact panels say Registry announcement. Summary sentences describe the exact returned field and operation, never minor metadata as business news. Employee registration-date updates do not mean headcount changed; latest-accounts-year updates do not establish a different filing/effective date.

## Single frozen1000 measurement

| Section / metric | Step13 | Step14 |
|---|---:|---:|
| Identity |1000|1000|
| People |997|997|
| Subunit workplaces |774|774|
| Financials |999|999|
| Websites |105|105|
| Social companies |42|42|
| Jobs |3|3|
| News/activity companies |236|999|
| Company-published dated article claims |63|63|
| Companies with those article claims |7|7|
| Activity claims, total |659|2964|
| Registry-announcement claims |596|2901|
| HTTP total |6869|6819|
| Max HTTP per company |40|40|
| Mean attributed / amortized HTTP |6.830 /6.869|6.779 /6.819|
| Wall seconds |493.126|582.093|
| Deadlines |0|0|

Source29a30a5a2909ef5ada88cf6cd14d054f13cd925c, run20261106T142139712906Z-29a30a5. One completed1000 run, no replacement/parameter crawl. Frozen input hashes matchStep13. C:7.743GiB free immediately before launch, above3GiB. Recorded working_tree_dirty=true because audit/report/scratch files were untracked; production source was committed and unchanged during the run. No warnings;1000envelopes/profiles. [Execution](benchmark-execution.json), [metrics and labels](metrics.json), [disk](pre-benchmark-disk.json).

The increase is supported registry activity, not a claim of999 companies publishing business news. All63 company-published article URL claims remain. New semantic registry event/field keys:2370 across993 companies;2901total retainedregistry claims across999companies. Maximum10supported claims/company in24calendar months; future events rejected. The ten-claim bound may omit an older supported announcement when newer ones fill the limit. One announcement can support multiple explicit field claims; claim counts are not independent business-event counts.

Shared exact-orgnr entity/subunit feed acquisition used15HTTP requests, all200 (0.015per input), inside the2requests/input acquisition ceiling and original18000global/40company caps. Automatic endpoint retries are disabled to enforce actual request accounting. Subunit events retain current exact-parent registry evidence, never infer parent identity from an unrelated unit. IDs use eventID/field/op/value rather than array position; equivalent timestamps/reordered/duplicate changes are stable.

## Precision and refresh tests

[Thirty-event manual review](REVIEW.md), [raw events, claim spans, URLs, retrieval dates and hashes](review30.json). Sample uses deterministic seed20261106 over distinct new company/eventIDs. Every exact orgnr/date/operation/value matches the saved official record, including one field removal.0wrong-company. Fullsource hashes and verbatim evidence spans checked; no additional source scraping needed.

The original fixture had31October event time but18October retrieval. Corrected it to10October, retained the future-date validation, and added a separate future-rejection test. Focused77passed8.49s; fullsuite1107passed330.28s. Added coverage for24-month cutoff, unknown/oldregistration abstention, dedup/reorder-stable IDs,10claim cap and transient failed refresh retaining original claims/evidence as stale. [Focused log](focused-tests.txt), [full log](full-tests.txt).

Full1000 independent verifierPASS:1000schema-validlines,113379supportedclaims,4069sourceblobs,9192citedsentences,0unverifiedvalues. [Verifier](verification.txt).

Fresh clone of the exact runtime commit, frozen sync, literal README command twice with same state and unchanged strict verifier: [official-run result](official-run/RESULTS.md). Reused the recorded release100nonbench+3invalid cohort, not a newly claimed random selection. Source and evidence commits authored/committed as Manish Rahul <manishrahul1705@gmail.com>; final fullhash is in the response. Nothing pushed.
