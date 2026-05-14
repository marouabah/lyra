# PHASE 1 - BLACKOUT DRAMATIQUE

## CONTEXTE
Phase 1 de la scène Iron Man: Créer la tension initiale.
S'exécute immédiatement après validation Phase 0.

## TON RÔLE
Créer la phase qui éteint tout et attend 3 secondes dans le noir total.

## TIMELINE

```
T+0.0s: Éteindre TOUTES les lumières Hue (instantané)
T+0.0s: Éteindre TV si allumée
T+0.0s → T+3.0s: ATTENTE dans le noir complet
T+3.0s: Phase terminée
```

Durée totale: 3.0 secondes exactement

## ACTIONS DÉTAILLÉES

### Extinction lumières

**Groupe Hue 81 (toutes lumières):**
- Action: Éteindre
- Mode: Instantané (transition 0ms)
- Outil disponible: `hue.turn_off_group(81)`

### Extinction TV

**TV Philips:**
- D'abord vérifier si allumée
- Si ON: Éteindre avec `tv.power_off`
- Si déjà OFF: Skip (ne rien faire)

### Attente silencieuse

- Durée: Exactement 3.0 secondes
- Aucune action pendant ce temps
- Aucune variation
- Noir et silence total

## GESTION ERREURS

**Commande Hue échoue:**
- Logger warning avec détails
- Continuer quand même (non-bloquant)
- La scène continue sans lumières

**Commande TV échoue:**
- Logger warning avec détails
- Continuer quand même (non-bloquant)

Principe: Les erreurs ne bloquent pas, on fait au mieux

## PERFORMANCE

**Latence extinction:**
- Temps entre début phase et extinction complète: <500ms
- Si plus lent: Logger warning

**Durée totale:**
- Exactement 3.0 secondes (±50ms acceptable)
- Mesurer et logger durée réelle

## STRUCTURE ATTENDUE

Fichier: `phase1_blackout.py`
Emplacement: `~/lyra/scenes/ironman/phases/`

Classe: `Phase1Blackout`

Constructeur:
- Reçoit tv_controller et hue_bridge

Méthodes:

**execute() -> dict**
- Fonction principale
- Orchestre extinction + attente
- Retourne dict avec: success, lights_off, tv_off, duration

**_turn_off_lights() -> bool**
- Éteint groupe 81
- Retourne True si succès, False si erreur

**_turn_off_tv() -> bool**
- Check si TV allumée
- Éteint si nécessaire
- Retourne True si succès ou skip, False si erreur

## TESTS

Fichier: `test_phase1.py`

Tests:
1. Extinction lumières fonctionne
2. TV allumée → éteinte
3. TV déjà éteinte → skip
4. Durée exacte 3.0s (±50ms)
5. Erreur Hue → continue quand même
6. Erreur TV → continue quand même
7. Latence <500ms

## DOCUMENTATION

Fichier: `README.md`

Contenu:
- Description effet visuel attendu
- Comment tester manuellement
- Comportement en cas d'erreur
- Mesure de performance

## EXPÉRIENCE UTILISATEUR

Quand la phase démarre:
1. Toutes lumières s'éteignent instantanément
2. TV s'éteint si allumée
3. Noir et silence total 3 secondes
4. Tension maximale

Émotion: "Qu'est-ce qui va se passer ?!"

## CRITÈRES DE SUCCÈS

✅ Extinction <500ms
✅ Durée totale 3.0s (±50ms)
✅ Gère erreurs sans crash
✅ Logs clairs
✅ Tests passent
✅ Expérience immersive (noir total)

## LIVRABLES

1. `phase1_blackout.py` - Implémentation
2. `test_phase1.py` - Tests
3. `README.md` - Documentation
