param(
    [ValidateSet(20, 100, 1000)]
    [int]$Size = 100,
    [switch]$Search,
    [switch]$SuffixContactProof,
    [switch]$DomainLocationProof
)
$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Push-Location -LiteralPath $repo
try {
    uv sync --frozen
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    $benchArgs = @('--size', $Size)
    if ($Search) { $benchArgs += '--search' }
    if ($SuffixContactProof) { $benchArgs += '--website-suffix-contact-proof' }
    if ($DomainLocationProof) { $benchArgs += '--website-domain-location-proof' }
    uv run --frozen python scripts/bench_run.py @benchArgs
    exit $LASTEXITCODE
} finally {
    Pop-Location
}
