# Phase 12 : Vidéo de Démonstration

## Objectif
Enregistrer une vidéo de démonstration pour YouTube et/ou le README GitHub.

## Prérequis
- Lyra fonctionnel (mode texte et/ou vocal)
- Logiciel d'enregistrement (OBS, SimpleScreenRecorder, ou asciinema)
- Micro fonctionnel (pour narration optionnelle)

## Scénario Suggéré (~3-5 minutes)

### 1. Introduction (30s)
```
- Écran titre: "Lyra - Assistant Vocal DevOps"
- Tagline: "100% local, 0€ API"
- Montrer le terminal prêt
```

### 2. Démo Mode Texte (1 min)
```bash
# Lancer Lyra
./run.sh

# Commandes à montrer:
Toi: liste mes VMs
# Attendre la réponse

Toi: démarre preprod-09
# Montrer la confirmation Human-in-the-Loop
# Confirmer avec 'o'

Toi: status de preprod-09
# Montrer le résultat

Toi: fais un snapshot de preprod-09
# Confirmer
```

### 3. Démo Mode Vocal (1 min)
```bash
# Lancer en mode vocal
./run.sh --vocal

# Montrer:
# - Le bip de début d'écoute
# - La barre de niveau audio
# - Dire: "status de preprod-09"
# - La réponse TTS
```

### 4. Démo Actions Multiples (30s)
```bash
Toi: supprime sandbox-01 et sandbox-02
# Montrer la todo list
# Montrer les options: [T]out / [1] par 1 / [n]on
# Annuler avec 'n' (pas vraiment supprimer en démo!)
```

### 5. Démo Backups (30s)
```bash
Toi: status des backups
# Montrer le dashboard

Toi: liste les backups timeshift
```

### 6. Conclusion (30s)
```
- Récap des features:
  - 100% local
  - Confirmation avant action
  - Mode texte et vocal
  - Français natif

- Call to action:
  - Lien GitHub
  - "Star le repo!"
```

## Outils d'Enregistrement

### Option A: OBS Studio (recommandé pour vidéo complète)
```bash
# Installer
sudo dnf install obs-studio

# Configuration:
# - Source: Window Capture (terminal)
# - Audio: Micro + Desktop Audio
# - Output: 1920x1080, 30fps, MP4
```

### Option B: SimpleScreenRecorder (plus simple)
```bash
# Installer
sudo dnf install simplescreenrecorder

# Sélectionner la fenêtre du terminal
# Enregistrer en MP4
```

### Option C: asciinema (terminal uniquement, pas de son)
```bash
# Pour GIF/embed sans narration
asciinema rec demo.cast
# Puis upload sur asciinema.org
```

### Option D: Kazam (GNOME)
```bash
sudo dnf install kazam
# Simple screen recorder avec audio
```

## Post-Production

### Édition basique avec Kdenlive
```bash
sudo dnf install kdenlive

# Actions:
# - Couper les temps morts
# - Ajouter titres/texte
# - Ajouter musique de fond (optionnel)
# - Exporter en 1080p MP4
```

### Conversion en GIF (pour README)
```bash
# Extraire un segment de 30s pour le GIF
ffmpeg -i demo.mp4 -ss 00:00:30 -t 30 \
    -vf "fps=10,scale=800:-1:flags=lanczos" \
    -c:v gif docs/demo.gif

# Optimiser la taille
gifsicle -O3 --colors 256 docs/demo.gif -o docs/demo-optimized.gif
```

## Upload

### YouTube
1. Créer un compte/chaîne si nécessaire
2. Upload la vidéo
3. Titre: "Lyra - Assistant Vocal DevOps 100% Local (Demo)"
4. Description avec lien GitHub
5. Tags: devops, voice assistant, kvm, linux, ollama, whisper
6. Thumbnail accrocheuse

### GitHub README
```markdown
## 🎬 Demo

[![Lyra Demo](https://img.youtube.com/vi/VIDEO_ID/0.jpg)](https://www.youtube.com/watch?v=VIDEO_ID)

Ou GIF intégré:
![Demo](docs/demo.gif)
```

## Tips pour une Bonne Vidéo

### Préparation
- [ ] Terminal propre (`clear`)
- [ ] Police de terminal agrandie (14-16pt)
- [ ] Thème sombre
- [ ] VMs de démo prêtes (preprod-09, sandbox-01, sandbox-02)
- [ ] Micro testé
- [ ] Script répété 1-2 fois

### Pendant l'enregistrement
- [ ] Parler clairement (si narration)
- [ ] Attendre les réponses de Lyra
- [ ] Pas de mouvements de souris inutiles
- [ ] Si erreur, recommencer le segment

### Post-production
- [ ] Couper les hésitations/erreurs
- [ ] Accélérer les temps d'attente (x2)
- [ ] Ajouter sous-titres si narration
- [ ] Vérifier le son est audible

## Checklist Finale
- [ ] Scénario préparé
- [ ] Environnement de démo prêt
- [ ] Outil d'enregistrement configuré
- [ ] Vidéo enregistrée
- [ ] Vidéo éditée (coupures, titres)
- [ ] GIF extrait pour README
- [ ] Vidéo uploadée sur YouTube
- [ ] Lien ajouté dans README
- [ ] Thumbnail créée

## Ressources

- [OBS Studio](https://obsproject.com/)
- [Kdenlive](https://kdenlive.org/)
- [asciinema](https://asciinema.org/)
- [Musique libre de droits](https://www.youtube.com/audiolibrary)
