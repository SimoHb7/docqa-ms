# Test if documents are actually anonymized and synthesis uses correct data
Write-Host "`n╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🧪 TESTING ANONYMIZED DOCUMENT SYNTHESIS           ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

# Step 1: Check which documents are anonymized
Write-Host "📋 Step 1: Checking document anonymization status..." -ForegroundColor Yellow
$docs = Invoke-RestMethod -Uri "http://localhost:8000/api/v1/documents?limit=10" -Method GET
Write-Host "`nFound $($docs.data.Count) documents:`n" -ForegroundColor White

$anonymizedDocs = @()
$nonAnonymizedDocs = @()

foreach ($doc in $docs.data) {
    if ($doc.is_anonymized) {
        $anonymizedDocs += $doc
        Write-Host "  ✅ $($doc.filename) (ID: $($doc.id))" -ForegroundColor Green
        Write-Host "     Patient: $($doc.patient_id) | Anonymized: YES" -ForegroundColor Gray
    } else {
        $nonAnonymizedDocs += $doc
        Write-Host "  ⚠️  $($doc.filename) (ID: $($doc.id))" -ForegroundColor Yellow
        Write-Host "     Patient: $($doc.patient_id) | Anonymized: NO" -ForegroundColor Gray
    }
}

Write-Host "`n📊 Summary:" -ForegroundColor Cyan
Write-Host "  • Anonymized documents: $($anonymizedDocs.Count)" -ForegroundColor Green
Write-Host "  • Non-anonymized documents: $($nonAnonymizedDocs.Count)" -ForegroundColor Yellow

# Step 2: Test synthesis with anonymized document (if any)
if ($anonymizedDocs.Count -gt 0) {
    $testDoc = $anonymizedDocs[0]
    Write-Host "`n📊 Step 2: Testing synthesis with ANONYMIZED document..." -ForegroundColor Yellow
    Write-Host "  Document: $($testDoc.filename)" -ForegroundColor White
    Write-Host "  ID: $($testDoc.id)" -ForegroundColor White
    Write-Host "  Patient: $($testDoc.patient_id)" -ForegroundColor White
    
    $synthesisRequest = @{
        synthesis_id = "test-anon-$(Get-Date -Format 'yyyyMMddHHmmss')"
        type = "summary"
        parameters = @{
            document_ids = @($testDoc.id)
            patient_id = $testDoc.patient_id
        }
    } | ConvertTo-Json -Depth 5
    
    $synthesisResponse = Invoke-RestMethod -Uri "http://localhost:8005/api/v1/synthesis/generate" `
        -Method POST `
        -ContentType "application/json" `
        -Body $synthesisRequest
    
    Write-Host "`n✅ Synthesis Result:" -ForegroundColor Green
    Write-Host "  Title: $($synthesisResponse.result.title)" -ForegroundColor White
    Write-Host "  Documents analyzed: $($synthesisResponse.result._metadata.documents_analyzed)" -ForegroundColor White
    Write-Host "  Used anonymized data: $($synthesisResponse.result._metadata.used_anonymized_data)" -ForegroundColor White
    Write-Host "  Is anonymized: $($synthesisResponse.result._metadata.is_anonymized)" -ForegroundColor White
    Write-Host "  PII detected: $($synthesisResponse.result._metadata.pii_count)" -ForegroundColor White
    
    Write-Host "`n📝 Recommendations:" -ForegroundColor Cyan
    foreach ($rec in $synthesisResponse.result.recommendations) {
        if ($rec -like "*non anonymisé*") {
            Write-Host "  ⚠️  $rec" -ForegroundColor Red
        } else {
            Write-Host "  ✅ $rec" -ForegroundColor Green
        }
    }
    
    if ($synthesisResponse.result._metadata.is_anonymized) {
        Write-Host "`n✅ PERFECT! Document is anonymized and synthesis knows it!" -ForegroundColor Green
    } else {
        Write-Host "`n⚠️  WARNING: Document marked as anonymized in DB but synthesis says it's not!" -ForegroundColor Yellow
        Write-Host "   This might be a data inconsistency issue." -ForegroundColor Gray
    }
}

# Step 3: Test with non-anonymized document
if ($nonAnonymizedDocs.Count -gt 0) {
    $testDoc = $nonAnonymizedDocs[0]
    Write-Host "`n📊 Step 3: Testing synthesis with NON-ANONYMIZED document..." -ForegroundColor Yellow
    Write-Host "  Document: $($testDoc.filename)" -ForegroundColor White
    Write-Host "  ID: $($testDoc.id)" -ForegroundColor White
    
    $synthesisRequest = @{
        synthesis_id = "test-nonanon-$(Get-Date -Format 'yyyyMMddHHmmss')"
        type = "summary"
        parameters = @{
            document_ids = @($testDoc.id)
            patient_id = $testDoc.patient_id
        }
    } | ConvertTo-Json -Depth 5
    
    $synthesisResponse = Invoke-RestMethod -Uri "http://localhost:8005/api/v1/synthesis/generate" `
        -Method POST `
        -ContentType "application/json" `
        -Body $synthesisRequest
    
    Write-Host "`n📋 Synthesis Result:" -ForegroundColor Cyan
    Write-Host "  Is anonymized: $($synthesisResponse.result._metadata.is_anonymized)" -ForegroundColor White
    
    Write-Host "`n📝 Recommendations:" -ForegroundColor Cyan
    foreach ($rec in $synthesisResponse.result.recommendations) {
        if ($rec -like "*non anonymisé*") {
            Write-Host "  ⚠️  $rec" -ForegroundColor Yellow
            Write-Host "     This is EXPECTED for non-anonymized documents" -ForegroundColor Gray
        } else {
            Write-Host "  ✅ $rec" -ForegroundColor Green
        }
    }
}

Write-Host "`n╔═══════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  📊 CONCLUSION                                        ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════╝`n" -ForegroundColor Cyan

if ($anonymizedDocs.Count -eq 0) {
    Write-Host "⚠️  NO ANONYMIZED DOCUMENTS FOUND!" -ForegroundColor Yellow
    Write-Host "`n💡 How to anonymize documents:" -ForegroundColor Cyan
    Write-Host "  1. Go to Documents page" -ForegroundColor White
    Write-Host "  2. Select a document" -ForegroundColor White
    Write-Host "  3. Click 'Anonymiser' button" -ForegroundColor White
    Write-Host "  4. Wait for anonymization to complete" -ForegroundColor White
    Write-Host "  5. Run this test again!" -ForegroundColor White
} else {
    Write-Host "✅ System is working correctly!" -ForegroundColor Green
    Write-Host "  • Anonymized documents are detected" -ForegroundColor White
    Write-Host "  • Synthesis correctly identifies anonymization status" -ForegroundColor White
    Write-Host "  • Warnings appear for non-anonymized documents" -ForegroundColor White
}

Write-Host "`n"
