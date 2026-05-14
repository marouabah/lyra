# Phase 10 : Validation Locale Complète

## Objectif
Vérifier que tout fonctionne correctement avant le test sur VM.

## Actions

### 1. Lancer le script de validation
```bash
cd ~/dev/lyra
./scripts/validate-for-release.sh
```

### 2. Lancer les tests pytest
```bash
cd ~/dev/lyra
source .venv/bin/activate
pytest tests/ -v
```

### 3. Tester Lyra manuellement
```bash
source .venv/bin/activate
./run.sh

# Tester ces commandes:
# > help
# > liste mes VMs
# > quit
```

### 4. Vérifier le mode vocal (si GPU disponible)
```bash
./run.sh --vocal
# Dire "help" ou "stop"
```

### 5. Vérifier git status
```bash
cd ~/dev/lyra
git status

# DOIT montrer:
# - Nouveaux fichiers à commiter (.env.example, config.yaml.example, etc.)
# - Fichiers modifiés (README.md, modules/*.py, etc.)

# NE DOIT PAS montrer:
# - config.yaml (doit être ignoré)
# - .env (doit être ignoré)
# - mcp-server/node_modules/ (doit être ignoré)
# - mcp-server/dist/ (doit être ignoré)
# - .venv/ (doit être ignoré)
```

### 6. Vérifier les fichiers trackés
```bash
# Lister ce qui sera commité
git ls-files --others --exclude-standard  # Nouveaux fichiers non trackés
git diff --name-only                       # Fichiers modifiés

# S'assurer que les .example sont trackés
git add config.yaml.example .env.example
git add LICENSE CONTRIBUTING.md CHANGELOG.md
git add install.sh scripts/*.sh
git add tests/*.py pytest.ini
git add .github/workflows/ci.yml
git add docs/  # Si assets créés
```

## Checklist Complète

### Fichiers requis
```
[ ] .env.example existe
[ ] config.yaml.example existe
[ ] LICENSE existe (MIT)
[ ] README.md mis à jour (premium)
[ ] CONTRIBUTING.md existe
[ ] CHANGELOG.md existe
[ ] install.sh existe et exécutable
[ ] run.sh existe et exécutable
[ ] mcp-server/ existe avec package.json
[ ] scripts/download-models.sh existe et exécutable
[ ] scripts/setup-mcp.sh existe et exécutable
[ ] scripts/validate-for-release.sh existe et exécutable
[ ] tests/ existe avec fichiers de test
[ ] .github/workflows/ci.yml existe
[ ] docs/ existe (même vide ou avec placeholders)
```

### Sécurité
```
[ ] Pas de /home/amineutron dans modules/*.py
[ ] Pas de /home/amineutron dans scripts/*.sh
[ ] Pas de /home/amineutron dans *.yaml (sauf .old)
[ ] Pas de JWT/secrets dans les fichiers
[ ] config.yaml dans .gitignore
[ ] .env dans .gitignore
[ ] mcp-server/node_modules/ dans .gitignore
[ ] mcp-server/dist/ dans .gitignore
```

### Fonctionnel
```
[ ] Lyra démarre (./run.sh)
[ ] "help" affiche l'aide
[ ] "liste mes VMs" fonctionne (ou erreur claire si pas de VMs)
[ ] Tests pytest passent
[ ] validate-for-release.sh passe
```

### Git
```
[ ] git status propre (pas de secrets visibles)
[ ] Fichiers .example trackés
[ ] LICENSE tracké
[ ] README.md tracké
[ ] Tous les scripts trackés
```

## Script de validation complète

```bash
#!/bin/bash
# Validation complète avant release

cd ~/dev/lyra
source .venv/bin/activate

echo "=== VALIDATION COMPLÈTE ==="
echo ""

# 1. Script de validation
echo "[1/4] Script validate-for-release.sh..."
./scripts/validate-for-release.sh || { echo "✗ ÉCHEC"; exit 1; }

# 2. Tests pytest
echo ""
echo "[2/4] Tests pytest..."
pytest tests/ -v --tb=short || { echo "✗ ÉCHEC"; exit 1; }

# 3. Vérifier git status
echo ""
echo "[3/4] Git status..."
if git status --porcelain | grep -E "config\.yaml$|^\.env$"; then
    echo "✗ SECRETS DANS GIT STATUS!"
    exit 1
else
    echo "✓ Pas de secrets exposés"
fi

# 4. Test Lyra démarre
echo ""
echo "[4/4] Test démarrage Lyra..."
timeout 5 python -c "
from modules.mcp import MCPClient
from modules.llm import OllamaClient
print('✓ Imports OK')
" || { echo "✗ ÉCHEC import"; exit 1; }

echo ""
echo "════════════════════════════════════════"
echo "  ✓ VALIDATION COMPLÈTE RÉUSSIE"
echo "════════════════════════════════════════"
echo ""
echo "Prochaine étape: Phase 11 (Test VM)"
```

## Tests de Validation

```bash
# Exécuter la validation complète
cd ~/dev/lyra
./scripts/validate-for-release.sh && pytest tests/ -v && echo "✓ PRÊT POUR TEST VM"
```

## Checklist Finale
- [ ] validate-for-release.sh passe
- [ ] pytest passe
- [ ] Lyra démarre et répond
- [ ] git status ne montre pas de secrets
- [ ] Tous fichiers requis présents
- [ ] Prêt pour test sur VM (Phase 11)
