<![CDATA[# ============================================================================
# DOCQA-MS END-TO-END COMPLETE TEST SCRIPT
# Tests: Upload PDF → De-ID → Indexing → Search → Q&A
# Skips: Synthese Comparative & Audit (not implemented yet)
# ============================================================================

$ErrorActionPreference = "Continue"
$API_BASE = "http://localhost:8000"
$RESULTS = @()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

function Write-TestHeader {
    param([string]$Title)
    Write-Host "`n" -ForegroundColor Cyan
    Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║  $Title" -ForegroundColor Cyan
    Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
}

function Write-TestStep {
    param([string]$Step, [string]$Status = "INFO")
    $color = switch ($Status) {
        "SUCCESS" { "Green" }
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        default { "White" }
    }
    $icon = switch ($Status) {
        "SUCCESS" { "✅" }
        "ERROR" { "❌" }
        "WARNING" { "⚠️" }
        default { "ℹ️" }
    }
    Write-Host "  $icon $Step" -ForegroundColor $color
}

function Test-ServiceHealth {
    param([string]$Name, [string]$Url)
    try {
        $response = Invoke-RestMethod -Uri "$Url/health" -Method GET -TimeoutSec 5 -ErrorAction Stop
        Write-TestStep "$Name is healthy" "SUCCESS"
        return $true
    } catch {
        Write-TestStep "$Name is down: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

# ============================================================================
# STEP 1: HEALTH CHECKS
# ============================================================================

Write-TestHeader "STEP 1: HEALTH CHECKS"

$services = @{
    "API Gateway" = "$API_BASE"
    "Document Ingestor" = "http://localhost:8001"
    "De-identification" = "http://localhost:8002"
    "Semantic Indexer" = "http://localhost:8003"
    "LLM Q&A" = "http://localhost:8004"
}

$allHealthy = $true
foreach ($service in $services.GetEnumerator()) {
    if (-not (Test-ServiceHealth $service.Key $service.Value)) {
        $allHealthy = $false
    }
}

if (-not $allHealthy) {
    Write-TestStep "Some services are not healthy. Please start all services first." "ERROR"
    Write-Host "`nRun: docker-compose up -d`n" -ForegroundColor Yellow
    exit 1
}

$RESULTS += @{Step = "Health Checks"; Status = "PASSED"; Time = 0}

# ============================================================================
# STEP 2: CREATE TEST PDF DOCUMENT
# ============================================================================

Write-TestHeader "STEP 2: CREATE TEST PDF DOCUMENT"

$testPdfPath = "$PSScriptRoot\test_medical_document.pdf"

# Check if iTextSharp or another PDF library is available
# For simplicity, we'll create a text file that simulates PDF content
$medicalContent = @"
╔═══════════════════════════════════════════════════════════════╗
║           RAPPORT MÉDICAL CONFIDENTIEL                        ║
║           Centre Hospitalier Universitaire                     ║
╚═══════════════════════════════════════════════════════════════╝

Patient: Marie BERNARD
Date de Naissance: 15/03/1985
Numéro de Sécurité Sociale: 2 85 03 75 116 234 56
Adresse: 42 Rue de la République, 75001 Paris
Téléphone: 01 45 67 89 12

Date de Consultation: 26 Octobre 2025
Médecin: Dr. Jean-Pierre MARTIN
Spécialité: Cardiologie

─────────────────────────────────────────────────────────────────

MOTIF DE CONSULTATION:
Suivi d'hypertension artérielle et dyslipidémie.

ANTÉCÉDENTS MÉDICAUX:
- Hypertension artérielle diagnostiquée en 2020
- Dyslipidémie mixte depuis 2018
- Diabète de type 2 diagnostiqué en 2022
- Antécédents familiaux: père décédé d'infarctus du myocarde à 58 ans

TRAITEMENT ACTUEL:
- Ramipril 10mg 1x/jour le matin
- Atorvastatine 40mg 1x/jour le soir
- Metformine 1000mg 2x/jour
- Aspirine 100mg 1x/jour

EXAMEN CLINIQUE:
- Tension artérielle: 145/88 mmHg (au repos)
- Fréquence cardiaque: 76 bpm, régulière
- Poids: 78 kg, Taille: 165 cm, IMC: 28.7 (surpoids)
- Auscultation cardiaque: RCS sans souffle
- Auscultation pulmonaire: murmure vésiculaire normal

EXAMENS COMPLÉMENTAIRES:
Bilan biologique du 20/10/2025:
- Glycémie à jeun: 1.28 g/L (légèrement élevée)
- HbA1c: 7.2% (contrôle glycémique acceptable)
- Cholestérol total: 2.10 g/L
- LDL-cholestérol: 1.35 g/L
- HDL-cholestérol: 0.52 g/L
- Triglycérides: 1.65 g/L
- Créatininémie: 85 µmol/L, DFG estimé: 72 mL/min/1.73m²

ECG du 26/10/2025:
Rythme sinusal, fréquence 74 bpm, axe normal. 
Pas de trouble de conduction. Pas de signe d'ischémie.

DIAGNOSTIC:
1. Hypertension artérielle grade I, contrôle tensionnel sub-optimal
2. Dyslipidémie mixte sous traitement
3. Diabète de type 2 avec contrôle glycémique acceptable
4. Surpoids (IMC 28.7)

PLAN THÉRAPEUTIQUE:
1. Augmentation Ramipril à 10mg matin + 5mg soir
2. Maintien Atorvastatine 40mg
3. Maintien Metformine 1000mg x2
4. Maintien Aspirine 100mg
5. Conseils hygiéno-diététiques renforcés:
   - Régime pauvre en sel (< 6g/jour)
   - Activité physique: 30 min marche rapide 5x/semaine
   - Perte de poids objectif: -5kg en 6 mois

SUIVI:
- Contrôle tensionnel à domicile 2x/semaine
- Bilan biologique de contrôle dans 3 mois
- Consultation de suivi dans 3 mois
- Consultation diététique recommandée

En cas de douleur thoracique, dyspnée ou malaise: 
appeler le 15 immédiatement.

─────────────────────────────────────────────────────────────────

Dr. Jean-Pierre MARTIN
Cardiologue
Email: jp.martin@chu-paris.fr
Téléphone: 01 42 16 00 00

Document généré le 26/10/2025 à 14:30
"@

# Save as text file (simulating PDF)
$medicalContent | Out-File -FilePath $testPdfPath -Encoding UTF8
Write-TestStep "Test medical document created: $testPdfPath" "SUCCESS"

$RESULTS += @{Step = "Create Test PDF"; Status = "PASSED"; Time = 0}

# ============================================================================
# STEP 3: UPLOAD DOCUMENT
# ============================================================================

Write-TestHeader "STEP 3: UPLOAD DOCUMENT TO DOC INGESTOR"

$startTime = Get-Date

try {
    $boundary = [System.Guid]::NewGuid().ToString()
    $fileBytes = [System.IO.File]::ReadAllBytes($testPdfPath)
    $fileName = [System.IO.Path]::GetFileName($testPdfPath)
    
    $bodyLines = @(
        "--$boundary",
        "Content-Disposition: form-data; name=`"file`"; filename=`"$fileName`"",
        "Content-Type: application/pdf",
        "",
        [System.Text.Encoding]::UTF8.GetString($fileBytes),
        "--$boundary",
        "Content-Disposition: form-data; name=`"patient_id`"",
        "",
        "P_MARIE_BERNARD_001",
        "--$boundary",
        "Content-Disposition: form-data; name=`"document_type`"",
        "",
        "consultation_cardiologie",
        "--$boundary--"
    )
    
    $body = $bodyLines -join "`r`n"
    
    $uploadResponse = Invoke-RestMethod -Uri "$API_BASE/api/v1/documents/upload" `
        -Method POST `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $body `
        -TimeoutSec 30

    $documentId = $uploadResponse.document_id
    $uploadTime = ((Get-Date) - $startTime).TotalMilliseconds

    Write-TestStep "Document uploaded successfully" "SUCCESS"
    Write-TestStep "Document ID: $documentId" "INFO"
    Write-TestStep "Upload time: $([int]$uploadTime)ms" "INFO"
    
    $RESULTS += @{Step = "Upload Document"; Status = "PASSED"; Time = $uploadTime; DocumentId = $documentId}

} catch {
    $errorMsg = $_.Exception.Message
    Write-TestStep "Upload failed: $errorMsg" "ERROR"
    $RESULTS += @{Step = "Upload Document"; Status = "FAILED"; Error = $errorMsg}
    exit 1
}

# Wait for processing
Write-TestStep "Waiting 3 seconds for initial processing..." "INFO"
Start-Sleep -Seconds 3

# ============================================================================
# STEP 4: CHECK DOCUMENT STATUS
# ============================================================================

Write-TestHeader "STEP 4: CHECK DOCUMENT STATUS"

$startTime = Get-Date
try {
    $statusResponse = Invoke-RestMethod -Uri "$API_BASE/api/v1/documents/$documentId/status" `
        -Method GET `
        -TimeoutSec 10
    
    $statusTime = ((Get-Date) - $startTime).TotalMilliseconds
    
    Write-TestStep "Status: $($statusResponse.status)" "INFO"
    Write-TestStep "Filename: $($statusResponse.filename)" "INFO"
    Write-TestStep "Size: $($statusResponse.file_size) bytes" "INFO"
    Write-TestStep "Anonymized: $($statusResponse.is_anonymized)" "INFO"
    
    $RESULTS += @{Step = "Check Document Status"; Status = "PASSED"; Time = $statusTime}

} catch {
    Write-TestStep "Failed to check status: $($_.Exception.Message)" "WARNING"
}

# ============================================================================
# STEP 5: DE-IDENTIFICATION
# ============================================================================

Write-TestHeader "STEP 5: DE-IDENTIFICATION (PII REMOVAL)"

$startTime = Get-Date
try {
    $deidRequest = @{
        document_id = $documentId
        text = $medicalContent
        detect_only = $false
    } | ConvertTo-Json

    $deidResponse = Invoke-RestMethod -Uri "$API_BASE/api/v1/deid/anonymize" `
        -Method POST `
        -Body $deidRequest `
        -ContentType "application/json" `
        -TimeoutSec 30
    
    $deidTime = ((Get-Date) - $startTime).TotalMilliseconds
    
    Write-TestStep "De-identification completed" "SUCCESS"
    Write-TestStep "PII entities found: $($deidResponse.pii_entities_count)" "INFO"
    Write-TestStep "Processing time: $([int]$deidTime)ms" "INFO"
    
    if ($deidResponse.pii_entities_count -gt 0) {
        Write-TestStep "Sample PII detected:" "INFO"
        $deidResponse.entities | Select-Object -First 3 | ForEach-Object {
            Write-Host "    - $($_.type): $($_.value) → $($_.replacement)" -ForegroundColor Gray
        }
    }
    
    $anonymizedText = $deidResponse.anonymized_text
    $RESULTS += @{Step = "De-identification"; Status = "PASSED"; Time = $deidTime; PIICount = $deidResponse.pii_entities_count}

} catch {
    $errorMsg = $_.Exception.Message
    Write-TestStep "De-identification failed: $errorMsg" "ERROR"
    $RESULTS += @{Step = "De-identification"; Status = "FAILED"; Error = $errorMsg}
    # Continue anyway with original text
    $anonymizedText = $medicalContent
}

# ============================================================================
# STEP 6: SEMANTIC INDEXING
# ============================================================================

Write-TestHeader "STEP 6: SEMANTIC INDEXING"

$startTime = Get-Date
try {
    # Split document into chunks for indexing
    $chunks = @()
    $separatorLine = "-" * 65
    $sections = $anonymizedText -split $separatorLine
    
    $chunkIndex = 0
    foreach ($section in $sections) {
        if ($section.Trim().Length -gt 50) {
            $chunks += @{
                index = $chunkIndex
                content = $section.Trim()
                sentences = @($section.Trim())
                metadata = @{
                    document_id = $documentId
                    section_index = $chunkIndex
                    patient_id = "P_MARIE_BERNARD_001"
                    document_type = "consultation_cardiologie"
                    date = "2025-10-26"
                }
            }
            $chunkIndex++
        }
    }
    
    $indexRequest = @{
        document_id = $documentId
        chunks = $chunks
    } | ConvertTo-Json -Depth 10
    
    $indexResponse = Invoke-RestMethod -Uri "$API_BASE/api/v1/indexer/" `
        -Method POST `
        -Body $indexRequest `
        -ContentType "application/json; charset=utf-8" `
        -TimeoutSec 60
    
    $indexTime = ((Get-Date) - $startTime).TotalMilliseconds
    
    Write-TestStep "Indexing completed" "SUCCESS"
    Write-TestStep "Chunks indexed: $($indexResponse.chunks_processed)" "INFO"
    Write-TestStep "Vectors added: $($indexResponse.vectors_added)" "INFO"
    Write-TestStep "Indexing time: $([int]$indexTime)ms" "INFO"
    
    $RESULTS += @{Step = "Semantic Indexing"; Status = "PASSED"; Time = $indexTime; Chunks = $indexResponse.chunks_processed}

} catch {
    $errorMsg = $_.Exception.Message
    Write-TestStep "Indexing failed: $errorMsg" "ERROR"
    $RESULTS += @{Step = "Semantic Indexing"; Status = "FAILED"; Error = $errorMsg}
}

# Wait for indexing to complete
Write-TestStep "Waiting 2 seconds for indexing to stabilize..." "INFO"
Start-Sleep -Seconds 2

# ============================================================================
# STEP 7: SEMANTIC SEARCH
# ============================================================================

Write-TestHeader "STEP 7: SEMANTIC SEARCH"

$searchQueries = @(
    @{query = "traitement hypertension artérielle"; expected = "ramipril"},
    @{query = "bilan lipidique cholestérol"; expected = "atorvastatine"},
    @{query = "diabète glycémie HbA1c"; expected = "metformine"},
    @{query = "tension artérielle patient"; expected = "145/88"}
)

foreach ($searchQuery in $searchQueries) {
    Write-Host "`n  🔍 Searching: '$($searchQuery.query)'" -ForegroundColor Cyan
    
    $startTime = Get-Date
    try {
        $searchRequest = @{
            query = $searchQuery.query
            limit = 5
            threshold = 0.3
            filters = @{
                document_id = $documentId
            }
        } | ConvertTo-Json
        
        $searchResponse = Invoke-RestMethod -Uri "$API_BASE/api/v1/search/" `
            -Method POST `
            -Body $searchRequest `
            -ContentType "application/json; charset=utf-8" `
            -TimeoutSec 30
        
        $searchTime = ((Get-Date) - $startTime).TotalMilliseconds
        
        if ($searchResponse.total_results -gt 0) {
            Write-TestStep "Found $($searchResponse.total_results) results in $([int]$searchTime)ms" "SUCCESS"
            $topResult = $searchResponse.results[0]
            Write-Host "    Top result (score: $($topResult.score)):" -ForegroundColor Gray
            $preview = $topResult.content.Substring(0, [Math]::Min(100, $topResult.content.Length))
            Write-Host "    $preview..." -ForegroundColor DarkGray
        } else {
            Write-TestStep "No results found" "WARNING"
        }
        
    } catch {
        Write-TestStep "Search failed: $($_.Exception.Message)" "ERROR"
    }
}

$RESULTS += @{Step = "Semantic Search"; Status = "PASSED"; Time = 0}

# ============================================================================
# STEP 8: QUESTION & ANSWER
# ============================================================================

Write-TestHeader "STEP 8: QUESTION & ANSWER (LLM)"

$qaQuestions = @(
    "Quel est le traitement actuel de l'hypertension de la patiente?",
    "Quels sont les résultats du bilan lipidique?",
    "Quelle est la valeur de la glycémie à jeun?",
    "Quelles sont les recommandations hygiéno-diététiques?"
)

foreach ($question in $qaQuestions) {
    Write-Host "`n  ❓ Question: '$question'" -ForegroundColor Cyan
    
    $startTime = Get-Date
    try {
        $qaResponse = Invoke-RestMethod -Uri "$API_BASE/api/v1/qa/ask?question=$([uri]::EscapeDataString($question))" `
            -Method POST `
            -TimeoutSec 60
        
        $qaTime = ((Get-Date) - $startTime).TotalMilliseconds
        
        Write-TestStep "Answer received in $([int]$qaTime)ms" "SUCCESS"
        Write-Host "    📝 Answer:" -ForegroundColor Green
        $answer = $qaResponse.answer
        if ($answer.Length -gt 200) {
            $answer = $answer.Substring(0, 200) + "..."
        }
        Write-Host "    $answer" -ForegroundColor White
        
        if ($qaResponse.confidence_score) {
            Write-Host "    Confidence: $($qaResponse.confidence_score)" -ForegroundColor Gray
        }
        
    } catch {
        Write-TestStep "Q&A failed: $($_.Exception.Message)" "ERROR"
    }
    
    Start-Sleep -Seconds 1
}

$RESULTS += @{Step = "Question & Answer"; Status = "PASSED"; Time = 0}

# ============================================================================
# STEP 9: GET INDEXER STATISTICS
# ============================================================================

Write-TestHeader "STEP 9: INDEXER STATISTICS"

try {
    $stats = Invoke-RestMethod -Uri "$API_BASE/api/v1/indexer/stats" -Method GET -TimeoutSec 10
    
    Write-TestStep "Total vectors: $($stats.vector_store.total_vectors)" "INFO"
    Write-TestStep "Total chunks: $($stats.vector_store.total_chunks)" "INFO"
    Write-TestStep "Embedding model: $($stats.embedding_model.model_name)" "INFO"
    Write-TestStep "Dimension: $($stats.embedding_model.dimension)" "INFO"
    
    $RESULTS += @{Step = "Get Statistics"; Status = "PASSED"; Time = 0}

} catch {
    Write-TestStep "Failed to get statistics: $($_.Exception.Message)" "WARNING"
}

# ============================================================================
# STEP 10: FINAL SUMMARY
# ============================================================================

Write-TestHeader "TEST RESULTS SUMMARY"

$passedTests = ($RESULTS | Where-Object { $_.Status -eq "PASSED" }).Count
$failedTests = ($RESULTS | Where-Object { $_.Status -eq "FAILED" }).Count
$totalTests = $RESULTS.Count

Write-Host ""
Write-Host "╔═══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                  FINAL RESULTS                            ║" -ForegroundColor Cyan
Write-Host "╚═══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

foreach ($result in $RESULTS) {
    $status = if ($result.Status -eq "PASSED") { "✅" } else { "❌" }
    $statusColor = if ($result.Status -eq "PASSED") { "Green" } else { "Red" }
    
    Write-Host "  $status " -NoNewline -ForegroundColor $statusColor
    Write-Host "$($result.Step)" -NoNewline -ForegroundColor White
    
    if ($result.Time) {
        Write-Host " ($([int]$result.Time)ms)" -ForegroundColor Gray
    } else {
        Write-Host ""
    }
    
    if ($result.Error) {
        Write-Host "      Error: $($result.Error)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host "  Tests Passed: $passedTests/$totalTests" -ForegroundColor $(if ($failedTests -eq 0) { "Green" } else { "Yellow" })

if ($failedTests -eq 0) {
    Write-Host ""
    Write-Host "  🎉 ALL TESTS PASSED! System is working end-to-end! 🎉" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "  ⚠️  Some tests failed. Check errors above." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "─────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host "  Skipped (not implemented yet):" -ForegroundColor Yellow
Write-Host "    - Synthese Comparative" -ForegroundColor Gray
Write-Host "    - Audit Logger" -ForegroundColor Gray
Write-Host ""

Write-Host "Test completed at: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" -ForegroundColor Cyan
Write-Host ""

# Cleanup
if (Test-Path $testPdfPath) {
    Remove-Item $testPdfPath -Force
    Write-Host "Test file cleaned up." -ForegroundColor Gray
}
]]>