# Complete Workflow Test - Document Upload to Q&A with Database Verification
# Tests: Upload -> De-ID -> Index -> Search -> Q&A -> Database Check

$ErrorActionPreference = "Stop"
$baseUrl = "http://localhost:8000"

# Load System.Web for URL encoding
Add-Type -AssemblyName System.Web

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "COMPLETE WORKFLOW TEST WITH DB CHECK" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$testsPassed = 0
$testsFailed = 0

# Test 1: Health Check
Write-Host "[1/10] Health Check..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health/" -Method GET -TimeoutSec 10
    if ($health.status -eq "healthy") {
        Write-Host "  [OK] All services healthy" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  [FAIL] Services not healthy" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  [FAIL] Health check failed: $_" -ForegroundColor Red
    $testsFailed++
}

# Test 2: Create Medical Document File
Write-Host "`n[2/10] Create Medical Document File..." -ForegroundColor Yellow
try {
    $medicalContent = @"
RAPPORT MEDICAL COMPLET

INFORMATIONS PATIENT:
Nom: DUPONT Jean-Pierre
Date de naissance: 12/08/1965
Numero de securite sociale: 1 65 08 75 456 123 89
Adresse: 45 Avenue des Champs, 69001 Lyon
Telephone: 04 78 92 15 34
Email: jean.dupont@email.fr
Numero de dossier: MRN2025-789456

ANTECEDENTS MEDICAUX:
- Hypertension arterielle essentielle depuis 2018
- Diabete de type 2 diagnostique en 2020
- Dyslipidémie mixte
- Insuffisance renale chronique stade 2

TRAITEMENT ACTUEL:
1. Ramipril 10mg - 1 comprime le matin
2. Metformine 1000mg - 1 comprime matin et soir
3. Atorvastatine 40mg - 1 comprime le soir
4. Aspirine 75mg - 1 comprime par jour

EXAMEN CLINIQUE (28/10/2025):
- Poids: 82 kg
- Taille: 175 cm
- IMC: 26.8 (surpoids)
- Tension arterielle: 145/92 mmHg
- Frequence cardiaque: 78 bpm
- Temperature: 36.8°C

RESULTATS BIOLOGIQUES:
- Glycemie a jeun: 1.42 g/L (elevee)
- HbA1c: 7.8% (controle insuffisant)
- Cholesterol total: 2.15 g/L
- LDL: 1.38 g/L
- HDL: 0.52 g/L
- Triglycerides: 1.85 g/L
- Creatinine: 115 µmol/L
- DFG: 62 mL/min/1.73m²

DIAGNOSTIC PRINCIPAL:
Diabete de type 2 avec controle glycemique insuffisant

DIAGNOSTICS SECONDAIRES:
- Hypertension arterielle non controlee
- Dyslipidémie mixte
- Surpoids (IMC 26.8)
- Insuffisance renale chronique stade 2

PLAN THERAPEUTIQUE:
1. Augmentation Metformine a 2000mg par jour
2. Ajout Empagliflozine 10mg le matin
3. Renforcement surveillance tension arterielle
4. Consultation dieteticienne pour perte de poids
5. Controle biologique dans 3 mois

RECOMMANDATIONS:
- Regime diabetique strict
- Activite physique moderee 30 min/jour
- Autosurveillance glycemique 2 fois/jour
- Surveillance tension arterielle quotidienne

Dr. Sophie MARTIN
Service de Diabetologie
Hopital Lyon Sud
Tel: 04 78 86 15 00
"@

    $tempFile = "$env:TEMP\test_medical_report_$(Get-Date -Format 'yyyyMMddHHmmss').txt"
    $medicalContent | Out-File -FilePath $tempFile -Encoding UTF8
    
    Write-Host "  [OK] Medical document file created" -ForegroundColor Green
    $testsPassed++
} catch {
    Write-Host "  [FAIL] File creation failed: $_" -ForegroundColor Red
    $testsFailed++
    exit 1
}

# Test 3: Upload Medical Document
Write-Host "`n[3/10] Upload Medical Document..." -ForegroundColor Yellow
try {
    $boundary = [System.Guid]::NewGuid().ToString()
    $LF = "`r`n"
    
    $bodyLines = @(
        "--$boundary",
        "Content-Disposition: form-data; name=`"file`"; filename=`"medical_report.txt`"",
        "Content-Type: text/plain$LF",
        $medicalContent,
        "--$boundary--$LF"
    )
    
    $body = $bodyLines -join $LF
    
    $uploadResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/documents/upload" -Method POST -Body $body -ContentType "multipart/form-data; boundary=$boundary"
    $documentId = $uploadResponse.document_id
    
    Write-Host "  [OK] Document uploaded successfully" -ForegroundColor Green
    Write-Host "      - Document ID: $documentId" -ForegroundColor Gray
    $testsPassed++
} catch {
    Write-Host "  [FAIL] Upload failed: $_" -ForegroundColor Red
    $testsFailed++
    exit 1
}

# Test 4: De-identify Content
Write-Host "`n[4/10] De-identify Medical Content..." -ForegroundColor Yellow
try {
    $deidRequest = @{
        document_id = $documentId
        content = $medicalContent
        language = "fr"
    } | ConvertTo-Json -Depth 10
    
    $deidResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/deid/anonymize" -Method POST -Body $deidRequest -ContentType "application/json"
    
    Write-Host "  [OK] De-identification complete" -ForegroundColor Green
    Write-Host "      - PII entities detected: $($deidResponse.pii_entities.Count)" -ForegroundColor Gray
    Write-Host "      - Field labels preserved: $(if ($deidResponse.anonymized_content -match 'Numero de securite sociale') {'YES'} else {'NO'})" -ForegroundColor Gray
    Write-Host "      - Medical terms preserved: $(if ($deidResponse.anonymized_content -match 'Hypertension arterielle') {'YES'} else {'NO'})" -ForegroundColor Gray
    $testsPassed++
    
    $anonymizedContent = $deidResponse.anonymized_content
} catch {
    Write-Host "  [FAIL] De-identification failed: $_" -ForegroundColor Red
    $testsFailed++
}

# Test 5: Index Document
Write-Host "`n[5/10] Index Document for Semantic Search..." -ForegroundColor Yellow
try {
    $indexRequest = @{
        document_id = $documentId
        content = $anonymizedContent
        metadata = @{
            title = "Patient Medical Record - Test"
            source_type = "clinical_notes"
        }
    } | ConvertTo-Json -Depth 10
    
    $indexResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/indexer/" -Method POST -Body $indexRequest -ContentType "application/json"
    Write-Host "  [OK] Document indexed: $($indexResponse.chunks_created) chunks created" -ForegroundColor Green
    $testsPassed++
} catch {
    Write-Host "  [FAIL] Indexing failed: $_" -ForegroundColor Red
    $testsFailed++
}

# Wait for indexing
Start-Sleep -Seconds 2

# Test 6: Semantic Search - Diabetes
Write-Host "`n[6/10] Semantic Search: Diabetes Query..." -ForegroundColor Yellow
try {
    $query = [System.Web.HttpUtility]::UrlEncode("diabete type 2 traitement")
    $searchResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/search/?query=$query&top_k=5" -Method GET
    if ($searchResponse.results.Count -gt 0) {
        Write-Host "  [OK] Found $($searchResponse.results.Count) relevant chunks" -ForegroundColor Green
        Write-Host "      - Top result score: $([math]::Round($searchResponse.results[0].score, 3))" -ForegroundColor Gray
        $testsPassed++
    } else {
        Write-Host "  [FAIL] No search results found" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  [FAIL] Search failed: $_" -ForegroundColor Red
    $testsFailed++
}

# Test 7: Semantic Search - Hypertension
Write-Host "`n[7/10] Semantic Search: Hypertension Query..." -ForegroundColor Yellow
try {
    $query = [System.Web.HttpUtility]::UrlEncode("hypertension arterielle tension")
    $searchResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/search/?query=$query&top_k=5" -Method GET
    if ($searchResponse.results.Count -gt 0) {
        Write-Host "  [OK] Found $($searchResponse.results.Count) relevant chunks" -ForegroundColor Green
        $testsPassed++
    } else {
        Write-Host "  [FAIL] No search results found" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  [FAIL] Search failed: $_" -ForegroundColor Red
    $testsFailed++
}

# Test 8: Q&A - Medical Question
Write-Host "`n[8/10] Q&A: Medical Question..." -ForegroundColor Yellow
try {
    $question = [System.Web.HttpUtility]::UrlEncode("Quels sont les diagnostics principaux et le plan therapeutique propose?")
    $qaResponse = Invoke-RestMethod -Uri "$baseUrl/api/v1/qa/ask?question=$question" -Method GET
    
    if ($qaResponse.answer -and $qaResponse.answer.Length -gt 50) {
        Write-Host "  [OK] Q&A response generated" -ForegroundColor Green
        Write-Host "      - Answer length: $($qaResponse.answer.Length) characters" -ForegroundColor Gray
        Write-Host "      - Confidence: $($qaResponse.confidence)" -ForegroundColor Gray
        Write-Host "      - Sources: $($qaResponse.sources.Count)" -ForegroundColor Gray
        $testsPassed++
    } else {
        Write-Host "  [FAIL] Q&A response too short or empty" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  [FAIL] Q&A failed: $_" -ForegroundColor Red
    $testsFailed++
}

# Test 9: Statistics
Write-Host "`n[9/10] Get Statistics..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "$baseUrl/api/v1/indexer/stats" -Method GET
    Write-Host "  [OK] Statistics retrieved" -ForegroundColor Green
    Write-Host "      - Total documents: $($stats.total_documents)" -ForegroundColor Gray
    Write-Host "      - Total chunks: $($stats.total_chunks)" -ForegroundColor Gray
    Write-Host "      - Total questions: $($stats.total_questions)" -ForegroundColor Gray
    $testsPassed++
} catch {
    Write-Host "  [FAIL] Statistics failed: $_" -ForegroundColor Red
    $testsFailed++
}

# Test 10: Database Verification
Write-Host "`n[10/10] Verify Data in Database..." -ForegroundColor Yellow
try {
    # Connect to PostgreSQL and verify data exists
    $dbQuery = "SELECT (SELECT COUNT(*) FROM documents WHERE document_id = '$documentId') as doc_exists, (SELECT COUNT(*) FROM document_chunks WHERE document_id = '$documentId') as chunks_count, (SELECT COUNT(*) FROM qa_interactions WHERE document_id = '$documentId') as qa_count;"
    
    $dbResult = docker exec docqa-ms-postgres-1 psql -U user -d docqa_db -t -c $dbQuery 2>$null
    
    if ($dbResult) {
        Write-Host "  [OK] Database verification complete" -ForegroundColor Green
        Write-Host "      Database Query Results:" -ForegroundColor Gray
        Write-Host "      $dbResult" -ForegroundColor Gray
        $testsPassed++
    } else {
        Write-Host "  [FAIL] Database query returned no results" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  [FAIL] Database verification failed: $_" -ForegroundColor Red
    $testsFailed++
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TEST SUMMARY" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Passed: $testsPassed/10" -ForegroundColor Green
Write-Host "Failed: $testsFailed/10" -ForegroundColor $(if ($testsFailed -eq 0) { "Green" } else { "Red" })

if ($testsFailed -eq 0) {
    Write-Host "`n[SUCCESS] All tests passed!" -ForegroundColor Green
    Write-Host "Document ID for verification: $documentId" -ForegroundColor Cyan
} else {
    Write-Host "`n[FAILURE] Some tests failed!" -ForegroundColor Red
    exit 1
}

# Additional Database Queries
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DETAILED DATABASE VERIFICATION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "[DB] Document Details:" -ForegroundColor Yellow
docker exec docqa-ms-postgres-1 psql -U user -d docqa_db -c "SELECT document_id, title, source_type, created_at FROM documents WHERE document_id = '$documentId';"

Write-Host "`n[DB] Document Chunks (first 3):" -ForegroundColor Yellow
docker exec docqa-ms-postgres-1 psql -U user -d docqa_db -c "SELECT chunk_id, LEFT(content, 80) as content_preview, chunk_index FROM document_chunks WHERE document_id = '$documentId' ORDER BY chunk_index LIMIT 3;"

Write-Host "`n[DB] Q&A Interactions:" -ForegroundColor Yellow
docker exec docqa-ms-postgres-1 psql -U user -d docqa_db -c "SELECT interaction_id, LEFT(question, 60) as question, confidence, created_at FROM qa_interactions WHERE document_id = '$documentId' ORDER BY created_at DESC LIMIT 3;"

Write-Host "`n[DB] Overall Statistics:" -ForegroundColor Yellow
docker exec docqa-ms-postgres-1 psql -U user -d docqa_db -c "SELECT (SELECT COUNT(*) FROM documents) as total_docs, (SELECT COUNT(*) FROM document_chunks) as total_chunks, (SELECT COUNT(*) FROM qa_interactions) as total_qa;"

Write-Host "`nTest completed successfully!" -ForegroundColor Green
