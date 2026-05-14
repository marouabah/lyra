#!/bin/bash
# Script de validation SESSION 4 (P3) - Context Injector
# Usage: ./validate_session4.sh

set -e

echo "=========================================="
echo "SESSION 4 (P3) - Context Injector"
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

if pytest tests/unit/rag_enhanced/test_context_db.py tests/unit/rag_enhanced/test_context_injector.py -v --tb=short > /tmp/test_output.txt 2>&1; then
    PASSED=$(grep -o "PASSED" /tmp/test_output.txt | wc -l)
    FAILED=$(grep -o "FAILED" /tmp/test_output.txt | wc -l)

    echo "  Tests passés: $PASSED"
    echo "  Tests échoués: $FAILED"

    # Accepter si FAILED=0 et PASSED>=25
    if [ "$FAILED" -eq 0 ] && [ "$PASSED" -ge 25 ]; then
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

if pytest tests/unit/rag_enhanced/test_context_db.py tests/unit/rag_enhanced/test_context_injector.py \
    --cov=lyra.rag_enhanced.context_db \
    --cov=lyra.rag_enhanced.context_injector \
    --cov-report=term > /tmp/coverage_output.txt 2>&1; then

    # Extraire le pourcentage de couverture TOTAL
    COVERAGE=$(grep "TOTAL" /tmp/coverage_output.txt | awk '{print $4}' | tr -d '%')

    if [ -n "$COVERAGE" ]; then
        echo "  Couverture: ${COVERAGE}%"

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
echo "  [INFO] Tests performance manuels (SQLite queries)"

# Vérifier que les opérations sont rapides (test approximatif)
if python -c "
from lyra.rag_enhanced import ContextDB, ContextInjector
import time
import tempfile

# Test ContextDB
with tempfile.TemporaryDirectory() as tmp:
    db = ContextDB(f'{tmp}/test.db')

    # Log 10 échanges et mesurer temps
    start = time.perf_counter()
    for i in range(10):
        db.log_exchange('123', 'user', f'query {i}', None, None)
    elapsed_log = (time.perf_counter() - start) * 1000  # ms

    # Get last exchanges
    start = time.perf_counter()
    history = db.get_last_exchanges('123', n=10)
    elapsed_get = (time.perf_counter() - start) * 1000  # ms

    db.close()

    # Vérifier limites
    assert elapsed_log < 100, f'log_exchange trop lent: {elapsed_log}ms'
    assert elapsed_get < 10, f'get_last_exchanges trop lent: {elapsed_get}ms'

    print(f'  log_exchange (10x): {elapsed_log:.2f}ms')
    print(f'  get_last_exchanges: {elapsed_get:.2f}ms')
" 2>&1; then
    check_pass "Performance OK"
    SCORE=$((SCORE + 15))
else
    check_fail "Performance insuffisante"
fi

echo ""

# 4. Intégration (20 pts)
echo "4. Intégration (20 pts)"
echo "-----------------------"

# Vérifier import ContextDB
if python -c "from lyra.rag_enhanced import ContextDB; print('✓ Import ContextDB OK')" 2>&1; then
    check_pass "Import ContextDB OK"
    SCORE=$((SCORE + 5))
else
    check_fail "Erreur import ContextDB"
fi

# Vérifier import ContextInjector
if python -c "from lyra.rag_enhanced import ContextInjector; print('✓ Import ContextInjector OK')" 2>&1; then
    check_pass "Import ContextInjector OK"
    SCORE=$((SCORE + 5))
else
    check_fail "Erreur import ContextInjector"
fi

# Vérifier singletons
if python -c "from lyra.rag_enhanced.context_db import get_context_db; from lyra.rag_enhanced.context_injector import get_context_injector; print('✓ Singletons OK')" 2>&1; then
    check_pass "Singletons OK"
    SCORE=$((SCORE + 5))
else
    check_fail "Erreur singletons"
fi

# Vérifier workflow complet
if python -c "
from lyra.rag_enhanced import ContextInjector
import tempfile

with tempfile.TemporaryDirectory() as tmp:
    injector = ContextInjector(db_path=f'{tmp}/test.db')

    # Log historique
    injector.log_exchange('123', 'user', 'test', None, None)
    injector.log_exchange('123', 'lyra', 'OK', 'vm_start', 'FEDORA')

    # should_inject
    rag_results = [
        {'tool_name': 'backup_create', 'score': 0.72},
        {'tool_name': 'vm_snapshot', 'score': 0.70}
    ]
    should_inject, n = injector.should_inject(rag_results)
    assert should_inject is True
    assert n == 10

    # inject
    result = injector.inject('query', session_id='123', n=n)
    assert '[ctx:' in result

    injector.db.close()
    print('✓ Workflow complet OK')
" 2>&1; then
    check_pass "Workflow complet OK"
    SCORE=$((SCORE + 5))
else
    check_fail "Erreur workflow"
fi

echo ""

# 5. Documentation (15 pts)
echo "5. Documentation (15 pts)"
echo "-------------------------"

# Vérifier fichiers docs
if [ -f "docs/rag_enhanced/CONTEXT_SCHEMA.md" ]; then
    check_pass "CONTEXT_SCHEMA.md existe"
    SCORE=$((SCORE + 5))
else
    check_fail "CONTEXT_SCHEMA.md manquant"
fi

# Vérifier fichiers source
if [ -f "lyra/rag_enhanced/context_db.py" ]; then
    # Vérifier docstrings
    if grep -q '"""' lyra/rag_enhanced/context_db.py; then
        check_pass "Docstrings ContextDB présentes"
        SCORE=$((SCORE + 3))
    else
        check_fail "Docstrings ContextDB manquantes"
    fi
else
    check_fail "context_db.py manquant"
fi

if [ -f "lyra/rag_enhanced/context_injector.py" ]; then
    # Vérifier docstrings
    if grep -q '"""' lyra/rag_enhanced/context_injector.py; then
        check_pass "Docstrings ContextInjector présentes"
        SCORE=$((SCORE + 3))
    else
        check_fail "Docstrings ContextInjector manquantes"
    fi
else
    check_fail "context_injector.py manquant"
fi

# Vérifier tests
if [ -f "tests/unit/rag_enhanced/test_context_db.py" ] && [ -f "tests/unit/rag_enhanced/test_context_injector.py" ]; then
    check_pass "Tests présents"
    SCORE=$((SCORE + 4))
else
    check_fail "Tests manquants"
fi

echo ""

# Récapitulatif
echo "=========================================="
echo "SCORE FINAL: ${SCORE}/${MAX_SCORE}"
echo "=========================================="

if [ "$SCORE" -ge 85 ]; then
    echo -e "${GREEN}✓ SESSION 4 VALIDÉE${NC} (seuil: 85/100)"
    echo ""
    echo "Prochaine étape: SESSION 5 (RAG 3-Tier Collections)"
    exit 0
else
    echo -e "${RED}✗ SESSION 4 NON VALIDÉE${NC} (score < 85/100)"
    echo ""
    echo "Corrections nécessaires avant SESSION 5."
    exit 1
fi
