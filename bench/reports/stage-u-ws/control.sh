#!/bin/sh
# Same-session control: revision-4 first, then the branch; identical command, fresh state each.
IN=/c/Users/Manish/Downloads/nordic-r4/bench/inputs/1000-r3/batch.jsonl
for pair in "rev4:/c/Users/Manish/Downloads/nordic-r4-rev4" "branch:/c/Users/Manish/Downloads/nordic-r4"; do
  name=${pair%%:*}; dir=${pair#*:}; R=/c/Users/Manish/Downloads/nordic-r4/bench/runs/control-$name
  rm -rf "$R"; mkdir -p "$R"
  start=$(date +%s); echo "start $(date -u +%FT%TZ)" > "$R/process.txt"
  (cd "$dir" && env -u CLAUDE_CODE_MESSAGING_TOKEN uv run --frozen signalpost run --organisations "$IN" --output "$R/envelopes.jsonl" --profiles-output "$R/profiles.jsonl" --report "$R/report.json" --state-dir "$R/state" --site-dir "$R/site") >> "$R/process.txt" 2>&1
  echo "exit=$? wall=$(( $(date +%s)-start )) end $(date -u +%FT%TZ) code=$(git -C "$dir" rev-parse HEAD) dirty=$(git -C "$dir" status --porcelain src | wc -l)" >> "$R/process.txt"
done
