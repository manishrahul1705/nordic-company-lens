$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repo
$raw = Join-Path $repo 'bench\reports\cc-proto\raw'
$log = Join-Path $raw 'overnight.log'
$python = Join-Path $repo '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Run uv sync --frozen in this checkout first.' }
New-Item -ItemType Directory -Force -Path (Join-Path $repo 'bench\reports\cc-proto\raw') | Out-Null
$deadline = [DateTimeOffset]::Parse('2026-11-13T10:00:00+05:30')
while ([DateTimeOffset]::UtcNow -lt $deadline) {
    $workerArgs = @('-NoProfile','-ExecutionPolicy','Bypass','-File',(Join-Path $PSScriptRoot 'run_cc_overnight_worker.ps1'))
    $worker = Start-Process -FilePath 'powershell.exe' -ArgumentList $workerArgs -WorkingDirectory $repo -WindowStyle Hidden -PassThru
    @{wrapper_pid=$PID; worker_pid=$worker.Id; hard_stop_ist=$deadline.ToString('o'); log=$log} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $raw 'overnight-launch.json') -Encoding utf8
    $remainingMs = [int][Math]::Max(1,($deadline-[DateTimeOffset]::UtcNow).TotalMilliseconds)
    if (-not $worker.WaitForExit($remainingMs)) {
        & taskkill.exe /PID $worker.Id /T /F *>> $log
        break
    }
    if ([DateTimeOffset]::UtcNow -ge $deadline) { break }
    $summaryPath = Join-Path $repo 'bench\reports\cc-proto\overnight-summary.json'
    $complete = $false
    if (Test-Path -LiteralPath $summaryPath) {
        $snapshot = Get-Content -LiteralPath $summaryPath -Raw | ConvertFrom-Json
        $unfinished = @($snapshot.crawls_covered | Where-Object {$_.status -ne 'complete'})
        $complete = @($snapshot.crawls_covered).Count -gt 0 -and $unfinished.Count -eq 0
    }
    if ($complete) { break }
    ('{0:o} Worker exited; retrying resume in15 minutes, bounded by hard stop.' -f [DateTimeOffset]::UtcNow) | Add-Content -LiteralPath $log
    $waitSeconds = [int][Math]::Min(900,[Math]::Max(0,($deadline-[DateTimeOffset]::UtcNow).TotalSeconds))
    Start-Sleep -Seconds $waitSeconds
}
# Final offline snapshot after all worker/selector processes have stopped; no network requests.
& $python -c "import sys;sys.path.insert(0,'scripts');from cc_overnight import summary;summary('stopped_or_finished')" *>> $log
