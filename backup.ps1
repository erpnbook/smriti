# ==============================================================================
# SMRITI Retail OS™ — One-Click Backup Utility
# Enterprise Retail Operations Platform
# Copyright © 2026 AITDL NETWORK & ERPNbook.com
# ==============================================================================

[CmdletBinding()]
param (
    [string]$Site = "smriti_retail",
    [string]$BackupDir = "backups",
    [switch]$WithFiles = $true
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "[SMRITI Backup] Initiating database & site backup for '$Site'..." -ForegroundColor Cyan

if (-not (Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null
}

$backendContainer = "smriti9-backend-1"

# Check if backend container is running
$status = docker inspect --format='{{.State.Running}}' $backendContainer 2>&1
if ($status -ne "true") {
    Write-Host "[ERROR] Container '$backendContainer' is not running. Please start the stack via docker compose -f pwd.yml up -d first." -ForegroundColor Red
    exit 1
}

Write-Host "[SMRITI Backup] Running bench backup inside $backendContainer..." -ForegroundColor Cyan
if ($WithFiles) {
    docker exec $backendContainer bench --site $Site backup --with-files
} else {
    docker exec $backendContainer bench --site $Site backup
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Site backup generated successfully in container sites/$Site/private/backups/" -ForegroundColor Green
    Write-Host "[SMRITI Backup] Backups are mounted to your local './backups' folder." -ForegroundColor Yellow
} else {
    Write-Host "[ERROR] Backup process failed." -ForegroundColor Red
    exit 1
}
