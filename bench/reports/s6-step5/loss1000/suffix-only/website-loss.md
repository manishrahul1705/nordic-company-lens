# Website loss diagnosis

This is a read-only analysis of saved run diagnostics. No network requests or behavior changes.

## primary — 1000 companies

Available: 73; missing: 927.

| Stop reason | Companies |
|---|---:|
| TLS-connect failure | 532 |
| all candidates DNS-missing | 134 |
| ambiguous (name-only or competing candidates) | 113 |
| proof conflict (other orgnr) | 48 |
| robots or blocked | 36 |
| budget exhausted | 32 |
| fetched but no proof | 15 |
| no candidates generated | 10 |
| no retained successful company page | 7 |

Reasons are exclusive stop buckets from recorded candidate diagnostics, not inferred exhaustive absence. Budget includes request/deadline limits. DNS/transient TLS failures are grouped conservatively when low-level transport messages are unavailable.

### TLS-connect failure

| Company | Name | Candidate domains |
|---|---|---|
| 918049215 | MENSTAD NÆRINGSPARK AS | menstadnaeringspark.no, menstadnaeringspark-as.no, menstadnaeringsparkas.no, menstadnaeringspark.as, menstadnaeringspark.com, menstad-naeringspark.no, menstad-naeringspark-as.no, menstad-naeringsparkas.no, menstad-naeringspark.as, menstad-naeringspark.com, menstadnaringspark.no, menstadnaringspark-as.no, menstadnaringsparkas.no, menstadnaringspark.as, menstadnaringspark.com, menstad-naringspark.no, menstad-naringspark-as.no, menstad-naringsparkas.no, menstad-naringspark.as, menstad-naringspark.com, xn--menstadnringspark-yrb.no, xn--menstadnringspark-yrb.com, xn--menstad-nringspark-wub.no, xn--menstad-nringspark-wub.com |
| 916049153 | SJØL INVEST AS | sjolinvest.no, sjolinvest-as.no, sjolinvestas.no, sjolinvest.as, sjolinvest.com, sjol-invest.no, sjol-invest-as.no, sjol-investas.no, sjol-invest.as, sjol-invest.com, sjoelinvest.no, sjoelinvest-as.no, sjoelinvestas.no, sjoelinvest.as, sjoelinvest.com, sjoel-invest.no, sjoel-invest-as.no, sjoel-investas.no, sjoel-invest.as, sjoel-invest.com, xn--sjlinvest-m8a.no, xn--sjlinvest-m8a.com, xn--sjl-invest-1cb.no, xn--sjl-invest-1cb.com |
| 936276075 | M BERGUM AS | mbergum.no, mbergum-as.no, mbergumas.no, mbergum.as, mbergum.com, m-bergum.no, m-bergum-as.no, m-bergumas.no, m-bergum.as, m-bergum.com |
| 918975934 | TØMRER TOMMY WIK OLSEN AS | tomrertommywikolsen.no, tomrertommywikolsen-as.no, tomrertommywikolsenas.no, tomrertommywikolsen.as, tomrertommywikolsen.com, tomrer-tommy-wik-olsen.no, tomrer-tommy-wik-olsen-as.no, tomrer-tommy-wik-olsenas.no, tomrer-tommy-wik-olsen.as, tomrer-tommy-wik-olsen.com, toemrertommywikolsen.no, toemrertommywikolsen-as.no, toemrertommywikolsenas.no, toemrertommywikolsen.as, toemrertommywikolsen.com, toemrer-tommy-wik-olsen.no, toemrer-tommy-wik-olsen-as.no, toemrer-tommy-wik-olsenas.no, toemrer-tommy-wik-olsen.as, toemrer-tommy-wik-olsen.com, xn--tmrertommywikolsen-g4b.no, xn--tmrertommywikolsen-g4b.com, xn--tmrer-tommy-wik-olsen-qfc.no, xn--tmrer-tommy-wik-olsen-qfc.com |
| 997768728 | SELMAN EIENDOM AS | sarpsborgdagligvare.no, sarpsborgdagligvare-as.no, sarpsborgdagligvareas.no, sarpsborgdagligvare.as, sarpsborgdagligvare.com, sarpsborg-dagligvare.no, sarpsborg-dagligvare-as.no, sarpsborg-dagligvareas.no, sarpsborg-dagligvare.as, sarpsborg-dagligvare.com, selmaneiendom.no, selmaneiendom-as.no, selmaneiendomas.no, selmaneiendom.as, selmaneiendom.com, selman-eiendom.no, selman-eiendom-as.no, selman-eiendomas.no, selman-eiendom.as, selman-eiendom.com |
| 920597122 | ARCTIC GRILL AS | arcticgrill.no, arcticgrill-as.no, arcticgrillas.no, arcticgrill.as, arcticgrill.com, arctic-grill.no, arctic-grill-as.no, arctic-grillas.no, arctic-grill.as, arctic-grill.com |
| 936256295 | VINKEL FRISØR AS | vinkelfrisor.no, vinkelfrisor-as.no, vinkelfrisoras.no, vinkelfrisor.as, vinkelfrisor.com, vinkel-frisor.no, vinkel-frisor-as.no, vinkel-frisoras.no, vinkel-frisor.as, vinkel-frisor.com, vinkelfrisoer.no, vinkelfrisoer-as.no, vinkelfrisoeras.no, vinkelfrisoer.as, vinkelfrisoer.com, vinkel-frisoer.no, vinkel-frisoer-as.no, vinkel-frisoeras.no, vinkel-frisoer.as, vinkel-frisoer.com, xn--vinkelfrisr-pgb.no, xn--vinkelfrisr-pgb.com, xn--vinkel-frisr-5jb.no, xn--vinkel-frisr-5jb.com |
| 915707238 | RØRESTRAND EIENDOM AS | rorestrandeiendom.no, rorestrandeiendom-as.no, rorestrandeiendomas.no, rorestrandeiendom.as, rorestrandeiendom.com, rorestrand-eiendom.no, rorestrand-eiendom-as.no, rorestrand-eiendomas.no, rorestrand-eiendom.as, rorestrand-eiendom.com, roerestrandeiendom.no, roerestrandeiendom-as.no, roerestrandeiendomas.no, roerestrandeiendom.as, roerestrandeiendom.com, roerestrand-eiendom.no, roerestrand-eiendom-as.no, roerestrand-eiendomas.no, roerestrand-eiendom.as, roerestrand-eiendom.com, xn--rrestrandeiendom-lxb.no, xn--rrestrandeiendom-lxb.com, xn--rrestrand-eiendom-00b.no, xn--rrestrand-eiendom-00b.com |
| 927901722 | KURIUS AS | kurius.no, kurius-as.no, kuriusas.no, kurius.as, kurius.com |
| 916108141 | EMPI AS | empi.no, empi-as.no, empias.no, empi.as, enovis.com, empi.com |

### all candidates DNS-missing

| Company | Name | Candidate domains |
|---|---|---|
| 912823970 | MYNT OG EIENDOM BESSAKER AS | mynteiendombessaker.no, mynteiendombessaker-as.no, mynteiendombessakeras.no, mynteiendombessaker.as, mynteiendombessaker.com, mynt-eiendom-bessaker.no, mynt-eiendom-bessaker-as.no, mynt-eiendom-bessakeras.no, mynt-eiendom-bessaker.as, mynt-eiendom-bessaker.com |
| 916729774 | FIKO EIENDOM AS | fikoeiendom.no, fikoeiendom-as.no, fikoeiendomas.no, fikoeiendom.as, fikoeiendom.com, fiko-eiendom.no, fiko-eiendom-as.no, fiko-eiendomas.no, fiko-eiendom.as, fiko-eiendom.com |
| 917998787 | DRAGEHAUGEN VERDI AS | dragehaugenverdi.no, dragehaugenverdi-as.no, dragehaugenverdias.no, dragehaugenverdi.as, dragehaugenverdi.com, dragehaugen-verdi.no, dragehaugen-verdi-as.no, dragehaugen-verdias.no, dragehaugen-verdi.as, dragehaugen-verdi.com |
| 919948493 | SQ URBAN LANDSKAP AS | squrbanlandskap.no, squrbanlandskap-as.no, squrbanlandskapas.no, squrbanlandskap.as, squrbanlandskap.com, sq-urban-landskap.no, sq-urban-landskap-as.no, sq-urban-landskapas.no, sq-urban-landskap.as, sq-urban-landskap.com |
| 923472134 | BOLIG 1 HALDEN AS | bolig1halden.no, bolig1halden-as.no, bolig1haldenas.no, bolig1halden.as, bolig1halden.com, bolig-1-halden.no, bolig-1-halden-as.no, bolig-1-haldenas.no, bolig-1-halden.as, bolig-1-halden.com |
| 936312055 | ULTRAMAX 8 AS | ultramax8.no, ultramax8-as.no, ultramax8as.no, ultramax8.as, ultramax8.com, ultramax-8.no, ultramax-8-as.no, ultramax-8as.no, ultramax-8.as, ultramax-8.com |
| 914723612 | HAAKON VII S GT HOLDING AS | haakonviisgtholding.no, haakonviisgtholding-as.no, haakonviisgtholdingas.no, haakonviisgtholding.as, haakonviisgtholding.com, haakon-vii-s-gt-holding.no, haakon-vii-s-gt-holding-as.no, haakon-vii-s-gt-holdingas.no, haakon-vii-s-gt-holding.as, haakon-vii-s-gt-holding.com |
| 933170705 | NORWEKA AS | norweka.no, norweka-as.no, norwekaas.no, norweka.as, norweka.com |
| 927239620 | BMF DRIFT AS | bmfdrift.no, bmfdrift-as.no, bmfdriftas.no, bmfdrift.as, bmfdrift.com, bmf-drift.no, bmf-drift-as.no, bmf-driftas.no, bmf-drift.as, bmf-drift.com |
| 935180759 | NESSET BLIKK AS | nessetblikk.no, nessetblikk-as.no, nessetblikkas.no, nessetblikk.as, nessetblikk.com, nesset-blikk.no, nesset-blikk-as.no, nesset-blikkas.no, nesset-blikk.as, nesset-blikk.com |

### ambiguous (name-only or competing candidates)

| Company | Name | Candidate domains |
|---|---|---|
| 989252968 | MARIA LOUISE AS | marialouise.no, marialouise-as.no, marialouiseas.no, marialouise.as, marialouise.com, maria-louise.no, maria-louise-as.no, maria-louiseas.no, maria-louise.as, maria-louise.com |
| 935450233 | FLUVIO AS | fluvio.no, fluvio-as.no, fluvioas.no, fluvio.as, fluvio.com |
| 995748983 | MAAEMO AS | maaemo.no, maaemo-as.no, maaemoas.no, maaemo.as, maaemo.com |
| 934404688 | SEROTONIC AS | serotonic.no, serotonic-as.no, serotonicas.no, serotonic.as, serotonic.com |
| 921810229 | KLINEVO AS | klinevo.no, klinevo-as.no, klinevoas.no, klinevo.as, klinevo.se, klinevo.com |
| 914582660 | SERIVA AS | nipa-as.no, seriva.no, seriva-as.no, serivaas.no, seriva.as, seriva.com |
| 929074009 | MULLIGAN INDOOR GOLF AS | mulligangolf.no, mulliganindoorgolf.no, mulliganindoorgolf-as.no, mulliganindoorgolfas.no, mulliganindoorgolf.as, mulliganindoorgolf.com |
| 999656099 | NETAD AS | netad24.com, netad.no, netad-as.no, netadas.no, netad.as, netad.com |
| 968468235 | HÅRSTUA AS | harstua.no, harstua-as.no, harstuaas.no, harstua.as, harstua.com, haarstua.no, haarstua-as.no, haarstuaas.no, haarstua.as, haarstua.com, xn--hrstua-iua.no, xn--hrstua-iua.com |
| 922069212 | KARLSEN AS | karlsen.no, karlsen-as.no, karlsenas.no, domenia.no, karlsen.com, karlsen.as |

## Recovery priority

Choose recovery work from the measured buckets: DNS-missing legal-name guesses need new nominations (Wikidata, then optional search); fetched/name-only pages need additional ownership evidence; budget stops need enough reserved proof requests. More budget does not make absent DNS guesses valid, and none of these bucket counts is a measured recovery promise.
