# SUITE DE TESTS COMPLÈTE

## CONTEXTE
Créer tous les tests pour valider la scène Iron Man.
Tests unitaires + intégration + end-to-end + edge cases.

## TON RÔLE
Créer une suite de tests exhaustive qui garantit qualité.

## TESTS UNITAIRES (PAR PHASE)

### Phase 0 - Détection

Fichier: `tests/test_phase0.py`

Tests:
1. **Triggers positifs:**
   - "je suis iron man" → True
   - "JE SUIS IRON MAN" → True (case insensitive)
   - "je suis tony stark" → True
   - "je suis tony" → True
   - "mode iron man" → True
   - "Lyra, je suis iron man stp" → True (dans phrase)

2. **Triggers négatifs:**
   - "je suis fatigué" → False
   - "iron man le film" → False
   - "je vais bien" → False

3. **Validation devices:**
   - TV online (mock) → (True, "")
   - TV offline (mock) → (False, "TV non disponible")
   - Hue online (mock) → (True, "")
   - Hue offline (mock) → (False, "Bridge non disponible")

4. **Sauvegarde état:**
   - JSON créé correctement
   - Contient état TV complet
   - Contient état Hue complet
   - Format valide

### Phase 1 - Blackout

Fichier: `tests/test_phase1.py`

Tests:
1. Lumières s'éteignent
2. TV allumée → éteinte
3. TV déjà éteinte → skip
4. Durée exacte 3.0s (±50ms)
5. Erreur Hue → continue
6. Erreur TV → continue
7. Latence <500ms

### Phase 2 - Impact

Fichier: `tests/test_phase2.py`

Tests:
1. Flash blanc instantané visible
2. Transition bleu fluide 300ms
3. TV s'allume
4. YouTube démarre
5. Retry si YouTube fail
6. Ambilight activé
7. Continue sans musique si Cast fail
8. Durée ~3.5s (±200ms)

### Phase 3 - Buildup

Fichier: `tests/test_phase3.py`

Tests:
1. Brightness progression linéaire 0→254
2. Un beat s'exécute correctement
3. Durée 12s (±300ms)
4. ~24 beats exécutés
5. Couleurs alternent rouge/bleu
6. Timing drift <100ms
7. Brightness final = 254

### Phase 4 - Transition

Fichier: `tests/test_phase4.py`

Tests:
1. Ralentissement beats visible
2. Fade brightness smooth
3. Musique stoppée
4. Retry méthodes stop musique
5. État final stable
6. Durée 7s (±500ms)
7. Pas variation après

### Phase 5 - TTS

Fichier: `tests/test_phase5.py`

Tests:
1. TTS prononcé clairement
2. Style J.A.R.V.I.S. appliqué
3. Pulse visible et agréable
4. Durée ~5-6s
5. État final stable
6. Random phrase sélection
7. Phrase spécifique utilisée si fournie

## TESTS INTÉGRATION

Fichier: `tests/test_integration.py`

### Test scène complète

**test_full_scene_success:**
- Mock TV et Hue
- Lancer orchestrateur
- Vérifier toutes phases exécutées
- Vérifier durée totale ~33s
- Vérifier état final correct

### Test rollback

**test_scene_rollback_on_error:**
- Simuler erreur en Phase 3
- Vérifier rollback exécuté
- Vérifier état restauré
- Vérifier logs erreur

### Test cancellation

**test_manual_cancellation:**
- Lancer scène
- Cancel pendant Phase 2
- Vérifier arrêt immédiat
- Vérifier rollback

### Test intégration Lyra

**test_trigger_in_lyra:**
- Intégrer dans main.py
- Envoyer "je suis iron man"
- Vérifier scène lance
- Vérifier LLM skip

**test_normal_command:**
- Envoyer commande normale
- Vérifier LLM exécute
- Vérifier scène skip

## TESTS END-TO-END

Fichier: `tests/e2e/test_ironman_e2e.sh`

Script bash qui:

1. **Vérifie prérequis:**
   - TV accessible (ping 192.168.1.50)
   - Hue accessible (ping 192.168.1.51)
   - Lyra installé

2. **Lance Lyra:**
   - Démarre en background
   - Attend ready (5s)

3. **Trigger scène:**
   - Envoie "je suis iron man"
   - Via interface Lyra

4. **Attend fin:**
   - Sleep 35s (scène + marge)

5. **Vérifie résultat:**
   - Lumières état bleu stable
   - Brightness ~150
   - TV état attendu

6. **Cleanup:**
   - Kill Lyra
   - Logs sauvegardés

## TESTS EDGE CASES

Fichier: `tests/test_edge_cases.py`

### Double trigger

**test_double_trigger:**
- Scène running
- Envoyer 2e trigger
- Vérifier ignoré
- Vérifier 1 seule exécution

### Devices offline

**test_tv_offline_graceful:**
- TV offline
- Trigger scène
- Vérifier annulation propre
- Vérifier message clair

**test_hue_offline_abort:**
- Hue offline
- Trigger scène
- Vérifier annulation propre

### YouTube fail

**test_youtube_cast_failure:**
- Mock Cast fail
- Trigger scène
- Vérifier retry
- Vérifier continue sans musique

### Cancellation rapide

**test_rapid_cancellation:**
- Lancer scène
- Cancel pendant blackout (Phase 1)
- Vérifier arrêt rapide

### Multiple scènes

**test_multiple_scenes_queued:**
- Trigger scène 1
- Trigger scène 2 pendant scène 1
- Vérifier scène 2 ignorée

## TESTS PERFORMANCE

Fichier: `tests/test_performance.py`

### Timing précision

**test_timing_precision:**
- Mesurer durée réelle chaque phase
- Vérifier <200ms drift phase
- Vérifier durée totale ±2s

### Latence lumières

**test_latency_lights:**
- Mesurer temps commande → changement
- Vérifier <100ms

### Latence TV

**test_latency_tv:**
- Mesurer temps commande → réponse
- Vérifier <500ms

## TESTS STRESS

Fichier: `tests/test_stress.py`

### Scènes répétées

**test_repeated_scenes:**
- Lancer scène 10 fois
- Vérifier toutes réussissent
- Vérifier pas de leak mémoire

### Interruptions multiples

**test_multiple_cancellations:**
- Lancer + cancel 5 fois
- Vérifier rollback toujours OK

## STRUCTURE TESTS

```
tests/
├── __init__.py
├── test_phase0.py
├── test_phase1.py
├── test_phase2.py
├── test_phase3.py
├── test_phase4.py
├── test_phase5.py
├── test_orchestrator.py
├── test_integration.py
├── test_edge_cases.py
├── test_performance.py
├── test_stress.py
└── e2e/
    └── test_ironman_e2e.sh
```

## MOCKS NÉCESSAIRES

**Mock TV:**
- Simuler power_on/off
- Simuler volume_set
- Simuler youtube_video
- Simuler ambilight_mode
- Configurable: success/fail

**Mock Hue:**
- Simuler set_color_rgb
- Simuler set_brightness
- Simuler turn_on/off_group
- Configurable: success/fail

**Mock TTS:**
- Simuler speak
- Vérifier texte prononcé
- Vérifier style appliqué

## COVERAGE

Objectif: >80% coverage

Utiliser pytest-cov:
```bash
pytest --cov=scenes/ironman --cov-report=html
```

Zones critiques 100%:
- Détection triggers
- Gestion erreurs
- Rollback
- State machine

## DOCUMENTATION

Fichier: `tests/README.md`

Contenu:
- Comment lancer tous tests
- Comment lancer tests spécifiques
- Comment mock devices
- Interprétation résultats
- Troubleshooting tests qui fail

## CRITÈRES DE SUCCÈS

✅ Tests unitaires 100% pass
✅ Tests intégration pass
✅ Test E2E validé vrais devices
✅ Coverage >80%
✅ Edge cases gérés
✅ Performance OK
✅ Stress tests pass
✅ Doc tests claire

## LIVRABLES

1. Tous fichiers tests
2. Script E2E bash
3. Fixtures et mocks
4. README tests
5. Coverage report
