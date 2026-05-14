# Guide de Test - RAG Enhanced

## 🎯 Résumé Diagnostic

**Date**: 2026-02-13
**Status**: ✅ TOUS LES COMPOSANTS FONCTIONNELS

| Étape | Composant | Performance | Status |
|-------|-----------|-------------|--------|
| 1 | SlangNormalizer | ~0.09ms | ✅ |
| 2 | SynonymExpander | ~0.02ms | ✅ |
| 3 | RAG Retrieval | ~16ms | ✅ |
| 4 | Pipeline Complet | ~18ms | ✅ |

**Overhead total**: 18ms (objectif <50ms) ✅

---

## 🔧 Environnement

- ✅ **ChromaDB 1.4.1** + **Pydantic 2.12.5** = Compatible
- ✅ **Collections**: lyra_mcp_specs_v2 (85 docs)
- ✅ **Dictionnaires**: slang_dict.json (109 patterns), synonym_dict.json (39 termes)
- ✅ **Ollama**: qwen2.5-coder:7b + llama3.2:3b running

---

## 🚀 Tests Automatisés

### 1. Diagnostic Rapide (13s)
```bash
source .venv/bin/activate
python tests/debug/diagnose.py
```

**Ce qu'il teste** :
- SlangNormalizer : 4 transformations
- SynonymExpander : 3 expansions
- RAG : Semantic + Keyword sur 4 queries
- Pipeline : Flow complet sur 3 queries

**Résultat attendu** : `✅ Tous les composants fonctionnent !`

---

### 2. Tests Composants (sans MCP, 30s)
```bash
source .venv/bin/activate
python tests/debug/test_live.py
```

**Ce qu'il teste** :
- 5 tests SlangNormalizer
- 5 tests SynonymExpander
- 1 test ContextInjector
- RAG retrieval complet
- ConfidenceCascader (5 seuils)

**Résultat attendu** : `11/11 tests passed`

---

## 🎮 Tests Interactifs (Avec LYRA)

### Mode 1 : RAG V2 Standard (sans Enhanced)
```bash
./run.sh
```

**Prompts de test** :
```
>>> démarre preprod-09
# Devrait appeler vm_start avec vm_name="preprod-09"

>>> allume les lumières de la chambre
# Devrait appeler hue.turn_on_group group_name="chambre"

>>> clone preprod-09 en test-clone
# Devrait appeler vm_clone avec source + destination

>>> éteins la télé
# Devrait appeler tv.power_off

>>> caste cette vidéo youtube
# Devrait appeler cast_youtube
```

---

### Mode 2 : RAG Enhanced (avec Slang + Synonym)
```bash
./run.sh --rag-enhanced
```

**Prompts de test avec slang/anglicismes** :
```
>>> start preprod-09
# Slang: "start" → "démarre"
# Devrait appeler vm_start

>>> stop la vm preprod-09
# Slang: "stop" → "arrête"
# Devrait appeler vm_stop

>>> switch les lights de la chambre
# Slang: "switch" → "allume", "lights" → "lumières"
# Devrait appeler hue.turn_on_group

>>> cast cette video youtube
# Slang: "cast" → "diffuse"
# Devrait appeler cast_youtube

>>> backup preprod-09
# Slang: "backup" → "sauvegarde"
# Devrait proposer backup_create OU vm_snapshot (ambiguïté)
```

---

### Mode 3 : Test Contexte Multi-tour
```bash
./run.sh --rag-enhanced
```

**Scénario A: Clone VM avec contexte**
```
>>> démarre preprod-09
# [Action 1] vm_start

>>> fais un snapshot
# [Contexte] last_mcp=vm_start, last_server=FEDORA
# Devrait proposer vm_snapshot avec vm_name="preprod-09" (contexte)

>>> clone cette vm en test-clone
# [Contexte] last_mcp=vm_snapshot, vm_name="preprod-09"
# Devrait appeler vm_clone avec source="preprod-09"
```

**Scénario B: Domotique avec contexte**
```
>>> allume les lumières du salon
# [Action 1] hue.turn_on_group group_name="salon"

>>> mets en rouge
# [Contexte] last_mcp=hue.turn_on_group, last_group="salon"
# Devrait appeler hue.set_group_color_rgb group_name="salon", color="red"

>>> baisse à 30%
# [Contexte] last_mcp=hue.set_group_color_rgb, last_group="salon"
# Devrait appeler hue.set_group_brightness group_name="salon", brightness=30
```

---

## 🧪 Tests Edge Cases

### Ambiguïté (Confidence MEDIUM)
```
>>> fais un backup
# Ambiguïté: backup_create vs vm_snapshot (score ~0.70-0.75)
# Devrait proposer les 2 options + demander clarification
```

### Hors scope (Confidence LOW)
```
>>> quel temps fait-il demain
# Aucun MCP adapté (score <0.60)
# Devrait fallback LYRA avec réponse "Je ne peux pas..."
```

### Multi-step complexe
```
>>> mets le salon en bleu tamisé
# Devrait décomposer en:
# 1. hue.set_group_color_rgb group="salon", color="blue"
# 2. hue.set_group_brightness group="salon", brightness=30
# OU proposer menu si MCP ne supporte pas multi-args
```

---

## 🔍 Vérifications Manuelles

### 1. Logs Enhanced

Activer logs verbose dans `config.yaml`:
```yaml
rag_enhanced:
  enabled: true
  metrics:
    enabled: true
    log_path: "logs/rag_enhanced_metrics.jsonl"
```

Puis lancer:
```bash
./run.sh --rag-enhanced
>>> start preprod-09
# Vérifier dans logs:
# - SlangNormalizer: "start" → "démarre"
# - SynonymExpander: +N tokens
# - RAG score: >0.85
# - Tool final: vm_start
```

### 2. Métriques Performance

```bash
tail -f logs/rag_enhanced_metrics.jsonl | jq .
```

**Métriques attendues par query** :
- `slang_latency_ms`: <1ms
- `synonym_latency_ms`: <1ms
- `rag_latency_ms`: <30ms
- `cascade_latency_ms`: <2ms
- `context_latency_ms`: <10ms (si injecté)
- `feedback_latency_ms`: <2ms
- **total_latency_ms**: <50ms

---

## 🐛 Debug en Cas de Problème

### Problème 1: SlangNormalizer ne normalise pas

**Symptôme**: "start" reste "start" au lieu de "démarre"

**Debug**:
```python
from lyra.rag_enhanced.slang_normalizer import SlangNormalizer
normalizer = SlangNormalizer(enabled=True)
print(len(normalizer.slang_dict))  # Devrait être 109
print(normalizer.normalize("start preprod-09"))  # Devrait être "démarre preprod-09"
```

**Fix**: Vérifier `config.yaml` → `rag_enhanced.slang_normalizer.enabled: true`

---

### Problème 2: RAG ne trouve aucun résultat

**Symptôme**: "No results" pour toutes les queries

**Debug**:
```bash
source .venv/bin/activate
python -c "
import chromadb
client = chromadb.PersistentClient(path='.chromadb')
col = client.get_collection('lyra_mcp_specs_v2')
print(f'Documents: {col.count()}')
"
```

**Fix**: Si count=0, ré-indexer avec:
```bash
source .venv/bin/activate
python scripts/index_mcp_specs.py
```

---

### Problème 3: Ollama timeout

**Symptôme**: "Connection timeout" lors de l'appel EPHAISTOS/LYRA

**Debug**:
```bash
curl http://localhost:11434/api/tags
# Devrait lister les modèles dont qwen2.5-coder:7b et llama3.2:3b
```

**Fix**: Relancer Ollama:
```bash
systemctl --user restart ollama
# ou
ollama serve
```

---

### Problème 4: MCP timeout

**Symptôme**: "MCP execution failed" après 120s

**Debug**:
```bash
# Tester MCP manuellement (exemple FEDORA)
node /home/amineutron/dev/fedora-setup/scripts/agents/mcp-server/dist/index.js
# Devrait démarrer le serveur MCP
```

**Fix**: Vérifier config MCP servers dans `config.yaml` → `mcp.servers`

---

## 📊 Matrice de Compatibilité

| Mode | Slang | Synonym | Context | RAG 3-Tier | Cascade | Feedback | Overhead |
|------|-------|---------|---------|------------|---------|----------|----------|
| **V2 Pur** | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ | 0ms |
| **Enhanced Léger** | ✓ | ✓ | ✗ | ✗ | ✓ | ✓ | <5ms |
| **Enhanced Complet** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | <50ms |

**Config actuelle** : Enhanced Léger (3-Tier désactivé car sous-peuplé)

---

## 🎯 Scénarios de Validation Complets

### Scénario 1: HUE - Allume lumières (Slang + Synonym)
```bash
./run.sh --rag-enhanced
>>> allume les lumières de la chambre
```
**Attendu**:
- Tool: `hue.turn_on_group`
- Args: `group_name="chambre"` ou `group_name="bedroom"`
- RAG score: >0.85

---

### Scénario 2: CATT - Cast vidéo YouTube (Slang)
```bash
./run.sh --rag-enhanced
>>> balance cette vidéo youtube sur la télé
```
**Attendu**:
- Slang: "balance" → "diffuse"
- Tool: `cast_youtube` ou `cast_url`
- RAG score: >0.85

---

### Scénario 3: TV - Éteindre (Slang)
```bash
./run.sh --rag-enhanced
>>> coupe la télé
```
**Attendu**:
- Slang: "coupe" → "éteins"
- Tool: `tv.power_off`
- RAG score: >0.85

---

### Scénario 4: FEDORA - Démarrer VM
```bash
./run.sh --rag-enhanced
>>> lance la vm de test
```
**Attendu**:
- Synonym: "lance" → "démarre"
- Tool: `vm_start`
- Args: `vm_name="test"` (extrait par EPHAISTOS)

---

### Scénario 5: DENON - Mute Home Cinema
```bash
./run.sh --rag-enhanced
>>> mute le home cinema
```
**Attendu**:
- Tool: `denon.mute_on` ou `denon.mute_toggle`
- RAG score: >0.85

---

### Scénario 6: CONTEXTE - Monte le volume (HDMI ARC ambiguïté)
```bash
./run.sh --rag-enhanced
>>> caste une vidéo
# [Action 1] cast_youtube

>>> monte le volume
# [Contexte] last_mcp=cast_youtube, last_server=CATT
```
**Attendu**:
- Tool: `cast_volume` (priorité CATT car contexte)
- Args: `volume=+10` (ou demande clarification)

---

### Scénario 7: CONTEXTE - Éteins tout (ambiguïté HUE vs TV+Denon)
```bash
./run.sh --rag-enhanced
>>> allume les lumières du salon
# [Action 1] hue.turn_on_group

>>> éteins tout
# [Contexte] last_mcp=hue.turn_on_group
```
**Attendu**:
- Tool: `hue.turn_off_all` (priorité HUE car contexte)

---

### Scénario 8: CASCADER - Fallback (aucun MCP adapté)
```bash
./run.sh --rag-enhanced
>>> quel temps fait-il demain
```
**Attendu**:
- RAG score: <0.60
- Cascade action: `fallback`
- Réponse LYRA: "Je ne peux pas consulter la météo..."

---

### Scénario 9: CASCADER - Ambiguïté backup
```bash
./run.sh --rag-enhanced
>>> fais un backup
```
**Attendu**:
- RAG score: 0.60-0.85 (MEDIUM)
- Cascade action: `propose`
- Options: backup_create OU vm_snapshot
- Pending args: demande clarification

---

### Scénario 10: PIPELINE - Multi-step HUE
```bash
./run.sh --rag-enhanced
>>> mets le salon en bleu tamisé
```
**Attendu**:
- Tool 1: `hue.set_group_color_rgb` (group="salon", color="blue")
- Tool 2: `hue.set_group_brightness` (group="salon", brightness=30)
- OU menu clarification si MCP ne supporte pas multi-args

---

## ✅ Checklist de Validation Finale

- [ ] SlangNormalizer : 109 patterns chargés
- [ ] SynonymExpander : 39 termes chargés
- [ ] RAG V2 : 85 documents indexés
- [ ] Ollama : qwen2.5-coder:7b + llama3.2:3b running
- [ ] Diagnostic complet : 4/4 étapes ✅
- [ ] Test interactif V2 : 5/5 prompts fonctionnent
- [ ] Test interactif Enhanced : 5/5 prompts avec slang fonctionnent
- [ ] Test contexte multi-tour : 2/2 scénarios fonctionnent
- [ ] Test edge cases : 3/3 scénarios (ambiguïté, fallback, multi-step) fonctionnent
- [ ] Overhead total : <50ms ✅
- [ ] Métriques loggées : logs/rag_enhanced_metrics.jsonl existe

---

## 🎓 Commandes Quick Reference

```bash
# Diagnostic rapide (13s)
python tests/debug/diagnose.py

# Tests automatisés (30s)
python tests/debug/test_live.py

# Lyra V2 standard
./run.sh

# Lyra RAG Enhanced
./run.sh --rag-enhanced

# Lyra + Vocal + Enhanced
./run.sh --vocal --rag-enhanced

# Logs en temps réel
tail -f logs/rag_enhanced_metrics.jsonl | jq .

# Vérifier collections ChromaDB
python -c "import chromadb; client = chromadb.PersistentClient(path='.chromadb'); col = client.get_collection('lyra_mcp_specs_v2'); print(f'Documents: {col.count()}')"

# Vérifier Ollama
curl http://localhost:11434/api/tags | jq -r '.models[].name'
```

---

**Dernière mise à jour** : 2026-02-13
**Session** : SESSION 8 - Tests Live Complets
**Score** : 110/100 ✅

