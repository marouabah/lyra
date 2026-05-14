# ORCHESTRATEUR PRINCIPAL

## CONTEXTE
Créer le chef d'orchestre qui coordonne toutes les phases.
C'est lui qui lance les phases dans le bon ordre et gère les erreurs.

## TON RÔLE
Créer la state machine robuste pour la scène Iron Man complète.

## STATE MACHINE

États possibles:
```
IDLE → VALIDATING → BLACKOUT → IMPACT → BUILDUP → TRANSITION → TTS → STABLE
  ↑                                                                      |
  └─────────────────────── ROLLBACK ←──────────────────────────────────┘
```

**IDLE:** En attente trigger
**VALIDATING:** Phase 0 en cours
**BLACKOUT:** Phase 1
**IMPACT:** Phase 2
**BUILDUP:** Phase 3
**TRANSITION:** Phase 4
**TTS:** Phase 5
**STABLE:** Scène terminée, état stable
**ROLLBACK:** Erreur, restauration

## TIMELINE COMPLÈTE

```
T+0s:    Phase 0 - Validation (2s)
T+2s:    Phase 1 - Blackout (3s)
T+5s:    Phase 2 - Impact (3.5s)
T+8.5s:  Phase 3 - Buildup (12s)
T+20.5s: Phase 4 - Transition (7s)
T+27.5s: Phase 5 - TTS (5.5s)
T+33s:   État stable
```

Durée totale: ~33 secondes

## GESTION ERREURS

### Erreur Phase 0

- Annuler immédiatement
- Message clair utilisateur
- Pas de rollback (rien changé)
- Rester en IDLE

### Erreur Phases 1-5

- Logger erreur + stacktrace complète
- Exécuter rollback automatique
- Notifier: "Scène interrompue, restauration"
- Restaurer état depuis Phase 0
- Retour IDLE

### Interruption manuelle

Commandes acceptées:
- "annule scène"
- "stop"
- "arrête"

Action:
- Rollback immédiat
- Confirmation vocale
- Retour IDLE

## LOGGING DÉTAILLÉ

Pour chaque phase:

**Début:**
```
[IRONMAN] Phase X started
```

**Fin:**
```
[IRONMAN] Phase X completed (duration: Xs)
```

**Erreur:**
```
[IRONMAN] Phase X failed: <error>
<stacktrace complète>
```

Niveau:
- INFO pour flow normal
- ERROR pour erreurs

## STRUCTURE ATTENDUE

Fichier: `orchestrator.py`
Emplacement: `~/lyra/scenes/ironman/`

Classe: `IronManOrchestrator`

États (Enum):
```
IDLE, VALIDATING, BLACKOUT, IMPACT,
BUILDUP, TRANSITION, TTS, STABLE, ROLLBACK
```

Constructeur:
- Reçoit: tv_controller, hue_bridge, tts_engine
- Initialise toutes les phases
- État initial: IDLE

Attributs:
- state: État actuel
- saved_state: État sauvegardé Phase 0
- Instances de chaque phase

Méthodes:

**trigger(text: str) -> bool**
- Vérifie si trigger détecté
- Si oui ET état=IDLE: Lance scène
- Retourne True si scène lancée

**_execute_scene()**
- Exécute toutes phases séquentiellement
- Gère erreurs avec try/except
- Rollback automatique si erreur

**_run_phase(state, func)**
- Change état
- Log début
- Exécute fonction phase
- Log fin avec durée
- Retourne résultat

**_rollback()**
- État → ROLLBACK
- Log "Rollback started"
- Restaure saved_state
- Rétablit TV + Hue état initial
- État → IDLE
- Log "Rollback completed"

**cancel()**
- Annulation manuelle
- Si IDLE: Rien
- Sinon: Rollback

## TESTS

Fichier: `test_orchestrator.py`

Tests:
1. Trigger détecté → scène lance
2. Trigger non-match → rien
3. Scène déjà running → ignore 2e trigger
4. Toutes phases exécutées ordre
5. Erreur Phase 3 → rollback auto
6. Cancel manuel → rollback
7. Durée totale ~33s (±2s)
8. Logs corrects toutes phases

## DOCUMENTATION

Fichier: `README.md`

Contenu:
- Architecture state machine
- Flow complet scène
- Gestion erreurs
- Comment intégrer dans Lyra
- Comment tester manuellement
- Comment debugger

## INTÉGRATION LYRA

Point d'entrée dans `main.py`:

Avant LLM:
- Check si trigger Iron Man
- Si oui: orchestrator.trigger()
- Si scène lancée: Return (skip LLM)
- Sinon: Flow normal

## ROLLBACK DÉTAILS

Restauration depuis saved_state JSON:

**TV:**
- Remettre volume initial
- Rallumer si était allumée
- Relancer app si était ouverte

**Lumières Hue:**
- Pour chaque lumière:
  * Remettre on/off
  * Remettre brightness
  * Remettre couleur RGB
- Réactiver scène si était active

## CRITÈRES DE SUCCÈS

✅ Exécute phases dans l'ordre
✅ Gère erreurs gracieusement
✅ Rollback fonctionne
✅ Logs clairs utiles
✅ Cancellation possible
✅ Durée ~33s (±2s)
✅ Intégrable facilement

## LIVRABLES

1. `orchestrator.py` - Implémentation complète
2. `test_orchestrator.py` - Tests end-to-end
3. `README.md` - Documentation intégration
