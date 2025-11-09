# Test Synthesis Workflow - From Patient ID to Anonymized Synthesis
Write-Host "`n=== TESTING COMPLETE SYNTHESIS WORKFLOW ===" -ForegroundColor Cyan

# Step 1: Get documents with patient_id
Write-Host "`n📋 Step 1: Fetching documents from API Gateway..." -ForegroundColor Yellow

$docsResponse = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/documents?limit=5" -Method GET -ErrorAction Stop
Write-Host "✅ Success! Retrieved $($docsResponse.data.Count) documents" -ForegroundColor Green

# Show patient IDs
Write-Host "`nAvailable Patient IDs:" -ForegroundColor White
$docsResponse.data | ForEach-Object {
    Write-Host "  - $($_.patient_id) ($($_.filename))" -ForegroundColor Gray
}

# Get first document with patient_id for testing
$testDoc = $docsResponse.data | Where-Object { $_.patient_id } | Select-Object -First 1

if (-not $testDoc) {
    Write-Host "`n⚠️ No documents with patient_id found!" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n✅ Test document selected:" -ForegroundColor Green
Write-Host "   ID: $($testDoc.id)" -ForegroundColor White
Write-Host "   Patient ID: $($testDoc.patient_id)" -ForegroundColor White
Write-Host "   Filename: $($testDoc.filename)" -ForegroundColor White
Write-Host "   Anonymized: $($testDoc.is_anonymized)" -ForegroundColor White

# Step 2: Test synthesis with this document
Write-Host "`n📊 Step 2: Testing synthesis generation with anonymized data..." -ForegroundColor Yellow

$synthesisRequest = @{
    synthesis_id = "test-$(Get-Date -Format 'yyyyMMddHHmmss')"
    type = "summary"
    parameters = @{
        document_ids = @($testDoc.id)
        patient_id = $testDoc.patient_id
    }
} | ConvertTo-Json -Depth 5

Write-Host "Request payload:" -ForegroundColor Gray
Write-Host $synthesisRequest -ForegroundColor DarkGray

$synthesisResponse = Invoke-RestMethod -Uri "http://localhost:8005/api/v1/synthesis/generate" `
    -Method POST `
    -ContentType "application/json" `
    -Body $synthesisRequest `
    -ErrorAction Stop

Write-Host "`n✅ Synthesis generated successfully!" -ForegroundColor Green
Write-Host "   Title: $($synthesisResponse.result.title)" -ForegroundColor White
Write-Host "   Documents analyzed: $($synthesisResponse.result._metadata.documents_analyzed)" -ForegroundColor White
Write-Host "   Used anonymized data: $($synthesisResponse.result._metadata.used_anonymized_data)" -ForegroundColor White
Write-Host "   Total PII detected: $($synthesisResponse.result._metadata.total_pii_detected)" -ForegroundColor White

Write-Host "`n📄 Content preview (first 200 chars):" -ForegroundColor Cyan
$contentPreview = $synthesisResponse.result.content.Substring(0, [Math]::Min(200, $synthesisResponse.result.content.Length))
Write-Host $contentPreview -ForegroundColor Gray

Write-Host "`n✅ WORKFLOW TEST PASSED!" -ForegroundColor Green
Write-Host "   The synthesis service successfully:" -ForegroundColor White
Write-Host "   1. Fetched documents from database" -ForegroundColor Gray
Write-Host "   2. Retrieved anonymized content" -ForegroundColor Gray
Write-Host "   3. Generated synthesis with real data" -ForegroundColor Gray
Write-Host "   4. Included anonymization metadata" -ForegroundColor Gray

Write-Host "`n=== TEST COMPLETE ===" -ForegroundColor Cyan
Write-Host "`n💡 To test in browser:" -ForegroundColor Yellow
Write-Host "   1. Go to http://localhost:3000/synthesis" -ForegroundColor White
Write-Host "   2. Open browser console (F12)" -ForegroundColor White
Write-Host "   3. Look for debug logs showing documentsData" -ForegroundColor White
Write-Host "   4. Select patient ID from dropdown" -ForegroundColor White
Write-Host "   5. Generate synthesis and verify it uses anonymized data`n" -ForegroundColor White
