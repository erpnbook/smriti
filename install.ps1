# ==============================================================================
# SMRITI Retail OS™ — Master PowerShell Auto-Installer
# Enterprise Retail Operations Platform
# Copyright © 2026 AITDL NETWORK & ERPNbook.com
# ==============================================================================

[CmdletBinding()]
param (
    [string]$Port = "8765",
    [switch]$SkipClone = $false
)

$ErrorActionPreference = "Stop"

function Write-Banner {
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host "                SMRITI Retail OS™ Master Installer                    " -ForegroundColor Green
    Write-Host "         Enterprise Retail Operations & Intelligence Platform          " -ForegroundColor Yellow
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host ""
}

function Write-Step ([string]$msg) {
    Write-Host "[SMRITI Installer] $msg" -ForegroundColor Cyan
}

function Write-Success ([string]$msg) {
    Write-Host "[SUCCESS] $msg" -ForegroundColor Green
}

function Write-Warn ([string]$msg) {
    Write-Host "[WARNING] $msg" -ForegroundColor Yellow
}

function Write-Err ([string]$msg) {
    Write-Host "[ERROR] $msg" -ForegroundColor Red
}

Write-Banner

# ------------------------------------------------------------------------------
# 1. Prerequisite Checks
# ------------------------------------------------------------------------------
Write-Step "Checking prerequisites (Git, Docker)..."

try {
    $gitVer = git --version 2>&1
    Write-Host "  ✔ Git detected: $gitVer" -ForegroundColor Gray
} catch {
    Write-Err "Git is not installed or not found in PATH. Please install Git and retry."
    exit 1
}

try {
    $dockerVer = docker --version 2>&1
    Write-Host "  ✔ Docker detected: $dockerVer" -ForegroundColor Gray
} catch {
    Write-Err "Docker is not installed or not found in PATH. Please install Docker Desktop."
    exit 1
}

Write-Step "Verifying Docker engine state..."
$dockerInfo = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Err "Docker engine is not running! Please start Docker Desktop and run this script again."
    exit 1
}
Write-Host "  ✔ Docker engine is active and responsive." -ForegroundColor Gray

# ------------------------------------------------------------------------------
# 2. Workspace & Directory Preparation
# ------------------------------------------------------------------------------
Write-Step "Preparing workspace directories (apps, backups, company)..."
$rootPath = Get-Location

$dirs = @("apps", "backups", "company")
foreach ($d in $dirs) {
    $targetPath = Join-Path $rootPath $d
    if (-not (Test-Path $targetPath)) {
        New-Item -ItemType Directory -Path $targetPath -Force | Out-Null
        Write-Host "  + Created directory: $d" -ForegroundColor Gray
    } else {
        Write-Host "  ✔ Existing directory: $d" -ForegroundColor Gray
    }
}

# Clone india_compliance dependency if missing
$icPath = Join-Path $rootPath "apps\india_compliance"
if (-not (Test-Path $icPath) -and -not $SkipClone) {
    Write-Step "Cloning required dependency: india_compliance (v16)..."
    git clone --branch version-16 https://github.com/resilient-tech/india-compliance.git $icPath
    if ($LASTEXITCODE -ne 0) {
        Write-Err "Failed to clone india_compliance repository."
        exit 1
    }
    Write-Success "india_compliance cloned successfully."
} else {
    Write-Host "  ✔ india_compliance app repository is ready." -ForegroundColor Gray
}

# ------------------------------------------------------------------------------
# 3. Windows Folder Icon Branding (Optional)
# ------------------------------------------------------------------------------
$icoPath = Join-Path $rootPath "smriti.ico"
if (Test-Path $icoPath) {
    try {
        $desktopIni = Join-Path $rootPath "desktop.ini"
        "[.ShellClassInfo]`r`nIconResource=smriti.ico,0`r`n[ViewState]`r`nFolderType=Generic" | Out-File -FilePath $desktopIni -Encoding ascii -Force
        (Get-Item $desktopIni).Attributes = [System.IO.FileAttributes]::Hidden -bor [System.IO.FileAttributes]::System
        (Get-Item $rootPath).Attributes = [System.IO.FileAttributes]::ReadOnly
        Write-Host "  ✔ Configured Windows folder branding icon." -ForegroundColor Gray
    } catch {
        # Non-critical, ignore if permissions restrict ini write
    }
}

# ------------------------------------------------------------------------------
# 4. Spin Up Docker Compose Stack
# ------------------------------------------------------------------------------
Write-Step "Launching SMRITI Retail OS Docker Stack (pwd.yml)..."
docker compose -f pwd.yml up -d
if ($LASTEXITCODE -ne 0) {
    Write-Err "docker compose up failed. Please review error messages above."
    exit 1
}

# ------------------------------------------------------------------------------
# 5. Monitor Provisioning Sentinel
# ------------------------------------------------------------------------------
Write-Step "Waiting for site provisioning and database setup to complete..."
Write-Host "  (This initial site creation usually takes 2–4 minutes)..." -ForegroundColor Yellow

$timeoutSeconds = 600
$elapsed = 0
$siteDone = $false

while ($elapsed -lt $timeoutSeconds) {
    Start-Sleep -Seconds 5
    $elapsed += 5

    # Check if create-site has exited with code 0
    $csStatus = docker inspect --format='{{.State.Status}} ({{.State.ExitCode}})' smriti9-create-site-1 2>&1
    if ($csStatus -match "exited \(0\)") {
        $siteDone = $true
        Write-Host ""
        Write-Success "Site provisioning and database migration completed successfully!"
        break
    } elseif ($csStatus -match "exited \([1-9]\)") {
        Write-Host ""
        Write-Err "Site creation failed with status: $csStatus"
        Write-Host "Review logs with: docker compose -f pwd.yml logs create-site" -ForegroundColor Yellow
        exit 1
    }

    # Print heart-beat dot
    Write-Host "." -NoNewline -ForegroundColor Green
}

if (-not $siteDone) {
    Write-Warn "Site provisioning timed out after $timeoutSeconds seconds. Services may still be completing in background."
}

# ------------------------------------------------------------------------------
# 6. Monitor Backend & Web Health Check
# ------------------------------------------------------------------------------
Write-Step "Verifying HTTP Web Service availability at http://localhost:$Port..."
$webOk = $false
$elapsed = 0

while ($elapsed -lt 120) {
    try {
        $resp = Invoke-WebRequest -Uri "http://localhost:$Port/" -UseBasicParsing -TimeoutSec 3 -ErrorAction SilentlyContinue
        if ($resp.StatusCode -eq 200) {
            $webOk = $true
            break
        }
    } catch {
        # Backend warming up
    }
    Start-Sleep -Seconds 3
    $elapsed += 3
    Write-Host "." -NoNewline -ForegroundColor Cyan
}

Write-Host ""

# ------------------------------------------------------------------------------
# 7. Final Success Banner
# ------------------------------------------------------------------------------
if ($webOk) {
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host " 🎉 SMRITI Retail OS™ is SUCCESSFULLY INSTALLED and RUNNING!          " -ForegroundColor Green
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "  🌐 Open Web Terminal : http://localhost:$Port" -ForegroundColor Yellow
    Write-Host "  🔑 POS Profile Setup : http://localhost:$Port/smriti-pos-profiles" -ForegroundColor Cyan
    Write-Host "  🔍 Field Explorer    : http://localhost:$Port/smriti-field-explorer" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Useful Commands:" -ForegroundColor Gray
    Write-Host "  • Stop Stack   : docker compose -f pwd.yml down" -ForegroundColor Gray
    Write-Host "  • View Logs    : docker compose -f pwd.yml logs -f" -ForegroundColor Gray
    Write-Host "  • Check Status : docker compose -f pwd.yml ps" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Warn "Services started, but port $Port is still initializing."
    Write-Host "Please check http://localhost:$Port in a minute or run: docker compose -f pwd.yml ps" -ForegroundColor Yellow
}
