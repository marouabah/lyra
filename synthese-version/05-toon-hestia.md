# TOON & HESTIA - Notes de Synthèse

## TOON - Encodeur Compact

**Fichier**: `lyra/utils/toon.py`
**Nom complet**: Token-Oriented Object Notation

### Rôle

Format compact pour **réduire les tokens** envoyés aux LLMs.
Économie: **~35-40%** sur données structurées répétitives.

### Format

```
[count]{field1,field2,...}:
val1,val2,...
val1,val2,...
```

**Exemple**:

```
[2]{outil,serveur,desc,req,opt}:
turn_on_group,hue,Allume les lumieres,,group_id
turn_off_group,hue,Eteint les lumieres,,group_id
```

vs texte complet:

```
Outil: turn_on_group
Serveur: hue
Description: Allume les lumieres
Parametres obligatoires:
Parametres optionnels: group_id

Outil: turn_off_group
Serveur: hue
Description: Eteint les lumieres
Parametres obligatoires:
Parametres optionnels: group_id
```

**Tokens**: 35 (TOON) vs 68 (texte) = **48% économie**.

### Méthodes Principales

```python
def toon_encode(records: list[dict]) -> str:
    """Encode liste de dicts en TOON."""
    1. Extraire champs du 1er record
    2. Header: [count]{fields}:
    3. Pour chaque record:
       - Extraire valeurs dans l'ordre des champs
       - Quote si virgules/guillemets
       - Join par virgules
    4. Return header + lignes

def parse_spec(spec_text: str) -> dict:
    """Parse spec MCP (texte RAG) en dict."""
    1. Extraire: outil, serveur, desc, req, opt, schema
    2. Return dict structuré

def toon_encode_specs(specs: list[str]) -> str:
    """Encode specs MCP en TOON."""
    1. Parse chaque spec en dict
    2. Encode via toon_encode()
    3. Return TOON compact

def toon_encode_history(turns: list[Turn]) -> str:
    """Encode historique session en TOON."""
    1. Convertir tours en dicts
    2. Encode via toon_encode()
    3. Return TOON compact
```

### Utilisation

**Dans pipeline.py**:

```python
# Specs MCP
specs = [r.document for r in fused]
specs_toon = toon_encode_specs(specs)

# Analyse avec EPHAISTOS
analysis = ephaistos.analyze_with_retry(
    user_query=query,
    mcp_specs=specs,         # Texte complet (fallback)
    specs_toon=specs_toon    # TOON (prioritaire)
)
```

**Dans session_memory.py**:

```python
# Contexte session
context_toon = session.get_context_for_llm(use_toon=True)
```

### Fallback Automatique

Si EPHAISTOS échoue avec TOON → retry avec specs complètes.

**Raison**: TOON peut parfois perdre nuances pour specs complexes.

### Quoting

**Valeurs avec virgules/guillemets** sont quotées:

```python
def _quote_value(value: str) -> str:
    if "," in value or '"' in value or "\n" in value:
        return '"' + value.replace('"', '""') + '"'
    return value
```

### Tests

**30 tests unitaires** (100% passent):

```bash
pytest tests/unit/test_toon.py -v
```

---

## HESTIA - Executor MCP

**Fichier**: `lyra/hestia/executor.py`
**Nom**: HESTIA, déesse du foyer, gardienne de la maison.

### Rôle

**Exécutrice des tâches MCP** avec:
- Execution synchrone/asynchrone
- Collecte métriques
- Logging optionnel Notion
- Wrapper du MCPManager

### Architecture

```python
HestiaExecutor
    ├── MCPManager (modules/mcp.py)
    ├── MetricsCollector (metrics.py)
    └── NotionLogger (notion_logger.py, optionnel)
```

### Méthodes Principales

```python
def execute(tool_name, arguments, context=None):
    """Execute un outil MCP."""
    1. Log début (Notion si activé)
    2. MCPManager.call_tool(tool_name, arguments)
    3. Mesurer durée
    4. Enregistrer métriques
    5. Log fin (Notion)
    6. Return ExecutionResult

def get_available_tools():
    """Liste outils MCP disponibles."""
    return mcp_manager.get_all_tools()

def is_dangerous_tool(tool_name):
    """Vérifie si outil dangereux."""
    dangerous = ["vm_destroy", "vm_delete", "backup_restore", "backup_clean"]
    return base_name in dangerous

def is_async_tool(tool_name):
    """Vérifie si outil async (longue durée)."""
    return base_name in ASYNC_TOOLS

def get_async_info(tool_name):
    """Retourne infos async."""
    return {
        "estimated_time": "1-2 minutes",
        "description": "Clonage de VM"
    }
```

### ExecutionContext

```python
@dataclass
class ExecutionContext:
    user_query: str
    tool_name: str
    arguments: dict
    session_id: Optional[str]
    request_id: Optional[str]
    timestamp: datetime
```

### ExecutionResult

```python
@dataclass
class ExecutionResult:
    success: bool
    content: str
    error: Optional[str]
    duration_ms: float
    logged_to_notion: bool
```

### Outils Async

**Opérations longues** (1-30 min):

```python
ASYNC_TOOLS = {
    "vm_clone": {
        "estimated_time": "1-2 minutes",
        "description": "Clonage de VM"
    },
    "vm_clone_system": {
        "estimated_time": "10-30 minutes",
        "description": "Clonage du systeme complet"
    },
    "backup_create": {
        "estimated_time": "2-5 minutes",
        "description": "Creation de backup"
    },
    "backup_restore": {
        "estimated_time": "2-5 minutes",
        "description": "Restauration de backup"
    },
}
```

### MCPManager

**Fichier**: `modules/mcp.py`
**Rôle**: Gestion connexions MCP multi-serveurs.

#### Méthodes

```python
def call_tool(tool_name, arguments):
    """Appelle un outil MCP."""
    1. Déterminer serveur (prefixe ou auto-detect)
    2. Récupérer client MCP
    3. Appeler outil via stdio
    4. Parser résultat
    5. Return MCPResult

def get_all_tools():
    """Liste tous les outils de tous les serveurs."""
    1. Pour chaque serveur actif:
       - Lister outils (list_tools)
       - Ajouter _server metadata
    2. Return liste fusionnée (~80 outils)

def get_server_names():
    """Liste serveurs actifs."""
    return list(clients.keys())
```

#### MCPResult

```python
@dataclass
class MCPResult:
    success: bool
    content: str
    error: Optional[str]
```

#### Configuration MCP

**5 serveurs** (config.yaml):

```yaml
mcp:
  servers:
    fedora:         # VM KVM + Backups
      enabled: true
      command: node
      args: [/path/to/mcp-server/dist/index.js]
      timeout: 120

    tv:             # Philips TV
      enabled: true
      command: python
      args: [/path/to/pylips-mcp/server.py]
      timeout: 10

    hue:            # Philips Hue
      enabled: true
      command: python3
      args: [/path/to/hue-mcp/hue_server.py]
      timeout: 10

    catt:           # Cast YouTube
      enabled: true
      command: python3
      args: [/path/to/catt-mcp/server.py]
      timeout: 60

    denon:          # Home Cinema Denon
      enabled: true
      command: python3
      args: [/path/to/denon-mcp/server.py]
      timeout: 10
```

### Metrics Collector

**Fichier**: `lyra/hestia/metrics.py`

#### Collecte

```python
def record_execution(tool_name, success, duration_ms):
    """Enregistre une exécution."""
    - Total calls
    - Success/failure count
    - Latence moyenne par outil
    - Timestamp

def get_summary():
    """Retourne résumé métriques."""
    {
        "total_calls": 42,
        "success_rate": 0.95,
        "by_tool": {
            "vm_start": {"count": 5, "success": 5, "avg_ms": 1234},
            ...
        }
    }
```

### Notion Logger (Optionnel)

**Fichier**: `lyra/hestia/notion_logger.py`

#### Rôle

Logging structuré vers Notion database.

#### Méthodes

```python
def log_start(context):
    """Log début d'exécution."""
    - Timestamp
    - User query
    - Tool name
    - Arguments

def log_end(context, success, result, duration_ms):
    """Log fin d'exécution."""
    - Success/failure
    - Result/error
    - Duration
    - Update page
```

#### Configuration

```yaml
notion:
  enabled: false      # Désactivé par défaut
  database_id: null
  token: null
```

---

## Background Tasks

**Fichier**: `lyra/hestia/background_tasks.py`

### Rôle

Gestion des tâches longues en arrière-plan (async).

### BackgroundTaskManager

```python
def launch_task(tool_name, arguments, description, estimated_time, webhook_url):
    """Lance tâche en subprocess."""
    1. Générer task_id unique
    2. Créer script wrapper async_mcp_wrapper.py
    3. subprocess.Popen()
    4. Return task_id

def get_active_tasks():
    """Liste tâches en cours."""

def cleanup_completed(max_age_seconds=300):
    """Nettoie tâches terminées anciennes."""
```

### Workflow Async

```
User demande clone
    ↓
Pipeline.handle_action()
    ↓
Si is_async_tool:
    ↓
LYRA.generate_async_message()
    "Je lance le clonage en arrière-plan, ça prend ~1-2 min..."
    ↓
BackgroundTaskManager.launch_task()
    subprocess: async_mcp_wrapper.py --tool vm_clone --args {...}
    ↓
User continue à interagir
    ↓
(~60s plus tard)
    ↓
Callback Discord webhook: "✅ Clone terminé!"
```

### Discord Notifications

**Fichier**: `modules/n8n.py`

```python
def send_discord_notification(webhook_url, title, description, fields, color):
    """Envoie notification Discord."""
    - Embed riche avec fields
    - Color: vert (succès) / rouge (erreur)
    - Footer: "Lyra RAG v2.0 - DevOps Assistant"
```

**Configuration**:

```yaml
discord:
  webhook_url: "https://discord.com/api/webhooks/..."
  enabled: true
  notify_on:
    - async_complete
    - errors
```

---

## Récapitulatif

| Composant | Rôle | Fichier |
|-----------|------|---------|
| **TOON** | Encodeur compact (~40% tokens) | utils/toon.py |
| **HESTIA** | Exécuteur MCP + métriques | hestia/executor.py |
| **MCPManager** | Multi-serveurs MCP | modules/mcp.py |
| **BackgroundTasks** | Tâches async | hestia/background_tasks.py |
| **Metrics** | Collecte stats | hestia/metrics.py |
| **Notion** | Logging structuré | hestia/notion_logger.py |
