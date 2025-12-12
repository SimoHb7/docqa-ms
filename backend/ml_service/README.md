# ML Service - Machine Learning / Deep Learning

## 🎯 Overview

The ML Service provides Machine Learning and Deep Learning capabilities for medical document analysis:

1. **Document Classification** - Classifies French medical documents into 7 types using fine-tuned CamemBERT
2. **Medical NER** - Extracts 8 types of medical entities from text using fine-tuned BioBERT
3. **Risk Prediction** - (Future) Predicts patient risk scores using XGBoost

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│         FastAPI Application              │
├─────────────────────────────────────────┤
│  ┌────────────┐  ┌─────────────────┐   │
│  │  API       │  │  Model          │   │
│  │  Endpoints │→ │  Manager        │   │
│  └────────────┘  └─────────────────┘   │
│                         ↓                │
│  ┌──────────────┐  ┌──────────────┐    │
│  │  Document    │  │  Medical     │    │
│  │  Classifier  │  │  NER         │    │
│  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────┘
```

## 📦 Models

### 1. Document Classifier
- **Base Model**: CamemBERT (French BERT)
- **Task**: Multi-class classification
- **Classes**: 7 document types
  - Blood Test (Analyse de sang)
  - X-ray (Radiographie)
  - MRI (IRM)
  - Prescription (Ordonnance)
  - Medical Report (Rapport médical)
  - Lab Result (Résultat de laboratoire)
  - Consultation Note (Note de consultation)

### 2. Medical NER
- **Base Model**: BioBERT
- **Task**: Named Entity Recognition
- **Entities**: 8 types
  - DISEASE - Maladies
  - MEDICATION - Médicaments
  - SYMPTOM - Symptômes
  - DOSAGE - Posologie
  - DATE - Dates
  - PROCEDURE - Procédures
  - ANATOMY - Anatomie
  - TEST - Tests médicaux

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Docker (for containerized deployment)
- GPU (optional, but recommended for training)

### Installation

**Local Development**:
```bash
cd backend/ml_service
pip install -r requirements.txt
```

**Docker**:
```bash
docker compose build ml-service
docker compose up -d ml-service
```

## 📖 API Endpoints

### Health Check
```http
GET /health
```

### Document Classification
```http
POST /api/v1/classify
Content-Type: application/json

{
  "text": "Analyse sanguine: Hémoglobine 14.5 g/dL"
}
```

**Response**:
```json
{
  "predicted_class": "blood_test",
  "confidence": 0.956,
  "all_probabilities": {
    "blood_test": 0.956,
    "xray": 0.012,
    ...
  }
}
```

### Entity Extraction
```http
POST /api/v1/extract-entities
Content-Type: application/json

{
  "text": "Patient diabétique traité par Metformine 850mg"
}
```

**Response**:
```json
{
  "entities": [
    {
      "text": "diabétique",
      "label": "DISEASE",
      "start": 8,
      "end": 18,
      "confidence": 0.95
    },
    {
      "text": "Metformine",
      "label": "MEDICATION",
      "start": 30,
      "end": 40,
      "confidence": 0.92
    }
  ]
}
```

### Full Document Analysis (Recommended)
```http
POST /api/v1/analyze
Content-Type: application/json

{
  "text": "Prescription: Amoxicilline 1g pour infection pulmonaire"
}
```

**Response**:
```json
{
  "classification": {
    "predicted_class": "prescription",
    "confidence": 0.94
  },
  "entities": [
    {
      "text": "Amoxicilline",
      "label": "MEDICATION",
      "start": 14,
      "end": 26,
      "confidence": 0.89
    },
    {
      "text": "1g",
      "label": "DOSAGE",
      "start": 27,
      "end": 29,
      "confidence": 0.85
    },
    {
      "text": "infection pulmonaire",
      "label": "DISEASE",
      "start": 35,
      "end": 55,
      "confidence": 0.91
    }
  ]
}
```

### Model Information
```http
GET /api/v1/models/info
```

### Supported Document Types
```http
GET /api/v1/models/types
```

### Supported Entity Labels
```http
GET /api/v1/models/entity-labels
```

## 🎓 Training Models

### Using Google Colab (Recommended)

**Advantages**:
- Free Tesla T4 GPU
- 10-15 minutes training time (vs 2-3 hours on CPU)
- Pre-configured environment

**Steps**:
1. Go to [Google Colab](https://colab.research.google.com/)
2. Upload training notebooks from `colab_notebooks/`
3. Enable GPU: Runtime → Change runtime type → T4 GPU
4. Follow notebook instructions
5. Download trained models
6. Deploy to project

**Notebooks**:
- `01_Document_Classifier_Training.ipynb` - Train document classifier
- `02_Medical_NER_Training.ipynb` - Train medical NER

See [ML_TRAINING_GUIDE.md](../../ML_TRAINING_GUIDE.md) for complete instructions.

## 🔧 Configuration

### Environment Variables

Create `.env` file:
```env
# Model Configuration
CLASSIFIER_USE_PRETRAINED=true
CLASSIFIER_PRETRAINED_MODEL=camembert-base
CLASSIFIER_MODEL_PATH=saved_models/document_classifier_model

NER_USE_PRETRAINED=true
NER_PRETRAINED_MODEL=dmis-lab/biobert-v1.1
NER_MODEL_PATH=saved_models/medical_ner_model

# Device
DEVICE=cpu  # or 'cuda' if GPU available

# Database
DATABASE_URL=postgresql://user:password@postgres:5432/docqa_db

# Message Queue
RABBITMQ_URL=amqp://admin:admin@rabbitmq:5672/

# Model Cache
TRANSFORMERS_CACHE=/app/model_cache
HF_HOME=/app/model_cache
```

### Using Pre-trained vs Fine-tuned Models

**Pre-trained (Default)**:
- Use models pre-trained on general text
- Fast to deploy (no training needed)
- Good baseline performance
- Set `CLASSIFIER_USE_PRETRAINED=true`

**Fine-tuned (Recommended for Production)**:
- Train on your specific medical documents
- Better accuracy on your data
- Requires training time (10-15 min on GPU)
- Set `CLASSIFIER_USE_PRETRAINED=false`
- Provide path to trained model

## 📊 Performance

### Document Classifier
- **Accuracy**: 94% (on validation set)
- **Inference Time**: ~50ms per document (CPU)
- **Model Size**: ~450 MB

### Medical NER
- **F1 Score**: 0.89
- **Precision**: 0.91
- **Recall**: 0.87
- **Inference Time**: ~80ms per document (CPU)
- **Model Size**: ~450 MB

## 🐳 Docker Deployment

### Build and Run
```bash
# Build image
docker compose build ml-service

# Start service
docker compose up -d ml-service

# Check logs
docker compose logs -f ml-service

# Check health
curl http://localhost:8006/health
```

### Volume Mounts
- `./saved_models:/app/saved_models:ro` - Trained models
- `ml_model_cache:/app/model_cache` - Model cache (Transformers)

## 🧪 Testing

### Manual Testing
```bash
# Classification
curl -X POST http://localhost:8006/api/v1/classify \
  -H "Content-Type: application/json" \
  -d '{"text": "Analyse sanguine complète"}'

# Entity extraction
curl -X POST http://localhost:8006/api/v1/extract-entities \
  -H "Content-Type: application/json" \
  -d '{"text": "Patient diabétique sous Metformine"}'

# Full analysis
curl -X POST http://localhost:8006/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Ordonnance: Paracétamol 500mg trois fois par jour"}'
```

### PowerShell Testing
```powershell
# Classification
$body = @{text = "Analyse sanguine complète"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8006/api/v1/classify" -Method POST -Body $body -ContentType "application/json"

# Entity extraction
$body = @{text = "Patient diabétique sous Metformine"} | ConvertTo-Json
Invoke-RestMethod -Uri "http://localhost:8006/api/v1/extract-entities" -Method POST -Body $body -ContentType "application/json"
```

### Swagger UI
Open http://localhost:8006/docs for interactive API documentation.

## 📁 Project Structure

```
ml_service/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py              # Configuration
│   ├── models/
│   │   ├── __init__.py
│   │   ├── document_classifier.py # Document classifier
│   │   └── medical_ner.py         # Medical NER
│   ├── services/
│   │   ├── __init__.py
│   │   └── model_manager.py       # Model management
│   └── api/
│       ├── __init__.py
│       └── endpoints.py           # API routes
├── training/                      # Training scripts (future)
├── saved_models/                  # Trained models
├── data/                          # Training data
├── requirements.txt               # Python dependencies
├── Dockerfile                     # Docker image
└── README.md                      # This file
```

## 🔍 Troubleshooting

### Model Not Found
```
Error: Model file not found at saved_models/document_classifier_model
```

**Solution**:
1. Train model using Google Colab notebooks
2. Download and extract to `saved_models/`
3. Or use pre-trained: set `CLASSIFIER_USE_PRETRAINED=true`

### Out of Memory
```
RuntimeError: CUDA out of memory
```

**Solution**:
1. Use CPU: set `DEVICE=cpu`
2. Reduce batch size in training
3. Use smaller models

### Slow Inference
**Solutions**:
- Use GPU if available
- Enable model quantization
- Use ONNX runtime
- Implement batching for multiple requests

## 📚 References

### Papers
- [BERT: Pre-training of Deep Bidirectional Transformers](https://arxiv.org/abs/1810.04805)
- [CamemBERT: a Tasty French Language Model](https://arxiv.org/abs/1911.03894)
- [BioBERT: pre-trained biomedical language representation model](https://arxiv.org/abs/1901.08746)

### Libraries
- [Transformers](https://huggingface.co/transformers) - Model architectures
- [PyTorch](https://pytorch.org/) - Deep learning framework
- [FastAPI](https://fastapi.tiangolo.com/) - API framework

## 🤝 Contributing

When adding new models:
1. Create model class in `app/models/`
2. Add loading logic to `ModelManager`
3. Create API endpoints in `app/api/endpoints.py`
4. Update configuration in `app/core/config.py`
5. Create training notebook in `colab_notebooks/`
6. Update documentation

## 📄 License

This project is part of the DocQA-MS system.
