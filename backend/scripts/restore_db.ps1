# TransAfrik Remit - PostgreSQL restore script
param(
    [Parameter(Mandatory=$true)][string]$BackupFile,
    [string]$DatabaseUrl = $env:DATABASE_URL
)
if (-not $DatabaseUrl) {
    $DatabaseUrl = "postgresql://transafrik:transafrik_secret@localhost:5432/transafrik"
}
if (-not (Test-Path $BackupFile)) { Write-Error "Backup file not found"; exit 1 }
if ($DatabaseUrl -match "postgresql://([^:]+):([^@]+)@([^:/]+):?(\d+)?/(.+)") {
    $user = $Matches[1]; $pass = $Matches[2]; $host = $Matches[3]; $port = if ($Matches[4]) { $Matches[4] } else { "5432" }; $db = $Matches[5]
    $env:PGPASSWORD = $pass
    psql -h $host -p $port -U $user -d $db -f $BackupFile
    Write-Host "Restore complete"
} else { Write-Error "Invalid DATABASE_URL"; exit 1 }
