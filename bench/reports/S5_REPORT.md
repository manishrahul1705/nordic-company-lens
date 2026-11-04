# S5 final report

Completed 2026-11-04. No push. Author on every commit: Manish Rahul <manishrahul1705@gmail.com>.

Full suite: **806 passed**. Final search-OFF scale: **1000 envelopes, exit 0, 472.309s** (19.68% of the 2,400s budget; required <1,200s).

## Every benchmark gate

| Step | Commit | Available identity/people/locations/financials/website/social/jobs/activity | Web budget errors | Seconds | HTTP | Tests | Decision |
|---|---|---|---:|---:|---:|---|---|
| 1 social | `3c98640` | 100/100/85/100/8/3/1/29 | 29 | 50.177 | 623 | 732 | KEEP |
| 2 C | `4cd4892` | 100/100/85/100/10/5/1/29 | 22 | 51.683 | 617 | 742 | KEEP |
| 1b observed profiles | `d41ea10` | 100/100/85/100/10/5/1/29 | 22 | 46.617 | 618 | 744 | KEEP |
| 2 D | `3240e5b` | 100/100/85/100/11/5/1/29 | 2 | 50.961 | 745 | 744 | KEEP |
| 3 F17 report | `c1ca5df` | 100/100/85/100/11/5/1/29 | 2 | 49.153 | 741 | 744 + 3 analyzer | KEEP |
| 4 Wikidata | `e9ebb73` | 100/100/85/100/11/5/1/29 | 2 | 61.377 | 747 | 753 | KEEP |
| 4 scale checkpoint | `e8f8467` | 1000/998/774/999/73/33/3/232 | 24 | 291.317 | 6592 | 753 | VALIDATION |
| 1c refresh safeguards | `66cdb5d` | 100/100/85/100/11/5/1/29 | 2 | 56.675 | 743 | 761 | KEEP |
| 5 typed sameAs | `18d31aa` | 100/100/85/100/11/5/1/29 | 2 | 53.128 | 745 | 772 | KEEP |
| 6 original control | `0b05b2e` | 100/100/85/100/10/4/1/29 | 1 | 420.166 | 1070 | 793 | CONTROL |
| 6 rejected trial | `0b05b2e` | 100/100/85/100/13/5/1/29 | 18 | 391.532 | 1512 | 793 | ROLLED BACK |
| 6 first directory guard | `47a295c` | 100/100/85/100/11/5/1/29 | 2 | 546.260 | 1091 | 776 | KEEP |
| 6 rejected LEI retrial | `e33b951` | 100/100/85/100/11/4/1/29 | 17 | 469.008 | 1470 | 797 | ROLLED BACK |
| 6 LEI-record ownership guard | `44bf7cb` | 100/100/85/100/11/5/1/29 | 2 | 344.674 | 1081 | 780 | KEEP |
| 6 reapplied Brave | `87ab7ab` | 100/100/85/100/11/5/1/29 | 15 | 372.803 | 1498 | 801 | KEEP |
| Scale checkpoint, metadata exception | `6213840` | 1000/997/774/999/68/29/2/231 | 25 | 807.587 | 7007 | 801 | REGRESSION FOUND |
| Malformed social URL safeguard | `098dc33` | 100/100/85/100/11/5/1/29 | 2 | 292.558 | 1090 | 806 | KEEP |
| Final scale, search OFF | `c0da0a1` | 1000/997/774/999/71/32/2/231 | 23 | 472.309 | 6989 | 806 | VALIDATION |

## Search comparison and precision failure

Corrected control: `bench/runs/20261104T055653185175Z-44bf7cb`. Reapplied optional search: `bench/runs/20261104T060955663646Z-87ab7ab`. Both use identical frozen input hashes and default source budgets; the control strips credentials. The only source-selection change is explicit Brave opt-in, on top of the same directory guard.

Brave: 59 attempted queries, 0 provider errors, 129 candidate domains, estimated **$0.295** at $0.005/attempt (not an invoice). One attempt/company, no retries; snippets are never proof.

| Section | Free available | Search available | Net difference |
|---|---:|---:|---:|
| website | 11 | 11 | +0 |
| social | 5 | 5 | +0 |
| news/activity | 29 | 29 | +0 |
| jobs | 1 | 1 | +0 |

The first trial was explicitly rejected: Utdanning.no for 926698435 and VAT-Validation.com for 911683237 copied the correct company details but are third-party directories, not official sites. All five social profiles matched. The pre-existing proof accepted both pages under registry-website, registry-email and search origins. Saved raw source hashes and six before/after reproductions: `bench/runs/20261104T051103339719Z-0b05b2e/directory-root-cause.json`.

The failed optional-search implementation was withdrawn in 312266a. The global directory/URL/candidate guard and independent auditor were fixed separately in 47a295c, with four regression cases; 776 tests passed, followed by its own free benchmark. The next trial exposed NordLEI, an LEI issuer/lookup service with its own NordLEI JSON-LD publisher, as a false official site for Giljeholmen. That trial was also withdrawn in 2c5ddbd. Separate fix 44bf7cb blocks NordLEI and LEI-record permalink paths even on unlisted providers, while retaining valid company homepages that disclose their own LEI. Eight directory regression cases and 780 full tests pass before its free benchmark. Optional search was reapplied only after these guards. These checks are not a claim to detect every unlisted directory.

Initial trial: 59 attempts, 58 HTTP 200 responses and one sanitized transport/provider failure; estimated $0.295. Two invalid directory assignments plus a free-source Ralston Bau timeout recovery made its apparent website gain invalid. Rolidbakken was already available in the control, so its changed search origin was not incremental.

Second rejected trial: 61 attempts, 59 HTTP 200 and two sanitized provider/transport failures, estimated $0.305. All four social profiles matched. KN Elektro was lost to robots-body and www-redirect timeouts before search; the only newly available website was the invalid NordLEI record. Its apparent unchanged website count masked one lost real site and one directory false positive.

Total live search attempts across all trials: 179; total estimated cost $0.895. Default/final scale search remains OFF.

## Current section states

### 100 free control for search pair

| Section | Available | Not available | Failed | Ambiguous | Blocked | Budget state | Deadline state | Facts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| identity | 100 | 0 | 0 | 0 | 0 | 0 | 0 | 2898 |
| people | 100 | 0 | 0 | 0 | 0 | 0 | 0 | 1154 |
| locations | 85 | 15 | 0 | 0 | 0 | 0 | 0 | 685 |
| financials | 100 | 0 | 0 | 0 | 0 | 0 | 0 | 6162 |
| website | 11 | 76 | 12 | 1 | 0 | 0 | 0 | 94 |
| social | 5 | 82 | 12 | 1 | 0 | 0 | 0 | 5 |
| jobs | 1 | 91 | 8 | 0 | 0 | 0 | 0 | 1 |
| news/activity | 29 | 61 | 10 | 0 | 0 | 0 | 0 | 70 |

Exit 0; envelopes 100; latest accounts 100; 344.674s; HTTP 1081; deadlines 0; website-budget diagnostic count 2; warnings [].

### 100 optional Brave

| Section | Available | Not available | Failed | Ambiguous | Blocked | Budget state | Deadline state | Facts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| identity | 100 | 0 | 0 | 0 | 0 | 0 | 0 | 2898 |
| people | 100 | 0 | 0 | 0 | 0 | 0 | 0 | 1154 |
| locations | 85 | 15 | 0 | 0 | 0 | 0 | 0 | 685 |
| financials | 100 | 0 | 0 | 0 | 0 | 0 | 0 | 6162 |
| website | 11 | 67 | 19 | 3 | 0 | 0 | 0 | 94 |
| social | 5 | 73 | 19 | 3 | 0 | 0 | 0 | 5 |
| jobs | 1 | 91 | 8 | 0 | 0 | 0 | 0 | 1 |
| news/activity | 29 | 53 | 18 | 0 | 0 | 0 | 0 | 70 |

Exit 0; envelopes 100; latest accounts 100; 372.803s; HTTP 1498; deadlines 0; website-budget diagnostic count 15; warnings [].

### 100 final code, search OFF

| Section | Available | Not available | Failed | Ambiguous | Blocked | Budget state | Deadline state | Facts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| identity | 100 | 0 | 0 | 0 | 0 | 0 | 0 | 2898 |
| people | 100 | 0 | 0 | 0 | 0 | 0 | 0 | 1154 |
| locations | 85 | 15 | 0 | 0 | 0 | 0 | 0 | 685 |
| financials | 100 | 0 | 0 | 0 | 0 | 0 | 0 | 6162 |
| website | 11 | 77 | 11 | 1 | 0 | 0 | 0 | 94 |
| social | 5 | 83 | 11 | 1 | 0 | 0 | 0 | 5 |
| jobs | 1 | 91 | 8 | 0 | 0 | 0 | 0 | 1 |
| news/activity | 29 | 61 | 10 | 0 | 0 | 0 | 0 | 70 |

Exit 0; envelopes 100; latest accounts 100; 292.558s; HTTP 1090; deadlines 0; website-budget diagnostic count 2; warnings [].

### 1000 final, search OFF

| Section | Available | Not available | Failed | Ambiguous | Blocked | Budget state | Deadline state | Facts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| identity | 1000 | 0 | 0 | 0 | 0 | 0 | 0 | 28737 |
| people | 997 | 3 | 0 | 0 | 0 | 0 | 0 | 11800 |
| locations | 774 | 226 | 0 | 0 | 0 | 0 | 0 | 6527 |
| financials | 999 | 0 | 1 | 0 | 0 | 0 | 0 | 62584 |
| website | 71 | 822 | 77 | 27 | 3 | 0 | 0 | 596 |
| social | 32 | 861 | 77 | 27 | 3 | 0 | 0 | 50 |
| jobs | 2 | 925 | 73 | 0 | 0 | 0 | 0 | 2 |
| news/activity | 231 | 686 | 83 | 0 | 0 | 0 | 0 | 607 |

Exit 0; envelopes 1000; latest accounts 999; 472.309s; HTTP 6989; deadlines 0; website-budget diagnostic count 23; warnings [].

## Source freshness and scale evidence

The earlier 53s checkpoint used a current NAV index. The next-day original control fell back because the index was stale: 362 full-feed pages, 394 NAV requests, 381.906s NAV runtime, complete feed transport. This explains most of its 420.166s wall time. Ralston Bau had a robots timeout and a redirect/body timeout, losing its website and linked Facebook without a code change. No 429s in that control; all 100 accounts remained available.

The first completed stale-index scale checkpoint took 807.587s, exit 0 and 1000 envelopes, NAV 560.188s/507 requests, with 68 website/29 social/2 jobs/231 activity available. Full review found a CNC Norway exception introduced through S5’s observation ledger: malformed JSON-LD sameAs https://[object Object] raised ValueError at urlsplit. Separate fix 098dc33 ignores malformed profile URLs, preserving valid proof and valid social links. Five regression cases plus the full suite pass before its own 100-company bench and the refreshed final scale. The checkpoint is preserved, not misrepresented as final-code output.

Raw final accounts failure/HTTP evidence: `scale-diagnosis.json` beside this report. This distinguishes BRREG source failures from request caps/rate limits; no accounts bug is changed in S5.

Wikidata 100-company batch returned no bindings. The earlier 1000 checkpoint matched nine companies, nominated nine websites and returned five name-matched CC0 social claims for Lofotposten and Danseinformasjonen. None of its verified websites used Wikidata origin; C/D gains must not be attributed to Wikidata. Final Wikidata metrics are preserved in report.json.

## F17 website loss diagnosis


This is a read-only analysis of saved run diagnostics. No network requests or behavior changes.

## primary — 100 companies

Available: 11; missing: 89.

| Stop reason | Companies |
|---|---:|
| all candidates DNS-missing | 44 |
| TLS-connect failure | 20 |
| fetched but no proof | 15 |
| robots or blocked | 6 |
| no candidates generated | 2 |
| budget exhausted | 1 |
| ambiguous (name-only or competing candidates) | 1 |

Reasons are exclusive stop buckets from recorded candidate diagnostics, not inferred exhaustive absence. Budget includes request/deadline limits. DNS/transient TLS failures are grouped conservatively when low-level transport messages are unavailable.

### all candidates DNS-missing

| Company | Name | Candidate domains |
|---|---|---|
| 912823970 | MYNT OG EIENDOM BESSAKER AS | mynteiendombessaker.no, mynteiendombessaker-as.no, mynteiendombessakeras.no, mynteiendombessaker.as, mynteiendombessaker.com, mynt-eiendom-bessaker.no, mynt-eiendom-bessaker-as.no, mynt-eiendom-bessakeras.no, mynt-eiendom-bessaker.as, mynt-eiendom-bessaker.com |
| 916729774 | FIKO EIENDOM AS | fikoeiendom.no, fikoeiendom-as.no, fikoeiendomas.no, fikoeiendom.as, fikoeiendom.com, fiko-eiendom.no, fiko-eiendom-as.no, fiko-eiendomas.no, fiko-eiendom.as, fiko-eiendom.com |
| 917998787 | DRAGEHAUGEN VERDI AS | dragehaugenverdi.no, dragehaugenverdi-as.no, dragehaugenverdias.no, dragehaugenverdi.as, dragehaugenverdi.com, dragehaugen-verdi.no, dragehaugen-verdi-as.no, dragehaugen-verdias.no, dragehaugen-verdi.as, dragehaugen-verdi.com |
| 918049215 | MENSTAD NÆRINGSPARK AS | menstadnaeringspark.no, menstadnaeringspark-as.no, menstadnaeringsparkas.no, menstadnaeringspark.as, menstadnaeringspark.com, menstad-naeringspark.no, menstad-naeringspark-as.no, menstad-naeringsparkas.no, menstad-naeringspark.as, menstad-naeringspark.com, menstadnaringspark.no, menstadnaringspark-as.no, menstadnaringsparkas.no, menstadnaringspark.as, menstadnaringspark.com, menstad-naringspark.no, menstad-naringspark-as.no, menstad-naringsparkas.no, menstad-naringspark.as, menstad-naringspark.com, xn--menstadnringspark-yrb.no, xn--menstadnringspark-yrb.com, xn--menstad-nringspark-wub.no, xn--menstad-nringspark-wub.com |
| 919948493 | SQ URBAN LANDSKAP AS | squrbanlandskap.no, squrbanlandskap-as.no, squrbanlandskapas.no, squrbanlandskap.as, squrbanlandskap.com, sq-urban-landskap.no, sq-urban-landskap-as.no, sq-urban-landskapas.no, sq-urban-landskap.as, sq-urban-landskap.com |
| 916049153 | SJØL INVEST AS | sjolinvest.no, sjolinvest-as.no, sjolinvestas.no, sjolinvest.as, sjolinvest.com, sjol-invest.no, sjol-invest-as.no, sjol-investas.no, sjol-invest.as, sjol-invest.com, sjoelinvest.no, sjoelinvest-as.no, sjoelinvestas.no, sjoelinvest.as, sjoelinvest.com, sjoel-invest.no, sjoel-invest-as.no, sjoel-investas.no, sjoel-invest.as, sjoel-invest.com, xn--sjlinvest-m8a.no, xn--sjlinvest-m8a.com, xn--sjl-invest-1cb.no, xn--sjl-invest-1cb.com |
| 923472134 | BOLIG 1 HALDEN AS | bolig1halden.no, bolig1halden-as.no, bolig1haldenas.no, bolig1halden.as, bolig1halden.com, bolig-1-halden.no, bolig-1-halden-as.no, bolig-1-haldenas.no, bolig-1-halden.as, bolig-1-halden.com |
| 936312055 | ULTRAMAX 8 AS | ultramax8.no, ultramax8-as.no, ultramax8as.no, ultramax8.as, ultramax8.com, ultramax-8.no, ultramax-8-as.no, ultramax-8as.no, ultramax-8.as, ultramax-8.com |
| 914723612 | HAAKON VII S GT HOLDING AS | haakonviisgtholding.no, haakonviisgtholding-as.no, haakonviisgtholdingas.no, haakonviisgtholding.as, haakonviisgtholding.com, haakon-vii-s-gt-holding.no, haakon-vii-s-gt-holding-as.no, haakon-vii-s-gt-holdingas.no, haakon-vii-s-gt-holding.as, haakon-vii-s-gt-holding.com |
| 918975934 | TØMRER TOMMY WIK OLSEN AS | tomrertommywikolsen.no, tomrertommywikolsen-as.no, tomrertommywikolsenas.no, tomrertommywikolsen.as, tomrertommywikolsen.com, tomrer-tommy-wik-olsen.no, tomrer-tommy-wik-olsen-as.no, tomrer-tommy-wik-olsenas.no, tomrer-tommy-wik-olsen.as, tomrer-tommy-wik-olsen.com, toemrertommywikolsen.no, toemrertommywikolsen-as.no, toemrertommywikolsenas.no, toemrertommywikolsen.as, toemrertommywikolsen.com, toemrer-tommy-wik-olsen.no, toemrer-tommy-wik-olsen-as.no, toemrer-tommy-wik-olsenas.no, toemrer-tommy-wik-olsen.as, toemrer-tommy-wik-olsen.com, xn--tmrertommywikolsen-g4b.no, xn--tmrertommywikolsen-g4b.com, xn--tmrer-tommy-wik-olsen-qfc.no, xn--tmrer-tommy-wik-olsen-qfc.com |

### TLS-connect failure

| Company | Name | Candidate domains |
|---|---|---|
| 982410851 | MARUN AS | marun.no, marun-as.no, marunas.no, marun.as, marun.com |
| 936276075 | M BERGUM AS | mbergum.no, mbergum-as.no, mbergumas.no, mbergum.as, mbergum.com, m-bergum.no, m-bergum-as.no, m-bergumas.no, m-bergum.as, m-bergum.com |
| 989252968 | MARIA LOUISE AS | marialouise.no, marialouise-as.no, marialouiseas.no, marialouise.as, marialouise.com, maria-louise.no, maria-louise-as.no, maria-louiseas.no, maria-louise.as, maria-louise.com |
| 920597122 | ARCTIC GRILL AS | arcticgrill.no, arcticgrill-as.no, arcticgrillas.no, arcticgrill.as, arcticgrill.com, arctic-grill.no, arctic-grill-as.no, arctic-grillas.no, arctic-grill.as, arctic-grill.com |
| 829363712 | JONSSON BYGG AS | jonssonbygg.no, jonssonbygg-as.no, jonssonbyggas.no, jonssonbygg.as, jonssonbygg.com, jonsson-bygg.no, jonsson-bygg-as.no, jonsson-byggas.no, jonsson-bygg.as, jonsson-bygg.com |
| 921810229 | KLINEVO AS | klinevo.no, klinevo-as.no, klinevoas.no, klinevo.as, klinevo.com |
| 929074009 | MULLIGAN INDOOR GOLF AS | mulligangolf.no, mulliganindoorgolf.no, mulliganindoorgolf-as.no, mulliganindoorgolfas.no, mulliganindoorgolf.as, mulliganindoorgolf.com, mulligan-indoor-golf.no, mulligan-indoor-golf-as.no, mulligan-indoor-golfas.no, mulligan-indoor-golf.as, mulligan-indoor-golf.com |
| 915707238 | RØRESTRAND EIENDOM AS | rorestrandeiendom.no, rorestrandeiendom-as.no, rorestrandeiendomas.no, rorestrandeiendom.as, rorestrandeiendom.com, rorestrand-eiendom.no, rorestrand-eiendom-as.no, rorestrand-eiendomas.no, rorestrand-eiendom.as, rorestrand-eiendom.com, roerestrandeiendom.no, roerestrandeiendom-as.no, roerestrandeiendomas.no, roerestrandeiendom.as, roerestrandeiendom.com, roerestrand-eiendom.no, roerestrand-eiendom-as.no, roerestrand-eiendomas.no, roerestrand-eiendom.as, roerestrand-eiendom.com, xn--rrestrandeiendom-lxb.no, xn--rrestrandeiendom-lxb.com, xn--rrestrand-eiendom-00b.no, xn--rrestrand-eiendom-00b.com |
| 927901722 | KURIUS AS | kurius.no, kurius-as.no, kuriusas.no, kurius.as, kurius.com |
| 922069212 | KARLSEN AS | karlsen.no, karlsen-as.no, karlsenas.no, karlsen.as, karlsen.com |

### fetched but no proof

| Company | Name | Candidate domains |
|---|---|---|
| 981508734 | MYKLEBUST MARITIME AS | myklebustverft.no, myklebustmaritime.no, myklebustmaritime-as.no, myklebustmaritimeas.no, myklebustmaritime.as, myklebustmaritime.com, myklebust-maritime.no, myklebust-maritime-as.no, myklebust-maritimeas.no, myklebust-maritime.as, myklebust-maritime.com |
| 995541432 | WACKER CHEMICALS NORWAY AS | wacker.com, wackerchemicalsnorway.no, wackerchemicalsnorway-as.no, wackerchemicalsnorwayas.no, wackerchemicalsnorway.as, wackerchemicalsnorway.com, wacker-chemicals-norway.no, wacker-chemicals-norway-as.no, wacker-chemicals-norwayas.no, wacker-chemicals-norway.as, wacker-chemicals-norway.com |
| 935450233 | FLUVIO AS | fluvio.no, fluvio-as.no, fluvioas.no, fluvio.as, fluvio.com |
| 995748983 | MAAEMO AS | maaemo.no, maaemo-as.no, maaemoas.no, maaemo.as, maaemo.com |
| 921338732 | DOKTOR MUNKS PARK III BORETTSLAG | pbbl.no, doktormunksparkiiiborettslag.no, doktormunksparkiiiborettslag-as.no, doktormunksparkiiiborettslagas.no, doktormunksparkiiiborettslag.as, doktormunksparkiiiborettslag.com, doktor-munks-park-iii-borettslag.no, doktor-munks-park-iii-borettslag-as.no, doktor-munks-park-iii-borettslagas.no, doktor-munks-park-iii-borettslag.as, doktor-munks-park-iii-borettslag.com |
| 968468235 | HÅRSTUA AS | harstua.no, harstua-as.no, harstuaas.no, harstua.as, harstua.com, haarstua.no, haarstua-as.no, haarstuaas.no, haarstua.as, haarstua.com, xn--hrstua-iua.no, xn--hrstua-iua.com |
| 997352572 | SMEDATUNET SAMEIE | vistnes.no, smedatunetsameie.no, smedatunetsameie-as.no, smedatunetsameieas.no, smedatunetsameie.as, smedatunetsameie.com, smedatunet-sameie.no, smedatunet-sameie-as.no, smedatunet-sameieas.no, smedatunet-sameie.as, smedatunet-sameie.com |
| 996927903 | BONO SANDVIKSBODER AS | backe.no, bonosandviksboder.no, bonosandviksboder-as.no, bonosandviksboderas.no, bonosandviksboder.as, bonosandviksboder.com, bono-sandviksboder.no, bono-sandviksboder-as.no, bono-sandviksboderas.no, bono-sandviksboder.as, bono-sandviksboder.com |
| 934244443 | KLET AS | klet.no, klet-as.no, kletas.no, klet.as, klet.com |
| 976746651 | SKRENTEN 21 AS | bntv.no, skrenten21.no, skrenten21-as.no, skrenten21as.no, skrenten21.as, skrenten21.com, skrenten-21.no, skrenten-21-as.no, skrenten-21as.no, skrenten-21.as, skrenten-21.com |

## scale — 1000 companies

Available: 71; missing: 929.

| Stop reason | Companies |
|---|---:|
| all candidates DNS-missing | 480 |
| fetched but no proof | 154 |
| TLS-connect failure | 153 |
| robots or blocked | 46 |
| proof conflict (other orgnr) | 43 |
| ambiguous (name-only or competing candidates) | 27 |
| budget exhausted | 15 |
| no candidates generated | 11 |

Reasons are exclusive stop buckets from recorded candidate diagnostics, not inferred exhaustive absence. Budget includes request/deadline limits. DNS/transient TLS failures are grouped conservatively when low-level transport messages are unavailable.

## Recovery priority

Choose recovery work from the measured buckets: DNS-missing legal-name guesses need new nominations (Wikidata, then optional search); fetched/name-only pages need additional ownership evidence; budget stops need enough reserved proof requests. More budget does not make absent DNS guesses valid, and none of these bucket counts is a measured recovery promise.

Every missing company, furthest stage, final stop bucket, candidate domains and original attempts are recorded in `website-loss.json`. These are observed candidate failures, not proof that the company has no genuine official site.

## Complete reviewed item lists

Every published social item was reviewed at each gate, using retained primary-page/registry/Wikidata evidence, not search snippets. New or changed official-site and website-article assignments were also opened and checked. All listed source blobs were SHA-256 checked. Social-platform pages are not crawled. Each run has s5-review.json with URLs, hashes, excerpts and manual resolutions. Repeated unchanged social profiles are deliberately included.

Step 1 removed Vokser Group and StudioRalstonBau handles because the extra brand words lacked registered-name corroboration; this is not an assertion that those accounts were proven to belong to another company. Rolidbakken’s Diseth FUS Facebook link remains rejected. The earlier scale review’s Lefdal/Wullum independent-auditor false positives are documented and regression-tested.

### 1 social — 20261103T203539261283Z-3c98640

| Org | Registered name | Field | Published URL | Review |
|---|---|---|---|---|
| 986739874 | AAS BETONG AS | social_profile.6f188b99ccf6f9021547 | https://www.facebook.com/Aas-Betong-As-576953999078361 | PASS: exact company/source checked |
| 991368000 | RALSTON BAU AS | social_profile.943c0bea445efdf691a2 | https://www.facebook.com/ralstonbau | PASS: exact company/source checked |
| 928657523 | VIVIFY GRUPPEN AS | social_profile.07cfe9a233e8741b1ba5 | https://www.linkedin.com/company/vivify-gruppen | PASS: exact company/source checked |

Opened 3; wrong/invalid ownership findings 0. Decision: KEEP.

### 2 C — 20261103T204015696246Z-4cd4892

| Org | Registered name | Field | Published URL | Review |
|---|---|---|---|---|
| 991247610 | ROLIDBAKKEN FUS BARNEHAGE AS | official_website | https://fus.no | PASS: exact company/source checked |
| 986739874 | AAS BETONG AS | social_profile.6f188b99ccf6f9021547 | https://www.facebook.com/Aas-Betong-As-576953999078361 | PASS: exact company/source checked |
| 920918204 | STOA AUTOREP AS | official_website | https://stoaautorep.no | PASS: exact company/source checked |
| 920918204 | STOA AUTOREP AS | social_profile.4a5bbc80815934310b5a | https://www.facebook.com/stoaautorep | PASS: exact company/source checked |
| 823147112 | KN ELEKTRO AS | official_website | https://knelektro.no | PASS: exact company/source checked |
| 823147112 | KN ELEKTRO AS | social_profile.19b491ae8376e3f94d32 | https://www.facebook.com/KN-Elektro-As-104194150969215 | PASS: exact company/source checked |
| 991368000 | RALSTON BAU AS | social_profile.943c0bea445efdf691a2 | https://www.facebook.com/ralstonbau | PASS: exact company/source checked |
| 928657523 | VIVIFY GRUPPEN AS | social_profile.07cfe9a233e8741b1ba5 | https://www.linkedin.com/company/vivify-gruppen | PASS: exact company/source checked |

Opened 8; wrong/invalid ownership findings 0. Decision: KEEP.

### 1b observed profiles — 20261103T204509504774Z-d41ea10

| Org | Registered name | Field | Published URL | Review |
|---|---|---|---|---|
| 986739874 | AAS BETONG AS | social_profile.6f188b99ccf6f9021547 | https://www.facebook.com/Aas-Betong-As-576953999078361 | PASS: exact company/source checked |
| 920918204 | STOA AUTOREP AS | social_profile.4a5bbc80815934310b5a | https://www.facebook.com/stoaautorep | PASS: exact company/source checked |
| 823147112 | KN ELEKTRO AS | social_profile.19b491ae8376e3f94d32 | https://www.facebook.com/KN-Elektro-As-104194150969215 | PASS: exact company/source checked |
| 991368000 | RALSTON BAU AS | social_profile.943c0bea445efdf691a2 | https://www.facebook.com/ralstonbau | PASS: exact company/source checked |
| 928657523 | VIVIFY GRUPPEN AS | social_profile.07cfe9a233e8741b1ba5 | https://www.linkedin.com/company/vivify-gruppen | PASS: exact company/source checked |

Opened 5; wrong/invalid ownership findings 0. Decision: KEEP.

### 2 D — 20261103T205132975943Z-3240e5b

| Org | Registered name | Field | Published URL | Review |
|---|---|---|---|---|
| 986739874 | AAS BETONG AS | social_profile.6f188b99ccf6f9021547 | https://www.facebook.com/Aas-Betong-As-576953999078361 | PASS: exact company/source checked |
| 920918204 | STOA AUTOREP AS | social_profile.4a5bbc80815934310b5a | https://www.facebook.com/stoaautorep | PASS: exact company/source checked |
| 823147112 | KN ELEKTRO AS | social_profile.19b491ae8376e3f94d32 | https://www.facebook.com/KN-Elektro-As-104194150969215 | PASS: exact company/source checked |
| 991368000 | RALSTON BAU AS | social_profile.943c0bea445efdf691a2 | https://www.facebook.com/ralstonbau | PASS: exact company/source checked |
| 913876954 | ØRJE REGNSKAPSKONTOR AS | official_website | https://www.orjeregnskap.no | PASS: exact company/source checked |
| 928657523 | VIVIFY GRUPPEN AS | social_profile.07cfe9a233e8741b1ba5 | https://www.linkedin.com/company/vivify-gruppen | PASS: exact company/source checked |

Opened 6; wrong/invalid ownership findings 0. Decision: KEEP.

### 3 F17 report — 20261103T205448475112Z-c1ca5df

| Org | Registered name | Field | Published URL | Review |
|---|---|---|---|---|
| 986739874 | AAS BETONG AS | social_profile.6f188b99ccf6f9021547 | https://www.facebook.com/Aas-Betong-As-576953999078361 | PASS: exact company/source checked |
| 920918204 | STOA AUTOREP AS | social_profile.4a5bbc80815934310b5a | https://www.facebook.com/stoaautorep | PASS: exact company/source checked |
| 823147112 | KN ELEKTRO AS | social_profile.19b491ae8376e3f94d32 | https://www.facebook.com/KN-Elektro-As-104194150969215 | PASS: exact company/source checked |
| 991368000 | RALSTON BAU AS | social_profile.943c0bea445efdf691a2 | https://www.facebook.com/ralstonbau | PASS: exact company/source checked |
| 928657523 | VIVIFY GRUPPEN AS | social_profile.07cfe9a233e8741b1ba5 | https://www.linkedin.com/company/vivify-gruppen | PASS: exact company/source checked |

Opened 5; wrong/invalid ownership findings 0. Decision: KEEP.

### 4 Wikidata — 20261103T210508740261Z-e9ebb73

| Org | Registered name | Field | Published URL | Review |
|---|---|---|---|---|
| 986739874 | AAS BETONG AS | social_profile.6f188b99ccf6f9021547 | https://www.facebook.com/Aas-Betong-As-576953999078361 | PASS: exact company/source checked |
| 920918204 | STOA AUTOREP AS | social_profile.4a5bbc80815934310b5a | https://www.facebook.com/stoaautorep | PASS: exact company/source checked |
| 823147112 | KN ELEKTRO AS | social_profile.19b491ae8376e3f94d32 | https://www.facebook.com/KN-Elektro-As-104194150969215 | PASS: exact company/source checked |
| 991368000 | RALSTON BAU AS | social_profile.943c0bea445efdf691a2 | https://www.facebook.com/ralstonbau | PASS: exact company/source checked |
| 928657523 | VIVIFY GRUPPEN AS | social_profile.07cfe9a233e8741b1ba5 | https://www.linkedin.com/company/vivify-gruppen | PASS: exact company/source checked |

Opened 5; wrong/invalid ownership findings 0. Decision: KEEP.

### 4 scale checkpoint — 20261103T210757525212Z-e8f8467

| Org | Registered name | Field | Published URL | Review |
|---|---|---|---|---|
| 991247610 | ROLIDBAKKEN FUS BARNEHAGE AS | official_website | https://fus.no | PASS: exact company/source checked |
| 986739874 | AAS BETONG AS | social_profile.6f188b99ccf6f9021547 | https://www.facebook.com/Aas-Betong-As-576953999078361 | PASS: exact company/source checked |
| 920918204 | STOA AUTOREP AS | official_website | https://stoaautorep.no | PASS: exact company/source checked |
| 920918204 | STOA AUTOREP AS | social_profile.4a5bbc80815934310b5a | https://www.facebook.com/stoaautorep | PASS: exact company/source checked |
| 823147112 | KN ELEKTRO AS | official_website | https://knelektro.no | PASS: exact company/source checked |
| 823147112 | KN ELEKTRO AS | social_profile.19b491ae8376e3f94d32 | https://www.facebook.com/KN-Elektro-As-104194150969215 | PASS: exact company/source checked |
| 991368000 | RALSTON BAU AS | social_profile.943c0bea445efdf691a2 | https://www.facebook.com/ralstonbau | PASS: exact company/source checked |
| 913876954 | ØRJE REGNSKAPSKONTOR AS | official_website | https://www.orjeregnskap.no | PASS: exact company/source checked |
| 928657523 | VIVIFY GRUPPEN AS | social_profile.07cfe9a233e8741b1ba5 | https://www.linkedin.com/company/vivify-gruppen | PASS: exact company/source checked |
| 987564911 | NÆRINGSØKONOMI AS | official_website | https://naringsokonomi.no | PASS: exact company/source checked |
| 936629466 | CLOSVA AS | social_profile.746d50370f5da22298d3 | https://www.linkedin.com/company/closva | PASS: exact company/source checked |
| 936629466 | CLOSVA AS | dated_item.b0ac1ef3391251b00ffe | https://closva.com/no/artikler/global-pivot-equity-case | PASS: exact company/source checked |
| 936629466 | CLOSVA AS | dated_item.fb739c4b40157569f2ea | https://closva.com/dk/artikler/global-pivot-equity-case | PASS: exact company/source checked |
| 936629466 | CLOSVA AS | dated_item.5caaebbca94f93a77909 | https://closva.com/no/artikler/andreas-rasmussen-blir-med-i-closva | PASS: exact company/source checked |
| 936629466 | CLOSVA AS | dated_item.5bd990fa461a5aac6772 | https://closva.com/dk/artikler/andreas-rasmussen-bliver-en-del-af-closva | PASS: exact company/source checked |
| 936629466 | CLOSVA AS | dated_item.6e2c1a1c8d023dd16bec | https://closva.com/no/artikler/global-pivot-equity-investerer-i-closva | PASS: exact company/source checked |
| 936629466 | CLOSVA AS | dated_item.e3f6904c734b799a3dfe | https://closva.com/dk/artikler/global-pivot-equity-investerer-i-closva | PASS: exact company/source checked |
| 924912758 | BORG BIERSTUBE AS | official_website | https://www.borgbierstube.no | PASS: exact company/source checked |
| 924912758 | BORG BIERSTUBE AS | social_profile.4c67ba313eda64e60646 | https://www.instagram.com/borgbierstube | PASS: exact company/source checked |
| 924912758 | BORG BIERSTUBE AS | social_profile.0c59d28066b5c16e3eec | https://www.facebook.com/borgbierstube | PASS: exact company/source checked |
| 931069373 | FJELDE TEKNIKK AS | official_website | https://www.fjeldeteknikk.no | PASS: exact company/source checked |
| 932448459 | ROMERIKE VVS AS | official_website | https://romerikevvs.no | PASS: exact company/source checked |
| 932448459 | ROMERIKE VVS AS | social_profile.d44ae658e298407818b9 | https://www.instagram.com/romerike_vvs | PASS: exact company/source checked |
| 893948112 | NORSK PUBLIKUMSUTVIKLING | official_website | https://norskpublikumsutvikling.no | PASS: exact company/source checked |
| 893948112 | NORSK PUBLIKUMSUTVIKLING | social_profile.958eeb99bc8fb420e436 | https://www.facebook.com/NorskPublikumsutvikling.AudiencesNorway | PASS: exact company/source checked |
| 893948112 | NORSK PUBLIKUMSUTVIKLING | social_profile.8bab7e90db4089cdf17f | https://www.instagram.com/norskpublikumsutvikling | PASS: exact company/source checked |
| 968386085 | LOFOTPOSTEN AS | official_website | https://www.lofotposten.no | PASS: exact company/source checked |
| 968386085 | LOFOTPOSTEN AS | social_profile.18827a4b63ceebca6fbd | https://x.com/lofotposten | PASS: exact company/source checked |
| 968386085 | LOFOTPOSTEN AS | social_profile.c0f4fd23d86e444b326b | https://www.instagram.com/lofotposten | PASS: exact company/source checked |
| 968386085 | LOFOTPOSTEN AS | social_profile.2ab01462d39d2bd0a770 | https://www.facebook.com/lofotposten | PASS: exact company/source checked |
| 926490060 | CONTROL SOLUTIONS AS | official_website | https://www.control-solutions.no | PASS: exact company/source checked |
| 926490060 | CONTROL SOLUTIONS AS | social_profile.d6ed8e08a0a64f44813c | https://www.facebook.com/ControlSolutionsAS | PASS: exact company/source checked |
| 919276843 | HOLAUG PUKKVERK AS | official_website | https://www.holaugpukkverk.no | PASS: exact company/source checked |
| 997024311 | GEONORD AS | official_website | https://www.geonord.no | PASS: exact company/source checked |
| 987895276 | CONPLAN AS | official_website | https://www.conplan.no | PASS: exact company/source checked |
| 987895276 | CONPLAN AS | social_profile.629a70b1abecf554d0cc | https://www.facebook.com/Conplan-AS-509721459118772 | PASS: exact company/source checked |
| 934982762 | ARKIDAL AS | official_website | https://www.arkidal.no | PASS: exact company/source checked |
| 934982762 | ARKIDAL AS | social_profile.dfe21c80c809e08f1ffb | https://www.youtube.com/@arkidal | PASS: exact company/source checked |
| 934982762 | ARKIDAL AS | social_profile.f3c46f3da81d2961092d | https://www.facebook.com/arkidal | PASS: exact company/source checked |
| 998077028 | INNOVATION SUPPORT AS | social_profile.fb88a1126bd44a5491ed | https://www.linkedin.com/company/innovation-support-as | PASS: exact company/source checked |
| 998077028 | INNOVATION SUPPORT AS | social_profile.879e94b8d418b4b7b866 | https://www.facebook.com/InnovationSupport | PASS: exact company/source checked |
| 942393679 | HARVELAND AS | official_website | https://harveland-as.no | PASS: exact company/source checked |
| 942393679 | HARVELAND AS | social_profile.274b76ad29764cfd8e8d | https://www.facebook.com/HarvelandAS | PASS: exact company/source checked |
| 990012288 | TB MASKIN AS | official_website | https://www.tbmaskin.no | PASS: exact company/source checked |
| 990012288 | TB MASKIN AS | social_profile.126746e2b1c39291086e | https://www.instagram.com/tbmaskin | PASS: exact company/source checked |
| 990012288 | TB MASKIN AS | social_profile.f1a2ea5e9c5099683f11 | https://www.linkedin.com/company/tbmaskin | PASS: exact company/source checked |
| 811888672 | Fusa Mekaniske Industri AS | official_website | https://www.fusamek.no | PASS: exact company/source checked |
| 926065173 | THE LAB RETRIEVER AS | official_website | https://thelabretriever.com | PASS: exact company/source checked |
| 926065173 | THE LAB RETRIEVER AS | social_profile.7619557adb370bbebaed | https://www.facebook.com/The-Lab-Retriever-107894350774301 | PASS: exact company/source checked |
| 926065173 | THE LAB RETRIEVER AS | social_profile.c3d54970de735857fb6a | https://www.instagram.com/thelabretriever | PASS: exact company/source checked |
| 933458032 | MOTORSYKLISTEN AS | official_website | https://motorsyklisten.as | PASS: exact company/source checked |
| 938092516 | OSLO CHAMBER OF COMMERCE | social_profile.9d8e1de3667fa506b055 | https://www.linkedin.com/company/oslo-chamber-of-commerce | PASS: exact company/source checked |
| 938092516 | OSLO CHAMBER OF COMMERCE | social_profile.ba2cfa7bb751aee963a5 | https://www.instagram.com/oslochamberofcommerce | PASS: exact company/source checked |
| 996979660 | VALDRESMEIERIET AS | official_website | https://www.valdresmeieriet.no | PASS: exact company/source checked |
| 993919675 | FEIE- OG TILSYNSTJENESTER AS | dated_item.3d67d5edd855ca5b4467 | https://www.tilsyn.no/nyheter/riktig-vedlikehold-av-ildsted-og-pipe-for-a-forebygge-pipebrann | PASS: exact company/source checked |
| 993919675 | FEIE- OG TILSYNSTJENESTER AS | dated_item.bc7523d8dec282548abd | https://www.tilsyn.no/nyheter/sotutslipp-fra-vedfyrt-pizzaovn-og-feierens-rolle-i-brannforebygging | PASS: exact company/source checked |
| 993919675 | FEIE- OG TILSYNSTJENESTER AS | dated_item.e7578a5a846fa8451f44 | https://www.tilsyn.no/nyheter/skorsteinsblokkering-pa-grunn-av-fuglereir-betydning-for-brannforebygging-og-fei | PASS: exact company/source checked |
| 993919675 | FEIE- OG TILSYNSTJENESTER AS | dated_item.52a4d275acc6dc4a3733 | https://www.tilsyn.no/nyheter/roykutvikling-i-peis-hendelse-i-tomm-murstadbakken-oslo | PASS: exact company/source checked |
| 993919675 | FEIE- OG TILSYNSTJENESTER AS | dated_item.6874f952187f72f148e4 | https://www.tilsyn.no/nyheter/roykutvikling-i-kjeller-forebygging-og-feierens-rolle | PASS: exact company/source checked |
| 993919675 | FEIE- OG TILSYNSTJENESTER AS | dated_item.26c159f4aacbc64269cc | https://www.tilsyn.no/nyheter/pipebrann-i-schwensens-gate-st-hanshaugen-brannforebygging-og-feierens-rolle | PASS: exact company/source checked |
| 993919675 | FEIE- OG TILSYNSTJENESTER AS | dated_item.abe8e46d380a5c952524 | https://www.tilsyn.no/nyheter/roykutvikling-i-kjeller-pa-gr-nerlokka-brannforebygging-og-feierens-rolle | PASS: exact company/source checked |
| 993919675 | FEIE- OG TILSYNSTJENESTER AS | dated_item.7b5613bec366fe1ef183 | https://www.tilsyn.no/nyheter/pipebranner-i-asker-og-baerum-brannvesenets-innsats-og-feierens-rolle-i-brannfor | PASS: exact company/source checked |
| 993919675 | FEIE- OG TILSYNSTJENESTER AS | dated_item.485c80058f6beee812e3 | https://www.tilsyn.no/nyheter/pipebrann-i-ekebergveien-branninnsats-og-brannforebygging | PASS: exact company/source checked |
| 983520944 | SPINELL FRISØR AS | official_website | https://www.spinellfrisor.no | PASS: exact company/source checked |
| 995654539 | TAKST MÅLENG AS | official_website | https://www.takstmaaleng.no | PASS: exact company/source checked |
| 992868775 | ALFA LAGERHOTELL AS | official_website | https://alfalagerhotell.no | PASS: exact company/source checked |
| 917283109 | CL BYGG & EIENDOM AS | official_website | https://clbygg.no | PASS: exact company/source checked |
| 917283109 | CL BYGG & EIENDOM AS | social_profile.59a1b99868a9705a4142 | https://www.facebook.com/CL-Bygg-Eiendom-As-105330174564671 | PASS: exact company/source checked |
| 917283109 | CL BYGG & EIENDOM AS | social_profile.8c2973c54b875a8cf074 | https://www.instagram.com/clbyggeiendom | PASS: exact company/source checked |
| 918486666 | ANTISINK AS | social_profile.7f3132bba63574468739 | https://no.linkedin.com/company/antisink-as | PASS: exact company/source checked |
| 982388449 | IDESTOVA AS | social_profile.c4b91b95c9085ccd16b6 | https://www.facebook.com/Idestova-As-293922170749469 | PASS: exact company/source checked |
| 982388449 | IDESTOVA AS | social_profile.fe5f389f36aa61edf799 | https://instagram.com/idestova | PASS: exact company/source checked |
| 982388449 | IDESTOVA AS | social_profile.e4f185ea4bc300f21707 | https://www.facebook.com/idestova | PASS: exact company/source checked |
| 920358411 | LARSZACHARIASSEN AS | social_profile.389e9e2abacc41593c67 | https://www.instagram.com/larszachariassen | PASS: exact company/source checked |
| 971558415 | DANSEINFORMASJONEN STI | social_profile.849b53a48559cc37adac | https://www.instagram.com/danseinformasjonen | PASS: exact company/source checked |
| 971558415 | DANSEINFORMASJONEN STI | social_profile.438117087531d9623489 | https://www.facebook.com/danseinformasjonen | PASS: exact company/source checked |
| 821962242 | LAKSESYSTEMER AS | social_profile.8274a67d0ace290d26fa | https://www.facebook.com/laksesystemer | PASS: exact company/source checked |
| 968545337 | LEFDAL INSTALLASJON AS | official_website | https://lefdal.no | PASS: exact company/source checked |
| 968545337 | LEFDAL INSTALLASJON AS | social_profile.f1c3874f5818e83511e7 | https://no.linkedin.com/company/lefdal-installasjon-as | PASS: exact company/source checked |
| 925201049 | SIDDIS GELATO AS | social_profile.b3242658ef873f5f27e7 | https://www.facebook.com/siddisgelato | PASS: exact company/source checked |
| 925201049 | SIDDIS GELATO AS | social_profile.83f8888e0da55defc5a3 | https://www.instagram.com/siddisgelato | PASS: exact company/source checked |
| 924828099 | ECOFRIC AS | social_profile.32c9f7eda5e0f9c1dc3f | https://www.facebook.com/Ecofric | PASS: exact company/source checked |
| 924828099 | ECOFRIC AS | social_profile.5c286957072172330463 | https://www.instagram.com/ecofric | PASS: exact company/source checked |
| 924828099 | ECOFRIC AS | social_profile.43d6ab301a85aeede593 | https://linkedin.com/company/ecofric | PASS: exact company/source checked |
| 984633718 | BUØY BAKERI & KONDITORI AS | official_website | https://www.buoybakeri.no | PASS: exact company/source checked |
| 987002808 | BRIDGE TECHNOLOGIES CO AS | official_website | https://bridgetech.tv | PASS: exact company/source checked |
| 987002808 | BRIDGE TECHNOLOGIES CO AS | social_profile.310845f10d91b2398a17 | https://www.facebook.com/bridgetechnologies.co.as | PASS: exact company/source checked |
| 935861144 | D-PRODUCTION AS | social_profile.d80b92e7e4637d7f3a4a | https://www.instagram.com/dproduction_as | PASS: exact company/source checked |
| 952785052 | NASJONALT SENTER FOR NORDLANDSHEST /LYNGSHEST AS | official_website | http://www.nsnl.no | PASS: exact company/source checked |
| 976758218 | VS ELEMENT AS | official_website | https://vselement.no | PASS: exact company/source checked |
| 925310492 | CNC NORWAY AS | social_profile.511fd7400e99d9b30bfb | https://www.instagram.com/cncnorwayas | PASS: exact company/source checked |
| 980362779 | RENTHALL AS | official_website | https://renthall.no | PASS: exact company/source checked |
| 960213912 | ROSENLUND BARNEHAGE SA | official_website | https://rosenlundbarnehage.no | PASS: exact company/source checked |
| 960213912 | ROSENLUND BARNEHAGE SA | social_profile.8dfd2496851b6c9fbb1a | https://www.facebook.com/rosenlundbarnehage | PASS: exact company/source checked |
| 960213912 | ROSENLUND BARNEHAGE SA | social_profile.13cef9a06ba0a5568550 | https://www.instagram.com/rosenlund_barnehage | PASS: exact company/source checked |
| 910217127 | FÅLAND HÅNDVERK AS | official_website | https://www.xn--flandhndverk-tcbf.no | PASS: exact company/source checked |
| 990412375 | BERGEN VAKTMESTERTJENESTER AS | dated_item.f40d08eca3b6df36bccf | https://bnv.no/nyheter/hvor-ofte-bor-takrenner-renses/ | PASS: exact company/source checked |
| 990412375 | BERGEN VAKTMESTERTJENESTER AS | dated_item.f8c663479d4e84c0a017 | https://bnv.no/nyheter/hva-koster-drenering-rundt-hus/ | PASS: exact company/source checked |
| 990412375 | BERGEN VAKTMESTERTJENESTER AS | dated_item.340323b78352ff35130c | https://bnv.no/nyheter/hva-gjor-en-vaktmester-i-et-borettslag/ | PASS: exact company/source checked |
| 990412375 | BERGEN VAKTMESTERTJENESTER AS | dated_item.fe34c7f4c00b51f8470b | https://bnv.no/nyheter/helleveien-belegningsstein/ | PASS: exact company/source checked |
| 990412375 | BERGEN VAKTMESTERTJENESTER AS | dated_item.a412ae50a63501df9701 | https://bnv.no/nyheter/apne-jobbsoknad/ | PASS: exact company/source checked |
| 995520982 | HETLY FRITID AS | official_website | https://www.kanobutikken.no | PASS: exact company/source checked |
| 927152630 | HYGGE TANNHELSE AS | official_website | https://www.hyggetannhelse.no | PASS: exact company/source checked |
| 927152630 | HYGGE TANNHELSE AS | social_profile.7299fc16018fb87675a0 | https://www.facebook.com/hyggetannhelse | PASS: exact company/source checked |
| 927152630 | HYGGE TANNHELSE AS | social_profile.15b1dad068b3fba45547 | http://instagram.com/hyggetannhelse | PASS: exact company/source checked |
| 818807562 | WULLUM EIENDOM AS | official_website | https://wullumeiendom.no | PASS: exact company/source checked |
| 910608193 | KAEFER ENERGY AS | official_website | https://kaeferenergy.no | PASS: exact company/source checked |
| 910608193 | KAEFER ENERGY AS | social_profile.bfbb300d4e49327dce56 | https://www.linkedin.com/company/kaefer-energy-as | PASS: exact company/source checked |
| 971521570 | NORDRE FOLLO RENSEANLEGG IKS | official_website | https://nfra.no | PASS: exact company/source checked |

Opened 109; wrong/invalid ownership findings 0. Decision: KEEP.

### 1c refresh safeguards — 20261103T212216230863Z-66cdb5d

| Org | Registered name | Field | Published URL | Review |
|---|---|---|---|---|
| 986739874 | AAS BETONG AS | social_profile.6f188b99ccf6f9021547 | https://www.facebook.com/Aas-Betong-As-576953999078361 | PASS: exact company/source checked |
| 920918204 | STOA AUTOREP AS | social_profile.4a5bbc80815934310b5a | https://www.facebook.com/stoaautorep | PASS: exact company/source checked |
| 823147112 | KN ELEKTRO AS | social_profile.19b491ae8376e3f94d32 | https://www.facebook.com/KN-Elektro-As-104194150969215 | PASS: exact company/source checked |
| 991368000 | RALSTON BAU AS | social_profile.943c0bea445efdf691a2 | https://www.facebook.com/ralstonbau | PASS: exact company/source checked |
| 928657523 | VIVIFY GRUPPEN AS | social_profile.07cfe9a233e8741b1ba5 | https://www.linkedin.com/company/vivify-gruppen | PASS: exact company/source checked |

Opened 5; wrong/invalid ownership findings 0. Decision: KEEP.

### 5 typed sameAs — 20261103T212841589097Z-18d31aa

| Org | Registered name | Field | Published URL | Review |
|---|---|---|---|---|
| 986739874 | AAS BETONG AS | social_profile.6f188b99ccf6f9021547 | https://www.facebook.com/Aas-Betong-As-576953999078361 | PASS: exact company/source checked |
| 920918204 | STOA AUTOREP AS | social_profile.4a5bbc80815934310b5a | https://www.facebook.com/stoaautorep | PASS: exact company/source checked |
| 823147112 | KN ELEKTRO AS | social_profile.19b491ae8376e3f94d32 | https://www.facebook.com/KN-Elektro-As-104194150969215 | PASS: exact company/source checked |
| 991368000 | RALSTON BAU AS | social_profile.943c0bea445efdf691a2 | https://www.facebook.com/ralstonbau | PASS: exact company/source checked |
| 928657523 | VIVIFY GRUPPEN AS | social_profile.07cfe9a233e8741b1ba5 | https://www.linkedin.com/company/vivify-gruppen | PASS: exact company/source checked |

Opened 5; wrong/invalid ownership findings 0. Decision: KEEP.

### 6 original control — 20261104T050326237114Z-0b05b2e

| Org | Registered name | Field | Published URL | Review |
|---|---|---|---|---|
| 986739874 | AAS BETONG AS | social_profile.6f188b99ccf6f9021547 | https://www.facebook.com/Aas-Betong-As-576953999078361 | PASS: exact company/source checked |
| 920918204 | STOA AUTOREP AS | social_profile.4a5bbc80815934310b5a | https://www.facebook.com/stoaautorep | PASS: exact company/source checked |
| 823147112 | KN ELEKTRO AS | social_profile.19b491ae8376e3f94d32 | https://www.facebook.com/KN-Elektro-As-104194150969215 | PASS: exact company/source checked |
| 928657523 | VIVIFY GRUPPEN AS | social_profile.07cfe9a233e8741b1ba5 | https://www.linkedin.com/company/vivify-gruppen | PASS: exact company/source checked |

Opened 4; wrong/invalid ownership findings 0. Decision: CONTROL.

### 6 rejected trial — 20261104T051103339719Z-0b05b2e

| Org | Registered name | Field | Published URL | Review |
|---|---|---|---|---|
| 991247610 | ROLIDBAKKEN FUS BARNEHAGE AS | official_website | https://fus.no | PASS: exact registered company and source checked |
| 986739874 | AAS BETONG AS | social_profile.6f188b99ccf6f9021547 | https://www.facebook.com/Aas-Betong-As-576953999078361 | PASS: exact registered company and source checked |
| 926698435 | UPPSTAD VVS AVDELING HOVDEN AS | official_website | https://utdanning.no | FAIL: third-party directory falsely presented as official website |
| 911683237 | SAMEIET KIRKEGATEN 36B | official_website | https://vat-validation.com | FAIL: third-party directory falsely presented as official website |
| 920918204 | STOA AUTOREP AS | social_profile.4a5bbc80815934310b5a | https://www.facebook.com/stoaautorep | PASS: exact registered company and source checked |
| 823147112 | KN ELEKTRO AS | social_profile.19b491ae8376e3f94d32 | https://www.facebook.com/KN-Elektro-As-104194150969215 | PASS: exact registered company and source checked |
| 991368000 | RALSTON BAU AS | official_website | https://ralstonbau.com | PASS: exact registered company and source checked |
| 991368000 | RALSTON BAU AS | social_profile.943c0bea445efdf691a2 | https://www.facebook.com/ralstonbau | PASS: exact registered company and source checked |
| 928657523 | VIVIFY GRUPPEN AS | social_profile.07cfe9a233e8741b1ba5 | https://www.linkedin.com/company/vivify-gruppen | PASS: exact registered company and source checked |

Opened 9; wrong/invalid ownership findings 2. Decision: ROLLED BACK.

### 6 first directory guard — 20261104T052607204480Z-47a295c

| Org | Registered name | Field | Published URL | Review |
|---|---|---|---|---|
| 986739874 | AAS BETONG AS | social_profile.6f188b99ccf6f9021547 | https://www.facebook.com/Aas-Betong-As-576953999078361 | PASS: exact company/source checked |
| 920918204 | STOA AUTOREP AS | social_profile.4a5bbc80815934310b5a | https://www.facebook.com/stoaautorep | PASS: exact company/source checked |
| 823147112 | KN ELEKTRO AS | social_profile.19b491ae8376e3f94d32 | https://www.facebook.com/KN-Elektro-As-104194150969215 | PASS: exact company/source checked |
| 991368000 | RALSTON BAU AS | official_website | https://ralstonbau.com | PASS: exact company/source checked |
| 991368000 | RALSTON BAU AS | social_profile.943c0bea445efdf691a2 | https://www.facebook.com/ralstonbau | PASS: exact company/source checked |
| 928657523 | VIVIFY GRUPPEN AS | social_profile.07cfe9a233e8741b1ba5 | https://www.linkedin.com/company/vivify-gruppen | PASS: exact company/source checked |

Opened 6; wrong/invalid ownership findings 0. Decision: KEEP.

### 6 rejected LEI retrial — 20261104T054207443662Z-e33b951

| Org | Registered name | Field | Published URL | Review |
|---|---|---|---|---|
| 991247610 | ROLIDBAKKEN FUS BARNEHAGE AS | official_website | https://fus.no | PASS: exact registered company and source checked |
| 986739874 | AAS BETONG AS | social_profile.6f188b99ccf6f9021547 | https://www.facebook.com/Aas-Betong-As-576953999078361 | PASS: exact registered company and source checked |
| 920918204 | STOA AUTOREP AS | social_profile.4a5bbc80815934310b5a | https://www.facebook.com/stoaautorep | PASS: exact registered company and source checked |
| 918270205 | GILJEHOLMEN AS | official_website | https://nordlei.no | FAIL: third-party LEI directory, not an owned company website |
| 991368000 | RALSTON BAU AS | social_profile.943c0bea445efdf691a2 | https://www.facebook.com/ralstonbau | PASS: exact registered company and source checked |
| 928657523 | VIVIFY GRUPPEN AS | social_profile.07cfe9a233e8741b1ba5 | https://www.linkedin.com/company/vivify-gruppen | PASS: exact registered company and source checked |

Opened 6; wrong/invalid ownership findings 1. Decision: ROLLED BACK.

### 6 LEI-record ownership guard — 20261104T055653185175Z-44bf7cb

| Org | Registered name | Field | Published URL | Review |
|---|---|---|---|---|
| 986739874 | AAS BETONG AS | social_profile.6f188b99ccf6f9021547 | https://www.facebook.com/Aas-Betong-As-576953999078361 | PASS: exact company/source checked |
| 920918204 | STOA AUTOREP AS | social_profile.4a5bbc80815934310b5a | https://www.facebook.com/stoaautorep | PASS: exact company/source checked |
| 823147112 | KN ELEKTRO AS | social_profile.19b491ae8376e3f94d32 | https://www.facebook.com/KN-Elektro-As-104194150969215 | PASS: exact company/source checked |
| 991368000 | RALSTON BAU AS | social_profile.943c0bea445efdf691a2 | https://www.facebook.com/ralstonbau | PASS: exact company/source checked |
| 928657523 | VIVIFY GRUPPEN AS | social_profile.07cfe9a233e8741b1ba5 | https://www.linkedin.com/company/vivify-gruppen | PASS: exact company/source checked |

Opened 5; wrong/invalid ownership findings 0. Decision: KEEP.

### 6 reapplied Brave — 20261104T060955663646Z-87ab7ab

| Org | Registered name | Field | Published URL | Review |
|---|---|---|---|---|
| 991247610 | ROLIDBAKKEN FUS BARNEHAGE AS | official_website | https://fus.no | PASS: exact company/source checked |
| 986739874 | AAS BETONG AS | social_profile.6f188b99ccf6f9021547 | https://www.facebook.com/Aas-Betong-As-576953999078361 | PASS: exact company/source checked |
| 920918204 | STOA AUTOREP AS | social_profile.4a5bbc80815934310b5a | https://www.facebook.com/stoaautorep | PASS: exact company/source checked |
| 823147112 | KN ELEKTRO AS | social_profile.19b491ae8376e3f94d32 | https://www.facebook.com/KN-Elektro-As-104194150969215 | PASS: exact company/source checked |
| 991368000 | RALSTON BAU AS | social_profile.943c0bea445efdf691a2 | https://www.facebook.com/ralstonbau | PASS: exact company/source checked |
| 928657523 | VIVIFY GRUPPEN AS | social_profile.07cfe9a233e8741b1ba5 | https://www.linkedin.com/company/vivify-gruppen | PASS: exact company/source checked |

Opened 6; wrong/invalid ownership findings 0. Decision: KEEP.

### Scale checkpoint, metadata exception — 20261104T061829762243Z-6213840

| Org | Registered name | Field | Published URL | Review |
|---|---|---|---|---|
| 986739874 | AAS BETONG AS | social_profile.6f188b99ccf6f9021547 | https://www.facebook.com/Aas-Betong-As-576953999078361 | PASS: exact registered identity and source checked |
| 920918204 | STOA AUTOREP AS | social_profile.4a5bbc80815934310b5a | https://www.facebook.com/stoaautorep | PASS: exact registered identity and source checked |
| 991368000 | RALSTON BAU AS | social_profile.943c0bea445efdf691a2 | https://www.facebook.com/ralstonbau | PASS: exact registered identity and source checked |
| 928657523 | VIVIFY GRUPPEN AS | social_profile.07cfe9a233e8741b1ba5 | https://www.linkedin.com/company/vivify-gruppen | PASS: exact registered identity and source checked |
| 936629466 | CLOSVA AS | social_profile.746d50370f5da22298d3 | https://www.linkedin.com/company/closva | PASS: exact registered identity and source checked |
| 924912758 | BORG BIERSTUBE AS | social_profile.4c67ba313eda64e60646 | https://www.instagram.com/borgbierstube | PASS: exact registered identity and source checked |
| 924912758 | BORG BIERSTUBE AS | social_profile.0c59d28066b5c16e3eec | https://www.facebook.com/borgbierstube | PASS: exact registered identity and source checked |
| 932448459 | ROMERIKE VVS AS | social_profile.d44ae658e298407818b9 | https://www.instagram.com/romerike_vvs | PASS: exact registered identity and source checked |
| 893948112 | NORSK PUBLIKUMSUTVIKLING | social_profile.958eeb99bc8fb420e436 | https://www.facebook.com/NorskPublikumsutvikling.AudiencesNorway | PASS: exact registered identity and source checked |
| 893948112 | NORSK PUBLIKUMSUTVIKLING | social_profile.8bab7e90db4089cdf17f | https://www.instagram.com/norskpublikumsutvikling | PASS: exact registered identity and source checked |
| 968386085 | LOFOTPOSTEN AS | social_profile.18827a4b63ceebca6fbd | https://x.com/lofotposten | PASS: exact registered identity and source checked |
| 968386085 | LOFOTPOSTEN AS | social_profile.c0f4fd23d86e444b326b | https://www.instagram.com/lofotposten | PASS: exact registered identity and source checked |
| 968386085 | LOFOTPOSTEN AS | social_profile.2ab01462d39d2bd0a770 | https://www.facebook.com/lofotposten | PASS: exact registered identity and source checked |
| 926490060 | CONTROL SOLUTIONS AS | social_profile.d6ed8e08a0a64f44813c | https://www.facebook.com/ControlSolutionsAS | PASS: exact registered identity and source checked |
| 987895276 | CONPLAN AS | social_profile.629a70b1abecf554d0cc | https://www.facebook.com/Conplan-AS-509721459118772 | PASS: exact registered identity and source checked |
| 934982762 | ARKIDAL AS | social_profile.dfe21c80c809e08f1ffb | https://www.youtube.com/@arkidal | PASS: exact registered identity and source checked |
| 934982762 | ARKIDAL AS | social_profile.f3c46f3da81d2961092d | https://www.facebook.com/arkidal | PASS: exact registered identity and source checked |
| 998077028 | INNOVATION SUPPORT AS | social_profile.fb88a1126bd44a5491ed | https://www.linkedin.com/company/innovation-support-as | PASS: exact registered identity and source checked |
| 998077028 | INNOVATION SUPPORT AS | social_profile.879e94b8d418b4b7b866 | https://www.facebook.com/InnovationSupport | PASS: exact registered identity and source checked |
| 990012288 | TB MASKIN AS | social_profile.01174da1e1bd6a813f9c | https://www.facebook.com/pages/TB-Maskin-As/455200387968353 | PASS: exact registered identity and source checked |
| 990012288 | TB MASKIN AS | social_profile.126746e2b1c39291086e | https://www.instagram.com/tbmaskin | PASS: exact registered identity and source checked |
| 990012288 | TB MASKIN AS | social_profile.f1a2ea5e9c5099683f11 | https://www.linkedin.com/company/tbmaskin | PASS: exact registered identity and source checked |
| 926065173 | THE LAB RETRIEVER AS | social_profile.7619557adb370bbebaed | https://www.facebook.com/The-Lab-Retriever-107894350774301 | PASS: exact registered identity and source checked |
| 926065173 | THE LAB RETRIEVER AS | social_profile.c3d54970de735857fb6a | https://www.instagram.com/thelabretriever | PASS: exact registered identity and source checked |
| 938092516 | OSLO CHAMBER OF COMMERCE | social_profile.9d8e1de3667fa506b055 | https://www.linkedin.com/company/oslo-chamber-of-commerce | PASS: exact registered identity and source checked |
| 938092516 | OSLO CHAMBER OF COMMERCE | social_profile.ba2cfa7bb751aee963a5 | https://www.instagram.com/oslochamberofcommerce | PASS: exact registered identity and source checked |
| 918486666 | ANTISINK AS | social_profile.7f3132bba63574468739 | https://no.linkedin.com/company/antisink-as | PASS: exact registered identity and source checked |
| 982388449 | IDESTOVA AS | social_profile.c4b91b95c9085ccd16b6 | https://www.facebook.com/Idestova-As-293922170749469 | PASS: exact registered identity and source checked |
| 982388449 | IDESTOVA AS | social_profile.fe5f389f36aa61edf799 | https://instagram.com/idestova | PASS: exact registered identity and source checked |
| 982388449 | IDESTOVA AS | social_profile.e4f185ea4bc300f21707 | https://www.facebook.com/idestova | PASS: exact registered identity and source checked |
| 920358411 | LARSZACHARIASSEN AS | social_profile.389e9e2abacc41593c67 | https://www.instagram.com/larszachariassen | PASS: exact registered identity and source checked |
| 971558415 | DANSEINFORMASJONEN STI | social_profile.849b53a48559cc37adac | https://www.instagram.com/danseinformasjonen | PASS: exact registered identity and source checked |
| 971558415 | DANSEINFORMASJONEN STI | social_profile.438117087531d9623489 | https://www.facebook.com/danseinformasjonen | PASS: exact registered identity and source checked |
| 821962242 | LAKSESYSTEMER AS | social_profile.8274a67d0ace290d26fa | https://www.facebook.com/laksesystemer | PASS: exact registered identity and source checked |
| 968545337 | LEFDAL INSTALLASJON AS | social_profile.f1c3874f5818e83511e7 | https://no.linkedin.com/company/lefdal-installasjon-as | PASS: exact registered identity and source checked |
| 925201049 | SIDDIS GELATO AS | social_profile.b3242658ef873f5f27e7 | https://www.facebook.com/siddisgelato | PASS: exact registered identity and source checked |
| 925201049 | SIDDIS GELATO AS | social_profile.83f8888e0da55defc5a3 | https://www.instagram.com/siddisgelato | PASS: exact registered identity and source checked |
| 924828099 | ECOFRIC AS | social_profile.32c9f7eda5e0f9c1dc3f | https://www.facebook.com/Ecofric | PASS: exact registered identity and source checked |
| 924828099 | ECOFRIC AS | social_profile.5c286957072172330463 | https://www.instagram.com/ecofric | PASS: exact registered identity and source checked |
| 924828099 | ECOFRIC AS | social_profile.43d6ab301a85aeede593 | https://linkedin.com/company/ecofric | PASS: exact registered identity and source checked |
| 987002808 | BRIDGE TECHNOLOGIES CO AS | social_profile.310845f10d91b2398a17 | https://www.facebook.com/bridgetechnologies.co.as | PASS: exact registered identity and source checked |
| 935861144 | D-PRODUCTION AS | social_profile.d80b92e7e4637d7f3a4a | https://www.instagram.com/dproduction_as | PASS: exact registered identity and source checked |
| 952785052 | NASJONALT SENTER FOR NORDLANDSHEST /LYNGSHEST AS | official_website | https://www.nsnl.no | PASS: exact registered identity and source checked |
| 960213912 | ROSENLUND BARNEHAGE SA | social_profile.8dfd2496851b6c9fbb1a | https://www.facebook.com/rosenlundbarnehage | PASS: exact registered identity and source checked |
| 960213912 | ROSENLUND BARNEHAGE SA | social_profile.13cef9a06ba0a5568550 | https://www.instagram.com/rosenlund_barnehage | PASS: exact registered identity and source checked |
| 927152630 | HYGGE TANNHELSE AS | social_profile.7299fc16018fb87675a0 | https://www.facebook.com/hyggetannhelse | PASS: exact registered identity and source checked |
| 927152630 | HYGGE TANNHELSE AS | social_profile.15b1dad068b3fba45547 | http://instagram.com/hyggetannhelse | PASS: exact registered identity and source checked |
| 910608193 | KAEFER ENERGY AS | social_profile.bfbb300d4e49327dce56 | https://www.linkedin.com/company/kaefer-energy-as | PASS: exact registered identity and source checked |

Opened 48; wrong/invalid ownership findings 0. Decision: CHECKPOINT - regression found.

### Malformed social URL safeguard — 20261104T064156705198Z-098dc33

| Org | Registered name | Field | Published URL | Review |
|---|---|---|---|---|
| 986739874 | AAS BETONG AS | social_profile.6f188b99ccf6f9021547 | https://www.facebook.com/Aas-Betong-As-576953999078361 | PASS: exact company/source checked |
| 920918204 | STOA AUTOREP AS | social_profile.4a5bbc80815934310b5a | https://www.facebook.com/stoaautorep | PASS: exact company/source checked |
| 823147112 | KN ELEKTRO AS | social_profile.19b491ae8376e3f94d32 | https://www.facebook.com/KN-Elektro-As-104194150969215 | PASS: exact company/source checked |
| 991368000 | RALSTON BAU AS | social_profile.943c0bea445efdf691a2 | https://www.facebook.com/ralstonbau | PASS: exact company/source checked |
| 928657523 | VIVIFY GRUPPEN AS | social_profile.07cfe9a233e8741b1ba5 | https://www.linkedin.com/company/vivify-gruppen | PASS: exact company/source checked |

Opened 5; wrong/invalid ownership findings 0. Decision: KEEP.

### Final scale, search OFF — 20261104T064749747167Z-c0da0a1

| Org | Registered name | Field | Published URL | Review |
|---|---|---|---|---|
| 986739874 | AAS BETONG AS | social_profile.6f188b99ccf6f9021547 | https://www.facebook.com/Aas-Betong-As-576953999078361 | PASS: exact registered company/source checked |
| 920918204 | STOA AUTOREP AS | social_profile.4a5bbc80815934310b5a | https://www.facebook.com/stoaautorep | PASS: exact registered company/source checked |
| 823147112 | KN ELEKTRO AS | official_website | https://knelektro.no | PASS: exact registered company/source checked |
| 823147112 | KN ELEKTRO AS | social_profile.19b491ae8376e3f94d32 | https://www.facebook.com/KN-Elektro-As-104194150969215 | PASS: exact registered company/source checked |
| 991368000 | RALSTON BAU AS | social_profile.943c0bea445efdf691a2 | https://www.facebook.com/ralstonbau | PASS: exact registered company/source checked |
| 928657523 | VIVIFY GRUPPEN AS | social_profile.07cfe9a233e8741b1ba5 | https://www.linkedin.com/company/vivify-gruppen | PASS: exact registered company/source checked |
| 936629466 | CLOSVA AS | social_profile.746d50370f5da22298d3 | https://www.linkedin.com/company/closva | PASS: exact registered company/source checked |
| 924912758 | BORG BIERSTUBE AS | social_profile.4c67ba313eda64e60646 | https://www.instagram.com/borgbierstube | PASS: exact registered company/source checked |
| 924912758 | BORG BIERSTUBE AS | social_profile.0c59d28066b5c16e3eec | https://www.facebook.com/borgbierstube | PASS: exact registered company/source checked |
| 932448459 | ROMERIKE VVS AS | social_profile.d44ae658e298407818b9 | https://www.instagram.com/romerike_vvs | PASS: exact registered company/source checked |
| 893948112 | NORSK PUBLIKUMSUTVIKLING | social_profile.958eeb99bc8fb420e436 | https://www.facebook.com/NorskPublikumsutvikling.AudiencesNorway | PASS: exact registered company/source checked |
| 893948112 | NORSK PUBLIKUMSUTVIKLING | social_profile.8bab7e90db4089cdf17f | https://www.instagram.com/norskpublikumsutvikling | PASS: exact registered company/source checked |
| 968386085 | LOFOTPOSTEN AS | social_profile.18827a4b63ceebca6fbd | https://x.com/lofotposten | PASS: exact registered company/source checked |
| 968386085 | LOFOTPOSTEN AS | social_profile.c0f4fd23d86e444b326b | https://www.instagram.com/lofotposten | PASS: exact registered company/source checked |
| 968386085 | LOFOTPOSTEN AS | social_profile.2ab01462d39d2bd0a770 | https://www.facebook.com/lofotposten | PASS: exact registered company/source checked |
| 926490060 | CONTROL SOLUTIONS AS | social_profile.d6ed8e08a0a64f44813c | https://www.facebook.com/ControlSolutionsAS | PASS: exact registered company/source checked |
| 987895276 | CONPLAN AS | social_profile.629a70b1abecf554d0cc | https://www.facebook.com/Conplan-AS-509721459118772 | PASS: exact registered company/source checked |
| 934982762 | ARKIDAL AS | social_profile.dfe21c80c809e08f1ffb | https://www.youtube.com/@arkidal | PASS: exact registered company/source checked |
| 934982762 | ARKIDAL AS | social_profile.f3c46f3da81d2961092d | https://www.facebook.com/arkidal | PASS: exact registered company/source checked |
| 998077028 | INNOVATION SUPPORT AS | social_profile.fb88a1126bd44a5491ed | https://www.linkedin.com/company/innovation-support-as | PASS: exact registered company/source checked |
| 998077028 | INNOVATION SUPPORT AS | social_profile.879e94b8d418b4b7b866 | https://www.facebook.com/InnovationSupport | PASS: exact registered company/source checked |
| 942393679 | HARVELAND AS | official_website | https://harveland-as.no | PASS: exact registered company/source checked |
| 942393679 | HARVELAND AS | social_profile.274b76ad29764cfd8e8d | https://www.facebook.com/HarvelandAS | PASS: exact registered company/source checked |
| 990012288 | TB MASKIN AS | social_profile.01174da1e1bd6a813f9c | https://www.facebook.com/pages/TB-Maskin-As/455200387968353 | PASS: exact registered company/source checked |
| 990012288 | TB MASKIN AS | social_profile.126746e2b1c39291086e | https://www.instagram.com/tbmaskin | PASS: exact registered company/source checked |
| 990012288 | TB MASKIN AS | social_profile.f1a2ea5e9c5099683f11 | https://www.linkedin.com/company/tbmaskin | PASS: exact registered company/source checked |
| 926065173 | THE LAB RETRIEVER AS | social_profile.7619557adb370bbebaed | https://www.facebook.com/The-Lab-Retriever-107894350774301 | PASS: exact registered company/source checked |
| 926065173 | THE LAB RETRIEVER AS | social_profile.c3d54970de735857fb6a | https://www.instagram.com/thelabretriever | PASS: exact registered company/source checked |
| 938092516 | OSLO CHAMBER OF COMMERCE | social_profile.9d8e1de3667fa506b055 | https://www.linkedin.com/company/oslo-chamber-of-commerce | PASS: exact registered company/source checked |
| 938092516 | OSLO CHAMBER OF COMMERCE | social_profile.ba2cfa7bb751aee963a5 | https://www.instagram.com/oslochamberofcommerce | PASS: exact registered company/source checked |
| 918486666 | ANTISINK AS | social_profile.7f3132bba63574468739 | https://no.linkedin.com/company/antisink-as | PASS: exact registered company/source checked |
| 982388449 | IDESTOVA AS | social_profile.c4b91b95c9085ccd16b6 | https://www.facebook.com/Idestova-As-293922170749469 | PASS: exact registered company/source checked |
| 982388449 | IDESTOVA AS | social_profile.fe5f389f36aa61edf799 | https://instagram.com/idestova | PASS: exact registered company/source checked |
| 982388449 | IDESTOVA AS | social_profile.e4f185ea4bc300f21707 | https://www.facebook.com/idestova | PASS: exact registered company/source checked |
| 920358411 | LARSZACHARIASSEN AS | social_profile.389e9e2abacc41593c67 | https://www.instagram.com/larszachariassen | PASS: exact registered company/source checked |
| 971558415 | DANSEINFORMASJONEN STI | social_profile.849b53a48559cc37adac | https://www.instagram.com/danseinformasjonen | PASS: exact registered company/source checked |
| 971558415 | DANSEINFORMASJONEN STI | social_profile.438117087531d9623489 | https://www.facebook.com/danseinformasjonen | PASS: exact registered company/source checked |
| 821962242 | LAKSESYSTEMER AS | social_profile.8274a67d0ace290d26fa | https://www.facebook.com/laksesystemer | PASS: exact registered company/source checked |
| 968545337 | LEFDAL INSTALLASJON AS | social_profile.f1c3874f5818e83511e7 | https://no.linkedin.com/company/lefdal-installasjon-as | PASS: exact registered company/source checked |
| 925201049 | SIDDIS GELATO AS | social_profile.b3242658ef873f5f27e7 | https://www.facebook.com/siddisgelato | PASS: exact registered company/source checked |
| 925201049 | SIDDIS GELATO AS | social_profile.83f8888e0da55defc5a3 | https://www.instagram.com/siddisgelato | PASS: exact registered company/source checked |
| 924828099 | ECOFRIC AS | social_profile.32c9f7eda5e0f9c1dc3f | https://www.facebook.com/Ecofric | PASS: exact registered company/source checked |
| 924828099 | ECOFRIC AS | social_profile.5c286957072172330463 | https://www.instagram.com/ecofric | PASS: exact registered company/source checked |
| 924828099 | ECOFRIC AS | social_profile.43d6ab301a85aeede593 | https://linkedin.com/company/ecofric | PASS: exact registered company/source checked |
| 987002808 | BRIDGE TECHNOLOGIES CO AS | social_profile.310845f10d91b2398a17 | https://www.facebook.com/bridgetechnologies.co.as | PASS: exact registered company/source checked |
| 935861144 | D-PRODUCTION AS | social_profile.d80b92e7e4637d7f3a4a | https://www.instagram.com/dproduction_as | PASS: exact registered company/source checked |
| 925310492 | CNC NORWAY AS | official_website | https://cncnorwayas.no | PASS: exact registered company/source checked |
| 925310492 | CNC NORWAY AS | social_profile.511fd7400e99d9b30bfb | https://www.instagram.com/cncnorwayas | PASS: exact registered company/source checked |
| 960213912 | ROSENLUND BARNEHAGE SA | social_profile.8dfd2496851b6c9fbb1a | https://www.facebook.com/rosenlundbarnehage | PASS: exact registered company/source checked |
| 960213912 | ROSENLUND BARNEHAGE SA | social_profile.13cef9a06ba0a5568550 | https://www.instagram.com/rosenlund_barnehage | PASS: exact registered company/source checked |
| 988456292 | STYREGUIDEN AS | official_website | https://www.styreguiden.no | PASS: exact registered company/source checked |
| 927152630 | HYGGE TANNHELSE AS | social_profile.7299fc16018fb87675a0 | https://www.facebook.com/hyggetannhelse | PASS: exact registered company/source checked |
| 927152630 | HYGGE TANNHELSE AS | social_profile.15b1dad068b3fba45547 | http://instagram.com/hyggetannhelse | PASS: exact registered company/source checked |
| 910608193 | KAEFER ENERGY AS | social_profile.bfbb300d4e49327dce56 | https://www.linkedin.com/company/kaefer-energy-as | PASS: exact registered company/source checked |

Opened 54; wrong/invalid ownership findings 0. Decision: FINAL VALIDATION.

## NAV freshness and proposal-only submission plan


Proposal only, 2026-11-04. No index rebuild, age-limit change or fallback implementation has been run in S5. The bundled gzip remains unchanged.

The bundled `src/signalpost/data/nav_index.json.gz` declares `built_at=2026-10-14T04:26:40.758720Z`, schema 1, 9,015 active ads, 5,769 employers, zero failed details, 6,791 disk-seeded and 2,224 freshly fetched entries. Its compressed size is 403,768 bytes.

`Config.nav_index_max_age_days=21`. `sources/nav_index.py:load` validates schema/counts/cursor, calculates UTC age and raises `index_stale` when age exceeds 21 days. `sources/nav.py:collect` records `full_feed_fallback` and the rejection reason instead of using the declared-index path. Expiry was **2026-11-04 04:26:40.758720 UTC**, or **09:56:40.758720 IST**.

| Run | Index age at execution start | NAV mode | NAV seconds | NAV requests | Total wall seconds |
|---|---|---|---:|---:|---:|
| Earlier 100, 18d31aa | 20.709732 days | declared_index | 28.891 | 52 | 53.128 |
| Current free 100, 44bf7cb | 21.062644 days (21d 1h 30m) | full_feed_fallback; index_stale | 298.421 | 394 | 344.674 |
| Pre-fix 1000 checkpoint, 6213840 | 21.077651 days | full_feed_fallback; index_stale | 560.188 | 507 | 807.587 |
| Final-code 1000, c0da0a1 | 21.098021 days (21d 2h 21m) | full_feed_fallback; index_stale | 363.188 | 508 | 472.309 |

The full-feed control traversed 362 pages versus 41 forward-feed pages in the earlier declared-index run. Feed transport completed. `reason=nav_detail_cap` and eight incomplete companies still mean that complete transport must not be described as complete company-level hiring coverage. No HTTP 429s occurred in this control. The pre-fix scale checkpoint took 807.587s (NAV 560.188s/507 requests/362 pages). It exposed a separate CNC Norway malformed-social-metadata exception. After a narrow guard and its tests/100-company benchmark, the final-code 1000 run completed: **exit 0, 1000 envelopes, 472.309s**, or **19.68% of 2400s**, below the required 1200s. Search OFF; 6989 total requests; zero deadlines; zero handled/unhandled exceptions. NAV used **363.188s and 508 requests**: 363 feed pages, 144 detail attempts (141 successful) plus token/control traffic; feed time 360.734s. Both runs used full_feed_fallback/index_stale with the same bundled index and unchanged NAV behavior. Their transport durations differ; the faster final run must not be attributed to a NAV optimization. In both, 73 companies remained hiring-incomplete with nav_detail_cap despite completed feed transport. The sole HTTP429 was Elkjop robots.txt, not NAV/accounts. The earlier declared-index scale checkpoint took 291.317s on the previous date. The measured final result passes today’s timing gate, not a future 1100-company guarantee.

## Rebuild before submission (not executed)

1. Within 24 hours before submission, use a **new empty checkpoint directory** and disable old disk seeding. Run the existing resumable builder at its supported concurrency of four, preserving NAV authentication/politeness and rate-limit handling. Example command, **not executed**:

   ```text
   uv run python scripts/build_nav_index.py --no-seed-from-disk --state-dir bench/cache/nav-index-submission --output bench/cache/nav-index-fresh.json.gz --report bench/cache/nav-index-build-report.json --concurrency 4
   ```

2. If a build is interrupted, resume its checkpoint and require a finished feed, `failed_details=0`, consistent ad/employer counts, valid source/cursor/schema, and an accurately recorded build timestamp. Never just edit `built_at`, relax the 21-day limit, or use the historical-snapshot override as a freshness fix.
3. Validate with `nav_index.load`, record SHA-256 and provenance/build counts, then review and replace the bundled artifact in a separate authorized change. Run tests and a frozen 1,100-company search-OFF benchmark with fresh state. Inspect employer/subunit matching, live INACTIVE handling, completeness and raw source failures. Preserve current live detail verification; an index is discovery metadata, not publication evidence.
4. Add a pre-submission freshness check/warning and rebuild reminder (for example, warn after 14 days). A recent bundle improves the next run; it does not make future stale runs disappear.

## Make later-date fallback resilient (future implementation)

1. Separate **structurally valid stale seed** from **fresh accepted index**. For a valid stale seed only, attempt a completed forward-feed catch-up from its validated cursor, reconcile every changed/INACTIVE header and fetch current candidate details. Publish only after the necessary feed/detail completeness checks pass. Do not silently accept stale entries as current. The existing declared-index path already has forward traversal and overlapping detail work; reuse those checks rather than inventing a weaker path.
2. If the seed is missing, malformed, incomplete, or its cursor cannot be continued, retain honest full-feed fallback. Measure this cold path separately. It already shares one traversal across the cohort and overlaps details with headers; those are not proposed new optimizations.
3. Profile full-feed transport versus header matching/JSON work and details. Preserve bounded memory, existing rare-token/name filtering, per-host limits, TLS, Retry-After and per-company incompleteness. Increase concurrency only if measured source headroom supports it. Do not shorten the feed or suppress errors to make a timing number look better.
4. Address the **512-page cap**: the current archive already needs 363 pages, so later feed growth can truncate hiring coverage even before the 900-second NAV time cap. Prefer safe cursor catch-up; for the unavoidable cold path, make page/time limits evidence-based and report an incomplete traversal honestly.
5. Gate the future change on the same frozen 1,100-company inputs in fresh-index, forced-stale-valid-seed, missing-index and malformed-index cases. Require exit 0, 1,100 envelopes, zero deadline hits, preserved ownership/employer checks and explicit completeness diagnostics. Target **<1,200 seconds end to end**, leaving at least half the 2,400-second official budget. Record NAV/registry/website/output timings, HTTP/429/timeout counts and accounts/jobs state changes; a projection is not a substitute for this measurement.

No future-date runtime guarantee is claimed before those measurements. Final S5 uses the existing bundled index and existing fallback unchanged, with search OFF.

## Git log with authors

```text
4b75753 Manish Rahul <manishrahul1705@gmail.com> Record final S5 scale validation and NAV freshness diagnosis
c0da0a1 Manish Rahul <manishrahul1705@gmail.com> Record malformed-social safeguard benchmark and source review
098dc33 Manish Rahul <manishrahul1705@gmail.com> Ignore malformed social metadata without failing verified websites
6213840 Manish Rahul <manishrahul1705@gmail.com> Record guarded Brave benchmark and zero incremental coverage
87ab7ab Manish Rahul <manishrahul1705@gmail.com> Add explicitly opted-in active-company Brave discovery and benchmark switch
f763b5b Manish Rahul <manishrahul1705@gmail.com> Record isolated LEI-record guard benchmark and full social review
44bf7cb Manish Rahul <manishrahul1705@gmail.com> Reject LEI registry records as official company websites
2c5ddbd Manish Rahul <manishrahul1705@gmail.com> Withdraw search retrial after LEI registry ownership false positive
e33b951 Manish Rahul <manishrahul1705@gmail.com> Add explicitly opted-in active-company Brave discovery and benchmark switch
050ab4e Manish Rahul <manishrahul1705@gmail.com> Record isolated directory guard benchmark and source review
47a295c Manish Rahul <manishrahul1705@gmail.com> Reject copied registry entries on education and VAT directories
312266a Manish Rahul <manishrahul1705@gmail.com> Withdraw Brave trial after directory ownership false positives
0b05b2e Manish Rahul <manishrahul1705@gmail.com> Record prepared Brave gate and S5 interim benchmark evidence
2801e02 Manish Rahul <manishrahul1705@gmail.com> Add explicitly opted-in active-company Brave discovery and benchmark switch
35dc089 Manish Rahul <manishrahul1705@gmail.com> Record typed sameAs benchmark and full social review
18d31aa Manish Rahul <manishrahul1705@gmail.com> Attribute JSON-LD sameAs only to verified company organizations
49a042d Manish Rahul <manishrahul1705@gmail.com> Record final social safeguard benchmark and precise removal reasons
66cdb5d Manish Rahul <manishrahul1705@gmail.com> Enforce social attribution after refresh and across every observed context
21396c8 Manish Rahul <manishrahul1705@gmail.com> Record Wikidata scale summary and full source-item review
e8f8467 Manish Rahul <manishrahul1705@gmail.com> Record Wikidata benchmark and complete social review
e9ebb73 Manish Rahul <manishrahul1705@gmail.com> Add batched exact-organisation Wikidata website and social discovery
244c2df Manish Rahul <manishrahul1705@gmail.com> Record website loss diagnosis and unchanged-runtime benchmark
c1ca5df Manish Rahul <manishrahul1705@gmail.com> Add read-only website loss-stage diagnosis
a0c5a21 Manish Rahul <manishrahul1705@gmail.com> Record restored website budget benchmark and full social review
3240e5b Manish Rahul <manishrahul1705@gmail.com> Reapply "Raise default website request budgets to fourteen and eighteen"
bac555b Manish Rahul <manishrahul1705@gmail.com> Record observed-profile safeguard benchmark
d41ea10 Manish Rahul <manishrahul1705@gmail.com> Suppress profiles observed across companies and language-scoped templates
2c1f475 Manish Rahul <manishrahul1705@gmail.com> Record restored ownership coverage and full social review
4cd4892 Manish Rahul <manishrahul1705@gmail.com> Reapply "Require strict complete website ownership proof"
5c3cd56 Manish Rahul <manishrahul1705@gmail.com> Record full social attribution benchmark review
3c98640 Manish Rahul <manishrahul1705@gmail.com> Require company-specific social attribution and drop shared profiles
```
