# Changelog - DocQA-MS

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project structure and architecture
- Microservices architecture with 7 core services:
  - API Gateway (FastAPI)
  - Document Ingestor (Python + Tika + OCR)
  - DeID Service (spaCy + Presidio)
  - Semantic Indexer (SentenceTransformers + FAISS)
  - LLM QA Module (LangChain + Ollama)
  - Comparative Synthesis (Transformers)
  - Audit Logger (PostgreSQL)
- React frontend with Tailwind CSS
- Docker Compose configuration for development
- PostgreSQL database schema with medical data models
- RabbitMQ for inter-service communication
- Comprehensive API documentation
- GitHub Actions CI/CD pipelines
- Security and compliance features (PII anonymization, audit trails)
- Development and deployment guides

### Infrastructure
- Docker containerization for all services
- Kubernetes deployment manifests (planned)
- Monitoring setup with Prometheus/Grafana (planned)
- CI/CD with automated testing and deployment

### Documentation
- System architecture documentation with Mermaid diagrams
- API endpoint specifications
- Setup and deployment guides
- Contributing guidelines
- Security and compliance documentation

## [0.1.0] - 2024-01-XX

### Planned for Initial Release
- Basic document upload and processing
- Simple text search functionality
- User authentication (Auth0 integration)
- Basic audit logging
- Docker Compose deployment
- Unit and integration tests
- API documentation

### Known Issues
- LLM integration requires external API keys or local Ollama setup
- GPU support for LLM inference (optional)
- Advanced anonymization features in development
- Frontend components partially implemented

---

## Types of changes
- `Added` for new features
- `Changed` for changes in existing functionality
- `Deprecated` for soon-to-be removed features
- `Removed` for now removed features
- `Fixed` for any bug fixes
- `Security` in case of vulnerabilities

## Versioning
This project uses [Semantic Versioning](https://semver.org/):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

## Development Status
- **Phase 1** (Current): Architecture and infrastructure setup ✅
- **Phase 2**: Core microservices implementation (In Progress)
- **Phase 3**: Advanced features and optimization
- **Phase 4**: Production deployment and monitoring

---
