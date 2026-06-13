# TransAfrik Remit - PostgreSQL backup script
param(
    [string]$DatabaseUrl = $env:DATABASE_URL
)
if (-not $DatabaseUrl) {
    $DatabaseUrl = "postgresql://transafrik:transafrik_secret@localhost:5432/transafrik"
}
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$outDir = Join-Path $PSScriptRoot "..\backups"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$outFile = Join-Path $outDir "transafrik_$timestamp.sql"
Write-Host "Backing up to $outFile"
# Requires pg_dump in PATH
if ($DatabaseUrl -match "postgresql://([^:]+):([^@]+)@([^:/]+):?(\d+)?/(.+)") {
    $user = $Matches[1]; $pass = $Matches[2]; $host = $Matches[3]; $port = if ($Matches[4]) { $Matches[4] } else { "5432" }; $db = $Matches[5]
    $env:PGPASSWORD = $pass
    pg_dump -h $host -p $port -U $user -d $db -f $outFile
    Write-Host "Backup complete"
} else {
    Write-Error "Invalid DATABASE_URL format"
    exit 1
}
