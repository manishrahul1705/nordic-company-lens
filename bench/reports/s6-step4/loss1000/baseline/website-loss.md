# Website loss diagnosis

This is a read-only analysis of saved run diagnostics. No network requests or behavior changes.

## primary — 1000 companies

Available: 69; missing: 931.

| Stop reason | Companies |
|---|---:|
| TLS-connect failure | 604 |
| all candidates DNS-missing | 135 |
| proof conflict (other orgnr) | 39 |
| budget exhausted | 36 |
| robots or blocked | 34 |
| fetched but no proof | 31 |
| ambiguous (name-only or competing candidates) | 26 |
| no retained successful company page | 16 |
| no candidates generated | 10 |

Reasons are exclusive stop buckets from recorded candidate diagnostics, not inferred exhaustive absence. Budget includes request/deadline limits. DNS/transient TLS failures are grouped conservatively when low-level transport messages are unavailable.

### TLS-connect failure

| Company | Name | Candidate domains |
|---|---|---|
| 916729774 | FIKO EIENDOM AS | fikoeiendom.no, fikoeiendom-as.no, fikoeiendomas.no, fikoeiendom.as, fikoeiendom.com, fiko-eiendom.no, fiko-eiendom-as.no, fiko-eiendomas.no, fiko-eiendom.as, fiko-eiendom.com |
| 917998787 | DRAGEHAUGEN VERDI AS | dragehaugenverdi.no, dragehaugenverdi-as.no, dragehaugenverdias.no, dragehaugenverdi.as, dragehaugenverdi.com, dragehaugen-verdi.no, dragehaugen-verdi-as.no, dragehaugen-verdias.no, dragehaugen-verdi.as, dragehaugen-verdi.com |
| 918049215 | MENSTAD NÆRINGSPARK AS | menstadnaeringspark.no, menstadnaeringspark-as.no, menstadnaeringsparkas.no, menstadnaeringspark.as, menstadnaeringspark.com, menstad-naeringspark.no, menstad-naeringspark-as.no, menstad-naeringsparkas.no, menstad-naeringspark.as, menstad-naeringspark.com, menstadnaringspark.no, menstadnaringspark-as.no, menstadnaringsparkas.no, menstadnaringspark.as, menstadnaringspark.com, menstad-naringspark.no, menstad-naringspark-as.no, menstad-naringsparkas.no, menstad-naringspark.as, menstad-naringspark.com, xn--menstadnringspark-yrb.no, xn--menstadnringspark-yrb.com, xn--menstad-nringspark-wub.no, xn--menstad-nringspark-wub.com |
| 982410851 | MARUN AS | marun.no, marun-as.no, marunas.no, marun.as, marun.com |
| 981508734 | MYKLEBUST MARITIME AS | myklebustverft.no, myklebustmaritime.no, myklebustmaritime-as.no, myklebustmaritimeas.no, myklebustmaritime.as, myklebustmaritime.com, myklebust-maritime.no, myklebust-maritime-as.no, myklebust-maritimeas.no, myklebust-maritime.as, myklebust-maritime.com |
| 916049153 | SJØL INVEST AS | sjolinvest.no, sjolinvest-as.no, sjolinvestas.no, sjolinvest.as, sjolinvest.com, sjol-invest.no, sjol-invest-as.no, sjol-investas.no, sjol-invest.as, sjol-invest.com, sjoelinvest.no, sjoelinvest-as.no, sjoelinvestas.no, sjoelinvest.as, sjoelinvest.com, sjoel-invest.no, sjoel-invest-as.no, sjoel-investas.no, sjoel-invest.as, sjoel-invest.com, xn--sjlinvest-m8a.no, xn--sjlinvest-m8a.com, xn--sjl-invest-1cb.no, xn--sjl-invest-1cb.com |
| 936276075 | M BERGUM AS | mbergum.no, mbergum-as.no, mbergumas.no, mbergum.as, mbergum.com, m-bergum.no, m-bergum-as.no, m-bergumas.no, m-bergum.as, m-bergum.com |
| 923472134 | BOLIG 1 HALDEN AS | bolig1halden.no, bolig1halden-as.no, bolig1haldenas.no, bolig1halden.as, bolig1halden.com, bolig-1-halden.no, bolig-1-halden-as.no, bolig-1-haldenas.no, bolig-1-halden.as, bolig-1-halden.com |
| 936312055 | ULTRAMAX 8 AS | ultramax8.no, ultramax8-as.no, ultramax8as.no, ultramax8.as, ultramax8.com, ultramax-8.no, ultramax-8-as.no, ultramax-8as.no, ultramax-8.as, ultramax-8.com |
| 995541432 | WACKER CHEMICALS NORWAY AS | wacker.com, wackerchemicalsnorway.no, wackerchemicalsnorway-as.no, wackerchemicalsnorwayas.no, wackerchemicalsnorway.as, wackerchemicalsnorway.com, wacker-chemicals-norway.no, wacker-chemicals-norway-as.no, wacker-chemicals-norwayas.no, wacker-chemicals-norway.as, wacker-chemicals-norway.com |

### all candidates DNS-missing

| Company | Name | Candidate domains |
|---|---|---|
| 912823970 | MYNT OG EIENDOM BESSAKER AS | mynteiendombessaker.no, mynteiendombessaker-as.no, mynteiendombessakeras.no, mynteiendombessaker.as, mynteiendombessaker.com, mynt-eiendom-bessaker.no, mynt-eiendom-bessaker-as.no, mynt-eiendom-bessakeras.no, mynt-eiendom-bessaker.as, mynt-eiendom-bessaker.com |
| 919948493 | SQ URBAN LANDSKAP AS | squrbanlandskap.no, squrbanlandskap-as.no, squrbanlandskapas.no, squrbanlandskap.as, squrbanlandskap.com, sq-urban-landskap.no, sq-urban-landskap-as.no, sq-urban-landskapas.no, sq-urban-landskap.as, sq-urban-landskap.com |
| 933170705 | NORWEKA AS | norweka.no, norweka-as.no, norwekaas.no, norweka.as, norweka.com |
| 935180759 | NESSET BLIKK AS | nessetblikk.no, nessetblikk-as.no, nessetblikkas.no, nessetblikk.as, nessetblikk.com, nesset-blikk.no, nesset-blikk-as.no, nesset-blikkas.no, nesset-blikk.as, nesset-blikk.com |
| 926648306 | EINE EIENDOM AS | eineeiendom.no, eineeiendom-as.no, eineeiendomas.no, eineeiendom.as, eineeiendom.com, eine-eiendom.no, eine-eiendom-as.no, eine-eiendomas.no, eine-eiendom.as, eine-eiendom.com |
| 930681628 | MEL HEIA 6 AS | melheia6.no, melheia6-as.no, melheia6as.no, melheia6.as, melheia6.com, mel-heia-6.no, mel-heia-6-as.no, mel-heia-6as.no, mel-heia-6.as, mel-heia-6.com |
| 934515218 | STERRE-BEERS AS | sterrebeers.no, sterrebeers-as.no, sterrebeersas.no, sterrebeers.as, sterrebeers.com, sterre-beers.no, sterre-beers-as.no, sterre-beersas.no, sterre-beers.as, sterre-beers.com |
| 836686462 | TANNLEGE ANAS ALHAYDAR AS | tannlegeanasalhaydar.no, tannlegeanasalhaydar-as.no, tannlegeanasalhaydaras.no, tannlegeanasalhaydar.as, tannlegeanasalhaydar.com, tannlege-anas-alhaydar.no, tannlege-anas-alhaydar-as.no, tannlege-anas-alhaydaras.no, tannlege-anas-alhaydar.as, tannlege-anas-alhaydar.com |
| 932386933 | GULBIS HOLDING AS | gulbisholding.no, gulbisholding-as.no, gulbisholdingas.no, gulbisholding.as, gulbisholding.com, gulbis-holding.no, gulbis-holding-as.no, gulbis-holdingas.no, gulbis-holding.as, gulbis-holding.com |
| 935327423 | EDSVIK INVEST AS | edsvikinvest.no, edsvikinvest-as.no, edsvikinvestas.no, edsvikinvest.as, edsvikinvest.com, edsvik-invest.no, edsvik-invest-as.no, edsvik-investas.no, edsvik-invest.as, edsvik-invest.com |

### proof conflict (other orgnr)

| Company | Name | Candidate domains |
|---|---|---|
| 985204381 | CLEMENS KRAFTVERK AS | clemenskraft.no, clemenskraftverk.no, clemenskraftverk-as.no, clemenskraftverkas.no, clemenskraftverk.as, clemenskraftverk.com, clemens-kraftverk.no, clemens-kraftverk-as.no, clemens-kraftverkas.no, clemens-kraftverk.as, clemens-kraftverk.com |
| 927944979 | GYLDEN ENG AS | eiendomsfinans.no, gyldeneng.no, gyldeneng-as.no, gyldenengas.no, gyldeneng.as, gyldeneng.com, gylden-eng.no, gylden-eng-as.no, gylden-engas.no, gylden-eng.as, gylden-eng.com |
| 977149312 | MARGIT OG KARL KVAVIKS LEGAT STI | lyngdal.kommune.no, margitkarlkvavikslegat.no, margitkarlkvavikslegat-as.no, margitkarlkvavikslegatas.no, margitkarlkvavikslegat.as, margitkarlkvavikslegat.com, margit-karl-kvaviks-legat.no, margit-karl-kvaviks-legat-as.no, margit-karl-kvaviks-legatas.no, margit-karl-kvaviks-legat.as, margit-karl-kvaviks-legat.com |
| 955010477 | AL ULLERUDTOPPEN BORETTSLAG | usbl.no, alullerudtoppenborettslag.no, alullerudtoppenborettslag-as.no, alullerudtoppenborettslagas.no, alullerudtoppenborettslag.as, alullerudtoppenborettslag.com, al-ullerudtoppen-borettslag.no, al-ullerudtoppen-borettslag-as.no, al-ullerudtoppen-borettslagas.no, al-ullerudtoppen-borettslag.as, al-ullerudtoppen-borettslag.com |
| 915097189 | OWREN EIENDOM HOLDING AS | owren.no, owreneiendomholding.no, owreneiendomholding-as.no, owreneiendomholdingas.no, owreneiendomholding.as, owreneiendomholding.com, owren-eiendom-holding.no, owren-eiendom-holding-as.no, owren-eiendom-holdingas.no, owren-eiendom-holding.as, owren-eiendom-holding.com |
| 928329828 | HAGE OG TREFELLING AS | bergenhageogtrefelling.no, moldeklev.no, hagetrefelling.no, hagetrefelling-as.no, hagetrefellingas.no, hagetrefelling.as, hagetrefelling.com, hage-trefelling.no, hage-trefelling-as.no, hage-trefellingas.no, hage-trefelling.as, hage-trefelling.com |
| 927327481 | SAMEIET SPANNATOPPEN 27-37 | vestbo.no, sameietspannatoppen2737.no, sameietspannatoppen2737-as.no, sameietspannatoppen2737as.no, sameietspannatoppen2737.as, sameietspannatoppen2737.com, sameiet-spannatoppen-27-37.no, sameiet-spannatoppen-27-37-as.no, sameiet-spannatoppen-27-37as.no, sameiet-spannatoppen-27-37.as, sameiet-spannatoppen-27-37.com |
| 990459606 | SAMEIET SKJELDERUPSGATE 15 | solibo.no, sameietskjelderupsgate15.no, sameietskjelderupsgate15-as.no, sameietskjelderupsgate15as.no, sameietskjelderupsgate15.as, sameietskjelderupsgate15.com, sameiet-skjelderupsgate-15.no, sameiet-skjelderupsgate-15-as.no, sameiet-skjelderupsgate-15as.no, sameiet-skjelderupsgate-15.as, sameiet-skjelderupsgate-15.com |
| 985470944 | SKI UR OG SMYKKER AS | bjorklund.no, skiursmykker.no, skiursmykker-as.no, skiursmykkeras.no, skiursmykker.as, skiursmykker.com, ski-ur-smykker.no, ski-ur-smykker-as.no, ski-ur-smykkeras.no, ski-ur-smykker.as, ski-ur-smykker.com |
| 954081311 | KLEPPESTØ BORETTSLAG | vestbo.no, kleppestoborettslag.no, kleppestoborettslag-as.no, kleppestoborettslagas.no, kleppestoborettslag.as, kleppestoborettslag.com, kleppesto-borettslag.no, kleppesto-borettslag-as.no, kleppesto-borettslagas.no, kleppesto-borettslag.as, kleppesto-borettslag.com, kleppestoeborettslag.no, kleppestoeborettslag-as.no, kleppestoeborettslagas.no, kleppestoeborettslag.as, kleppestoeborettslag.com, kleppestoe-borettslag.no, kleppestoe-borettslag-as.no, kleppestoe-borettslagas.no, kleppestoe-borettslag.as, kleppestoe-borettslag.com, xn--kleppestborettslag-n4b.no, xn--kleppestborettslag-n4b.com, xn--kleppest-borettslag-27b.no, xn--kleppest-borettslag-27b.com |

## Recovery priority

Choose recovery work from the measured buckets: DNS-missing legal-name guesses need new nominations (Wikidata, then optional search); fetched/name-only pages need additional ownership evidence; budget stops need enough reserved proof requests. More budget does not make absent DNS guesses valid, and none of these bucket counts is a measured recovery promise.
