# Nordic Company Lens

Nordic Company Lens researches Norwegian companies using official registries and bounded company-owned sources. It checks company identity, publishes evidence-linked facts and cited template summaries, and can generate searchable offline profiles. The Python import package and console command remain `signalpost`.

Builds on an earlier Signalpost entry (signalpost-agent), with permission.

## Install

Requires Python 3.12+ and [uv](https://docs.astral.sh/uv/). From this repository:

```sh
uv sync --frozen
```

## Run

This command uses the included company inputs and registry fixture. It includes all seven evaluator flags and enables website, hiring and public-activity research:

```sh
uv run signalpost run --organisations tests/fixtures/ci20.jsonl --bulk tests/fixtures/ci20.csv --output out/envelopes.jsonl --profiles-output out/profiles.jsonl --report out/report.json --run-id nordic-company-lens --expected-count 20 --websites --hiring --public-activity --site-dir out/site --synthesis template --search-max-queries 0 --max-cost-usd 0
```

For your own batch, replace the input paths and set `--expected-count` to its record count. The seven evaluator flags are `--organisations`, `--bulk`, `--output`, `--profiles-output`, `--report`, `--run-id` and `--expected-count`. Omit `--bulk` for live registry lookup. Source research requires internet access; the offline tests use local fixtures.

Input accepts organisation-number JSONL, JSON lists/objects or plain lines. Identifiers are normalized and checksum-validated. Output preserves input order and duplicates; duplicate companies share research. Invalid inputs retain explicit failed envelopes. Add `--previous prior.jsonl` for refresh, or `--deduplicate` to request unique output identifiers.

## Outputs

- `out/envelopes.jsonl`: validated company envelopes, with verified claims, evidence, section states and cited summaries. The default shape is `union`; `contract` and `reference` are also supported.
- `out/profiles.jsonl`: separate evaluator-compatible raw profiles from the same verified facts.
- `out/report.json`: membership, source states, errors, requests, budgets, timing and cost.
- `out/site/`: optional static searchable company profiles with evidence excerpts. Open `index.html` locally. Site generation may be skipped if remaining time is insufficient.
- `state/`: local evidence bodies, caches and progress. Keep the matching state when verifying evidence or carrying facts forward.

Exit zero means output was written for parsed input records. Inspect report warnings and source states: `complete` does not mean every source succeeded. Missing or unavailable facts remain explicit, without invented evidence. Refresh distinguishes supported company changes from source failures and retains original provenance for carried-forward facts.

## Sources and licences

Registry identity, roles, subunits and accounts come from official Bronnoysundregistrene APIs or the supplied registry snapshot. Registry data is attributed under NLOD 2.0. Optional hiring uses the official NAV feed and live detail verification against the exact company or registered subunit. The bundled NAV index is declared discovery metadata; it does not replace live evidence.

Website research follows robots, public-IP, redirect, request and time limits. Published website facts require the documented company-identity proof. Social profile links can be recognised on accepted company pages; social platforms are not fetched. Public activity uses bounded company-site feeds/sitemaps and supported registry events. Bundled SSB KLASS industry titles retain CC BY 4.0 attribution to Statistics Norway.

Code and documentation use the [MIT licence](LICENSE). NAV, company websites and dependencies retain their own terms. See [source policy and dependency licences](docs/SOURCES.md) and [identity rules](docs/IDENTITY_RESOLUTION.md).

## Cost

The command above has **$0 provider cost**, uses no LLM and makes no paid search calls. Compute, storage and network costs are excluded. Summaries use deterministic templates; no live model adapter is shipped. Optional paid Brave search exists in the code but is disabled in this command by `--search-max-queries 0`. When configured separately, search only nominates candidates; published facts still require permitted-source verification.

## Limitations and checks

Strict identity rules and bounded discovery can miss genuine websites, jobs and activity. Bulk data and the bundled NAV index can age; stale or unusable indexes trigger feed fallback. API failures, robots restrictions, timeouts and budget caps leave explicit incomplete states. Website research has no browser renderer. Unknown trading names can escape NAV discovery, and name matching alone never proves employer identity. Financial comparisons abstain when entity, period, currency or units are incompatible. Source-reported text is not an independent assessment, and cited templates do not provide general semantic fact verification.

No coverage, performance or official evaluator score is claimed here. Run `uv run pytest -q` for the offline suite. The [evaluation guide](docs/EVAL.md) documents smoke checks and output verification. See also [schema](docs/DATA_SCHEMA.md), [agent loop](docs/AGENT.md), [refresh](docs/REFRESH.md) and [limitations](docs/LIMITATIONS.md).
