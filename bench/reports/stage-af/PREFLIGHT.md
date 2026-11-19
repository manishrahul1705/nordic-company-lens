# Stage AF: source preflight and scope decision

Historical preflight under the original zero-new-request scope. The user subsequently authorized signatur/prokura requests for all companies and group requests only for companies already flagged as group members. The implementation and live measurement supersede the pending decision below.

19 November 2026. The requested post-TED-re-probe full suite passed: **1,535 tests in 492.53 seconds**. The NAV investigation and its SUBMISSION reference were committed locally as **4b5a91e**. Nothing was pushed. Earlier runtime changes remain uncommitted.

## Source finding

The retained frozen 1,000-company run contains 1,000 successful entity-response bodies (997 normal entities, three deleted-entity records) and 997 successful roles-response bodies. The complete decoded JSON bodies were scanned, not just the existing extractor output.

| Requested information | Explicit data in fetched entity/roles bodies | New companies covered | New claims published |
|---|---|---:|---:|
| Parent identity and registered subsidiaries | None | 0 | 0 |
| Registered signatur/prokura | None; no relevant keys or SIGN/PROK role codes | 0 | 0 |

The entity bodies contain `erIKonsern` on 997 records: 75 true and 922 false. This is already published as the group-membership flag. It supplies no parent name/number or subsidiary identity. The roles bodies contain 4,140 appointments across ordinary director, board, accounting/auditing and related role types, without signatur or prokura declarations. Missing fields in this API are not evidence that the real company has no relationships or signing rights.

No extraction code was changed on the basis of a nonexistent field. No ownership relationship was inferred from names, ordinary role-holder entities, registered workplaces, or group membership. No signing right was inferred from a board/director appointment.

## Why additional requests are needed

BRREG documents separate routes on the same provider/host:

- `https://data.brreg.no/enhetsregisteret/api/konsernstruktur/{orgnr}` for group structure. [Official open-data documentation](https://data.brreg.no/enhetsregisteret/api/dokumentasjon/no/index.html).
- `https://data.brreg.no/fullmakt/enheter/{orgnr}/signatur` and `/prokura` for the public lookup variant. [Official Fullmakt documentation](https://data.brreg.no/fullmakt/docs/index.html).

A full three-call-per-company acquisition would add up to 3,000 attempts before retries to a 1,000-company run. Using the latest 8,953-request baseline, that projects 11,953 / 19,000 = 62.9% pooled use, versus 47.1%. Selective group requests may reduce that cost; these are projections, not measured runtime/cost promises. Existing per-company/global caps must remain unchanged. No dedicated endpoint calls have been made or enabled while the stated zero-new-request scope is unresolved.

`overordnetEnhet` must not be promoted to corporate ownership indiscriminately: the entity API documents it as an administrative superior in the public sector, while the subunit API uses it for the main registered entity. Registered workplaces are not automatically subsidiaries. A future group extractor must use an explicitly reported relation anchored to the requested company. A future rights extractor must preserve joint/conditional authority and must not treat possible signing roles as granted rights.

## Ten source reviews per family: withholding audit, not positive-claim review

There are no positive new claims to hand-review under the existing-data scope. The following ten companies were inspected for each family to verify withholding. Their own records explicitly report group membership but do not name any counterpart; their role records show appointments rather than signing-right grants. This does not substitute for the requested ten positive reviews after an implemented feature. Full source URLs, body hashes, JSON keys and role codes are retained in [preflight-abstention-review.json](preflight-abstention-review.json).

| Company | Group evidence and value | Signing-right evidence and value | Decision |
|---|---|---|---|
| MYKLEBUST MARITIME AS (981508734) | [Own entity](https://data.brreg.no/enhetsregisteret/api/enheter/981508734), `/erIKonsern=true`; no parent/subsidiary value | [Own roles](https://data.brreg.no/enhetsregisteret/api/enheter/981508734/roller), codes `DAGL, LEDE, MEDL, REVI`; no signatur/prokura value | Withhold; neither requested value is stated |
| NOTEK HOLDING AS (882749762) | [Own entity](https://data.brreg.no/enhetsregisteret/api/enheter/882749762), `/erIKonsern=true`; no parent/subsidiary value | [Own roles](https://data.brreg.no/enhetsregisteret/api/enheter/882749762/roller), codes `DAGL, LEDE, REVI, VARA`; no signatur/prokura value | Withhold; neither requested value is stated |
| ROLIDBAKKEN FUS BARNEHAGE AS (991247610) | [Own entity](https://data.brreg.no/enhetsregisteret/api/enheter/991247610), `/erIKonsern=true`; no parent/subsidiary value | [Own roles](https://data.brreg.no/enhetsregisteret/api/enheter/991247610/roller), codes `DAGL, LEDE, REGN, REVI`; no signatur/prokura value | Withhold; neither requested value is stated |
| KARLSEN AS (922069212) | [Own entity](https://data.brreg.no/enhetsregisteret/api/enheter/922069212), `/erIKonsern=true`; no parent/subsidiary value | [Own roles](https://data.brreg.no/enhetsregisteret/api/enheter/922069212/roller), codes `LEDE, MEDL, REGN, REVI`; no signatur/prokura value | Withhold; neither requested value is stated |
| EDSVIK INVEST AS (935327423) | [Own entity](https://data.brreg.no/enhetsregisteret/api/enheter/935327423), `/erIKonsern=true`; no parent/subsidiary value | [Own roles](https://data.brreg.no/enhetsregisteret/api/enheter/935327423/roller), codes `LEDE, REGN`; no signatur/prokura value | Withhold; neither requested value is stated |
| KV 2 EIENDOM AS (879309182) | [Own entity](https://data.brreg.no/enhetsregisteret/api/enheter/879309182), `/erIKonsern=true`; no parent/subsidiary value | [Own roles](https://data.brreg.no/enhetsregisteret/api/enheter/879309182/roller), codes `LEDE, MEDL, REVI`; no signatur/prokura value | Withhold; neither requested value is stated |
| VIVIFY GRUPPEN AS (928657523) | [Own entity](https://data.brreg.no/enhetsregisteret/api/enheter/928657523), `/erIKonsern=true`; no parent/subsidiary value | [Own roles](https://data.brreg.no/enhetsregisteret/api/enheter/928657523/roller), codes `LEDE, MEDL, REGN, REVI`; no signatur/prokura value | Withhold; neither requested value is stated |
| H1 CAPITAL AS (921678851) | [Own entity](https://data.brreg.no/enhetsregisteret/api/enheter/921678851), `/erIKonsern=true`; no parent/subsidiary value | [Own roles](https://data.brreg.no/enhetsregisteret/api/enheter/921678851/roller), codes `DAGL, LEDE, REGN`; no signatur/prokura value | Withhold; neither requested value is stated |
| BAKERIUTSALGET KROKSTADELVA AS (994919482) | [Own entity](https://data.brreg.no/enhetsregisteret/api/enheter/994919482), `/erIKonsern=true`; no parent/subsidiary value | [Own roles](https://data.brreg.no/enhetsregisteret/api/enheter/994919482/roller), codes `DAGL, LEDE, MEDL, REVI`; no signatur/prokura value | Withhold; neither requested value is stated |
| FLEXISPUNT AS (927146487) | [Own entity](https://data.brreg.no/enhetsregisteret/api/enheter/927146487), `/erIKonsern=true`; no parent/subsidiary value | [Own roles](https://data.brreg.no/enhetsregisteret/api/enheter/927146487/roller), codes `DAGL, LEDE`; no signatur/prokura value | Withhold; neither requested value is stated |

## Evidence and validation

- [Full-suite output](pytest-before-af.txt).
- [Full entity/role key inventory](source-inventory.json).
- [Role types and code inventory](role-type-inventory.json).
- [Ten-company preflight reviews](preflight-abstention-review.json).
- The strict integrity verifier passed on the retained 1,000-envelope output: 165,952 published claims, 4,086 stored source blobs, zero unverified synthesis values; exit 0 in 213.811 seconds. See [verifier output](baseline-strict-verifier.txt). As in the earlier strict runs, this is schema/membership/evidence/synthesis verification without `--require-clean`; the known local section timeout is unchanged. This baseline verification is not a claim that Stage AF was implemented.

## Pending decision

Permit the separate BRREG requests to implement and measure Stage AF, or retain the zero-new-request scope and publish no unsupported claims. A source/request scope clarification was requested; no inference or acceptance rule has been relaxed.
