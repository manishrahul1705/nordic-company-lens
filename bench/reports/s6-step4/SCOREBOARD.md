# S6 Step 4 scoreboard

Search OFF; benchmark credentials stripped. Counts are available companies.

| Section | Baseline 6163e09 (100) | Step 0 (100) | Step 1 (100) | Step 2 (100) | Baseline 6163e09 (1000) | Final flags OFF (1000) | Final flags ON (1000) |
|---|---:|---:|---:|---:|---:|---:|---:|
| identity | 100 | 100 | 100 | 100 | pending | pending | pending |
| people | 100 | 100 | 100 | 100 | pending | pending | pending |
| locations | 85 | 85 | 85 | 85 | pending | pending | pending |
| financials | 100 | 100 | 100 | 100 | pending | pending | pending |
| website | 10 | 11 | 11 | 11 | pending | pending | pending |
| social | 4 | 5 | 5 | 5 | pending | pending | pending |
| jobs | 1 | 1 | 1 | 1 | pending | pending | pending |
| news/activity | 29 | 29 | 29 | 29 | pending | pending | pending |

## Step decisions

| Step | Decision | Wrong-company count | Evidence / note | Commit |
|---|---|---:|---|---|
| 0 flags OFF | KEEP | 0 | `step0/`; 855 tests passed. | `7cab7e2` |
| 1 TLS/www and redirect proof | KEEP | 0 | `step1/`; 859 tests passed; 50 new claims manually reviewed; 823 HTTP, website budget exhaustion 6 to 14. | `1b99775` |
| 2 registry website/email candidates | KEEP (already implemented) | 0 | `step2/`; 859 tests passed; 54 registry claims / 22 events checked against official records; 825 HTTP. No candidate code change. | no new commit |
