#!/usr/bin/env python3
"""
Test RAPIDE du RAG Enhanced - Scénarios E2E
Utilise un pipeline pré-initialisé pour éviter de recharger les modèles
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lyra.core.config import RAGConfig
from lyra.rag_enhanced.config import RAGEnhancedConfig
from lyra.rag_enhanced.pipeline_enhanced import EnhancedPipeline

def test_e2e_scenarios():
    """Test les 12 scénarios E2E avec le vrai pipeline"""

    print("="*80)
    print("LYRA - Test RAPIDE des 12 Scénarios E2E")
    print("="*80)
    print()

    # Charger config
    print("[1/3] Chargement config...")
    config = RAGConfig.from_yaml("config.yaml")

    # Activer tous les composants Enhanced
    enhanced_config = RAGEnhancedConfig(enabled=True)
    enhanced_config.slang_normalizer.enabled = True
    enhanced_config.synonym_expander.enabled = True
    enhanced_config.context_injector.enabled = True
    enhanced_config.feedback_loop.enabled = True
    enhanced_config.rag_3tier.enabled = False  # Utiliser V2 (mieux peuplé)

    # Créer pipeline
    print("[2/3] Initialisation pipeline Enhanced...")
    pipeline = EnhancedPipeline(
        config=config,
        enhanced_config=enhanced_config,
        enabled=True
    )

    print("  - Chargement composants Enhanced...")
    pipeline.initialize()
    print("  ✓ Pipeline prêt\n")

    session_id = "test-quick-e2e"

    # 12 scénarios adaptés aux MCP disponibles
    print("[3/3] Exécution 12 scénarios E2E...")
    print()

    scenarios = [
        # HUE (2 scénarios)
        ("allume les lumières de la chambre", "HUE", ["hue.turn_on_group", "hue.turn_on_light"]),
        ("éteins toutes les lumières", "HUE", ["hue.turn_off_all", "hue.turn_off_group"]),

        # FEDORA (3 scénarios)
        ("démarre preprod-09", "FEDORA", ["vm_start"]),
        ("clone preprod-09 en test-clone", "FEDORA", ["vm_clone"]),
        ("fais un backup de preprod-09", "FEDORA", ["backup_create", "vm_snapshot"]),

        # TV (3 scénarios)
        ("allume la télé", "TV", ["tv.power_on"]),
        ("éteins la télé", "TV", ["tv.power_off"]),
        ("monte le volume de la télé", "TV", ["tv.volume_up", "denon.volume_up"]),

        # CATT (1 scénario)
        ("caste cette vidéo youtube", "CATT", ["cast_youtube", "cast_url"]),

        # DENON (1 scénario)
        ("mute le home cinema", "DENON", ["denon.mute_on", "denon.mute_toggle"]),

        # Edge cases (2 scénarios)
        ("quel temps fait-il demain", "FALLBACK", ["fallback"]),
        ("fais un backup", "AMBIGUOUS", ["backup_create", "vm_snapshot"]),
    ]

    results = []
    passed = 0
    failed = 0

    for i, (query, category, expected_tools) in enumerate(scenarios, 1):
        print(f"\n[Scénario {i}/12] {category}")
        print(f"  Query: '{query}'")

        start = time.time()

        try:
            result = pipeline._route_query(query, session_id)
            duration = (time.time() - start) * 1000

            # Logs détaillés
            print(f"  Time:  {duration:.0f}ms")

            # Composants Enhanced
            if hasattr(pipeline, '_slang_normalizer'):
                normalized = pipeline._slang_normalizer.normalize(query)
                if normalized != query:
                    print(f"  Slang: '{query}' → '{normalized}'")

            # Vérifier le résultat
            success = False
            tool_name = None

            if hasattr(result, 'tool_call') and result.tool_call:
                tool_name = result.tool_call.get('name', 'N/A')
                success = any(exp in tool_name for exp in expected_tools)
                print(f"  Tool:  {tool_name}")

                # Afficher arguments
                if 'arguments' in result.tool_call:
                    args = result.tool_call['arguments']
                    if args:
                        print(f"  Args:  {args}")

            elif hasattr(result, 'query_type'):
                tool_name = f"fallback ({result.query_type})"
                success = "fallback" in expected_tools
                print(f"  Type:  {result.query_type}")

            elif hasattr(result, 'pending_args') and result.pending_args:
                tool_name = "pending_clarification"
                success = True  # C'est ok pour les queries ambiguës
                print(f"  Pending: {len(result.pending_args)} args")

            # Résultat
            if success:
                print(f"  ✅ PASS")
                passed += 1
            else:
                print(f"  ❌ FAIL (expected: {expected_tools}, got: {tool_name})")
                failed += 1

            results.append({
                'scenario': f"{i}. {category}",
                'query': query,
                'tool': tool_name,
                'success': success,
                'duration_ms': duration
            })

        except Exception as e:
            duration = (time.time() - start) * 1000
            print(f"  ❌ ERROR: {e}")
            failed += 1

            results.append({
                'scenario': f"{i}. {category}",
                'query': query,
                'tool': 'ERROR',
                'success': False,
                'duration_ms': duration
            })

    # Résumé
    print("\n" + "="*80)
    print("RÉSUMÉ")
    print("="*80)
    print(f"\nTotal: {len(scenarios)} scénarios")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success rate: {passed/len(scenarios)*100:.1f}%")

    # Temps moyens
    if results:
        avg_time = sum(r['duration_ms'] for r in results) / len(results)
        print(f"\nTemps moyen: {avg_time:.0f}ms par scénario")

    # Échecs détaillés
    if failed > 0:
        print("\n--- Échecs ---")
        for r in results:
            if not r['success']:
                print(f"  ❌ {r['scenario']}: '{r['query']}'")
                print(f"     Got: {r['tool']}")

    print("\n" + "="*80)

    return passed, failed


if __name__ == "__main__":
    try:
        passed, failed = test_e2e_scenarios()
        sys.exit(0 if failed == 0 else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrompu par l'utilisateur")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
