# Mode Debug - RAG Enhanced

## 🔍 Activer le Mode Debug

### Via l'alias lyra
```bash
lyra --debug
```

### Via run.sh
```bash
./run.sh --rag-enhanced --debug
```

### Combiner avec d'autres flags
```bash
lyra --debug --vocal      # Debug + mode vocal
lyra --debug -p           # Debug + mode performance
```

---

## 📊 Informations Affichées

Quand le mode debug est actif, chaque query affiche :

### 🔧 Étapes du Pipeline

```
================================================================================
🔍 DEBUG - Pipeline Enhanced
================================================================================
[1] Slang Normalization:
    Input:  'start preprod-09'
    Output: 'démarre preprod-09'

[2] Synonym Expansion: +7 tokens
    'démarre preprod-09 lance boot active machine serveur instance virtuelle...'

[3] RAG Retrieval:
    Score: 0.850
    Source: v2_fallback

[4] Confidence Cascade:
    Action: execute
    Level: MEDIUM (0.60-0.85)

[5] Context Injection: NON

[6] Tool Final:
    Name: fedora.vm_start
    Args: {'vm_name': 'preprod-09'}

📊 Performance Metrics:
    slang_latency_ms         :   0.09ms
    synonym_latency_ms       :   0.02ms
    rag_latency_ms           :  18.50ms
    cascade_latency_ms       :   0.15ms
    feedback_latency_ms      :   0.08ms
    TOTAL                    :  18.84ms
    ✅ Overhead <50ms (objectif)
================================================================================
```

---

## 🎯 Exemples de Tests

### Test 1 : Slang Normalization
```bash
lyra --debug

>>> start preprod-09
# Vérifie que "start" → "démarre"
```

### Test 2 : Synonym Expansion
```bash
>>> lance la vm
# Vérifie que "lance" est étendu avec "démarre", "boot", "active"...
```

### Test 3 : Confidence Cascade
```bash
>>> fais un backup
# Vérifie le niveau de confiance (devrait être MEDIUM ~0.70)
# Devrait proposer backup_create ET vm_snapshot
```

### Test 4 : Context Injection
```bash
>>> démarre preprod-09
# [Action 1] vm_start

>>> fais un snapshot
# Vérifie [5] Context Injection: OUI
# Le contexte devrait injecter vm_name="preprod-09"
```

### Test 5 : Performance Totale
```bash
>>> allume les lumières
# Vérifie que TOTAL <50ms (objectif)
```

---

## 📈 Interprétation des Métriques

### Slang Normalization (<1ms attendu)
- ✅ <0.5ms : Excellent
- ⚠️ 0.5-1ms : Acceptable
- ❌ >1ms : Trop lent, dict trop grand ?

### Synonym Expansion (<1ms attendu)
- ✅ <0.5ms : Excellent
- ⚠️ 0.5-1ms : Acceptable
- ❌ >1ms : Trop lent, dict trop grand ?

### RAG Retrieval (<30ms attendu)
- ✅ <20ms : Excellent
- ⚠️ 20-30ms : Acceptable
- ❌ >30ms : Trop lent, collection trop grande ?

### Overhead Total (<50ms objectif)
- ✅ <25ms : Excellent
- ⚠️ 25-50ms : Acceptable
- ❌ >50ms : Dépasse l'objectif

---

## 🔍 Debug Avancé

### Logs Complets
```bash
# Activer tous les logs (très verbeux)
tail -f logs/rag_enhanced_metrics.jsonl | jq .
```

### Profiling
```python
import cProfile
import pstats

# Dans le code
profiler = cProfile.Profile()
profiler.enable()
result = pipeline.process(query)
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumtime')
stats.print_stats(20)  # Top 20 fonctions
```

---

## 🐛 Problèmes Courants

### Slang ne normalise pas
**Symptôme** : `[1] Slang Normalization: (inchangé)` alors que le mot devrait être normalisé

**Debug** :
```python
from lyra.rag_enhanced.slang_normalizer import SlangNormalizer
norm = SlangNormalizer(enabled=True)
print(norm.slang_dict)  # Vérifier si le mot est dans le dict
print(norm.normalize("start"))  # Tester directement
```

### RAG score trop bas
**Symptôme** : Score <0.60 pour une query qui devrait matcher

**Debug** :
```python
from lyra.core.pipeline import Pipeline
from lyra.core.config import RAGConfig
config = RAGConfig.from_yaml("config.yaml")
pipeline = Pipeline(config=config)
pipeline.initialize()

# Test semantic
sem = pipeline._semantic.search("démarre vm", top_k=5)
for r in sem:
    print(f"{r.metadata.get('name')}: {r.score:.3f}")

# Test keyword
kw = pipeline._keyword.search("démarre vm", top_k=5)
for r in kw:
    print(f"{r.metadata.get('name')}: {r.score:.3f}")
```

### Overhead trop élevé
**Symptôme** : TOTAL >50ms régulièrement

**Analyse** :
1. Identifier l'étape la plus lente dans les métriques
2. Si RAG >30ms : collection trop grande ?
3. Si slang/synonym >1ms : dict trop grand ?
4. Si context >10ms : DB SQLite lente ?

---

## 💡 Tips

### Désactiver un composant temporairement
```yaml
# Dans config.yaml
rag_enhanced:
  slang_normalizer:
    enabled: false  # Désactiver pour isoler le problème
```

### Comparer V2 vs Enhanced
```bash
# Terminal 1 : V2 standard
./run.sh
>>> démarre preprod-09

# Terminal 2 : Enhanced avec debug
lyra --debug
>>> démarre preprod-09

# Comparer les timings
```

---

**Dernière mise à jour** : 2026-02-13
**Session** : Tests Live + Mode Debug

