# 🚀 Test JWT Authentication

Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host "   JWT Authentication Test - InterfaceClinique" -ForegroundColor Cyan
Write-Host "==============================================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health check (no auth required)
Write-Host "1️⃣  Testing health endpoint (no auth required)..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:8000/health/" -Method Get
    Write-Host "   ✅ Health check: $($health.status)" -ForegroundColor Green
} catch {
    Write-Host "   ❌ Health check failed" -ForegroundColor Red
}

Write-Host ""

# Test 2: User profile without token (should fail)
Write-Host "2️⃣  Testing protected endpoint without token..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/users/me" -Method Get -ErrorAction Stop
    Write-Host "   ❌ Should have been blocked!" -ForegroundColor Red
} catch {
    if ($_.Exception.Response.StatusCode -eq 403) {
        Write-Host "   ✅ Correctly blocked (403 Forbidden)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Unexpected error: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "==============================================================" -ForegroundColor Gray
Write-Host ""
Write-Host "📋 NEXT STEPS:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Open your frontend: " -NoNewline
Write-Host "http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. Click 'Se connecter avec Auth0' and login" -ForegroundColor White
Write-Host ""
Write-Host "3. Open Browser DevTools:" -ForegroundColor White
Write-Host "   - Press F12 key" -ForegroundColor Gray
Write-Host "   - Go to Console tab" -ForegroundColor Gray
Write-Host "   - Type: localStorage.getItem('token')" -ForegroundColor Gray
Write-Host "   - Copy the JWT token" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Test with your token:" -ForegroundColor White
Write-Host '   $token = "your-jwt-token-here"' -ForegroundColor Gray
Write-Host '   $headers = @{ Authorization = "Bearer $token" }' -ForegroundColor Gray
Write-Host '   Invoke-RestMethod -Uri "http://localhost:8000/api/v1/users/me" -Headers $headers' -ForegroundColor Gray
Write-Host ""
Write-Host "==============================================================" -ForegroundColor Gray
Write-Host ""
Write-Host "📚 Documentation: JWT_AUTHENTICATION_GUIDE.md" -ForegroundColor Cyan
Write-Host ""
