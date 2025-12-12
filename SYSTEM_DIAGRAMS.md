# DocQA-MS System Diagrams

This document contains all the architectural and process diagrams for the DocQA-MS (Medical Document Q&A System) project.

## Table of Contents
1. [Microservices Architecture](#microservices-architecture)
2. [BPMN - Document Processing Workflow](#bpmn---document-processing-workflow)
3. [Security Architecture](#security-architecture)
4. [Application Flow Diagram](#application-flow-diagram)
5. [Data Flow Diagram](#data-flow-diagram)
6. [Database Schema Diagram](#database-schema-diagram)
7. [API Interaction Diagram](#api-interaction-diagram)
8. [Deployment Architecture](#deployment-architecture)

---

## Microservices Architecture

```mermaid
graph TB
    subgraph "Frontend Layer"
        FE[React SPA<br/>InterfaceClinique<br/>Port: 3000]
    end

    subgraph "API Gateway Layer"
        GW[API Gateway<br/>FastAPI<br/>Port: 8000<br/>- Authentication<br/>- Routing<br/>- Security Headers<br/>- CORS]
    end

    subgraph "Microservices Layer"
        DI[Document Ingestor<br/>Port: 8001<br/>- File Upload<br/>- Queue Publishing]
        DEID[De-Identification<br/>Port: 8002<br/>- PII Detection<br/>- Anonymization<br/>Presidio + spaCy]
        IDX[Semantic Indexer<br/>Port: 8003<br/>- Vector Embeddings<br/>- FAISS Search<br/>- Document Chunking]
        QA[LLM Q&A<br/>Port: 8004<br/>- Groq API<br/>- Medical Q&A<br/>- Context Retrieval]
        SYN[Synthesis Comparative<br/>Port: 8005<br/>- Document Synthesis<br/>- Comparison Analysis]
        AUDIT[Audit Logger<br/>Port: 8006<br/>- Activity Logging<br/>- Compliance Tracking]
        MLS[ML Service<br/>Port: 8007<br/>- Model Inference<br/>- Classification<br/>- NER]
    end

    subgraph "Infrastructure Layer"
        DB[(PostgreSQL<br/>Database<br/>- Documents<br/>- Users<br/>- QA History<br/>- Audit Logs)]
        QUEUE[(RabbitMQ<br/>Message Queue<br/>- Document Processing<br/>- Async Tasks)]
        FS[(File Storage<br/>- Uploaded Documents<br/>- Processed Files)]
    end

    FE --> GW
    GW --> DI
    GW --> DEID
    GW --> IDX
    GW --> QA
    GW --> SYN
    GW --> AUDIT
    GW --> MLS

    DI --> QUEUE
    IDX --> QUEUE
    QUEUE --> IDX

    DI --> DB
    DEID --> DB
    IDX --> DB
    QA --> DB
    AUDIT --> DB
    MLS --> DB

    DI --> FS
    IDX --> FS

    classDef frontend fill:#e1f5fe
    classDef gateway fill:#fff3e0
    classDef service fill:#f3e5f5
    classDef infra fill:#e8f5e8

    class FE frontend
    class GW gateway
    class DI,DEID,IDX,QA,SYN,AUDIT,MLS service
    class DB,QUEUE,FS infra
```

---

## BPMN - Document Processing Workflow

```mermaid
flowchart TD
    Start([Document Upload<br/>Starts]) --> Validate[Validate File<br/>- Size Check<br/>- Type Check<br/>- Security Scan]

    Validate --> QueuePub[Publish to Queue<br/>document_processing]

    QueuePub --> Consumer[Indexer Consumer<br/>Processes Message]

    Consumer --> ChunkDoc[Chunk Document<br/>- Text Extraction<br/>- Chunking Logic<br/>- Metadata]

    ChunkDoc --> DeID{De-Identification<br/>Required?}

    DeID -->|Yes| AnonService[Call DeID Service<br/>- PII Detection<br/>- Anonymization<br/>- Store Results]

    DeID -->|No| Embed[Generate Embeddings<br/>- Sentence Transformers<br/>- Vector Creation]

    AnonService --> Embed

    Embed --> StoreDB[Store in Database<br/>- document_chunks<br/>- Update FAISS Index]

    StoreDB --> UpdateStatus[Update Document Status<br/>processing_status = 'processed']

    UpdateStatus --> SearchReady[Document Ready<br/>for Search & Q&A]

    SearchReady --> End([Process Complete])

    classDef startEnd fill:#e8f5e8,stroke:#2e7d32
    classDef process fill:#fff3e0,stroke:#f57c00
    classDef decision fill:#fff8e1,stroke:#f9a825
    classDef queue fill:#f3e5f5,stroke:#7b1fa2

    class Start,End startEnd
    class Validate,ChunkDoc,Embed,StoreDB,UpdateStatus process
    class DeID decision
    class QueuePub,Consumer queue
```

---

## Security Architecture

```mermaid
flowchart TD
    subgraph "External Threats"
        Threats[Attack Vectors<br/>- XSS<br/>- CSRF<br/>- Injection<br/>- Unauthorized Access]
    end

    subgraph "Network Security"
        CDN[Vercel CDN<br/>- DDoS Protection<br/>- SSL/TLS<br/>- Global Edge]
        FW[Application Firewall<br/>- Request Filtering<br/>- Rate Limiting]
    end

    subgraph "Authentication Layer"
        Auth0[Auth0 Service<br/>- JWT Tokens<br/>- OAuth2/OIDC<br/>- MFA Support<br/>- User Management]
    end

    subgraph "API Gateway Security"
        JWT[Token Validation<br/>- RS256 JWT<br/>- Token Refresh<br/>- User Context]
        CORS[CORS Policy<br/>- Origin Control<br/>- Credential Handling]
        Headers[Security Headers<br/>- CSP<br/>- HSTS<br/>- X-Frame-Options<br/>- X-Content-Type]
    end

    subgraph "Application Security"
        AuthZ[Authorization<br/>- User Isolation<br/>- Role-Based Access<br/>- Resource Ownership]
        Input[Input Validation<br/>- Sanitization<br/>- Type Checking<br/>- SQL Injection Prevention]
        Audit[Audit Logging<br/>- All Actions<br/>- Compliance<br/>- Forensic Analysis]
    end

    subgraph "Data Security"
        Encrypt[Encryption<br/>- At Rest: Railway<br/>- In Transit: SSL<br/>- Database: PostgreSQL]
        Anon[Data Anonymization<br/>- PII Detection<br/>- Entity Replacement<br/>- Privacy Compliance]
        Backup[Secure Backups<br/>- Encrypted<br/>- Regular<br/>- Disaster Recovery]
    end

    Threats --> CDN
    CDN --> FW
    FW --> Auth0
    Auth0 --> JWT
    JWT --> CORS
    CORS --> Headers
    Headers --> AuthZ
    AuthZ --> Input
    Input --> Audit
    Audit --> Encrypt
    Encrypt --> Anon
    Anon --> Backup

    classDef threat fill:#ffebee,stroke:#c62828
    classDef network fill:#e8f5e8,stroke:#2e7d32
    classDef auth fill:#fff3e0,stroke:#f57c00
    classDef app fill:#f3e5f5,stroke:#7b1fa2
    classDef data fill:#e1f5fe,stroke:#0277bd

    class Threats threat
    class CDN,FW network
    class Auth0,JWT,CORS,Headers auth
    class AuthZ,Input,Audit app
    class Encrypt,Anon,Backup data
```

---

## Application Flow Diagram

```mermaid
flowchart TD
    User([Healthcare<br/>Professional]) --> Login[Login via Auth0<br/>- OAuth2 Flow<br/>- JWT Token]

    Login --> Dashboard[Dashboard<br/>- Document Overview<br/>- Recent Activity<br/>- Statistics]

    Dashboard --> Upload{Upload<br/>Document?}
    Dashboard --> Search{Search<br/>Documents?}
    Dashboard --> QA{Ask<br/>Question?}

    Upload --> FileSelect[Select File<br/>- PDF, DOC, TXT<br/>- Size Validation]
    FileSelect --> Processing[Document Processing<br/>- Ingestion<br/>- De-identification<br/>- Indexing]

    Processing --> Indexed[Document Indexed<br/>- Searchable<br/>- Q&A Ready]

    Search --> Query[Enter Search Query<br/>- Semantic Search<br/>- Filter Options]
    Query --> Results[Search Results<br/>- Document Chunks<br/>- Relevance Scores<br/>- Source Documents]

    QA --> Question[Enter Question<br/>- Natural Language<br/>- Context Selection]
    Question --> Retrieval[Retrieve Context<br/>- Semantic Search<br/>- Top-K Chunks<br/>- Document Filtering]

    Retrieval --> LLM[LLM Processing<br/>- Groq API<br/>- Medical Context<br/>- Answer Generation]

    LLM --> Answer[Display Answer<br/>- Sources Cited<br/>- Confidence Score<br/>- Response Time]

    Indexed --> Dashboard
    Results --> Dashboard
    Answer --> Dashboard

    Dashboard --> Audit[All Actions Logged<br/>- User Activity<br/>- Compliance<br/>- Security]

    classDef user fill:#e1f5fe,stroke:#0277bd
    classDef action fill:#fff3e0,stroke:#f57c00
    classDef process fill:#f3e5f5,stroke:#7b1fa2
    classDef decision fill:#fff8e1,stroke:#f9a825
    classDef result fill:#e8f5e8,stroke:#2e7d32

    class User user
    class Login,Dashboard,FileSelect,Query,Question action
    class Processing,Retrieval,LLM process
    class Upload,Search,QA decision
    class Indexed,Results,Answer,Audit result
```

---

## Data Flow Diagram

```mermaid
flowchart TD
    subgraph "Input Sources"
        Upload[File Upload<br/>- PDF/DOC/TXT<br/>- Medical Reports<br/>- Clinical Notes]
        API[API Ingestion<br/>- HL7 Messages<br/>- FHIR Resources<br/>- External Systems]
    end

    subgraph "Ingestion Layer"
        Parser[Document Parser<br/>- Text Extraction<br/>- Format Detection<br/>- Metadata Extraction]
        Validate[Validation<br/>- File Integrity<br/>- Content Check<br/>- Security Scan]
    end

    subgraph "Processing Pipeline"
        Queue[(RabbitMQ<br/>Processing Queue)]
        DeID[De-Identification<br/>- PII Detection<br/>- Anonymization<br/>- Entity Storage]
        Chunk[Text Chunking<br/>- Sentence Splitting<br/>- Overlap Handling<br/>- Metadata Preservation]
        Embed[Embedding Generation<br/>- Sentence Transformers<br/>- Vector Creation<br/>- FAISS Indexing]
    end

    subgraph "Storage Layer"
        DB[(PostgreSQL<br/>- documents<br/>- document_chunks<br/>- document_anonymizations<br/>- qa_interactions<br/>- audit_logs)]
        Vector[(FAISS Index<br/>- Vector Embeddings<br/>- Similarity Search<br/>- Fast Retrieval)]
        Files[(File Storage<br/>- Original Files<br/>- Processed Files<br/>- Temporary Files)]
    end

    subgraph "Query Processing"
        Search[Semantic Search<br/>- Query Embedding<br/>- Vector Similarity<br/>- Result Ranking]
        Context[Context Retrieval<br/>- Top-K Chunks<br/>- Document Filtering<br/>- Relevance Scoring]
        LLM[LLM Generation<br/>- Prompt Engineering<br/>- Answer Synthesis<br/>- Source Attribution]
    end

    subgraph "Output"
        Results[Search Results<br/>- Document Snippets<br/>- Source Citations<br/>- Confidence Scores]
        Answers[Q&A Responses<br/>- Natural Language<br/>- Medical Context<br/>- Evidence-Based]
        Audit[Audit Trail<br/>- All Access Logs<br/>- Compliance Data<br/>- Security Events]
    end

    Upload --> Parser
    API --> Parser
    Parser --> Validate
    Validate --> Queue
    Queue --> DeID
    DeID --> Chunk
    Chunk --> Embed
    Embed --> DB
    Embed --> Vector
    Validate --> Files

    Search --> Vector
    Vector --> Context
    Context --> LLM
    LLM --> Answers

    Search --> DB
    Context --> DB
    LLM --> DB

    Search --> Results
    Answers --> Audit
    Results --> Audit

    classDef input fill:#e1f5fe,stroke:#0277bd
    classDef process fill:#fff3e0,stroke:#f57c00
    classDef storage fill:#e8f5e8,stroke:#2e7d32
    classDef query fill:#f3e5f5,stroke:#7b1fa2
    classDef output fill:#fff8e1,stroke:#f9a825

    class Upload,API input
    class Parser,Validate,DeID,Chunk,Embed process
    class DB,Vector,Files storage
    class Search,Context,LLM query
    class Results,Answers,Audit output
```

---

## Database Schema Diagram

```mermaid
erDiagram
    users {
        uuid id PK
        varchar auth0_sub UK
        varchar email UK
        varchar name
        varchar nickname
        varchar picture
        varchar role
        jsonb permissions
        boolean is_active
        timestamp last_login
        boolean email_verified
        jsonb metadata
        timestamp created_at
        timestamp updated_at
    }

    documents {
        uuid id PK
        varchar filename
        varchar file_type
        text content
        bigint file_size
        timestamp upload_date
        varchar processing_status
        boolean is_anonymized
        timestamp indexed_at
        jsonb metadata
        timestamp created_at
    }

    document_chunks {
        uuid id PK
        uuid document_id FK
        integer chunk_index
        text content
        jsonb metadata
        timestamp created_at
    }

    document_anonymizations {
        uuid id PK
        varchar document_id
        text original_content
        text anonymized_content
        jsonb pii_entities
        integer processing_time_ms
        timestamp created_at
    }

    qa_interactions {
        uuid id PK
        uuid user_id FK
        text question
        text answer
        uuid[] context_documents
        decimal confidence_score
        integer response_time_ms
        varchar llm_model
        timestamp created_at
    }

    audit_logs {
        uuid id PK
        uuid user_id FK
        varchar action
        varchar resource_type
        uuid resource_id
        jsonb details
        timestamp timestamp
    }

    users ||--o{ qa_interactions : "has"
    users ||--o{ audit_logs : "performs"
    documents ||--o{ document_chunks : "chunked_into"
    documents ||--o{ qa_interactions : "used_in"
```

---

## API Interaction Diagram

```mermaid
sequenceDiagram
    participant FE as Frontend (React)
    participant GW as API Gateway
    participant DI as Document Ingestor
    participant DEID as DeID Service
    participant IDX as Semantic Indexer
    participant QA as LLM Q&A
    participant DB as PostgreSQL
    participant MQ as RabbitMQ

    Note over FE,MQ: Document Upload Flow
    FE->>GW: POST /api/v1/documents/upload
    GW->>GW: Validate JWT Token
    GW->>DI: Forward to Document Ingestor
    DI->>DI: Validate file & extract text
    DI->>MQ: Publish document_processing message
    DI->>DB: Store document metadata
    DI-->>GW: Success response
    GW-->>FE: Upload confirmation

    Note over FE,MQ: Background Processing
    MQ->>IDX: Consume document_processing
    IDX->>IDX: Chunk document text
    IDX->>DEID: POST /anonymize (if needed)
    DEID->>DEID: Detect & anonymize PII
    DEID->>DB: Store anonymization results
    DEID-->>IDX: Anonymized content
    IDX->>IDX: Generate embeddings
    IDX->>DB: Store chunks & update FAISS
    IDX->>DB: Update document status

    Note over FE,DB: Q&A Flow
    FE->>GW: POST /api/v1/qa/ask
    GW->>GW: Validate JWT & permissions
    GW->>QA: Forward question
    QA->>IDX: POST /api/v1/search (semantic search)
    IDX->>IDX: Query FAISS index
    IDX->>DB: Retrieve relevant chunks
    IDX-->>QA: Return context chunks
    QA->>QA: Prepare prompt with context
    QA->>QA: Call Groq API
    QA->>DB: Store Q&A interaction
    QA-->>GW: Answer with sources
    GW-->>FE: Formatted response

    Note over FE,DB: Audit Logging
    GW->>GW: Log all requests
    QA->>GW: Send audit events
    GW->>GW: POST /api/v1/audit/log
    GW->>DB: Store audit logs
```

---

## Deployment Architecture

```mermaid
graph TB
    subgraph "Development"
        Dev[Local Development<br/>- VS Code<br/>- Docker Compose<br/>- Hot Reload]
    end

    subgraph "CI/CD Pipeline"
        Git[GitHub Repository<br/>- Source Code<br/>- Workflows<br/>- Secrets]
        Actions[GitHub Actions<br/>- Frontend Build<br/>- Backend Build<br/>- Testing<br/>- Security Scan]
    end

    subgraph "Production Hosting"
        Vercel[Vercel (Frontend)<br/>- React SPA<br/>- CDN<br/>- SSL/TLS<br/>- Global Edge]
        Railway[Railway (Backend)<br/>- Docker Containers<br/>- Internal Network<br/>- Auto Scaling<br/>- Health Checks]
    end

    subgraph "Railway Services"
        APIGW[API Gateway<br/>Container: api-gateway<br/>Port: 8000]
        DocIng[Document Ingestor<br/>Container: doc-ingestor<br/>Port: 8001]
        DeID[De-Identification<br/>Container: deid<br/>Port: 8002]
        Indexer[Semantic Indexer<br/>Container: indexer<br/>Port: 8003]
        LLMQA[LLM Q&A<br/>Container: llm-qa<br/>Port: 8004]
        Synth[Synthesis<br/>Container: synthesis<br/>Port: 8005]
        Audit[Audit Logger<br/>Container: audit-logger<br/>Port: 8006]
        ML[ML Service<br/>Container: ml-service<br/>Port: 8007]
    end

    subgraph "Infrastructure"
        Postgres[(PostgreSQL<br/>- 512MB Storage<br/>- Auto Backups<br/>- Connection Pooling)]
        RabbitMQ[(RabbitMQ<br/>- Message Queue<br/>- Task Distribution<br/>- Async Processing)]
        Redis[(Redis<br/>- Caching<br/>- Session Store<br/>- Rate Limiting)]
    end

    subgraph "External Services"
        Auth0[Auth0<br/>- Authentication<br/>- User Management<br/>- JWT Tokens<br/>- MFA]
        Groq[Groq API<br/>- LLM Inference<br/>- Medical Q&A<br/>- Context Processing]
    end

    Dev --> Git
    Git --> Actions
    Actions --> Vercel
    Actions --> Railway

    Railway --> APIGW
    Railway --> DocIng
    Railway --> DeID
    Railway --> Indexer
    Railway --> LLMQA
    Railway --> Synth
    Railway --> Audit
    Railway --> ML

    APIGW --> Postgres
    DocIng --> Postgres
    DeID --> Postgres
    Indexer --> Postgres
    LLMQA --> Postgres
    Audit --> Postgres
    ML --> Postgres

    DocIng --> RabbitMQ
    Indexer --> RabbitMQ

    LLMQA --> Groq
    APIGW --> Auth0

    classDef dev fill:#e1f5fe,stroke:#0277bd
    classDef cicd fill:#fff3e0,stroke:#f57c00
    classDef hosting fill:#e8f5e8,stroke:#2e7d32
    classDef service fill:#f3e5f5,stroke:#7b1fa2
    classDef infra fill:#fff8e1,stroke:#f9a825
    classDef external fill:#ffebee,stroke:#c62828

    class Dev dev
    class Git,Actions cicd
    class Vercel,Railway hosting
    class APIGW,DocIng,DeID,Indexer,LLMQA,Synth,Audit,ML service
    class Postgres,RabbitMQ,Redis infra
    class Auth0,Groq external
```

---

*This document provides comprehensive architectural documentation for the DocQA-MS system. Each diagram serves a specific purpose in understanding different aspects of the system architecture, from high-level component interactions to detailed data flows and security measures.*