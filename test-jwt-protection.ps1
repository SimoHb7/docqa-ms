# Test JWT Protection on All Endpoints

Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host "   JWT Protection Test - All Endpoints Secured" -ForegroundColor Cyan
Write-Host "=============================================================" -ForegroundColor Cyan
Write-Host ""

$endpoints = @(
    @{ Name = "Documents List"; URL = "http://localhost:8000/api/v1/documents/" },
    @{ Name = "Dashboard Stats"; URL = "http://localhost:8000/api/v1/dashboard/stats" },
    @{ Name = "Search"; URL = "http://localhost:8000/api/v1/search/suggestions?prefix=test" },
    @{ Name = "QA Sessions"; URL = "http://localhost:8000/api/v1/qa/sessions" },
    @{ Name = "Synthesis List"; URL = "http://localhost:8000/api/v1/synthesis/" },
    @{ Name = "Audit Logs"; URL = "http://localhost:8000/api/v1/audit/logs" },
    @{ Name = "User Profile"; URL = "http://localhost:8000/api/v1/users/me" }
)

$protected = 0
$failed = 0

foreach ($endpoint in $endpoints) {
    Write-Host "Testing: $($endpoint.Name)..." -NoNewline
    
    try {
        $response = Invoke-RestMethod -Uri $endpoint.URL -Method Get -ErrorAction Stop
        Write-Host " ❌ NOT PROTECTED!" -ForegroundColor Red
        $failed++
    } catch {
        if ($_.Exception.Response.StatusCode -eq 403 -or $_.Exception.Response.StatusCode -eq 401) {
            Write-Host " ✅ Protected (403/401)" -ForegroundColor Green
            $protected++
        } else {
            Write-Host " ⚠️  Unexpected: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
            $failed++
        }
    }
}

Write-Host ""
Write-Host "=============================================================" -ForegroundColor Gray
Write-Host ""
Write-Host "📊 Results:" -ForegroundColor Yellow
Write-Host "   Protected endpoints: $protected / $($endpoints.Count)" -ForegroundColor $(if ($protected -eq $endpoints.Count) { "Green" } else { "Yellow" })
Write-Host "   Failed/Unprotected: $failed" -ForegroundColor $(if ($failed -eq 0) { "Green" } else { "Red" })
Write-Host ""

if ($protected -eq $endpoints.Count) {
    Write-Host "✅ SUCCESS! All endpoints are properly protected with JWT!" -ForegroundColor Green
} else {
    Write-Host "❌ WARNING: Some endpoints are not properly protected!" -ForegroundColor Red
}

Write-Host ""
Write-Host "=============================================================" -ForegroundColor Gray
Write-Host ""
Write-Host "🔐 JWT Authentication is ACTIVE!" -ForegroundColor Cyan
Write-Host ""
Write-Host "To access the API:" -ForegroundColor White
Write-Host "1. Login at: http://localhost:3000" -ForegroundColor Gray
Write-Host "2. Get token from localStorage" -ForegroundColor Gray
Write-Host "3. Use: Authorization: Bearer <token>" -ForegroundColor Gray
Write-Host ""
Write-Host "Swagger UI: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "(Click 'Authorize' button to test with JWT)" -ForegroundColor Gray
Write-Host ""
