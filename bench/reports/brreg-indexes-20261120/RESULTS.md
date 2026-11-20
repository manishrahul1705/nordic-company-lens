# Official BRREG index rebuild - 20 November 2026

Both current bundled indexes are derived directly from the official full Enhetsregisteret dataset, replacing the competition-archive derivatives. No runtime request is added. No raw download is committed. No push.

## Source and reproducible build

Contains data under [NLOD 2.0](https://data.norge.no/nlod/en/2.0) distributed by Brønnøysundregistrene. [Official licensing](https://www.brreg.no/en/use-of-data-from-the-bronnoysund-register-centre/datasets-and-api/).

- Source: https://data.brreg.no/enhetsregisteret/api/enheter/lastned/csv
- Retrieved: 2026-11-20T01:21:14.581183+00:00
- Official snapshot filename: `enheter_2026-11-19T04-26-05.995209546.csv.gz`.
- Download: 155,330,892 bytes; SHA-256 `f3f4f93d2e4c597c15b3d08193d0a055e0bcc788a858b8bec8fcf7e8438f1dba`.
- Source rows: **1,181,598** main entities, without cohort or legal-form filtering; zero invalid organisation numbers or empty names. Duplicate identities are rejected.
- Raw file: ignored `bench/cache/official-brreg-20261120/enheter.csv.gz`; not distributed. `download.json` here contains source metadata, not raw records or response cookies.
- Underenheter was not needed for these main-entity indexes. Relationship exceptions continue to require explicit own-company registry claims, never inferred relationships.

```powershell
python scripts/download_brreg_index_source.py --directory bench/cache/official-brreg
python scripts/build_social_company_names.py bench/cache/official-brreg/enheter.csv.gz --download-manifest bench/cache/official-brreg/download.json
python scripts/build_registry_domains.py bench/cache/official-brreg/enheter.csv.gz --download-manifest bench/cache/official-brreg/download.json
```

The name builder selects organisation number and registered name, trims whitespace, validates checksums, rejects duplicate numbers, sorts and writes deterministic gzip/JSON. The domain builder normalizes the official `hjemmeside` field with the existing policy, groups by registrable domain and keeps at least two distinct organisation numbers. Neither contains page bodies or contact/person fields. Runtime handle normalization, relationship exceptions, ownership acceptance and shared-site vetoes are unchanged. Source metadata and output hashes are embedded/recorded in `data/social_company_names_build.json` and `src/signalpost/data/registry_domains_build.json`; runtime name-index pins were updated to the official dataset and index hashes.

## Before and after

| Index | Old rows | New rows | Old gzip bytes | New gzip bytes |
|---|---:|---:|---:|---:|
| Company names | 411,160 | 1,181,598 | 4,748,226 | 16,130,532 |
| Shared domains | 2,258 | 5,679 | 86,911 | 202,486 |

Names: **772,378 added organisation numbers**, **1,940 old numbers absent**, **1,804 changed name strings** among common numbers. Domains: **3,465 added**, **44 removed**, **455 changed owner sets** among common domains. Snapshot absence/name differences are not published as legal events or proof of company deletion. The new domain index represents 34,330 retained domain/number pairs from 113,836 valid website rows. See `index-comparison.json`.

## Saved-run replay

Baseline: `bench/runs/overnight-all-20261120`, frozen 1,000. Both control and official-index replays use the identical **304 saved pages**, no HTTP, the same extraction and final vetoes. The original saved run and evidence are not rewritten. `replay.py old` uses ignored backups of the old indexes; `replay.py new` uses the current bundled official indexes. Replay outputs remain ignored under `bench/runs/brreg-index-replay-20261120-{old,new}`. The committed report records the complete diff; reproduction of this saved-page experiment requires the original ignored run and, for control, old index backups (or their earlier Git versions).

The old-index control reproduces **167,200 claims, zero changes**. The official-index replay publishes **167,166 claims: 34 removed, zero added**. Every removal is for **TENSIO AS (922828172)**:

| Removed claim type | Count |
|---|---:|
| website | 1 |
| descriptions | 4 |
| social | 3 |
| phone | 1 |
| dated items | 25 |

The official shared-domain index lists `tensio.no` for other entities **TENSIO B.I.L. (923482806)** and **TENSIO TN AS (988807648)**. The existing group/shared-site guard therefore withholds these claims; no relationship exception or acceptance rule was loosened. See `change-diagnostics.json` and the complete `all_published_claim_changes` in `replay-new.json`.

| Coverage | Before | After |
|---|---:|---:|
| Verified websites | 115 | 114 |
| Social companies | 63 | 62 |
| Social claims (including registry social) | 129 | 126 |
| Brands | 19 | 19 |
| GLEIF companies | 142 | 142 |
| TED companies / awards | 6 / 20 | 6 / 20 |
| Hiring companies | 3 | 3 |
| Group companies / claims | 75 / 119 | 75 / 119 |
| Signatur | 765 | 765 |
| Prokura | 201 | 201 |

No name-index-only change survives publication in this replay. Named handle checks remain: hallmakergroup withheld, valdresost withheld (official spelling now VALDRES OST AS), RentHallGlobal allowed, scenehuset allowed. The replay is not a new live run or a new runtime estimate. Historical live wall time and request count remain 1,309.681 seconds / 11,477; acquisition was not repeated, and site files were not rebuilt.

## Verification

- **Full suite: 1,660 passed, one warning, 470.38 seconds**. Four official-builder checks were added to the previous 1,656. The warning is the existing pytest cache-write permission warning; no test failed. See `pytest.txt` and `pytest-timing.json`.
- An earlier restricted focused run had 107 passed / four temp-directory setup errors (WinError 5); those were environment permissions, and the full suite with required access passed all four builder tests as well. No acceptance logic was changed to pass them.
- **Unchanged strict integrity verifier PASS**: 1,000 envelopes, 167,166 claims, 5,155 source blobs, 2,570 synthesis sentences, **zero unverified values**, 187.79 seconds. Same integrity mode as previous stages, without the extra optional-source-health `--require-clean` gate. See `strict-verifier.txt` and `verifier-timing.json`.
- Wheel built successfully; both indexes, both manifests and NLOD notice match local bytes. See `wheel-check.json`; wheel stays in ignored cache.
- Raw download and old-index backups remain ignored. Only derived indexes, manifests, builders, tests, notices and report material belong in Git. No raw official full dataset is distributed.
