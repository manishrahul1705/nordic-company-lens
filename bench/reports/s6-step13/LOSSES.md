# Website/social losses versus the saved baseline

The baseline is the reviewed Step 12 **saved-evidence projection**, not a fresh current-code baseline crawl. Two website companies and two social URLs from one company are absent. Neither loss is traced to DNS or timeout; no transient-noise exemption is claimed.

| Company / orgnr | Prior item | Current finding | Classification |
|---|---|---|---|
| ISTAD ART SOLUTION NORWAY NUF / 911691248 | https://www.pederistad.no | Homepage and contact pages fetched HTTP 200. The collector found a link-only registered-role proof; the unchanged final entity-scope guard withheld it as ambiguous because the full role-holder name did not survive its owner-text support check. | Proof/guard withholding; not DNS/timeout |
| SNAPPY AS / 929481070 | https://snappy.no | Root, Contact_Us and About returned HTTP 200. The captured pages did not pass the current corroboration rule. Christoffer Beddari Kristiansen appears as MEDL in the current registry, while the website proof helper uses director/chair names. The saved earlier unique-name proof is not a fresh current-code proof. | Insufficient current proof; not DNS/timeout |
| SNAPPY AS / 929481070 | https://twitter.com/snappy_as | Withheld with the unverified website. | Consequence of proof loss |
| SNAPPY AS / 929481070 | https://www.instagram.com/snappy_as | Withheld with the unverified website. | Consequence of proof loss |

Istad's historical Step 11 proof blob was already missing at Step 12 cleanup; it was preserved as an explicitly un-revalidated baseline row. Current captured pages are available and were evaluated normally. No missing body was recreated, substituted or fetched for the baseline.

The speculative `snappysoftware.com` site is Snappy Fax Software and did not pass exact-company/contact proof; it was not published. Other Snappy brand spelling candidates produced NXDOMAIN/no_such_domain. Those failures are not the cause of losing the previously accepted **snappy.no**, which was successfully fetched.

Net website -2 / social-available-company -1 is numerically within the old Step 6 bands of 2 / 4, but these proof losses are **not** excused as transient. This run demonstrates no breadth gain from A or B; it does not establish a causal count loss from those changes, because the baseline is an older saved projection. Precision review of every addition remains the Step 13 gate.

[Complete website diagnostics](losses.json), [social URLs and diagnostics](social-losses.json). The run's second-pass detail ledger is in [funnel.json](funnel.json); it records 34 eligible companies, 33 attempted, 35 selected candidates, one fetched candidate and zero recoveries.
