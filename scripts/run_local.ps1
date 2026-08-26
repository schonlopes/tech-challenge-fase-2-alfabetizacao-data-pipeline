$ErrorActionPreference = "Stop"

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $Python)) {
    python -m venv (Join-Path $ProjectRoot ".venv")
}

& $Python -m pip install -e $ProjectRoot
& $Python (Join-Path $PSScriptRoot "generate_sample_data.py")
& $Python -m alfabetizacao_pipeline.cli --project-root $ProjectRoot run-all --events 24

