param()
Write-Host "Installing dependencies and running tests"
Set-StrictMode -Version Latest
$root = Join-Path -Path $PSScriptRoot -ChildPath '..'
$composeFile = Join-Path -Path $root -ChildPath 'docker\docker-compose.test.yml'
$etlRequirements = Join-Path -Path $root -ChildPath 'etl\requirements.txt'
$testsDir = Join-Path -Path $root -ChildPath 'tests'

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
    return $null
}

$dockerCompose = Get-DockerComposeCommand
python -m pip install --upgrade pip
if (Test-Path $etlRequirements) {
    python -m pip install -r $etlRequirements
}

if ($dockerCompose -and (Test-Path $composeFile)) {
    Write-Host "Detected Docker Compose and compose file; running tests inside isolated compose 'etl-runner' container."
    $project = 'wrestling_pipeline_test'
    $networkName = "${project}_net"
    try {
        docker network create $networkName | Out-Null
    } catch {
        Write-Host "Network $networkName already exists or creation failed; continuing."
    }

    $composeArgs = $dockerCompose.Args + @('-p', $project, '-f', $composeFile)

    & $dockerCompose.Command @($composeArgs + @('down', '-v', '--remove-orphans')) 2>$null
    & $dockerCompose.Command @($composeArgs + @('build', 'etl-runner'))
    & $dockerCompose.Command @($composeArgs + @('up', '-d', 'db'))

    Write-Host "Running pytest inside container..."
    $exitCode = 0
    try {
        & $dockerCompose.Command @($composeArgs + @('run', '--rm', '-e', 'PYTHONPATH=/app', 'etl-runner', 'pytest', '-v', '/app/tests'))
        $exitCode = $LASTEXITCODE
    } catch {
        $exitCode = $LASTEXITCODE
    }

    if ($exitCode -ne 0) {
        Write-Host "Tests failed with exit code $exitCode."
    }
    exit $exitCode
}

Write-Host "Docker Compose unavailable or compose file missing; running tests locally as fallback."
python -m pytest -q $testsDir
