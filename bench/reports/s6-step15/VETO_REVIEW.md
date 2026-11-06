# Step15 pre-change veto audit

No veto rule changed. Saved Step14 evidence only; no new requests. Same160-company subset as the pre-code funnel. One primary category per company: first explicit terminal veto in saved candidate order. All other candidate vetoes remain in the JSON ledger. Parking/default codes are categorised from actual saved page text, not blindly treated as company publishers.

| Primary veto category | Companies |
|---|---:|
| group/shared site | 46 |
| different publisher | 52 |
| parked/for-sale | 53 |
| foreign .com | 0 |
| other | 9 |

Counts sum160. Foreign .com=0 refers only to this subset/primary-veto allocation; it is not a claim that no global-site withholding occurred anywhere in the1000 run. Other9 includes non-parking hosting/default/frameset/construction cases.

Two largest: parked/for-sale53 and different publisher52. Sampled10 distinct companies in each using seed20261106 on the saved input order, without replacement. Each available saved response SHA256 was checked.

## Hand review

| Group | Company / orgnr | Candidate | Was veto right? | Source finding |
|---|---|---|---|---|
| parked/for-sale | TOBIASSEN FJELLSPRENGNING AS / 996698920 | tobiassenfjellsprengning.no | right | Saved page explicitly says the domain is parked and/or has no active website. Hosting-provider content is not a company-owned business site. |
| parked/for-sale | NORGESSTILLAS AS / 930014397 | norgesstillas.no | right | Saved page explicitly says the domain is parked and/or has no active website. Hosting-provider content is not a company-owned business site. |
| parked/for-sale | FGLIDES AS / 921484623 | fglides.no | right | Saved page explicitly says the domain is parked and/or has no active website. Hosting-provider content is not a company-owned business site. |
| parked/for-sale | HANSEBU AS / 919893389 | hansebu.no | right | Saved page explicitly says the domain is parked and/or has no active website. Hosting-provider content is not a company-owned business site. |
| parked/for-sale | HAND AS / 934012674 | hand.no | right | Saved page explicitly says the domain is parked and/or has no active website. Hosting-provider content is not a company-owned business site. |
| parked/for-sale | MARIA LOUISE AS / 989252968 | marialouise.no | right | Saved page explicitly says the domain is parked and/or has no active website. Hosting-provider content is not a company-owned business site. |
| parked/for-sale | WRIXIT AS / 933031071 | wrixit.no | right | Saved page explicitly says the domain is parked and/or has no active website. Hosting-provider content is not a company-owned business site. |
| parked/for-sale | TUDAL EIENDOM AS / 918004440 | tudaleiendom.no | right | Saved page explicitly says the domain is parked and/or has no active website. Hosting-provider content is not a company-owned business site. |
| parked/for-sale | SVANANESET AS / 994986740 | svananeset.no | right | Saved page explicitly says the domain is parked and/or has no active website. Hosting-provider content is not a company-owned business site. |
| parked/for-sale | JARO EIENDOMSUTVIKLING AS / 912972062 | jaroeiendomsutvikling.no | right | Saved page explicitly says the domain is parked and/or has no active website. Hosting-provider content is not a company-owned business site. |
| different publisher | NSF LØVENSKIOLDBANEN AS / 927826550 | skyting.no | right | Page names Norges Sportsskytterforbund, org946168114, not927826550. A club range link/email at the federation does not prove ownership by the AS. |
| different publisher | UPPSTAD VVS AVDELING HOVDEN AS / 926698435 | uppstadvvs.no | right | Title/member identity is UPPSTAD VVS AS in Rysstad; mentions a Hovden branch, but does not establish the exact separate AVDELING HOVDEN AS orgnr/address. |
| different publisher | EINE EIENDOM AS / 926648306 | eine.no | right | Bagn Pølsemakeri AS explicitly shows org992041684; subject is EINE EIENDOM AS926648306 in Sarpsborg. |
| different publisher | NORWEGIAN BUSINESS PAVILIONS AS / 993327182 | messetjeneste.no | right | Footer explicitly names Messetjeneste AS. Shared Lommedalsveien address/phone and nominated email do not establish Norwegian Business Pavilions as the same entity. |
| different publisher | BYGGOM AS / 933547000 | montasje-service.no | right | Contact names Montasje Service AS in Frei. BYGGOM AS is registered in Namsos; a byggom.no email on that page is insufficient and does not prove this AS owns it. |
| different publisher | FIKO EIENDOM AS / 916729774 | fiko.no | right | Page explicitly contracts/bills through ANZYZ Technologies AS org914490944. Subject FIKO EIENDOM AS916729774 is a different legal entity. |
| different publisher | BRA BO EIENDOM AS / 981063635 | brabo.no | right | Footer names Brabo Sør AS org997410815 in Kristiansand/PHM. Subject BRA BO EIENDOM AS981063635 is in Bodø. |
| different publisher | MOTORSYKLISTEN AS / 933458032 | motorsyklisten.no | wrong reason; withholding still justified | The sole detected copyright AS is Webshop Quick Systems AS, a software supplier credit, not evidence of the merchant publisher. However the page is an MC shop in Søgne with phone38051615; the subject registry is MOTORSYKLISTEN AS933458032 in Stord with phone53414211. No exact orgnr or matching registry contact is shown. Ignoring this credit would not publish the site under the unchanged proof rules. |
| different publisher | RUTA EIENDOM AS / 812190172 | ruta.no | right | Footer identifies Ruta Entreprenør AS org983830196. Shared address with RUTA EIENDOM AS812190172 does not establish exact-entity website ownership. |
| different publisher | 7OCEAN HOLDING AS / 999530095 | 7ocean.no | right | Page says7ocean AS and copyright7ocean Group AS. Registry subject is7OCEAN HOLDING AS; homepage/address nomination does not override the explicitly different publisher identities. |

## Result and proposed changes

Parked/for-sale:10/10 correct vetoes,0wrong. Different publisher:9/10 correct publisher reasons;1/10 wrong publisher inference (MOTORSYKLISTEN / supplier credit), but0confirmed company-owned sites wrongly withheld. Publication still requires the existing exact-entity proof; a shared address, parent/branch name or same-name brand alone does not suffice.

Neither sampled category has3+wrong reasons/outcomes in10. The requested threshold for proposing a narrower veto rule is not triggered. **No veto change is proposed or applied, and no sampled company would newly qualify for publication.** Motorsyklisten is explicitly flagged for a possible future supplier-credit parser refinement, subject to review: ignoring that one clearly labelled software credit would remove that particular veto but still fail current ownership proof. All other sampled sites remain blocked. No company-specific exception is suggested.

Evidence URLs, hashes, extracted titles/text/footer, primary and all candidate vetoes: [full160 ledger](veto-breakdown.json), [20 individual review records](veto-review-sample.json).
