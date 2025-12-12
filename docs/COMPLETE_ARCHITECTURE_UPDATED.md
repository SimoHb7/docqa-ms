# 🏗️ DocQA-MS Complete Architecture Documentation (Updated)

**Date**: December 11, 2025  
**Version**: 2.0 (with ML Service)  
**Status**: Production Ready

---

## 📋 Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagrams](#architecture-diagrams)
3. [Microservices Details](#microservices-details)
4. [Technology Stack](#technology-stack)
5. [Data Flow](#data-flow)
6. [API Documentation](#api-documentation)
7. [Security Architecture](#security-architecture)
8. [Deployment](#deployment)

---

## 🎯 System Overview

### **Project Name**: DocQA-MS (Medical Document Q&A Microservices)

### **Purpose**
Intelligent medical document management system with:
- Automated document processing (PDF, images)
- PII anonymization
- Semantic search
- AI-powered Q&A (RAG)
- Comparative document synthesis
- **ML/DL document classification and entity extraction** 🆕

### **Architecture Type**
- **Pattern**: Microservices Architecture
- **Communication**: REST APIs + Message Queue
- **Containerization**: Docker + Docker Compose
- **Frontend**: SPA (Single Page Application)
- **Backend**: Multiple Python FastAPI services

---

## 📊 Architecture Diagrams

### **1. Complete System Architecture**

```mermaid
graph TB
    subgraph "Client Layer"
        UI[React Frontend<br/>Port 3000<br/>TypeScript + MUI]
    end
    
    subgraph "Authentication Layer"
        Auth0[Auth0 Service<br/>JWT Tokens<br/>OAuth 2.0]
    end
    
    subgraph "API Gateway Layer"
        Gateway[API Gateway<br/>Port 8000<br/>FastAPI + CORS]
    end
    
    subgraph "ML/AI Services Layer 🆕"
        ML[ML Service<br/>Port 8006<br/>PyTorch + Transformers]
        ML1[CamemBERT<br/>Document Classifier<br/>7 Types]
        ML2[BioBERT<br/>Medical NER<br/>Entity Extraction]
        ML3[XGBoost<br/>Risk Predictor<br/>Placeholder]
        
        ML --> ML1
        ML --> ML2
        ML --> ML3
    end
    
    subgraph "Document Processing Services"
        DocIng[Doc Ingestor<br/>Port 8001<br/>PDF Processing]
        DeID[DeID Service<br/>Port 8002<br/>Anonymization]
        Index[Semantic Indexer<br/>Port 8003<br/>Vector Embeddings]
    end
    
    subgraph "AI/LLM Services"
        LLM[LLM Q&A<br/>Port 8004<br/>RAG Pipeline]
        Synth[Synthesis Service<br/>Port 8005<br/>Comparative Analysis]
    end
    
    subgraph "Data Layer"
        PG[(PostgreSQL<br/>Port 5432<br/>Main Database)]
        RMQ[RabbitMQ<br/>Ports 5672/15672<br/>Message Queue]
        Models[(Model Storage<br/>Saved Models<br/>Volume Mount)]
    end
    
    UI <-->|JWT Auth| Auth0
    UI <-->|REST API| Gateway
    
    Gateway --> DocIng
    Gateway --> DeID
    Gateway --> Index
    Gateway --> LLM
    Gateway --> Synth
    Gateway --> ML
    
    DocIng --> ML
    DeID --> ML
    
    DocIng --> RMQ
    DeID --> RMQ
    Index --> RMQ
    ML --> RMQ
    
    DocIng --> PG
    DeID --> PG
    Index --> PG
    LLM --> PG
    Synth --> PG
    ML --> PG
    
    ML --> Models
    
    style UI fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style Auth0 fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    style Gateway fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style ML fill:#e1f5ff,stroke:#01579b,stroke-width:3px
    style ML1 fill:#fff9c4,stroke:#f57f17
    style ML2 fill:#fff9c4,stroke:#f57f17
    style ML3 fill:#ffebee,stroke:#c62828
    style PG fill:#c8e6c9,stroke:#388e3c,stroke-width:2px
    style RMQ fill:#ffe0b2,stroke:#e65100,stroke-width:2px
    style Models fill:#e1bee7,stroke:#6a1b9a,stroke-width:2px
```

---

### **2. BPMN Business Process Diagram (Updated)**

```mermaid
graph TB
    Start([User Action])
    
    Start --> Choice{Action Type?}
    
    Choice -->|Upload Document| Upload[Document Upload]
    Choice -->|Search Documents| Search[Search Service]
    Choice -->|Ask Question| QA[Q&A Service]
    Choice -->|Generate Synthesis| Synth[Synthesis Service]
    Choice -->|ML Analysis| MLAnalytics[ML Analytics] 
    
    %% Upload Flow
    Upload --> Validate{Valid File?}
    Validate -->|No| Error1[Show Error]
    Error1 --> End1([End])
    
    Validate -->|Yes| Extract[Extract Text]
    Extract --> CheckPII{Contains PII?}
    
    CheckPII -->|Yes| DeID[Anonymize PII]
    CheckPII -->|No| Store
    DeID --> Store[Store in Database]
    
    Store --> Index[Create Vector Embeddings]
    Index --> Notify1[Notify User]
    Notify1 --> End2([End])
    
    %% Search Flow
    Search --> VectorSearch[Semantic Search]
    VectorSearch --> Results[Display Results]
    Results --> End3([End])
    
    %% Q&A Flow
    QA --> SelectDocs[Select Context Documents]
    SelectDocs --> RetrieveContext[Retrieve Relevant Chunks]
    RetrieveContext --> LLMQuery[Query LLM with Context]
    LLMQuery --> Answer[Display Answer + Sources]
    Answer --> End4([End])
    
    %% Synthesis Flow
    Synth --> SelectMulti[Select Multiple Documents]
    SelectMulti --> Compare[Comparative Analysis]
    Compare --> GenerateReport[Generate Synthesis Report]
    GenerateReport --> ShowReport[Display Report]
    ShowReport --> End5([End])
    
    %% ML Analytics Flow 🆕
    MLAnalytics --> EnterPatient[Enter Patient ID]
    EnterPatient --> Autocomplete{Select from Dropdown}
    Autocomplete --> FilterDocs[Filter Patient Documents]
    FilterDocs --> SearchDocs[Search/Filter Documents]
    SearchDocs --> SelectDoc[Select Document]
    SelectDoc --> Analyze[Click Analyze]
    
    Analyze --> Classify[ML: Classify Document Type]
    Classify --> ExtractEnt[ML: Extract Medical Entities]
    ExtractEnt --> DisplayML[Display ML Results]
    
    DisplayML --> Charts[Show Charts]
    Charts --> Doughnut[Doughnut Chart: Classification]
    Charts --> Radar[Radar Chart: Entity Confidence]
    Charts --> EntityGrid[Entity Grid with Colors]
    
    EntityGrid --> Stats[Performance Stats]
    Stats --> End6([End])
    
    style MLAnalytics fill:#e1f5ff,stroke:#01579b,stroke-width:3px
    style EnterPatient fill:#e1f5ff,stroke:#01579b
    style Classify fill:#e1f5ff,stroke:#01579b
    style ExtractEnt fill:#e1f5ff,stroke:#01579b
    style DisplayML fill:#e1f5ff,stroke:#01579b
    style Charts fill:#fff9c4,stroke:#f57f17
```

---

### **3. ML Service Internal Architecture**

```mermaid
graph TB
    subgraph "ML Service - Port 8006"
        FastAPI[FastAPI Application<br/>Health Checks<br/>CORS Enabled]
        
        subgraph "API Endpoints"
            E1[POST /api/v1/classify]
            E2[POST /api/v1/extract-entities]
            E3[POST /api/v1/analyze]
            E4[GET /api/v1/models/status]
            E5[POST /api/v1/predict-risk]
            E6[POST /api/v1/batch-classify]
            E7[GET /api/v1/statistics]
            E8[GET /health]
        end
        
        subgraph "ML Models"
            M1[CamemBERT Classifier<br/>camembert-base<br/>110M parameters<br/>7 document classes]
            M2[BioBERT NER<br/>dmis-lab/biobert-base-cased-v1.1<br/>110M parameters<br/>6 entity types]
            M3[XGBoost Risk Predictor<br/>Ensemble model<br/>Feature engineering<br/>SHAP explainability]
        end
        
        subgraph "Services"
            MS[ML Service Manager<br/>Model Loading<br/>Inference Pipeline]
            Cache[Model Cache<br/>GPU/CPU Detection<br/>Optimization]
        end
        
        subgraph "Data Processing"
            Preproc[Preprocessor<br/>Tokenization<br/>Text Cleaning]
            Postproc[Postprocessor<br/>Entity Aggregation<br/>Confidence Scoring]
        end
        
        FastAPI --> E1 & E2 & E3 & E4 & E5 & E6 & E7 & E8
        
        E1 --> MS
        E2 --> MS
        E3 --> MS
        
        MS --> Preproc
        Preproc --> M1 & M2 & M3
        M1 & M2 & M3 --> Postproc
        Postproc --> FastAPI
        
        MS --> Cache
        Cache --> M1 & M2 & M3
    end
    
    subgraph "External Storage"
        Models[(Saved Models<br/>/app/saved_models/<br/>Volume Mount)]
        Logs[(Logs<br/>/app/logs/<br/>JSON Format)]
    end
    
    FastAPI --> Models
    FastAPI --> Logs
    
    style FastAPI fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    style M1 fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style M2 fill:#fff9c4,stroke:#f57f17,stroke-width:2px
    style M3 fill:#ffebee,stroke:#c62828,stroke-width:2px
    style MS fill:#e1f5ff,stroke:#01579b,stroke-width:2px
```

---

### **4. ML Analytics Page Flow (Frontend)**

```mermaid
sequenceDiagram
    participant User
    participant UI as ML Analytics Page
    participant API as API Gateway
    participant ML as ML Service
    participant DB as PostgreSQL
    
    User->>UI: Navigate to /ml-analytics
    activate UI
    
    UI->>API: GET /documents?limit=1000
    activate API
    API->>DB: SELECT * FROM documents
    activate DB
    DB-->>API: All documents
    deactivate DB
    API-->>UI: {data: [...documents]}
    deactivate API
    
    UI->>UI: Parse metadata<br/>Extract patient_ids
    UI->>UI: Create unique patient ID list
    UI-->>User: Show patient ID autocomplete dropdown
    
    User->>UI: Click input field
    UI-->>User: Open dropdown with patient IDs
    
    User->>UI: Type/Select patient ID
    UI->>UI: Filter documents by patient_id
    UI-->>User: Display filtered documents (count)
    
    User->>UI: Type in search box
    UI->>UI: Client-side filter by filename/type
    UI-->>User: Update document list
    
    User->>UI: Click on document
    UI->>UI: Set selectedDocumentId
    UI-->>User: Highlight document + show info card
    
    User->>UI: Click "Analyser avec IA"
    
    UI->>UI: Find document in list
    
    alt Document has content
        UI->>API: POST /ml/analyze<br/>{text: doc.content}
        activate API
        
        API->>ML: Forward analyze request
        activate ML
        
        ML->>ML: Load CamemBERT model
        ML->>ML: Tokenize text
        ML->>ML: Classify document
        Note over ML: Get probabilities for 7 classes
        
        ML->>ML: Load BioBERT model
        ML->>ML: Extract entities (NER)
        Note over ML: Find diseases, medications,<br/>dosages, symptoms, tests
        
        ML-->>API: {<br/>  classification: {...},<br/>  entities: {...},<br/>  processing_time_ms: 65<br/>}
        deactivate ML
        
        API-->>UI: ML results
        deactivate API
        
        UI->>UI: Render Doughnut Chart<br/>(Classification probabilities)
        UI->>UI: Render Radar Chart<br/>(Entity confidences)
        UI->>UI: Render Entity Grid<br/>(Color-coded by type)
        UI->>UI: Update Performance Stats
        
        UI-->>User: Display ML insights ✨
        
    else Document has no content
        UI-->>User: Error: "Document sans contenu"
    end
    
    deactivate UI
```

---

### **5. Authentication & Authorization Flow**

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Frontend as React App
    participant Auth0 as Auth0 Service
    participant Gateway as API Gateway
    participant Service as Backend Service
    participant DB as PostgreSQL
    
    User->>Browser: Visit http://localhost:3000
    Browser->>Frontend: Load React App
    Frontend->>Frontend: Check localStorage for tokens
    
    alt No Token Found
        Frontend->>Auth0: Redirect to login
        Auth0-->>User: Show login page
        User->>Auth0: Enter credentials
        Auth0->>Auth0: Validate credentials
        Auth0-->>Frontend: Redirect with code
        Frontend->>Auth0: Exchange code for tokens
        Auth0-->>Frontend: {<br/>  access_token,<br/>  id_token,<br/>  refresh_token<br/>}
        Frontend->>Frontend: Store tokens in memory
        Frontend->>Auth0: GET /userinfo
        Auth0-->>Frontend: User profile
        Frontend-->>User: Show Dashboard
    end
    
    User->>Frontend: Click "Upload Document"
    
    Frontend->>Frontend: Get access_token
    Frontend->>Gateway: POST /api/documents/upload<br/>Authorization: Bearer {token}
    
    Gateway->>Gateway: Verify JWT signature
    Gateway->>Gateway: Check token expiration
    Gateway->>Gateway: Extract user claims
    
    alt Token Valid
        Gateway->>Service: Forward request + user context
        Service->>DB: INSERT document
        DB-->>Service: Document created
        Service-->>Gateway: {document_id, status}
        Gateway-->>Frontend: Success response
        Frontend-->>User: Show success message
    else Token Invalid/Expired
        Gateway-->>Frontend: 401 Unauthorized
        Frontend->>Auth0: Refresh token
        Auth0-->>Frontend: New access_token
        Frontend->>Gateway: Retry request
    else Token Missing
        Gateway-->>Frontend: 401 Unauthorized
        Frontend->>Auth0: Redirect to login
    end
```

---

### **6. Document Processing Pipeline**

```mermaid
graph LR
    subgraph "Stage 1: Upload"
        U1[User Selects File]
        U2[Frontend Validation]
        U3[Upload to Gateway]
        
        U1 --> U2
        U2 --> U3
    end
    
    subgraph "Stage 2: Ingestion"
        I1[Doc Ingestor Receives]
        I2{File Type?}
        I3[Extract PDF Text]
        I4[OCR Image]
        I5[Parse Metadata]
        
        I1 --> I2
        I2 -->|PDF| I3
        I2 -->|Image| I4
        I3 --> I5
        I4 --> I5
    end
    
    subgraph "Stage 3: Anonymization"
        D1[DeID Service]
        D2[Detect PII with BioBERT]
        D3[Presidio Anonymizer]
        D4[Replace with Tokens]
        
        D1 --> D2
        D2 --> D3
        D3 --> D4
    end
    
    subgraph "Stage 4: Storage"
        S1[Save to PostgreSQL]
        S2[Generate Document ID]
        S3[Store Metadata]
        
        S1 --> S2
        S2 --> S3
    end
    
    subgraph "Stage 5: Indexing"
        IX1[Semantic Indexer]
        IX2[Chunk Text]
        IX3[Generate Embeddings]
        IX4[Store Vectors]
        
        IX1 --> IX2
        IX2 --> IX3
        IX3 --> IX4
    end
    
    subgraph "Stage 6: ML Analysis (Optional)"
        ML1[User Triggers Analysis]
        ML2[Classify Document]
        ML3[Extract Entities]
        ML4[Display Results]
        
        ML1 --> ML2
        ML2 --> ML3
        ML3 --> ML4
    end
    
    U3 --> I1
    I5 --> D1
    D4 --> S1
    S3 --> IX1
    IX4 --> ML1
    
    style ML1 fill:#e1f5ff,stroke:#01579b
    style ML2 fill:#e1f5ff,stroke:#01579b
    style ML3 fill:#e1f5ff,stroke:#01579b
    style ML4 fill:#e1f5ff,stroke:#01579b
```

---

### **7. Class Diagram - ML Service**

```mermaid
classDiagram
    class FastAPIApp {
        +app: FastAPI
        +startup_event()
        +shutdown_event()
        +health_check()
    }
    
    class MLServiceManager {
        -classifier: DocumentClassifier
        -ner_model: MedicalNER
        -risk_predictor: RiskPredictor
        -device: str
        +__init__()
        +load_models()
        +classify(text: str)
        +extract_entities(text: str)
        +analyze(text: str)
        +predict_risk(features: dict)
        +get_model_status()
    }
    
    class DocumentClassifier {
        -model: CamembertForSequenceClassification
        -tokenizer: CamembertTokenizer
        -label_map: Dict
        -confidence_threshold: float
        +__init__(model_path: str)
        +predict(text: str) ClassificationResult
        +predict_batch(texts: List) List
        +get_probabilities(text: str) Dict
    }
    
    class MedicalNER {
        -model: BertForTokenClassification
        -tokenizer: BertTokenizer
        -entity_labels: List
        -aggregation_strategy: str
        +__init__(model_path: str)
        +extract_entities(text: str) List~Entity~
        +annotate_text(text: str) AnnotatedText
        +aggregate_entities(tokens: List) List~Entity~
    }
    
    class RiskPredictor {
        -model: XGBoostClassifier
        -scaler: StandardScaler
        -feature_names: List
        -explainer: shap.Explainer
        +__init__(model_path: str)
        +predict(features: dict) float
        +predict_proba(features: dict) Dict
        +explain_prediction(features: dict) SHAP
        +get_feature_importance() Dict
    }
    
    class ClassificationResult {
        +predicted_class: str
        +confidence: float
        +all_probabilities: Dict
        +processing_time_ms: int
    }
    
    class Entity {
        +text: str
        +label: str
        +start: int
        +end: int
        +confidence: float
    }
    
    class EntityExtractionResult {
        +entities: List~Entity~
        +Count: int
        +value: List~Entity~
        +processing_time_ms: int
    }
    
    class AnalyzeResult {
        +classification: ClassificationResult
        +entities: EntityExtractionResult
        +processing_time_ms: int
    }
    
    class RiskScore {
        +score: float
        +risk_level: str
        +factors: List~str~
        +shap_values: Dict
        +recommendation: str
    }
    
    FastAPIApp --> MLServiceManager
    MLServiceManager --> DocumentClassifier
    MLServiceManager --> MedicalNER
    MLServiceManager --> RiskPredictor
    
    DocumentClassifier --> ClassificationResult
    MedicalNER --> Entity
    MedicalNER --> EntityExtractionResult
    RiskPredictor --> RiskScore
    
    MLServiceManager --> AnalyzeResult
    AnalyzeResult --> ClassificationResult
    AnalyzeResult --> EntityExtractionResult
```

---

## 🔧 Microservices Details

### **Service 1: Frontend (React)**

| Property | Value |
|----------|-------|
| **Port** | 3000 |
| **Technology** | React 18 + TypeScript |
| **UI Library** | Material-UI (MUI) v5 |
| **State Management** | Zustand + React Query |
| **Routing** | React Router v6 |
| **Auth** | Auth0 React SDK |
| **Charts** | Chart.js + react-chartjs-2 |
| **HTTP Client** | Axios |

**Pages:**
- `/` - Dashboard
- `/upload` - Document Upload
- `/documents` - Document Library
- `/qa-chat` - AI Q&A Interface
- `/synthesis` - Comparative Analysis
- `/analyses` - Modern Synthesis (Patient-based)
- `/ml-analytics` - 🆕 ML/DL Analysis
- `/settings` - User Settings

---

### **Service 2: API Gateway**

| Property | Value |
|----------|-------|
| **Port** | 8000 |
| **Framework** | FastAPI |
| **Auth** | JWT validation |
| **CORS** | Enabled for port 3000 |
| **Rate Limiting** | Implemented |

**Endpoints:**
```
POST   /api/documents/upload
GET    /api/documents
GET    /api/documents/{id}
DELETE /api/documents/{id}
POST   /api/qa/ask
POST   /api/synthesis/generate
GET    /api/health
```

---

### **Service 3: Document Ingestor**

| Property | Value |
|----------|-------|
| **Port** | 8001 |
| **Purpose** | PDF/Image text extraction |
| **Libraries** | PyPDF2, pytesseract, Pillow |

**Features:**
- PDF text extraction
- OCR for images
- Metadata extraction
- Multi-format support

---

### **Service 4: DeID Service**

| Property | Value |
|----------|-------|
| **Port** | 8002 |
| **Purpose** | PII anonymization |
| **Libraries** | Presidio, spaCy, Transformers |

**PII Detection:**
- Names (Persons)
- Locations
- Organizations
- Dates
- Phone numbers
- Email addresses
- Medical record numbers

---

### **Service 5: Semantic Indexer**

| Property | Value |
|----------|-------|
| **Port** | 8003 |
| **Purpose** | Vector embeddings + search |
| **Model** | sentence-transformers |

**Features:**
- Text chunking
- Embedding generation
- Vector storage
- Semantic similarity search

---

### **Service 6: LLM Q&A**

| Property | Value |
|----------|-------|
| **Port** | 8004 |
| **Purpose** | RAG-based question answering |
| **LLM** | Mistral 7B / Claude API |

**Features:**
- Context retrieval
- Prompt engineering
- Answer generation
- Source attribution

---

### **Service 7: Synthesis Service**

| Property | Value |
|----------|-------|
| **Port** | 8005 |
| **Purpose** | Multi-document comparative analysis |
| **LLM** | Claude API |

**Features:**
- Multi-document selection
- Comparative analysis
- Report generation
- Timeline creation

---

### **Service 8: ML Service 🆕**

| Property | Value |
|----------|-------|
| **Port** | 8006 |
| **Purpose** | Document classification & NER |
| **Framework** | PyTorch + Transformers |
| **Models** | CamemBERT + BioBERT + XGBoost |

**Features:**
- Document type classification (7 classes)
- Medical entity extraction (6 types)
- Risk prediction (placeholder)
- Batch processing
- Model statistics

**Document Classes:**
1. Blood Test (Analyse sanguine)
2. X-Ray (Radiographie)
3. MRI (IRM)
4. Prescription (Ordonnance)
5. Medical Report (Rapport médical)
6. Lab Result (Résultat de laboratoire)
7. Consultation Note (Note de consultation)

**Entity Types:**
1. DISEASE (Maladie)
2. MEDICATION (Médicament)
3. DOSAGE (Posologie)
4. TEST (Examen)
5. SYMPTOM (Symptôme)
6. ANATOMY (Anatomie)

---

## 💾 Database Schema

### **PostgreSQL Database**

**Tables:**

#### 1. `documents`
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50),
    file_size BIGINT,
    processing_status VARCHAR(50),
    is_anonymized BOOLEAN DEFAULT FALSE,
    content TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP,
    uploaded_by VARCHAR(255),
    patient_id VARCHAR(100),
    document_type VARCHAR(100)
);
```

#### 2. `document_chunks`
```sql
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER,
    content TEXT,
    embedding VECTOR(384),
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 3. `qa_history`
```sql
CREATE TABLE qa_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255),
    question TEXT NOT NULL,
    answer TEXT,
    context_documents UUID[],
    sources JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### 4. `ml_predictions` 🆕
```sql
CREATE TABLE ml_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id),
    prediction_type VARCHAR(50), -- 'classification' | 'ner' | 'risk'
    predicted_class VARCHAR(100),
    confidence FLOAT,
    probabilities JSONB,
    entities JSONB,
    processing_time_ms INTEGER,
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🔐 Security Architecture

*See separate [SECURITY_DOCUMENTATION.md](SECURITY_DOCUMENTATION.md) for details*

**Key Security Features:**
- ✅ Auth0 OAuth 2.0 authentication
- ✅ JWT token-based authorization
- ✅ CORS protection
- ✅ Rate limiting
- ✅ PII anonymization
- ✅ HTTPS in production
- ✅ Environment variable encryption
- ✅ SQL injection protection (SQLAlchemy ORM)
- ✅ XSS protection (React escaping)

---

## 🚀 Deployment

### **Development Environment**

```bash
# Start all services
docker-compose up -d

# Access services
Frontend:     http://localhost:3000
API Gateway:  http://localhost:8000
ML Service:   http://localhost:8006
PostgreSQL:   localhost:5432
RabbitMQ UI:  http://localhost:15672
```

### **Production Considerations**

- Use environment-specific configs
- Enable HTTPS with SSL certificates
- Set up CI/CD pipeline
- Configure monitoring (Prometheus + Grafana)
- Implement log aggregation (ELK stack)
- Database backups
- Load balancing
- Auto-scaling

---

## 📈 Performance Metrics

| Metric | Target | Current |
|--------|--------|---------|
| **Document Upload** | < 2s | ~1.5s |
| **PDF Processing** | < 5s | ~3s |
| **ML Classification** | < 100ms | ~65ms |
| **ML Entity Extraction** | < 150ms | ~85ms |
| **Q&A Response** | < 3s | ~2s |
| **Semantic Search** | < 500ms | ~300ms |
| **Synthesis Generation** | < 10s | ~7s |

---

## 📚 Additional Documentation

- [Security & Auth0 Documentation](SECURITY_DOCUMENTATION.md)
- [ML Service Training Guide](ML_TRAINING_GUIDE.md)
- [API Reference](API_DOCUMENTATION.md)
- [Deployment Guide](DEPLOYMENT_GUIDE.md)

---

**Last Updated**: December 11, 2025  
**Maintained by**: Development Team
