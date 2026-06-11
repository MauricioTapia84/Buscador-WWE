<#
PowerShell helper to build and start the docker-compose stack on Windows.
Usage (PowerShell):
  Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
  .\docker_compose_up.ps1
#>

Param()

$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$rootDir = Resolve-Path (Join-Path $scriptDir '..')
$composeFile = Join-Path $rootDir 'docker\docker-compose.yml'
$envFile = Join-Path $rootDir '.env'

Write-Host "Root: $rootDir"

if (-not (Test-Path $envFile)) {
    Write-Host ".env not found in $rootDir — creating with default values (change them as needed)."
    @"
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=wrestling
"@ | Out-File -FilePath $envFile -Encoding utf8
    Write-Host "Created $envFile"
}

$dashReq = Join-Path $rootDir 'dashboards\requirements.txt'
if (-not (Test-Path $dashReq)) {
    Write-Warning "Warning: dashboard requirements not found at $dashReq. The dashboard build may fail."
}

Write-Host "Running: docker compose -f $composeFile up --build -d"
& docker compose -f $composeFile up --build -d

Write-Host "Services status:"
& docker compose -f $composeFile ps

Write-Host "Showing last 200 lines of logs for api and etl-runner"
try {
    & docker compose -f $composeFile logs --tail 200 api etl-runner
} catch {
    Write-Warning "Couldn't fetch logs: $_"
}

Write-Host "Done. Use 'docker compose -f $composeFile logs -f <service>' to follow logs." 
