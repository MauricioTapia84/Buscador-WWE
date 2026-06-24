Param()

# Build and run services using docker compose, wait for health endpoint and open dashboard
$root = Join-Path -Path $PSScriptRoot -ChildPath '..'
Set-Location $root

function Get-DockerComposeCommand {
    if (Get-Command 'docker' -ErrorAction SilentlyContinue) {
        try {
            docker compose version >/dev/null 2>&1
            return @{ Command = 'docker'; Args = @('compose') }
        } catch {
        }
    }
    if (Get-Command 'docker-compose' -ErrorAction SilentlyContinue) {
        return @{ Command = 'docker-compose'; Args = @() }
    }
    throw 'Error: neither docker compose nor docker-compose is installed.'
}

$composeCmd = Get-DockerComposeCommand
Write-Host "Using compose command: $($composeCmd.Command) $($composeCmd.Args -join ' ')"

Write-Host 'Building and starting services...'
$composeFile = Join-Path $root 'docker\docker-compose.yml'
$project = 'wrestling-pipeline'
& $composeCmd.Command @($composeCmd.Args + @('-p', $project, '-f', $composeFile, 'build'))
& $composeCmd.Command @($composeCmd.Args + @('-p', $project, '-f', $composeFile, 'up', '-d'))

$dataDir = Join-Path $root 'data'
if (-Not (Test-Path $dataDir)) {
    New-Item -ItemType Directory -Path $dataDir | Out-Null
}
Write-Host "Ensuring data directory exists: $dataDir"

Write-Host 'Running ETL extractors inside etl-runner container...'
$etlCmd = 'python -u /app/run_etl.py --verbose'
try {
    $current = & $composeCmd.Command @($composeCmd.Args + @('-p', $project, '-f', $composeFile, 'ps'))
    if ($current -match 'etl-runner' -and $current -match 'Up') {
        & $composeCmd.Command @($composeCmd.Args + @('-p', $project, '-f', $composeFile, 'exec', '-T', 'etl-runner', 'sh', '-lc', $etlCmd))
    } else {
        throw 'etl-runner not running'
    }
} catch {
    Write-Host 'etl-runner not running; starting the service and retrying'
    & $composeCmd.Command @($composeCmd.Args + @('-p', $project, '-f', $composeFile, 'up', '-d', 'etl-runner'))
    Start-Sleep -Seconds 2
    & $composeCmd.Command @($composeCmd.Args + @('-p', $project, '-f', $composeFile, 'exec', '-T', 'etl-runner', 'sh', '-lc', $etlCmd))
}

Write-Host 'Waiting for API to be healthy...'
$url = 'http://localhost:8000/api/health'
$timeout = 60
$end = (Get-Date).AddSeconds($timeout)
while ((Get-Date) -lt $end) {
    try {
        $r = Invoke-WebRequest -Uri $url -UseBasicParsing -TimeoutSec 5
        if ($r.StatusCode -eq 200) { break }
    } catch { }
    Start-Sleep -Seconds 2
}

Write-Host 'Opening dashboard in default browser...'
Start-Process 'http://localhost:8501'
Write-Host 'Services started. Use docker-compose logs -f to follow logs.'
