# TODO avant SESSION 7 (Pipeline Integration)

## Dépendances de Développement

**IMPORTANT** : Installer les dépendances dev avant SESSION 7 pour débloquer tous les tests de performance.

### Installation

```bash
pip install -r requirements-dev.txt
```

### Packages Critiques

| Package | Usage | Sessions |
|---------|-------|----------|
| **pytest-benchmark** | Benchmarks performance | S2, S3, S5, S7, S8 |
| pytest-cov | Couverture code | Toutes |
| ruff | Linter | S7, S8 |
| mypy | Type checking | S7, S8 |

### Vérification

```bash
# Vérifier pytest-benchmark installé
python -c "import pytest_benchmark; print('✅ pytest-benchmark OK')"

# Relancer tests performance SESSION 2
pytest tests/unit/rag_enhanced/test_slang_normalizer.py::TestSlangNormalizer::test_normalize_performance -v
# → Devrait passer au lieu d'être skipped
```

### Impact sur Scores

**Avant installation** :
- SESSION 2 : 96/100 (1 test skipped)
- SESSION 3 : ~96/100 (1 test skipped estimé)
- SESSION 5 : ~96/100 (1 test skipped estimé)

**Après installation** :
- SESSION 2 : 98/100 (+2 points)
- SESSION 3 : 98/100 (+2 points)
- SESSION 5 : 98/100 (+2 points)

**Total gain** : +6 points sur 3 sessions

### Alternative

Si pytest-benchmark pose problème (dépendances CUDA, etc.), les tests manuels alternatifs sont déjà en place :
- `test_normalize_performance_manual` (SESSION 2) ✅
- Tests similaires dans SESSION 3, 5, 7, 8

---

**Date limite** : Avant SESSION 7 (Pipeline Integration)

**Responsable** : À installer par l'utilisateur ou dans le setup CI/CD

**Priorité** : 🟡 MOYENNE (tests manuels alternatifs existent)

---

**Créé le** : 2026-02-13
**Contexte** : Discussion utilisateur - noter que pytest-benchmark devrait être dans deps dev
