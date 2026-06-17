param()
Write-Host "Installing dependencies and running tests"
Set-StrictMode -Version Latest
python -m pip install --upgrade pip
if (Test-Path "../wrestling-pipeline/etl/requirements.txt") {
    python -m pip install -r "../wrestling-pipeline/etl/requirements.txt"
}
Write-Host "Running pytest..."
python -m pytest -q "../wrestling-pipeline/tests"
