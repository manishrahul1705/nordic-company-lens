# Saved-run funnel diagnosis

Categories overlap. Domains are registrable domains. Resolves is observed positive only (HTTP status or request-sent marker); absent DNS telemetry is not called NXDOMAIN. Fetched OK excludes robots. Proof failure is fetched 200 without verified proof. No network requests.

Source: `bench\runs\20261106T055741582104Z-1909653`. No new crawl was used for diagnosis.

| Candidate source | Companies nominated | Domains nominated/tried | Observed resolves | Fetched OK | Proof passed | Proof failed | Group withheld |
|---|---:|---:|---:|---:|---:|---:|---:|
| registry_homepage | 107 | 107 | 91 | 80 | 26 | 54 | 0 |
| registry_email | 189 | 189 | 150 | 129 | 31 | 98 | 0 |
| subunit | 155 | 167 | 129 | 109 | 31 | 78 | 0 |
| guessed | 941 | 10455 | 383 | 276 | 43 | 233 | 1 |

The categories overlap; their proof totals must not be added. Subunit domains are from retained registry records. Resolution is a lower bound because the old run did not retain every DNS outcome.

| Source | Failed proof reason | Domains |
|---|---|---:|
| registry_homepage | insufficient_owner_proof | 18 |
| registry_homepage | name_without_suffix_insufficient_contacts_or_domain | 20 |
| registry_homepage | foreign_orgnr | 15 |
| registry_homepage | no_proof_diagnostic | 1 |
| registry_email | insufficient_owner_proof | 47 |
| registry_email | block_page | 1 |
| registry_email | foreign_orgnr | 24 |
| registry_email | name_without_suffix_insufficient_contacts_or_domain | 24 |
| registry_email | parent_group_without_exact_orgnr | 1 |
| registry_email | no_proof_diagnostic | 1 |
| subunit | insufficient_owner_proof | 37 |
| subunit | name_without_suffix_insufficient_contacts_or_domain | 21 |
| subunit | parent_group_without_exact_orgnr | 1 |
| subunit | foreign_orgnr | 19 |
| guessed | insufficient_owner_proof | 108 |
| guessed | name_without_suffix_insufficient_contacts_or_domain | 99 |
| guessed | foreign_orgnr | 21 |
| guessed | parked | 2 |
| guessed | body_cap | 2 |
| guessed | website_budget_exhausted | 1 |

## Thirty seeded fetched-OK / unverified cases

Seed 10; one company/domain per sampled item. Titles and reasons are from saved responses and diagnostics, not live checks.

| Company / orgnr | Domain | Page title(s) | Reason |
|---|---|---|---|
| FIXIC AS / 829604922 | fixic.shop | Home - Fixic; Privacy Policy - Fixic | name_without_suffix_insufficient_contacts_or_domain |
| NETAD AS / 999656099 | netad24.com | netad24 / Publisher Affiliate Marketing Company; Contact Us / netad24; About-us / netad24; Privacy Policy / netad24 | name_without_suffix_insufficient_contacts_or_domain |
| LOGOS AS / 980411575 | lyse.net | www.lyse.net in parked; www.lyse.net in parked; www.lyse.net in parked; www.lyse.net in parked; www.lyse.net in parked; www.lyse.net in parked; www.lyse.net in parked | insufficient_owner_proof |
| LINDÅS NÆRSENTER AS / 971173459 | lindasnaersenter.no | Nærsenter på Lindås / Lindås Nærsenter / Vestland; Kontakt oss / Lindås Nærsenter; Om oss / Lindås Nærsenter; Personvernerklæring / Lindås Nærsenter / Vestland | name_without_suffix_insufficient_contacts_or_domain |
| SANDØ AS / 934500644 | sando.no | Bunadsølv og smykker / Gullsmed Sando | foreign_orgnr |
| ROLIDBAKKEN FUS BARNEHAGE AS / 991247610 | tryggebarnehager.no | Trygge barnehager | foreign_orgnr |
| EVENTMAKER AS / 965530819 | eventmaker.no | www.eventmaker.no; www.eventmaker.no; www.eventmaker.no; www.eventmaker.no; www.eventmaker.no; www.eventmaker.no; www.eventmaker.no | name_without_suffix_insufficient_contacts_or_domain |
| NORWEGIAN SCAFFOLD GROUP AS / 998162564 | fjordstillas.no | Få stillas tilbud hos / Fjord Stillas AS; Kontakt oss / Fjord Stillas AS; Om oss / Fjord Stillas AS | insufficient_owner_proof |
| RUMLESKAFT AS / 927671174 | rumleskaft.no | www.rumleskaft.no is parked; www.rumleskaft.no is parked; www.rumleskaft.no is parked; www.rumleskaft.no is parked; www.rumleskaft.no is parked; www.rumleskaft.no is parked; www.rumleskaft.no is parked | name_without_suffix_insufficient_contacts_or_domain |
| OWER TRAFIKKSKOLE AS / 834141582 | owertrafikkskole.no | owertrafikkskole.no – registrert domene; owertrafikkskole.no – registrert domene; owertrafikkskole.no – registrert domene; owertrafikkskole.no – registrert domene; owertrafikkskole.no – registrert domene; owertrafikkskole.no – registrert domene; owertrafikkskole.no – registrert domene | insufficient_owner_proof |
| EVOLVE AS / 983244858 | evolve.com | Evolve / Authentic Vacation Rental Homes You Can Count On; Contact Evolve - Vacation Rental Support for Owners & Guests; Evolve / Terms & Conditions for Use of Evolve.com; Evolve Privacy Policy | name_without_suffix_insufficient_contacts_or_domain |
| M&S EIENDOM AS / 932799901 | mseiendom.com | www.mseiendom.com is parked; www.mseiendom.com is parked; www.mseiendom.com is parked; www.mseiendom.com is parked; www.mseiendom.com is parked; www.mseiendom.com is parked | insufficient_owner_proof |
| NETAD AS / 999656099 | netad.no | Netad is coming soon | name_without_suffix_insufficient_contacts_or_domain |
| KAIKANTEN GRYLLEFJORD AS / 988836311 | kaikanten.no | Kaikanten – Byens beste pizza; Personvernerklæring – Kaikanten | foreign_orgnr |
| HVALEN STUDIO AS / 935666481 | hvalenstudio.no | Hvalen Studio — Management, musikk, design; Om oss — Hvalen Studio | name_without_suffix_insufficient_contacts_or_domain |
| MEDIA CITY DRAMMEN AS / 928035212 | mediacitydrammen.no | www.mediacitydrammen.no is parked; www.mediacitydrammen.no is parked; www.mediacitydrammen.no is parked; www.mediacitydrammen.no is parked; www.mediacitydrammen.no is parked; www.mediacitydrammen.no is parked; www.mediacitydrammen.no is parked | insufficient_owner_proof |
| NORWEGIAN BUSINESS PAVILIONS AS / 993327182 | messetjeneste.no | Messetjeneste / Messetjeneste / Vi realiserer kreative ideer; Messetjeneste / Kontakt oss; Messetjeneste / Send filer; Messetjeneste / Om oss; Messetjeneste / beMaster+; Messetjeneste / IFES; Messetjeneste / Miljøfyrtårn | insufficient_owner_proof |
| REMOTE ROBOTIC SYSTEMS AS / 933372332 | remoteroboticsystems.no | www.remoteroboticsystems.no is parked; www.remoteroboticsystems.no is parked; www.remoteroboticsystems.no is parked; www.remoteroboticsystems.no is parked; www.remoteroboticsystems.no is parked; www.remoteroboticsystems.no is parked; www.remoteroboticsystems.no is parked | insufficient_owner_proof |
| UNIME AS / 921186924 | unime.no | unime.no is parked; unime.no is parked; unime.no is parked; unime.no is parked; unime.no is parked; unime.no is parked; unime.no is parked | name_without_suffix_insufficient_contacts_or_domain |
| BONO SANDVIKSBODER AS / 996927903 | backe.no | Backe – entreprenør og eiendomsutvikler; Kontaktinformasjon / Backe | insufficient_owner_proof |
| SKATTEKISTEN AS / 922154635 | skattekisten.no | Skattekisten - Gull, Sølv og Edelstener | foreign_orgnr |
| AL ULLERUDTOPPEN BORETTSLAG / 955010477 | usbl.no | Boligbyggelag, forretningsfører og boligutvikler / Usbl | foreign_orgnr |
| KINDRA AS / 912493296 | ourkindra.com | Vaginal Health & Sexual Wellness / Kindra; Contact  – Kindra; Privacy policy  – Kindra; Privacy Policy  – Kindra; Terms of Service  – Kindra | name_without_suffix_insufficient_contacts_or_domain |
| SØRLIE HOLDING AS / 922753768 | sorlieholding.no | www.sorlieholding.no is not set up yet | insufficient_owner_proof |
| LAU CAPITAL AS / 927661683 | lau.com.cn | Lau Capital | name_without_suffix_insufficient_contacts_or_domain |
| FINNMARK RENSEFISK AS / 915884482 | rensefiskgruppen.no | Rensefiskgruppen – Rensefisk for dine merder | foreign_orgnr |
| ELTEK AS / 833912682 | eltek.no | www.eltek.no is parked; www.eltek.no is parked; www.eltek.no is parked; www.eltek.no is parked; www.eltek.no is parked; www.eltek.no is parked; www.eltek.no is parked | name_without_suffix_insufficient_contacts_or_domain |
| HANCHE AS / 925547530 | hanche.no | www.hanche.no is parked; www.hanche.no is parked; www.hanche.no is parked; www.hanche.no is parked; www.hanche.no is parked; www.hanche.no is parked; www.hanche.no is parked | name_without_suffix_insufficient_contacts_or_domain |
| SMEDGATA 45 OG 49 AS / 919092734 | sabinum.no | www.sabinum.no in parked; www.sabinum.no in parked; www.sabinum.no in parked; www.sabinum.no in parked; www.sabinum.no in parked; www.sabinum.no in parked; www.sabinum.no in parked | insufficient_owner_proof |
| SCENE MIDT AS / 998236002 | scenemidt.no | Scene Midt - Scene Midt; Kontakt - Scene Midt; Om oss - Scene Midt | name_without_suffix_insufficient_contacts_or_domain |
