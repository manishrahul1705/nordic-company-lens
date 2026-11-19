import json
import re
from pathlib import Path

out=Path(__file__).parent
m=json.loads((out/'measurement.json').read_text(encoding='utf-8'))
a=json.loads((out/'audit.json').read_text(encoding='utf-8'))
v=json.loads((out/'verifier-timing.json').read_text(encoding='utf-8'))
old=json.loads((out/'older-profile-withheld.json').read_text(encoding='utf-8'))
build=json.loads(Path('data/social_company_names_build.json').read_text(encoding='utf-8'))
assert a['passed'] and v['exit_code']==0
tests=re.findall(r'\d+ passed[^\n]*',(out/'pytest.txt').read_text(encoding='utf-8'))[-1]
rows=[]
earlier=json.loads(Path('bench/reports/proven-site-socials-20261120/measurement.json').read_text(encoding='utf-8'))
for platform,label in [('facebook.com','Facebook'),('instagram.com','Instagram'),('linkedin.com','LinkedIn'),('x.com','X'),('youtube.com','YouTube'),('tiktok.com','TikTok')]:
    b=earlier['platforms'][platform];c=m['platforms'][platform]
    rows.append(f"| {label} | {b['after_companies']} / {b['after_claims']} | {c['after_companies']} / {c['after_claims']} |")
oldrows=[]
for r in old:
    match=r['matches'][0]
    oldrows.append(f"| {r['company']} ({r['organisation_number']}) | `{r['url']}` | {match['name']} ({match['organisation_number']}) |")
text=f'''# Full-universe social-name veto

20 November 2026. Branch `audit-fixes`. Implemented locally; nothing committed or pushed for this change. This report supersedes the earlier 46-addition result where the wider name veto changes an outcome.

## Changes among the 46 additions

**43 remain eligible; three profiles are withheld:**

- VALDRESMEIERIET AS (`996979660`): Facebook **and** Instagram `valdresost` match **VALDRES OST AS (`914992605`)**. The retained own-company registry claims establish no permitted subunit/parent/subsidiary relationship with that number. Similar branding and a proven website do not grant the exception.
- RENTHALL AS (`980362779`): Instagram `hallmakergroup` matches **HALLMAKER AS (`937920040`)** after stripping the trailing social qualifier `group`. Renthall’s own registry group lookup explicitly lists **RENTHALL AS and HALLMAKER AS with the same parent, ZURHAAR INDUSTRIES AS (`935243351`)**. That is a sibling relationship, outside the permitted exception.

The final replay contains exactly the other 43 reviewed additions, with unchanged values, source URLs, source hashes and quotes: [review-carryover.json](review-carryover.json). There are no new unreviewed additions. The original complete hand reviews remain available as [historical evidence](../proven-site-socials-20261120/REVIEW.md); their policy conclusions for these three profiles are superseded here. [All 46 universe decisions](46-profile-decisions.json).

## Named handles

| Company | Handle | Final decision | Full-universe check / exception |
|---|---|---|---|
| DANSEINFORMASJONEN STI, 971558415 | `scenehuset` — Facebook and Instagram | **Retain both** | No matching registered-company name in the pinned 411,160 snapshot. Existing proven-site, role-person, shared-profile and group checks still apply. No registry relationship is inferred from the brand. |
| RENTHALL AS, 980362779 | `hallmakergroup` — Instagram | **Withhold** | Matches HALLMAKER AS, 937920040. Own registry evidence shows both as children of 935243351; a sibling does not qualify. |
| RENTHALL AS, 980362779 | `RentHallGlobal` — X | **Retain** | Checking the qualifier-free key `renthall` matches the same company, 980362779; no other company match requires an exception. |
| VALDRESMEIERIET AS, 996979660 | `valdresost` — Facebook and Instagram | **Withhold both** | Matches VALDRES OST AS, 914992605; no qualifying registered relationship is established in the retained own-company records. |

The Scenehuset result means **no collision in this frozen corpus**, not a claim that no similarly named company exists in today’s registry or that platform ownership was independently checked. The check is not a live national-register search. [Six named-profile decisions and explicit own-registry nodes/pointers/hash](named-cases.json).

Renthall’s relevant source is its own [konsernstruktur lookup](https://data.brreg.no/enhetsregisteret/api/konsernstruktur/980362779), retained SHA-256 `c71aede1db50d3fbf27a01aa12e77500d8bd0215117a83dc8394f61e17ed3503`: Renthall at `/children/4/children/3` and Hallmaker at `/children/4/children/4` each explicitly report `parentOrganisasjonsnummer=935243351`. No relationship permission is derived from a company name or from a website footer.

## Four older profiles also withheld

The protection runs on **all candidate and carried-forward profile claims**, not only the new 46. Four profiles published before the social changes also fail the stronger check:

| Subject company | Withheld profile | Different company matched |
|---|---|---|
{chr(10).join(oldrows)}

No permitted relationship to those matched numbers is established by the retained own-company registry evidence. “Not established” is not a claim that the companies are unrelated in reality. [Full older-profile decisions](older-profile-withheld.json).

## Final frozen-cohort publication

These counts compare the earlier proven-site replay (133 profiles) with the **same pages, same 1,000 companies, stronger universe veto**:

| Platform | Before companies / claims | After companies / claims |
|---|---:|---:|
{chr(10).join(rows)}
| **Total profiles** | **133** | **126** |

Companies publishing social profiles change **65 → 62**. Relative to the original Stage AG baseline (49 companies / 87 claims), the new result is **62 companies / 126 claims**: **43 reviewed additions and four older withholdings**. Of the 31 companies receiving the earlier 46 additions, 30 retain at least one new profile. The 43 remaining additions are a strict subset of the already-reviewed 46.

## Implementation and scope

- Bundles **all 411,160 organisation-number/name pairs**, not a filtered sample or only the frozen cohort. The original archive SHA-256 and decompressed content SHA-256 are verified at build time; exact generated-index SHA-256 and row count are checked at runtime. Duplicate organisation numbers, missing/corrupt data and count/hash mismatches cannot silently disable protection. A missing/corrupt index withholds profiles.
- Case, Norwegian letters, punctuation/spacing and legal forms are normalized while preserving name order. Full normalized keys are compared. Trailing handle qualifiers `group`, `gruppen`, `global`, `norge`, `norway` are also checked. For example, `HallmakerGroup` checks both `hallmakergroup` and `hallmaker`. This is not fuzzy substring matching, and never proves ownership.
- The subject’s own organisation number is excluded from foreign-company collisions. **Every other matching number must have its own permitted registry relationship**; one allowed match cannot excuse another unrelated one.
- Exceptions come only from available own-company BRREG claims: a registered subunit number, explicit group parent number, or explicit subsidiary whose reported parent is this company. Each exception carries the supporting claim ID and official-registry evidence IDs. Wrong-subject URLs, website-only assertions, names, shared group roots, siblings and stale carried-forward relationships do not qualify. This conservatively uses the explicit relationships already published from the subject’s record; it does not infer additional kinship through names or branding.
- Role-person, designer/agency, personal LinkedIn, share/tracking/home, shared-profile and group-site vetoes remain effective. A relationship exception only resolves the name collision; it does not override another veto. The frozen replay exercised **no relationship exception among surviving profiles**; positive subunit/parent/subsidiary exceptions are explicitly covered by tests.
- The name index is a **withholding-only resource**. It never becomes evidence for a positive company fact or corporate relationship. [Index notice](../../../data/SOCIAL_COMPANY_NAMES_NOTICE.md), [build manifest](../../../data/social_company_names_build.json), [offline builder](../../../scripts/build_social_company_names.py).

## Cost and validation

The compressed name bundle is **{build['bytes']:,} bytes (4.75 MB)** and loaded once per process from local disk. **No runtime HTTP is added**. The same saved 302 accepted pages and 1,000 envelopes were reprocessed; acquisition remains **11,254 requests before and after**. This is an offline extraction/publication replay, not a fresh live crawl or site build. The previous live-run time is not remeasured or replaced by replay timing. Caps and the normal site-on CLI default remain unchanged.

An offline wheel build passed, and the wheel contains the runtime module, full hash-matched index, build manifest and provenance notice: [wheel-check.json](wheel-check.json). No build dependency or corpus was downloaded.

- **Full suite: {tests}.** [Test log](pytest.txt).
- Focused source/social/registry checks: **220 passed**. New tests cover all 411,160 pinned rows, the four named handle cases, positive exceptions for subunits/parents/subsidiaries, wrong-company evidence, stale/non-registry evidence, multiple colliding companies and missing-index fail-closed behavior. Synthetic tests whose example handles collide with real registered names now use an explicit own number or unmistakably synthetic brand; real-data collision tests retain the true identifiers.
- Independent audit checked **all 126 surviving profiles**, with no unresolved foreign-company match: [audit.json](audit.json). Production source hashes match the final replay snapshot. No unreviewed new profile was introduced.
- **Unchanged strict verifier PASS**, exit 0, in **{v['seconds']:,.3f}s**: **1,000 envelopes, 167,176 available claims, 5,166 source blobs, 2,557 synthesis sentences, zero unverified synthesis values**. [Verifier output](strict-verifier.txt), [command/timing](verifier-timing.json). It uses the original retained Stage AG blobs. As before, strict integrity verification does not invoke the optional `--require-clean` source-health gate.

Artifacts: `bench/runs/social-universe-veto-20261120/`. Reproduce with [replay.py](replay.py), [audit.py](audit.py), [verify.py](verify.py). Original pinned archive hash: `1c89710e5b01f8617e86d09fbdff4a52f2f8dbbba297e74f7164b5984f5a0384`. Index SHA-256: `{build['index_sha256']}`. No push performed.
'''
(out/'RESULTS.md').write_text(text,encoding='utf-8')
print(out/'RESULTS.md')
