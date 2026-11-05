# Official README command validation

Validated from a fresh local clone of commit `1d96e04d32f12cfd7e38e7da59f0d772a464be93`, with application credential/search environment variables absent. `uv sync --frozen` passed.

Exact README command, run twice without modification:

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --profiles-output out/profiles.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

The input contained 100 distinct, checksum-valid identifiers selected at random from 800 records returned by eight randomly selected pages of the public BRREG Enhetsregisteret API, plus three invalid lines (`NOT-AN-ORGNR`, `123456789`, and whitespace-only). None of the 100 valid identifiers occurs in `bench/inputs`. Input SHA-256: `6635ddfc9bf22b70f2adccea0b0ab6db156005f6749a8d6ccde545f103780681`.

| Run | Wall time | HTTP requests | Envelopes | Profiles | Changes | Observation changes | Verification |
|---|---:|---:|---:|---:|---:|---:|---|
| First command | 183.627 s | 816 | 103 | 103 | 0 | 0 | Pass: 103 lines, schema valid, 6,937 published claims, 319 source blobs checked, 669 cited template sentences, zero unverified values |
| Same command, same state directory | 154.211 s | 816 | 103 | 103 | 0 | 0 | Pass: identical claim IDs, zero changes and observations, 103 refresh lines |

All three invalid lines each produced exactly one envelope and one profile, with every enabled section marked `failed`. The run report had no warnings or deadlines. Each run stayed below the requested 2,000 HTTP / 2,700 seconds per 100 inputs. The application’s stricter limits were 1,854 requests for 103 records and 2,400 seconds configured (2,472-second hard scaled cap).

`scripts/verify_output.py` passed on the first output. It also passed with `--first out/first-run.jsonl --second out/envelopes.jsonl`; this independently checked membership, schema, evidence, identical claim IDs, and zero changes. The first output copy was only for verification. Both actual invocations used the exact README command with no extra flags. The automatic snapshot `out/state/latest-envelopes.jsonl` was present and used by run 2. The targeted implicit-refresh test also changes a role from “Person One” to “Person Two” and verifies the old/current values and retained evidence; an identical next snapshot reports zero changes.

The repository’s `OUTPUT_CONTRACT.md`, `docs/RULES_COMPLIANCE.md`, and input tests describe plain lines and JSONL; JSONL objects use the field `organisation_number`. No separate starter-kit format document exists in this checkout. The README documents plain text for the one-command run and explicitly states JSONL compatibility.
