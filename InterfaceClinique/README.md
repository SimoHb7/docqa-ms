# InterfaceClinique

Une application web professionnelle de Q&R (Questions & Réponses) sur documents médicaux, construite avec React, TypeScript et Material-UI.

## 🚀 Fonctionnalités

### ✅ Implémenté
- **Authentification Auth0** - Connexion sécurisée avec gestion des rôles
- **Tableau de bord** - Vue d'ensemble avec statistiques et métriques
- **Gestion des documents** - Upload, visualisation et gestion des documents médicaux
- **Recherche sémantique** - Recherche intelligente dans les documents avec IA
- **Q&R Médical** - Chat interactif pour poser des questions sur les documents
- **Synthèses médicales** - Génération de rapports et chronologies patient
- **Logs d'audit** - Traçabilité complète des actions utilisateur
- **Paramètres utilisateur** - Gestion du profil et préférences
- **Interface responsive** - Design adaptatif pour tous les appareils
- **Thème sombre/clair** - Support des thèmes avec mode système
- **Notifications en temps réel** - Mises à jour et alertes
- **Architecture modulaire** - Code organisé et maintenable

### 🔄 En développement
- Export et reporting avancés
- Visualisations de données avec Chart.js
- Notifications push
- Intégration WebSocket pour mises à jour temps réel
- Tests unitaires et d'intégration

## 🛠️ Technologies

### Frontend
- **React 19** - Framework UI moderne
- **TypeScript** - Typage statique
- **Vite** - Build tool ultra-rapide
- **Material-UI (MUI)** - Composants UI professionnels
- **Tailwind CSS** - Utilitaires CSS
- **React Router** - Navigation
- **TanStack Query** - Gestion d'état serveur
- **Zustand** - Gestion d'état client
- **Auth0** - Authentification
- **Axios** - Client HTTP
- **React Hook Form** - Gestion des formulaires
- **Framer Motion** - Animations
- **React Dropzone** - Upload de fichiers
- **Chart.js** - Graphiques et visualisations

### Backend (Intégré)
- **FastAPI** - API RESTful
- **PostgreSQL** - Base de données
- **Redis** - Cache et sessions
- **Elasticsearch** - Recherche sémantique
- **Docker** - Conteneurisation

## 📁 Structure du projet

```
InterfaceClinique/
├── public/                 # Assets statiques
├── src/
│   ├── components/         # Composants réutilisables
│   │   ├── layout/        # Layout et navigation
│   │   └── ui/            # Composants UI de base
│   ├── pages/             # Pages de l'application
│   ├── services/          # Services API et utilitaires
│   ├── store/             # Gestion d'état (Zustand)
│   ├── types/             # Types TypeScript
│   ├── utils/             # Utilitaires
│   ├── hooks/             # Hooks personnalisés
│   └── assets/            # Assets (images, icônes)
├── tests/                 # Tests
├── docs/                  # Documentation
└── dist/                  # Build output
```

## 🚀 Démarrage rapide

### Prérequis
- Node.js 18+
- npm ou yarn
- Backend DocQA-MS en cours d'exécution

### Installation

1. **Cloner le repository**
   ```bash
   git clone <repository-url>
   cd InterfaceClinique
   ```

2. **Installer les dépendances**
   ```bash
   npm install
   ```

3. **Configuration**
   ```bash
   cp .env.example .env
   # Éditer .env avec vos valeurs Auth0 et API
   ```

4. **Démarrer en développement**
   ```bash
   npm run dev
   ```

5. **Build pour la production**
   ```bash
   npm run build
   npm run preview
   ```

## 🔧 Configuration

### Variables d'environnement (.env)

```env
# API Configuration
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=30000

# Auth0 Configuration
VITE_AUTH0_DOMAIN=your-domain.auth0.com
VITE_AUTH0_CLIENT_ID=your-client-id
VITE_AUTH0_AUDIENCE=https://api.interfaceclinique.com

# Application Configuration
VITE_APP_NAME=InterfaceClinique
VITE_APP_VERSION=1.0.0
VITE_APP_ENV=development
```

### Auth0 Setup

1. Créer une application SPA dans Auth0
2. Configurer les URLs de callback et logout
3. Ajouter les permissions nécessaires
4. Configurer les rôles utilisateur

## 📱 Fonctionnalités principales

### 🔐 Authentification
- Connexion via Auth0
- Gestion des rôles (Admin, Médecin, Chercheur, Qualité)
- Sessions sécurisées avec refresh tokens

### 📊 Tableau de bord
- Statistiques en temps réel
- Graphiques de distribution des documents
- Activité récente
- Métriques de performance

### 📄 Gestion des documents
- Upload multiple avec drag & drop
- Support PDF, DOC, DOCX, TXT, images
- Anonymisation automatique
- Indexation sémantique
- Métadonnées enrichies

### 🔍 Recherche sémantique
- Recherche en langage naturel
- Filtres avancés (type, date, patient)
- Résultats avec score de pertinence
- Extraits contextuels

### 💬 Q&R Médical
- Chat interactif
- Réponses basées sur les documents
- Sources citées avec pertinence
- Historique des conversations

### 📋 Synthèses médicales
- Chronologies patient
- Résumés de traitement
- Rapports de diagnostic
- Synthèses personnalisées

### 📋 Audit et sécurité
- Logs complets des actions
- Traçabilité des accès
- Conformité RGPD
- Sécurité des données médicales

## 🧪 Tests

```bash
# Tests unitaires
npm run test

# Tests avec UI
npm run test:ui

# Vérification des types
npm run type-check

# Linting
npm run lint
```

## 📦 Build et déploiement

### Build de production
```bash
npm run build
```

### Aperçu du build
```bash
npm run preview
```

### Docker (optionnel)
```bash
docker build -t interface-clinique .
docker run -p 3000:3000 interface-clinique
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit les changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

## 📄 Licence

Ce projet est sous licence MIT - voir le fichier [LICENSE](../LICENSE) pour plus de détails.

## 🙏 Remerciements

- [DocQA-MS](https://github.com/your-org/docqa-ms) - Backend API
- [Material-UI](https://mui.com/) - Composants UI
- [Auth0](https://auth0.com/) - Authentification
- [React](https://reactjs.org/) - Framework UI

## 📞 Support

Pour le support, veuillez contacter l'équipe de développement ou ouvrir une issue sur GitHub.

---

**InterfaceClinique** - Système professionnel de Q&R sur documents médicaux