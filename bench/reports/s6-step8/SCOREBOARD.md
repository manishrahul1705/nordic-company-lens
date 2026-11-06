# S6 Step 8 scoreboard

Work stayed on `main`, starting from the submitted Step 8 code `1909653`. No push. Search was OFF and credentials were removed in both final benchmark runs. The two failed-network runs are excluded.

## Coverage and runtime

| Section | Step 7 baseline | Final full fallback run 2 | Final full fallback run 3 |
|---|---:|---:|---:|
| Identity | 1000 | 1000 | 1000 |
| People | 997 | 997 | 997 |
| Locations | 774 | 774 | 774 |
| Financials | 999 | 999 | 999 |
| Website | 79 | 83 | 83 |
| Social | 33 | 36 | 37 |
| Jobs | 3 | 3 | 3 |
| News/activity | 231 | 231 | 231 |
| HTTP requests | — | 7922 | 7953 |
| Wall time | — | 1128.419 s (18.81 min) | 1340.399 s (22.34 min) |
| Deadline hits | — | 0 | 0 |
| Wrong-company findings | — | 0 | 0 |

Website mean = **83**; mean runtime = **1234.409 s (20.57 min)**. The DNS fallback gate passes: website mean is at least the Step 7 level of 83, and both runs are below 45 minutes per 1000. Social coverage varied by one company, within the Step 6 measured noise band of four. Step 8 is KEEP under the stated gate.

An earlier valid-network precursor run with the narrower top-three NXDOMAIN recheck produced 78 websites in 794.737 s; it is not counted in the final mean because it did not use the restored full fallback. It explains why the final code was remeasured twice.

## DNS fallback

| Metric | Run 2 | Run 3 |
|---|---:|---:|
| Resolver attempts | 17,715 | 16,989 |
| Domains recovered | 49 | 50 |
| Aggregate resolver wait | 8,731.972 s | 8,770.904 s |
| Max per company | 10.0 s | 10.0 s |
| Companies that used fallback | 912 | 915 |

Both public resolver calls retain a 2-second timeout, run concurrently, and silently stop when UDP/53 is blocked. Per-run positive answers are cached. The blocked-UDP test passed in the focused DNS suite. Resolver wait is summed across concurrently processed companies, so its total can exceed wall time.

## Group websites

The current group-site review has five cases. Four are available only because their proof page includes the exact company org nr; the Wullum candidate is withheld as ambiguous. See [GROUP_WEBSITE_REVIEW.md](GROUP_WEBSITE_REVIEW.md) for each page and excerpt. All five were manually reviewed; no wrong-company website item was found.

## Wikidata social claims

All five current Wikidata-sourced social claims were reviewed: three for LOFOTPOSTEN AS and two for STIFTELSEN DANSEINFORMASJONEN. Each has exact P2333 and a legal-name-matching handle, or a direct verified-site link. Verdicts: 5 correct, 0 wrong, 0 unsure. See [WIKIDATA_SOCIAL_REVIEW.md](WIKIDATA_SOCIAL_REVIEW.md).

## Differential review

Against Step 7, every new/changed website and social claim was checked from captured evidence; additions and authority changes were correct. The one previously emitted group website Wullum Eiendom is now withheld. Nerland Autosalg's prior site and social links were absent in benchmark 2; they reappeared with exact company proof and linked social pages in benchmark 3. Two further inter-run website absences, Ensure IT AS and Støren Dyreklinikk AS, have explicit DNS timeout/unavailable candidate diagnostics. Full classifications are in [DIFFERENTIAL_REVIEW.md](DIFFERENTIAL_REVIEW.md). Final-code run-to-run review: 0 wrong-company items; DNS explains the two disappearances.

## NAV public token and manual audit

With `NAV_API_TOKEN` absent and no credentials in the environment, both final benchmark reports record one HTTP 200 request to NAV's official `https://pam-stilling-feed.nav.no/api/publicToken` endpoint. This is NAV's published public token, cached for that run; the response value is not in outputs or logs. The bundled NAV index was complete at version `nav-20261104T071654.150483Z-v1` (6 feed pages, 4,145 indexed items). Live detail checks: 9 in run 2 and 10 in run 3. Each run published 3 jobs. The 20-company manual Arbeidsplassen audit found no active exact-scope ads missed; the three emitted ads were individually checked as ACTIVE, unexpired and attached to the company or registered subunit. See [NAV_AUDIT.md](NAV_AUDIT.md).

## Fresh-clone README command

`uv sync --frozen` and both exact README invocations succeeded in a fresh local clone with application credentials/search disabled. Each produced one envelope per 100 valid + 3 invalid input lines, within budget. Both outputs passed individual schema, input-membership, 337-blob and 103-synthesis verification. Run 2 had zero claim-value changes and an empty normal changes list, but 48 section observations changed between `not_available` and `failed` when live websites timed out or had DNS failures; therefore this was not a strict zero-observation refresh. Timings and exact command are in [official-run/RESULTS.md](official-run/RESULTS.md).

## Tests and commits

The first full test invocation without a workspace temp base failed during temporary-directory setup because `%LOCALAPPDATA%\Temp\pytest-of-Manish` was inaccessible. The sandbox run then had 927 passes and 3 failures: two evaluator tests saw registry source errors in the network-restricted sandbox, and one NAV boundary test still asserted the old blocked-mode behavior. That test now checks fail-closed behavior when both the public token and candidate ad page cannot be verified. With network access and a workspace-local temp base, the full suite passed: **930 passed in 330.39 seconds**. The focused evaluator/NAV subset passed **21 tests**.

Code commit: `1909653` (public NAV fallback and full DNS fallback), authored by Manish Rahul <manishrahul1705@gmail.com>. The final evidence/test commit is listed in the response. Nothing was pushed.
