# Build script for FadCrypt Windows .exe package with Inno Setup
# Usage: .\build-windows.ps1

param(
    [switch]$SkipInnoSetup = $false,
    [string]$InnoSetupPath = "D:\Software's data\Inno Setup 6\ISCC.exe"
)

# Stop on any error
$ErrorActionPreference = "Stop"

Write-Host "=== Building FadCrypt for Windows ===" -ForegroundColor Cyan

# Extract version from version.py
try {
    $versionInfo = python -c "from core.version import __version__, PACKAGE_NAME, MAINTAINER_FULL, PACKAGE_DESCRIPTION; print(f'{__version__}|{PACKAGE_NAME}|{MAINTAINER_FULL}|{PACKAGE_DESCRIPTION}')"
    $versionParts = $versionInfo.Split('|')
    $VERSION = $versionParts[0]
    $PACKAGE_NAME = $versionParts[1]
    $MAINTAINER = $versionParts[2]
    $DESCRIPTION = $versionParts[3]
}
catch {
    Write-Host "Error: Could not extract version info" -ForegroundColor Red
    exit 1
}

Write-Host "Building version: $VERSION" -ForegroundColor Green

# Check dependencies
Write-Host "Checking dependencies..." -ForegroundColor Yellow
$pyinstaller = $null
try {
    $pyinstaller = python -m pip show pyinstaller | Select-String "Name:"
}
catch {
    Write-Host "Error: PyInstaller not found. Install with: pip install pyinstaller" -ForegroundColor Red
    exit 1
}

# Check if Inno Setup is available (if not skipping)
if (-not $SkipInnoSetup) {
    if (-not (Test-Path $InnoSetupPath)) {
        Write-Host "Error: Inno Setup not found at $InnoSetupPath" -ForegroundColor Red
        Write-Host "Either:" -ForegroundColor Yellow
        Write-Host "  1. Install Inno Setup 6 to: $InnoSetupPath" -ForegroundColor Yellow
        Write-Host "  2. Run: .\build-windows.ps1 -SkipInnoSetup" -ForegroundColor Yellow
        exit 1
    }
}

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
if (Test-Path "build") { Remove-Item -Recurse -Force "build" -ErrorAction SilentlyContinue }
if (Test-Path "dist") { Remove-Item -Recurse -Force "dist" -ErrorAction SilentlyContinue }

# Build GUI with PyInstaller
Write-Host "Building GUI executable with PyInstaller..." -ForegroundColor Yellow
Write-Host "Command: python -m PyInstaller FadCrypt.spec --clean --noconfirm" -ForegroundColor DarkGray
python -m PyInstaller FadCrypt.spec --clean --noconfirm

# Check if GUI build succeeded
if (-not (Test-Path "dist\FadCrypt\FadCrypt.exe")) {
    Write-Host "Error: Build failed - FadCrypt.exe not found in dist\FadCrypt\" -ForegroundColor Red
    exit 1
}

Write-Host "✓ GUI build successful!" -ForegroundColor Green
Write-Host "  Output: dist\FadCrypt\FadCrypt.exe" -ForegroundColor Green

# Build CLI with PyInstaller
Write-Host "`nBuilding CLI executable with PyInstaller..." -ForegroundColor Yellow
Write-Host "Command: python -m PyInstaller FadCryptCLI.spec --clean --noconfirm" -ForegroundColor DarkGray
python -m PyInstaller FadCryptCLI.spec --clean --noconfirm

# Check if CLI build succeeded
if (-not (Test-Path "dist\FadCryptCLI\fadcrypt.exe")) {
    Write-Host "Error: Build failed - fadcrypt.exe not found in dist\FadCryptCLI\" -ForegroundColor Red
    exit 1
}

Write-Host "✓ CLI build successful!" -ForegroundColor Green
Write-Host "  Output: dist\FadCryptCLI\fadcrypt.exe" -ForegroundColor Green

# If Inno Setup is skipped, exit early
if ($SkipInnoSetup) {
    Write-Host "`n✓ Build complete! Inno Setup skipped." -ForegroundColor Green
    Write-Host "`nTo build the installer, run:" -ForegroundColor Cyan
    Write-Host "  $InnoSetupPath innosetup\FadCrypt-inno-setup-script.iss" -ForegroundColor Yellow
    exit 0
}

# Build with Inno Setup
Write-Host "`nBuilding installer with Inno Setup..." -ForegroundColor Yellow
if (-not (Test-Path "innosetup\FadCrypt-inno-setup-script.iss")) {
    Write-Host "Error: Inno Setup script not found at innosetup\FadCrypt-inno-setup-script.iss" -ForegroundColor Red
    exit 1
}

Write-Host "Command: $InnoSetupPath innosetup\FadCrypt-inno-setup-script.iss" -ForegroundColor DarkGray
& $InnoSetupPath "innosetup\FadCrypt-inno-setup-script.iss"

# Check if installer was created - Inno Setup outputs to a temp folder
# Find the most recent .exe in common Inno Setup output locations
$installerPath = $null

# Check multiple possible output locations
$possiblePaths = @(
    "innosetup\Output\*.exe",
    "$env:APPDATA\Inno Setup\*.exe",
    "*.exe"  # In current directory as fallback
)

foreach ($pattern in $possiblePaths) {
    $found = @(Get-ChildItem $pattern -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1)
    if ($found.Count -gt 0) {
        $installerPath = $found[0].FullName
        break
    }
}

if ($installerPath) {
    Write-Host "`n✓ Inno Setup build successful!" -ForegroundColor Green
    
    Write-Host "`n" -ForegroundColor Cyan
    Write-Host "=== Build Complete ===" -ForegroundColor Cyan
    Write-Host "Executable: dist\FadCrypt\FadCrypt.exe" -ForegroundColor Green
    Write-Host "Installer:  $installerPath" -ForegroundColor Green
    
    Write-Host "`nTo install FadCrypt, run:" -ForegroundColor Cyan
    Write-Host "`"$installerPath`"" -ForegroundColor Yellow
    
    Write-Host "`n✓ All done!" -ForegroundColor Green
}
else {
    Write-Host "✓ Build completed! Inno Setup may have created installer in a custom location." -ForegroundColor Green
    Write-Host "`nExecutable: .\dist\FadCryptSetup.exe" -ForegroundColor Green
}
