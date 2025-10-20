# Organisation de l'équipe - DocQA-MS

## Vue d'ensemble

Ce document décrit comment organiser le travail collaboratif sur DocQA-MS entre collègues pour une efficacité maximale.

## Structure de l'équipe

### Composition de l'équipe DocQA-MS

#### **1️⃣ EL-BELAIDI - Tech Lead & Backend Infrastructure**
**Responsabilités principales :**
- Architecture globale du système
- Configuration Docker & DevOps
- API Gateway centrale
- Gestion base de données PostgreSQL
- Service d'ingestion de documents (DocIngestor)

**Outils de travail :**
- VS Code + Docker Desktop
- PostgreSQL + pgAdmin
- FastAPI + Python 3.11
- Postman (tests API)

**Livrables clés :**
- Infrastructure Docker complète
- API d'upload fonctionnelle
- Base de données opérationnelle
- Documentation technique

#### **2️⃣ LAHBARI - AI/ML Specialist**
**Responsabilités principales :**
- Intégration du LLM (Ollama/Llama)
- Module de Question-Réponse
- Anonymisation de documents (Presidio)
- Prompt engineering
- Synthèse comparative (optionnel)

**Outils de travail :**
- Ollama + Llama 3.1
- LangChain
- Presidio + spaCy
- Python + Jupyter Notebook (prototypage)

**Livrables clés :**
- Service LLM QA fonctionnel
- Module d'anonymisation
- Bibliothèque de prompts optimisés
- Documentation des modèles

#### **3️⃣ ELMANSOR - Data Engineer**
**Responsabilités principales :**
- Recherche sémantique (embeddings)
- ChromaDB / Base vectorielle
- Service d'indexation
- Optimisation des performances
- Pipeline de traitement de données

**Outils de travail :**
- ChromaDB
- Sentence-Transformers
- FAISS (backup)
- Python + FastAPI

**Livrables clés :**
- Service d'indexation vectorielle
- API de recherche sémantique
- Optimisation des embeddings
- Métriques de performance

#### **4️⃣ [À définir] - Full Stack Developer**
**Responsabilités principales :**
- Interface utilisateur (React)
- Intégration frontend-backend
- Service d'audit (logs)
- Déploiement et CI/CD
- Tests end-to-end

**Outils de travail :**
- React + Vite + Tailwind CSS
- Figma (design)
- GitHub Actions
- Vercel / Railway

**Livrables clés :**
- Interface web complète
- Dashboard d'administration
- Module d'audit fonctionnel
- Application déployée

## Répartition des tâches

### Phase 1: Architecture & Setup (Semaine 1-2)
**Statut: ✅ TERMINÉ**

- [x] Analyse des exigences
- [x] Conception de l'architecture
- [x] Configuration du repository Git
- [x] Setup Docker et base de données
- [x] Documentation initiale

**Responsable**: Toute l'équipe

### Phase 2: Développement Core (Semaine 3-8)

#### Sprint 1 (Semaine 3-4): Infrastructure Backend - EL-BELAIDI
```
API Gateway:
├── Routing et middleware FastAPI
├── Authentification JWT/Auth0
├── Rate limiting et sécurité
└── Gestion d'erreurs unifiée

Base de données PostgreSQL:
├── Implémentation du schéma SQL
├── Migrations et seed data
├── Connexions et sessions
└── Optimisations de performance

DocIngestor Service:
├── Upload et validation de fichiers
├── Extraction de texte (PDF, DOCX)
├── OCR pour images scannées avec Tesseract
└── Métadonnées et indexation
```

#### Sprint 2 (Semaine 5-6): Services IA - LAHBARI
```
DeID Service (Anonymisation):
├── Détection PII avec spaCy/Presidio
├── Anonymisation automatique des documents
├── Validation et tests des patterns PII
└── Génération données synthétiques pour tests

LLM QA Module:
├── Intégration Ollama/Llama 3.1
├── Module de Question-Réponse avec LangChain
├── Templates de prompts médicaux spécialisés
└── Gestion GPU/CPU pour inférence
```

#### Sprint 3 (Semaine 7-8): Data & Analytics - ELMANSOR + LAHBARI
```
Semantic Indexer (ELMANSOR):
├── Embeddings avec SentenceTransformers
├── Indexation ChromaDB/FAISS
├── Chunking intelligent du texte médical
└── Recherche vectorielle optimisée

Comparative Synthesis (LAHBARI):
├── Génération de synthèses médicales
├── Comparaisons inter-patients
├── Templates de rapports structurés
└── Export et formatage PDF/JSON
```

### Phase 3: Frontend & Intégration (Semaine 9-12)

#### Sprint 4 (Semaine 9-10): Core Frontend - [Membre 4]
```
Interface de recherche:
├── Barre de recherche sémantique avec React
├── Filtres avancés (date, type, patient)
├── Affichage des résultats avec Tailwind CSS
└── Pagination et tri optimisés

Gestion des documents:
├── Upload avec drag & drop (React Dropzone)
├── Liste et visualisation des documents
├── Statuts de traitement en temps réel
└── Téléchargement et partage sécurisé
```

#### Sprint 5 (Semaine 11-12): Features Avancées - [Membre 4]
```
Q&A Interface:
├── Chatbot médical intégré
├── Historique des conversations persisté
├── Citations et sources des réponses
└── Export des réponses (PDF/JSON)

Dashboard Admin & Audit:
├── Métriques d'utilisation en temps réel
├── Logs d'audit avec filtres avancés
├── Gestion des utilisateurs (si Auth0)
└── Monitoring système et alertes

Service d'audit (Backend):
├── Traçabilité complète des actions
├── Logs structurés pour conformité
├── Métriques de performance
└── Intégration RGPD/HIPAA
```

### Phase 4: Testing & Déploiement (Semaine 13-14)

#### Sprint 6 (Semaine 13-14): Finalisation
```
Tests & QA (Toute l'équipe):
├── Tests unitaires et d'intégration
├── Tests end-to-end
├── Tests de sécurité
└── Tests de performance

Déploiement (Personne H):
├── Configuration production
├── CI/CD complet
├── Monitoring et alerting
└── Documentation de déploiement
```

## Workflow quotidien

### Stand-up meeting (15 min chaque matin)
- **Hier**: Ce qui a été fait
- **Aujourd'hui**: Objectifs de la journée
- **Blocages**: Problèmes rencontrés

### Communication
- **GitHub Issues**: Pour les tâches et bugs
- **Pull Requests**: Pour les code reviews
- **Discord/Slack**: Pour la communication rapide
- **Documents partagés**: Pour l'architecture et les décisions

### Points de synchronisation
- **Fin de sprint**: Revue des accomplissements
- **Code reviews**: Validation qualité du code
- **Merge dans develop**: Intégration continue

## Branches et collaboration

### Structure des branches
```
main (protégé) ← develop ← feature/*
                    ← bugfix/*
                    ← hotfix/*
```

### Responsabilités par branche
```
feature/api-gateway-*       → EL-BELAIDI
feature/doc-ingestor-*      → EL-BELAIDI
feature/database-*          → EL-BELAIDI
feature/docker-*            → EL-BELAIDI
feature/infra-*             → EL-BELAIDI

feature/deid-*              → LAHBARI
feature/llm-*               → LAHBARI
feature/synthesis-*         → LAHBARI
feature/prompt-*            → LAHBARI
feature/ollama-*            → LAHBARI

feature/indexer-*           → ELMANSOR
feature/chromadb-*          → ELMANSOR
feature/embeddings-*        → ELMANSOR
feature/vector-search-*     → ELMANSOR
feature/performance-*       → ELMANSOR

feature/frontend-*          → [Membre 4]
feature/ui-*                → [Membre 4]
feature/audit-logs-*        → [Membre 4]
feature/admin-*             → [Membre 4]
feature/deployment-*        → [Membre 4]
```

## Outils et environnements

### Environnements de développement
- **Local**: Docker Compose pour développement
- **Staging**: Environnement de test partagé
- **Production**: Déploiement final

### Outils obligatoires
- **Git**: Contrôle de version
- **Docker**: Conteneurisation
- **VS Code**: Éditeur recommandé
- **GitHub**: Repository et collaboration

### Outils recommandés
- **Postman/Insomnia**: Test des APIs
- **pgAdmin/DBeaver**: Gestion base de données
- **Draw.io/Mermaid**: Diagrammes
- **Notion/Miro**: Documentation et brainstorming

## Gestion des risques

### Risques identifiés
1. **Complexité technique**: Microservices + IA
2. **Coordination équipe**: 8 personnes sur 14 semaines
3. **Dépendances externes**: APIs LLM, Auth0
4. **Conformité médicale**: RGPD, données sensibles

### Mitigation
- **Réunions régulières**: Stand-ups quotidiens
- **Documentation**: Tout documenté et versionné
- **Code reviews**: Qualité assurée par pairs
- **Tests automatisés**: CI/CD pour validation
- **Planning buffer**: 2 semaines pour imprévus

## Métriques de succès

### Qualité du code
- **Coverage tests**: > 80%
- **Code reviews**: 100% des PRs
- **Linting**: 0 erreurs
- **Performance**: < 2s réponse API

### Avancement projet
- **Tâches complétées**: Suivi GitHub Issues
- **Branches actives**: < 10 simultanées
- **Merges quotidiens**: Intégration continue
- **Documentation**: Mise à jour régulière

### Satisfaction équipe
- **Communication**: Feedback hebdomadaire
- **Charge de travail**: Équilibrée entre membres
- **Apprentissage**: Nouvelles compétences acquises
- **Motivation**: Objectifs clairs et atteignables

## Planning détaillé

### Semaine 1-2: Setup ✅
- [x] Repository GitHub créé
- [x] Branches main/develop configurées
- [x] Architecture validée
- [x] Docker Compose fonctionnel
- [x] Documentation initiale

### Semaine 3-4: Backend Core
- [ ] API Gateway implémenté
- [ ] Base de données configurée
- [ ] DocIngestor opérationnel
- [ ] Tests unitaires backend

### Semaine 5-6: IA Services
- [ ] DeID opérationnel
- [ ] Indexation sémantique
- [ ] Recherche vectorielle
- [ ] Intégration tests

### Semaine 7-8: LLM & Analytics
- [ ] Module Q&A fonctionnel
- [ ] Synthèse comparative
- [ ] Audit logging complet
- [ ] Performance optimisée

### Semaine 9-10: Frontend Core
- [ ] Interface de recherche
- [ ] Gestion des documents
- [ ] Design responsive
- [ ] Intégration API

### Semaine 11-12: Features Avancées
- [ ] Chatbot Q&A
- [ ] Dashboard admin
- [ ] Monitoring utilisateur
- [ ] Tests end-to-end

### Semaine 13-14: Finalisation
- [ ] Tests complets
- [ ] Déploiement production
- [ ] Documentation finale
- [ ] Présentation projet

## Contacts d'urgence

### Professeurs référents
- **Pr. Oumayma OUEDRHIRI**: O.ouedrhiri@emsi.ma
- **Pr. Hiba TABBAA**: H.Tabbaa@emsi.ma
- **Pr. Mohamed LACHGAR**: lachgar.m@gmail.com

### Chef de projet
- **Nom**: [À définir]
- **Rôle**: Coordination et support

---

*Ce document sera mis à jour régulièrement selon l'avancement du projet.*