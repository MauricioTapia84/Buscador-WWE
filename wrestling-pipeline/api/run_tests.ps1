Param()

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $scriptDir

if (-not (Test-Path .venv)) {
    python -m venv .venv
}

# Activate venv
$activate = Join-Path $PWD '.venv\Scripts\Activate.ps1'
if (Test-Path $activate) {
    & $activate
}

python -m pip install --upgrade pip
python -m pip install -r requirements.txt pytest requests

python -m pytest -q
