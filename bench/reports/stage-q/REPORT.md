# Stage Q: identifier-matching sweep

## Scope and method

Add RA000473 (Enhetsregisteret) alongside RA000472 (Foretaksregisteret) only for the child's GLEIF match and the batched child lookup. Both authority identities were checked against official GLEIF in Stage P; see ../stage-p/ra472.json and ra473.json. Exact complete organisation number after whitespace normalization remains mandatory. No name matching, legal-status changes or parent acceptance changes. Stage P whitespace matching and shared-parent evidence deduplication are included in this branch.

The complete code inventory is identifier-code-inventory.json: national-identifier references with exact source lines and surrounding comparison code in 53 runtime/builder files. The table below classifies external ingress and downstream matching rather than treating already normalized internal identifiers as independent source parsers. No external national-ID family found by that search is omitted. Internal claim IDs, SHA hashes, LEIs, UUIDs, phones, postal codes, personal IDs and municipality codes are different namespaces and are not converted into org numbers.

## Audit: exact comparisons and accepted spellings

| Boundary | Exact code / normalization | Spaces | Punctuation | NO / MVA | Finding and action |
|---|---|---|---|---|---|
| GLEIF child (official_extra.py, gleif_extract/collect) | `gleif_orgnr(entity.get('registeredAs')) != org`; query requests unspaced and `XXX XXX XXX`; authority `not in GLEIF_AUTHORITIES` | Complete 9 digits or 3 groups separated by whitespace; no partial matches | Rejected | Rejected | P demonstrated 107 misses from spaced API records. P fixed this; Q adds exactly RA000473 (+3 expected). Prefix/substring/name matches remain rejected. |
| GLEIF parent optional national-ID annotation | `entity.get('registeredAt',{}).get('id')=='RA000472' and re.fullmatch(r'\d{9}',entity.get('registeredAs',''))` | Not normalized | Rejected | Rejected | Spaced or RA000473 parents omit the optional organisation_number annotation; LEI relationship claims are still accepted only through the unchanged active explicit start/end/type edge. This is a documented formatting limitation, deliberately untouched because the user requires no parent acceptance change. |
| TED XML CompanyID | `national=re.sub(r'^NO\s*|\s*MVA$','',national,flags=re.I).replace(' ','')` | ASCII spaces, plus whitespace adjacent to prefix/suffix | Inner punctuation retained, so it cannot equal org | Prefix/suffix removed, case-insensitive | Winners/buyers then compare complete `organisations.get(x,{}).get('orgnr')==org` AND country in `{'NOR','NO'}`. Amount ownership repeats complete-ID comparison in the linked tender. No prefix/substring match. Interior NBSP/tab or dotted digits would not normalize. No actual valid missed XML CompanyID was found in the retained material; source 202 failures are not matching evidence. No speculative change. |
| TED search nomination | search query constructed from the canonical input org numbers; returned notices remain candidates until XML role/ID checks | Canonical query only | No conversion | No conversion | Search hits never establish winner/buyer identity. The nomination path is distinct from publication. Unchanged. |
| Wikidata query/parse (web/wikidata.py) | `VALUES ?org { ... } ?item wdt:P2333 ?org`; `if org not in numbers ...:continue` | Not normalized | Rejected | Rejected | P2333's own mandatory format is `\d{9}` and its usage instruction says 9 digits only, no spaces. Exact lookup is correct for conforming values. Nonconforming data would be missed, but no proven valid formatted mismatch was found; unchanged. |
| NAV forward header (nav_cached.py, add_company_scope/inspect) | `employer_org=str(employer.get('orgnr') or '')`; `employer_org in subunits`, `if valid(employer_org)` then exact owners lookup | Not normalized | Rejected | Rejected | Header names nominate only; detail must prove exact employer. Saved detail values are canonical. Hypothetical spaced header would fail direct-ID routing; no observed source case justifies changing it. |
| NAV detail, cached/stream paths | `org=str((ad.get('employer') or {}).get('orgnr') or '').strip()`; `if not valid(org):return True`; `actual_emp not in parents: continue` in nav.section | Outer whitespace only | Rejected | Rejected | Canonical employer must equal input or a currently registered subunit. Three saved detail identifiers are canonical. No proven under-match. |
| NAV public page fallback | `_records`: `r'"orgnr"\s*:\s*"\d{9}"'`; `orgnr=str(employer.get('orgnr') or '').strip()` and `valid(orgnr)`; `org!=indexed['employer_orgnr'] or not any(org in state.scopes...):` | Outer only after parse; discovery requires contiguous digits | Rejected | Rejected | Exact known UUID, dates and employer scope remain required. No recorded formatting miss found; unchanged. |
| NAV bundled metadata/build | nav_index.validate: `not valid(ad['employer_orgnr'])`; `self.owners.get(ad['employer_orgnr'],set())` | Canonical serialized keys only | Rejected | Rejected | Shipped schema requires valid nine digits; metadata is nomination only. The builder exports canonical official detail values. No runtime broadening. |
| Subunit-parent map (sources/subunits.py) | `emp=normalize(str(employer_orgnr or ''))`, same for parent; `valid` before map insertion | All whitespace removed | Rejected | Rejected | Exact canonical map keys. Existing normalized map does not override current live subunit publication checks. |
| Common Crawl labelled extraction | cc_proto.numbers and build_cc_candidate_index.labelled: LABEL captures labelled `[0-9][ .\u00a0]*` groups and optional NO / MVA; `re.sub(r'[^0-9]','',capture)`; mod-11 validation before retaining | ASCII and NBSP accepted | Dots accepted; hyphens rejected | NO in labelled form; bare NO...MVA accepted | Complete captured 9-digit checksum-valid numbers; suffix/prefix are grammar, not fuzzy matching. No observed recoverable format missed; no rebuild or extraction change. |
| Common Crawl parent mapping / runtime lookup | `parents.get(number) or number`; `bundled('cc_orgnr_index.json.gz').get(str(context.get('orgnr') or ''),[])` | Canonical keys, no additional normalization | None | None | Observed ID is separately preserved; max-three domain nomination is never proof. Canonical keys already produced upstream. |
| Website visible/meta/raw owner IDs (web/proof.py.orgnrs) | NO wrapper replaced using anchored word boundaries; numeric token capture; `digits=re.sub(r'[^0-9]','',match.group())`; `valid(digits)`; own/allowed set equality and differences | ASCII/NBSP accepted | Dots accepted; hyphens rejected | Recognizes NO...MVA with or without spaces | Existing parser accepts normal Norwegian tax-number displays. Longer digit tokens and substring-number probes are rejected. Existing owner/foreign/group vetoes unchanged. See website-existing-format-probes.json. |
| Website structured identifiers | `json_ids |= orgnrs(normalized)` for vatID/taxID/identifier; explicit NO/MVA wrapper removal for string fields; dictionary `value` also parsed through orgnrs | Same parser | Same parser | Same parser | Structured organisation objects only; no name-only loosening. A hyphenated ID is an existing limitation, not a demonstrated missed proof in this audit; unchanged. |
| Website entity-scope, raw identity, names/round2 | `orgnrs(...)=={org}`, `orgnrs(...) - allowed`, sibling/parent checks; registry-unique candidates use `{str(r.get('organisasjonsnummer')) ...}!={org}` | Parsed site IDs normalize above; BRREG IDs exact | As above | As above | Existing proof/veto and unique-name nomination rules are unchanged. Raw scanner still masks layout attributes/CSS. |
| Website jobs/ATS | `identifiers |= orgnrs(str(value))` from hiringOrganization identifier/taxID/vatID; `identifiers - allowed` rejects conflicts; `identifiers & allowed` selects exact number | Same website parser | Same parser | Same parser | Verified linked-board chain remains alternative under existing rules; names do not turn a national-ID prefix into proof. NAV dedup keys `(employer_orgnr,title)` use internal canonical values. |
| BRREG main entity | `str(data.get('organisasjonsnummer')) != org` -> wrong_company | No formatting conversion | Rejected | Rejected | Saved official 9-digit JSON values conform; no under-match demonstrated. |
| BRREG roles | `(str(explicit_org) != org and linked_entity != BASE + org)` -> wrong_company | No formatting conversion | Rejected | Rejected | Exact explicit ID OR exact official entity link, not a substring. Related role entity IDs are retained as facts, not conflated with subject identity. |
| BRREG subunits | `str(item.get('overordnetEnhet'))!=org` -> wrong_company; unit `organisasjonsnummer` becomes canonical claim/map key | No formatting conversion | Rejected | Rejected | Saved parent fields all canonical. Publication requires current exact parent relationship. |
| BRREG accounts / fact_depth.accounts | `str(reported_org) != org` -> wrong_company; history `str(get(row,('virksomhet','organisasjonsnummer')))!=org:continue` | No formatting conversion | Rejected | Rejected | Same strict entity check on latest/history accounts. No formatted official source values found. |
| Registry changes | `event.get('organisasjonsnummer') != org`; `event['organisasjonsnummer'] not in numbers`; exact `owners[event['organisasjonsnummer']]`; subunit detail `item.get('organisasjonsnummer')==unit` and exact overordnetEnhet | No formatting conversion | Rejected | Rejected | Canonical official event stream; IDs and live parent link must agree. `company_orgnr` in constructed facts is internal, later compared exactly in synthesis. |
| BRREG bulk CSV / cached map | `org=values[org_index]`; membership/SQLite exact key lookup; no general punctuation stripping | Exact cached CSV keys | Rejected | Rejected | Official bulk uses canonical keys. External noncanonical CSV would not match. The 20-company clean-clone control established exact org/name pairs; no evidence of official bulk under-match. |
| Input adapter | `org=normalize(item.get('organisation_number') ... )`; `normalize` removes whitespace/BOM, then checksum validation | Yes | Rejected | Rejected | User input, not external source proof; unchanged. |
| Refresh, envelope I/O, output verifier, synthesis, reporting, site | keys/membership compare internal `organisation_number`, `company_orgnr`, claim subunit/employer keys exactly; national-ID boundary already checked upstream | No new conversion | No new conversion | No new conversion | Internal identity-preservation checks; do not repair an external identifier by fuzzy matching here. Display/export code does not establish external identity. |

### Evidence and limits

The actual saved-payload sweep read 4,031 distinct successful JSON response bodies from the Stage P frozen run. It found 22,173 BRREG organisasjonsnummer values, 844 overordnetEnhet values and 3 NAV orgnr values, all canonical nine-digit strings/numbers; **zero noncanonical examples**. See official-saved-format-audit.json. This does not prove every possible future source value is canonical.

[Wikidata P2333](https://www.wikidata.org/wiki/Property:P2333) explicitly requires nine digits with no spaces; the property JSON is retained as wikidata-property.json. The attempted NAV and BRREG schema endpoints returned 404 (schema-fetches.json); no unsupported schema claim is made. The existing parser tests and saved-source audit, rather than hypothetical input changes, are used to decide whether to edit anything.

No additional demonstrable under-match was found beyond Stage P's GLEIF whitespace and Stage Q's authorised second official authority. Unsupported hypothetical formats are listed plainly above. No website proof code, TED normalization, NAV normalization, Wikidata query, registry matching, Common Crawl extractor/index, parent acceptance or scoring changed.

## Fifteen-company source review

Selection seed 20261114: all three Q-only gains, plus 12 P whitespace gains (only three new matches exist for Q alone). Each was fetched individually from the official GLEIF LEI endpoint and the official BRREG company endpoint. Review compares the full normalized identifier, exact accepted authority, registry legal name against GLEIF legal name, and the returned LEI. Legal-name equality is a review cross-check only, never a production acceptance rule. All 15 names also match verbatim. Full source responses and per-item verdicts: review-live.json.

| Org number | Legal name (BRREG) | LEI | registeredAs verbatim | registeredAt | Verdict |
|---|---|---|---|---|---|
| 935327423 | EDSVIK INVEST AS | 648800DQI4N427CA5U74 | `935 327 423` | RA000473 | correct |
| 995541432 | WACKER CHEMICALS NORWAY AS | 529900F0Z0I9SECX4P10 | `995541432` | RA000473 | correct |
| 926970348 | ROTOR REAL 1 AS | 648800SCG49S6IXSYQ40 | `926 970 348` | RA000473 | correct |
| 836491742 | SJAND AS | 636700OBRG85Z2Z7JX55 | `836 491 742` | RA000472 | correct |
| 927616084 | METHØYEN AS | 636700XXYYOS5PKYM615 | `927 616 084` | RA000472 | correct |
| 912052680 | RAABAKK HOLDING AS | 636700OXGMZ21JSNHB18 | `912 052 680` | RA000472 | correct |
| 971173459 | LINDÅS NÆRSENTER AS | 549300F9KCHXM4OG2B67 | `971 173 459` | RA000472 | correct |
| 934609441 | SM-S INVEST AS | 636700SIJ6T39CM80F47 | `934 609 441` | RA000472 | correct |
| 989113437 | ØYVIND LIE INVEST AS | 549300Z2Q4PNJ9UV0Z77 | `989 113 437` | RA000472 | correct |
| 819952132 | ELBILFORMIDLING AS | 254900WI73VP6ZRAM023 | `819 952 132` | RA000472 | correct |
| 930380423 | MJÅTVEIT HOLDING AS | 636700TZB5TZGECE5475 | `930 380 423` | RA000472 | correct |
| 927661683 | LAU CAPITAL AS | 25490024RQ1KF4MCK503 | `927 661 683` | RA000472 | correct |
| 918270205 | GILJEHOLMEN AS | 254900XUQRFIPTZYQ539 | `918 270 205` | RA000472 | correct |
| 933762467 | BVK HOLDING AS | 6367003LXAVNH592A676 | `933 762 467` | RA000472 | correct |
| 998535611 | SKISTAD AS | 549300I14DH8PB3KGW90 | `998 535 611` | RA000472 | correct |

**15 correct, 0 wrong, 0 doubtful.** All returned GLEIF legal names agree with BRREG verbatim.

## Isolated authority effect

On identical saved official responses, accepting the second authority gives **139 -> 142 companies** and **695 -> 710 direct GLEIF claims**: precisely 3 companies and 15 claims, with no other matching change. The added organisation numbers are 926970348, 935327423 and 995541432; all three are in the live review above. See authority-offline-effect.json. This isolates the authority change from date/network variation in the full live run.

## Tests, frozen measurement and merge

Full suite: **1,416 passed, 0 failed in 431.65 seconds**. Source AST checks confirm parent_extract, award_extract, gleif_orgnr and gleif_lookup_numbers are unchanged from Stage P. The existing RA000473 negative examples were changed to foreign RA000170 because the user explicitly authorises RA000473; foreign-authority rejection expectations remain. No wrong-company regression expectation was relaxed. Live measurement completed below; normal merge follows the evidence commit. No push.


## Completed frozen-1,000 live measurement

Code commit `4ae29bc4127de87b41fd717e6275fb8ff693400e`. Source content did not change during the run (the tested commit was created while it was running). Input SHA-256 `7ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782`. Fresh state, documented README settings, no bulk override; credential variables stripped; no search, LLM or paid API. Exact command/source hash: execution.json. Runtime output is ignored under bench/runs/stage-q-whitespace/; the historical directory name does not mean the P run was reused.

| Metric | Stage P | Stage Q |
|---|---:|---:|
| GLEIF companies | 139 | 142 |
| GLEIF claims (all, including parents) | 719 | 736 |
| GLEIF direct claims | 695 | 710 |
| Websites | 112 | 112 |
| Social companies | 47 | 47 |
| Job companies | 2 | 2 |
| Activity companies | 1000 | 1000 |
| News companies | 7 | 7 |
| Article claims | 69 | 69 |
| TED award companies | 0 | 6 |
| Distinct supported facts | 166042 | 166047 |
| HTTP total | 9309 | 9170 |
| HTTP mean/company | 9.309 | 9.170 |
| HTTP max attributed/company | 40 | 40 |
| Wall seconds, including site finalisation | 1678.390 | 851.984 |
| Seconds per 100 | 167.839 | 85.198 |
| Deadline hits | 0 | 0 |

Exit **0**; **1,000 envelopes and 1,000 profiles**. **3 gained GLEIF companies, zero GLEIF losses**, matching the isolated prediction. Direct claims increased by 15; two additional parent-relationship claims give +17 total GLEIF claims. Parent acceptance was not changed: the extra matched child makes its existing explicit LEI relationships reachable. The reviewed three new RA000473 records are exactly the published gains (gleif-published-gains.json).

### Website proof-type composition (unchanged from P)

| proof_type | Websites |
|---|---:|
| `jsonld_vatid` | 5 |
| `legal_name_and_registry_contact` | 24 |
| `legal_name_without_suffix_and_two_contacts` | 9 |
| `orgnr_on_page` | 37 |
| `registry_declared_hard_contact_tier_b` | 3 |
| `registry_declared_name_tier_a` | 25 |
| `registry_phone_on_site` | 2 |
| `unique_no_corroborated` | 7 |

All proof-type counts are identical between P and Q; no website code changed. Social, jobs, activity-company and article coverage also stayed unchanged.

### Source variation, not matching-rule changes

TED source transport recovered: Q's 86 requests were all HTTP 200, versus P's 15 HTTP 200 / 215 HTTP 202. Q published **20 awards for 6 companies**, versus 0 in P. award_extract is AST-identical to P. Its full winner/buyer national-ID, country, award type, date window and exact lot linkage requirements are unchanged. The new child authority does not cause a TED request to succeed. The shorter measured wall time cannot be causally attributed to this identifier patch.

Total supported facts increased by 5: +17 GLEIF claims, +20 TED awards, and 32 fewer registry-activity facts in the separate live source snapshot. All 1,000 activity sections remain available; all 69 company-news article claims remain, with the same per-company counts. Accounts, roles, subunits, hiring and website-family claim counts are unchanged. See composition.json and activity-live-variation.json. No source/parser change was made to compensate for live differences.

NAV remained declared_index, 53.734 seconds, 8 requests, 2 companies with published ads, 0 incomplete companies, reason complete. P and Q use the identical bundled index and NAV logic.

Site publication completed: all 1,000 companies, zero warnings, largest HTML 239,582 bytes, compact fallback intact. No deadlines; pooled 19/input and per-company 40 caps unchanged.

## Decision and merge scope

KEEP the explicitly authorised child authority addition and the tested P fixes. No other external comparison was changed without evidence of a real format mismatch. The 53-file audit, saved official format counts and 15-item review are included here; no raw crawl/bulk/universe cache is added. Existing main at 1ea96a0 is the merge target, preserving P commits 588f356 and 38897f0 plus Q commit 4ae29bc in branch history. Final merge SHA is reported to the user after the normal merge. No push.
