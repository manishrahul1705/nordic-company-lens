# Evaluation and smoke checks

Install the locked dependencies and run the offline suite:

```sh
uv sync --frozen
uv run pytest -q
```

Tests cover input membership and multiplicity, identity checks, budgets and cancellation, envelope shapes, evidence provenance, refresh, website safety, NAV authentication and recovery, output verification, financial comparability and cited synthesis. Local fixtures and mocked transports keep the suite independent of live source availability.

## Resource defaults

The default time budget is 2,400 seconds. Crawl time is bounded by the deadline fraction and the reserved finalisation work; optional site generation is skipped if it cannot fit. The request budget derives from unique input identifiers unless explicitly overridden. Default output safety ceiling is 256 MiB. Consult `uv run signalpost run --help` for controls; inspect report states rather than treating a successful exit as source completeness.

NAV uses a separate connection pool and an adaptive time cap of min(900 seconds, 40% of the run budget), unless overridden. Its declared index only nominates candidates: published ads require live exact-company or listed-subunit proof. Missing, stale or unusable indexes trigger feed fallback. Incomplete discovery never establishes absence.

## Live registry smoke check

```sh
uv run signalpost run --organisations tests/fixtures/ci20.jsonl --bulk tests/fixtures/ci20.csv --output out/smoke.jsonl --report out/smoke-report.json --expected-count 20 --time-budget-seconds 180 --no-websites --no-hiring --no-public-activity
uv run python scripts/verify_output.py --first out/smoke.jsonl --organisations tests/fixtures/ci20.jsonl --count 20 --state-dir state --report out/smoke-report.json --require-clean
```

The public fixtures provide bulk identity rows; roles, subunits and accounts are requested live. Website, NAV and public-activity checks are explicitly disabled for this smoke command. The runner should emit an envelope for every input record even when sources fail. The separate `--require-clean` verifier is stricter: it checks section success, exceptions, deadlines, warnings, membership, evidence and output bounds. Network failures can therefore fail verification despite a successful runner exit.

GitHub Actions defines Ubuntu `tests` and `live-20` jobs using frozen installation. See the [Actions page](https://github.com/manishrahul1705/nordic-company-lens/actions) for results after the repository is pushed. Local validation does not establish hosted CI success or official evaluator acceptance.

## Output verification and refresh

The verifier checks schemas, input membership/order, claim evidence, stored-body hashes and verbatim spans. It also validates synthesis citations and values when present. Verification uses local blobs and makes no network requests.

```sh
uv run signalpost run --organisations batch.jsonl --bulk registry.csv --output out/first.jsonl --report out/first-report.json
uv run signalpost run --organisations batch.jsonl --bulk registry.csv --output out/second.jsonl --report out/second-report.json --previous out/first.jsonl
uv run python scripts/verify_output.py --first out/first.jsonl --second out/second.jsonl --organisations batch.jsonl --count 100 --state-dir state
```

Set the verifier count to your input membership. Keep source blobs, including original support for carried-forward claims. Fixed-source refresh should preserve claim IDs; live sources can legitimately change. Inspect both sides of each reported company event.

The optional `--profiles-output` writes separate raw profiles from the same verified facts. All seven evaluator flags are documented in the [README](../README.md); envelope evidence remains unchanged. Parsing compatibility alone does not establish an official score.

## Sampling and bulk preparation

The sampling helper accepts the public [company-universe archive](https://builderr.ai/signalpost-company-universe-2025.jsonl.gz), verifies its pinned hashes and samples with a fixed seed:

```sh
uv run python scripts/sample_universe.py --universe downloads/universe.jsonl.gz --output out/batch100.jsonl --count 100 --seed 20261013
uv run python scripts/extract_bulk.py --bulk downloads/registry.csv --batch out/batch100.jsonl --output out/registry100.csv
```

Obtain the bulk snapshot from the [official registry CSV endpoint](https://data.brreg.no/enhetsregisteret/api/enheter/lastned/csv). The extractor accepts plain/gzip CSV; missing rows retain live fallback. Downloaded snapshots, generated outputs and local evidence are ignored by git.

## Offline site checks

Site tests exercise envelope shapes, escaping, safe links, evidence and citations, deterministic output and isolated rendering failures. For manual review, open generated profiles at desktop and mobile sizes, check search, comparison, keyboard navigation and evidence controls, and verify local-file loading. These checks do not constitute accessibility certification.

See [sources](SOURCES.md) for data terms and [limitations](LIMITATIONS.md) for incomplete-coverage risks. No historical run measurements or official score are asserted by this guide.
