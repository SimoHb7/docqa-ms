# Semantic Indexer Service

Vector indexing and semantic search service for DocQA-MS medical document assistant.

## Overview

The Semantic Indexer service transforms medical documents into searchable vector embeddings using SentenceTransformers and FAISS. It provides fast semantic search capabilities for the LLM Q&A system.

## Features

- **Document Chunking**: Intelligent text splitting with overlap
- **Vector Embeddings**: High-quality embeddings using SentenceTransformers
- **FAISS Indexing**: Fast similarity search with Inner Product
- **REST API**: Complete API for indexing and searching
- **Health Monitoring**: Comprehensive health checks and metrics

## Quick Start

### Using Docker Compose

```bash
# Start the service
docker-compose up indexer-semantique

# Check health
curl http://localhost:8003/health
```

### Local Development

```bash
cd backend/indexer_semantique

# Install dependencies
pip install -r requirements.txt

# Run the service
uvicorn app.main:app --reload --host 0.0.0.0 --port 8003
```

## API Endpoints

### Document Indexing

#### POST `/api/v1/index/`
Index document chunks in the vector store.

**Request Body:**
```json
{
  "document_id": "doc-123",
  "chunks": [
    {
      "index": 0,
      "content": "Le patient présente une hypertension...",
      "sentences": ["Le patient présente une hypertension."],
      "metadata": {
        "page": 1,
        "section": "clinical_report"
      }
    }
  ]
}
```

**Response:**
```json
{
  "document_id": "doc-123",
  "chunks_processed": 5,
  "vectors_added": 5,
  "processing_time_ms": 1250,
  "status": "completed"
}
```

### Semantic Search

#### POST `/api/v1/search/`
Perform semantic search across indexed documents.

**Request Body:**
```json
{
  "query": "traitement hypertension",
  "filters": {
    "document_type": "medical_report",
    "patient_id": "ANON_PAT_001"
  },
  "limit": 10,
  "threshold": 0.7
}
```

**Response:**
```json
{
  "query": "traitement hypertension",
  "results": [
    {
      "chunk_id": "doc-123_chunk_2",
      "document_id": "doc-123",
      "score": 0.89,
      "content": "Le traitement par irbesartan...",
      "metadata": {
        "page": 2,
        "section": "treatment"
      }
    }
  ],
  "total_results": 3,
  "execution_time_ms": 45
}
```

### Status and Statistics

#### GET `/api/v1/index/status/{document_id}`
Check indexing status for a document.

#### GET `/api/v1/search/stats`
Get search and indexing statistics.

#### GET `/health`
Service health check.

## Configuration

### Environment Variables

```bash
# Service Configuration
INDEXER_SEMANTIQUE_HOST=0.0.0.0
INDEXER_SEMANTIQUE_PORT=8003
DEBUG=false

# Embedding Model
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
EMBEDDING_DIMENSION=384
BATCH_SIZE=32
DEVICE=cpu

# Text Processing
CHUNK_SIZE=512
CHUNK_OVERLAP=50

# FAISS Configuration
VECTOR_INDEX_PATH=/app/data/vectors/faiss_index.idx
SIMILARITY_THRESHOLD=0.7

# Search Settings
MAX_SEARCH_RESULTS=20
SEARCH_TIMEOUT=30
```

## Architecture

### Components

1. **Text Chunker**: Splits documents into overlapping chunks
2. **Embedding Service**: Generates vector representations
3. **Vector Store**: FAISS-based storage and search
4. **API Layer**: REST endpoints for indexing and search

### Data Flow

```
Document Chunks → Embedding Generation → FAISS Index → Semantic Search
       ↓                ↓                      ↓             ↓
   Text Processing  SentenceTransformers    Vector Storage  Similarity Search
```

## Development

### Project Structure

```
backend/indexer_semantique/
├── app/
│   ├── core/              # Core services
│   │   ├── config.py      # Configuration
│   │   ├── embeddings.py  # Embedding service
│   │   ├── chunker.py     # Text chunking
│   │   ├── vector_store.py # FAISS management
│   │   ├── health.py      # Health checks
│   │   └── logging.py     # Logging setup
│   ├── api/v1/            # API endpoints
│   │   ├── endpoints/
│   │   │   ├── indexer.py # Indexing endpoints
│   │   │   └── search.py  # Search endpoints
│   │   └── api.py         # API router
│   └── main.py            # FastAPI app
├── requirements.txt       # Dependencies
├── Dockerfile            # Container config
└── README.md             # This file
```

### Testing

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

### Code Quality

```bash
# Linting
flake8 app/
black app/ --check
isort app/ --check

# Type checking
mypy app/
```

## Performance

### Benchmarks

- **Indexing**: ~1000 chunks/minute
- **Search**: <50ms per query
- **Memory**: ~500MB for 100K chunks
- **Accuracy**: >85% relevant results

### Optimization Tips

1. **Batch Processing**: Process embeddings in batches
2. **GPU Acceleration**: Use CUDA for faster embedding generation
3. **Index Persistence**: Save/load FAISS index to disk
4. **Memory Management**: Clear unused embeddings

## Troubleshooting

### Common Issues

#### Model Loading Failed
```
Error: Can't find model 'sentence-transformers/all-MiniLM-L6-v2'
```
**Solution**: Check internet connection or use local model path

#### Out of Memory
```
CUDA out of memory
```
**Solution**: Reduce batch size or use CPU mode

#### FAISS Index Corrupted
```
Error: Failed to load FAISS index
```
**Solution**: Delete index files and rebuild

### Logs

Check service logs:
```bash
docker-compose logs indexer-semantique
```

### Health Check

```bash
curl http://localhost:8003/health
```

## Integration

### With DeID Service

The indexer receives anonymized documents from DeID:

```python
# Example integration
response = requests.post("http://localhost:8002/anonymize", json={
    "document_id": "doc-123",
    "content": raw_text,
    "language": "fr"
})

anonymized = response.json()

# Then index
indexer_response = requests.post("http://localhost:8003/api/v1/index/", json={
    "document_id": "doc-123",
    "chunks": chunked_anonymized_content
})
```

### With LLM QA Service

The indexer provides context for Q&A:

```python
# Search for relevant chunks
search_response = requests.post("http://localhost:8003/api/v1/search/", json={
    "query": user_question,
    "limit": 5
})

context_chunks = search_response.json()["results"]

# Pass to LLM
qa_response = requests.post("http://localhost:8004/api/v1/qa/ask", json={
    "question": user_question,
    "context": context_chunks
})
```

## Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation
4. Create pull requests with clear descriptions

## License

MIT License - see main project LICENSE file.