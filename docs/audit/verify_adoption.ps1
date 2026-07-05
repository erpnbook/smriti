$cssDir = "D:\Smriti_Retail_OS\apps\smriti_retail_os\smriti_retail_os\public\css"
$densityTokens = @(
    "--smriti-table-row-height",
    "--smriti-spacing-card",
    "--smriti-toolbar-height",
    "--smriti-form-field-height",
    "--smriti-card-header-height",
    "--smriti-spacing-padding-y",
    "--smriti-spacing-padding-x"
)
$mandatoryTokens = @("--smriti-table-row-height", "--smriti-spacing-card", "--smriti-toolbar-height")
$riskFiles = @("smriti-inventory.css", "smriti-purchase.css", "smriti-reports.css", "smriti-sizewise-invoice.css")

foreach ($file in $riskFiles) {
    $found = 0
    $missing = @()
    $mandatoryMissing = @()
    foreach ($token in $densityTokens) {
        $filePath = Join-Path $cssDir $file
        $count = (Get-Content $filePath | Select-String $token).Count
        if ($count -gt 0) {
            $found++
        } else {
            $missing += $token
            if ($mandatoryTokens -contains $token) {
                $mandatoryMissing += $token
            }
        }
    }
    $mandatoryOk = ($mandatoryMissing.Count -eq 0)
    $totalOk = ($found -ge 6)
    $status = if ($mandatoryOk -and $totalOk) { "PASS" } elseif (-not $mandatoryOk) { "FAIL (mandatory missing: $($mandatoryMissing -join ', '))" } else { "FAIL ($found/7 total)" }
    Write-Host "$file : $found/7 [$status]"
    if ($missing.Count -gt 0) {
        Write-Host "  Missing: $($missing -join ', ')"
    }
}

$sidebarPath = Join-Path $cssDir "smriti_sidebar_standalone.css"
$sidebarCheck = (Get-Content $sidebarPath | Select-String "--smriti-dimension-sidebar-width").Count
Write-Host "smriti_sidebar_standalone.css: sidebar-width token = $(if ($sidebarCheck -gt 0) { 'PRESENT' } else { 'MISSING' })"
