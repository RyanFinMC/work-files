param(
    [string]$VenvPath = ".venv"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
Set-Location $repoRoot

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "Created .env from .env.example"
    } else {
        throw ".env.example not found. Create .env manually."
    }
}

$pythonLauncher = $null
$versionArgs = @()
$venvArgs = @()

if (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonLauncher = "py"
    $versionArgs = @("-3", "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    $venvArgs = @("-3", "-m", "venv", $VenvPath)
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonLauncher = "python"
    $versionArgs = @("-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    $venvArgs = @("-m", "venv", $VenvPath)
} else {
    throw "Python is not installed or not in PATH."
}

$pyVersionOutput = & $pythonLauncher @versionArgs
if (-not $pyVersionOutput) {
    throw "Unable to detect Python version from launcher '$pythonLauncher'."
}
$pyVersion = $pyVersionOutput.Trim()
if ([version]$pyVersion -lt [version]"3.11") {
    throw "Python 3.11+ is required. Found $pyVersion"
}

& $pythonLauncher @venvArgs

$venvActivate = Join-Path $repoRoot "$VenvPath\Scripts\Activate.ps1"
if (-not (Test-Path $venvActivate)) {
    throw "Virtual environment activation script not found at $venvActivate"
}

& $venvActivate
python -m pip install --upgrade pip
pip install -e .

Write-Host "Bootstrap complete. Activate with: $venvActivate"
