# DocQA-MS DeID Service

Document anonymization service using Presidio and spaCy for PII detection and removal.

## Overview

The DeID service is responsible for automatically detecting and anonymizing personally identifiable information (PII) in medical documents before they are processed by other services. This ensures compliance with privacy regulations like GDPR and HIPAA.

## Features

- **PII Detection**: Uses Presidio to identify various types of personal information
- **French Language Support**: Optimized for French medical documents using spaCy
- **Multiple Entity Types**: Detects names, dates, phone numbers, emails, addresses, etc.
- **Configurable Anonymization**: Customizable replacement strategies
- **Database Integration**: Stores anonymization results and PII mappings
- **RESTful API**: Clean API for integration with other services

## Architecture

```
DeID Service (Port 8002)
├── Presidio Analyzer: Detects PII entities
├── Presidio Anonymizer: Replaces detected PII
├── spaCy Model: French language processing
├── PostgreSQL: Stores anonymization results
└── RabbitMQ: Message queue integration
```

## API Endpoints

### POST /anonymize
Anonymize a single document.

**Request:**
```json
{
  "document_id": "doc-123",
  "content": "Patient Jean Dupont, né le 15/01/1980...",
  "language": "fr"
}
```

**Response:**
```json
{
  "document_id": "doc-123",
  "original_content": "Patient mohamed HB, né le 15/01/1980...",
  "anonymized_content": "Patient ANON_PAT_001, né le [DATE]...",
  "pii_entities": [
    {
      "entity_type": "PERSON",
      "start": 8,
      "end": 20,
      "confidence_score": 0.95,
      "text": "mohamed HB"
    }
  ],
  "processing_time_ms": 150
}
```

### GET /anonymize/status/{document_id}
Check anonymization status for a document.

### POST /deid/batch-anonymize
Anonymize multiple documents in batch.

## Configuration

### Environment Variables

```bash
# Service Configuration
DEID_LANGUAGE=fr
DEID_CONFIDENCE_THRESHOLD=0.5

# SpaCy Configuration
SPACY_MODEL=fr_core_news_sm

# Presidio Configuration
PRESIDIO_ANALYZERS=["PERSON", "LOCATION", "DATE_TIME", "PHONE_NUMBER", "EMAIL_ADDRESS"]

# Database
DATABASE_URL=postgresql://user:password@postgres:5432/docqa_db

# Message Queue
RABBITMQ_URL=amqp://admin:admin@rabbitmq:5672/
```

## Dependencies

- **presidio-analyzer**: PII detection engine
- **presidio-anonymizer**: PII replacement engine
- **spacy**: French language processing
- **fr-core-news-sm**: French spaCy model
- **fastapi**: Web framework
- **psycopg2**: PostgreSQL client

## Database Schema

The service uses these tables:

- `pii_entities`: Detected PII entities
- `anonymization_mappings`: Original → anonymized value mappings
- `document_anonymizations`: Anonymization results

## Health Checks

### GET /health
Comprehensive health check including:
- Database connectivity
- RabbitMQ connectivity
- SpaCy model loading
- Presidio initialization

## Development

### Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download fr_core_news_sm

# Run service
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002
```

### Docker Development

```bash
# Build and run
docker-compose up --build deid

# View logs
docker-compose logs -f deid

# Test health
curl http://localhost:8002/health
```

## Testing

### Unit Tests

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html
```

### Integration Tests

```bash
# Test with other services
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## Performance Considerations

- **Model Loading**: SpaCy model is loaded once at startup
- **Batch Processing**: Supports batch anonymization for efficiency
- **Confidence Thresholds**: Configurable detection sensitivity
- **Caching**: Results cached in database to avoid reprocessing

## Security

- **Data Encryption**: Sensitive data encrypted at rest
- **Access Control**: Service-to-service authentication
- **Audit Logging**: All anonymization operations logged
- **PII Handling**: Secure deletion of original PII mappings

## Monitoring

### Metrics
- Anonymization processing time
- PII detection accuracy
- Service health status
- Error rates

### Logs
- Structured JSON logging
- Error tracking
- Performance monitoring
- Audit trails

## Troubleshooting

### Common Issues

1. **SpaCy Model Not Found**
   ```bash
   python -m spacy download fr_core_news_sm
   ```

2. **Database Connection Failed**
   - Check DATABASE_URL configuration
   - Verify PostgreSQL is running
   - Check network connectivity

3. **Presidio Initialization Failed**
   - Check Python dependencies
   - Verify presidio installation
   - Check available memory

4. **High Memory Usage**
   - Reduce batch size
   - Monitor spaCy model memory
   - Consider model optimization

## API Documentation

Full API documentation available at `/docs` when service is running.

## Contributing

See main project [CONTRIBUTING.md](../../CONTRIBUTING.md) for development guidelines.