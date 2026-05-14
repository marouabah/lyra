# Phase 2 : Sécurisation des Secrets

## Objectif
Supprimer tous les secrets du code et créer des templates.

## Actions

### 1. Créer .env.example
```bash
cat > ~/dev/lyra/.env.example << 'EOF'
# Lyra - Variables d'environnement
# Copier vers .env et remplir les valeurs

# n8n API Key (optionnel - pour opérations async via n8n)
N8N_API_KEY=

# Discord Webhook (optionnel - notifications)
DISCORD_WEBHOOK_URL=

# Chemins personnalisés (optionnel - défauts utilisés sinon)
# MCP_SERVER_PATH=./mcp-server/dist/index.js
# SCRIPTS_BASE_PATH=~/.local/share/lyra/scripts
EOF
```

### 2. Créer config.yaml.example
```bash
cat > ~/dev/lyra/config.yaml.example << 'EOF'
# Lyra - Configuration
# Copier vers config.yaml et adapter selon votre setup

# =============================================================================
# LLM Configuration (Ollama)
# =============================================================================
llm:
  provider: ollama
  model: qwen2.5-coder:14b
  base_url: http://localhost:11434
  timeout: 120
  temperature: 0.3
  max_tokens: 2048

# =============================================================================
# MCP Server
# =============================================================================
mcp:
  # Chemin relatif vers le MCP server intégré
  server_path: ./mcp-server/dist/index.js
  timeout: 120

# =============================================================================
# n8n (optionnel - pour opérations async)
# =============================================================================
n8n:
  base_url: http://localhost:5678
  # Sera lu depuis .env (N8N_API_KEY)
  api_key: ${N8N_API_KEY}
  enabled: false  # Mettre true si n8n est configuré
  webhooks:
    clone-vm: /webhook/lyra-clone-vm
    backup-create: /webhook/lyra-backup-create
    backup-restore: /webhook/lyra-backup-restore

# =============================================================================
# Discord (optionnel)
# =============================================================================
discord:
  webhook_url: ${DISCORD_WEBHOOK_URL}
  enabled: false

# =============================================================================
# Speech-to-Text (faster-whisper)
# =============================================================================
stt:
  engine: faster-whisper
  model: base
  language: fr
  device: cuda
  compute_type: float16
  beam_size: 5
  vad_filter: true

# =============================================================================
# Text-to-Speech (Piper)
# =============================================================================
tts:
  engine: piper
  model: fr_FR-upmc-medium
  speaker_id: 0
  length_scale: 1.0

# =============================================================================
# Audio
# =============================================================================
audio:
  sample_rate: 48000
  channels: 1
  silence_threshold: 0.005
  silence_duration: 1.0
  input_device: null   # null = défaut système
  output_device: null

# =============================================================================
# Sécurité
# =============================================================================
security:
  require_snapshot_before_delete: true
  snapshot_max_age_minutes: 5
  read_first_enabled: true
  destructive_tools:
    - vm_destroy
    - vm_delete
    - backup_restore
    - backup_clean

# =============================================================================
# Logging
# =============================================================================
logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file: null
  rich_console: true

# =============================================================================
# Paths
# =============================================================================
paths:
  prompts: prompts/
  logs: logs/
  cache: .cache/
EOF
```

### 3. Créer le loader Python pour les variables d'environnement

Créer/modifier `modules/config.py` :
```python
"""
Lyra - Configuration loader avec support variables d'environnement
"""
import os
import re
import yaml
from pathlib import Path

def load_dotenv_file(env_path: Path) -> None:
    """Charge un fichier .env dans os.environ."""
    if not env_path.exists():
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

def load_config(config_path: str = None) -> dict:
    """Charge la configuration avec expansion des variables d'environnement.

    Supporte:
    - ${VAR_NAME} dans le YAML
    - Fallback vers .env si variable non définie
    """
    # Charger .env si présent
    project_root = Path(__file__).parent.parent
    env_path = project_root / ".env"
    load_dotenv_file(env_path)

    # Chemin config
    if config_path is None:
        config_path = project_root / "config.yaml"
    else:
        config_path = Path(config_path)

    with open(config_path) as f:
        content = f.read()

    # Remplacer ${VAR} par la valeur de l'environnement
    def replace_env_var(match):
        var_name = match.group(1)
        return os.environ.get(var_name, "")

    content = re.sub(r'\$\{(\w+)\}', replace_env_var, content)

    config = yaml.safe_load(content)

    # Fallback: lire directement depuis os.environ si null/vide
    if config.get("n8n", {}).get("api_key") in (None, ""):
        config.setdefault("n8n", {})["api_key"] = os.environ.get("N8N_API_KEY")

    if config.get("discord", {}).get("webhook_url") in (None, ""):
        config.setdefault("discord", {})["webhook_url"] = os.environ.get("DISCORD_WEBHOOK_URL")

    return config


def get_project_root() -> Path:
    """Retourne le chemin racine du projet."""
    return Path(__file__).parent.parent


def get_mcp_server_path(config: dict = None) -> str:
    """Retourne le chemin du MCP server."""
    # 1. Variable d'environnement
    env_path = os.environ.get("MCP_SERVER_PATH")
    if env_path:
        return env_path

    # 2. Config
    if config and config.get("mcp", {}).get("server_path"):
        path = config["mcp"]["server_path"]
        if not os.path.isabs(path):
            path = str(get_project_root() / path)
        return path

    # 3. Défaut: MCP server intégré
    return str(get_project_root() / "mcp-server" / "dist" / "index.js")


def get_scripts_base_path() -> str:
    """Retourne le chemin de base des scripts."""
    # 1. Variable d'environnement
    env_path = os.environ.get("SCRIPTS_BASE_PATH")
    if env_path:
        return os.path.expanduser(env_path)

    # 2. Défaut: ~/.local/share/lyra/scripts
    return os.path.expanduser("~/.local/share/lyra/scripts")
```

### 4. Supprimer config.yaml du suivi git (sera fait dans phase 04-gitignore)

## Tests de Validation

```bash
# Test 1: .env.example existe
[ -f ~/dev/lyra/.env.example ] && echo "✓ .env.example OK" || echo "✗ ERREUR"

# Test 2: config.yaml.example existe
[ -f ~/dev/lyra/config.yaml.example ] && echo "✓ config.yaml.example OK" || echo "✗ ERREUR"

# Test 3: Pas de JWT token dans les fichiers
grep -r "eyJ" ~/dev/lyra/*.yaml ~/dev/lyra/*.example 2>/dev/null && echo "✗ SECRET TROUVÉ!" || echo "✓ Pas de JWT"

# Test 4: Variables d'env utilisées
grep -q '\${N8N_API_KEY}' ~/dev/lyra/config.yaml.example && echo "✓ Var env OK" || echo "✗ ERREUR"

# Test 5: modules/config.py existe
[ -f ~/dev/lyra/modules/config.py ] && echo "✓ config.py OK" || echo "✗ ERREUR"
```

## Checklist
- [ ] .env.example créé
- [ ] config.yaml.example créé
- [ ] modules/config.py créé
- [ ] Aucun secret dans les fichiers example
- [ ] Variables ${...} utilisées pour secrets
