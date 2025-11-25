# 🚀 Test Auth0 Setup Script
# Run this after configuring Auth0 to verify everything works

Write-Host "🔐 Testing Auth0 Configuration..." -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (Test-Path ".\InterfaceClinique\.env") {
    Write-Host "✅ .env file found" -ForegroundColor Green
    
    # Read and display Auth0 config
    $envContent = Get-Content ".\InterfaceClinique\.env" | Where-Object { $_ -match "VITE_AUTH0" }
    Write-Host "📝 Current Auth0 Configuration:" -ForegroundColor Yellow
    $envContent | ForEach-Object { Write-Host "   $_" -ForegroundColor White }
    Write-Host ""
} else {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    Write-Host "   Create it from .env.example" -ForegroundColor Yellow
    exit 1
}

# Check if frontend is running
Write-Host "🔍 Checking if frontend is running..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5173" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Frontend is running on http://localhost:5173" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend is not running!" -ForegroundColor Red
    Write-Host "   Start it with: cd InterfaceClinique; npm run dev" -ForegroundColor Yellow
}

Write-Host ""

# Check if backend is running  
Write-Host "🔍 Checking if backend is running..." -ForegroundColor Cyan
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "✅ Backend is running on http://localhost:8000" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend is not running!" -ForegroundColor Red
    Write-Host "   Start it with: docker compose up -d" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Open Auth0 Dashboard: https://manage.auth0.com" -ForegroundColor White
Write-Host "   2. Go to Applications → Applications → InterfaceClinique" -ForegroundColor White
Write-Host "   3. Add these Callback URLs:" -ForegroundColor White
Write-Host "      http://localhost:5173,http://localhost:5173/callback" -ForegroundColor Yellow
Write-Host "   4. Add these Logout URLs:" -ForegroundColor White
Write-Host "      http://localhost:5173" -ForegroundColor Yellow
Write-Host "   5. Add these Web Origins:" -ForegroundColor White
Write-Host "      http://localhost:5173,http://localhost:8000" -ForegroundColor Yellow
Write-Host "   6. Save changes in Auth0" -ForegroundColor White
Write-Host "   7. Open http://localhost:5173 and click 'Se connecter'" -ForegroundColor White
Write-Host ""
Write-Host "✨ Ready to test login!" -ForegroundColor Green
