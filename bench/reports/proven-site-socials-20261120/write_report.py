import json
import re
from pathlib import Path

out=Path(__file__).parent
m=json.loads((out/'measurement.json').read_text(encoding='utf-8'))
v=json.loads((out/'verifier-timing.json').read_text(encoding='utf-8'))
reviews=json.loads((out/'reviewed.json').read_text(encoding='utf-8'))
assert len(reviews)==m['new_profiles']==46 and v['exit_code']==0
testtext=(out/'pytest.txt').read_text(encoding='utf-8-sig')
match=re.findall(r'\d+ passed[^\n]*',testtext)
assert match,'Wait for the full suite to pass before publishing the report'
platforms={'facebook.com':'Facebook','instagram.com':'Instagram','linkedin.com':'LinkedIn',
           'x.com':'X / Twitter','youtube.com':'YouTube','tiktok.com':'TikTok'}
table=[]
for platform,label in platforms.items():
    p=m['platforms'][platform]
    table.append(f"| {label} | {p['before_companies']} | {p['after_companies']} | {p['before_claims']} | {p['after_claims']} | +{p['after_claims']-p['before_claims']} |")
text=f'''# Social profiles linked from proven company sites

20 November 2026. Branch `audit-fixes`; local changes, nothing pushed.

## Controlled frozen-1,000 measurement

Reprocessed the **same 1,000 Stage AG envelopes and the same 302 accepted website page URLs** retained in `bench/runs/stage-ag-20261119`. This isolates extraction/attribution from live-network changes. The original envelope file, report and response blobs were not rewritten. **Zero new HTTP requests**: acquisition remains **11,254 before and after**. No social platform, redirect destination, profile, metadata endpoint or extra company page was requested.

This is a saved-output extraction replay, **not a new live end-to-end benchmark**. Synthesis was regenerated for all 1,000 and the resulting envelope file was strictly verified. The offline site was not rebuilt; a normal future CLI run includes the new extraction and still builds the site by default. Replay time was {m['replay_seconds']:,.3f} seconds, alongside validation activity; it is not a replacement runtime-budget benchmark.

| Platform | Companies before | Companies after | Claims before | Claims after | New claims |
|---|---:|---:|---:|---:|---:|
{chr(10).join(table)}
| **Total profiles** | — | — | **87** | **133** | **+46** |

Companies publishing at least one social profile rise from **49 to 65**. All were among the existing 114 VERIFIED websites. The **46 additions span 31 companies**: sixteen gain their first profile, others gain additional platforms/profiles. **No prior published profile was removed**. Counts deduplicate normalized profile identities per company; Facebook numeric id is preserved, and X/Twitter aliases share an identity key. [Measured counts and source hashes](measurement.json).

## Implemented changes

1. Facebook `/p/<Name>-<digits>/` and `profile.php?id=<digits>` are profile forms. The numeric query id is retained; non-identity tracking parameters and trailing slashes normalize away. Personal LinkedIn paths, share/intent, platform-home and tracking URLs remain rejected. Facebook’s `tr` pixel path is explicitly refused.
2. Social links are extracted from repeated `og:see_also` metadata, direct page links, eligible own-Organization `sameAs` and Facebook page widgets. Versioned `/v12.0/plugins/page.php?href=…`, unversioned page/likebox widgets and `fb-page data-href` are handled. Metadata and widgets use exact retained source spans, without fetching them. Repeated metadata is processed without a last-tag-wins loss.
3. On a website already proven VERIFIED for the company, the eligible company-page link is the attribution evidence; legal-name handle equality is no longer required. Unproven sources and shared/path-scoped branches retain stricter attribution. Company role-person names, other cohort companies, designer/agency accounts, shared profiles and group sites remain vetoes. Editorial/hidden/share/credit contexts remain excluded; ordinary contact-page wrappers and global CMS settings are distinguished from those contexts.
4. Additional forms requested during implementation: LinkedIn `/showcase/` and `/school/` alongside `/company/`; YouTube `/channel/<id>` when linked on a proven company page; Instagram/TikTok trailing-slash and query variants; `mobile.twitter.com` and `www.x.com`. `linkedin.com/in/` remains rejected. Opaque YouTube IDs from Wikidata alone do not establish attribution.

The production collector supplies own registry role names to the extractor. The final cohort pass checks other legal companies’ names and all observed profile owners before publication. All requests/caps, ordinary website ownership proof, registry-first rules and BRREG group relationships remain unchanged.

## Why CONPLAN and TANGERIN were excluded

**CONPLAN `/kontakt`:** Squarespace puts `tweak-share-buttons-style-icon-only`, `tweak-share-buttons-icons-show`, etc. in the **body’s global configuration classes**. The prior parser searched ancestors’ class strings for `share[-_]?button` anywhere. That matched the global setting and marked every descendant—including the footer’s “Følg oss på Facebook” link—as excluded. It was not a share URL or another company’s profile. The new social-only scanner does not treat a body-level setting as a local share widget. CONPLAN’s page link now publishes. The same link is on the saved homepage, which supplies its first retained claim citation.

**TANGERIN `/contact/`:** WordPress wraps the ordinary contact page in `<article class="post-50 page type-page status-publish hentry">`. The previous parser marked every link under any article element as excluded. The new scanner recognizes ordinary type-page/contact wrappers; it still excludes editorial articles and actual share controls. The LinkedIn `/company/tangerin-as` link now publishes from the saved `/contact/` page. The malformed `/companytangerin-as` links elsewhere remain invalid.

No global HTML-parser behavior for descriptions, contacts or activity was changed; the correction is confined to social extraction.

## Required cases and retained vetoes

| Company / profile | Final result | Evidence/rule |
|---|---|---|
| Objectfront — `twitter.com/bjornkaupang` | **Rejected** | Matches Bjørn Kaupang in its own roles records |
| Stillasfordeg — `x.com/istiaqdesign` | **Rejected** | Unattributed designer handle; proven-site rule does not authorize template/designer accounts |
| Fusa Mekaniske Industri — `facebook.com/fusamek` | **Accepted** | Direct Facebook icon link on its proven homepage |
| Indre Salten Opplæringskontor — `facebook.com/IndreSaltenOK` | **Accepted** | Explicit Follow-on-Facebook link on its proven homepage |
| Scene Midt — `instagram.com/martehallem` | **Rejected** | Matches role-holder Marte Heie Hallem with middle name omitted |
| TB Maskin — `youtube.com/user/thomasbech8` | **Rejected** | Matches role-holder Thomas Bech with numeric suffix |

Review of the first replay exposed the final two person-account variants; the guard and regression tests were strengthened, and the measurement was rerun. The initial +48 is superseded by the final **+46**.

After local extraction, four further candidates were still withheld by the existing final **group-site veto**: SKOGLI’s Facebook account and SAGA’s Facebook, LinkedIn and Instagram accounts. [Final veto trace](final-vetoes.json). Shared-profile suppression and numeric-Facebook identity equivalence remain tested. Personal LinkedIn paths, tracking pixels and malformed/redirect URLs are tested as rejections. The new cohort-company veto does not require that the other company itself publish the profile.

## Every new profile reviewed

[REVIEW.md](REVIEW.md) lists **all 46 newly published profiles**, company, exact URL, cited page, source hash/locator, and case-specific reasons. [Machine-readable full evidence and verdicts](reviewed.json). Every source hash was recomputed; every bounded quote was checked verbatim; every profile was re-extracted from its saved company page; every role-person/cohort/shared/group veto was checked. Numeric profiles and opaque channels are accepted only as declarations from the already-proven company site. No live platform identity or current account availability was inferred.

The reviews explicitly describe brand/venue/group-named accounts such as Scenehuset, Valdresost and HallmakerGroup. Under the requested rule, the proven-site link establishes the company’s declaration. It does not establish exclusive legal ownership outside the frozen cohort; no platform was visited to assert that stronger claim.

Source blobs remain in the original Stage AG state directory; `verify.py` passes that exact directory. Source retrieval timestamps are retained from existing evidence where present; otherwise they are reconstructed from the recorded request start plus duration within the original run. No fetched content is invented or changed.

## Validation

- Full suite: **{match[-1]}**. [Complete test output](pytest.txt). Old tests that required legal-name handles even on proven company sites were updated for the user’s new rule; unproven/shared-branch and veto expectations remain.
- The broader focused social/website/Wikidata regression set passed **220 tests**, including all four requested real cases, middle-name/numeric-suffix person variants, new URL forms, widgets, repeated metadata, true share/credit/hidden/editorial contexts and the contact-wrapper fixes.
- **Unchanged strict verifier PASS**, exit 0, in **{v['seconds']:,.3f} seconds**: **1,000 envelopes, 167,183 published claims, 5,166 source blobs, 2,557 synthesis sentences, zero unverified synthesis values**. [Verifier output](strict-verifier.txt), [command/timing](verifier-timing.json). This is strict schema/membership/hash/evidence/synthesis verification, without the optional `--require-clean` source-health gate. The verifier and its acceptance rules were not changed.
- All new profiles passed the separate full review checks. The production source hashes are recorded in measurement.json; the replay uses the same frozen input SHA-256 `7ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782`.

Reproduce with [replay.py](replay.py), [review.py](review.py) and [verify.py](verify.py). Output: `bench/runs/proven-site-socials-20261120/envelopes.jsonl`. No push was performed.
'''
(out/'RESULTS.md').write_text(text,encoding='utf-8')
print(out/'RESULTS.md')
