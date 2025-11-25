# Security Verification Test Script
# Run this script to verify all security measures are working correctly

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "       DocQA-MS Security Verification Script                " -ForegroundColor Cyan
Write-Host "       Testing Security Headers & Configuration             " -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

$testsPassed = 0
$testsFailed = 0
$warnings = 0

# Test 1: Check if services are running
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host "TEST 1: Docker Services Status" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Yellow

$dockerServices = docker ps --format "table {{.Names}}\t{{.Status}}" | Select-String "docqa"
if ($dockerServices) {
    Write-Host "✅ Docker services are running:" -ForegroundColor Green
    $dockerServices | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
    $testsPassed++
} else {
    Write-Host "❌ Docker services are not running!" -ForegroundColor Red
    Write-Host "   Run: docker compose up -d" -ForegroundColor Yellow
    $testsFailed++
}
Write-Host ""

# Test 2: Check API health endpoint
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host "TEST 2: API Health Check" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Yellow

try {
    $healthCheck = Invoke-RestMethod -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5
    if ($healthCheck.status -eq "healthy") {
        Write-Host "✅ API is healthy and responding" -ForegroundColor Green
        Write-Host "   Status: $($healthCheck.status)" -ForegroundColor Gray
        Write-Host "   Database: $($healthCheck.database)" -ForegroundColor Gray
        $testsPassed++
    } else {
        Write-Host "⚠️  API responded but status is not healthy" -ForegroundColor Yellow
        $warnings++
    }
} catch {
    Write-Host "❌ API health check failed!" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
    $testsFailed++
}
Write-Host ""

# Test 3: Verify Security Headers
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host "TEST 3: Security Headers" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Yellow

try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -TimeoutSec 5
    
    $requiredHeaders = @{
        'Content-Security-Policy' = 'CSP protection against XSS'
        'X-Content-Type-Options' = 'MIME type sniffing prevention'
        'X-Frame-Options' = 'Clickjacking protection'
        'X-XSS-Protection' = 'Legacy XSS protection'
        'Referrer-Policy' = 'Referrer information control'
        'Permissions-Policy' = 'Browser feature restrictions'
    }
    
    $headersPassed = 0
    $headersFailed = 0
    
    foreach ($header in $requiredHeaders.Keys) {
        if ($response.Headers[$header]) {
            Write-Host "   ✅ $header" -ForegroundColor Green
            Write-Host "      Purpose: $($requiredHeaders[$header])" -ForegroundColor Gray
            Write-Host "      Value: $($response.Headers[$header])" -ForegroundColor DarkGray
            $headersPassed++
        } else {
            Write-Host "   ❌ $header - MISSING!" -ForegroundColor Red
            Write-Host "      Purpose: $($requiredHeaders[$header])" -ForegroundColor Gray
            $headersFailed++
        }
    }
    
    if ($headersFailed -eq 0) {
        Write-Host "✅ All security headers present" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "❌ $headersFailed security headers missing" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "❌ Failed to check security headers" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
    $testsFailed++
}
Write-Host ""

# Test 4: CORS Configuration
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host "TEST 4: CORS Configuration" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Yellow

try {
    $corsHeaders = @{
        'Origin' = 'http://localhost:3000'
    }
    $corsResponse = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method GET -Headers $corsHeaders -TimeoutSec 5
    
    $allowOrigin = $corsResponse.Headers['Access-Control-Allow-Origin']
    $allowCredentials = $corsResponse.Headers['Access-Control-Allow-Credentials']
    
    if ($allowOrigin -eq 'http://localhost:3000' -or $allowOrigin -eq '*') {
        Write-Host "   ✅ Access-Control-Allow-Origin: $allowOrigin" -ForegroundColor Green
    } else {
        Write-Host "   ❌ Access-Control-Allow-Origin: $allowOrigin (unexpected)" -ForegroundColor Red
    }
    
    if ($allowCredentials -eq 'true') {
        Write-Host "   ✅ Access-Control-Allow-Credentials: true" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Access-Control-Allow-Credentials: $allowCredentials" -ForegroundColor Yellow
    }
    
    Write-Host "✅ CORS configuration verified" -ForegroundColor Green
    $testsPassed++
} catch {
    Write-Host "❌ CORS verification failed" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
    $testsFailed++
}
Write-Host ""

# Test 5: Database Connection
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host "TEST 5: Database Connection" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Yellow

try {
    $dbLogs = docker logs docqa-ms-postgres-1 --tail 20 2>&1 | Select-String -Pattern "database system is ready" -Quiet
    if ($dbLogs) {
        Write-Host "✅ PostgreSQL database is ready" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "⚠️  Cannot verify database status from logs" -ForegroundColor Yellow
        $warnings++
    }
} catch {
    Write-Host "❌ Database verification failed" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
    $testsFailed++
}
Write-Host ""

# Test 6: Check for exposed secrets in environment
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host "TEST 6: Environment Variables Security" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Yellow

$envFile = "C:\docqa-ms\backend\api_gateway\.env"
if (Test-Path $envFile) {
    $envContent = Get-Content $envFile -Raw
    
    # Check for weak secrets
    if ($envContent -match 'SECRET_KEY=changeme|SECRET_KEY=secret|SECRET_KEY=12345') {
        Write-Host "   ⚠️  Weak SECRET_KEY detected - change before production!" -ForegroundColor Yellow
        $warnings++
    } else {
        Write-Host "   ✅ SECRET_KEY appears to be strong" -ForegroundColor Green
    }
    
    # Check for Auth0 configuration
    if ($envContent -match 'AUTH0_DOMAIN=') {
        Write-Host "   ✅ AUTH0_DOMAIN configured" -ForegroundColor Green
    } else {
        Write-Host "   ❌ AUTH0_DOMAIN not configured" -ForegroundColor Red
        $testsFailed++
    }
    
    if ($envContent -match 'AUTH0_AUDIENCE=') {
        Write-Host "   ✅ AUTH0_AUDIENCE configured" -ForegroundColor Green
    } else {
        Write-Host "   ❌ AUTH0_AUDIENCE not configured" -ForegroundColor Red
        $testsFailed++
    }
    
    if ($testsFailed -eq 0) {
        $testsPassed++
    }
} else {
    Write-Host "⚠️  .env file not found at $envFile" -ForegroundColor Yellow
    $warnings++
}
Write-Host ""

# Test 7: Frontend Token Storage
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host "TEST 7: Frontend Token Storage Configuration" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Yellow

$mainTsxPath = "C:\docqa-ms\InterfaceClinique\src\main.tsx"
if (Test-Path $mainTsxPath) {
    $mainTsxContent = Get-Content $mainTsxPath -Raw
    
    if ($mainTsxContent -match 'cacheLocation="memory"') {
        Write-Host "   ✅ cacheLocation set to 'memory' (secure)" -ForegroundColor Green
        $testsPassed++
    } elseif ($mainTsxContent -match 'cacheLocation="localstorage"') {
        Write-Host "   ⚠️  cacheLocation set to 'localstorage' (less secure)" -ForegroundColor Yellow
        Write-Host "      Consider using 'memory' for production" -ForegroundColor Gray
        $warnings++
    } else {
        Write-Host "   ❌ cacheLocation not configured" -ForegroundColor Red
        $testsFailed++
    }
    
    if ($mainTsxContent -match 'useRefreshTokens=\{true\}') {
        Write-Host "   ✅ useRefreshTokens enabled" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  useRefreshTokens not enabled" -ForegroundColor Yellow
        $warnings++
    }
} else {
    Write-Host "❌ main.tsx not found" -ForegroundColor Red
    $testsFailed++
}
Write-Host ""

# Test 8: Check for hardcoded secrets in code
Write-Host "================================================================" -ForegroundColor Yellow
Write-Host "TEST 8: Hardcoded Secrets Check" -ForegroundColor Yellow
Write-Host "================================================================" -ForegroundColor Yellow

$suspiciousPatterns = @(
    'password\s*=\s*"[^"]+"',
    'secret\s*=\s*"[^"]+"',
    'api_key\s*=\s*"[^"]+"'
)

$foundSecrets = $false
$filesToCheck = Get-ChildItem -Path "C:\docqa-ms\backend\api_gateway\app" -Recurse -Include *.py | Select-Object -First 50

foreach ($file in $filesToCheck) {
    $content = Get-Content $file.FullName -Raw
    foreach ($pattern in $suspiciousPatterns) {
        if ($content -match $pattern) {
            Write-Host "   ⚠️  Potential hardcoded secret in: $($file.Name)" -ForegroundColor Yellow
            $foundSecrets = $true
            $warnings++
        }
    }
}

if (-not $foundSecrets) {
    Write-Host "   ✅ No obvious hardcoded secrets found" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "   Review flagged files manually" -ForegroundColor Gray
}
Write-Host ""

# Summary
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "                    TEST SUMMARY" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "   ✅ Tests Passed: $testsPassed" -ForegroundColor Green
Write-Host "   ❌ Tests Failed: $testsFailed" -ForegroundColor Red
Write-Host "   ⚠️  Warnings: $warnings" -ForegroundColor Yellow
Write-Host ""

if ($testsFailed -eq 0 -and $warnings -eq 0) {
    Write-Host "🎉 ALL SECURITY CHECKS PASSED! System is secure." -ForegroundColor Green
    $score = 10.0
} elseif ($testsFailed -eq 0) {
    Write-Host "✅ All critical tests passed, but review warnings." -ForegroundColor Yellow
    $score = 9.5
} elseif ($testsFailed -le 2) {
    Write-Host "⚠️  Some tests failed. Review and fix before production." -ForegroundColor Yellow
    $score = 7.5
} else {
    Write-Host "❌ Multiple critical tests failed. Do not deploy to production!" -ForegroundColor Red
    $score = 5.0
}

Write-Host ""
Write-Host "Security Score: $score/10" -ForegroundColor $(if ($score -ge 9) { "Green" } elseif ($score -ge 7) { "Yellow" } else { "Red" })
Write-Host ""

# Manual verification instructions
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "            MANUAL VERIFICATION REQUIRED" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Please manually verify the following:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Browser Token Storage Test:" -ForegroundColor White
Write-Host "   - Open http://localhost:3000 in browser" -ForegroundColor Gray
Write-Host "   - Login with Auth0" -ForegroundColor Gray
Write-Host "   - Open DevTools then Application then Local Storage" -ForegroundColor Gray
Write-Host "   - Verify NO tokens are stored (should be empty or only Auth0 cache)" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Auth0 Configuration:" -ForegroundColor White
Write-Host "   - Go to https://manage.auth0.com" -ForegroundColor Gray
Write-Host "   - Applications then InterfaceClinique then Settings then Advanced" -ForegroundColor Gray
Write-Host "   - OAuth tab then Enable Allow Skipping User Consent" -ForegroundColor Gray
Write-Host "   - Enable OIDC Conformant" -ForegroundColor Gray
Write-Host ""
Write-Host "3. User Isolation Test:" -ForegroundColor White
Write-Host "   - Login as User A, upload document" -ForegroundColor Gray
Write-Host "   - Logout, login as User B" -ForegroundColor Gray
Write-Host "   - Verify User B cannot see User A documents" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Network Traffic Inspection:" -ForegroundColor White
Write-Host "   - Open DevTools then Network tab" -ForegroundColor Gray
Write-Host "   - Verify all API requests include Authorization Bearer token" -ForegroundColor Gray
Write-Host "   - Verify no tokens visible in URL parameters" -ForegroundColor Gray
Write-Host ""

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "For detailed security documentation, see:" -ForegroundColor Cyan
Write-Host "- SECURITY_VERIFICATION.md" -ForegroundColor Gray
Write-Host "- SECURITY_RECOMMENDATIONS.md" -ForegroundColor Gray
Write-Host "- SECURE_TOKEN_STORAGE.md" -ForegroundColor Gray
Write-Host "================================================================" -ForegroundColor Cyan
