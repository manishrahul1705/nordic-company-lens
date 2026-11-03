#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."
uv sync --frozen
uv run --frozen python scripts/bench_run.py "$@"
