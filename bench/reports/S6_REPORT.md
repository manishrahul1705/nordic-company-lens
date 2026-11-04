# S6 hard-stop report — 4 November 2026

Code checkpoint after reverting unbenchmarked Step 3b: `5a4301307f84a3d551bd818abbbd5a4c2d3fe93d`. Final wrap-up commit is identified by the repository HEAD and HANDOFF.md checkpoint note. No push.

Steps 1, 2 and 3a: KEEP. Step 3b (`2b97438`): reverted, **not completed (model capacity interruption)**. Step 4: not started. S7: not started. Search OFF; benchmark credentials stripped. No new benchmarks or feature work during wrap-up.

| Gate | Decision | Website/social/jobs/activity available | Wall s | HTTP | Website budget errors | NAV mode | NAV s / requests | Hiring incomplete |
|---|---|---|---:|---:|---:|---|---|---:|
| 1-100 | KEEP | 11/5/1/29 | 59.596 | 700 | 2 | declared_index | 4.516 / 4 | 0 |
| 1-1000 | KEEP | 72/33/3/231 | 316.499 | 6495 | 24 | declared_index | 34.453 / 6 | 0 |
| 2-100 | KEEP | 11/5/1/29 | 55.340 | 694 | 2 | declared_index | 4.500 / 4 | 0 |
| 2-stale1000 | KEEP | 71/32/2/231 | 346.998 | 7143 | 26 | full_feed_fallback | 272.438 / 663 | 69 |
| 2-1000 | KEEP | 72/33/3/231 | 249.476 | 6482 | 21 | declared_index | 29.203 / 6 | 0 |
| 3a-100 | KEEP | 11/5/1/29 | 56.959 | 751 | 6 | declared_index | 4.187 / 4 | 0 |
| 3a-1000 | KEEP | 75/34/3/231 | 273.237 | 7108 | 65 | declared_index | 28.750 / 7 | 0 |

Current results are the last measured Step 3a results, not a new post-revert benchmark. The revert restores Step 3a production behavior. 100 available (identity/people/locations/financials/website/social/jobs/activity): **100/100/85/100/11/5/1/29**. 1000: **1000/997/774/999/75/34/3/231**. Both exit 0, correct envelope counts, zero deadline hits and zero hiring-incomplete companies. Step 3a 1000 wall 273.237 s; NAV declared_index 28.750 s / 7 requests. Website budget errors rose from 21 to 65 at 1000: a measured unresolved cost of extra proof checks.

Fresh public-token NAV index: built 2026-11-04T07:16:54.150483Z, 8554 ads, 5500 employers, zero failed details, 396394 bytes; build 1303.454 s / 9262 requests. Valid for 21 days, through 25 Nov. Fresh-index hiring-incomplete improved from 73 to 0. Forced-stale fallback remains honest: 69 name-unusable companies incomplete, no unchecked candidate companies; 346.998 s wall (<1200 s), NAV 272.438 s / 663 requests. Header-name matching remains a limitation, not solved by increasing detail capacity.

## Open Step 4 issue: plaintext HTTP

NSNL, org 952785052: Step 3a review found `http://www.nsnl.no` published by the legacy plaintext fallback. Company attribution passed; transport evidence does not meet the valid-TLS requirement. No fix has been made. Step 4 must try www/apex with TLS verification, allow only one HTTP redirect probe to a valid HTTPS destination, and never publish plaintext evidence. Keep robots, owner-conflict, scope and exact-company checks.

## Review evidence

All gate source reviews are copied under `bench/reports/s6-evidence/`, together with measured scoreboards. Step 3a reviewed all 54 social claims and five changed website proofs, zero wrong-company items; no section available count dropped. These are attribution findings, not a claim that NSNL transport is secure. Gates and raw NAV/build validation are also preserved. The 30-company sample and suffix screen are copied alongside this report. Suffix screen is offline evidence only, not a benchmark or a KEEP result.

## Historical progress notes

The following notes record intermediate states and pending work at the time written. The hard-stop status above supersedes all earlier pending/trial statements.

# S6 progress report

Fresh NAV build continues using public token, no disk seeds. F17 diagnostic correction committed as 64d3c3c; 808 tests pass. Runtime changes pending. Search OFF.

## 30-company retained-body classification

Seed 20261104. After correcting F17, retain 21 original sample companies with complete successful company bodies and replace nine missing/truncated-body cases using the same seed from the remaining corrected bucket. The original table remains in proof-sample-original.json. Corrected bucket: 102 companies; new no-retained-page bucket: 53. No image/PDF-only identifier is asserted without inspecting it.

| Org | Company | Classification | Saved evidence finding |
|---|---|---|---|
| 932763559 | FOLVENGAARD AQUA AS | different/renamed company or shell | Site says Medcis AS; no target legal name or orgnr. |
| 989986414 | GOLLAN AS | parked domain | Above.com parking/sale terms; no company proof. |
| 993484407 | DRØBAK MONTESSORI UNGDOMSSKOLE AS | legal suffix absent | School branding/contact match but full legal name with AS absent; name-only must not authorize. |
| 923998012 | ASKØY24 AS | unfetched ownership page | News publisher homepage has no legal entity proof; inspect contact/about/terms within capped followups. |
| 995541432 | WACKER CHEMICALS NORWAY AS | parent group | Wacker Chemie AG global site; Norway legal entity not proved. |
| 822291082 | FAMSA ESTATE CO AS | placeholder | Both domains only say Her kommer; no identity. |
| 950220317 | INFLOW MEDIA NORWAY AS | different/renamed brand | Simply.TV lacks the target full legal name/orgnr on fetched pages. |
| 934244443 | KLET AS | different company | Czech mountain accommodation; +420 address, not Norwegian Klet AS. |
| 989665537 | EKÅS EIENDOM AS | different company | Aktiv Bemanning contact shows 993114006, not target 989665537. |
| 915118305 | HEIANE LEGESENTER AS | legal suffix absent | Heiane Legesenter has matching location but lacks AS and exact orgnr. |
| 922828172 | TENSIO AS | unfetched ownership page | Tensio customer pages lack AS/orgnr; privacy/company imprint page may provide exact proof. |
| 825986332 | GEIRTECH AS | empty/script shell | Saved bodies lack visible legal identity. |
| 930219665 | LIZZI AS | different company | Italian heating/air-conditioning service, not target Norwegian AS. |
| 935073359 | NEUPHAI AS | legal suffix absent | NeuPhai brand only on home/contact; exact AS/orgnr not established. |
| 931613294 | MAN WITH A PLAN AS | empty/script shell | No visible legal identity in saved home/followups. |
| 990033897 | RELASJONSSENTERET AS | different/renamed brand | EQ Institute pages lack target legal entity; shared email insufficient. |
| 939725709 | SAGA REGNSKAP OG RÅDGIVNING AS | proof excluded by page structure | Exact 939725709 exists in visible contact page but excluded from owner_text; needs carefully scoped contact-owner proof, not arbitrary page text. |
| 988944645 | JØRN PERSSON AS | empty/script shell | Saved homepage has no visible identity. |
| 988236756 | BYGGTEMA AS | different company and punctuation | Norwegian Bygg-Tema name differs in punctuation; Swedish .com is BYGGTEMA AB with Swedish number. Do not accept Swedish site. |
| 977107385 | INDRE SALTEN OPPLÆRINGSKONTOR AS | legal suffix/name incomplete | ISOK AS and full name without AS on contact page; registered full legal name with suffix not established. |
| 996744744 | NORCON NORWAY AS | parent group | Redirected Jacobs page is discontinued global-brand content, not Norway entity proof. |
| 981058771 | STORHAMARSENTERET AS | legal suffix absent and text soft hyphens | Site name lacks AS; contact values contain soft hyphens. Owner page mentions Credo Gruppen; strict two-contact/domain trial needed, not name-only. |
| 911691248 | ISTAD ART SOLUTION NORWAY NUF | personal brand/registered entity unproved | Peder Istad artwork/contact page in Sweden lacks full NUF identity and target orgnr. |
| 930832707 | DOGLEG AS | legal suffix absent | Dogleg brand plus physical street/postcode and email on own domain; candidate for separately authorized two-contact trial. |
| 812753932 | TIME 2 TRADE AS | empty/script shell | Retained home and followup bodies have no visible identity. |
| 931863509 | SK BYGG & BETONG AS | name punctuation differs | S.K Bygg & Betong AS versus SK BYGG & BETONG AS; punctuation normalization alone cannot remove requirement for registry contacts or exact number. |
| 990342555 | NORDSTRAND KULTURSKOLE AS | legal suffix absent | Nordstrand Kulturskole brand plus email and phone on own domain; candidate for strict two-contact trial. |
| 995748983 | MAAEMO AS | legal suffix absent | Maaemo brand and contact address/email; verify against registry and domain before any suffix-absent acceptance. |
| 992174676 | DEIGEN HOLDING AS | different brand/holding entity unproved | Credor branded service lacks DEIGEN HOLDING AS identity; same contact cannot prove holding ownership. |
| 919280204 | NESFJELLET PROSJEKTUTVIKLING AS | different group entity | Privacy text explicitly names Nesfjellet Alpin AS, not Nesfjellet Prosjektutvikling AS. |

## TLS/connect classification from saved request logs

153 companies: 102 connect/TLS errors whose low-level cause was not retained, 43 timeouts and eight DNS/transient cases without a typed transport event. A ConnectError is not proof of a certificate hostname mismatch. Exact candidates and recorded events are in tls-classification.json; live diagnostics will distinguish mismatch/HTTP-only/timeout before a Step 4 claim.

## Separately authorized suffix-absent trial

Suffix-stripped legal name + at least two independent registry contact categories + name-derived registrable label + no foreign owner identifier. One signal stays ambiguous. Own commit, 100/1000 benches and full new-item review; no implementation/KEEP yet.

## Step 1 build progress

The optional NAV key file was absent. Public-token builder started with a new checkpoint and --no-seed-from-disk; it scanned the complete feed, discovering 8,898 active headers. Detail refresh is still running (more than 6,700 complete at last progress check). Current bundle has not been replaced. No Step 1 KEEP decision or live bench yet.

Saved-body suffix screen (not a live trial): 22 page records across 11 companies meet the proposed name/domain/two-contact filters. Full registry contexts, source hashes and proof excerpts are in suffix-screen.json. This is not a measured coverage increase or a KEEP decision.

Step 1 build completed and validated: 8554 ads, 5500 employers, 0 failed details, 396394 bytes, 1303.454s, 9262 requests, public token. Fresh timestamp 2026-11-04T07:16:54.150483Z; expires 25 Nov. Bundled index replaced; tests and public-token benches pending.

Post-build full suite: 808 passed in 151.12s. Step 1 first benchmark running at bench/runs/20261104T073725872378Z-52818c4 (100, credential-stripped public token).

## Step 1 KEEP

Post-rebuild 808 tests pass. 100: declared_index, NAV4.516s/4 requests, 59.596s wall, 0 hiring incomplete. 1000: declared_index, NAV34.453s/6 requests, 316.499s wall, 0 hiring incomplete versus73. Available100 website/social/jobs/activity 11/5/1/29; available1000 72/33/3/231. No section drops; full review of52 social,3 exact-employer/subunit jobs and2 changed sites,0 wrong. Bench folders 20261104T073725872378Z-52818c4 and 20261104T073852917844Z-52818c4.

## Step 2 trial

4407516 changes fallback default detail admission to remaining time/observed service/request capacity; explicit cap preserved. Same-version in-flight UUID guard avoids duplicate work. Page-cap exceedance records unread next URL and remains incomplete.22 focused NAV tests pass; full suite and benches pending. Forced stale bench uses the original October14 artifact saved in ignored bench/cache; bundled fresh artifact is not re-dated.

Step2 full suite:811 passed. Normal100 55.340s, unchanged11/5/1/29 website/social/jobs/activity; source review passes. Forced-stale1000 running at 20261104T075124281242Z-4407516 using original October14 index override. Normal1000 remains pending.

## Step 2 KEEP

811 tests. Normal100:55.340s, unchanged counts. Normal1000:249.476s,72/33/3/231 website/social/jobs/activity,0 hiring incomplete; NAV declared_index29.203s/6requests. Forced-stale1000:346.998s (<1200),full_feed_fallback/index_stale,NAV272.438s/663requests;299detail attempts,0unchecked candidate companies/failed ads/cap hits;69name-unusable companies honestly remain incomplete (73 before). No available-count drops versus corresponding baselines; full source reviews pass. All measured gates recorded in gates.json.

## Step 3a trial

f1c5986: CMS type-page article contact evidence bounded to own Hovedkontor section with full legal name + labelled exact orgnr; excludes news/customer mentions and foreign owner identifiers. Actual Saga saved contact body now verifies. At most3extra imprint/privacy proof requests, only while not yet verified, within14/18caps. Street abbreviation normalization preserves exact house numbers. Full suite running; benchmarks pending.

## Step3a KEEP

823 tests.100:56.959s,11/5/1/29 website/social/jobs/activity; website budget count6.1000:273.237s,75/34/3/231 vs72/33/3/231. No section drops; all54social and5changed site proofs reviewed,0wrong. Saga full legal name and939725709 in bounded Hovedkontor section, Balder seller914283116, Eimealt controller912667758,7ocean Holding exact legal name+registered street. Independent source checks pass. Website budget errors21to65 is a measured cost. Legacy NSNL plaintext fallback remains tracked for Step4.

## Step3b trial

2b97438 suffix-free legal name requires at least2distinct registry contact categories and name-derived registrable label; no conflicting owner numbers. One contact stays ambiguous. New proof method retains registry evidence. Compact NO-number-MVA parsed for owner conflicts.30focused tests pass; full suite and100/1000gates pending.

## Implementation and revert history before documentation wrap-up

```text
5a43013 Manish Rahul <manishrahul1705@gmail.com> Revert "Trial suffix-free legal names with two contacts and name-derived domains"
2b97438 Manish Rahul <manishrahul1705@gmail.com> Trial suffix-free legal names with two contacts and name-derived domains
4d80529 Manish Rahul <manishrahul1705@gmail.com> Record contact-proof trial benchmarks and complete source review
1abf474 Manish Rahul <manishrahul1705@gmail.com> Recognize bounded own-company contact sections and extend proof-page checks
8d8b1b2 Manish Rahul <manishrahul1705@gmail.com> Record fallback robustness benchmarks and honest name limitations
4407516 Manish Rahul <manishrahul1705@gmail.com> Size fallback NAV detail work from remaining time and report unread feed pages
8d9d3d6 Manish Rahul <manishrahul1705@gmail.com> Record fresh NAV index benchmarks and complete hiring coverage
52818c4 Manish Rahul <manishrahul1705@gmail.com> Rebuild official NAV index from fresh public feed details
64d3c3c Manish Rahul <manishrahul1705@gmail.com> Require retained successful company pages in F17 loss diagnosis
4b75753 Manish Rahul <manishrahul1705@gmail.com> Record final S5 scale validation and NAV freshness diagnosis
c0da0a1 Manish Rahul <manishrahul1705@gmail.com> Record malformed-social safeguard benchmark and source review
098dc33 Manish Rahul <manishrahul1705@gmail.com> Ignore malformed social metadata without failing verified websites
```

Final hard-stop validation after reverting Step 3b: `uv run pytest -q` ? **823 passed in 192.93s**, exit 0. No new benchmark was run during wrap-up. Production code, scripts and tests match the kept Step 3a checkpoint (`4d80529`).
