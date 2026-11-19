"""Assemble final Stage AG findings from immutable run artifacts."""
import json
from pathlib import Path

out=Path(__file__).parent
before=json.loads((out/'before.json').read_text(encoding='utf-8'))
after=json.loads((out/'after.json').read_text(encoding='utf-8'))
requests=json.loads((out/'request-comparison.json').read_text(encoding='utf-8'))
audit=json.loads((out/'audit.json').read_text(encoding='utf-8'))
timing=json.loads((out/'verifier-timing.json').read_text(encoding='utf-8'))
measurement=json.loads(Path('bench/runs/stage-ag-20261119/measurement.json').read_text(encoding='utf-8'))
assert audit['passed'] and timing['exit_code']==0
names={'P1448':'Official name','P571':'Inception','P159':'Headquarters location','P452':'Industry',
       'P1128':'Employees with point in time','P2139':'Revenue with point in time','P856':'Official website assertion',
       'P2002':'X','P2003':'Instagram','P2013':'Facebook','P4264':'LinkedIn'}
notes={'P1448':'Agrees with registry after case normalization','P571':'Six conflicting dates withheld',
       'P159':'Explicit headquarters; never inferred from contact address','P452':'Separate from existing NACE classification',
       'P1128':'Dated observations; current registry counts unchanged','P2139':'No matching source statements',
       'P856':'One conflict withheld; does not establish website ownership',
       'P2002':'Existing profile now revision-bound','P2003':'One existing website profile gains Wikidata support',
       'P2013':'One existing website profile gains support; shared TENSIO profile withheld',
       'P4264':'No matching source statements'}
table=[]
for p,name in names.items():
    b,a=before['properties'][p],after['properties'][p]
    table.append(f"| {p} {name} | {b['companies']} / {b['claims']} | {a['companies']} / {a['claims']} | {a['source_companies']} / {a['source_values']} | {notes[p]} |")
conflicts=[]
for c in after['disagreements']:
    conflicts.append('| '+c['company']+' ('+c['organisation_number']+') | '+c['property']+' | `'+json.dumps(c['registry_value'],ensure_ascii=False)+'` | `'+json.dumps(c['wikidata_value'],ensure_ascii=False)+'` |')
f=requests['finalisation']
overhead=measurement['wall_seconds']-f['crawl_seconds']-f['outputs_seconds']-f['site_seconds']
text=f'''# Stage AG: revision-bound Wikidata extraction

19 November 2026. Branch `audit-fixes`; Stage AG is local and uncommitted. Nothing pushed. Before is the retained fresh-state Stage AF run (`bench/runs/stage-af-final-20261119`); after is a fresh-state default CLI run (`bench/runs/stage-ag-20261119`), with the same frozen input and site ON.

## Before and after publication

Counts below are **companies / available published claims with Wikidata evidence**, measured from final envelopes. They are not cached-index counters. A profile already published from a company website can gain a Wikidata citation without creating another profile claim. Before contained three Wikidata social claims, not zero: the run-local index had been saved before publication, so its social counter was not the final result. Those old citations did not include an item revision; the new ones do.

| Property | Before companies / claims | After companies / claims | Source-present companies / distinct values after | Disposition |
|---|---:|---:|---:|---|
{chr(10).join(table)}

The result contains **52 distinct Wikidata-supported published claims**: **47 new factual claims**, the three existing Wikidata social profiles now carrying exact-query/revision proof, and two existing website-discovered profiles gaining an additional Wikidata citation. There are **no additional social profile URLs** in the final output. Language-label rows do not multiply claims. Thirteen companies have matching Wikidata items, versus nine yielding the old website/social-only query results.

An independent cross-run comparison found no added/removed social-profile URLs and no changes to the matched companies' primary registry name, founding date, employees, registered website or revenue: [primary-and-social-comparison.json](primary-and-social-comparison.json).

P2139 and P4264 are implemented but have no source statements in this frozen cohort. No revenue or LinkedIn claim was fabricated to fill the table. Quantity/currency/qualifier and LinkedIn routing paths remain covered by synthetic tests and the normal social policy.

## Which information types were previously zero?

**Explicit structured headquarters claims were the only type at zero in the requested list: 0 companies / 0 claims before, 13 / 13 after.** A registered business/contact address was not re-labelled as headquarters; unstructured website descriptions are not counted as structured headquarters properties.

Other types already existed from other sources: legal names for 1,000 companies; founding dates for 988; NACE industries for 996; published current employee counts for 122; current revenue for 790; ownership-verified websites for 114; X profiles for two, Instagram for 29, Facebook for 34 and LinkedIn for 16. Their Wikidata-specific coverage can start at zero without the information type being absent overall. Wikidata industry classes are additional explicit categories, not inferred NACE mappings. Full before/after inventories: [before.json](before.json), [after.json](after.json).

## HTTP cost and runtime

The premise that the old code sends one SPARQL query per company is incorrect: it already batches **200 numbers per request**. Stage AG keeps those same **five requests for 1,000 companies**. It widens the result to include property statements, labels, units, qualifiers, precision/calendar and `schema:version` item revisions. There are **no individual entity/revision/label calls and no social-platform requests**.

| Metric | Before | After |
|---|---:|---:|
| Total HTTP attempts, frozen 1,000 | 11,345 | **11,254** |
| Wikidata HTTP attempts | 5 | **5** |
| Added website nomination URLs | — | **0** |
| Distinct website nominations | 9 | **9, identical sets** |
| Maximum attributed requests/company | 40 | **40** |
| Complete CLI wall seconds, including site | 1,337.059 | **{measurement['wall_seconds']:,.3f}** |

**The feature's additional HTTP cost is zero.** Facts are published after network collection has ended; they cannot seed more crawls in that run. The observed total decreased by 91, but this is not a claimed AG optimization: TED notice-host requests changed from 82 to 15 (67 fewer); other live-source differences account for the remaining net 24. [Request comparison and all changed hosts](request-comparison.json). The preflight also found identical nominations, independently of the final run: [probe-summary.json](probe-summary.json).

After timing: collection **{f['crawl_seconds']:,.2f}s**, finalization/synthesis/output validation and writing **{f['outputs_seconds']:,.2f}s**, offline site **{f['site_seconds']:,.2f}s**, other overhead **{overhead:,.3f}s**. Live sources and host activity were uncontrolled, so the wall-time difference is observational, not an isolated extraction-cost measurement. The independent verifier ran afterwards, outside CLI wall time.

All 1,000 terminal envelopes and all 1,000 company pages were emitted. The site contains {requests['site']['pages']:,} pages. `deadline_hits=0`; handled/unhandled exceptions 0; warnings none. The existing pool, 40/company cap, 3,600-second local safeguard, pacing, timeout and body limits are unchanged. Source hashes were unchanged during measurement. Linear 1,100-company wall projection is **{measurement['projection_1100_seconds']:,.3f}s**, below the earlier 3,000-second stop threshold.

## Proof, ranking and precedence

- The query requires the item to carry the exact company number through `?item wdt:P2333 ?org`; name matching never establishes the Wikidata item identity. Existing best-rank/truthy selection is preserved. Requested statements are emitted in separate rows rather than a cross-product of optional company facts.
- Every published Wikidata fact or supporting social citation is rechecked against its immutable stored result row, orgnr, item, value and numeric revision. Evidence contains the **exact SPARQL request URI**, response SHA-256, JSON row pointer, verbatim bounded excerpt and pinned item-revision URL. The same conditions are enforced after refresh carry-forward; legacy unversioned Wikidata-only proof cannot bypass them.
- P1128/P2139 observations require P585 metadata, retain its precision/calendar and quantity units, and never invent a current date, scale or exchange conversion. Decimal amounts retain their lexical precision. P571 year precision remains a year, not an invented 1 January founding date.
- Facts occupy separately attributed `identity.wikidata.*` or `accounts.wikidata.*` fields. Registry legal name, founding date, current headcount, registered website and financial fields remain primary. P159 is not equated with a contact address; P452 is not silently compared with NACE codes. Those concepts are not automatically disagreements.
- P856 is an attributed Wikidata assertion and nomination, **not website ownership proof**. It cannot create an ownership-VERIFIED website claim. All nine nominations are the same as before.
- Social identifiers use the **same existing handle/subunit-name or verified-site-link attribution**, followed by unchanged shared-profile and entity-scope vetoes. Existing matching profiles gain evidence without a duplicate or changed fact ID. TENSIO's `tensionett` Facebook candidate is not published after the shared-profile veto.

## Registry disagreements

Seven comparable values were withheld; the registry values stayed published. Both source evidence links, proposed Wikidata value, item and revision are recorded in `run.refresh.wikidata.disagreements`, reproduced in [after.json](after.json).

| Company | Property | Published registry value | Withheld Wikidata value |
|---|---|---|---|
{chr(10).join(conflicts)}

Five differing employee counts have different or unknown registry observation dates. They are recorded in `comparisons`, not falsely declared same-date contradictions. Dated historical Wikidata observations remain separate from the current primary registry count. For example, EIDEFOSS's 18 in 2023 does not overwrite its current registry count. No dated quantity is published as an unqualified current value.

## Reviews and validation

[Ten hand reviews](REVIEW.md) cover ten distinct companies and seven properties: official name, day/year inception precision, municipality headquarters, industry, historical employees, website assertions and social attribution. Each includes company, full published value, raw row, exact saved SPARQL response, item revision and a case-specific explanation. [Machine-readable reviews](reviewed.json); [five request URLs/query texts and snapshots](sparql/requests.json). Data is Wikidata CC0. The empty-result batch URL is reconstructed from measured code/input/order; every cited nonempty result URI comes from the live response index.

The **unchanged `scripts/verify_output.py` passed**, exit 0, in **{timing['seconds']:,.3f}s**: **1,000 envelopes, 167,137 published claims, 5,166 source blobs, 2,557 synthesis sentences, zero unverified synthesis values**. [Verifier output](strict-verifier.txt), [exact command/timing](verifier-timing.json). As for the baseline, this is strict integrity verification without the optional `--require-clean` source-health gate.

The independent [raw-binding audit](audit.json) checked all **52 Wikidata-supported published claims**, all **seven disagreements**, the exact query scope, four used source hashes, revisions, values/qualifiers and social attribution. All checks passed. No primary field was overwritten or website ownership promoted from Wikidata. The social branch of `accuracy_audit.py` recognizes the new exact-query citation format with additional revision/identity checks; the handle attribution test itself is unchanged. No acceptance rule was loosened.

**Full suite: 1,592 passed in 487.37 seconds**. [Test log](pytest.txt). Focused extraction/proof/precedence/quantity/social/refresh checks passed before the full suite. Tests include an actual 1,000-number mock transport proving exactly five requests and no per-item fetches.

Reproduce using [run_frozen.py](run_frozen.py), then [inventory.py](inventory.py), [audit.py](audit.py), [verify.py](verify.py) and [write_review.py](write_review.py). The frozen input SHA-256 is `7ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782`. No bulk input, previous state, personal credential, model call or new host was used. No push was performed.
'''
(out/'RESULTS.md').write_text(text,encoding='utf-8')
print(out/'RESULTS.md')
