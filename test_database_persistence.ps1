# Test Database Persistence
# This test verifies that data flows through the API and is stored in PostgreSQL

$ErrorActionPreference = "Stop"
$API_BASE = "http://localhost:8000"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DATABASE PERSISTENCE TEST" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Create test document
Write-Host "[1/6] Creating test medical document..." -ForegroundColor Yellow

$medicalContent = @"
RAPPORT MEDICAL CONSULTATION

Date: 28 octobre 2025
Patient: Sophie MARTIN
Date de naissance: 12/05/1978
Numero de securite sociale: 2 78 05 69 123 456 89
Adresse: 15 Boulevard Victor Hugo, 31000 Toulouse
Telephone: 05 61 22 33 44
Email: sophie.martin@email.fr

ANTECEDENTS:
- Hypertension arterielle depuis 2019
- Diabete de type 2 diagnostique en 2021
- Hypercholesterolemie

TRAITEMENT ACTUEL:
- Ramipril 5mg 1x/jour
- Metformine 850mg 2x/jour
- Atorvastatine 20mg 1x/jour

EXAMEN CLINIQUE:
- Poids: 75 kg
- Taille: 165 cm
- IMC: 27.5
- Tension arterielle: 138/85 mmHg
- Glycemie a jeun: 1.15 g/L

DIAGNOSTIC:
Hypertension arterielle controlee
Diabete de type 2 avec bon controle glycemique

PLAN THERAPEUTIQUE:
- Maintien traitement actuel
- Controle dans 3 mois
- Bilan biologique trimestriel

Dr. Pierre DURAND
Service de Medecine Generale
"@

$tempFile = "$env:TEMP\medical_report_test_$(Get-Date -Format 'yyyyMMddHHmmss').txt"
$medicalContent | Out-File -FilePath $tempFile -Encoding UTF8

Write-Host "  [OK] Test document created" -ForegroundColor Green

# Step 2: Upload document via API Gateway
Write-Host "`n[2/6] Uploading document via API Gateway..." -ForegroundColor Yellow

try {
    $fileBytes = [System.IO.File]::ReadAllBytes($tempFile)
    $fileName = [System.IO.Path]::GetFileName($tempFile)
    
    $boundary = [System.Guid]::NewGuid().ToString()
    $LF = "`r`n"
    
    $bodyLines = @(
        "--$boundary",
        "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"",
        "Content-Type: text/plain$LF",
        $medicalContent,
        "--$boundary",
        "Content-Disposition: form-data; name=`"patient_id`"$LF",
        "TEST-PATIENT-002",
        "--$boundary",
        "Content-Disposition: form-data; name=`"document_type`"$LF",
        "medical_report",
        "--$boundary--$LF"
    )
    
    $body = $bodyLines -join $LF
    
    $uploadResponse = Invoke-RestMethod -Uri "$API_BASE/api/v1/documents/upload" `
        -Method POST `
        -Body $body `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -TimeoutSec 30
    
    $documentId = $uploadResponse.document_id
    Write-Host "  [OK] Document uploaded" -ForegroundColor Green
    Write-Host "      Document ID: $documentId" -ForegroundColor Gray
    
} catch {
    Write-Host "  [FAIL] Upload failed: $_" -ForegroundColor Red
    exit 1
}

# Step 3: Wait for processing
Write-Host "`n[3/6] Waiting for document processing..." -ForegroundColor Yellow
Start-Sleep -Seconds 3
Write-Host "  [OK] Wait completed" -ForegroundColor Green

# Step 4: Check document in database
Write-Host "`n[4/6] Verifying document in database..." -ForegroundColor Yellow

$docQuery = "SELECT id, filename, file_type, file_size, processing_status, is_anonymized, created_at FROM documents WHERE id = '$documentId';"
$docResult = docker exec docqa-ms-postgres-1 psql -U user -d docqa_db -c $docQuery 2>$null

if ($docResult -match $documentId) {
    Write-Host "  [OK] Document found in database" -ForegroundColor Green
    Write-Host $docResult -ForegroundColor Gray
} else {
    Write-Host "  [FAIL] Document NOT found in database" -ForegroundColor Red
    Write-Host "      Query: $docQuery" -ForegroundColor Yellow
}

# Step 5: De-identify and index
Write-Host "`n[5/6] De-identifying and indexing..." -ForegroundColor Yellow

try {
    # De-identify
    $deidRequest = @{
        document_id = $documentId
        content = $medicalContent
        language = "fr"
    } | ConvertTo-Json
    
    $deidResponse = Invoke-RestMethod -Uri "$API_BASE/api/v1/deid/anonymize" `
        -Method POST `
        -Body $deidRequest `
        -ContentType "application/json"
    
    Write-Host "  [OK] De-identification complete" -ForegroundColor Green
    Write-Host "      PII entities: $($deidResponse.pii_entities.Count)" -ForegroundColor Gray
    
    $anonymizedContent = $deidResponse.anonymized_content
    
    # Create chunks for indexing
    $chunks = @()
    $lines = $anonymizedContent -split "`n"
    $chunkSize = 10
    $chunkIndex = 0
    
    for ($i = 0; $i -lt $lines.Count; $i += $chunkSize) {
        $chunkLines = $lines[$i..[Math]::Min($i + $chunkSize - 1, $lines.Count - 1)]
        $chunkContent = $chunkLines -join "`n"
        
        if ($chunkContent.Trim().Length -gt 20) {
            $chunks += @{
                index = $chunkIndex
                content = $chunkContent.Trim()
                sentences = @($chunkContent.Trim())
                metadata = @{
                    document_id = $documentId
                    chunk_index = $chunkIndex
                }
            }
            $chunkIndex++
        }
    }
    
    # Index
    $indexRequest = @{
        document_id = $documentId
        chunks = $chunks
        metadata = @{
            title = "Medical Report Test"
            source_type = "medical_report"
        }
    } | ConvertTo-Json -Depth 10
    
    $indexResponse = Invoke-RestMethod -Uri "$API_BASE/api/v1/indexer/" `
        -Method POST `
        -Body $indexRequest `
        -ContentType "application/json"
    
    Write-Host "  [OK] Indexing complete" -ForegroundColor Green
    Write-Host "      Chunks indexed: $($indexResponse.chunks_created)" -ForegroundColor Gray
    
} catch {
    Write-Host "  [FAIL] De-ID/Index failed: $_" -ForegroundColor Red
}

# Step 6: Ask a question to create Q&A interaction
Write-Host "`n[6/6] Creating Q&A interaction..." -ForegroundColor Yellow

try {
    Start-Sleep -Seconds 2
    
    Add-Type -AssemblyName System.Web
    $question = [System.Web.HttpUtility]::UrlEncode("Quel est le traitement de l'hypertension?")
    
    $qaResponse = Invoke-RestMethod -Uri "$API_BASE/api/v1/qa/ask?question=$question" `
        -Method GET `
        -TimeoutSec 30
    
    Write-Host "  [OK] Q&A completed" -ForegroundColor Green
    Write-Host "      Answer length: $($qaResponse.answer.Length) chars" -ForegroundColor Gray
    
} catch {
    Write-Host "  [WARN] Q&A failed: $_" -ForegroundColor Yellow
}

# Final Database Verification
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "FINAL DATABASE VERIFICATION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "[DB] Overall Statistics:" -ForegroundColor Yellow
docker exec docqa-ms-postgres-1 psql -U user -d docqa_db -c "SELECT 'documents' as table_name, COUNT(*) as count FROM documents UNION ALL SELECT 'document_chunks', COUNT(*) FROM document_chunks UNION ALL SELECT 'qa_interactions', COUNT(*) FROM qa_interactions;"

Write-Host "`n[DB] Document Details:" -ForegroundColor Yellow
docker exec docqa-ms-postgres-1 psql -U user -d docqa_db -c "SELECT id, filename, file_type, file_size, processing_status, is_anonymized FROM documents WHERE id = '$documentId';"

Write-Host "`n[DB] Document Chunks:" -ForegroundColor Yellow
docker exec docqa-ms-postgres-1 psql -U user -d docqa_db -c "SELECT id, LEFT(content, 80) as content_preview, chunk_index FROM document_chunks WHERE document_id = '$documentId' ORDER BY chunk_index LIMIT 3;"

Write-Host "`n[DB] Q&A Interactions:" -ForegroundColor Yellow
docker exec docqa-ms-postgres-1 psql -U user -d docqa_db -c "SELECT id, LEFT(question, 60) as question, LEFT(answer, 60) as answer_preview, confidence_score FROM qa_interactions ORDER BY created_at DESC LIMIT 2;"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "TEST COMPLETED" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Cleanup
Remove-Item $tempFile -ErrorAction SilentlyContinue
