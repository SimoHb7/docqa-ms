# Deploy ML Service - Quick Setup Script
# Run this after training models on Google Colab

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  ML Service Deployment Script" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Check if models exist
Write-Host "🔍 Checking for trained models..." -ForegroundColor Yellow

$downloadsPath = "$env:USERPROFILE\Downloads"
$modelsPath = "C:\docqa-ms\backend\ml_service\saved_models"

$classifierZip = "$downloadsPath\document_classifier_model.zip"
$nerZip = "$downloadsPath\medical_ner_model.zip"

$hasClassifier = Test-Path $classifierZip
$hasNER = Test-Path $nerZip

Write-Host ""
Write-Host "Classifier model: " -NoNewline
if ($hasClassifier) {
    Write-Host "✅ Found in Downloads" -ForegroundColor Green
} else {
    Write-Host "❌ Not found" -ForegroundColor Red
    Write-Host "   Expected: $classifierZip" -ForegroundColor Gray
}

Write-Host "NER model: " -NoNewline
if ($hasNER) {
    Write-Host "✅ Found in Downloads" -ForegroundColor Green
} else {
    Write-Host "❌ Not found" -ForegroundColor Red
    Write-Host "   Expected: $nerZip" -ForegroundColor Gray
}

# Extract models if found
if ($hasClassifier -or $hasNER) {
    Write-Host "`n📦 Extracting models..." -ForegroundColor Yellow
    
    if ($hasClassifier) {
        Write-Host "Extracting document classifier..."
        Expand-Archive -Path $classifierZip -DestinationPath $modelsPath -Force
        Write-Host "✅ Classifier extracted" -ForegroundColor Green
    }
    
    if ($hasNER) {
        Write-Host "Extracting medical NER..."
        Expand-Archive -Path $nerZip -DestinationPath $modelsPath -Force
        Write-Host "✅ NER extracted" -ForegroundColor Green
    }
    
    Write-Host "`n📁 Models location: $modelsPath" -ForegroundColor Gray
    ls $modelsPath
}

# Check internet connectivity
Write-Host "`n🌐 Checking internet connectivity..." -ForegroundColor Yellow
$internetWorks = $false
try {
    $response = Test-NetConnection -ComputerName "8.8.8.8" -Port 443 -InformationLevel Quiet -WarningAction SilentlyContinue
    if ($response) {
        Write-Host "✅ Internet connection available" -ForegroundColor Green
        $internetWorks = $true
    } else {
        Write-Host "❌ No internet connection" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ No internet connection" -ForegroundColor Red
}

# Build ML service if internet works
if ($internetWorks) {
    Write-Host "`n🔨 Building ML service..." -ForegroundColor Yellow
    Write-Host "This will take 3-5 minutes..." -ForegroundColor Gray
    
    cd C:\docqa-ms
    docker compose build ml-service
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ ML service built successfully!" -ForegroundColor Green
        
        Write-Host "`n🚀 Starting ML service..." -ForegroundColor Yellow
        docker compose up -d ml-service
        
        Start-Sleep -Seconds 10
        
        Write-Host "`n📊 Checking ML service status..." -ForegroundColor Yellow
        docker compose ps ml-service
        
        Write-Host "`n🧪 Testing ML service..." -ForegroundColor Yellow
        try {
            $health = Invoke-RestMethod -Uri "http://localhost:8006/health" -ErrorAction Stop
            Write-Host "✅ ML service is healthy!" -ForegroundColor Green
            Write-Host "Status: $($health.status)" -ForegroundColor Gray
            
            Write-Host "`n🎉 SUCCESS! ML service is ready!" -ForegroundColor Green
            Write-Host "`n📖 API Documentation: http://localhost:8006/docs" -ForegroundColor Cyan
            Write-Host "💡 Try opening in browser: " -NoNewline -ForegroundColor Yellow
            Write-Host "Start-Process 'http://localhost:8006/docs'" -ForegroundColor White
        } catch {
            Write-Host "⚠️  Service is starting... Give it 30 seconds" -ForegroundColor Yellow
            Write-Host "Then test with: Invoke-RestMethod -Uri 'http://localhost:8006/health'" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ Build failed. Check logs with: docker compose logs ml-service" -ForegroundColor Red
    }
} else {
    Write-Host "`n⚠️  Cannot build without internet" -ForegroundColor Yellow
    Write-Host "   Solution: Train models on Google Colab first!" -ForegroundColor Gray
    Write-Host "   1. Go to: https://colab.research.google.com/" -ForegroundColor Gray
    Write-Host "   2. Upload: colab_notebooks\01_Document_Classifier_Training.ipynb" -ForegroundColor Gray
    Write-Host "   3. Enable GPU (Runtime → Change runtime type → T4 GPU)" -ForegroundColor Gray
    Write-Host "   4. Run all cells" -ForegroundColor Gray
    Write-Host "   5. Download the trained model" -ForegroundColor Gray
    Write-Host "   6. Run this script again" -ForegroundColor Gray
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  Next Steps" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

if (-not ($hasClassifier -and $hasNER)) {
    Write-Host "1. Train models on Google Colab" -ForegroundColor White
    Write-Host "   - Upload colab_notebooks\*.ipynb to Colab" -ForegroundColor Gray
    Write-Host "   - Enable GPU and run training" -ForegroundColor Gray
    Write-Host "   - Download trained models" -ForegroundColor Gray
    Write-Host ""
}

if ($hasClassifier -and $hasNER -and -not $internetWorks) {
    Write-Host "1. Wait for stable internet connection" -ForegroundColor White
    Write-Host "2. Run this script again to build service" -ForegroundColor White
    Write-Host ""
}

if ($internetWorks) {
    Write-Host "✅ Everything is ready!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Test commands:" -ForegroundColor White
    Write-Host @"
# Health check
Invoke-RestMethod -Uri "http://localhost:8006/health"

# Classify document
`$body = @{text = "Analyse sanguine complète"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8006/api/v1/classify" ``
    -Method POST ``
    -Body `$body ``
    -ContentType "application/json"

# Extract entities
`$body = @{text = "Patient diabétique sous Metformine"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8006/api/v1/extract-entities" ``
    -Method POST ``
    -Body `$body ``
    -ContentType "application/json"

# Open API docs
Start-Process "http://localhost:8006/docs"
"@ -ForegroundColor Gray
}

Write-Host "`n📚 Full guide: ML_TRAINING_GUIDE.md" -ForegroundColor Cyan
Write-Host "🚀 Quick start: QUICK_START_ML.md" -ForegroundColor Cyan
Write-Host ""
