# Fixed benchmark

Run `powershell -File scripts/bench.ps1 -Size 100` on Windows or
`bash scripts/bench.sh --size 100` on Linux/macOS. Use size 20 for the first
20 companies. Both wrappers install with `uv sync --frozen`, use the evaluator
flags, retain all production budget defaults, remove API key/NAV credential and
model selector variables from the child environment, and create fresh
state under `bench/runs/<UTC timestamp>-<short commit>/`. Nothing is reused from
an earlier run's state. Runtime files and caches are ignored by git.


The committed 100-company JSONL/CSV are byte-identical to the comparison inputs;
20 is its first 20 records and corresponding CSV subset. `inputs/MANIFEST.txt`
pins both sizes. Preserve file bytes, including line endings. The runner checks
hashes and records the commit, dirty status, exact command, input hashes, process
exit, UTC times and measured wall time in `execution.json`. Each run retains
its inputs, envelopes, raw profiles, report, logs, source state, site and scoreboard.

`python scripts/scoreboard.py --envelopes RUN/envelopes.jsonl --report
RUN/report.json --profiles RUN/profiles.jsonl --output RUN/scoreboard.json`
scores existing outputs. It automatically reads sibling `execution.json` for
process wall time, or falls back to report runtime with an explicit source label.
Counts match the comparison definition: distinct available non-null
(organisation, field, value, reporting period) tuples; reported zero/false count,
duplicate facts do not. Social links are excluded from website fact totals.
Social states are derived from links and website scope because there is no
independent social source section. Native states and raw-profile states are
separate; budget/deadline error conditions may overlap native states. Latest-year
accounts require an available non-null non-history account claim with fiscal year;
the registry latest-year match is counted separately. The website budget count
counts companies once, even if their section contains multiple matching errors.

Live APIs, DNS, TLS, robots and source content can change; a frozen cohort is not
a frozen network replay. An available activity section may include registry
events; it is not necessarily company-website news. Scoreboards are coverage
measurements, not wrong-company audits or proof of exhaustive source coverage.

The manual GitHub workflow accepts 20, 100 or 1000 and uploads `bench/runs/` even
after a failure. It has no automatic triggers and is not dispatched by local runs.
The optional 1000 size samples the same pinned universe with seed 20261103 and
streams a current BRREG subset into `bench/cache/inputs/1000/` on first use.
That expanded bulk snapshot is not the committed fixed 100-company snapshot;
its hashes, source retrieval metadata and exact input bytes accompany each run.
Reuse that cache for subsequent comparable 1000 runs, or deliberately archive
and replace it when establishing a new baseline. Missing bulk companies retain
the production live fallback. Preparing this size requires network access.

Input registry data is attributed to Bronnoysundregistrene under NLOD 2.0.
NAV and company content retain their terms; see [source policy](../docs/SOURCES.md).
