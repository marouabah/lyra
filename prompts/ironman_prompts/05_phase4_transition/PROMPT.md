# PHASE 4 - TRANSITION & STABILISATION

## CONTEXTE
Ralentissement puis stabilisation après l'apogée.
Du chaos énergétique vers le calme maîtrisé.

## TON RÔLE
Créer la phase: Ralentir beats → Fondu bleu → Couper musique.

## SPÉCIFICATIONS VALIDÉES

- **Début:** T+20.5s scène globale
- **Fin:** T+27.5s scène globale
- **Durée:** 7 secondes exactement
- **Musique:** Coupée PENDANT cette phase

## TIMELINE STRICTE

```
T+0s:             Dernière pulsation forte (100%)
T+0s → T+3s:      Ralentissement beats progressif
T+3s → T+5s:      Fondu vers bleu stable
T+4s:             Couper musique
T+5s → T+7s:      Stabilisation complète
T+7s:             Phase terminée
```

Durée totale: 7 secondes

## RALENTISSEMENT BEATS (T+0s → T+3s)

### Pattern ralenti

Timestamps beats (secondes depuis début phase):
```
0.0s  - Beat normal
0.5s  - Encore normal
1.2s  - Commence ralentir
2.0s  - Plus lent
3.0s  - Dernier beat
```

Total: 5 beats sur 3 secondes

### Caractéristiques

- Brightness: Reste 100% (254)
- Couleurs: Rouge/bleu alterné
- Durée flash: 100ms
- Transition: 200ms
- **Seul changement:** Espacement augmente

## FONDU BLEU STABLE (T+3s → T+5s)

### Transition

**De:**
- Bleu (0, 100, 255) @ brightness 254

**Vers:**
- Bleu (0, 100, 255) @ brightness 150

**Durée:** 2 secondes
**Type:** Fluide et progressive

Outil avec transition:
`hue.set_group_brightness(81, 150, transitiontime=20)`
(transitiontime en dixièmes de seconde, 20 = 2s)

### Effet

Les lumières "respirent" vers état calme.
Pas de changement brusque, tout doux.

## ARRÊT MUSIQUE (T+4s)

### Priorités

Essayer dans cet ordre, premier qui marche:

1. **Pause YouTube**
   - `tv.send_key("Pause")`
   - Préféré: Garde TV allumée

2. **Volume à 0**
   - `tv.volume_set(0)`
   - Alternative si pause marche pas

3. **Éteindre TV**
   - `tv.power_off`
   - Dernier recours

### Gestion erreurs

- Si tout échoue: Logger mais continuer
- Musique continue: Pas grave
- Ne PAS bloquer

## STABILISATION (T+5s → T+7s)

### État final

**Lumières:**
- Bleu (0, 100, 255)
- Brightness: 150
- Mode: Statique (aucune variation)

**TV:**
- Idéal: Allumée muette/pause
- Acceptable: Éteinte

**Ambiance:**
- Calme total
- Stabilité absolue
- Zéro mouvement

Prépare Phase 5 (TTS).

## STRUCTURE ATTENDUE

Fichier: `phase4_transition.py`
Emplacement: `~/lyra/scenes/ironman/phases/`

Classe: `Phase4Transition`

Constantes:
- DURATION = 7.0
- SLOWDOWN_BEATS = [0.0, 0.5, 1.2, 2.0, 3.0]
- FADE_START = 3.0
- MUSIC_STOP = 4.0
- STABLE_BRIGHTNESS = 150

Méthodes:

**execute() -> dict**
- Orchestre transition complète
- Retourne: success, music_stopped, duration

**_slowdown_beats()**
- Exécute 5 beats ralentis

**_fade_to_stable()**
- Transition brightness 254→150

**_stop_music() -> bool**
- Essaye pause → volume 0 → power off
- Retourne True si stoppée

## TESTS

Fichier: `test_phase4.py`

Tests:
1. Ralentissement visible
2. Fade smooth
3. Musique stoppée
4. Retry méthodes stop musique
5. État final stable
6. Durée 7s (±500ms)
7. Stabilité maintenue après

## DOCUMENTATION

Fichier: `README.md`

Contenu:
- Description transition visuelle
- Explication ralentissement
- Méthodes arrêt musique
- État stable en sortie

## EXPÉRIENCE UTILISATEUR

Effet:
1. Pulsations ralentissent visiblement
2. Lumières se "calment" doucement
3. Musique s'arrête (pause idéalement)
4. Retour bleu stable apaisant

Émotion: "L'armure est stable"

Transition: Chaos → Calme maîtrisé

## CRITÈRES DE SUCCÈS

✅ Ralentissement perceptible
✅ Fondu fluide agréable
✅ Musique coupée T+4s (±500ms)
✅ Durée 7s (±500ms)
✅ État final stable
✅ Pas variation après
✅ Expérience progressive

## LIVRABLES

1. `phase4_transition.py` - Implémentation
2. `test_phase4.py` - Tests
3. `README.md` - Documentation
