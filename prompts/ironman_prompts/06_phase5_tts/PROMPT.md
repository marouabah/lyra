# PHASE 5 - TTS LYRA (J.A.R.V.I.S.)

## CONTEXTE
Phase finale: Lyra parle avec voix J.A.R.V.I.S.
S'exécute après Phase 4 (T+27.5s scène globale).

## TON RÔLE
Créer la phase: TTS phrase signature + pulse bleu confirmation.

## TIMELINE

```
T+0s:    Vérifier état stable
T+0.5s:  TTS Lyra (phrase J.A.R.V.I.S.)
T+4.5s:  Pulse bleu confirmation
T+5.5s:  Phase terminée
```

Durée totale: ~5.5 secondes

## VÉRIFICATION ÉTAT (T+0s)

Avant TTS, confirmer:
- Lumières: Bleu (0,100,255) @ 150
- TV: Muette ou éteinte
- Aucune variation

## TTS LYRA (T+0.5s)

### Phrases disponibles

```
"Bonjour monsieur. Tous les systèmes sont opérationnels."
"Armure Mark 50 prête. Bienvenue, Tony."
"Jarvis en ligne. Comment puis-je vous aider?"
"Bonjour Amineutron. Que la forge commence."
"Systèmes armure initialisés. Prêt au décollage."
```

Sélection:
- Aléatoire par défaut
- Ou configurable via paramètre

### Configuration voix J.A.R.V.I.S.

Style:
- Ton: Formel, légèrement robotique
- Vitesse: 0.9x (plus lent que normal)
- Pitch: 0 (neutre) ou -1 (légèrement grave)

Implémentation dépend TTS engine Lyra:
- Si piper/coqui: Ajuster paramètres
- Si edge-tts: Voix "en-GB-RyanNeural"
- Si autre: Adapter selon possibilités

### Pendant TTS

Durée: ~3-4 secondes
Lumières: STABLES (pas de variation)

## PULSE CONFIRMATION (T+4.5s)

### Animation pulse

```
Montée:   150 → 200 brightness en 500ms
Descente: 200 → 150 brightness en 500ms
```

Couleur: Bleu constant (0, 100, 255)
Durée totale pulse: 1 seconde

Outil avec transition:
`hue.set_group_brightness(81, 200, transitiontime=5)`
Puis:
`hue.set_group_brightness(81, 150, transitiontime=5)`

(transitiontime=5 → 500ms)

### Effet

Pulse doux et élégant.
Confirmation visuelle que Lyra a parlé.

## ÉTAT FINAL (T+5.5s)

**Lumières:**
- Bleu (0, 100, 255) @ 150
- Totalement stables

**TV:**
- État inchangé depuis Phase 4

**Scène:**
- Complète et terminée
- État stable maintenu

## STRUCTURE ATTENDUE

Fichier: `phase5_tts.py`
Emplacement: `~/lyra/scenes/ironman/phases/`

Classe: `Phase5TTS`

Constantes:
- PHRASES = [liste phrases J.A.R.V.I.S.]
- PULSE_BRIGHTNESS_HIGH = 200
- PULSE_BRIGHTNESS_LOW = 150
- PULSE_DURATION = 0.5

Méthodes:

**execute(phrase: str = None) -> dict**
- Orchestre TTS + pulse
- phrase: Spécifique ou None (random)
- Retourne: success, phrase_used, duration

**_select_phrase(phrase: str = None) -> str**
- Si phrase fournie: utiliser
- Sinon: random.choice()

**_speak_jarvis_style(text: str)**
- Configure TTS style J.A.R.V.I.S.
- Parle avec ton approprié

**_confirmation_pulse()**
- Exécute pulse 150→200→150

## TESTS

Fichier: `test_phase5.py`

Tests:
1. TTS prononcé clairement
2. Style J.A.R.V.I.S. appliqué
3. Pulse visible et agréable
4. Durée totale ~5-6s
5. État final stable
6. Phrases différentes sélection random
7. Phrase spécifique utilisée si fournie

## DOCUMENTATION

Fichier: `README.md`

Contenu:
- Description effet final
- Phrases disponibles
- Configuration voix selon TTS
- Customisation phrases

## EXPÉRIENCE UTILISATEUR

Effet:
1. Silence après transition
2. Voix Lyra formelle style J.A.R.V.I.S.
3. Phrase signature claire
4. Pulse bleu élégant
5. Stabilité finale

Émotion: "I AM IRON MAN. Ready."

## CRITÈRES DE SUCCÈS

✅ TTS clair audible
✅ Style J.A.R.V.I.S. perceptible
✅ Pulse visible agréable
✅ Durée ~5-6s
✅ État final stable
✅ Sélection phrase fonctionne
✅ Expérience finale immersive

## LIVRABLES

1. `phase5_tts.py` - Implémentation
2. `test_phase5.py` - Tests
3. `README.md` - Documentation
