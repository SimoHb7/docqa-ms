# DocQA-MS — Assistant médical sur documents cliniques (LLM + microservices)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![React](https://img.shields.io/badge/react-18+-61dafb.svg)](https://reactjs.org/)

Un assistant intelligent basé sur des microservices et des LLMs pour l'interrogation en langage naturel de documents cliniques, garantissant confidentialité et traçabilité.

## 🎯 Objectif

Permettre aux professionnels de santé d'interroger efficacement les vastes corpus de documents cliniques non structurés (comptes-rendus, ordonnances, résultats de laboratoire, etc.) via des requêtes en langage naturel, tout en assurant la sécurité des données sensibles.

## 🏗️ Architecture

Le système repose sur une architecture microservices modulaire composée de 7 services principaux :

- **DocIngestor**: Ingestion sécurisée de documents (PDF, DOCX, TXT, HL7, FHIR)
- **DeID**: Anonymisation automatique des données personnelles
- **IndexeurSémantique**: Recherche vectorielle sémantique
- **LLMQAModule**: Question-Réponse avec LLM (GPT-4/Llama)
- **SyntheseComparative**: Synthèses et comparaisons inter-patients
- **AuditLogger**: Traçabilité complète des interactions
- **InterfaceClinique**: Interface web utilisateur (React)

## 🚀 Démarrage rapide

### Prérequis

- Docker & Docker Compose
- Python 3.9+
- Node.js 16+
- PostgreSQL (optionnel pour développement local)

### Installation

1. **Cloner le repository**
   ```bash
   git clone https://github.com/your-org/docqa-ms.git
   cd docqa-ms
   ```

2. **Configuration**
   ```bash
   cp .env.example .env
   # Éditer .env avec vos paramètres
   ```

3. **Lancement avec Docker Compose**
   ```bash
   docker-compose up -d
   ```

4. **Accès à l'application**
   - Interface web: http://localhost:3000
   - API Gateway: http://localhost:8000
   - Documentation API: http://localhost:8000/docs

## 📚 Documentation

- [Architecture système](docs/architecture/system_architecture.md)
- [Guide d'installation](docs/guides/setup_guide.md)
- [Guide de déploiement](docs/guides/deployment_guide.md)
- [API Documentation](docs/api/)
- [Résolution de problèmes](docs/guides/troubleshooting.md)

## 🛠️ Technologies

### Backend
- **Framework**: FastAPI, Python
- **Base de données**: PostgreSQL
- **Message Queue**: RabbitMQ
- **Vector Store**: FAISS/ChromaDB
- **LLM**: LangChain, LlamaIndex, Ollama

### Frontend
- **Framework**: React 18+
- **Styling**: Tailwind CSS
- **Authentification**: Auth0
- **Charts**: Chart.js

### Infrastructure
- **Conteneurisation**: Docker
- **Orchestration**: Kubernetes (production)
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana

## 🔒 Sécurité & Conformité

- **Anonymisation automatique** des données personnelles (PII)
- **Chiffrement end-to-end** des données sensibles
- **Audit trail complet** de toutes les interactions
- **Authentification robuste** avec Auth0
- **Conformité RGPD/HIPAA** pour données médicales

## 🤝 Contribution

Voir [CONTRIBUTING.md](CONTRIBUTING.md) pour les guidelines de contribution.

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👥 Auteurs

- **Pr. Oumayma OUEDRHIRI** (O.ouedrhiri@emsi.ma)
- **Pr. Hiba TABBAA** (H.Tabbaa@emsi.ma)
- **Pr. Mohamed LACHGAR** (lachgar.m@gmail.com)

## 📞 Support

Pour toute question ou problème, créez une [issue](https://github.com/your-org/docqa-ms/issues) sur GitHub.