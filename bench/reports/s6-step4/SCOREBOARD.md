# S6 Step 4 scoreboard

Search OFF; benchmark credentials stripped. Counts are available companies.

| Section | Baseline 6163e09 (100) | Step 0 (100) | Step 1 (100) | Step 2 (100) | Baseline 6163e09 (1000) | Final flags OFF (1000) | Final flags ON (1000) |
|---|---:|---:|---:|---:|---:|---:|---:|
| identity | 100 | 100 | 100 | 100 | 1000 | 1000 | 1000 |
| people | 100 | 100 | 100 | 100 | 997 | 997 | 997 |
| locations | 85 | 85 | 85 | 85 | 774 | 774 | 774 |
| financials | 100 | 100 | 100 | 100 | 999 | 999 | 999 |
| website | 10 | 11 | 11 | 11 | 69 | 73 | 100 |
| social | 4 | 5 | 5 | 5 | 32 | 35 | 40 |
| jobs | 1 | 1 | 1 | 1 | 3 | 3 | 3 |
| news/activity | 29 | 29 | 29 | 29 | 231 | 231 | 231 |

## Step decisions

| Step | Decision | Wrong-company count | Evidence / note | Commit |
|---|---|---:|---|---|
| 0 flags OFF | KEEP | 0 | `step0/`; 855 tests passed. | `7cab7e2` |
| 1 TLS/www and redirect proof | KEEP | 0 | `step1/`; 859 tests passed; 50 new claims manually reviewed; 823 HTTP, website budget exhaustion 6 to 14. | `1b99775` |
| 2 registry website/email candidates | KEEP (already implemented) | 0 | `step2/`; 859 tests passed; 54 registry claims / 22 events checked against official records; 825 HTTP. No candidate code change. | no new commit |


## Scale comparison and losses

All three 1000-company runs use the same frozen batch and registry hashes (`7ba0c3263afbca7dc5277f21f265e60484a937c59dc1871e9f1e0260d9bfe782`, `b5b3462dc1a27dbf5383ee91508b6126f6ccf9b3b8c9e190dd31d601413e1850`), search OFF, and credentials stripped. Baseline commit `6163e09`; final code commit `ee6674c`.

| Run | Website available | Social available | HTTP requests | Website budget exhausted | Deadlines | Wall seconds | Proof flags |
|---|---:|---:|---:|---:|---:|---:|---|
| Baseline 6163e09 | 69 | 32 | 6628 | 50 | 0 | 665.586 | OFF |
| Final, flags OFF | 73 | 35 | 7306 | 103 | 0 | 683.159 | OFF |
| Final, flags ON | 100 | 40 | 7421 | 102 | 0 | 630.292 | both ON |

Exclusive website loss buckets from captured diagnostics (counts of companies):

| Bucket | Baseline | Final OFF | Final ON |
|---|---:|---:|---:|
| DNS-missing | 135 | 222 | 266 |
| TLS/connect failure | 604 | 442 | 328 |
| fetched, no proof | 31 | 44 | 29 |
| no retained successful page | 16 | 13 | 20 |
| proof conflict | 39 | 48 | 56 |
| budget exhausted | 36 | 80 | 42 |
| robots/blocked | 34 | 42 | 42 |
| ambiguous | 26 | 26 | 107 |
| no candidates | 10 | 10 | 10 |

Loss buckets are exclusive diagnostics, not predicted recoveries. Full run metadata, summaries, raw differential review lists and saved loss reports are in `scale1000/` and `loss1000/`.

Step 4.3 1000 comparison: flags OFF gained 4 websites and 3 social profiles over baseline; flags ON gained 31 websites and 8 social profiles. No other section dropped. Manual review of Step 1 and Step 2 trial additions found zero wrong-company items. No further implementation changes were needed. Final test result: 859 passed (Step 2 validation run). Search remained OFF; no push.
