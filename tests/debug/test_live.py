#!/usr/bin/env python3
"""
Test LIVE du RAG Enhanced - Sans Mocks
Tests chaque composant individuellement puis le pipeline complet
avec logging verbose pour debugging
"""

import sys
import time
import logging
from pathlib import Path
from typing import Dict, Any

# Setup path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from lyra.core.config import RAGConfig
from lyra.rag_enhanced.config import RAGEnhancedConfig
from lyra.rag_enhanced.slang_normalizer import SlangNormalizer
from lyra.rag_enhanced.synonym_expander import SynonymExpander
from lyra.rag_enhanced.context_injector import ContextInjector
from lyra.rag_enhanced.confidence_cascader import ConfidenceCascader
from lyra.rag_enhanced.feedback_loop import FeedbackLoop
from lyra.rag_enhanced.pipeline_enhanced import EnhancedPipeline
from lyra.core.pipeline import Pipeline

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('tests/debug/test_live.log', mode='w')
    ]
)
logger = logging.getLogger(__name__)


class LiveTestRunner:
    """Runner pour tests live avec logging détaillé"""

    def __init__(self):
        self.results = []
        self.config = RAGConfig.from_yaml("config.yaml")

    def log_test_start(self, test_name: str):
        """Log début de test"""
        logger.info(f"\n{'='*80}")
        logger.info(f"TEST: {test_name}")
        logger.info(f"{'='*80}")

    def log_test_result(self, test_name: str, passed: bool, duration_ms: float, details: str = ""):
        """Log résultat de test"""
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} | {test_name} | {duration_ms:.2f}ms")
        if details:
            logger.info(f"  Details: {details}")

        self.results.append({
            'test': test_name,
            'passed': passed,
            'duration_ms': duration_ms,
            'details': details
        })

    def test_slang_normalizer(self):
        """Test SlangNormalizer avec queries réelles"""
        self.log_test_start("SlangNormalizer - Normalisation Slang/Anglicismes")

        test_cases = [
            ("start preprod-09", "démarre preprod-09"),
            ("stop la vm", "arrête la vm"),
            ("switch les lights", "allume les lumières"),
            ("cast cette vidéo", "diffuse cette vidéo"),
            ("backup la vm", "sauvegarde la vm"),
        ]

        normalizer = SlangNormalizer(enabled=True)
        logger.info(f"SlangNormalizer chargé avec {len(normalizer.slang_dict)} patterns")

        for query_in, expected_contains in test_cases:
            start = time.time()
            result = normalizer.normalize(query_in)
            duration = (time.time() - start) * 1000

            # Check si au moins un mot a été normalisé
            passed = result != query_in

            logger.info(f"  Input:  '{query_in}'")
            logger.info(f"  Output: '{result}'")
            logger.info(f"  Time:   {duration:.3f}ms")

            self.log_test_result(
                f"Slang: '{query_in}'",
                passed,
                duration,
                f"Output: '{result}'"
            )

    def test_synonym_expander(self):
        """Test SynonymExpander avec queries réelles"""
        self.log_test_start("SynonymExpander - Expansion Synonymes")

        test_cases = [
            "démarre la vm",
            "allume les lumières",
            "éteins tout",
            "clone preprod-09",
            "monte le volume",
        ]

        expander = SynonymExpander(enabled=True)
        logger.info(f"SynonymExpander chargé avec {len(expander.synonym_dict)} termes")

        for query_in in test_cases:
            start = time.time()
            result = expander.expand(query_in)
            duration = (time.time() - start) * 1000

            # Check si des synonymes ont été ajoutés
            passed = len(result) > len(query_in)

            logger.info(f"  Input:  '{query_in}'")
            logger.info(f"  Output: '{result}'")
            logger.info(f"  Tokens added: {len(result.split()) - len(query_in.split())}")
            logger.info(f"  Time:   {duration:.3f}ms")

            self.log_test_result(
                f"Synonym: '{query_in}'",
                passed,
                duration,
                f"Tokens added: {len(result.split()) - len(query_in.split())}"
            )

    def test_context_injector(self):
        """Test ContextInjector avec historique de session"""
        self.log_test_start("ContextInjector - Injection Contexte")

        injector = ContextInjector(enabled=True)
        session_id = "test-session-live"

        # Simuler un historique de session
        injector.db.log_exchange(
            session_id=session_id,
            role="user",
            content="démarre preprod-09",
            mcp_used=None,
            server_used=None
        )
        injector.db.log_exchange(
            session_id=session_id,
            role="lyra",
            content="VM démarrée",
            mcp_used="vm_start",
            server_used="FEDORA"
        )

        # Test injection sur query ambiguë
        query = "fais un snapshot"

        # Simuler résultats RAG ambigus
        rag_results = [
            {'tool_name': 'backup_create', 'score': 0.72},
            {'tool_name': 'vm_snapshot', 'score': 0.70}
        ]

        start = time.time()
        should_inject, n = injector.should_inject(rag_results)
        duration_check = (time.time() - start) * 1000

        logger.info(f"  Should inject: {should_inject} (n={n} échanges)")
        logger.info(f"  Gap score: {rag_results[0]['score'] - rag_results[1]['score']:.3f}")

        if should_inject:
            start = time.time()
            result = injector.inject(query, session_id, n)
            duration_inject = (time.time() - start) * 1000

            logger.info(f"  Query original: '{query}'")
            logger.info(f"  Query injecté:  '{result}'")
            logger.info(f"  Time inject:    {duration_inject:.3f}ms")

            passed = "[ctx:" in result and "vm_start" in result
        else:
            duration_inject = 0
            passed = False

        self.log_test_result(
            "Context Injection",
            passed,
            duration_check + duration_inject,
            f"Should inject: {should_inject}, n={n}"
        )

    def test_rag_retrieval(self):
        """Test RAG retrieval avec ChromaDB"""
        self.log_test_start("RAG - Semantic + Keyword Retrieval")

        # Créer pipeline V2 pour accéder au RAG
        pipeline = Pipeline(config=self.config)
        pipeline.initialize()

        test_queries = [
            "démarre preprod-09",
            "allume les lumières du salon",
            "clone la vm",
            "éteins la télé",
            "monte le volume",
        ]

        for query in test_queries:
            start = time.time()

            # Semantic search
            semantic_results = pipeline._semantic.search(query, top_k=5)

            # Keyword search
            keyword_results = pipeline._keyword.search(query, top_k=5)

            # Fusion
            fused_results = pipeline._fusion.fuse(
                semantic_results=semantic_results,
                keyword_results=keyword_results,
                top_k=3
            )

            duration = (time.time() - start) * 1000

            logger.info(f"\n  Query: '{query}'")
            logger.info(f"  Semantic results: {len(semantic_results)}")
            logger.info(f"  Keyword results:  {len(keyword_results)}")
            logger.info(f"  Fused results:    {len(fused_results)}")

            if fused_results:
                top_result = fused_results[0]
                logger.info(f"  Top match: {top_result['metadata'].get('name', 'N/A')} (score: {top_result.get('score', 0):.3f})")

            logger.info(f"  Time: {duration:.2f}ms")

            passed = len(fused_results) > 0

            self.log_test_result(
                f"RAG: '{query}'",
                passed,
                duration,
                f"Top: {fused_results[0]['metadata'].get('name', 'N/A') if fused_results else 'None'}"
            )

    def test_confidence_cascader(self):
        """Test ConfidenceCascader avec différents seuils"""
        self.log_test_start("ConfidenceCascader - Seuils de Confiance")

        cascader = ConfidenceCascader()

        test_cases = [
            # (score, expected_action, description)
            (0.95, "execute", "HIGH confidence - Execute direct"),
            (0.75, "propose", "MEDIUM confidence - Propose options"),
            (0.45, "fallback", "LOW confidence - Fallback LYRA"),
            (0.85, "propose", "Boundary HIGH - Propose (pas execute)"),
            (0.60, "propose", "Boundary LOW - Propose"),
        ]

        for score, expected_action, description in test_cases:
            rag_results = [{'tool_name': 'test_tool', 'score': score}]

            start = time.time()
            action = cascader.cascade(score, rag_results)
            duration = (time.time() - start) * 1000

            passed = action.value == expected_action

            logger.info(f"  {description}")
            logger.info(f"    Score: {score:.2f} → Action: {action.value}")
            logger.info(f"    Time: {duration:.3f}ms")

            self.log_test_result(
                f"Cascade: score={score}",
                passed,
                duration,
                f"Action: {action.value} (expected: {expected_action})"
            )

    def test_enhanced_pipeline_e2e(self):
        """Test pipeline Enhanced complet E2E"""
        self.log_test_start("EnhancedPipeline - End-to-End (12 Scénarios)")

        # Activer tous les composants
        enhanced_config = RAGEnhancedConfig(enabled=True)
        enhanced_config.slang_normalizer.enabled = True
        enhanced_config.synonym_expander.enabled = True
        enhanced_config.context_injector.enabled = True
        enhanced_config.feedback_loop.enabled = True
        enhanced_config.rag_3tier.enabled = False  # Utiliser V2 (mieux peuplé)

        pipeline = EnhancedPipeline(
            config=self.config,
            enhanced_config=enhanced_config,
            enabled=True
        )
        pipeline.initialize()

        session_id = "test-e2e-live"

        # 12 scénarios du TOPO (adaptés aux MCP disponibles)
        test_scenarios = [
            # HUE
            ("allume les lumières de la chambre", ["hue.turn_on_group", "hue.turn_on_light"]),
            ("éteins toutes les lumières", ["hue.turn_off_all", "hue.turn_off_group"]),

            # FEDORA
            ("démarre preprod-09", ["vm_start"]),
            ("clone preprod-09 en test-clone", ["vm_clone"]),
            ("fais un backup de preprod-09", ["backup_create", "vm_snapshot"]),

            # TV
            ("allume la télé", ["tv.power_on"]),
            ("éteins la télé", ["tv.power_off"]),
            ("monte le volume de la télé", ["tv.volume_up", "denon.volume_up"]),

            # CATT
            ("caste cette vidéo youtube", ["cast_youtube", "cast_url"]),

            # DENON
            ("mute le home cinema", ["denon.mute_on", "denon.mute_toggle"]),

            # Ambigus (test cascader)
            ("quel temps fait-il", ["fallback"]),  # Pas de MCP adapté
            ("fais un backup", ["backup_create", "vm_snapshot"]),  # Ambiguïté
        ]

        for i, (query, expected_tools) in enumerate(test_scenarios, 1):
            logger.info(f"\n--- Scénario {i}/12 ---")

            start = time.time()
            result = pipeline._route_query(query, session_id)
            duration = (time.time() - start) * 1000

            logger.info(f"  Query: '{query}'")
            logger.info(f"  Expected tools: {expected_tools}")

            # Logs détaillés du pipeline
            if hasattr(result, 'metrics'):
                logger.info(f"  Metrics:")
                for key, value in result.metrics.items():
                    if '_ms' in key:
                        logger.info(f"    {key}: {value:.2f}ms")

            # Vérifier le résultat
            passed = False
            actual_tool = None

            if hasattr(result, 'tool_call') and result.tool_call:
                actual_tool = result.tool_call.get('name', 'N/A')
                passed = any(expected in actual_tool for expected in expected_tools)
                logger.info(f"  Tool appelé: {actual_tool}")
            elif hasattr(result, 'query_type'):
                actual_tool = f"fallback ({result.query_type})"
                passed = "fallback" in expected_tools
                logger.info(f"  Fallback: {result.query_type}")

            logger.info(f"  Total time: {duration:.2f}ms")
            logger.info(f"  Result: {'✅ PASS' if passed else '❌ FAIL'}")

            self.log_test_result(
                f"E2E Scénario {i}: '{query[:30]}...'",
                passed,
                duration,
                f"Tool: {actual_tool}"
            )

    def print_summary(self):
        """Affiche le résumé des tests"""
        logger.info(f"\n{'='*80}")
        logger.info("RÉSUMÉ DES TESTS LIVE")
        logger.info(f"{'='*80}")

        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        failed = total - passed

        logger.info(f"\nTotal: {total} tests")
        logger.info(f"✅ Passed: {passed}")
        logger.info(f"❌ Failed: {failed}")
        if total > 0:
            logger.info(f"Success rate: {passed/total*100:.1f}%")
        else:
            logger.info("Success rate: N/A (no tests run)")

        # Temps moyen par composant
        logger.info(f"\n--- Temps Moyens ---")

        components = {
            'Slang': [r for r in self.results if 'Slang' in r['test']],
            'Synonym': [r for r in self.results if 'Synonym' in r['test']],
            'Context': [r for r in self.results if 'Context' in r['test']],
            'RAG': [r for r in self.results if 'RAG' in r['test']],
            'Cascade': [r for r in self.results if 'Cascade' in r['test']],
            'E2E': [r for r in self.results if 'E2E' in r['test']],
        }

        for comp_name, comp_results in components.items():
            if comp_results:
                avg_time = sum(r['duration_ms'] for r in comp_results) / len(comp_results)
                comp_passed = sum(1 for r in comp_results if r['passed'])
                logger.info(f"{comp_name:15s}: {avg_time:6.2f}ms avg | {comp_passed}/{len(comp_results)} passed")

        # Tests échoués en détail
        if failed > 0:
            logger.info(f"\n--- Tests Échoués (Détails) ---")
            for r in self.results:
                if not r['passed']:
                    logger.info(f"❌ {r['test']}")
                    logger.info(f"   {r['details']}")

        logger.info(f"\nLogs complets: tests/debug/test_live.log")


def main():
    """Point d'entrée"""
    print("="*80)
    print("LYRA - Tests LIVE du RAG Enhanced (Sans Mocks)")
    print("="*80)
    print()

    runner = LiveTestRunner()

    try:
        # Tests individuels des composants
        runner.test_slang_normalizer()
        runner.test_synonym_expander()
        runner.test_context_injector()
        runner.test_rag_retrieval()
        runner.test_confidence_cascader()

        # Test E2E complet
        runner.test_enhanced_pipeline_e2e()

    except Exception as e:
        logger.error(f"Erreur lors des tests: {e}", exc_info=True)

    finally:
        runner.print_summary()


if __name__ == "__main__":
    main()
