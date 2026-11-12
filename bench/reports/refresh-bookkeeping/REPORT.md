# Final refresh bookkeeping fix

Full suite: **1,301 passed in 369.61 s**. Four new cases cover the 897051982 provisional-accept/final-withhold pattern, a real final state difference, a real final claim difference, and runner ordering after the publication guard. No existing tests were weakened.

`reconcile_final_observations` runs after shared-social filtering and the final entity-scope guard. It removes an observation only when the section's final published state and claims match the previous snapshot. Claim comparison includes IDs, fields, values, availability and reporting period; retrieval timestamps are not company facts. It does not restore claims, rerun proof, alter company changes, or modify guard logic.

## Saved final-code-v2 pair: strict PASS after offline bookkeeping replay

The unmodified strict verifier passes: **103 envelopes, identical claim IDs, 0 company changes, 0 observation changes**. It verifies 416 saved blobs and all 103 cited briefings. The second run's evidence is also verified independently.

Only org **897051982** loses the provisional website observation. Its final ambiguous website state and all claims remain unchanged. Original saved envelopes remain byte-for-byte untouched (SHA-256 recorded); the replay copy changes only `run.refresh.observation_changes`. The original historical pair still contains its historical observation and is not relabelled as having passed without replay. No live run was needed or performed.

Reproduce from the worktree: `uv run --frozen python scripts/replay_final_observations.py`. The replay reads the retained ignored final-precision clone/state and writes a separate ignored replay file. Results and original hashes: `offline-verifier.json`. Full suite output: `pytest.txt`.

Files changed: `src/signalpost/refresh/diff.py` (final-state reconciliation), `src/signalpost/runner.py` (invoke after guards), `tests/test_refresh_final_publication.py` (regressions), `scripts/replay_final_observations.py` (offline replay/strict verification), and these audit reports. No proof or entity-scope source file changed. No push.
