# S6 Step 5 scoreboard

Started on main at `73d7902`. Search OFF and credentials stripped for all diagnostic/benchmark requests. No production behavior or dependency change. Both experimental flags remain default OFF; no push.

| Section | Prior OFF 1000 | Prior both ON 1000 | Suffix-only 100 | Suffix-only 1000 trial |
|---|---:|---:|---:|---:|
| identity | 1000 | 1000 | 100 | 1000 |
| people | 997 | 997 | 100 | 997 |
| locations | 774 | 774 | 85 | 774 |
| financials | 999 | 999 | 100 | 999 |
| website | 73 | 100 | 11 | 73 |
| social | 35 | 40 | 5 | 36 |
| jobs | 3 | 3 | 1 | 3 |
| news/activity | 231 | 231 | 29 | 230 |

**Decisions:** domain/location ON is not kept because two ownership cases remain unsure. Suffix/contact ON passes the 100 gate but is ROLLBACK at 1000: news/activity falls 231 to 230. Both production defaults therefore remain OFF. No runtime patch was applied, so rollback consists of rejecting the trial configuration, not reverting source changes.

The lost activity company is BERGEN VAKTMESTERTJENESTER AS (990412375): bnv.no and www.bnv.no recorded dns_unavailable during precheck; no website HTTP request was made for this company. Its website was consequently unverified and five dated articles were withheld. This is observed live-source variation, not proof that the suffix rule caused the loss. The strict no-drop gate still fails; no repeat was used to replace this failed trial.

100-company trial: 94.996 seconds, 827 HTTP requests, 15 company request-cap exhaustions, zero deadlines. 1000-company trial: 650.466 seconds, 7008 HTTP requests, 87 company request-cap exhaustions, zero deadlines. Frozen 1000 hashes match the earlier OFF/ON runs. Runtime code is still 73d7902; execution records mark the working tree dirty because the new diagnostic/report files were present.

Final tests: **859 passed in 147.93 seconds**. Initial sandbox run: 857 passed and two official-source smoke failures; the suite passed after allowing those existing network tests. No test or runtime code was edited.

## Ownership audit

Net +27 websites was 28 additions minus one removal. Net +5 social companies was six additions (11 URLs) minus one removal. All 39 added items have company, URL, exact saved proof excerpt, registry comparisons, hashes and a manual verdict in [OWNERSHIP_REVIEW.md](OWNERSHIP_REVIEW.md) / [ownership-review.json](ownership-review.json). Website verdicts: 26 correct, zero conclusively wrong, two unsure (Tensio and Lindas Naersenter); social: 11 correct. Suffix-only trial additions: 17 correct, zero wrong/unsure, recorded in suffix-only-1000/review.json.

## Ambiguity

107 = 26 + 89 entrants - 8 departures = 18 retained + 89 entrants. Of the 89 entrants, 45 were failed and 44 not available. All have a MEDIUM suffix-free-name observation but insufficient contacts or domain evidence. These are withheld observations rather than 89 established owner conflicts. Fifteen named examples and reasons: [AMBIGUOUS.md](AMBIGUOUS.md).

## TLS comparison

30 seeded recorded HTTPS failures, four arms, same Windows machine. HTTP responses: default 4/30, truststore 3/30, explicit certifi 4/30, curl 4/30; all have one HTTP 200. Truststore fixes zero default failures. Each arm still has three certificate failures and three other TLS errors. Default/certifi/truststore/curl respectively have 12/10/10/11 timeouts and 8/10/11/9 connection/protocol failures. Exact classes, complete messages/chains and native curl stderr: [TLS.md](TLS.md), [sample30.json](tls/sample30.json). Historical messages were not stored, so only contemporary retries provide exact messages. Truststore was not added to project dependencies or startup.

## Budget

The previous 80 exclusive budget losses were request-count ceilings, not time-budget expiry; previous total request-cap exhaustions were 103 OFF / 102 ON. The new trial has 87. All have zero company/global deadline errors; no per-company time budget exists. Therefore the requested >=80 time-budget trigger is false and no concurrent/4-second fallback trial was made. [BUDGET.md](BUDGET.md).

## Exclusive loss buckets at 1000

Order below: prior OFF / prior both ON / suffix-only rejected trial.

| Bucket | Prior OFF | Prior both ON | Suffix-only trial |
|---|---:|---:|---:|
| TLS-connect failure | 442 | 328 | 532 |
| all candidates DNS-missing | 222 | 266 | 134 |
| budget exhausted | 80 | 42 | 32 |
| proof conflict (other orgnr) | 48 | 56 | 48 |
| fetched but no proof | 44 | 29 | 15 |
| robots or blocked | 42 | 42 | 36 |
| ambiguous (name-only or competing candidates) | 26 | 107 | 113 |
| no retained successful company page | 13 | 20 | 7 |
| no candidates generated | 10 | 10 | 10 |

The TLS/connect loss bucket is a conservative grouping including connection and DNS/request timeout codes, not a count of certificate failures. Bucket priorities can move companies between categories; none is a forecast of recoverable coverage.

Production checkpoint: `73d7902`; this step adds the diagnostic script and durable evidence only. The final local evidence commit is reported in the response.
