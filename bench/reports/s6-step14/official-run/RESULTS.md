# Step14 fresh-clone README command pair

Fresh local clone29a30a5a2909ef5ada88cf6cd14d054f13cd925c; uv sync --frozen passed; application credential/search environment removed. Reused the release cohort of100checksum-valid nonbench orgnrs+3invalid lines, SHA256aa4a2176651c8d05c38f97919733a2c4625117eb1f4925036bef8e13dfe49289. This is not claimed as a new random selection.

```sh
uv run --frozen signalpost run --organisations orgnrs.txt --output out/envelopes.jsonl --profiles-output out/profiles.jsonl --report out/report.json --state-dir out/state --site-dir out/site
```

Literal command twice without modification or --previous, same state directory. First149.531seconds/655HTTP, second138.906seconds/653HTTP. Each103envelopes and103profiles,0company changes,0observation changes,0deadlines, no warnings. Invalid lines each retained a failed result. Both comfortably within the original request/time caps; source/evidence and automatic latest snapshot retained in bench/cache/s6-step14-official.

Strict pairwise verifier exit0:103schema-valid lines,6095publishedclaims,315sourceblobs,698citedsentences,0unverifiedvalues, identicalclaimIDs,0changes,0observationchanges. No weakened checks or repeated pair selection. [Exact execution](execution.json), [strict verifier](verification.txt).
