# DocQA-MS API Endpoints Documentation

## Overview

This document describes the REST API endpoints for each microservice in the DocQA-MS system. All services use FastAPI and follow RESTful conventions.

## API Gateway (Port 8000)

The API Gateway provides a unified entry point for all client requests and handles routing, authentication, and load balancing.

### Authentication Endpoints

#### POST /auth/login
Authenticate user and return JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### POST /auth/refresh
Refresh JWT access token.

#### POST /auth/logout
Invalidate user session.

### Document Management Endpoints

#### POST /documents/upload
Upload a new document for processing.

**Request:**
- Content-Type: multipart/form-data
- Body: file (PDF, DOCX, TXT, etc.)

**Response:**
```json
{
  "document_id": "uuid",
  "status": "uploaded",
  "message": "Document uploaded successfully"
}
```

#### GET /documents
List user's documents with filtering options.

**Query Parameters:**
- `status`: processing status
- `type`: document type
- `date_from`: start date
- `date_to`: end date
- `limit`: max results (default: 50)
- `offset`: pagination offset

**Response:**
```json
{
  "documents": [
    {
      "id": "uuid",
      "filename": "string",
      "status": "processed",
      "upload_date": "2024-01-15T10:30:00Z",
      "document_type": "medical_report"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

#### GET /documents/{document_id}
Get detailed information about a specific document.

#### DELETE /documents/{document_id}
Delete a document and all associated data.

### Search Endpoints

#### POST /search
Perform semantic search across documents.

**Request Body:**
```json
{
  "query": "hypertension treatment",
  "filters": {
    "document_type": ["medical_report"],
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-12-31"
    },
    "patient_id": "ANON_PAT_001"
  },
  "limit": 20
}
```

**Response:**
```json
{
  "query_id": "uuid",
  "results": [
    {
      "document_id": "uuid",
      "chunk_id": "uuid",
      "score": 0.92,
      "content": "Patient presents with hypertension...",
      "metadata": {
        "page": 1,
        "section": "clinical_report"
      }
    }
  ],
  "total_results": 15,
  "execution_time_ms": 245
}
```

### Q&A Endpoints

#### POST /qa/ask
Submit a question for LLM-powered Q&A.

**Request Body:**
```json
{
  "question": "What is the current treatment for hypertension?",
  "context_documents": ["uuid1", "uuid2"],
  "session_id": "uuid"
}
```

**Response:**
```json
{
  "answer": "The patient is currently treated with irbesartan 150mg daily...",
  "sources": [
    {
      "document_id": "uuid",
      "chunk_id": "uuid",
      "relevance_score": 0.88,
      "excerpt": "irbesartan 150mg: 1 comprimé par jour"
    }
  ],
  "confidence_score": 0.91,
  "execution_time_ms": 1250
}
```

#### GET /qa/sessions
List user's Q&A sessions.

#### GET /qa/sessions/{session_id}
Get conversation history for a session.

### Synthesis Endpoints

#### POST /synthesis
Generate structured synthesis or comparison.

**Request Body:**
```json
{
  "type": "patient_timeline",
  "parameters": {
    "patient_id": "ANON_PAT_001",
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-12-31"
    }
  }
}
```

**Response:**
```json
{
  "synthesis_id": "uuid",
  "type": "patient_timeline",
  "content": "# Chronologie du patient\n\n## January 2024\n- Consultation: Hypertension well controlled...",
  "generated_at": "2024-01-15T14:30:00Z"
}
```

### Audit Endpoints

#### GET /audit/logs
Retrieve audit logs with filtering.

**Query Parameters:**
- `user_id`: filter by user
- `action`: filter by action type
- `date_from`: start date
- `date_to`: end date
- `resource_type`: document, query, etc.

**Response:**
```json
{
  "logs": [
    {
      "id": "uuid",
      "timestamp": "2024-01-15T10:30:00Z",
      "user_id": "anon_user_123",
      "action": "document_upload",
      "resource_type": "document",
      "resource_id": "uuid",
      "ip_address": "192.168.1.100"
    }
  ],
  "total": 500
}
```

## Document Ingestor Service (Internal API)

### POST /ingest
Process uploaded document.

**Internal Request Body:**
```json
{
  "document_id": "uuid",
  "file_path": "/data/uploads/file.pdf",
  "metadata": {
    "filename": "report.pdf",
    "mime_type": "application/pdf"
  }
}
```

### GET /ingest/status/{document_id}
Check document processing status.

## DeID Service (Internal API)

### POST /anonymize
Anonymize document content.

**Request Body:**
```json
{
  "document_id": "uuid",
  "content": "Patient John Doe, born 01/01/1980...",
  "language": "fr"
}
```

**Response:**
```json
{
  "anonymized_content": "Patient ANON_PAT_001, born [DATE]...",
  "pii_entities": [
    {
      "type": "PERSON",
      "value": "John Doe",
      "replacement": "ANON_PAT_001",
      "confidence": 0.95
    }
  ]
}
```

## Semantic Indexer Service (Internal API)

### POST /index
Create vector embeddings for document chunks.

**Request Body:**
```json
{
  "document_id": "uuid",
  "chunks": [
    {
      "index": 1,
      "content": "Clinical report content...",
      "metadata": {"page": 1}
    }
  ]
}
```

### POST /search
Perform vector similarity search.

**Request Body:**
```json
{
  "query_embedding": [0.1, 0.2, ...],
  "limit": 10,
  "filters": {"document_type": "medical_report"}
}
```

## LLM QA Service (Internal API)

### POST /generate
Generate answer using LLM.

**Request Body:**
```json
{
  "question": "What is the treatment?",
  "context": "Document content...",
  "model": "llama2:7b-chat",
  "temperature": 0.7
}
```

**Response:**
```json
{
  "answer": "The treatment consists of...",
  "confidence": 0.88,
  "tokens_used": 156
}
```

## Audit Logger Service (Internal API)

### POST /log
Record audit event.

**Request Body:**
```json
{
  "user_id": "anon_user_123",
  "action": "search_query",
  "resource_type": "query",
  "resource_id": "uuid",
  "details": {"query": "hypertension"},
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0..."
}
```

## Error Responses

All endpoints return standardized error responses:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "query",
      "reason": "cannot be empty"
    }
  }
}
```

### Common Error Codes
- `VALIDATION_ERROR`: Invalid request data
- `AUTHENTICATION_ERROR`: Invalid or missing credentials
- `AUTHORIZATION_ERROR`: Insufficient permissions
- `NOT_FOUND`: Resource not found
- `RATE_LIMITED`: Too many requests
- `INTERNAL_ERROR`: Server error

## Rate Limiting

- Search endpoints: 100 requests/minute per user
- Q&A endpoints: 50 requests/minute per user
- Document upload: 20 requests/minute per user

## Pagination

List endpoints support cursor-based pagination:

```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6IjEyMyJ9",
    "has_more": true
  }
}
```

## WebSocket Endpoints

Real-time updates for long-running operations:

### WS /ws/documents/{document_id}
Receive document processing status updates.

### WS /ws/synthesis/{synthesis_id}
Receive synthesis progress updates.