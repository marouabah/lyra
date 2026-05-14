# Architecture Lyra - Notes de Synthèse

## Vue d'Ensemble

Lyra = **Assistant DevOps vocal français 100% local** pour gérer VMs KVM, backups et domotique.

## Deux Architectures

### V1 (Legacy) - Monolithique
```
User → Ollama Qwen 14B → JSON Tool Call → Confirmation → MCP/n8n → Résultat → TTS
```
- **Modèle**: Qwen 2.5 Coder 14B (~10 GB VRAM)
- **Force**: Simple, directe
- **Faiblesse**: Consomme beaucoup de VRAM, pas de spécialisation

### V2 (RAG - ACTUEL) - Dual Models
```
User → IntentClassifier → [demande/info/discussion]
            │
    ┌───────┴────────┐
    ▼                ▼
[demande]     [info/discussion]
    │                │
    ▼                ▼
RAG Hybrid        LYRA (réponse)
(Semantic+BM25)
    │
    ▼
TOON Encode (~40% tokens économisés)
    │
    ▼
EPHAISTOS (Qwen 7B)
    │
    ▼
HESTIA (MCP Execution)
    │
    ▼
LYRA (formatage réponse)
    │
    ▼
Output (texte/vocal)
```

## Composants Principaux V2

| Composant | Modèle | Rôle | VRAM |
|-----------|--------|------|------|
| **IntentClassifier** | Llama 3.2 3B | Tri demande/info/discussion | ~2.5 GB |
| **EPHAISTOS** | Qwen 2.5 Coder 7B | Backend: analyse specs MCP, extraction args | ~5 GB |
| **LYRA** | Llama 3.2 3B | Frontend: dialogue, personnalité | ~2.5 GB |
| **HESTIA** | - | Exécution MCP, gestion erreurs | 0 GB |
| **RAG** | ChromaDB + BM25 | Recherche specs MCP | ~0.5 GB |
| **TOON** | Python natif | Encodeur compact specs (~40% économie) | 0 GB |

**VRAM Total Estimé**: ~10.5 GB (RTX 3080 Ti 12GB)

## Flux de Traitement

1. **Input utilisateur** (texte ou vocal via Whisper)
2. **IntentClassifier** classe en 3 types:
   - `demande` → Action MCP (ex: "démarre preprod-09")
   - `info` → Question connaissance (ex: "c'est quoi vm_clone")
   - `discussion` → Conversation (ex: "salut")
3. **Si demande**:
   - RAG Hybrid recherche specs MCP pertinentes
   - TOON encode specs en format compact (~40% tokens)
   - EPHAISTOS analyse et extrait arguments
   - Si args manquants → LYRA demande clarification
   - Si args complets → HESTIA exécute MCP
   - LYRA formate résultat pour user
4. **Si info**: RAG + LYRA répond directement
5. **Si discussion**: LYRA dialogue naturellement
6. **Output** (texte ou TTS via Piper)

## Modes de Fonctionnement

- **default**: Confirmation obligatoire, read-first, TTS, verbose
- **performance**: Skip confirmation domotique (JAMAIS pour VM/backup), fast, pas de TTS

## Stack Technique

- **LLMs**: Ollama (Qwen 7B + Llama 3B)
- **RAG**: ChromaDB + rank-bm25
- **Embeddings**: paraphrase-multilingual-MiniLM-L12-v2
- **MCP**: 5 serveurs (fedora, tv, hue, catt, denon) = 80 outils
- **STT/TTS**: faster-whisper (CUDA) + Piper (fr_FR-upmc-medium)
- **Async**: n8n webhooks + fallback subprocess
- **Notifications**: Discord webhooks

## Points d'Entrée

- **main_rag.py**: V2 RAG (défaut)
- **main.py**: V1 legacy
- **run.sh**: Script de lancement avec options (`--vocal`, `-p`, `--legacy`)
