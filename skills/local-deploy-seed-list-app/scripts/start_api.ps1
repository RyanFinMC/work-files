param(
    [string]$VenvPath = ".venv"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
Set-Location $repoRoot

if (-not (Test-Path ".env")) {
    throw ".env not found. Run bootstrap_local.ps1 first."
}

$venvActivate = Join-Path $repoRoot "$VenvPath\Scripts\Activate.ps1"
if (-not (Test-Path $venvActivate)) {
    throw "Virtual environment not found at $venvActivate. Run bootstrap_local.ps1 first."
}

$host = "0.0.0.0"
$port = "8000"
Get-Content ".env" | ForEach-Object {
    if ($_ -match '^\s*APP_HOST\s*=\s*(.+)\s*$') { $host = $Matches[1] }
    if ($_ -match '^\s*APP_PORT\s*=\s*(.+)\s*$') { $port = $Matches[1] }
}

& $venvActivate
alembic upgrade head
uvicorn app.main:app --host $host --port $port --reload
