# Phase 7 : Assets Visuels

## Objectif
Créer les GIFs, screenshots et assets pour un README attrayant.

## Actions

### 1. Créer le dossier docs
```bash
mkdir -p ~/dev/lyra/docs
```

### 2. Screenshot mode texte

```bash
# Méthode 1: Capture manuelle
# 1. Lancer Lyra
cd ~/dev/lyra && source .venv/bin/activate && ./run.sh

# 2. Exécuter quelques commandes pour avoir du contenu:
#    - "liste mes VMs"
#    - "status de preprod-09"

# 3. Capturer avec:
#    - gnome-screenshot -a -f ~/dev/lyra/docs/screenshot-text.png
#    - Ou: spectacle (KDE)
#    - Ou: flameshot gui

# Méthode 2: Import depuis terminal
import -window root ~/dev/lyra/docs/screenshot-text.png
```

### 3. Screenshot mode vocal

```bash
# Lancer en mode vocal
./run.sh --vocal

# Attendre que la barre de niveau audio soit visible
# Capturer quand tu parles (barre active)

gnome-screenshot -a -f ~/dev/lyra/docs/screenshot-vocal.png
```

### 4. GIF de démonstration

#### Option A: asciinema (recommandé - fonctionne sans GPU)
```bash
# Installer asciinema
pip install asciinema

# Enregistrer
cd ~/dev/lyra
asciinema rec docs/demo.cast

# Dans l'enregistrement, faire:
# 1. ./run.sh
# 2. "liste mes VMs"
# 3. Attendre réponse
# 4. "démarre preprod-09" + confirmer avec 'o'
# 5. "status de preprod-09"
# 6. quit
# 7. exit

# Convertir en GIF (via Docker)
docker run --rm -v $PWD/docs:/data asciinema/asciicast2gif \
    -w 80 -h 24 -s 2 \
    /data/demo.cast /data/demo.gif

# Alternative: uploader sur asciinema.org et embedder
asciinema upload docs/demo.cast
```

#### Option B: peek (GUI screen recorder)
```bash
# Installer
sudo dnf install peek

# Lancer peek
peek &

# Sélectionner la zone du terminal
# Enregistrer ~30 secondes de démo
# Sauvegarder en GIF: docs/demo.gif
```

#### Option C: OBS + ffmpeg
```bash
# Enregistrer avec OBS en MP4
# Puis convertir:
ffmpeg -i demo.mp4 -vf "fps=10,scale=800:-1:flags=lanczos" -c:v gif docs/demo.gif
```

### 5. Utiliser le script record-demo.sh (créé en Phase 5)
```bash
cd ~/dev/lyra
./scripts/record-demo.sh
```

### 6. Logo (optionnel)

```bash
# Option simple: emoji dans le README (pas besoin de fichier)
# Le README utilisera: 🎙️

# Option avancée: créer un logo avec ImageMagick
convert -size 200x200 xc:transparent \
    -font "DejaVu-Sans-Bold" -pointsize 100 \
    -fill "#4A90D9" -gravity center \
    -annotate 0 "🎙️" \
    ~/dev/lyra/docs/logo.png 2>/dev/null || echo "ImageMagick non disponible, skip logo"
```

### 7. Placeholder si pas de captures disponibles

Si tu ne peux pas créer les assets maintenant, créer des placeholders :
```bash
# Créer des fichiers placeholder
echo "TODO: Ajouter screenshot mode texte" > ~/dev/lyra/docs/screenshot-text.md
echo "TODO: Ajouter screenshot mode vocal" > ~/dev/lyra/docs/screenshot-vocal.md
echo "TODO: Ajouter GIF de démo" > ~/dev/lyra/docs/demo.md

# Le README peut référencer asciinema.org au lieu d'un GIF local
```

## Fichiers Attendus

| Fichier | Description | Priorité |
|---------|-------------|----------|
| `docs/demo.gif` | GIF de démo ~30s | Haute |
| `docs/demo.cast` | Source asciinema | Moyenne |
| `docs/screenshot-text.png` | Mode texte | Haute |
| `docs/screenshot-vocal.png` | Mode vocal avec barre audio | Moyenne |
| `docs/logo.png` | Logo Lyra | Basse (optionnel) |

## Conseils pour de bons screenshots

1. **Terminal propre**: `clear` avant de commencer
2. **Police lisible**: Augmenter la taille de police du terminal
3. **Thème sombre**: Plus agréable pour les yeux
4. **Contenu intéressant**: Montrer une vraie interaction
5. **Résolution**: 1920x1080 ou plus, puis réduire si besoin

## Tests de Validation

```bash
# Test: Le dossier docs existe
[ -d ~/dev/lyra/docs ] && echo "✓ docs/ existe" || echo "✗ ERREUR"

# Test: Au moins un asset présent
ls ~/dev/lyra/docs/*.{gif,png,cast,md} 2>/dev/null | head -3

# Test: Taille raisonnable des fichiers (< 10MB chacun)
find ~/dev/lyra/docs -type f -size +10M 2>/dev/null && echo "⚠ Fichiers > 10MB trouvés" || echo "✓ Tailles OK"
```

## Checklist
- [ ] docs/ créé
- [ ] demo.gif OU demo.cast créé
- [ ] screenshot-text.png créé (ou placeholder)
- [ ] screenshot-vocal.png créé (ou placeholder)
- [ ] Fichiers < 10MB chacun
- [ ] Assets testés dans le README (liens valides)
