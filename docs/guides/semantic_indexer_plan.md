# Plan de Développement - IndexeurSémantique (Semantic Indexer)

## Vue d'ensemble

Le service IndexeurSémantique est responsable de la création d'embeddings vectoriels pour les documents médicaux afin d'activer la recherche sémantique. Il transforme le texte brut en représentations vectorielles qui peuvent être utilisées par le LLM pour retrouver le contexte pertinent.

## Objectifs

- **Créer des embeddings** de haute qualité pour les documents médicaux
- **Stocker les vecteurs** dans une base de données optimisée
- **Fournir une API** de recherche sémantique rapide
- **S'intégrer** parfaitement avec le pipeline DeID → Indexer → LLM-QA

## Architecture Technique

### Technologies Choisies

#### **SentenceTransformers** (Embeddings)
- Modèle: `sentence-transformers/all-MiniLM-L6-v2` (384 dimensions)
- Avantages: Léger, rapide, bonne qualité pour le français médical
- Alternative: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`

#### **FAISS** (Vector Search)
- Index: `IndexFlatIP` (Inner Product pour similarité cosinus)
- Avantages: Ultra-rapide, optimisé pour CPU/GPU
- Persistance: Sauvegarde/chargement automatique des index

#### **PostgreSQL** (Métadonnées)
- Stockage des chunks de texte et métadonnées
- Requêtes SQL pour filtrage avancé
- Intégration avec pgvector (optionnel pour production)

### Flux de Données

```
Document Anonymisé → Chunking → Embedding → Indexation → Recherche
       ↓                ↓          ↓          ↓          ↓
     DeID Service    Texte brut  Vecteurs   FAISS    API REST
```

## Plan de Développement (Phase par Phase)

### Phase 1: Infrastructure de Base (Jour 1-2)

#### 1.1 Configuration du Service
- [ ] Créer la structure de dossiers `backend/indexer_semantique/`
- [ ] Configuration FastAPI avec endpoints de base
- [ ] Intégration avec PostgreSQL et RabbitMQ
- [ ] Configuration Docker et requirements.txt

#### 1.2 Modèle d'Embeddings
- [ ] Installation et test de SentenceTransformers
- [ ] Validation des performances du modèle français
- [ ] Tests de génération d'embeddings

#### 1.3 Base FAISS
- [ ] Configuration de FAISS IndexFlatIP
- [ ] Tests de sauvegarde/chargement d'index
- [ ] Validation des performances de recherche

### Phase 2: Pipeline d'Indexation (Jour 3-4)

#### 2.1 Chunking Intelligent
- [ ] Implémentation du découpage de texte
- [ ] Gestion des chevauchements (overlap)
- [ ] Métadonnées des chunks (page, section, etc.)

#### 2.2 Pipeline d'Embeddings
- [ ] Génération d'embeddings par batch
- [ ] Gestion de la mémoire GPU/CPU
- [ ] Optimisations de performance

#### 2.3 Stockage en Base
- [ ] Sauvegarde des chunks en PostgreSQL
- [ ] Indexation FAISS avec mapping ID
- [ ] Gestion des erreurs et rollback

### Phase 3: API de Recherche (Jour 5-6)

#### 3.1 Recherche Sémantique
- [ ] Endpoint de recherche par similarité
- [ ] Filtrage par document/patient
- [ ] Pagination et scoring

#### 3.2 Recherche Hybride
- [ ] Combinaison recherche sémantique + mots-clés
- [ ] Scoring pondéré
- [ ] Optimisations de performance

#### 3.3 Intégration RabbitMQ
- [ ] Réception des documents depuis DeID
- [ ] File d'attente pour l'indexation
- [ ] Notifications de progression

### Phase 4: Optimisations et Tests (Jour 7-8)

#### 4.1 Optimisations Performance
- [ ] Batch processing pour gros volumes
- [ ] Cache des embeddings fréquents
- [ ] Optimisation mémoire

#### 4.2 Tests et Validation
- [ ] Tests unitaires complets
- [ ] Tests d'intégration avec DeID
- [ ] Tests de performance et charge

#### 4.3 Monitoring et Logging
- [ ] Métriques de performance
- [ ] Logs détaillés pour debugging
- [ ] Health checks complets

## API Endpoints Prévu

### POST /index
Indexe un document et ses chunks.

**Request:**
```json
{
  "document_id": "doc-123",
  "chunks": [
    {
      "index": 1,
      "content": "Le patient présente une hypertension...",
      "metadata": {"page": 1, "section": "clinical_report"}
    }
  ]
}
```

### POST /search
Recherche sémantique dans les documents.

**Request:**
```json
{
  "query": "traitement hypertension",
  "filters": {
    "document_type": "medical_report",
    "patient_id": "ANON_PAT_001"
  },
  "limit": 10
}
```

**Response:**
```json
{
  "results": [
    {
      "document_id": "doc-123",
      "chunk_id": 1,
      "score": 0.87,
      "content": "Le patient présente une hypertension...",
      "metadata": {"page": 1}
    }
  ]
}
```

### GET /status/{document_id}
Vérifie le statut d'indexation d'un document.

## Métriques de Performance Cibles

- **Temps d'indexation**: < 30s pour un document de 10 pages
- **Temps de recherche**: < 100ms pour une requête
- **Précision**: > 85% de résultats pertinents
- **Rappel**: > 90% de documents pertinents retrouvés

## Gestion des Erreurs

### Erreurs Prévisibles
1. **Modèle d'embeddings non disponible**
   - Solution: Fallback vers modèle plus léger
   - Logging: Alerte monitoring

2. **Mémoire insuffisante**
   - Solution: Traitement par batch plus petits
   - Logging: Métriques d'utilisation mémoire

3. **Index FAISS corrompu**
   - Solution: Reconstruction automatique
   - Logging: Backup et recovery

## Tests d'Intégration

### Pipeline Complet
```
1. Upload document → DocIngestor
2. Anonymisation → DeID
3. Indexation → Semantic Indexer ← TEST CE POINT
4. Recherche → LLM-QA
```

### Jeux de Test
- Documents médicaux français (comptes-rendus, prescriptions)
- Requêtes médicales variées
- Tests de performance avec gros volumes

## Déploiement et Production

### Configuration Production
- GPU support pour accélérer les embeddings
- Index FAISS persisté sur disque
- Cache Redis pour les requêtes fréquentes
- Monitoring Prometheus/Grafana

### Scaling
- Service stateless (sauf index FAISS)
- Possibilité de réplication
- Load balancing pour les recherches

## Risques et Mitigation

### Risques Techniques
1. **Performance des embeddings**: Solution - Optimisation et cache
2. **Précision sémantique**: Solution - Fine-tuning du modèle
3. **Volume de données**: Solution - Indexation incrémentale

### Risques Projet
1. **Délais serrés**: Solution - Développement itératif
2. **Intégration complexe**: Solution - Tests d'intégration précoces
3. **Performance insuffisante**: Solution - Benchmarks réguliers

## Livrables

### Code
- Service FastAPI complet
- Tests unitaires et d'intégration
- Documentation API
- Scripts de déploiement

### Documentation
- Guide d'utilisation
- Architecture technique
- Procédures de maintenance
- Métriques de monitoring

### Tests
- Suite de tests automatisés
- Jeux de données de test
- Benchmarks de performance
- Scripts de validation

## Planning Détaillé

### Semaine 1: Infrastructure
- Jour 1: Setup et configuration de base
- Jour 2: Intégration SentenceTransformers + FAISS
- Jour 3: Pipeline d'indexation basique
- Jour 4: Tests et debugging

### Semaine 2: Features Avancées
- Jour 5: API de recherche complète
- Jour 6: Intégration RabbitMQ
- Jour 7: Optimisations et tests
- Jour 8: Documentation et déploiement

Ce plan assure une implémentation robuste et performante du service d'indexation sémantique, parfaitement intégré dans l'architecture DocQA-MS.