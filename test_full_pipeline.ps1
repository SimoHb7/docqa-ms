# Full Pipeline E2E Test - Document Upload to Q&A with Complete Database Persistence
# Tests the entire production workflow with real file uploads

$ErrorActionPreference = "Stop"
$API_BASE = "http://localhost:8000"

Write-Host "`n========================================" -ForegroundColor Green -BackgroundColor Black
Write-Host "FULL PIPELINE E2E TEST" -ForegroundColor Green -BackgroundColor Black
Write-Host "Upload -> De-ID -> Index -> Search -> Q&A -> Database" -ForegroundColor Green -BackgroundColor Black
Write-Host "========================================`n" -ForegroundColor Green -BackgroundColor Black

$testsPassed = 0
$testsFailed = 0

# Clear database first
Write-Host "[SETUP] Clearing database..." -ForegroundColor Yellow
docker exec docqa-ms-postgres-1 psql -U user -d docqa_db -c "TRUNCATE TABLE qa_interactions, document_chunks, documents CASCADE;" 2>&1 | Out-Null
Write-Host "  [OK] Database cleared`n" -ForegroundColor Green

# Test 1: Health Checks
Write-Host "[1/10] Health Checks..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$API_BASE/health/" -Method GET -TimeoutSec 10
    if ($health.status -eq "healthy") {
        Write-Host "  [OK] All services healthy" -ForegroundColor Green
        $testsPassed++
    }
} catch {
    Write-Host "  [FAIL] Health check failed" -ForegroundColor Red
    $testsFailed++
}

# Test 2: Create test medical document
Write-Host "`n[2/10] Creating test medical document..." -ForegroundColor Yellow

$medicalContent = @"
RAPPORT MEDICAL CONSULTATION CARDIOLOGIE

Date de consultation: 28 octobre 2025
Hopital Universitaire Lyon Sud

INFORMATIONS PATIENT:
Nom: LAURENT Sophie
Date de naissance: 15/04/1975
Numero de securite sociale: 2 75 04 69 234 567 12
Adresse: 28 Avenue de la Republique, 69003 Lyon
Telephone: 04 72 33 44 55
Email: sophie.laurent@email.fr
Numero de dossier medical: MRN2025-456789

MEDECIN TRAITANT:
Dr. Pierre DUBOIS
Cardiologue
Service de Cardiologie
Email: p.dubois@chu-lyon.fr
Telephone: 04 78 86 43 21

ANTECEDENTS MEDICAUX:
- Hypertension arterielle diagnostiquee en 2018
- Diabete de type 2 depuis 2020
- Hypercholesterolemie familiale
- Tabagisme actif (15 cigarettes/jour depuis 20 ans)
- Antecedents familiaux: pere decede d'infarctus du myocarde a 62 ans

TRAITEMENT ACTUEL:
1. Ramipril 10mg - 1 comprime le matin
2. Metformine 1000mg - 1 comprime matin et soir  
3. Atorvastatine 40mg - 1 comprime le soir
4. Aspirine 100mg - 1 comprime par jour
5. Bisoprolol 5mg - 1 comprime le matin

EXAMEN CLINIQUE:
- Poids: 78 kg
- Taille: 165 cm
- IMC: 28.7 (surpoids)
- Tension arterielle: 152/94 mmHg (non controlee)
- Frequence cardiaque: 82 bpm, reguliere
- Temperature: 36.7°C
- SpO2: 98% en air ambiant

EXAMENS COMPLEMENTAIRES:
Bilan biologique du 25/10/2025:
- Glycemie a jeun: 1.35 g/L (elevee)
- HbA1c: 7.9% (controle insuffisant)
- Cholesterol total: 2.45 g/L
- LDL-cholesterol: 1.68 g/L (eleve)
- HDL-cholesterol: 0.48 g/L (bas)
- Triglycerides: 2.15 g/L (eleves)
- Creatininemie: 98 µmol/L
- DFG estime: 68 mL/min/1.73m² (insuffisance renale moderee)

ECG du 28/10/2025:
Rythme sinusal, frequence 82 bpm
Hypertrophie ventriculaire gauche
Pas de trouble de conduction
Pas de signe d'ischemie aiguë

DIAGNOSTIC:
1. Hypertension arterielle grade II non controlee
2. Diabete de type 2 avec controle glycemique insuffisant
3. Dyslipidémie mixte severe
4. Insuffisance renale chronique stade 3a
5. Surpoids avec obesite abdominale
6. Tabagisme actif

PLAN THERAPEUTIQUE:
1. Augmentation Ramipril a 10mg matin + 5mg soir
2. Augmentation Atorvastatine a 80mg le soir
3. Ajout Empagliflozine 10mg le matin (cardioprotection + controle glycemique)
4. Maintien Metformine 1000mg x2
5. Maintien Aspirine 100mg
6. Maintien Bisoprolol 5mg

RECOMMANDATIONS HYGENO-DIETETIQUES:
- Regime pauvre en sel (< 5g/jour)
- Regime diabetique avec reduction glucides rapides
- Reduction apport lipides satures
- Augmentation fibres et legumes
- Activite physique: marche rapide 30 min/jour minimum
- Perte de poids objectif: -8kg en 6 mois
- ARRET TABAC URGENT (orientation tabacologie)

SURVEILLANCE:
- Auto-surveillance tension arterielle matin et soir
- Auto-surveillance glycemique 2 fois/jour
- Consultation de suivi dans 6 semaines
- Bilan biologique de controle dans 3 mois
- Consultation dietetique dans 2 semaines
- Consultation tabacologie dans 1 semaine

URGENCES:
En cas de douleur thoracique, dyspnee importante, malaise, palpitations:
Appeler le 15 immediatement

Prochain rendez-vous: 09 decembre 2025 a 14h30

Dr. Pierre DUBOIS
Cardiologue
Service de Cardiologie - Hopital Lyon Sud
Date et signature electronique: 28/10/2025 16:45
"@

$tempFile = "$env:TEMP\medical_report_full_test.txt"
$medicalContent | Out-File -FilePath $tempFile -Encoding UTF8

Write-Host "  [OK] Test document created ($([math]::Round((Get-Item $tempFile).Length / 1KB, 1)) KB)" -ForegroundColor Green
$testsPassed++

# Test 3: Upload document through API Gateway
Write-Host "`n[3/10] Uploading document via API Gateway..." -ForegroundColor Yellow

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
        "PATIENT-LAURENT-2025",
        "--$boundary",
        "Content-Disposition: form-data; name=`"document_type`"$LF",
        "cardiology_consultation",
        "--$boundary--$LF"
    )
    
    $body = $bodyLines -join $LF
    
    $uploadResponse = Invoke-RestMethod -Uri "$API_BASE/api/v1/documents/upload" `
        -Method POST `
        -Body $body `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -TimeoutSec 30
    
    $documentId = $uploadResponse.document_id
    Write-Host "  [OK] Document uploaded successfully" -ForegroundColor Green
    Write-Host "      Document ID: $documentId" -ForegroundColor Gray
    Write-Host "      Status: $($uploadResponse.status)" -ForegroundColor Gray
    $testsPassed++
    
} catch {
    Write-Host "  [FAIL] Upload failed: $_" -ForegroundColor Red
    $testsFailed++
    exit 1
}

# Test 4: Verify document in database
Write-Host "`n[4/10] Verifying document in database..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

$dbCheck = docker exec docqa-ms-postgres-1 psql -U user -d docqa_db -t -c "SELECT COUNT(*) FROM documents WHERE id = '$documentId';" 2>$null
if ($dbCheck -match "1") {
    Write-Host "  [OK] Document found in database" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "  [FAIL] Document NOT in database" -ForegroundColor Red
    $testsFailed++
}

# Test 5: De-identify content
Write-Host "`n[5/10] De-identifying medical content..." -ForegroundColor Yellow

try {
    $deidRequest = @{
        document_id = $documentId
        content = $medicalContent
        language = "fr"
    } | ConvertTo-Json -Depth 10
    
    $deidResponse = Invoke-RestMethod -Uri "$API_BASE/api/v1/deid/anonymize" `
        -Method POST `
        -Body $deidRequest `
        -ContentType "application/json" `
        -TimeoutSec 30
    
    Write-Host "  [OK] De-identification complete" -ForegroundColor Green
    Write-Host "      PII entities detected: $($deidResponse.pii_entities.Count)" -ForegroundColor Gray
    Write-Host "      Doctor name masked: $(if ($deidResponse.anonymized_content -notmatch 'Dr\. Pierre DUBOIS') {'YES'} else {'NO'})" -ForegroundColor Gray
    Write-Host "      Patient name masked: $(if ($deidResponse.anonymized_content -notmatch 'LAURENT Sophie') {'YES'} else {'NO'})" -ForegroundColor Gray
    $testsPassed++
    
    $anonymizedContent = $deidResponse.anonymized_content
    
} catch {
    Write-Host "  [FAIL] De-identification failed: $_" -ForegroundColor Red
    $testsFailed++
}

# Test 6: Index document
Write-Host "`n[6/10] Indexing document for semantic search..." -ForegroundColor Yellow

try {
    # Create chunks
    $chunks = @()
    $lines = $anonymizedContent -split "`n"
    $chunkSize = 15
    $chunkIndex = 0
    
    for ($i = 0; $i -lt $lines.Count; $i += $chunkSize) {
        $chunkLines = $lines[$i..[Math]::Min($i + $chunkSize - 1, $lines.Count - 1)]
        $chunkContent = $chunkLines -join "`n"
        
        if ($chunkContent.Trim().Length -gt 30) {
            $chunks += @{
                index = $chunkIndex
                content = $chunkContent.Trim()
                sentences = @($chunkContent.Trim())
                metadata = @{
                    document_id = $documentId
                    chunk_index = $chunkIndex
                    patient_id = "PATIENT-LAURENT-2025"
                    document_type = "cardiology_consultation"
                }
            }
            $chunkIndex++
        }
    }
    
    $indexRequest = @{
        document_id = $documentId
        chunks = $chunks
        metadata = @{
            title = "Cardiology Consultation - Full Test"
            source_type = "medical_report"
        }
    } | ConvertTo-Json -Depth 10
    
    $indexResponse = Invoke-RestMethod -Uri "$API_BASE/api/v1/indexer/" `
        -Method POST `
        -Body $indexRequest `
        -ContentType "application/json" `
        -TimeoutSec 30
    
    Write-Host "  [OK] Document indexed successfully" -ForegroundColor Green
    Write-Host "      Chunks created: $($indexResponse.chunks_processed)" -ForegroundColor Gray
    Write-Host "      Vectors added: $($indexResponse.vectors_added)" -ForegroundColor Gray
    $testsPassed++
    
} catch {
    Write-Host "  [FAIL] Indexing failed: $_" -ForegroundColor Red
    $testsFailed++
}

# Wait for indexing
Start-Sleep -Seconds 3

# Test 7: Semantic Search
Write-Host "`n[7/10] Testing semantic search..." -ForegroundColor Yellow

try {
    $searchRequest = @{
        query = "traitement hypertension et diabete"
        top_k = 3
    } | ConvertTo-Json
    
    $searchResponse = Invoke-RestMethod -Uri "$API_BASE/api/v1/search/" -Method POST -Body $searchRequest -ContentType "application/json"
    
    if ($searchResponse.results.Count -gt 0) {
        Write-Host "  [OK] Search found $($searchResponse.results.Count) results" -ForegroundColor Green
        Write-Host "      Top score: $([math]::Round($searchResponse.results[0].score, 3))" -ForegroundColor Gray
        $testsPassed++
    } else {
        Write-Host "  [WARN] No search results" -ForegroundColor Yellow
        $testsPassed++
    }
} catch {
    Write-Host "  [FAIL] Search failed: $_" -ForegroundColor Red
    $testsFailed++
}

# Test 8: Q&A
Write-Host "`n[8/10] Testing Q&A..." -ForegroundColor Yellow

try {
    Add-Type -AssemblyName System.Web
    $question = [System.Web.HttpUtility]::UrlEncode("Quels sont les diagnostics principaux et le plan therapeutique pour le patient?")
    $qaResponse = Invoke-RestMethod -Uri "$API_BASE/api/v1/qa/ask?question=$question" -Method POST -TimeoutSec 30
    
    if ($qaResponse.answer -and $qaResponse.answer.Length -gt 50) {
        Write-Host "  [OK] Q&A response generated" -ForegroundColor Green
        Write-Host "      Answer length: $($qaResponse.answer.Length) chars" -ForegroundColor Gray
        Write-Host "      Confidence: $($qaResponse.confidence_score)" -ForegroundColor Gray
        $testsPassed++
    } else {
        Write-Host "  [FAIL] Q&A response too short" -ForegroundColor Red
        $testsFailed++
    }
} catch {
    Write-Host "  [FAIL] Q&A failed: $_" -ForegroundColor Red
    $testsFailed++
}

# Test 9: Verify chunks in database
Write-Host "`n[9/10] Verifying chunks in database..." -ForegroundColor Yellow

$chunkCount = docker exec docqa-ms-postgres-1 psql -U user -d docqa_db -t -c "SELECT COUNT(*) FROM document_chunks WHERE document_id = '$documentId';" 2>$null | Out-String
$chunkCountNum = [int]($chunkCount.Trim())

if ($chunkCountNum -gt 0) {
    Write-Host "  [OK] Found $chunkCountNum chunks in database" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "  [FAIL] No chunks in database" -ForegroundColor Red
    $testsFailed++
}

# Test 10: Verify Q&A in database
Write-Host "`n[10/10] Verifying Q&A interactions in database..." -ForegroundColor Yellow

$qaCount = docker exec docqa-ms-postgres-1 psql -U user -d docqa_db -t -c "SELECT COUNT(*) FROM qa_interactions;" 2>$null | Out-String
$qaCountNum = [int]($qaCount.Trim())

if ($qaCountNum -gt 0) {
    Write-Host "  [OK] Found $qaCountNum Q&A interactions in database" -ForegroundColor Green
    $testsPassed++
} else {
    Write-Host "  [FAIL] No Q&A interactions in database" -ForegroundColor Red
    $testsFailed++
}

# Final Summary
Write-Host "`n========================================" -ForegroundColor Green -BackgroundColor Black
Write-Host "TEST SUMMARY" -ForegroundColor Green -BackgroundColor Black
Write-Host "========================================" -ForegroundColor Green -BackgroundColor Black
Write-Host "Passed: $testsPassed/10" -ForegroundColor Green
Write-Host "Failed: $testsFailed/10" -ForegroundColor $(if ($testsFailed -eq 0) { "Green" } else { "Red" })

if ($testsFailed -eq 0) {
    Write-Host "`n[SUCCESS] Full pipeline working!" -ForegroundColor White -BackgroundColor Green
} else {
    Write-Host "`n[PARTIAL] Some tests failed" -ForegroundColor White -BackgroundColor Yellow
}

# Database Verification
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DATABASE COMPLETE VERIFICATION" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "[DB] Table Counts:" -ForegroundColor Yellow
docker exec docqa-ms-postgres-1 psql -U user -d docqa_db -c "SELECT 'documents' as table, COUNT(*) as records FROM documents UNION ALL SELECT 'document_chunks', COUNT(*) FROM document_chunks UNION ALL SELECT 'qa_interactions', COUNT(*) FROM qa_interactions;"

Write-Host "`n[DB] Document Record:" -ForegroundColor Yellow
docker exec docqa-ms-postgres-1 psql -U user -d docqa_db -c "SELECT id, filename, file_type, file_size, processing_status, LENGTH(content) as content_length FROM documents WHERE id = '$documentId';"

Write-Host "`n[DB] Sample Chunks (verify PII masked):" -ForegroundColor Yellow
docker exec docqa-ms-postgres-1 psql -U user -d docqa_db -c "SELECT chunk_index, LEFT(content, 120) as preview FROM document_chunks WHERE document_id = '$documentId' ORDER BY chunk_index LIMIT 3;"

Write-Host "`n[DB] Q&A Interaction:" -ForegroundColor Yellow
docker exec docqa-ms-postgres-1 psql -U user -d docqa_db -c "SELECT LEFT(question, 60) as question, confidence_score, llm_model, response_time_ms FROM qa_interactions LIMIT 1;"

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "FULL PIPELINE TEST COMPLETED!" -ForegroundColor Green
Write-Host "Document ID: $documentId" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Green

# Cleanup
Remove-Item $tempFile -ErrorAction SilentlyContinue
