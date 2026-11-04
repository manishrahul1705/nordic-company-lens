param(
    [ValidateSet(20, 100, 1000)]
    [int]$Size = 100
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $repo
try {
    uv sync --frozen
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    uv run --frozen python scripts/bench_run.py --size $Size
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
