#!/bin/bash
# Script de validation SESSION 3 (P2) - Synonym Expander
# Usage: ./validate_session3.sh

set -e

echo "=========================================="
echo "SESSION 3 (P2) - Synonym Expander"
echo "Validation Automatique"
echo "=========================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SCORE=0
MAX_SCORE=100

# Helper functions
check_pass() {
    echo -e "${GREEN}✓${NC} $1"
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# 1. Tests Unitaires (40 pts)
echo "1. Tests Unitaires (40 pts)"
echo "----------------------------"

if pytest tests/unit/rag_enhanced/test_synonym_expander.py -v --tb=short > /tmp/test_output.txt 2>&1; then
    PASSED=$(grep -o "PASSED" /tmp/test_output.txt | wc -l)
    FAILED=$(grep -o "FAILED" /tmp/test_output.txt | wc -l)
    SKIPPED=$(grep -o "SKIPPED" /tmp/test_output.txt | wc -l)

    echo "  Tests passés: $PASSED"
    echo "  Tests échoués: $FAILED"
    echo "  Tests skipped: $SKIPPED"

    # Accepter si FAILED=0 (même avec des skipped)
    if [ "$FAILED" -eq 0 ] && [ "$PASSED" -ge 20 ]; then
        check_pass "Tous les tests passent"
        SCORE=$((SCORE + 40))
    else
        check_fail "Des tests échouent"
        cat /tmp/test_output.txt
    fi
else
    check_fail "Erreur lors de l'exécution des tests"
    cat /tmp/test_output.txt
fi

echo ""

# 2. Couverture Code (10 pts)
echo "2. Couverture Code (10 pts)"
echo "---------------------------"

if pytest tests/unit/rag_enhanced/test_synonym_expander.py \
    --cov=lyra.rag_enhanced.synonym_expander \
    --cov-report=term > /tmp/coverage_output.txt 2>&1; then

    # Extraire le pourcentage de couverture (ligne avec Stmts Miss Cover)
    COVERAGE=$(grep "lyra/rag_enhanced/synonym_expander\.py" /tmp/coverage_output.txt | awk '{print $4}' | tr -d '%')

    if [ -n "$COVERAGE" ]; then
        echo "  Couverture: ${COVERAGE}%"

        # Déjà un entier
        COV_INT=$COVERAGE

        if [ "$COV_INT" -ge 95 ]; then
            check_pass "Couverture ≥95%"
            SCORE=$((SCORE + 10))
        elif [ "$COV_INT" -ge 90 ]; then
            check_pass "Couverture ≥90%"
            SCORE=$((SCORE + 9))
        elif [ "$COV_INT" -ge 85 ]; then
            check_warn "Couverture ${COVERAGE}% (objectif: 90%)"
            SCORE=$((SCORE + 8))
        else
            check_fail "Couverture ${COVERAGE}% < 85%"
        fi
    else
        check_warn "Impossible d'extraire le pourcentage de couverture"
        echo "Sortie complète:"
        cat /tmp/coverage_output.txt
    fi
else
    check_fail "Erreur lors du calcul de couverture"
    cat /tmp/coverage_output.txt
fi

echo ""

# 3. Performance (15 pts)
echo "3. Performance (15 pts)"
echo "-----------------------"

# Test manuel de performance
if pytest tests/unit/rag_enhanced/test_synonym_expander.py::TestSynonymExpander::test_expand_performance_manual -v -s > /tmp/perf_output.txt 2>&1; then
    # Extraire la latence médiane
    MEDIAN=$(grep "Médiane:" /tmp/perf_output.txt | awk '{print $3}' | tr -d 'ms')

    if [ -n "$MEDIAN" ]; then
        echo "  Latence médiane: ${MEDIAN}ms"

        # Utiliser awk pour comparaison float
        if awk "BEGIN {exit !($MEDIAN < 0.5)}"; then
            check_pass "Performance excellente (<0.5ms)"
            SCORE=$((SCORE + 15))
        elif awk "BEGIN {exit !($MEDIAN < 1.0)}"; then
            check_pass "Performance OK (<1ms)"
            SCORE=$((SCORE + 13))
        else
            check_fail "Performance insuffisante (≥1ms)"
        fi
    else
        check_warn "Impossible d'extraire la latence"
        cat /tmp/perf_output.txt
    fi
else
    check_fail "Test de performance échoué"
    cat /tmp/perf_output.txt
fi

echo ""

# 4. Intégration (20 pts)
echo "4. Intégration (20 pts)"
echo "-----------------------"

# Vérifier import
if python -c "from lyra.rag_enhanced import SynonymExpander; print('✓ Import OK')" 2>&1; then
    check_pass "Import SynonymExpander OK"
    SCORE=$((SCORE + 5))
else
    check_fail "Erreur import SynonymExpander"
fi

# Vérifier singleton
if python -c "from lyra.rag_enhanced.synonym_expander import get_synonym_expander; e = get_synonym_expander(); print('✓ Singleton OK')" 2>&1; then
    check_pass "Singleton get_synonym_expander OK"
    SCORE=$((SCORE + 5))
else
    check_fail "Erreur singleton"
fi

# Vérifier chargement dict
if python -c "from lyra.rag_enhanced import SynonymExpander; e = SynonymExpander(); assert len(e.synonym_dict) > 0; print('✓ Dict chargé')" 2>&1; then
    check_pass "Dictionnaire chargé"
    SCORE=$((SCORE + 5))
else
    check_fail "Erreur chargement dictionnaire"
fi

# Vérifier expansion fonctionnelle
if python -c "
from lyra.rag_enhanced import SynonymExpander
e = SynonymExpander()
result = e.expand('vm')
assert 'machine' in result or 'serveur' in result
print('✓ Expansion fonctionne')
" 2>&1; then
    check_pass "Expansion fonctionnelle"
    SCORE=$((SCORE + 5))
else
    check_fail "Erreur expansion"
fi

echo ""

# 5. Documentation (15 pts)
echo "5. Documentation (15 pts)"
echo "-------------------------"

# Vérifier fichiers docs
if [ -f "data/synonym_dict.json" ]; then
    check_pass "data/synonym_dict.json existe"
    SCORE=$((SCORE + 3))

    # Vérifier contenu dict
    KEYWORDS=$(python -c "
import json
with open('data/synonym_dict.json') as f:
    data = json.load(f)
    keywords = [k for k in data if not k.startswith('_')]
    print(len(keywords))
" 2>&1)

    if [ "$KEYWORDS" -gt 0 ]; then
        echo "  Keywords: $KEYWORDS (objectif: ≥40)"
        if [ "$KEYWORDS" -ge 40 ]; then
            check_pass "Dictionnaire complet (≥40 keywords)"
            SCORE=$((SCORE + 2))
        else
            check_warn "Dictionnaire incomplet (<40 keywords)"
            SCORE=$((SCORE + 1))
        fi
    fi
else
    check_fail "data/synonym_dict.json manquant"
fi

if [ -f "docs/rag_enhanced/SYNONYM_STRATEGY.md" ]; then
    check_pass "SYNONYM_STRATEGY.md existe"
    SCORE=$((SCORE + 5))
else
    check_fail "SYNONYM_STRATEGY.md manquant"
fi

if [ -f "lyra/rag_enhanced/synonym_expander.py" ]; then
    # Vérifier docstrings
    if grep -q '"""' lyra/rag_enhanced/synonym_expander.py; then
        check_pass "Docstrings présentes"
        SCORE=$((SCORE + 3))
    else
        check_fail "Docstrings manquantes"
    fi
else
    check_fail "synonym_expander.py manquant"
fi

# Vérifier README
if [ -f "tests/unit/rag_enhanced/test_synonym_expander.py" ]; then
    check_pass "Tests présents"
    SCORE=$((SCORE + 2))
else
    check_fail "Tests manquants"
fi

echo ""

# Récapitulatif
echo "=========================================="
echo "SCORE FINAL: ${SCORE}/${MAX_SCORE}"
echo "=========================================="

if [ "$SCORE" -ge 85 ]; then
    echo -e "${GREEN}✓ SESSION 3 VALIDÉE${NC} (seuil: 85/100)"
    echo ""
    echo "Prochaine étape: SESSION 4 (Context Injector)"
    exit 0
else
    echo -e "${RED}✗ SESSION 3 NON VALIDÉE${NC} (score < 85/100)"
    echo ""
    echo "Corrections nécessaires avant SESSION 4."
    exit 1
fi
