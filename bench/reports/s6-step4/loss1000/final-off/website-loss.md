# Website loss diagnosis

This is a read-only analysis of saved run diagnostics. No network requests or behavior changes.

## primary — 1000 companies

Available: 73; missing: 927.

| Stop reason | Companies |
|---|---:|
| TLS-connect failure | 442 |
| all candidates DNS-missing | 222 |
| budget exhausted | 80 |
| proof conflict (other orgnr) | 48 |
| fetched but no proof | 44 |
| robots or blocked | 42 |
| ambiguous (name-only or competing candidates) | 26 |
| no retained successful company page | 13 |
| no candidates generated | 10 |

Reasons are exclusive stop buckets from recorded candidate diagnostics, not inferred exhaustive absence. Budget includes request/deadline limits. DNS/transient TLS failures are grouped conservatively when low-level transport messages are unavailable.

### TLS-connect failure

| Company | Name | Candidate domains |
|---|---|---|
| 917998787 | DRAGEHAUGEN VERDI AS | dragehaugenverdi.no, dragehaugenverdi-as.no, dragehaugenverdias.no, dragehaugenverdi.as, dragehaugenverdi.com, dragehaugen-verdi.no, dragehaugen-verdi-as.no, dragehaugen-verdias.no, dragehaugen-verdi.as, dragehaugen-verdi.com |
| 918049215 | MENSTAD NÆRINGSPARK AS | menstadnaeringspark.no, menstadnaeringspark-as.no, menstadnaeringsparkas.no, menstadnaeringspark.as, menstadnaeringspark.com, menstad-naeringspark.no, menstad-naeringspark-as.no, menstad-naeringsparkas.no, menstad-naeringspark.as, menstad-naeringspark.com, menstadnaringspark.no, menstadnaringspark-as.no, menstadnaringsparkas.no, menstadnaringspark.as, menstadnaringspark.com, menstad-naringspark.no, menstad-naringspark-as.no, menstad-naringsparkas.no, menstad-naringspark.as, menstad-naringspark.com, xn--menstadnringspark-yrb.no, xn--menstadnringspark-yrb.com, xn--menstad-nringspark-wub.no, xn--menstad-nringspark-wub.com |
| 981508734 | MYKLEBUST MARITIME AS | myklebustverft.no, myklebustmaritime.no, myklebustmaritime-as.no, myklebustmaritimeas.no, myklebustmaritime.as, myklebustmaritime.com, myklebust-maritime.no, myklebust-maritime-as.no, myklebust-maritimeas.no, myklebust-maritime.as, myklebust-maritime.com |
| 916049153 | SJØL INVEST AS | sjolinvest.no, sjolinvest-as.no, sjolinvestas.no, sjolinvest.as, sjolinvest.com, sjol-invest.no, sjol-invest-as.no, sjol-investas.no, sjol-invest.as, sjol-invest.com, sjoelinvest.no, sjoelinvest-as.no, sjoelinvestas.no, sjoelinvest.as, sjoelinvest.com, sjoel-invest.no, sjoel-invest-as.no, sjoel-investas.no, sjoel-invest.as, sjoel-invest.com, xn--sjlinvest-m8a.no, xn--sjlinvest-m8a.com, xn--sjl-invest-1cb.no, xn--sjl-invest-1cb.com |
| 936276075 | M BERGUM AS | mbergum.no, mbergum-as.no, mbergumas.no, mbergum.as, mbergum.com, m-bergum.no, m-bergum-as.no, m-bergumas.no, m-bergum.as, m-bergum.com |
| 923472134 | BOLIG 1 HALDEN AS | bolig1halden.no, bolig1halden-as.no, bolig1haldenas.no, bolig1halden.as, bolig1halden.com, bolig-1-halden.no, bolig-1-halden-as.no, bolig-1-haldenas.no, bolig-1-halden.as, bolig-1-halden.com |
| 936312055 | ULTRAMAX 8 AS | ultramax8.no, ultramax8-as.no, ultramax8as.no, ultramax8.as, ultramax8.com, ultramax-8.no, ultramax-8-as.no, ultramax-8as.no, ultramax-8.as, ultramax-8.com |
| 914723612 | HAAKON VII S GT HOLDING AS | haakonviisgtholding.no, haakonviisgtholding-as.no, haakonviisgtholdingas.no, haakonviisgtholding.as, haakonviisgtholding.com, haakon-vii-s-gt-holding.no, haakon-vii-s-gt-holding-as.no, haakon-vii-s-gt-holdingas.no, haakon-vii-s-gt-holding.as, haakon-vii-s-gt-holding.com |
| 918975934 | TØMRER TOMMY WIK OLSEN AS | tomrertommywikolsen.no, tomrertommywikolsen-as.no, tomrertommywikolsenas.no, tomrertommywikolsen.as, tomrertommywikolsen.com, tomrer-tommy-wik-olsen.no, tomrer-tommy-wik-olsen-as.no, tomrer-tommy-wik-olsenas.no, tomrer-tommy-wik-olsen.as, tomrer-tommy-wik-olsen.com, toemrertommywikolsen.no, toemrertommywikolsen-as.no, toemrertommywikolsenas.no, toemrertommywikolsen.as, toemrertommywikolsen.com, toemrer-tommy-wik-olsen.no, toemrer-tommy-wik-olsen-as.no, toemrer-tommy-wik-olsenas.no, toemrer-tommy-wik-olsen.as, toemrer-tommy-wik-olsen.com, xn--tmrertommywikolsen-g4b.no, xn--tmrertommywikolsen-g4b.com, xn--tmrer-tommy-wik-olsen-qfc.no, xn--tmrer-tommy-wik-olsen-qfc.com |
| 997768728 | SELMAN EIENDOM AS | sarpsborgdagligvare.no, sarpsborgdagligvare-as.no, sarpsborgdagligvareas.no, sarpsborgdagligvare.as, sarpsborgdagligvare.com, sarpsborg-dagligvare.no, sarpsborg-dagligvare-as.no, sarpsborg-dagligvareas.no, sarpsborg-dagligvare.as, sarpsborg-dagligvare.com, selmaneiendom.no, selmaneiendom-as.no, selmaneiendomas.no, selmaneiendom.as, selmaneiendom.com, selman-eiendom.no, selman-eiendom-as.no, selman-eiendomas.no, selman-eiendom.as, selman-eiendom.com |

### all candidates DNS-missing

| Company | Name | Candidate domains |
|---|---|---|
| 912823970 | MYNT OG EIENDOM BESSAKER AS | mynteiendombessaker.no, mynteiendombessaker-as.no, mynteiendombessakeras.no, mynteiendombessaker.as, mynteiendombessaker.com, mynt-eiendom-bessaker.no, mynt-eiendom-bessaker-as.no, mynt-eiendom-bessakeras.no, mynt-eiendom-bessaker.as, mynt-eiendom-bessaker.com |
| 916729774 | FIKO EIENDOM AS | fikoeiendom.no, fikoeiendom-as.no, fikoeiendomas.no, fikoeiendom.as, fikoeiendom.com, fiko-eiendom.no, fiko-eiendom-as.no, fiko-eiendomas.no, fiko-eiendom.as, fiko-eiendom.com |
| 919948493 | SQ URBAN LANDSKAP AS | squrbanlandskap.no, squrbanlandskap-as.no, squrbanlandskapas.no, squrbanlandskap.as, squrbanlandskap.com, sq-urban-landskap.no, sq-urban-landskap-as.no, sq-urban-landskapas.no, sq-urban-landskap.as, sq-urban-landskap.com |
| 933170705 | NORWEKA AS | norweka.no, norweka-as.no, norwekaas.no, norweka.as, norweka.com |
| 975822567 | MESEL EIENDOM AS | meseleiendom.no, meseleiendom-as.no, meseleiendomas.no, meseleiendom.as, meseleiendom.com, mesel-eiendom.no, mesel-eiendom-as.no, mesel-eiendomas.no, mesel-eiendom.as, mesel-eiendom.com |
| 925321419 | TJELTA VINDUSPUSS AS | tjeltavinduspuss.no, tjeltavinduspuss-as.no, tjeltavinduspussas.no, tjeltavinduspuss.as, tjeltavinduspuss.com, tjelta-vinduspuss.no, tjelta-vinduspuss-as.no, tjelta-vinduspussas.no, tjelta-vinduspuss.as, tjelta-vinduspuss.com |
| 836686462 | TANNLEGE ANAS ALHAYDAR AS | tannlegeanasalhaydar.no, tannlegeanasalhaydar-as.no, tannlegeanasalhaydaras.no, tannlegeanasalhaydar.as, tannlegeanasalhaydar.com, tannlege-anas-alhaydar.no, tannlege-anas-alhaydar-as.no, tannlege-anas-alhaydaras.no, tannlege-anas-alhaydar.as, tannlege-anas-alhaydar.com |
| 987454709 | NYE NEPTUNE PUB AS | nyeneptunepub.no, nyeneptunepub-as.no, nyeneptunepubas.no, nyeneptunepub.as, nyeneptunepub.com, nye-neptune-pub.no, nye-neptune-pub-as.no, nye-neptune-pubas.no, nye-neptune-pub.as, nye-neptune-pub.com |
| 934940792 | HELHETLIG HELSE E&M AS | helhetlighelseem.no, helhetlighelseem-as.no, helhetlighelseemas.no, helhetlighelseem.as, helhetlighelseem.com, helhetlig-helse-e-m.no, helhetlig-helse-e-m-as.no, helhetlig-helse-e-mas.no, helhetlig-helse-e-m.as, helhetlig-helse-e-m.com |
| 918270205 | GILJEHOLMEN AS | giljeholmen.no, giljeholmen-as.no, giljeholmenas.no, giljeholmen.as, giljeholmen.com |

### budget exhausted

| Company | Name | Candidate domains |
|---|---|---|
| 982410851 | MARUN AS | marun.no, marun-as.no, marunas.no, marun.as, cristty.com, marun.com |
| 989252968 | MARIA LOUISE AS | marialouise.no, marialouise-as.no, marialouiseas.no, marialouise.as, marialouise.com, maria-louise.no, maria-louise-as.no, maria-louiseas.no, maria-louise.as, maria-louise.com |
| 995748983 | MAAEMO AS | maaemo.no, maaemo-as.no, maaemoas.no, maaemo.as, maaemo.com |
| 914582660 | SERIVA AS | nipa-as.no, seriva.no, seriva-as.no, serivaas.no, seriva.as, seriva.com |
| 929074009 | MULLIGAN INDOOR GOLF AS | mulligangolf.no, mulliganindoorgolf.no, mulliganindoorgolf-as.no, mulliganindoorgolfas.no, mulliganindoorgolf.as, mulliganindoorgolf.com |
| 968468235 | HÅRSTUA AS | harstua.no, harstua-as.no, harstuaas.no, harstua.as, harstua.com, haarstua.no, haarstua-as.no, haarstuaas.no, haarstua.as, haarstua.com, xn--hrstua-iua.no, xn--hrstua-iua.com |
| 887820082 | ARENA HOLDING AS | arenaholding.no, arenaholding-as.no, arenaholdingas.no, arenaholding.as, hugedomains.com, arena-holding.no, arena-holding-as.no, arena-holdingas.no, arena-holding.as, arena-holding.com, arenaholding.com |
| 935641403 | CAPORUM AS | caporum.se, caporum-as.no, caporumas.no, caporum.as, caporum.no, caporum.com |
| 931975552 | VERA INVEST AS | verainvest.no, verainvest-as.no, verainvestas.no, verainvest.as, verainvest.se, vera-invest.no, vera-invest-as.no, vera-investas.no, vera-invest.as, vera-invest.com, verainvest.com |
| 923219137 | GREEN 4 YOU AS | green4you.no, green4you-as.no, green4youas.no, green4you.as, green4you.com |

## Recovery priority

Choose recovery work from the measured buckets: DNS-missing legal-name guesses need new nominations (Wikidata, then optional search); fetched/name-only pages need additional ownership evidence; budget stops need enough reserved proof requests. More budget does not make absent DNS guesses valid, and none of these bucket counts is a measured recovery promise.
