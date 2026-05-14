# Modèles LLM - Notes de Synthèse

## Vue d'Ensemble

**Dual Models Architecture**: 2 modèles spécialisés au lieu d'un seul monolithique.

## EPHAISTOS - Backend Analyste

**Fichier**: `lyra/models/ephaistos.py`
**Modèle**: Qwen 2.5 Coder 7B
**VRAM**: ~5 GB
**Température**: 0.1 (très déterministe)

### Rôle

Analyser specs MCP et extraire arguments des requêtes utilisateur.

### System Prompt

**Format**: JSON uniquement, 0 texte explicatif.

**Structure de réponse**:
```json
{
  "tool": "nom_outil",
  "arguments": {"arg1": "val1"},
  "missing_args": ["arg_manquant"],
  "confidence": 0.95,
  "reasoning": "explication interne"
}
```

**Règles critiques**:
- Arguments optionnels avec défaut → PAS dans missing_args
- ATTENTION aux VERBES:
  - allumer/allume/active → ON (pas OFF!)
  - éteindre/éteint/désactive → OFF (pas ON!)
  - monter/augmenter → up
  - baisser/diminuer → down/set_brightness (PAS turn_off!)

### Exemples Intégrés

**90+ exemples** dans le prompt pour chaque MCP:

- **FEDORA** (17 exemples): vm_start, vm_stop, vm_clone, vm_snapshot, backup_create...
- **HUE** (15 exemples): turn_on/off_group, set_brightness, set_color_rgb...
- **TV** (10 exemples): power_on/off, volume_up/down/set, launch_app...
- **CATT** (8 exemples): cast_youtube, cast_stop, cast_pause, cast_seek...
- **MERMAID** (10 exemples): generate_diagram, show_diagram, list_diagrams...

### Format TOON

**Support natif** pour specs compactes:

```
[2]{outil,serveur,desc,req,opt,schema}:
turn_on_group,hue,Allume les lumieres,,group_id,"group_id(integer):ID"
turn_off_group,hue,Eteint les lumieres,,group_id,"group_id(integer):ID"
```

→ ~40% économie tokens vs texte complet.

### Méthodes Principales

```python
def analyze_with_retry(user_query, mcp_specs, specs_toon):
    """Analyse avec retry si TOON échoue."""
    1. Essayer avec specs_toon (compact)
    2. Si échec → retry avec specs complets
    3. Parse JSON response
    4. Return EphaistosAnalysis

def extract_missing_args(analysis, user_response):
    """Extrait args depuis réponse user."""
    1. Construire prompt avec args manquants
    2. Appeler EPHAISTOS
    3. Fusionner known_args + nouveaux
    4. Return updated analysis
```

### EphaistosAnalysis

```python
@dataclass
class EphaistosAnalysis:
    tool: Optional[str]
    arguments: dict
    missing_args: list[str]
    confidence: float
    reasoning: str
    raw_response: str

    @property is_ready → tool != None and len(missing_args) == 0
    @property needs_clarification → tool != None and len(missing_args) > 0
    @property no_match → tool == None
```

---

## LYRA - Frontend Dialogue

**Fichier**: `lyra/models/lyra_voice.py`
**Modèle**: Llama 3.2 3B
**VRAM**: ~2.5 GB
**Température**: 0.5 (créatif)

### Rôle

Dialogue friendly, personnalité, clarification, formatage résultats.

### Deux Modes Adaptatifs

#### Mode TTS (Vocal)

**Règles**:
- ZERO emoji
- Phrases courtes (1-2 max)
- Éviter acronymes ("machine virtuelle" pas "VM")
- Virgules pour pauses naturelles

**System prompt**: `LYRA_SYSTEM_PROMPT_TTS`

#### Mode TEXT (Interface texte)

**Règles**:
- ZERO emoji
- 1-2 phrases max
- Acronymes OK (VM, IP, SSH)
- Infos essentielles uniquement
- **Mentions fréquentes** EPHAISTOS/HESTIA pour immersion (style J.A.R.V.I.S.)

**System prompt**: `LYRA_SYSTEM_PROMPT_TEXT`

### Probabilités de Mentions

**Adaptatif selon mode**:

| Contexte | TTS | TEXT |
|----------|-----|------|
| Mention EPHAISTOS | 20% | 30% |
| Mention HESTIA (erreur) | 20% | 40% |
| Mention HESTIA (si EPHAISTOS) | 50% | 50% |

### Méthodes Principales

```python
def ask_clarification(missing_args, tool_name, known_args):
    """Génère question pour args manquants."""
    1. Décider mentions (random selon mode)
    2. Si 1 arg + template → utiliser template
    3. Sinon → LLM génère question naturelle
    4. Return LyraResponse

def generate_acknowledgement(intent, query):
    """ACK immédiat (Phase 4)."""
    # Ex: "D'accord, je démarre preprod-09..."

def confirm_action(tool_name, arguments):
    """Message confirmation avant exécution."""
    # Ex: "Je clone preprod-09 en test-vm ?"

def format_result(tool_name, result, success):
    """Formate résultat MCP."""
    # Ex: "Parfait ! La VM preprod-09 est démarrée, IP 192.168.122.146."

def format_error(tool_name, error):
    """Formate erreur."""
    # Ex: "Ah mince, timeout expiré. On peut réessayer ?"
```

### Templates de Questions

**60+ templates** pré-définis par type d'argument:

```python
QUESTION_TEMPLATES = {
    "vm_name": [
        "Quelle VM tu veux {action}?",
        "C'est pour quelle machine virtuelle?",
    ],
    "source_vm": [
        "Quelle VM tu veux cloner?",
    ],
    "new_vm_name": [
        "Comment tu veux appeler la nouvelle VM?",
    ],
    # ...
}
```

### Verbes d'Action FR

**Mapping outil → verbe français**:

```python
ACTION_VERBS = {
    "vm_start": "demarrer",
    "vm_stop": "arreter",
    "vm_clone": "cloner",
    "vm_snapshot": {
        "list": "lister les snapshots de",
        "create": "creer un snapshot de",
        "revert": "restaurer un snapshot de",
        "delete": "supprimer un snapshot de",
    },
    # ...
}
```

### LyraResponse

```python
@dataclass
class LyraResponse:
    text: str
    mentions_ephaistos: bool
    mentions_hestia: bool
```

---

## IntentClassifier - Agent de Décision

**Fichier**: `lyra/models/intent_classifier.py`
**Modèle**: Llama 3.2 3B (même que LYRA)
**VRAM**: Partagé avec LYRA

### Rôle

Classification **rapide** des intentions: demande / info / discussion.

### Intents

```python
class Intent(Enum):
    DEMANDE = "demande"      # Action MCP
    INFO = "info"            # Question connaissance
    DISCUSSION = "discussion" # Conversation
```

### System Prompt

**Ultra-minimal** pour vitesse:

```python
CLASSIFIER_SYSTEM_PROMPT = """
Reponds UNIQUEMENT par JSON: {"intent": "demande|info|discussion"}

REGLES:
- demande = FAIRE quelque chose (demarrer, arreter, allumer, lister...)
- info = QUESTION sur comment ca marche, c'est quoi...
- discussion = salutations, remerciements, bavardage
"""
```

### Exemples

```python
"demarre la vm" → {"intent": "demande"}
"quels sont mes backups" → {"intent": "demande"}
"c'est quoi vm_clone" → {"intent": "info"}
"salut" → {"intent": "discussion"}
```

### Méthode

```python
def classify(query: str) -> ClassificationResult:
    1. Prompt minimal: 'Classifie: "{query}"'
    2. Appeler LYRA (rapide)
    3. Parse JSON response
    4. Fallback: si échec → Intent.DEMANDE (défaut)
    5. Return ClassificationResult
```

### ClassificationResult

```python
@dataclass
class ClassificationResult:
    intent: Intent
    confidence: float
    raw_response: str
```

---

## ModelManager - Orchestrateur

**Fichier**: `lyra/models/model_manager.py`
**Rôle**: Wrapper Ollama pour EPHAISTOS + LYRA.

### Méthodes

```python
def call_ephaistos(prompt, system_prompt, specs_toon=None):
    """Appelle Qwen 7B."""

def call_lyra(prompt, system_prompt):
    """Appelle Llama 3B."""

def check_models_available():
    """Vérifie que modèles sont pullés."""

def get_stats():
    """Retourne stats d'utilisation."""
```

### Configuration

```yaml
models:
  ephaistos:
    name: "qwen2.5-coder:7b"
    temperature: 0.1
  lyra:
    name: "llama3.2:3b"
    temperature: 0.5
```

---

## Récapitulatif

| Composant | Modèle | Température | Rôle Principal |
|-----------|--------|-------------|----------------|
| **EPHAISTOS** | Qwen 7B | 0.1 | Analyse specs, extraction args |
| **LYRA** | Llama 3B | 0.5 | Dialogue, clarification, formatage |
| **IntentClassifier** | Llama 3B | 0.5 | Classification rapide |

**Total VRAM LLMs**: ~7.5 GB (partagé entre LYRA et IntentClassifier)
