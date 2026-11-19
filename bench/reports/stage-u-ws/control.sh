#!/bin/sh
# Same-session control: revision-4 first, then the branch; identical command, fresh state each.
# BRANCH_DIR: checkout under test (default: this repository). REV4_DIR: a revision-4 checkout.
BRANCH_DIR=${BRANCH_DIR:-$(git rev-parse --show-toplevel)}
REV4_DIR=${REV4_DIR:?set REV4_DIR to a revision-4 checkout}
IN=$BRANCH_DIR/bench/inputs/1000-r3/batch.jsonl
for pair in "rev4:$REV4_DIR" "branch:$BRANCH_DIR"; do
  name=${pair%%:*}; dir=${pair#*:}; R=$BRANCH_DIR/bench/runs/control-$name
  rm -rf "$R"; mkdir -p "$R"
  start=$(date +%s); echo "start $(date -u +%FT%TZ)" > "$R/process.txt"
  (cd "$dir" && env -u CLAUDE_CODE_MESSAGING_TOKEN uv run --frozen signalpost run --organisations "$IN" --output "$R/envelopes.jsonl" --profiles-output "$R/profiles.jsonl" --report "$R/report.json" --state-dir "$R/state" --site-dir "$R/site") >> "$R/process.txt" 2>&1
  echo "exit=$? wall=$(( $(date +%s)-start )) end $(date -u +%FT%TZ) code=$(git -C "$dir" rev-parse HEAD) dirty=$(git -C "$dir" status --porcelain src | wc -l)" >> "$R/process.txt"
done
