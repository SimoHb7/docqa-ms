# 🎯 Complete Auth0 Test - All in One
# This script checks everything and provides clear next steps

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   🔐 InterfaceClinique - Auth0 Setup Check    ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# 1. Check .env configuration
Write-Host "1️⃣  Checking environment configuration..." -ForegroundColor Yellow
$envPath = ".\InterfaceClinique\.env"
if (Test-Path $envPath) {
    $domain = (Get-Content $envPath | Select-String "VITE_AUTH0_DOMAIN=").Line -replace "VITE_AUTH0_DOMAIN=", ""
    $clientId = (Get-Content $envPath | Select-String "VITE_AUTH0_CLIENT_ID=").Line -replace "VITE_AUTH0_CLIENT_ID=", ""
    $audience = (Get-Content $envPath | Select-String "VITE_AUTH0_AUDIENCE=").Line -replace "VITE_AUTH0_AUDIENCE=", ""
    
    if ($domain -and $domain -ne "your-domain.auth0.com") {
        Write-Host "   ✅ Auth0 Domain configured: $domain" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Auth0 Domain NOT configured!" -ForegroundColor Red
        exit 1
    }
    
    if ($clientId -and $clientId -ne "your-client-id-here") {
        Write-Host "   ✅ Auth0 Client ID configured" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Auth0 Client ID NOT configured!" -ForegroundColor Red
        exit 1
    }
    
    if ($audience) {
        Write-Host "   ✅ Auth0 Audience configured: $audience" -ForegroundColor Green
    }
} else {
    Write-Host "   ❌ .env file not found!" -ForegroundColor Red
    exit 1
}

Write-Host ""

# 2. Check Docker services
Write-Host "2️⃣  Checking Docker services..." -ForegroundColor Yellow
$containers = docker ps --format "{{.Names}}" 2>$null
if ($containers -match "postgres" -and $containers -match "api-gateway") {
    Write-Host "   ✅ Docker services running" -ForegroundColor Green
} else {
    Write-Host "   ⚠️  Docker services not fully running" -ForegroundColor Yellow
    Write-Host "   Run: docker compose up -d" -ForegroundColor Cyan
}

Write-Host ""

# 3. Check backend API
Write-Host "3️⃣  Checking backend API..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health" -TimeoutSec 3 -ErrorAction Stop
    Write-Host "   ✅ Backend API is healthy" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Backend API not responding" -ForegroundColor Red
    Write-Host "   Run: docker compose up -d" -ForegroundColor Cyan
}

Write-Host ""

# 4. Check frontend
Write-Host "4️⃣  Checking frontend..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 2 -ErrorAction Stop | Out-Null
    Write-Host "   ✅ Frontend is running" -ForegroundColor Green
    Write-Host "   🌐 Open: http://localhost:3000" -ForegroundColor Cyan
} catch {
    Write-Host "   ⚠️  Frontend not running" -ForegroundColor Yellow
    Write-Host "   Run: cd InterfaceClinique; npm run dev" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""

# Final instructions
Write-Host "📋 NEXT STEPS TO COMPLETE AUTH0 SETUP:" -ForegroundColor Yellow
Write-Host ""
Write-Host "   Step 1: Configure Auth0 Dashboard" -ForegroundColor White
Write-Host "   ────────────────────────────────" -ForegroundColor Gray
Write-Host "   1. Open: " -NoNewline; Write-Host "https://manage.auth0.com" -ForegroundColor Cyan
Write-Host "   2. Go to: Applications → Applications → InterfaceClinique" -ForegroundColor White
Write-Host "   3. Scroll to 'Application URIs' section" -ForegroundColor White
Write-Host ""
Write-Host "   4. Add these URLs:" -ForegroundColor Yellow
Write-Host ""
Write-Host "      Allowed Callback URLs:" -ForegroundColor White
Write-Host "      http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "      Allowed Logout URLs:" -ForegroundColor White  
Write-Host "      http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "      Allowed Web Origins:" -ForegroundColor White
Write-Host "      http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "   5. Scroll down and click " -NoNewline
Write-Host "💾 Save Changes" -ForegroundColor Green
Write-Host ""
Write-Host "   Step 2: Create Auth0 API (Recommended)" -ForegroundColor White
Write-Host "   ────────────────────────────────────────" -ForegroundColor Gray
Write-Host "   1. Go to: Applications → APIs → " -NoNewline
Write-Host "+ Create API" -ForegroundColor Cyan
Write-Host "   2. Name: InterfaceClinique API" -ForegroundColor White
Write-Host "   3. Identifier: https://api.interfaceclinique.com" -ForegroundColor Cyan
Write-Host "   4. Click Create" -ForegroundColor White
Write-Host ""
Write-Host "   Step 3: Test Login" -ForegroundColor White
Write-Host "   ─────────────────" -ForegroundColor Gray
   Write-Host "   1. Open: " -NoNewline; Write-Host "http://localhost:3000" -ForegroundColor Cyan
Write-Host "   2. Click: Se connecter avec Auth0" -ForegroundColor White
Write-Host "   3. Sign up or log in" -ForegroundColor White
Write-Host "   4. You will be redirected to the dashboard" -ForegroundColor White
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Documentation:" -ForegroundColor Yellow
Write-Host "   • Quick Guide: InterfaceClinique\QUICK_AUTH0_SETUP.md" -ForegroundColor White
Write-Host "   • Full Guide:  AUTH0_SETUP_GUIDE.md" -ForegroundColor White
Write-Host ""
Write-Host "✨ Once you complete these steps, your app will be fully secured!" -ForegroundColor Green
Write-Host ""
