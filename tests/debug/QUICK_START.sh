#!/bin/bash
# QUICK START - Tests RAG Enhanced
# Copie-colle ces commandes dans ton terminal

echo "========================================="
echo "RAG ENHANCED - Quick Start Tests"
echo "========================================="
echo ""

# 1. Diagnostic automatique (13s)
echo "[1/3] Diagnostic automatique..."
source .venv/bin/activate
python tests/debug/diagnose.py

# Attendre validation
read -p "Diagnostic OK ? (Enter pour continuer, Ctrl+C pour arrêter) "

# 2. Test interactif mode Enhanced
echo ""
echo "[2/3] Mode interactif - Lance LYRA avec --rag-enhanced"
echo ""
echo "Commande à lancer dans un AUTRE terminal:"
echo "  ./run.sh --rag-enhanced"
echo ""
echo "Puis teste ces prompts (copie-colle dans LYRA):"
echo ""
echo "# TEST 1: Slang 'start' → 'démarre'"
echo ">>> start preprod-09"
echo ""
echo "# TEST 2: Slang 'switch' + 'lights'"
echo ">>> switch les lights de la chambre"
echo ""
echo "# TEST 3: Slang 'cast'"
echo ">>> cast cette video youtube"
echo ""
echo "# TEST 4: Contexte multi-tour"
echo ">>> démarre preprod-09"
echo ">>> fais un snapshot"
echo ">>> clone cette vm en test-clone"
echo ""
echo "# TEST 5: Ambiguïté (score MEDIUM)"
echo ">>> fais un backup"
echo ""
echo "# TEST 6: Fallback (score LOW)"
echo ">>> quel temps fait-il demain"
echo ""

read -p "Tests manuels terminés ? (Enter pour continuer) "

# 3. Résumé
echo ""
echo "[3/3] Résumé"
echo ""
echo "✅ Diagnostic automatique : PASS"
echo ""
echo "Résultats attendus pour les tests manuels:"
echo "  ✅ TEST 1: vm_start avec vm_name='preprod-09'"
echo "  ✅ TEST 2: hue.turn_on_group avec group_name='chambre'"
echo "  ✅ TEST 3: cast_youtube"
echo "  ✅ TEST 4: Contexte injecté sur snapshot + clone"
echo "  ✅ TEST 5: Propose backup_create + vm_snapshot"
echo "  ✅ TEST 6: Fallback LYRA (pas de MCP)"
echo ""
echo "Si tous les tests passent:"
echo "  🎉 RAG Enhanced 100% fonctionnel !"
echo ""
echo "Si un test échoue:"
echo "  📝 Note le prompt + l'erreur, on debuggera ensemble"
echo ""
echo "Docs complètes:"
echo "  - tests/debug/RECAP.md          (résumé)"
echo "  - tests/debug/TEST_GUIDE.md     (guide détaillé)"
echo "  - docs/rag_enhanced/E2E_SCENARIOS.md  (scénarios)"
echo ""
echo "========================================="
