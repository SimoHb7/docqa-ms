# InterfaceClinique - Complete Fix Script
# This script will clear all caches and restart the dev server properly

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "InterfaceClinique - Complete Fix" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Stop all Node processes
Write-Host "[1/5] Stopping Node processes..." -ForegroundColor Yellow
try {
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "  ✓ Node processes stopped`n" -ForegroundColor Green
} catch {
    Write-Host "  ! No Node processes to stop`n" -ForegroundColor Gray
}

# Step 2: Navigate to project directory
Write-Host "[2/5] Navigating to InterfaceClinique..." -ForegroundColor Yellow
Set-Location "c:\docqa-ms\InterfaceClinique"
Write-Host "  ✓ Changed to: $(Get-Location)`n" -ForegroundColor Green

# Step 3: Clear Vite cache
Write-Host "[3/5] Clearing Vite cache..." -ForegroundColor Yellow
$cachesCleared = 0

if (Test-Path "node_modules/.vite") {
    Remove-Item -Recurse -Force "node_modules/.vite" -ErrorAction SilentlyContinue
    $cachesCleared++
    Write-Host "  ✓ Cleared node_modules/.vite" -ForegroundColor Green
}

if (Test-Path ".vite") {
    Remove-Item -Recurse -Force ".vite" -ErrorAction SilentlyContinue
    $cachesCleared++
    Write-Host "  ✓ Cleared .vite" -ForegroundColor Green
}

if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist" -ErrorAction SilentlyContinue
    $cachesCleared++
    Write-Host "  ✓ Cleared dist" -ForegroundColor Green
}

if ($cachesCleared -eq 0) {
    Write-Host "  ! No caches to clear" -ForegroundColor Gray
}

Write-Host ""

# Step 4: Check backend status
Write-Host "[4/5] Checking backend services..." -ForegroundColor Yellow
try {
    $backendStatus = docker ps --filter "name=docqa-ms" --format "{{.Names}}" 2>$null
    if ($backendStatus) {
        $serviceCount = ($backendStatus | Measure-Object -Line).Lines
        Write-Host "  ✓ Backend running ($serviceCount services)`n" -ForegroundColor Green
    } else {
        Write-Host "  ! Backend NOT running - start with: docker-compose up -d`n" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  ! Could not check backend status`n" -ForegroundColor Yellow
}

# Step 5: Start dev server
Write-Host "[5/5] Starting dev server..." -ForegroundColor Yellow
Write-Host "  → Running: npm run dev`n" -ForegroundColor Cyan

Write-Host "========================================" -ForegroundColor Green
Write-Host "Frontend starting..." -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Once started, access the app at:" -ForegroundColor White
Write-Host "  → http://localhost:3000`n" -ForegroundColor Cyan

npm run dev
