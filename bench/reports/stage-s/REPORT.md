# Stage S: bound website recall; registry-value syntax only

## Cached fill rates

Read the existing ignored official BRREG entity bulk `bench/reports/cc-proto/raw/entities.csv.download` once; no replacement bulk download. Matched **409,653 / 411,160 universe companies** and **997 / 1,000 frozen companies**. The missing **1,507** and **3** are unknown in this cached snapshot, not proven blank or nonexistent. Primary rates below use the full requested denominators; they are observed filled fractions / lower bounds. Rates conditional on a row being present are also shown. No missing value was imputed. A nonempty contact or homepage is not necessarily usable and does not establish ownership; fill rates are not verified-site coverage.

| Field | Filled / 411,160 | Observed universe % | Filled / 1,000 | Observed cohort % | Universe % among cached rows | Cohort % among cached rows |
|---|---:|---:|---:|---:|---:|---:|
| hjemmeside | 44,864 / 411,160 | 10.9116 | 107 / 1,000 | 10.70 | 10.9517 | 10.7322 |
| epostadresse | 97,479 / 411,160 | 23.7083 | 257 / 1,000 | 25.70 | 23.7955 | 25.7773 |
| telefon | 77,914 / 411,160 | 18.9498 | 211 / 1,000 | 21.10 | 19.0195 | 21.1635 |
| mobil | 81,415 / 411,160 | 19.8013 | 225 / 1,000 | 22.50 | 19.8741 | 22.5677 |

The cohort is broadly representative for homepage fill: 10.70% vs 10.91% (about 2 fewer filled records than the 109.12 expected). It is contact-richer: email is +1.99 percentage points, phone +2.15 pp, mobile +2.70 pp. Mobile is about 2.14 ordinary sampling standard deviations above the observed universe fraction; email 1.48 and phone 1.74. These are descriptive comparisons with a finite-population sampling correction, not proof that the sample design is biased. This cohort does not understate registered contact availability; if extrapolated mechanically, it slightly overstates email/phone/mobile fill. Missing-cache rows limit exact population fill claims.

Even if every missing cache row had each field filled, universe rates would only increase by 0.3665 percentage points, cohort rates by 0.30 pp. Counts, denominators, conditional rates and arithmetic are retained in cached-measurement.json.

## Every declared-but-unpublished frozen website

Use the **Stage Q final published output**, not a provisional accepted candidate. It contains 108 nonempty parent homepage declarations, compared with 107 in the older cached bulk; these are separate source snapshots. Of the 108 live declarations, 42 companies publish an available website (possibly from another nomination) and **66 publish none**. Every such company and its verbatim value, saved declared-candidate diagnostics, final entity-scope guard, section state and errors is in declared-losses.json. Cached/live declaration lists are retained separately.

Company-level buckets use the final recorded group/shared-site guard first, otherwise the declared-source outcome. Guessed-domain errors do not replace the declared-source result. Fetched-but-no-proof is used only when a successful HTTP 200 non-robots same-domain page is still retained in state. A provisional VERIFIED candidate later withheld by a group/shared-site guard stays in the group bucket.

| Recorded outcome bucket | Companies |
|---|---:|
| malformed/unusable declared value | 0 |
| DNS failure | 7 |
| parked | 0 |
| different publisher | 8 |
| group site | 35 |
| robots | 2 |
| fetched-but-no-proof | 7 |
| budget | 0 |
| other | 7 |

The largest bucket is group/shared site (35). The second is different publisher (8); it contains fewer than ten companies, so all eight are shown rather than inventing two additional examples.

### Ten group/shared-site examples

| Org number | Legal name | Verbatim declared hjemmeside | Exact recorded outcome |
|---|---|---|---|
| 981508734 | MYKLEBUST MARITIME AS | `www.myklebustverft.no` | shared_registry_domain |
| 959189412 | NORGESVINDUET KOMPETANSE AS | `www.norgesvinduet.no` | shared_registry_domain |
| 989997459 | STASJONSBYEN BORETTSLAG | `www.framforvaltning.no` | shared_registry_domain |
| 985204381 | CLEMENS KRAFTVERK AS | `www.clemenskraft.no` | shared_registry_domain |
| 930239070 | PERMOBIL AS | `www.permobil.com` | group_site |
| 980910857 | THE ORCHARD AS | `www.phonofile.com` | group_site |
| 955010477 | AL ULLERUDTOPPEN BORETTSLAG | `usbl.no` | shared_registry_domain |
| 888951482 | OVTUN EIENDOM AS | `www.ovtun.no` | shared_registry_domain |
| 927327481 | SAMEIET SPANNATOPPEN 27-37 | `www.vestbo.no` | shared_registry_domain |
| 990459606 | SAMEIET SKJELDERUPSGATE 15 | `www.solibo.no` | shared_registry_domain |

### All eight different-publisher examples

| Org number | Legal name | Verbatim declared hjemmeside | Exact recorded outcome |
|---|---|---|---|
| 912492575 | HAUGESUND ELEKTRISKE FORRETNING AS | `www.haugel.no` | different_legal_entity |
| 915015743 | INVENSYS AS | `www.ebru.no` | different_legal_entity |
| 928329828 | HAGE OG TREFELLING AS | `Www.bergenhageogtrefelling.no` | foreign_orgnr |
| 999530095 | 7OCEAN HOLDING AS | `www.7ocean.no` | different_legal_entity |
| 977456436 | SKAUEN KRISTELIGE SKOLE | `www.delk.no/skauen` | foreign_orgnr |
| 930219746 | WIRGENESVEI 3 AS | `www.cognia.no` | foreign_orgnr |
| 988836311 | KAIKANTEN GRYLLEFJORD AS | `www.kaikanten.no` | foreign_orgnr |
| 971521570 | NORDRE FOLLO RENSEANLEGG IKS | `www.nfra.no` | different_legal_entity |

The seven other outcomes include redirects without company identity, timeouts and TLS/URL refusals; their exact records remain in declared-losses.json. They are not automatically called fetched/no-proof or a different publisher. The zero parked/budget/malformed counts apply to this declared-parent, unpublished subset only, not all website guesses in the run.

## Verbatim unusable-value distribution

Among 44,864 nonempty cached universe homepage declarations, **127 values (125 distinct verbatim strings)** did not produce an eligible registry candidate under the previous reader/filter. This includes deliberately excluded social, directory and existing provider-domain vetoes, not just parse errors. None belongs to the cached frozen 1,000.

| Exclusive classification | Objects |
|---|---:|
| missing/unrecognised host or suffix (not repaired) | 43 |
| social URL (correctly skipped) | 55 |
| unambiguous www separator (repaired) | 4 |
| email address/credentials, not website | 3 |
| existing free-mail/ISP-domain candidate veto (unchanged) | 6 |
| directory URL (existing veto, unchanged) | 4 |
| numeric nonwebsite value | 7 |
| unrecognised TLD, apparent typo (not repaired) | 5 |

All 127 lack a scheme; **that is not their cause of rejection**: the existing reader already adds HTTPS, and successfully reads nearly all missing-scheme declarations. There are 22 uppercase strings in the rejected set, but case itself is already normalized. The rejected set has zero surrounding-whitespace, terminal punctuation, trailing-text and mailto cases in this cached snapshot. Three are email/credential-shaped strings, 55 social URLs and 4 directory URLs. The full frequency table with every verbatim string and company is in verbatim-unusable-distribution.json; format flags overlap and must not be summed.

Five apparent typo TLDs (`.cno`, `.nno`, `.n`, `.o`) remain unrepaired. The anomalous nonstandard scheme string `htttp//www.fabicon.no` is also left verbatim rather than guessed by this narrowly scoped www repair. Other missing/unrecognised suffixes are retained verbatim; an intended TLD is not inferred. Six syntactically valid free-mail/ISP domains are excluded by an existing candidate-domain veto (including Telenor declarations). That is explicitly a veto limitation rather than a parser failure, and it is **not weakened** in this stage.

### The four authorised syntax repairs

| Org number | Legal name | Verbatim value | Candidate after parsing |
|---|---|---|---|
| 859419712 | OPPDAL NÆRINGSFORENING | `www/oppdal.com` | `https://www.oppdal.com/` |
| 954639258 | BALTIC EXCHANGE NORGE AS | `/www.balticyachts.no` | `https://www.balticyachts.no/` |
| 987720476 | STIKLESTAD GOLFKLUBB KLUBBHUS AS | `www:stiklestad-golfklubb.no` | `https://www.stiklestad-golfklubb.no/` |
| 990318131 | MAHARISHI-STIFTELSEN | `www/no.tm.org` | `https://www.no.tm.org/` |

Only a leading slash before `www.` and `www/` or `www:` used as the initial separator are normalized, in registry/subunit website cells only. The registered claim stays verbatim. No host spelling or TLD is guessed; no global URL parser, website proof, name match, Tier A/B check, veto, source or budget is changed. Email/social/directory/provider exclusions remain. Repaired candidates still need the existing live ownership proof before publication.

Measured isolated effect: **4 newly usable universe nominations, 0 frozen-company nominations**. Across all saved live frozen values, **108 parent + 84 subunit homepage cells**, the normalized candidate URL changes **zero** times (frozen-normalization-effect.json). Thus the frozen benchmark cannot attribute new websites to these four out-of-cohort repairs. The upper opportunity in the cached universe is four companies, not four verified sites: `4 / 411,160 * 1,000 = 0.00973` extra candidates per random 1,000 if representative. We do not claim a coverage gain we did not measure.

The evidence points mainly at existing group/publisher/proof vetoes, not malformed formatting. No name/proof-rule change is proposed or applied here. Any broader recovery of those buckets needs a separate evidence review and explicit authorization; it is outside Stage S.

## GLEIF headroom

A fresh official lookup of the frozen 1,000 in ten bounded batches, with both RA000472 and RA000473 and canonical/three-group whitespace number spellings, returned **142 exact LEI companies**. All 142 already publish in Stage Q; **0 measured unpublished exact matches**. No published Q LEI was missing from the current responses. Exact responses are cohort-0000.json through cohort-0900.json; comparison is gleif-headroom.json. This is headroom under the supported exact-ID query forms, not a guarantee that no malformed LEI record exists elsewhere or a name-based lookup.

## Validation and live effect

Focused parser/candidate tests: **30 passed in 8.93 seconds**. **Full suite: 1,432 passed, 0 failed in 692.16 seconds.** Existing tests were not changed or removed; sixteen parsing tests were added. The completed live retry and clean website review are recorded below; merge follows this evidence commit. No push.


## First benchmark attempt and resolved disk blocker

The first fresh frozen run failed during output publication with `OSError: [Errno 28] No space left on device`, exit 1, after 746.719 seconds. It produced no complete envelopes/report, so no coverage or precision result is inferred from that attempt. The exact command/input hash and failure text are preserved in disk-full-execution.json and disk-full-process.txt. This is an environment failure, not evidence of a source or proof-rule regression.

Cleanup removed only redundant generated M/N site caches and the incomplete failed-S state/site. Completed Q/P outputs, inputs, captured source evidence and repositories were preserved. Roughly 3 GiB remained, below the 10 GiB free-space retry guard. Other recently created pytest sessions were left untouched; this session's test outputs were measured but not removed. A fresh retry is prepared in bench/cache/stage_s_retry.py using bench/runs/stage-s-retry1, after the existing 1,432-test PASS and without runtime changes. It refuses to start below 10 GiB free.

After the user freed storage, the disk check showed 31,231,270,912 bytes free (29.1 GiB). A new empty-state retry started at bench/runs/stage-s-retry1 using the unchanged tested code 4788513. At that checkpoint main remained e2d32ec; the successful retry and clean review are recorded below. No coverage or precision claim is made for the failed first attempt. No push.


## Completed fresh retry and Q comparison

Code commit `47885131e12b45c5b61628da6559e4d785b46602`. Input SHA-256 `7ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782`. Fresh empty state in `bench/runs/stage-s-retry1`, README settings, no bulk override, credential variables stripped, unchanged per-company/time/pooled caps. Runtime source content remained identical to the passing full suite. The disk-full attempt was not reused or counted as a completed benchmark.

Exit **0**, **1,000 envelopes and 1,000 profiles**, completed offline site for all 1,000 companies, zero warnings, largest HTML 239,582 bytes. Exact command, wall time and tested-source hash are in execution.json. Raw runtime/state/site output remains ignored.

| Metric | Stage Q | Stage S retry |
|---|---:|---:|
| Websites | 112 | 112 |
| Social companies | 47 | 47 |
| Job companies | 2 | 2 |
| Activity companies | 1000 | 1000 |
| News companies | 7 | 7 |
| Article claims | 69 | 69 |
| GLEIF companies | 142 | 142 |
| GLEIF claims including parents | 736 | 736 |
| TED companies | 6 | 6 |
| Distinct facts | 166047 | 166046 |
| HTTP total | 9170 | 9214 |
| HTTP mean per input | 9.170 | 9.214 |
| HTTP maximum attributed/company | 40 | 40 |
| Wall seconds including finalisation | 851.984 | 1364.110 |
| Seconds per 100 | 85.198 | 136.411 |
| Deadline hits | 0 | 0 |

TED awards: **20 in both runs**. Source family counts other than website facts are identical. Website-family facts changed by -1: Maaemo booking@maaemo.no and Skoglund Maskin post@skoglundmaskin.no were absent, while one LOFOTPOSTEN AS phone claim +4777604512 was present. The exact retained/missing field records are in website-fact-membership-delta.json; the phone company's organisation number is 968386085. These are differences between separate live runs, not a normalization gain or an asserted parser failure. No contact extractor changed. Runtime differences are measured observations, not causal performance claims.

### Website proof-type composition

| proof_type | Q | S |
|---|---:|---:|
| `jsonld_vatid` | 5 | 5 |
| `legal_name_and_registry_contact` | 24 | 24 |
| `legal_name_without_suffix_and_two_contacts` | 9 | 9 |
| `orgnr_on_page` | 37 | 37 |
| `registry_declared_hard_contact_tier_b` | 3 | 3 |
| `registry_declared_name_tier_a` | 25 | 25 |
| `registry_phone_on_site` | 2 | 2 |
| `unique_no_corroborated` | 7 | 7 |

All proof-type counts and website company membership are unchanged. No newly published company website exists to attribute to the four repaired out-of-cohort registry values. The before/after URLs for one existing company differ only by www/apex.

## Every new or changed website: hand review

**New website companies: 0. Lost website companies: 0. URL-changed existing websites: 1.** The requested new-company review is therefore empty; the sole changed URL was reviewed as an additional precaution.

| Org number | Legal name | Published URL | Proof type | Verdict |
|---|---|---|---|---|
| 922187991 | ULSTEIN MINILAGER AS | http://ulsteinminilager.no | unique_no_corroborated | correct |

Q URL: `http://www.ulsteinminilager.no`; S URL: `http://ulsteinminilager.no`. This is an apex/www hostname change, **not an HTTPS-to-HTTP change**: both measured runs already use HTTP. The same previously accepted proof type is retained. This company has no registered homepage, so the registry-cell helper is not in its nomination path.

Exact saved page text:

- `<title>Ulstein Minilager</title>`
- `Flott tilbud på minilager i Ulstein`
- `Lett tilgjengelig i Saunesmarka nær Ulsteinvik sentrum (adresse: Brendehaugen 7).`
- `Ta kontakt på telefon 92 133 432 , epost: kontakt@ulsteinminilager.no`

The complete saved registry query `https://data.brreg.no/enhetsregisteret/api/enheter?navn=ulstein+minilager&size=1000` has exactly one legal-name-core match: ULSTEIN MINILAGER AS, organisation number 922187991. The saved website title/name, exact .no domain label, local service description and existing municipality/registry uniqueness corroboration agree. No new acceptance rule is inferred from the review. Exact captured claim span, visible text quotes, complete-query pagination, source URLs and hashes are in website-url-review-verdict.json and ulstein-review-source.json.

**Review: 1 correct, 0 wrong, 0 doubtful; no rule removal required.** The review used only saved sources, not a relaxed proof or a replacement live page. The four repaired universe candidates were not claimed verified or added to this cohort.

## Decision

KEEP the strictly limited registry-www syntax repair. All 1,432 tests passed, the fresh retry exited 0, every new/changed published website has a clean review, all website/social/jobs/activity/news/GLEIF/TED company counts match Q, and no proof/veto/scoring/budget logic changed. Main merge is authorised after this evidence commit; its SHA is reported to the user. The failed first attempt remains documented. No push.
