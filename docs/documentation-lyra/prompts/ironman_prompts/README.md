# SCÈNE IRON MAN - PROMPTS DE DÉVELOPPEMENT

## 🦾 DESCRIPTION

Cette archive contient 9 prompts pour implémenter la scène "Iron Man" de Lyra.
Chaque prompt est une instruction complète pour générer le code d'une phase.

## 📋 CONTENU

```
ironman_prompts/
├── README.md (ce fichier)
├── 01_phase0_detection/
│   ├── PROMPT.md
│   └── README.md
├── 02_phase1_blackout/
│   ├── PROMPT.md
│   └── README.md
├── 03_phase2_impact/
│   ├── PROMPT.md
│   └── README.md
├── 04_phase3_buildup/
│   ├── PROMPT.md
│   └── README.md
├── 05_phase4_transition/
│   ├── PROMPT.md
│   └── README.md
├── 06_phase5_tts/
│   ├── PROMPT.md
│   └── README.md
├── 07_orchestrator/
│   ├── PROMPT.md
│   └── README.md
├── 08_integration/
│   ├── PROMPT.md
│   └── README.md
└── 09_tests/
    ├── PROMPT.md
    └── README.md
```

## 🎯 UTILISATION

### Extraction

```bash
cd ~/lyra/prompts
tar -xzf ironman_prompts.tar.gz
```

### Ordre d'implémentation recommandé

1. **Phase 0 - Détection** (critique, base de tout)
2. **Phase 1 - Blackout** (simple, test rapide)
3. **Phase 2 - Impact** (validation TV + Hue)
4. **Orchestrateur** (MVP simple pour tester)
5. **Phase 3 - Buildup** (plus complexe)
6. **Phase 4 - Transition** (finalisation)
7. **Phase 5 - TTS** (polish final)
8. **Intégration** (dans Lyra main)
9. **Tests** (validation complète)

### Génération du code

Pour chaque prompt:

```bash
cd 01_phase0_detection
# Lire PROMPT.md
# Donner le prompt à l'IA de ton choix
# Implémenter selon instructions
# Tester
# Passer au suivant
```

## 📊 TIMELINE SCÈNE COMPLÈTE

```
T+0s:    Phase 0 - Validation (2s)
T+2s:    Phase 1 - Blackout (3s)
T+5s:    Phase 2 - Impact (3.5s)
T+8.5s:  Phase 3 - Buildup (12s) - 0→100% brightness
T+20.5s: Phase 4 - Transition (7s) - Ralentissement + Fondu
T+27.5s: Phase 5 - TTS (5.5s) - Lyra parle
T+33s:   État stable
```

Durée totale: ~33 secondes

## 🎬 DÉCLENCHEURS

Phrases qui activent la scène:
- "je suis iron man"
- "je suis tony stark"
- "je suis tony"
- "mode iron man"
- "scène iron man"

## 🔧 PRÉREQUIS TECHNIQUES

**Hardware:**
- TV Philips 55OLED705 (IP: 192.168.1.50)
- Bridge Hue (IP: 192.168.1.51)
- 5 lumières Hue (ID 1-5, groupe 81)

**Software:**
- Python 3.11+
- Bibliothèque phue
- Bibliothèque requests
- catt (YouTube Cast)
- TTS engine (piper/coqui/edge-tts)

**Lyra:**
- Système principal fonctionnel
- MCP TV et Hue déjà implémentés
- TTS configuré

## 📝 NOTES IMPORTANTES

### Pas de code dans les prompts

Les prompts contiennent UNIQUEMENT des instructions.
Le code est généré par l'IA selon ces instructions.

### Tests inclus

Chaque prompt demande:
- Implémentation fonctionnelle
- Tests unitaires
- Documentation

### Flexibilité

Les prompts sont des guides, pas des ordres stricts.
Adapter selon contraintes techniques rencontrées.

## 🎨 EXPÉRIENCE VISUELLE ATTENDUE

1. **Noir total** (3s) - Tension
2. **Flash blanc brutal** - Arc reactor boot
3. **Stabilisation bleu** - Électrique
4. **Pulsations croissantes** (12s) - Charge armure
5. **Ralentissement** - Contrôle retrouvé
6. **Stabilité bleue** - Prêt
7. **Voix J.A.R.V.I.S.** - Confirmation

Émotion finale: "I AM IRON MAN. Ready."

## 🐛 TROUBLESHOOTING

### TV ne répond pas
- Vérifier IP: 192.168.1.50
- Vérifier JointSpace API activée
- Tester manuellement: `curl http://192.168.1.50:1925/6/system`

### Hue ne répond pas
- Vérifier IP: 192.168.1.51
- Vérifier Bridge accessible
- Tester: `ping 192.168.1.51`

### YouTube Cast fail
- Vérifier catt installé: `catt --version`
- Vérifier Chromecast intégré TV actif
- Tester: `catt -d "Philips TV" cast https://youtube.com/watch?v=pAgnJDJN4VA`

### Désynchronisation musique
- Ajuster timing dans Phase 2
- Vérifier latence réseau
- Possibilité: Audio local au lieu YouTube

## 📚 RESSOURCES

**Documentation:**
- Chaque prompt a son README.md
- Tests documentés
- Architecture expliquée

**Support:**
- Logs détaillés dans chaque phase
- State machine avec rollback
- Gestion erreurs robuste

## ✅ CRITÈRES DE SUCCÈS GLOBAL

Scène validée si:
- ✅ Toutes phases implémentées
- ✅ Tests passent (>80% coverage)
- ✅ Durée totale ~33s (±2s)
- ✅ Expérience immersive
- ✅ Gestion erreurs robuste
- ✅ Rollback fonctionnel
- ✅ Intégration Lyra propre

## 🚀 PROCHAINES ÉTAPES

Après implémentation:
1. Tester scène complète
2. Ajuster timing si besoin
3. Créer variations (mode jour/nuit)
4. Easter eggs (5% probabilité)
5. Scènes alternatives (autres films)

## 👤 AUTEUR

Prompts créés pour: Amineutron
Projet: Lyra (Assistant IA local)
Date: 2026-01-24

---

**Que la forge soit avec toi ! 🔨⚡**
