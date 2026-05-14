#!/usr/bin/env python3
"""
Diagnostic progressif du RAG Enhanced
Teste chaque étape du pipeline sans executer les MCP
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lyra.core.config import RAGConfig
from lyra.rag_enhanced.config import RAGEnhancedConfig
from lyra.rag_enhanced.slang_normalizer import SlangNormalizer
from lyra.rag_enhanced.synonym_expander import SynonymExpander
from lyra.rag_enhanced.context_injector import ContextInjector
from lyra.core.pipeline import Pipeline


def test_step_1_slang():
    """Étape 1: SlangNormalizer"""
    print("\n" + "="*80)
    print("ÉTAPE 1: SlangNormalizer")
    print("="*80)

    normalizer = SlangNormalizer(enabled=True)
    print(f"✓ Chargé avec {len(normalizer.slang_dict)} patterns")

    test_cases = [
        "start preprod-09",
        "stop la vm",
        "switch les lights",
        "cast cette vidéo",
    ]

    for query in test_cases:
        result = normalizer.normalize(query)
        changed = "✓" if result != query else "○"
        print(f"  {changed} '{query}' → '{result}'")

    return True


def test_step_2_synonym():
    """Étape 2: SynonymExpander"""
    print("\n" + "="*80)
    print("ÉTAPE 2: SynonymExpander")
    print("="*80)

    expander = SynonymExpander(enabled=True)
    print(f"✓ Chargé avec {len(expander.synonym_dict)} termes")

    test_cases = [
        "démarre la vm",
        "allume les lumières",
        "clone preprod-09",
    ]

    for query in test_cases:
        result = expander.expand(query)
        added = len(result.split()) - len(query.split())
        print(f"  ✓ '{query}' → +{added} tokens")
        if added > 0:
            print(f"    '{result[:80]}...'")

    return True


def test_step_3_rag():
    """Étape 3: RAG Retrieval (Semantic + Keyword + Fusion)"""
    print("\n" + "="*80)
    print("ÉTAPE 3: RAG Retrieval (Semantic + Keyword + Fusion)")
    print("="*80)

    config = RAGConfig.from_yaml("config.yaml")
    pipeline = Pipeline(config=config)

    print("  [1/3] Initialisation Pipeline V2...")
    start = time.time()
    pipeline.initialize()
    init_time = (time.time() - start) * 1000
    print(f"  ✓ Initialisé en {init_time:.0f}ms")

    test_queries = [
        ("démarre preprod-09", "vm_start"),
        ("allume les lumières", "hue.turn_on"),
        ("clone la vm", "vm_clone"),
        ("éteins la télé", "tv.power_off"),
    ]

    print("\n  [2/3] Tests Semantic Search...")
    for query, expected in test_queries:
        start = time.time()
        results = pipeline._semantic.search(query, top_k=3)
        duration = (time.time() - start) * 1000

        if results:
            top = results[0]
            tool_name = top.metadata.get('name', 'N/A')
            score = top.score
            match = "✓" if expected in tool_name else "○"
            print(f"    {match} '{query}' → {tool_name} ({score:.3f}) [{duration:.0f}ms]")
        else:
            print(f"    ✗ '{query}' → No results")

    print("\n  [3/3] Tests Keyword Search...")
    for query, expected in test_queries:
        start = time.time()
        results = pipeline._keyword.search(query, top_k=3)
        duration = (time.time() - start) * 1000

        if results:
            top = results[0]
            tool_name = top.metadata.get('name', 'N/A')
            score = top.score
            match = "✓" if expected in tool_name else "○"
            print(f"    {match} '{query}' → {tool_name} ({score:.3f}) [{duration:.0f}ms]")
        else:
            print(f"    ✗ '{query}' → No results")

    return True


def test_step_4_pipeline_flow():
    """Étape 4: Pipeline complet Slang → Synonym → RAG"""
    print("\n" + "="*80)
    print("ÉTAPE 4: Pipeline Complet (Slang → Synonym → RAG)")
    print("="*80)

    # Composants Enhanced
    slang = SlangNormalizer(enabled=True)
    synonym = SynonymExpander(enabled=True)

    # Pipeline V2 pour RAG
    config = RAGConfig.from_yaml("config.yaml")
    pipeline = Pipeline(config=config)
    pipeline.initialize()

    test_queries = [
        "start la vm preprod-09",
        "switch les lights de la chambre",
        "cast cette video youtube",
    ]

    for query in test_queries:
        print(f"\n  Query: '{query}'")

        # Étape 1: Slang
        start = time.time()
        query_normalized = slang.normalize(query)
        t1 = (time.time() - start) * 1000

        if query_normalized != query:
            print(f"    [1] Slang:   '{query_normalized}' ({t1:.2f}ms)")
        else:
            print(f"    [1] Slang:   (inchangé) ({t1:.2f}ms)")

        # Étape 2: Synonym
        start = time.time()
        query_expanded = synonym.expand(query_normalized)
        t2 = (time.time() - start) * 1000

        added = len(query_expanded.split()) - len(query_normalized.split())
        if added > 0:
            print(f"    [2] Synonym: +{added} tokens ({t2:.2f}ms)")
        else:
            print(f"    [2] Synonym: (inchangé) ({t2:.2f}ms)")

        # Étape 3: RAG
        start = time.time()
        sem_results = pipeline._semantic.search(query_expanded, top_k=5)
        key_results = pipeline._keyword.search(query_expanded, top_k=5)
        fused = pipeline._fusion.fuse(sem_results, key_results, top_k=3)
        t3 = (time.time() - start) * 1000

        if fused:
            top = fused[0]
            tool_name = top.metadata.get('name', 'N/A')
            score = top.rrf_score
            print(f"    [3] RAG:     {tool_name} (RRF: {score:.3f}) ({t3:.0f}ms)")
        else:
            print(f"    [3] RAG:     No results ({t3:.0f}ms)")

        total_time = t1 + t2 + t3
        print(f"    TOTAL: {total_time:.0f}ms")

    return True


def main():
    """Lance le diagnostic complet"""
    print("="*80)
    print("DIAGNOSTIC RAG ENHANCED - Progressif")
    print("="*80)

    steps = [
        ("SlangNormalizer", test_step_1_slang),
        ("SynonymExpander", test_step_2_synonym),
        ("RAG Retrieval", test_step_3_rag),
        ("Pipeline Flow", test_step_4_pipeline_flow),
    ]

    results = []

    for i, (name, test_func) in enumerate(steps, 1):
        try:
            print(f"\n[{i}/{len(steps)}] Test: {name}")
            start = time.time()
            success = test_func()
            duration = time.time() - start

            results.append({
                'name': name,
                'success': success,
                'duration': duration
            })

        except Exception as e:
            print(f"\n  ✗ ERREUR: {e}")
            import traceback
            traceback.print_exc()

            results.append({
                'name': name,
                'success': False,
                'duration': 0
            })

    # Résumé
    print("\n" + "="*80)
    print("RÉSUMÉ DIAGNOSTIC")
    print("="*80)

    for r in results:
        status = "✓" if r['success'] else "✗"
        print(f"  {status} {r['name']:30s} ({r['duration']:.1f}s)")

    passed = sum(1 for r in results if r['success'])
    total = len(results)

    print(f"\n  Total: {passed}/{total} étapes réussies")

    if passed == total:
        print("\n  ✅ Tous les composants fonctionnent !")
        print("\n  Prochaine étape: ./run.sh --rag-enhanced")
    else:
        print("\n  ⚠️  Certains composants ont échoué")

    print("="*80)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDiagnostic interrompu")
    except Exception as e:
        print(f"\nERREUR: {e}")
        import traceback
        traceback.print_exc()
