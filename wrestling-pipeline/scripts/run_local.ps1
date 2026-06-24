Param()

# Build and run services using docker-compose, wait for health endpoint and open dashboard
$root = Join-Path -Path $PSScriptRoot -ChildPath '..'
Set-Location $root

Write-Host 'Building and starting services...'
$composeFile = Join-Path $root 'docker\docker-compose.yml'
$project = 'wrestling-pipeline'
docker-compose -p $project -f $composeFile build
docker-compose -p $project -f $composeFile up -d

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
