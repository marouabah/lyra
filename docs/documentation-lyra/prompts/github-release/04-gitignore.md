# Phase 4 : Mise à jour .gitignore

## Objectif
Protéger les secrets et fichiers générés du commit.

## Actions

### 1. Lire le .gitignore actuel
```bash
cat ~/dev/lyra/.gitignore
```

### 2. Ajouter les entrées manquantes

Ajouter au `.gitignore` :
```bash
cat >> ~/dev/lyra/.gitignore << 'EOF'

# =============================================================================
# Secrets & Configuration locale
# =============================================================================
config.yaml
.env

# =============================================================================
# MCP Server (build artifacts)
# =============================================================================
mcp-server/node_modules/
mcp-server/dist/

# =============================================================================
# Python
# =============================================================================
.venv/
__pycache__/
*.pyc
*.pyo
.pytest_cache/

# =============================================================================
# Cache & Logs
# =============================================================================
.cache/
logs/
*.log

# =============================================================================
# IDE
# =============================================================================
.vscode/
.idea/
*.swp
*.swo

# =============================================================================
# OS
# =============================================================================
.DS_Store
Thumbs.db

# =============================================================================
# Backup files
# =============================================================================
*.old
*.bak
*.backup
EOF
```

### 3. Retirer config.yaml du suivi git (si déjà tracké)
```bash
cd ~/dev/lyra

# Vérifier si config.yaml est tracké
git ls-files | grep config.yaml

# Si oui, le retirer du suivi (sans supprimer le fichier)
git rm --cached config.yaml 2>/dev/null && echo "config.yaml retiré du suivi" || echo "config.yaml pas tracké (OK)"

# Pareil pour .env si présent
git rm --cached .env 2>/dev/null || true
```

### 4. Vérifier que les fichiers sont bien ignorés
```bash
cd ~/dev/lyra

# Créer un .env de test si pas présent
[ ! -f .env ] && cp .env.example .env

# Vérifier le status
git status --porcelain | grep -E "config\.yaml|\.env"
# Ne devrait rien afficher si bien ignoré
```

## Tests de Validation

```bash
# Test 1: config.yaml dans gitignore
grep -q "^config.yaml$" ~/dev/lyra/.gitignore && echo "✓ config.yaml ignoré" || echo "✗ ERREUR"

# Test 2: .env dans gitignore
grep -q "^\.env$" ~/dev/lyra/.gitignore && echo "✓ .env ignoré" || echo "✗ ERREUR"

# Test 3: node_modules ignoré
grep -q "mcp-server/node_modules" ~/dev/lyra/.gitignore && echo "✓ node_modules ignoré" || echo "✗ ERREUR"

# Test 4: dist ignoré
grep -q "mcp-server/dist" ~/dev/lyra/.gitignore && echo "✓ dist ignoré" || echo "✗ ERREUR"

# Test 5: git status propre (pas de secrets)
cd ~/dev/lyra
git status --porcelain | grep -E "config\.yaml|\.env" && echo "✗ SECRETS VISIBLES!" || echo "✓ Secrets cachés"

# Test 6: Les fichiers example sont trackés
git ls-files | grep -E "config\.yaml\.example|\.env\.example" && echo "✓ Examples trackés" || echo "⚠ Examples non trackés (ajouter avec git add)"
```

## Fichiers qui DOIVENT être trackés
- `config.yaml.example`
- `.env.example`
- `.gitignore`
- Tout le code source

## Fichiers qui NE DOIVENT PAS être trackés
- `config.yaml` (secrets)
- `.env` (secrets)
- `mcp-server/node_modules/`
- `mcp-server/dist/`
- `.venv/`
- `__pycache__/`
- `.cache/`

## Checklist
- [ ] config.yaml ajouté à .gitignore
- [ ] .env ajouté à .gitignore
- [ ] mcp-server/node_modules/ ajouté
- [ ] mcp-server/dist/ ajouté
- [ ] .venv/ ajouté
- [ ] config.yaml retiré du suivi git (si était tracké)
- [ ] git status ne montre pas les secrets
- [ ] Les fichiers .example sont bien trackés
