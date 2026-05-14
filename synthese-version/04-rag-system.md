# RAG System - Notes de Synthèse

## Vue d'Ensemble

**Hybrid RAG**: Sémantique (embeddings) + Keyword (BM25) fusionnés via RRF.

## Composants

### Semantic Retriever

**Fichier**: `lyra/rag/semantic_retriever.py`
**Backend**: ChromaDB
**Embeddings**: `paraphrase-multilingual-MiniLM-L12-v2`

#### Rôle

Recherche sémantique dans les specs MCP par similarité vectorielle.

#### Méthodes

```python
def initialize():
    """Initialise ChromaDB + collection."""
    - Persist directory: .chromadb
    - Collection: lyra_mcp_specs_v2
    - Distance: cosine

def add_documents(documents, metadatas, ids):
    """Ajoute docs à ChromaDB."""
    - Documents: specs MCP (texte)
    - Metadatas: {name, server, category}
    - IDs: {server}_{tool_name}

def search(query, top_k=10):
    """Recherche sémantique."""
    1. Embed query
    2. Query ChromaDB (cosine similarity)
    3. Return top_k results
    4. Format: list[SemanticResult]
```

#### SemanticResult

```python
@dataclass
class SemanticResult:
    document: str        # Spec MCP complète
    metadata: dict       # {name, server, category}
    score: float         # Similarité (0-1)
    doc_id: str          # {server}_{tool_name}
```

### Keyword Retriever

**Fichier**: `lyra/rag/keyword_retriever.py`
**Backend**: rank-bm25 (Python natif)

#### Rôle

Recherche keyword (mots-clés) avec BM25 (TF-IDF amélioré).

#### Méthodes

```python
def add_documents(documents, metadatas, ids):
    """Indexe docs pour BM25."""
    1. Tokenize documents (lowercase)
    2. Build BM25 index
    3. Store metadatas + ids

def search(query, top_k=10):
    """Recherche BM25."""
    1. Tokenize query
    2. Score tous les docs (BM25)
    3. Return top_k results
    4. Format: list[KeywordResult]
```

#### KeywordResult

```python
@dataclass
class KeywordResult:
    document: str
    metadata: dict
    score: float
    doc_id: str
```

### RRF Fusion

**Fichier**: `lyra/rag/fusion.py`
**Algorithme**: Reciprocal Rank Fusion

#### Rôle

Fusionne résultats sémantique + keyword en un seul ranking.

#### Méthode

```python
def fuse(semantic_results, keyword_results, top_k=5):
    """Fusion RRF."""
    1. Pour chaque doc:
       - score_sem = 1 / (k + rank_sem)
       - score_kw = 1 / (k + rank_kw)
       - score_final = score_sem + score_kw
    2. Trier par score_final
    3. Return top_k
    4. Format: list[FusedResult]

    Params:
    - k = 60 (config.rag.retrieval.rrf_k)
```

#### FusedResult

```python
@dataclass
class FusedResult:
    document: str
    metadata: dict
    score: float        # Score RRF fusionné
    doc_id: str
    sources: dict       # {semantic: score, keyword: score}
```

---

## Configuration RAG

**Fichier**: `config.yaml`

```yaml
rag:
  enabled: true
  chromadb:
    persist_directory: ".chromadb"
    collection_name: "lyra_mcp_specs_v2"
    embedding_model: "paraphrase-multilingual-MiniLM-L12-v2"
  retrieval:
    semantic_top_k: 10      # Candidats sémantiques
    keyword_top_k: 10       # Candidats keywords
    fusion_top_k: 5         # Résultats finaux fusionnés
    rrf_k: 60               # Paramètre RRF
```

---

## Indexation MCP

**Processus** (dans `pipeline.py`):

```python
def _index_all_mcp_tools():
    """Indexe tous les outils MCP au démarrage."""
    1. Récupérer tools depuis HESTIA.get_available_tools()
    2. Pour chaque tool:
       - Construire document:
         ```
         Outil: {name}
         Serveur: {server}
         Description: {enriched_description}
         Parametres obligatoires: {required}
         Parametres optionnels: {optional}
         Schema:
           - {param} ({type}): {desc}
         ```
       - Enrichir description avec mots-clés FR
       - Metadata: {name, server, category}
       - ID: {server}_{name}
    3. Vider ChromaDB existant
    4. Ajouter à ChromaDB (semantic)
    5. Ajouter à BM25 (keyword)
```

**Documents indexés**: ~80 outils MCP

---

## Enrichissements FR

**60+ mots-clés français** ajoutés aux descriptions:

```python
FRENCH_ENRICHMENTS = {
    "turn_on": "allumer allume activer active",
    "turn_off": "eteindre eteins eteint desactiver desactive",
    "set_brightness": "luminosite intensite baisse baisser diminue diminuer",
    "vm_clone": "cloner clone copier copie dupliquer",
    "cast_youtube": "caster caste diffuser url lien video",
    # ... 60+ enrichissements
}
```

**Serveurs enrichis**:

```python
server_names = {
    "hue": "philips hue lumieres lampes eclairage domotique",
    "tv": "television philips tele ecran domotique",
    "catt": "chromecast cast diffusion streaming video",
    "fedora": "vm machine virtuelle kvm backup sauvegarde serveur",
}
```

---

## Pré-Filtrage par Catégorie

**Boost résultats** selon détection de mots-clés:

```python
CATEGORY_KEYWORDS = {
    "hue": ["lumiere", "lumieres", "lampe", "hue", "brightness"],
    "tv": ["tv", "tele", "volume", "ambilight", "netflix"],
    "catt": ["cast", "caste", "caster", "chromecast", "diffuser"],
    "fedora": ["vm", "machine virtuelle", "backup", "snapshot", "kvm"],
}
```

**Priorité spéciale**: "caste" → CATT même si "tv" présent.

---

## Boost Listing

Si requête contient mots de listing:

```python
LIST_VERBS = ["liste", "lister", "quels", "quelles", "donne", "montre"]
```

→ Boost outils `get_all_*`, `list_*`, `*_status` en tête.

---

## Session Memory

**Fichier**: `lyra/rag/session_memory.py`

### Rôle

Gestion du contexte multi-tour + actions/choix en attente.

### Structures

```python
@dataclass
class Turn:
    user_input: str
    assistant_response: str
    tool_call: Optional[dict]
    tool_result: Optional[str]
    timestamp: datetime

@dataclass
class PendingAction:
    tool_name: str
    known_args: dict
    missing_args: list[str]
    clarification_question: str

@dataclass
class PendingChoice:
    choice_type: str           # "server_selection"
    options: list[str]         # ["fedora", "tv", "hue", "catt", "tous"]
    question: str
```

### Méthodes

```python
def add_turn(user_input, assistant_response, tool_call, tool_result):
    """Ajoute un tour à l'historique."""

def set_pending_action(tool_name, known_args, missing_args, question):
    """Définit action en attente."""

def get_pending_action() -> Optional[PendingAction]:
    """Retourne action en attente."""

def set_pending_choice(choice_type, options, question):
    """Définit choix en attente (menu)."""

def get_context_for_llm(include_tools=True, use_toon=True):
    """Génère contexte pour LLM."""
    - Si use_toon=True → format TOON (~35% tokens)
    - Sinon → format texte classique
```

### Configuration

```yaml
session:
  max_turns: 10
```

---

## Performance

**Latence estimée** (RTX 3080 Ti):

- Semantic search (ChromaDB): ~50-100 ms
- Keyword search (BM25): ~10-30 ms
- Fusion RRF: ~5 ms
- **Total RAG**: ~70-150 ms

**Économie tokens**:

- TOON encoding specs: ~40% économie
- TOON encoding history: ~35% économie
