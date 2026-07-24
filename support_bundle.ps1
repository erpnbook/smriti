# ==============================================================================
# SMRITI Retail OS™ — Diagnostic Bundle Exporter
# Enterprise Retail Operations Platform
# Copyright © 2026 AITDL NETWORK & ERPNbook.com
# ==============================================================================

[CmdletBinding()]
param (
    [string]$OutputDir = "backups"
)

$ErrorActionPreference = "Continue"

$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$bundleFolder = Join-Path $OutputDir "support_bundle_$timestamp"

Write-Host ""
Write-Host "[SMRITI Diagnostics] Collecting support bundle..." -ForegroundColor Cyan

if (-not (Test-Path $bundleFolder)) {
    New-Item -ItemType Directory -Path $bundleFolder -Force | Out-Null
}

# 1. Collect Container Logs
Write-Host "  • Exporting container logs..." -ForegroundColor Gray
docker compose -f pwd.yml logs > (Join-Path $bundleFolder "docker_compose_all.log") 2>&1
docker logs smriti9-backend-1 > (Join-Path $bundleFolder "backend.log") 2>&1
docker logs smriti9-create-site-1 > (Join-Path $bundleFolder "create_site.log") 2>&1
docker logs smriti9-frontend-1 > (Join-Path $bundleFolder "frontend.log") 2>&1

# 2. Collect Container States
Write-Host "  • Collecting container statuses..." -ForegroundColor Gray
docker compose -f pwd.yml ps -a > (Join-Path $bundleFolder "container_ps.txt") 2>&1

# 3. Collect SDC Health Report if Python is available
Write-Host "  • Running SDC Architecture Discovery check..." -ForegroundColor Gray
try {
    python sdc/discovery.py > (Join-Path $bundleFolder "sdc_discovery.txt") 2>&1
} catch {
    # Non-critical
}

# 4. Zip the bundle
$zipFile = Join-Path $OutputDir "smriti_support_bundle_$timestamp.zip"
Write-Host "  • Creating zip archive..." -ForegroundColor Gray
Compress-Archive -Path "$bundleFolder\*" -DestinationPath $zipFile -Force

# Clean temporary folder
Remove-Item -Path $bundleFolder -Recurse -Force

Write-Host ""
Write-Host "[SUCCESS] Support bundle exported to: $zipFile" -ForegroundColor Green
