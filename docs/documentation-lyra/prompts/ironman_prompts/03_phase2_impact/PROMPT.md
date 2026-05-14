# PHASE 2 - PREMIER IMPACT

## CONTEXTE
L'arc reactor s'allume après 3s de noir.
Explosion lumineuse + démarrage musique AC/DC.

## TON RÔLE
Créer la phase: Flash blanc → Bleu arc reactor → Musique YouTube.

## TIMELINE EXACTE

```
T+0.0s:  Flash blanc pur instantané
T+0.2s:  Transition vers bleu arc reactor
T+0.5s:  Allumer TV
T+2.5s:  Lancer YouTube vidéo AC/DC
T+3.0s:  Activer Ambilight mode audio
T+3.5s:  Phase terminée
```

Durée totale: 3.5 secondes

## ACTIONS DÉTAILLÉES

### Flash blanc (T+0.0s)

**Lumières Hue groupe 81:**
- Couleur: RGB (255, 255, 255) - Blanc pur
- Luminosité: 254 (maximum)
- Transition: 0ms (instantané)
- Durée flash: 200ms
- Effet: Aveuglant, brutal

Outils:
- `hue.set_group_color_rgb(81, 255, 255, 255)`
- `hue.set_group_brightness(81, 254)`

### Transition bleu (T+0.2s)

**Lumières Hue:**
- Couleur: RGB (0, 100, 255) - Bleu arc reactor
- Luminosité: 200
- Transition: 300ms (rapide mais fluide)
- Effet: Stabilisation électrique

### Allumage TV (T+0.5s)

**TV Philips:**
- Action: `tv.power_on`
- Attendre 2 secondes boot complet

### Lancement musique (T+2.5s)

**YouTube via Cast:**
- Vidéo: AC/DC - Back In Black
- ID: pAgnJDJN4VA
- URL: https://youtube.com/watch?v=pAgnJDJN4VA
- Outil: `tv.youtube_video("pAgnJDJN4VA")`

**Gestion erreur Cast:**
- Si échec: Retry 1 fois
- Si toujours échec:
  * Logger erreur
  * Continuer en mode "lights only"
  * Ne PAS bloquer la scène

### Ambilight (T+3.0s)

**TV:**
- Mode: follow_audio (suit le son)
- Outil: `tv.ambilight_mode("follow_audio")`
- Si erreur: Logger warning, continuer

## SYNCHRONISATION

Le flash blanc doit être pile au début du riff guitare.

Timing critique:
- Flash à T+0.0s de cette phase
- Soit T+5.0s scène globale (2s validation + 3s blackout)
- YouTube démarre ~0.5-1s après commande Cast
- Donc lancer à T+2.5s pour sync audio

## GESTION ERREURS

**YouTube Cast échoue:**
- Retry automatique 1 fois
- Si encore échec:
  * Logger: "YouTube Cast failed, lights-only mode"
  * Continuer normalement
  * Skip Ambilight (pas de son)

**Ambilight échoue:**
- Logger warning
- Continuer (pas critique)

**TV ne s'allume pas:**
- Logger erreur
- Continuer (lumières seules)

## STRUCTURE ATTENDUE

Fichier: `phase2_impact.py`
Emplacement: `~/lyra/scenes/ironman/phases/`

Classe: `Phase2Impact`

Constantes:
- YOUTUBE_VIDEO_ID = "pAgnJDJN4VA"
- FLASH_DURATION = 0.2
- BLUE_TRANSITION = 0.3

Méthodes:

**execute() -> dict**
- Orchestre toute la séquence
- Retourne: success, music_started, ambilight_active, duration

**_flash_white()**
- Flash blanc instantané 200ms

**_transition_to_blue()**
- Transition fluide vers bleu

**_launch_music() -> bool**
- Allume TV
- Lance YouTube
- Retourne True si musique démarre

**_activate_ambilight() -> bool**
- Active follow_audio
- Retourne True si succès

## TESTS

Fichier: `test_phase2.py`

Tests:
1. Flash blanc visible et instantané
2. Transition bleu fluide 300ms
3. TV s'allume
4. YouTube démarre
5. Retry si YouTube échoue
6. Ambilight s'active
7. Continue sans musique si Cast fail
8. Durée totale ~3.5s (±200ms)

## DOCUMENTATION

Fichier: `README.md`

Contenu:
- Effet visuel attendu
- Synchronisation musique
- Troubleshooting YouTube
- Troubleshooting Ambilight

## EXPÉRIENCE UTILISATEUR

Après 3s de noir:
1. **FLASH** blanc aveuglant 200ms
2. Stabilisation rapide bleu électrique
3. TV s'allume
4. Riff AC/DC démarre pile poil
5. Ambilight commence à réagir

Émotion: "L'armure démarre !"

## CRITÈRES DE SUCCÈS

✅ Flash blanc brutal visible
✅ Transition bleu fluide
✅ Musique sync (±500ms)
✅ Gère échec YouTube gracieusement
✅ Durée 3.5s (±200ms)
✅ Ambilight actif si musique OK
✅ Expérience immersive

## LIVRABLES

1. `phase2_impact.py` - Implémentation
2. `test_phase2.py` - Tests
3. `README.md` - Documentation
