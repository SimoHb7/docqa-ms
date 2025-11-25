# 🔗 Guide d'Intégration Backend - InterfaceClinique

## 📋 Vue d'ensemble

Ce guide explique comment intégrer InterfaceClinique avec votre backend DocQA-MS. L'application frontend est conçue pour fonctionner avec ou sans backend actif.

## 🚀 Démarrage Rapide

### 1. Configuration du Backend

Assurez-vous que votre backend DocQA-MS fonctionne sur `http://localhost:8000` :

```bash
# Dans le répertoire backend
cd backend
# Suivez les instructions de démarrage de votre backend
```

### 2. Configuration Frontend

Le frontend est déjà configuré pour communiquer avec le backend. Vérifiez les variables d'environnement dans `InterfaceClinique/.env` :

```env
VITE_API_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
```

### 3. Authentification

Pour l'authentification complète, configurez Auth0 (voir `src/components/ui/Auth0SetupGuide.tsx`).

## 🔧 Architecture d'Intégration

### Services Backend

Le fichier `src/services/backend.ts` fournit des fonctions pour interagir avec le backend :

```typescript
import { backend } from '@/services/backend';

// Vérifier la santé du backend
const health = await backend.health();

// Lister les documents
const documents = await backend.documents.list();

// Effectuer une recherche
const results = await backend.search.search('query');

// Poser une question
const answer = await backend.qa.ask({ question: '...' });
```

### Mode Développement

Si le backend n'est pas disponible, l'application utilise des données mock pour permettre le développement de l'interface utilisateur.

## 📊 Endpoints API Utilisés

### Documents
- `GET /documents` - Lister les documents
- `POST /documents/upload` - Télécharger un document
- `GET /documents/{id}` - Détails d'un document
- `DELETE /documents/{id}` - Supprimer un document

### Recherche
- `POST /search` - Recherche sémantique

### Q&R
- `POST /qa/ask` - Poser une question

### Dashboard
- `GET /dashboard/stats` - Statistiques du tableau de bord

### Audit
- `GET /audit/logs` - Logs d'audit

### Synthèse
- `POST /synthesis` - Générer une synthèse

## 🔄 États de Connexion

### Backend En Ligne
- Toutes les fonctionnalités sont disponibles
- Données en temps réel
- Authentification complète

### Backend Hors Ligne
- Interface utilisateur fonctionnelle
- Données mock pour le développement
- Notifications d'indisponibilité

## 🛠️ Dépannage

### Problèmes Courants

#### 1. Erreur CORS
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution :** Assurez-vous que votre backend a CORS activé :
```python
# Dans votre configuration FastAPI
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### 2. Backend Non Accessible
```
Failed to fetch documents: Failed to fetch
```

**Solution :**
- Vérifiez que le backend fonctionne sur le port 8000
- Vérifiez les variables d'environnement
- L'application basculera automatiquement en mode mock

#### 3. Authentification
Si Auth0 n'est pas configuré, l'application affiche un guide de configuration.

## 📈 Fonctionnalités Avancées

### WebSocket (Temps Réel)
Pour les mises à jour en temps réel :
```typescript
// Dans votre backend, implémentez les WebSocket
# Exemple avec FastAPI
from fastapi import WebSocket

@app.websocket("/ws/documents/{document_id}")
async def document_updates(websocket: WebSocket, document_id: str):
    await websocket.accept()
    # Envoyer les mises à jour de statut
```

### Pagination
Toutes les listes supportent la pagination :
```typescript
const params = {
  limit: 20,
  offset: 0,
  // Filtres supplémentaires
};
const result = await backend.documents.list(params);
```

### Gestion d'Erreurs
Les erreurs sont automatiquement gérées et affichées à l'utilisateur :
```typescript
try {
  const result = await backend.documents.upload(file);
} catch (error) {
  // Erreur automatiquement affichée via toast
  console.error('Upload failed:', error);
}
```

## 🎯 Tests d'Intégration

### Tests Automatisés
```bash
cd InterfaceClinique
npm test
```

### Tests Manuels
1. **Connexion Backend :** Vérifiez la console pour les messages de santé
2. **Téléchargement :** Essayez de télécharger un document
3. **Recherche :** Effectuez une recherche
4. **Q&R :** Posez une question
5. **Dashboard :** Vérifiez les statistiques

## 📚 Ressources Supplémentaires

- [Documentation API Backend](./docs/api/api_endpoints.md)
- [Guide Auth0](./src/components/ui/Auth0SetupGuide.tsx)
- [Configuration Environnement](./.env.example)

## 🤝 Support

Si vous rencontrez des problèmes d'intégration :

1. Vérifiez les logs de la console du navigateur
2. Vérifiez les logs du backend
3. Consultez la documentation API
4. Ouvrez une issue sur le repository

---

**InterfaceClinique** - Système professionnel de Q&R sur documents médicaux