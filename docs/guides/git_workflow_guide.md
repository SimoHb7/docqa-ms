# Guide du Workflow Git - DocQA-MS

## Vue d'ensemble

Ce guide explique comment organiser votre travail collaboratif sur DocQA-MS en utilisant Git et GitHub de manière efficace.

## Structure des branches

### Branches principales (protégées)
```
main          # Production - code déployé
develop       # Intégration - code stable prêt pour release
```

### Branches de développement
```
feature/*     # Nouvelles fonctionnalités
bugfix/*      # Corrections de bugs
hotfix/*      # Corrections urgentes
release/*     # Préparation de release
```

## Workflow de développement

### 1. Configuration initiale

```bash
# 1. Créer le repository GitHub (privé)
# Aller sur github.com et créer un repo privé nommé "docqa-ms"

# 2. Initialiser Git localement
cd votre-dossier-docqa-ms
git init
git add .
git commit -m "Initial commit: DocQA-MS architecture and setup"

# 3. Connecter au repository GitHub
git remote add origin https://github.com/votre-username/docqa-ms.git
git push -u origin main

# 4. Créer la branche develop
git checkout -b develop
git push -u origin develop
```

### 2. Travail quotidien

#### Démarrer une nouvelle tâche
```bash
# Toujours partir de develop
git checkout develop
git pull origin develop

# Créer une branche pour votre tâche
git checkout -b feature/api-gateway-auth

# Commencer à travailler...
```

#### Commiter régulièrement
```bash
# Ajouter les fichiers modifiés
git add backend/api_gateway/app/main.py
git add backend/api_gateway/requirements.txt

# Commiter avec un message descriptif
git commit -m "feat(api-gateway): implement JWT authentication

- Add login endpoint with Auth0 integration
- Add token validation middleware
- Add user role-based permissions
- Add comprehensive error handling"

# Pousser votre branche
git push origin feature/api-gateway-auth
```

#### Créer une Pull Request
1. Aller sur GitHub
2. Cliquer sur "Pull Request"
3. Sélectionner votre branche → develop
4. Remplir le template de PR
5. Assigner un reviewer
6. Créer la PR

## Organisation par collègue

### Assignation des responsabilités

#### Backend Team
```
Personne A - API Gateway + Auth
├── feature/api-gateway-routing
├── feature/auth0-integration
└── feature/rate-limiting

Personne B - Document Services
├── feature/doc-ingestor-ocr
├── feature/deid-anonymization
└── feature/file-validation

Personne C - IA & Search
├── feature/semantic-indexing
├── feature/llm-integration
└── feature/vector-search

Personne D - Analytics & Audit
├── feature/comparative-synthesis
├── feature/audit-logging
└── feature/performance-metrics
```

#### Frontend Team
```
Personne E - Core UI
├── feature/frontend-search
├── feature/frontend-dashboard
└── feature/responsive-design

Personne F - Document Management
├── feature/document-upload
├── feature/document-viewer
└── feature/bulk-operations

Personne G - Admin & Monitoring
├── feature/admin-dashboard
├── feature/audit-viewer
└── feature/user-management
```

#### DevOps Team
```
Personne H - Infrastructure
├── feature/docker-optimization
├── feature/kubernetes-deploy
└── feature/monitoring-setup
```

### Branches actives simultanées
```
develop
├── feature/api-gateway-auth (Personne A)
├── feature/doc-ingestor-ocr (Personne B)
├── feature/semantic-indexing (Personne C)
├── feature/audit-logging (Personne D)
├── feature/frontend-search (Personne E)
├── feature/document-upload (Personne F)
├── feature/admin-dashboard (Personne G)
└── feature/docker-optimization (Personne H)
```

## Gestion des conflits

### Prévention des conflits
```bash
# Vérifier l'état avant de commencer
git status
git log --oneline -10

# Mettre à jour régulièrement
git checkout develop
git pull origin develop
git checkout votre-branche
git rebase develop
```

### Résolution de conflits
```bash
# Si conflit lors du rebase
git status  # Voir les fichiers en conflit
# Éditer les fichiers pour résoudre les conflits
git add fichier-résolu
git rebase --continue

# Si trop de conflits, abandonner et recommencer
git rebase --abort
git merge develop  # Utiliser merge au lieu de rebase
```

## Code Reviews

### Processus de review
1. **Auteur** crée la PR et assigne un reviewer
2. **Reviewer** examine le code :
   - Fonctionnalités implémentées
   - Tests présents
   - Code style respecté
   - Sécurité vérifiée
3. **Discussion** sur GitHub si besoin
4. **Approbation** ou demandes de changements
5. **Merge** une fois approuvé

### Checklist de review
- [ ] Code compile sans erreurs
- [ ] Tests passent
- [ ] Fonctionnalité testée manuellement
- [ ] Documentation mise à jour
- [ ] Pas de secrets commités
- [ ] Sécurité : pas de vulnérabilités évidentes
- [ ] Performance : pas de régressions
- [ ] Conformité : respecte les standards médicaux

## Releases et versions

### Processus de release
```bash
# 1. Créer une branche release
git checkout develop
git pull origin develop
git checkout -b release/v1.0.0

# 2. Finaliser la release
# Tests finaux, documentation, etc.
git commit -m "chore: prepare release v1.0.0"

# 3. Merger dans main
git checkout main
git merge release/v1.0.0
git tag v1.0.0
git push origin main --tags

# 4. Merger les changements dans develop
git checkout develop
git merge release/v1.0.0
git push origin develop

# 5. Nettoyer
git branch -d release/v1.0.0
git push origin --delete release/v1.0.0
```

## Commandes Git essentielles

### Status et historique
```bash
git status              # État des fichiers
git log --oneline       # Historique simplifié
git log --graph         # Historique avec graphique
git diff                # Différences non commitées
git diff --staged       # Différences stagées
```

### Branches
```bash
git branch              # Lister les branches
git branch -a           # Toutes les branches (local + remote)
git checkout -b nouvelle-branche  # Créer et basculer
git branch -d branche   # Supprimer branche locale
git push origin --delete branche  # Supprimer branche remote
```

### Synchronisation
```bash
git fetch               # Récupérer les changements remote
git pull                # Fetch + merge
git push                # Pousser les commits
git push -u origin branche  # Pousser et tracker
```

### Undo operations
```bash
git reset --soft HEAD~1    # Annuler commit, garder les changements
git reset --hard HEAD~1    # Annuler commit et changements
git revert commit-hash     # Créer commit qui annule un autre
git commit --amend         # Modifier le dernier commit
```

## Bonnes pratiques

### Messages de commit
Suivre [Conventional Commits](https://conventionalcommits.org/) :

```
type(scope): description courte

Description longue si nécessaire

Closes #123
```

Types : `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Taille des commits
- Commits atomiques (une fonctionnalité = un commit)
- Pas de commits trop gros (>500 lignes)
- Messages descriptifs en anglais

### Gestion des fichiers
- Ne pas commiter :
  - `.env` (utiliser `.env.example`)
  - Fichiers temporaires
  - Dépendances (sauf requirements.txt)
  - Secrets ou clés API

### Communication
- Utiliser les issues GitHub pour discuter des tâches
- Mentionner les collègues avec @username
- Utiliser les labels pour catégoriser
- Fermer les issues automatiquement avec "Closes #123"

## Outils recommandés

### Git GUI
- **GitKraken** : Interface graphique complète
- **GitHub Desktop** : Simple pour débutants
- **VS Code** : Intégré avec extensions Git

### Extensions VS Code
- GitLens : Historique avancé
- Git Graph : Visualisation des branches
- GitHub Pull Requests : Gestion des PR

### Commandes utiles
```bash
# Alias recommandés (dans ~/.gitconfig)
[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = !gitk
```

## Résolution de problèmes courants

### "fatal: remote origin already exists"
```bash
git remote remove origin
git remote add origin nouvelle-url
```

### Branches divergées
```bash
# Option 1: Rebase (préféré)
git checkout votre-branche
git rebase develop

# Option 2: Merge
git checkout develop
git merge votre-branche
```

### Commits dans la mauvaise branche
```bash
# Créer nouvelle branche depuis le commit
git branch nouvelle-branche commit-hash
git reset --hard HEAD~n  # Annuler les n derniers commits
```

### Fichiers oubliés dans .gitignore
```bash
git rm --cached fichier-secret
echo "fichier-secret" >> .gitignore
git add .gitignore
git commit -m "chore: ignore sensitive files"
```

## Support

Pour toute question sur Git :
1. `git --help commande`
2. [Documentation Git](https://git-scm.com/doc)
3. [GitHub Guides](https://guides.github.com/)
4. Demander à un collègue expérimenté

---

*Ce guide évoluera avec vos retours d'expérience.*