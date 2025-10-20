# Guide d'installation et de configuration - DocQA-MS

## Prérequis

Avant de commencer, assurez-vous d'avoir installé :

- **Docker & Docker Compose** (version 3.8+)
- **Git** pour le contrôle de version
- **Python 3.9+** (optionnel pour développement local)
- **Node.js 16+** (optionnel pour développement frontend)
- **GitHub account** pour la collaboration

## 1. Clonage du repository

```bash
# Cloner le repository
git clone https://github.com/votre-username/docqa-ms.git
cd docqa-ms

# Créer et basculer vers la branche develop
git checkout -b develop
git push -u origin develop
```

## 2. Configuration de l'environnement

```bash
# Copier le fichier d'exemple d'environnement
cp .env.example .env

# Éditer le fichier .env avec vos paramètres
nano .env  # ou utiliser votre éditeur préféré
```

### Variables d'environnement importantes

```bash
# Base de données
DATABASE_URL=postgresql://user:password@localhost:5432/docqa_db

# Message Queue
RABBITMQ_URL=amqp://admin:admin@localhost:5672/

# LLM (choisir une option)
OLLAMA_BASE_URL=http://localhost:11434
# ou
OPENAI_API_KEY=votre_clé_openai

# Authentification (optionnel)
AUTH0_DOMAIN=votre-domaine.auth0.com
AUTH0_CLIENT_ID=votre_client_id
```

## 3. Lancement avec Docker Compose

```bash
# Construire et lancer tous les services
docker-compose up -d

# Vérifier que tous les services sont démarrés
docker-compose ps

# Voir les logs
docker-compose logs -f
```

### Services disponibles

- **Frontend**: http://localhost:3000
- **API Gateway**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **RabbitMQ Management**: http://localhost:15672 (admin/admin)
- **pgAdmin** (si configuré): http://localhost:5050

## 4. Initialisation de la base de données

```bash
# Attendre que PostgreSQL soit prêt
docker-compose exec postgres pg_isready -U user -d docqa_db

# Les tables et données de test sont automatiquement créées via docker-compose
# Vérifier que les données sont bien insérées
docker-compose exec postgres psql -U user -d docqa_db -c "SELECT COUNT(*) FROM documents;"
```

## 5. Test de l'installation

### Test du frontend
1. Ouvrir http://localhost:3000
2. Vérifier que l'interface se charge correctement

### Test de l'API
```bash
# Test de santé de l'API Gateway
curl http://localhost:8000/health

# Test de la documentation API
curl http://localhost:8000/docs
```

### Test d'upload de document
```bash
# Utiliser curl pour uploader un document de test
curl -X POST \
  http://localhost:8000/documents/upload \
  -F "file=@data/test_documents/sample_medical_report_1.pdf"
```

## 6. Développement local (optionnel)

### Backend - Python
```bash
# Installer les dépendances Python
cd backend
pip install -r requirements.txt

# Lancer un service spécifique en mode développement
cd api_gateway
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend - React
```bash
# Installer les dépendances Node.js
cd frontend
npm install

# Lancer le serveur de développement
npm start
```

## 7. Configuration Git pour la collaboration

### Branches principales
```
main          # Code de production (protégé)
develop       # Intégration continue
feature/*     # Nouvelles fonctionnalités
bugfix/*      # Corrections de bugs
hotfix/*      # Corrections urgentes
```

### Workflow Git recommandé

```bash
# 1. Créer une branche pour votre travail
git checkout develop
git pull origin develop
git checkout -b feature/ma-fonctionnalite

# 2. Commiter régulièrement
git add .
git commit -m "feat: ajouter la fonctionnalité X"

# 3. Pousser votre branche
git push -u origin feature/ma-fonctionnalite

# 4. Créer une Pull Request sur GitHub
# Aller sur GitHub et créer une PR vers develop
```

## 8. Tests et qualité du code

### Tests automatisés
```bash
# Tests backend
docker-compose exec api-gateway pytest

# Tests frontend
cd frontend && npm test

# Tests d'intégration
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Linting et formatage
```bash
# Backend
black backend/
flake8 backend/
mypy backend/

# Frontend
cd frontend
npm run lint
npm run format
```

## 9. Déploiement en production

### Préparation
```bash
# Build des images
docker-compose -f docker-compose.prod.yml build

# Test en staging
docker-compose -f docker-compose.staging.yml up -d

# Déploiement en production
docker-compose -f docker-compose.prod.yml up -d
```

### Variables d'environnement production
- Utiliser des secrets GitHub Actions
- Configurer des certificats SSL
- Activer l'authentification Auth0
- Configurer le monitoring (Prometheus/Grafana)

## 10. Résolution des problèmes courants

### Service qui ne démarre pas
```bash
# Vérifier les logs
docker-compose logs <nom-du-service>

# Redémarrer un service
docker-compose restart <nom-du-service>
```

### Problèmes de base de données
```bash
# Réinitialiser la base de données
docker-compose down -v
docker-compose up -d postgres
docker-compose exec postgres psql -U user -d docqa_db -f /docker-entrypoint-initdb.d/01-schema.sql
```

### Problèmes de mémoire GPU
```bash
# Ajuster la configuration GPU dans .env
GPU_MEMORY_FRACTION=0.7
CUDA_VISIBLE_DEVICES=0
```

## 11. Support et documentation

- **Documentation API**: `/docs/api/api_endpoints.md`
- **Architecture**: `/docs/architecture/system_architecture.md`
- **Résolution de problèmes**: `/docs/guides/troubleshooting.md`
- **Issues GitHub**: Pour signaler des bugs ou demander des features

## 12. Checklist post-installation

- [ ] Repository cloné et branches configurées
- [ ] Environnement configuré (.env)
- [ ] Services Docker démarrés
- [ ] Base de données initialisée
- [ ] Frontend accessible
- [ ] API fonctionnelle
- [ ] Tests passent
- [ ] Documentation lue
- [ ] Équipe briefée sur les responsabilités