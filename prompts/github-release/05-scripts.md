# Phase 5 : Scripts d'Installation

## Objectif
Créer les scripts pour faciliter l'installation et la validation.

## Actions

### 1. Créer le dossier scripts
```bash
mkdir -p ~/dev/lyra/scripts
```

### 2. scripts/download-models.sh
```bash
cat > ~/dev/lyra/scripts/download-models.sh << 'EOF'
#!/bin/bash
# Télécharge les modèles Piper TTS pour Lyra
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODELS_DIR="$SCRIPT_DIR/../models"

echo "=== Téléchargement des modèles Piper TTS ==="

mkdir -p "$MODELS_DIR"
cd "$MODELS_DIR"

# Voix française UPMC medium
BASE_URL="https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/upmc/medium"

if [ -f "fr_FR-upmc-medium.onnx" ]; then
    echo "[!] Modèle déjà présent, skip download"
else
    echo "[1/2] Téléchargement du modèle ONNX..."
    wget -q --show-progress "$BASE_URL/fr_FR-upmc-medium.onnx" -O fr_FR-upmc-medium.onnx

    echo "[2/2] Téléchargement de la config..."
    wget -q --show-progress "$BASE_URL/fr_FR-upmc-medium.onnx.json" -O fr_FR-upmc-medium.onnx.json
fi

echo ""
echo "✓ Modèles téléchargés dans $MODELS_DIR"
ls -lh "$MODELS_DIR"/*.onnx 2>/dev/null || echo "(aucun modèle .onnx trouvé)"
EOF
chmod +x ~/dev/lyra/scripts/download-models.sh
```

### 3. scripts/setup-mcp.sh
```bash
cat > ~/dev/lyra/scripts/setup-mcp.sh << 'EOF'
#!/bin/bash
# Compile le MCP server intégré
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MCP_DIR="$SCRIPT_DIR/../mcp-server"

echo "=== Configuration du MCP Server ==="

if [ ! -d "$MCP_DIR" ]; then
    echo "✗ Dossier mcp-server/ non trouvé"
    echo "  Assurez-vous d'avoir cloné le repo complet"
    exit 1
fi

cd "$MCP_DIR"

echo "[1/2] Installation des dépendances npm..."
npm install --silent

echo "[2/2] Compilation TypeScript..."
npm run build

echo ""
echo "✓ MCP Server compilé"
ls -la "$MCP_DIR/dist/" | head -5
EOF
chmod +x ~/dev/lyra/scripts/setup-mcp.sh
```

### 4. scripts/validate-for-release.sh
```bash
cat > ~/dev/lyra/scripts/validate-for-release.sh << 'EOF'
#!/bin/bash
# Valide que le repo est prêt pour publication GitHub
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$SCRIPT_DIR/.."

echo "=== Validation Pre-Release ==="
ERRORS=0

# Test 1: Pas de chemins hardcodés
echo -n "[1/7] Chemins hardcodés... "
if grep -rn "/home/" --include="*.py" --include="*.sh" "$REPO_DIR" 2>/dev/null | grep -v ".example" | grep -v "lyra.old" | grep -v ".venv" | grep -v "__pycache__" | head -3; then
    echo "✗ TROUVÉ (voir ci-dessus)"
    ((ERRORS++))
else
    echo "✓ OK"
fi

# Test 2: Pas de secrets JWT
echo -n "[2/7] Secrets JWT... "
if grep -rn "eyJ" --include="*.yaml" --include="*.py" --include="*.json" "$REPO_DIR" 2>/dev/null | grep -v ".example" | grep -v "node_modules" | grep -v ".venv"; then
    echo "✗ TROUVÉ"
    ((ERRORS++))
else
    echo "✓ OK"
fi

# Test 3: config.yaml.example existe
echo -n "[3/7] config.yaml.example... "
if [ -f "$REPO_DIR/config.yaml.example" ]; then
    echo "✓ OK"
else
    echo "✗ MANQUANT"
    ((ERRORS++))
fi

# Test 4: .env.example existe
echo -n "[4/7] .env.example... "
if [ -f "$REPO_DIR/.env.example" ]; then
    echo "✓ OK"
else
    echo "✗ MANQUANT"
    ((ERRORS++))
fi

# Test 5: LICENSE existe
echo -n "[5/7] LICENSE... "
if [ -f "$REPO_DIR/LICENSE" ]; then
    echo "✓ OK"
else
    echo "✗ MANQUANT"
    ((ERRORS++))
fi

# Test 6: MCP server présent
echo -n "[6/7] MCP Server... "
if [ -d "$REPO_DIR/mcp-server" ] && [ -f "$REPO_DIR/mcp-server/package.json" ]; then
    echo "✓ OK"
else
    echo "✗ MANQUANT"
    ((ERRORS++))
fi

# Test 7: README existe et contient sections clés
echo -n "[7/7] README.md... "
if [ -f "$REPO_DIR/README.md" ]; then
    if grep -q "Installation" "$REPO_DIR/README.md" && grep -q "Usage" "$REPO_DIR/README.md"; then
        echo "✓ OK"
    else
        echo "⚠ Incomplet (manque sections)"
    fi
else
    echo "✗ MANQUANT"
    ((ERRORS++))
fi

echo ""
if [ $ERRORS -eq 0 ]; then
    echo "════════════════════════════════"
    echo "  ✓ VALIDATION RÉUSSIE"
    echo "════════════════════════════════"
    exit 0
else
    echo "════════════════════════════════"
    echo "  ✗ $ERRORS ERREUR(S) TROUVÉE(S)"
    echo "════════════════════════════════"
    exit 1
fi
EOF
chmod +x ~/dev/lyra/scripts/validate-for-release.sh
```

### 5. scripts/record-demo.sh (fallback pour GIF sans GPU)
```bash
cat > ~/dev/lyra/scripts/record-demo.sh << 'EOF'
#!/bin/bash
# Enregistre une démo automatique avec asciinema (sans GPU requis)
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOCS_DIR="$SCRIPT_DIR/../docs"

echo "=== Enregistrement de démo ==="

# Vérifier asciinema
if ! command -v asciinema &> /dev/null; then
    echo "Installation de asciinema..."
    pip install asciinema
fi

mkdir -p "$DOCS_DIR"

echo ""
echo "Instructions:"
echo "  1. Le terminal va s'ouvrir en mode enregistrement"
echo "  2. Lancez: ./run.sh"
echo "  3. Tapez quelques commandes de démo:"
echo "     - liste mes VMs"
echo "     - status de preprod-09"
echo "     - help"
echo "     - quit"
echo "  4. Tapez 'exit' pour terminer l'enregistrement"
echo ""
read -p "Appuyez sur Entrée pour commencer..."

cd "$SCRIPT_DIR/.."
asciinema rec "$DOCS_DIR/demo.cast"

echo ""
echo "✓ Enregistrement sauvegardé: $DOCS_DIR/demo.cast"
echo ""
echo "Pour convertir en GIF:"
echo "  docker run --rm -v \$PWD/docs:/data asciinema/asciicast2gif /data/demo.cast /data/demo.gif"
echo ""
echo "Ou uploader sur asciinema.org:"
echo "  asciinema upload $DOCS_DIR/demo.cast"
EOF
chmod +x ~/dev/lyra/scripts/record-demo.sh
```

### 6. install.sh (racine du projet)
```bash
cat > ~/dev/lyra/install.sh << 'EOF'
#!/bin/bash
# Lyra - Script d'installation
set -e

echo "╔════════════════════════════════════════╗"
echo "║       🎙️  Installation de Lyra         ║"
echo "╚════════════════════════════════════════╝"
echo ""

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Vérifier les prérequis
echo "[1/7] Vérification des prérequis..."
command -v python3 >/dev/null || { echo "❌ Python3 requis"; exit 1; }
command -v node >/dev/null || { echo "❌ Node.js requis (pour MCP server)"; exit 1; }
command -v npm >/dev/null || { echo "❌ npm requis"; exit 1; }
command -v ollama >/dev/null || { echo "❌ Ollama requis (https://ollama.ai)"; exit 1; }
echo "✓ Prérequis OK"

# Environnement Python
echo ""
echo "[2/7] Création de l'environnement Python..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install --upgrade pip -q

# Dépendances Python
echo ""
echo "[3/7] Installation des dépendances Python..."
pip install -r requirements.txt -q
echo "✓ Dépendances Python installées"

# MCP Server
echo ""
echo "[4/7] Compilation du MCP Server..."
./scripts/setup-mcp.sh

# Modèles TTS
echo ""
echo "[5/7] Téléchargement des modèles TTS..."
./scripts/download-models.sh

# Modèle LLM
echo ""
echo "[6/7] Vérification du modèle LLM..."
if ollama list | grep -q "qwen2.5-coder:14b"; then
    echo "✓ Modèle qwen2.5-coder:14b déjà présent"
else
    echo "Téléchargement de qwen2.5-coder:14b (~9GB)..."
    echo "(Cela peut prendre plusieurs minutes)"
    ollama pull qwen2.5-coder:14b
fi

# Configuration
echo ""
echo "[7/7] Configuration..."
if [ ! -f config.yaml ]; then
    cp config.yaml.example config.yaml
    echo "✓ config.yaml créé (éditer selon votre setup)"
else
    echo "✓ config.yaml existe déjà"
fi

if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ .env créé (optionnel - pour n8n/Discord)"
else
    echo "✓ .env existe déjà"
fi

echo ""
echo "╔════════════════════════════════════════╗"
echo "║       ✓ Installation terminée!         ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "Lancer Lyra:"
echo "  source .venv/bin/activate"
echo "  ./run.sh"
echo ""
echo "Mode vocal (nécessite GPU CUDA):"
echo "  ./run.sh --vocal"
echo ""
EOF
chmod +x ~/dev/lyra/install.sh
```

## Tests de Validation

```bash
# Test 1: Scripts exécutables
[ -x ~/dev/lyra/scripts/download-models.sh ] && echo "✓ download-models.sh OK" || echo "✗ ERREUR"
[ -x ~/dev/lyra/scripts/setup-mcp.sh ] && echo "✓ setup-mcp.sh OK" || echo "✗ ERREUR"
[ -x ~/dev/lyra/scripts/validate-for-release.sh ] && echo "✓ validate-for-release.sh OK" || echo "✗ ERREUR"
[ -x ~/dev/lyra/scripts/record-demo.sh ] && echo "✓ record-demo.sh OK" || echo "✗ ERREUR"
[ -x ~/dev/lyra/install.sh ] && echo "✓ install.sh OK" || echo "✗ ERREUR"

# Test 2: Pas de chemins hardcodés dans les scripts
grep -r "/home/amineutron" ~/dev/lyra/scripts/*.sh && echo "✗ CHEMIN HARDCODÉ!" || echo "✓ Scripts OK"

# Test 3: Validation script fonctionne (peut échouer si phases précédentes pas faites)
cd ~/dev/lyra && ./scripts/validate-for-release.sh || echo "(Échec attendu si phases précédentes incomplètes)"
```

## Checklist
- [ ] scripts/ créé
- [ ] download-models.sh créé et exécutable
- [ ] setup-mcp.sh créé et exécutable
- [ ] validate-for-release.sh créé et exécutable
- [ ] record-demo.sh créé et exécutable
- [ ] install.sh créé et exécutable
- [ ] Aucun chemin hardcodé dans les scripts
