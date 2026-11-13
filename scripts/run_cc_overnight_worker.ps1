$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repo
$python = Join-Path $repo '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Run uv sync --frozen in this checkout first.' }
New-Item -ItemType Directory -Force -Path (Join-Path $repo 'bench\reports\cc-proto\raw') | Out-Null
$log = Join-Path $repo 'bench\reports\cc-proto\raw\overnight.log'
& $python -u (Join-Path $PSScriptRoot 'cc_overnight.py') *>> $log
exit $LASTEXITCODE
