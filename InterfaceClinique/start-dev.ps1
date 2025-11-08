# Quick fix script for InterfaceClinique
Write-Host "Fixing InterfaceClinique issues..." -ForegroundColor Cyan

# Kill any running node processes
Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Change to InterfaceClinique directory
Set-Location c:\docqa-ms\InterfaceClinique

# Clear any cached data
if (Test-Path "node_modules/.vite") {
    Write-Host "Clearing Vite cache..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force "node_modules/.vite" -ErrorAction SilentlyContinue
}

Write-Host "Starting dev server..." -ForegroundColor Green
npm run dev
