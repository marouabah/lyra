# Pipeline RAG - Notes de Synthèse

## Rôle

**Orchestrateur central** du workflow V2: reçoit requête user, route vers bons composants, retourne réponse.

## Fichier

`lyra/core/pipeline.py` (1936 lignes)

## Workflow Principal

```python
def process(query: str) -> PipelineResult:
    1. Vérifier choix en attente (PendingChoice)
    2. Vérifier action en attente (PendingAction)
    3. Router vers bon handler (_route_query)
```

### Routing (_route_query)

```python
1. Liste outils ? → _process_tools_query_step1()
2. IntentClassifier.classify(query)
   → Intent.DEMANDE → _process_action()
   → Intent.INFO → _process_knowledge()
   → Intent.DISCUSSION → _process_discussion()
3. Callback acknowledgement immédiat (Phase 4)
```

## Processus par Type

### Process Action (demande MCP)

```python
def _process_action(query):
    1. Retrieve specs MCP (_retrieve_specs)
       - Détection catégorie (hue/tv/catt/fedora)
       - Semantic search (ChromaDB)
       - Keyword search (BM25)
       - Fusion RRF (top_k=5)

    2. Encode TOON (~40% tokens)

    3. EPHAISTOS.analyze_with_retry(specs_toon)
       → EphaistosAnalysis

    4. Si no_match → "pas compris"

    5. Workflows spéciaux:
       - vm_clone → _handle_vm_clone_workflow()
       - vm_snapshot create → _handle_vm_snapshot_create_workflow()

    6. Si needs_clarification:
       - LYRA.ask_clarification()
       - session.set_pending_action()
       - return pending_args

    7. Si is_ready → _prepare_execution()
       - LYRA.confirm_action()
       - return tool_call
```

### Process Knowledge (question)

```python
def _process_knowledge(query):
    1. Retrieve specs MCP (RAG)
    2. LYRA.answer_knowledge(context=specs)
    3. Return response directement
```

### Process Discussion (conversation)

```python
def _process_discussion(query):
    1. LYRA.chat(query)
    2. Return response directement
```

## Workflows Spéciaux

### VM Clone Workflow

**6 étapes de validation**:

1. Lister VMs existantes (toujours afficher)
2. Demander source_vm si manquant
3. Vérifier que source existe
4. Demander new_vm_name avec suggestion
5. Valider que new_vm_name n'existe pas
6. **Vérifier état VM** (running ou arrêtée):
   - Si running → Proposer menu 3 options:
     1. Arrêter → Cloner → Redémarrer
     2. Arrêter → Cloner (sans redémarrage)
     3. Annuler
   - Si arrêtée → Préparer execution

**Fonction**: `_handle_vm_clone_workflow()` (lignes 1067-1298)

### VM Snapshot Create Workflow

**Nom par défaut automatique**:

1. Générer `snap-{vm_name}-{timestamp}`
2. Proposer avec "💡 Par défaut: ..."
3. Si réponse vide/"ok"/"default" → utiliser défaut
4. Valider `snapshot_name != vm_name` (auto-suffixage si égal)

**Fonction**: `_handle_vm_snapshot_create_workflow()` (lignes 1300-1353)

### VM Snapshot Restore Workflow

**Sécurité maximale** (4-6 points de validation):

1. Lister snapshots disponibles
2. Vérifier que snapshot existe
3. Afficher état VM
4. **Proposer snapshot de sécurité** (recommandé):
   - Option 1: Créer snapshot → Restaurer
   - Option 2: Restaurer directement
   - Option 3: Annuler
5. Si VM running → Arrêter avant restauration
6. Restaurer snapshot
7. Optionnel: Redémarrer VM
8. Notification Discord

**Fonction**: `_handle_snapshot_restore_with_safety()` (lignes 471-755)

## Retrieve Specs (RAG Hybrid)

```python
def _retrieve_specs(query):
    1. Détection catégorie cible
       - Mots-clés: "lumiere"→hue, "tv"→tv, "caste"→catt, "vm"→fedora
       - Priorité: "caste" → CATT même si "tv" présent

    2. Recherche sémantique (ChromaDB)
       - Embedding multilingue
       - top_k=10

    3. Recherche keyword (BM25)
       - rank-bm25
       - top_k=10

    4. Fusion RRF (Reciprocal Rank Fusion)
       - k=60
       - Fusionne semantic + keyword

    5. Boost par catégorie détectée
       - Résultats de la catégorie cible en tête

    6. Boost listing si "quels/liste"
       - get_all_*, list_*, *_status en tête

    7. Return top_k=5 final
```

## Enrichissements FR

**Pipeline ajoute des mots-clés français** aux specs MCP pour améliorer détection:

```python
FRENCH_ENRICHMENTS = {
    "turn_on": "allumer allume activer active",
    "turn_off": "eteindre eteins eteint desactiver desactive",
    "set_brightness": "luminosite intensite baisse baisser diminue",
    "vm_snapshot": "snapshot instantane capture sauvegarde",
    # ... 60+ enrichissements
}
```

## Indexation MCP

**Au démarrage** (`_index_all_mcp_tools()`):

1. Récupérer tous les outils depuis HESTIA
2. Pour chaque outil:
   - Construire doc: Outil, Serveur, Description enrichie, Params
   - Ajouter à ChromaDB (semantic)
   - Ajouter à BM25 (keyword)
3. Synchroniser keyword retriever avec ChromaDB

**Documents indexés**: ~80 outils MCP

## Session Memory

**Gestion du contexte multi-tour**:

- Historique des N derniers tours (max_turns=10)
- PendingAction (action en attente de clarification)
- PendingChoice (choix menu en attente)
- Contexte TOON encodable (~35% tokens)

## Exécution Action

```python
def execute_action(tool_name, arguments):
    1. Créer ExecutionContext
    2. HESTIA.execute(tool_name, arguments)
    3. Si listing tool → formater lisiblement
       Sinon → LYRA.format_result()
    4. Notification Discord si async tool
    5. Return PipelineResult
```

## Outils de Listing

**Formatage spécial** (JSON → texte lisible):

```python
LISTING_TOOLS = [
    "get_all_scenes", "get_all_lights", "get_all_groups",
    "vm_status", "backup_list", "cast_scan", ...
]
```

## Métriques

```python
def get_metrics():
    - Models stats (ModelManager)
    - Hestia stats (execution count, success rate)
    - Session stats (turns, has_pending)
```

## Callback Progressif (Phase 4)

**Feedback immédiat** avant exécution:

```python
callback("acknowledgement", ack)
# Ex: "D'accord, je démarre preprod-09..."
```

**Types de steps**:
- `acknowledgement`: Réponse immédiate
- `progress`: Progression (futur)
- `result`: Résultat final
