param(
    [string]$ContainerName = "seed-list-postgres",
    [int]$Port = 5432,
    [string]$User = "postgres",
    [string]$Password = "postgres",
    [string]$Database = "seed_list"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker is not installed or not in PATH."
}

$existing = docker ps -a --filter "name=^/$ContainerName$" --format "{{.Names}}" | Select-Object -First 1
if ([string]::IsNullOrWhiteSpace($existing)) {
    docker run -d --name $ContainerName -e POSTGRES_USER=$User -e POSTGRES_PASSWORD=$Password -e POSTGRES_DB=$Database -p "$Port`:5432" postgres:16 | Out-Null
} else {
    $running = docker ps --filter "name=^/$ContainerName$" --format "{{.Names}}" | Select-Object -First 1
    if ([string]::IsNullOrWhiteSpace($running)) {
        docker start $ContainerName | Out-Null
    }
}

Write-Host "PostgreSQL container ready: $ContainerName on localhost:$Port"
Write-Host "DATABASE_URL should be: postgresql+psycopg://$User`:$Password@localhost`:$Port/$Database"
