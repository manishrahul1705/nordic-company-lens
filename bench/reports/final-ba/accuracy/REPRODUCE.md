# Reproduce Stage BA accuracy and attribution checks without `bench/runs`

The Stage X sample is drawn from the compressed final-BA population in `extract/envelopes.jsonl.xz`. Its saved SHA-256 checked evidence bytes, extracted sample, adjudication and manifests are committed in this directory. No company HTTP calls are needed.

From the repository root, run:

```
.venv/Scripts/python.exe bench/reports/final-ba/accuracy/reproduce.py
.venv/Scripts/python.exe bench/reports/final-ba/accuracy/review_support.py
.venv/Scripts/python.exe bench/reports/final-ba/accuracy/adjudicate_sample.py
.venv/Scripts/python.exe bench/reports/final-ba/accuracy/attribution_audit.py
.venv/Scripts/python.exe bench/reports/final-ba/accuracy/adjudicate_bulk.py
.venv/Scripts/python.exe bench/reports/final-ba/measure_extract.py
```

`reproduce.py` redraws the **200-claim** Stage X sample (seed `20261119`), checks the fixed family allocation and mechanical evidence predicate, then compares the recorded verdicts and Wilson summary. The sample has 165 exact locator/span/subject-URL checks and 35 source-reviewed items; **200/200 are correct**, Wilson 95% lower bound **98.12%**. Synthesis is independently checked by the strict verifier and is not part of this claim sample.

`review_support.py` recreates the saved source context for the 35 source-reviewed items. `adjudicate_sample.py` verifies those saved registry, company-site, official bulk, GLEIF, NAV, DiBK, TED and other source rows without accessing the network. `attribution_audit.py` preserves the original raw audit checks. It reports four reused official bulk URLs. `adjudicate_bulk.py` checks 791 SHA-256-verified official rows, including four explicitly scoped registered-recipient subunit rows; actual cross-company contamination is zero.

`measure_extract.py` recounts the family table from the committed compressed envelope population. The extract has all **236,654** published claims and all evidence needed for the sample and attribution adjudication. `manifest.json` records the compressed population and source-blob hashes.

The unseen-300 seed-7 precision audit is separately self-contained in `../jury-precision/`: its sample has 100/100 correct, with 80 exact mechanical checks and 20 source-row reviews; Uniktur has no published brand claim. Use:

```
.venv/Scripts/python.exe bench/reports/final-ba/jury-precision/verify_sample.py
```
