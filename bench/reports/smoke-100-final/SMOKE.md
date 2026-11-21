# Final 100-company smoke

Source commit: `e1d271593c3830647da7951545a9b9519365bcb9` (Stage BB). Branch: audit-fixes.

Installation: `uv sync --frozen` succeeded. Run from repository root with unchanged defaults, fresh state and site discovery ON:

```sh
uv run --frozen signalpost run --organisations bench/inputs/100/batch.jsonl --output bench/runs/smoke-100-final-bc/envelopes.jsonl --report bench/runs/smoke-100-final-bc/report.json --state-dir bench/runs/smoke-100-final-bc/state --site-dir bench/runs/smoke-100-final-bc/site
```

Input: `bench/inputs/100/batch.jsonl`; 100 valid records, 100 unique organisation numbers, zero invalids or duplicates. Exactly 100 output envelopes match the input order, with no missing or duplicate results.

UTC start: 2026-11-21T10:55:39.1921064Z. UTC end: 2026-11-21T11:01:24.6640968Z. Observed wall time: **345.472 seconds**, including site build and process startup. Report crawl runtime: 313859 ms. HTTP requests: **1289**. Process exit: 0. Run status: **completed**. Deadline hits: 0. Warnings: [].

Strict verifier: **PASS**, exit 0, unchanged repository verifier:

```sh
python scripts/verify_output.py --first bench/runs/smoke-100-final-bc/envelopes.jsonl --state-dir bench/runs/smoke-100-final-bc/state --count 100 --organisations bench/inputs/100/batch.jsonl --report bench/runs/smoke-100-final-bc/report.json
```

```json
{"lines": 100, "schema_valid": true, "published_claims": 23806, "source_blobs_verified": 593, "synthesis_companies": 100, "synthesis_sentences": 274, "synthesis_unverified_values": 0}
```

The strict verifier checked membership, schema, stored evidence, attribution safety and report consistency. Full local envelopes, source blobs and site remain under `bench/runs/smoke-100-final-bc/`; source evidence is under `state/blobs/`. Large outputs and state are not committed. This artifact includes the original report and verifier output. Reproduction requires network access; public source availability and content can change. Passing verification checks captured evidence consistency, not an independent manual precision audit.

Input SHA256: `54f5c4254b5d61a969ed6ec5969fab905e45d947f920a8f8cdcb71e575b159f7`.
Envelope SHA256: `cb9d92f442473128bf81486af1f4a70e488e78985529d7d3ed5d0bf23d4d43d9`.
