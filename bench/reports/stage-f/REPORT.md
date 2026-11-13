# Stage F TED transport trial

**GATES FAILED: no merge or push.** Implementation commit007b34fb691eb02caf121e9da6dc19c3c5bc603a remains on more-websites for inspection; existing main stays e57bd749a9f8583bb655cca0710d3d360b295c29. Do not treat this as a passing submission candidate. No expectation or precision rule was changed to force recovery.

## Schema verified before coding

The Swagger UI loads /api-v3.yaml. The official OpenAPI notice schema has links.xml (an object mapping language keys to strings), plus pdf/pdfs/html/htmlDirect maps. An anonymous real search requesting publication-number,notice-type,links returnedHTTP200 for notice1-2026 with links.xml.MUL=https://ted.europa.eu/en/notice/1-2026/xml. Exact request/response, Swagger initializer/config and schema excerpt are retained here.

**The returned URL is the same form the old code constructed.** The initial hypothesis of a different download endpoint was not borne out by this response. Honoring the API link is still correct, but it does not itself cure202 responses. See schema-verification.json. Official schema:https://api.ted.europa.eu/api-v3.yaml; UI:https://api.ted.europa.eu/swagger-ui/index.html#/Search/search.

## Transport-only implementation

Request links in search fields; select links.xml.MUL per notice, with old constructed URL only when no link exists. Only HTTPS api.ted.europa.eu and ted.europa.eu TED URLs are accepted; no credentials in URL, no nonstandard port, redirects disabled. XML GETs keep application/xml,text/xml even on the API host. A202 is not-ready: at most2retries, delays3s then8s; exhausted responses remain extra_http_202 source failures. Every attempt is globally accounted; TED hard cap250 includes searches/downloads/retries. The existing total official-extra cap/lower pooled limits also still apply. Report includes TED status counts and failure URL/codes.

award_extract AST is identical before/after. Award-only can-standard/can-social filter, exact winner/buyer national ID,36month window,max10/company and exactly linked lot amount unchanged.28focused tests passed. Full suite **1,400passed,0failed564.47s**. Tests add returned-link/fallback,202success/exhaustion/backoff,250cap,XMLAccept,unsafeURLs and redirect refusal; existing precision fixtures unchanged.

## Frozen1,000 benchmark versus Stage E

README command,freshstate,no bulk override,credentials stripped,no search/LLM/paidAPI; inputSHA7ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782. Exit0,1,000envelopes/1,000profiles,offline site. Exact command/commit/timing in execution.json, raw state remains ignored at bench/runs/stage-f-live.

| Metric | Stage E | Stage F | Difference |
|---|---:|---:|---:|
| Websites | 113 | 111 | -2 |
| Social companies | 47 | 47 | +0 |
| Jobs companies | 2 | 2 | +0 |
| Activity companies | 1000 | 1000 | +0 |
| News companies | 7 | 4 | -3 |
| Article claims | 69 | 21 | -48 |
| GLEIF companies | 32 | 32 | +0 |
| TED companies | 0 | 1 | +1 |
| TED awards | 0 | 1 | +1 |
| Facts | 165484 | 165422 | -62 |
| HTTP total | 9173 | 9278 | +105 |
| HTTP mean including shared | 9.173 | 9.278 | +0.105 |
| HTTP max attributed | 40 | 40 | +0 |
| Wall seconds | 2286.951 | 2396.023 | +109.072 |
| Seconds per100 | 228.695 | 239.602 | +10.907 |
| Deadline hits | 0 | 0 | +0 |

No warnings or site warnings. TED requests231<=250, of which14HTTP200 and217HTTP202.76notices nominated. Most XMLs remain not-ready after retries; exact failed URL/codes in ted-metrics.json. HTTP9278<=19000;max40/company;deadlinehits0. Timing includes live source and host variability; no isolated causal timing claim.

| proof_type | Websites |
|---|---:|
| orgnr_on_page | 38 |
| jsonld_vatid | 5 |
| registry_declared_name_tier_a | 24 |
| legal_name_without_suffix_and_two_contacts | 9 |
| legal_name_and_registry_contact | 24 |
| unique_no_corroborated | 6 |
| registry_declared_hard_contact_tier_b | 3 |
| registry_phone_on_site | 2 |

## Every published award reviewed

One award, one company. Verdict **correct**,0wrong/0doubtful. No removals or acceptance changes needed.

| Org | Legal name | Notice | Matched role | Award date | Exact linked amount | Verdict |
|---|---|---|---|---|---:|---|
| 993919675 | FEIE- OG TILSYNSTJENESTER AS | 341549-2025 | winner | 2025-05-09 | NOK8,529,600 | correct |

Source:https://ted.europa.eu/en/notice/341549-2025/xml; retained SHA-256c76eb4b6052b2a5c7c7f5c650b43cbeb793333c5e713bff5b7d7800527590761. Exact XML identifier text:`<cbc:CompanyID schemeID="002">993919675</cbc:CompanyID>`; same Company element has name`Feie og tilsynstjenester AS`, organizationID`ORG-0004` and country`NOR`. SettledContractCON-0001 referencesTEN-0002; that LotTender referencesTPA-0002; that TenderingParty referencesORG-0004. TEN-0002 contains`<cbc:PayableAmount currencyID="NOK">8529600</cbc:PayableAmount>`. AwardDate2025-05-09Z is within36months. Notice totalNOK40,000,000 is NOT used. Full exact original XML company/contract/tender/party blocks and cited lexical spans are in award-review-verdicts.json; review pack additionally retains structural XML.

## Failed gates and observed losses

PASS activity1,000/deadlines0/suite0failed. **FAIL websites111<113 and articles21<69.** No remeasurement or rule change to force a pass. Saved diagnostics show three lost websites (Tensio,Danseinformasjonen,Bike2Work) and one gain, net-2. Tensio's contact proof page timed out; Danseinformasjonen's declared URL/host variants timed out and subsequent name-guess proof remained insufficient; Bike2Work had TLS/url-refusal and redirect-without-identity diagnostics. See coverage-loss-diagnostics.json and lost-items.json for exact errors.

Article losses are Feie- og Tilsynstjenester11->0(website_connect_error),Tensio28->0(website_check_incomplete),Danseinformasjonen9->0(website_check_incomplete),total48. These source failures occur in unchanged website/news collection, before the later TED requests; they are observed live failures, not evidence to loosen proof. Gates still fail regardless of inferred cause. No exceptions or output edits were used.

## Delivery

Keep tested transport commit on branch for review, preserve evidence and log the failed gate. Do not merge. Main in the same bench/cache/stage-a-main clone remains e57bd74. No push. README/SUBMISSION retain Stage E measurements because Stage F is unapproved by its gate. No credentials/raw downloads committed.
