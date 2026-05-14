# PHASE 3 - PULSATIONS SYNCHRONISÉES

## CONTEXTE
Montée en puissance avec pulsations lumineuses fortes.
L'armure charge son énergie progressivement.

## TON RÔLE
Créer la phase: Pulsations rouge/bleu avec progression 0→100% brightness.

## SPÉCIFICATIONS VALIDÉES

- **Durée:** 12 secondes
- **Progression:** 0% → 100% luminosité linéaire
- **Pulsations:** Très prononcées et visibles
- **Position scène:** T+8.5s → T+20.5s

## PATTERN LUMINEUX

### Couleurs

**Base:** Bleu arc reactor RGB (0, 100, 255)
**Beat:** Rouge intense RGB (255, 0, 0)

### Rythme beats

- Basé sur AC/DC Back In Black
- Tempo: ~120 BPM
- Fréquence: 1 beat / 0.5 secondes
- Total sur 12s: ~24 beats

**Durée flash rouge:** 100ms
**Transition retour bleu:** 200ms

### Progression intensité (CRITIQUE)

Brightness évolue linéairement:

```
T+0s:   0% (brightness 0)
T+3s:   25% (brightness 63)
T+6s:   50% (brightness 127)
T+9s:   75% (brightness 190)
T+12s:  100% (brightness 254)
```

**Formule:** brightness = int((temps_écoulé / 12.0) * 254)

### Séquence par beat

Pour chaque beat:
1. Calculer brightness selon temps écoulé
2. Flash rouge à ce brightness (100ms)
3. Retour bleu à ce brightness (200ms transition)
4. Attendre prochain beat

## TIMING BEATS

Liste timestamps approximatifs (secondes depuis début phase):

```
0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5,
4.0, 4.5, 5.0, 5.5, 6.0, 6.5, 7.0, 7.5,
8.0, 8.5, 9.0, 9.5, 10.0, 10.5, 11.0, 11.5
```

Note: Timing manuel pour MVP.
V2 future: Analyse audio temps réel possible.

## OUTILS DISPONIBLES

**Lumières Hue:**
- `hue.set_group_color_rgb(81, r, g, b)` - Change couleur
- `hue.set_group_brightness(81, brightness)` - Change luminosité
- `hue.set_group_brightness(81, brightness, transitiontime=X)`
  * transitiontime en dixièmes de seconde (2 = 200ms)

## LOGIQUE RECOMMANDÉE

1. Démarrer chronomètre phase
2. Pour chaque beat:
   - Calculer brightness actuel (formule linéaire)
   - Flash rouge à ce brightness
   - Attendre 100ms
   - Retour bleu avec transition 200ms
   - Attendre prochain beat
3. Phase terminée

### Gestion timing

- Mesurer temps réel écoulé
- Ajuster sleep pour rester synchro
- Tolérance drift: <100ms acceptable

## STRUCTURE ATTENDUE

Fichier: `phase3_buildup.py`
Emplacement: `~/lyra/scenes/ironman/phases/`

Classe: `Phase3Buildup`

Constantes:
- DURATION = 12.0
- BEATS_TIMING = [liste complète]
- FLASH_DURATION = 0.1
- TRANSITION_DURATION = 0.2

Méthodes:

**execute() -> dict**
- Orchestre toutes pulsations
- Retourne: success, beats_executed, final_brightness, duration

**_calculate_brightness(elapsed: float) -> int**
- Calcule brightness selon temps
- Retourne 0-254

**_execute_beat(brightness: int)**
- Flash rouge puis retour bleu
- À la luminosité spécifiée

## TESTS

Fichier: `test_phase3.py`

Tests:
1. Brightness progression 0→254 linéaire
2. Un beat s'exécute correctement
3. Durée totale 12s (±300ms)
4. ~24 beats exécutés
5. Couleurs alternent rouge/bleu
6. Timing drift <100ms
7. Brightness final = 254

## DOCUMENTATION

Fichier: `README.md`

Contenu:
- Description effet visuel
- Explication progression linéaire
- Comment ajuster timing si désync
- Idées futures: analyse audio

## EXPÉRIENCE UTILISATEUR

Effet visuel:
- Démarrage pulsations très faibles
- Augmentation progressive constante
- Pulsations de plus en plus intenses
- Rouge/Bleu bien contrasté
- Fin: Pulsations à fond

Émotion: "L'armure se charge !"

Synchronisation:
- Beats visuels = batterie AC/DC
- Montée = intensité musicale
- Climax visuel = climax musical

## CRITÈRES DE SUCCÈS

✅ Pulsations visibles rythmiques
✅ Progression 0→100% claire
✅ Durée 12s (±300ms)
✅ Sync beats acceptable (<100ms drift)
✅ Pas de freeze/lag
✅ Couleurs prononcées
✅ Expérience énergétique

## LIVRABLES

1. `phase3_buildup.py` - Implémentation
2. `test_phase3.py` - Tests
3. `README.md` - Documentation
