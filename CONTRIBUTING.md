# Guide de contribution - DocQA-MS

## Bienvenue ! 👋

Merci de contribuer à DocQA-MS ! Ce guide explique comment travailler efficacement sur le projet.

## Table des matières
- [Code de conduite](#code-de-conduite)
- [Structure du projet](#structure-du-projet)
- [Workflow de développement](#workflow-de-développement)
- [Configuration de l'environnement](#configuration-de-lenvironnement)
- [Standards de codage](#standards-de-codage)
- [Tests](#tests)
- [Pull Requests](#pull-requests)
- [Gestion des branches](#gestion-des-branches)
- [Communication](#communication)

## Code de conduite

Nous nous engageons à fournir un environnement accueillant et respectueux. Tous les contributeurs doivent :

- Respecter les opinions et expériences des autres
- Accepter les critiques constructives
- Se concentrer sur ce qui est meilleur pour la communauté
- Montrer de l'empathie envers les autres membres

## Structure du projet

```
docqa-ms/
├── backend/                    # Services backend Python
│   ├── api_gateway/           # Point d'entrée API
│   ├── doc_ingestor/          # Ingestion de documents
│   ├── deid/                  # Anonymisation
│   ├── indexer_semantique/    # Indexation vectorielle
│   ├── llm_qa/               # Q&A avec LLM
│   ├── synthese_comparative/  # Synthèses comparatives
│   ├── audit_logger/          # Traçabilité
│   ├── database/              # Schéma et migrations
│   └── shared/                # Code partagé
├── frontend/                  # Interface React
├── docs/                      # Documentation
├── tests/                     # Tests automatisés
├── infra/                     # Infrastructure
└── scripts/                   # Scripts utilitaires
```

## Workflow de développement

### 1. Préparation
```bash
# Cloner le repository
git clone https://github.com/votre-org/docqa-ms.git
cd docqa-ms

# Installer les dépendances
pip install -r backend/requirements.txt
cd frontend && npm install && cd ..

# Copier la configuration
cp .env.example .env
```

### 2. Branches

Nous utilisons un workflow Git Flow simplifié :

#### Branches principales
- **`main`**: Code de production (protégé)
- **`develop`**: Intégration continue

#### Branches de développement
- **`feature/*`**: Nouvelles fonctionnalités
- **`bugfix/*`**: Corrections de bugs
- **`hotfix/*`**: Corrections urgentes en production

#### Exemples de noms de branches
```
feature/api-gateway-auth
feature/doc-ingestor-ocr
bugfix/deid-performance
hotfix/security-patch
```

### 3. Développement quotidien

```bash
# Basculer vers develop et mettre à jour
git checkout develop
git pull origin develop

# Créer une branche pour votre travail
git checkout -b feature/ma-fonctionnalite

# Commiter régulièrement avec des messages clairs
git add .
git commit -m "feat: ajouter validation des documents PDF

- Ajouter vérification du type MIME
- Valider la taille des fichiers
- Retourner erreurs appropriées"

# Pousser votre branche
git push -u origin feature/ma-fonctionnalite
```

## Configuration de l'environnement

### Variables d'environnement
Copiez `.env.example` vers `.env` et ajustez les valeurs :

```bash
# Base de données
DATABASE_URL=postgresql://user:password@localhost:5432/docqa_db

# LLM
OLLAMA_BASE_URL=http://localhost:11434
# ou
OPENAI_API_KEY=votre_clé

# Développement
DEBUG=True
LOG_LEVEL=INFO
```

### Lancement des services
```bash
# Tout lancer
docker-compose up -d

# Un service spécifique
docker-compose up api-gateway

# Avec rebuild
docker-compose up --build api-gateway
```

## Standards de codage

### Backend (Python)

#### Style
- **Black** pour le formatage automatique
- **isort** pour l'importation des modules
- **flake8** pour le linting
- **mypy** pour le typage statique

#### Conventions
```python
# Imports organisés
from typing import List, Optional
import fastapi
from fastapi import HTTPException

# Nommage
class DocumentService:  # PascalCase pour classes
    def __init__(self, db_session):
        self.db = db_session

    def get_document(self, document_id: str) -> Optional[Document]:  # snake_case pour fonctions
        pass

    async def process_document(self, file: UploadFile) -> Document:  # async/await pour I/O
        pass
```

#### Gestion d'erreurs
```python
from fastapi import HTTPException

def validate_document(file):
    if file.size > MAX_SIZE:
        raise HTTPException(
            status_code=413,
            detail="File too large"
        )

    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type"
        )
```

### Frontend (React/TypeScript)

#### Structure des composants
```typescript
// components/DocumentUpload.tsx
import React, { useState, useCallback } from 'react';
import { Upload, message } from 'antd';

interface DocumentUploadProps {
  onUploadSuccess: (documentId: string) => void;
  maxSize?: number;
}

export const DocumentUpload: React.FC<DocumentUploadProps> = ({
  onUploadSuccess,
  maxSize = 50 * 1024 * 1024
}) => {
  const [uploading, setUploading] = useState(false);

  const handleUpload = useCallback(async (file: File) => {
    // Logique d'upload
  }, [onUploadSuccess]);

  return (
    <Upload
      beforeUpload={handleUpload}
      showUploadList={false}
    >
      <Button loading={uploading}>
        <UploadOutlined /> Upload Document
      </Button>
    </Upload>
  );
};
```

#### Hooks personnalisés
```typescript
// hooks/useDocuments.ts
import { useQuery, useMutation } from 'react-query';

export const useDocuments = (filters?: DocumentFilters) => {
  return useQuery(['documents', filters], () =>
    api.getDocuments(filters)
  );
};

export const useUploadDocument = () => {
  return useMutation(api.uploadDocument);
};
```

## Tests

### Backend - Tests unitaires
```python
# tests/test_document_service.py
import pytest
from app.services.document_service import DocumentService

class TestDocumentService:
    def test_get_document_success(self, db_session, sample_document):
        service = DocumentService(db_session)
        result = service.get_document(sample_document.id)

        assert result is not None
        assert result.id == sample_document.id

    def test_get_document_not_found(self, db_session):
        service = DocumentService(db_session)
        result = service.get_document("nonexistent-id")

        assert result is None
```

### Backend - Tests d'intégration
```python
# tests/integration/test_document_workflow.py
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_document_upload_workflow(client: AsyncClient, sample_pdf):
    # Upload document
    response = await client.post(
        "/documents/upload",
        files={"file": ("test.pdf", sample_pdf, "application/pdf")}
    )
    assert response.status_code == 200

    document_id = response.json()["document_id"]

    # Check processing status
    response = await client.get(f"/documents/{document_id}")
    assert response.status_code == 200
    assert response.json()["status"] in ["processing", "processed"]
```

### Frontend - Tests
```typescript
// components/__tests__/DocumentUpload.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DocumentUpload } from '../DocumentUpload';

const mockOnUploadSuccess = jest.fn();

describe('DocumentUpload', () => {
  it('renders upload button', () => {
    render(<DocumentUpload onUploadSuccess={mockOnUploadSuccess} />);
    expect(screen.getByText('Upload Document')).toBeInTheDocument();
  });

  it('calls onUploadSuccess on successful upload', async () => {
    // Test d'upload simulé
  });
});
```

### Exécution des tests
```bash
# Backend
pytest backend/ --cov=backend --cov-report=html

# Frontend
cd frontend && npm test -- --coverage

# Tests d'intégration
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## Pull Requests

### Processus de PR
1. **Créer une branche** depuis `develop`
2. **Développer** et tester localement
3. **Commiter** avec des messages descriptifs
4. **Pousser** la branche
5. **Créer une PR** sur GitHub
6. **Review** par au moins un collègue
7. **Merge** après approbation

### Template de PR
Utilisez le template fourni dans `.github/pull_request_template.md` :

- Description claire des changements
- Type de changement (feature, bugfix, etc.)
- Tests effectués
- Considérations de sécurité
- Screenshots si applicable

### Checklist de PR
- [ ] Code suit les standards du projet
- [ ] Tests ajoutés/mis à jour
- [ ] Documentation mise à jour
- [ ] Pas de secrets commités
- [ ] Branches à jour avec develop
- [ ] CI passe
- [ ] Review obtenue

## Gestion des branches

### Création de branches
```bash
# Feature
git checkout develop
git pull origin develop
git checkout -b feature/nom-de-la-feature

# Bugfix
git checkout develop
git pull origin develop
git checkout -b bugfix/description-du-bug

# Hotfix (depuis main)
git checkout main
git pull origin main
git checkout -b hotfix/correction-urgente
```

### Merge de branches
```bash
# Après review et approbation
git checkout develop
git pull origin develop
git merge feature/ma-feature
git push origin develop

# Nettoyer la branche
git branch -d feature/ma-feature
git push origin --delete feature/ma-feature
```

## Communication

### Issues GitHub
- Utilisez les templates fournis
- Soyez descriptif et précis
- Ajoutez des labels appropriés
- Liez les issues aux PRs

### Messages de commit
Suivez la convention [Conventional Commits](https://conventionalcommits.org/) :

```
type(scope): description

[body optionnel]

[footer optionnel]
```

Types :
- `feat`: Nouvelle fonctionnalité
- `fix`: Correction de bug
- `docs`: Changement de documentation
- `style`: Changement de style (formatage, etc.)
- `refactor`: Refactorisation du code
- `test`: Ajout/modification de tests
- `chore`: Tâche de maintenance

Exemples :
```
feat(api): add document upload endpoint
fix(deid): handle edge case in PII detection
docs(readme): update installation instructions
test(auth): add login integration tests
```

### Code Reviews
- Soyez constructif et respectueux
- Expliquez votre raisonnement
- Suggérez des alternatives
- Approuvez ou demandez des changements

## Ressources supplémentaires

- [Documentation API](docs/api/api_endpoints.md)
- [Guide d'installation](docs/guides/setup_guide.md)
- [Architecture système](docs/architecture/system_architecture.md)
- [Résolution de problèmes](docs/guides/troubleshooting.md)

## Support

Pour toute question :
1. Vérifiez la documentation
2. Cherchez dans les issues existantes
3. Créez une nouvelle issue
4. Contactez l'équipe sur Discord/Slack

Merci de votre contribution à DocQA-MS ! 🚀