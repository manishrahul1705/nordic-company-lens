# Step 18 precision review

Seed 20261108; 20 distinct new raw event IDs not published in Step 17, then 10 random company briefings. No sampled record was replaced. Each event was compared with its raw feed row, exact organisation number or retained registered-parent record, publication instant, event type, source URL and source hash. Canonical UTC dates may differ from the local-calendar date in an offset timestamp; the instants must be identical.

**20 events correct; 10 briefings correct. Zero wrong-company items, unsupported statements, wrong numbers or wrong dates.**

| Company | Orgnr | Event ID | Published label | Verdict |
|---|---|---:|---|---|
| YIELDSTONE CAPITAL AS | 929098463 | 18631711 | Registry update recorded | correct |
| BERGSFJORD HOLDING AS | 999196462 | 22091037 | Registry update recorded | correct |
| FOSDALTUNET AS | 925853488 | 18009455 | Workplace registry update recorded | correct |
| CL BYGG & EIENDOM AS | 917283109 | 21597332 | Registry update recorded | correct |
| SAG AS | 989028367 | 23234003 | Registry event recorded (type unspecified) | correct |
| BERGEN CONTAINER TRANSPORT AS | 919038438 | 20122170 | Registry update recorded | correct |
| RØRLEGGERMESTER TORSTEIN SOLLI AS | 983486703 | 18717774 | Registry update recorded | correct |
| BORG BIERSTUBE AS | 924912758 | 18878037 | Workplace registry update recorded | correct |
| RØRLEGGERMESTER TORSTEIN SOLLI AS | 983486703 | 20920645 | Workplace registry update recorded | correct |
| HEIANE LEGESENTER AS | 915118305 | 20347081 | Workplace registry update recorded | correct |
| DRAGEHAUGEN VERDI AS | 917998787 | 22485843 | Registry event recorded (type unspecified) | correct |
| BRIDGE TECHNOLOGIES CO AS | 987002808 | 18996423 | Workplace registry update recorded | correct |
| WIRGENESVEI 3 AS | 930219746 | 17913271 | Workplace registry update recorded | correct |
| BIKE2WORK AS | 921596154 | 22565467 | Registry event recorded (type unspecified) | correct |
| POLARDC DRA02 AS | 936106536 | 22013579 | Entity registration recorded | correct |
| HEMO SOLSKJERMING AS | 924910275 | 21400259 | Registry update recorded | correct |
| LANDBRUKETS HUS SA | 966443960 | 20320580 | Workplace registry update recorded | correct |
| JAR HELSE AS | 979973969 | 20388024 | Registry update recorded | correct |
| RØRLEGGERMESTER TORSTEIN SOLLI AS | 983486703 | 18509059 | Workplace registry update recorded | correct |
| MYNT OG EIENDOM BESSAKER AS | 912823970 | 21932031 | Registry update recorded | correct |

The generic entries assert only what the record shows. Missing details do not become board changes, account events or employment changes. The unspecified Ukjent records remain explicitly unspecified. Subunit updates retain exact-parent source proof; no subunit number is mislabelled as its parent number.

| Briefing | Orgnr | Sentences | Verdict |
|---|---|---:|---|
| MUFFINS AS | 996233391 | 4 | correct |
| SAMEIET BORGÅSEN 1 | 998138558 | 6 | correct |
| LAU CAPITAL AS | 927661683 | 4 | correct |
| TUENESET AS | 991807209 | 5 | correct |
| TERON AS | 889320532 | 5 | correct |
| FOSS-EIK EIENDOM AS | 985868972 | 5 | correct |
| ELEKTROKOMPETANSE AS | 989916319 | 6 | correct |
| SNUGGERUD TRANSPORT AS | 997927885 | 5 | correct |
| SAMEIET SANDVIKSVEIEN 44 D | 828095382 | 5 | correct |
| BRØDRENE WILHELMSEN HOLDING AS | 889146192 | 4 | correct |

Every briefing sentence was checked against its cited values: legal identity, municipality/founding year, SSB industry title, source-native purpose, company-only amounts and annual period, rounded revenue percentage, employee count, workplace records, major-event scope and section-state gaps. Losses remain neutral. The sample includes both rising and falling revenue, a company with no revenue claim, registered employees and a major postal-address event.

[Raw event records and complete evidence](event-review.json), [briefing texts and cited input values](briefing-review.json), [six readable examples](EXAMPLES.md).