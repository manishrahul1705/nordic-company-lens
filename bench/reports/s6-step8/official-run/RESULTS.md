# Step 8 official README command check

Fresh local clone of commit `1909653` with `uv sync --frozen`; application credential, search, and model environment variables were removed. `NAV_API_TOKEN` was absent. The 100 valid IDs were random records from the public BRREG Enhetsregister API and are not present in `bench/inputs`; the file also contains `NOT-AN-ORGNR`, `123456789`, and a whitespace-only line. Input SHA-256: e42b962027dd5839e6c9b0ba396481421fa7ec07ef9ccf6d82cb898e01848a8b.

The exact README command was run twice without modification and used the same state folder:

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --profiles-output out/profiles.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

| Run | Wall time | HTTP requests | Envelopes | Claim changes | Observation changes |
|---|---:|---:|---:|---:|---:|
| First | 248.0 s | 935 | 103 | 0 | 0 |
| Same command, same state | 281.3 s | 965 | 103 | 0 | 48 |

Each run emitted exactly one output per input, including one failed result for each invalid line. `scripts/verify_output.py` passed individually for both outputs: 103 lines, valid schema and membership, 7,683 published claims, 337 cited source blobs verified, 103 checked syntheses, zero unverified synthesis values. The two-run comparison itself did **not** pass the strict byte-derived claim-ID/zero-observation check: 48 observation changes were section-state flips between `not_available` and `failed` under transient website failures; the published claim values had zero changes and the normal change list was empty. The second run did reuse the same state directory and retained source blobs. This is environmental/source availability churn, not a clean zero-observation refresh.

Both runs used 935 / 965 requests for 103 records and stayed within the per-company and global request/time caps. Search was disabled and the application credential variables were absent.

