# Stage C: evaluator CLI resilience

Only --organisations and --output remain required. Profiles, report and offline site default to out/profiles.jsonl, out/report.json and out/site. Unknown arguments are ignored, warned about on stderr and recorded in the report. Abbreviation is disabled so invented flag prefixes cannot silently change known settings. Known option validation remains intact.

The report records effective feature switches, suffix-contact proof, zero search queries/cost, requested/effective synthesis, LLM calls, pooled/per-company request caps, NAV index build/mode, ignored arguments and output paths. Proof rules, source collection and scoring are unchanged.

## Evaluator cases

All four cases use the frozen bench/inputs/20 cohort with mocked external HTTP and the real CLI, runner and output writers. Each produces 20 envelopes, 20 profiles, a non-empty report and an offline site (index and comparison pages).

| Command | Result |
|---|---|
| Only organisations/output | PASS |
| README command | PASS |
| README command plus three invented flags | PASS, warnings and tokens recorded |
| README command without site-dir | PASS, default site produced |

A separate test verifies disabled switches and auto-to-template reporting.

## Live 100-company comparison

Both runs use the README settings, fresh state, the same frozen input, default budgets and stripped credentials. Before is a clean local clone of 11f0d38; after tests the Stage C working-tree patch saved as runtime.patch and runtime-source.json.

| Metric | Before | After |
|---|---:|---:|
| Exit | 0 | 0 |
| Envelopes/profiles | 100/100 | 100/100 |
| Identity/people/locations/financials | 100/100/85/100 | 100/100/85/100 |
| Website/social/jobs/activity/news | 13/5/0/100/0 | 13/5/0/100/0 |
| Published claims | 16,741 | 16,741 |
| HTTP | 992 | 993 |
| Wall seconds | 250.390 | 235.333 |
| Deadline hits | 0 | 0 |

Every published claim ID is identical, with zero different fields. Sorted ID digest for both: 1d44afb3caaee795dd5a6bcbc7699b1755a4d7d8185cf1c475a4d9cd3a5f1c67. The extra live request changes no published result. See live-comparison.json and live-differences.json; raw benchmark outputs remain ignored under bench/runs.

The initial full suite exposed an existing report-unit-test DummyConfig without the new optional attribute. Report warning assembly now defaults that absent attribute to an empty list; the existing test and expectations were not changed. This metadata-only compatibility correction follows the live comparison; final-runtime.patch/source.json record it separately.

## Merge target

Use the existing main worktree bench/cache/stage-a-main, whose HEAD before this merge is 5e16dc4539667904750cc8aaad628e3aa1fd7107. Make a normal merge preserving it as first parent. No push.

## Final validation

Full suite: **1387 passed, 0 failed in 418.54 seconds**. Existing fixtures/expectations unchanged. All five new Stage C tests pass.
