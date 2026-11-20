# Reproduce without bench/runs

Use the project environment at the measured source commit cede54701d5e50067764f472009b6c830254065a plus this measurement commit. No company HTTP or saved run directories are needed.

```
python bench/reports/final-20261120/accuracy/reproduce.py
python bench/reports/final-20261120/accuracy/attribution_audit.py
python bench/reports/final-20261120/accuracy/adjudicate_bulk.py
python bench/reports/final-20261120/accuracy/adjudicate_sample.py
python bench/reports/final-20261120/measure_extract.py
```

The first command redraws the 200-claim fixed-seed sample and checks exact verdict/summary reproduction. The raw attribution audit retains four expected bulk URL-reuse flags; the next command independently checks the exact subject in each of 791 selected official rows, with four explicitly labelled recipient-subunit cases additionally requiring the company's own registry relationship. The raw audit host list is unchanged. Zero actual cross-company contamination is an adjudicated result, not a claim that the raw URL-reuse counter is zero.

`reproduce_extract_only.py <fresh-destination>` copies this directory to an artifact-only location and runs every check with all bench/runs file opens forbidden. It also regenerates hand-review-support.json from the retained blobs and checks decoded JSON identity independently of checkout line endings. The recorded extract-only run passed.

The extract contains all 178,669 published claims with cited evidence metadata across all 1,000 companies. blobs.jsonl.xz contains sampled evidence bytes plus official bulk-row and registry relationship bytes needed for independent attribution adjudication. manifest.json hashes both compressed files; common.read_blobs recomputes each content SHA-256. Original raw bulk downloads, site output and full bench/runs are not committed.

Stage X seed 20261119, size 200, stratified allocation, fixed-seed draw, original mechanical predicate and Wilson formula are retained. Stage AP requested 200 claims: synthesis sentences are excluded from this sampling population and are independently checked by the strict verifier. This one scope change is recorded in script-provenance.json; extraction, reproduction and raw attribution audit are otherwise copied unchanged. The Wilson lower bound describes this sample and is not a recall or competition-score estimate.

extract.txt records the initial sample-only extraction. The subsequent bulk-attribution capture added source/relationship blobs and updated the manifest; the committed extract/manifest.json contains the authoritative final file hashes.
