# Phase 0 : Sauvegarde Avant Modifications

## Objectif
Créer une sauvegarde complète du projet Lyra avant toute modification pour la publication GitHub.

## Actions

### 1. Copie locale
```bash
cd ~/dev
cp -r lyra lyra.old
echo "Copie créée: $(du -sh lyra.old)"
```

### 2. Archive compressée
```bash
tar -czvf lyra-backup-pre-github-$(date +%Y%m%d-%H%M).tar.gz --exclude='lyra.old/.venv' --exclude='lyra.old/mcp-server/node_modules' lyra.old
ls -lh lyra-backup-*.tar.gz
```

### 3. Copie sur VM preprod
```bash
# Créer le dossier backups si nécessaire
ssh preprod-09 "mkdir -p ~/backups"

# Copier l'archive
scp lyra-backup-pre-github-*.tar.gz preprod-09:~/backups/

# Vérifier
ssh preprod-09 "ls -lh ~/backups/lyra-backup-pre-github-*.tar.gz"
```

## Tests de Validation

```bash
# Test 1: Copie locale existe
[ -d ~/dev/lyra.old ] && echo "✓ lyra.old existe" || echo "✗ ERREUR"

# Test 2: Archive existe
ls ~/dev/lyra-backup-pre-github-*.tar.gz && echo "✓ Archive existe" || echo "✗ ERREUR"

# Test 3: Archive sur VM
ssh preprod-09 "ls ~/backups/lyra-backup-pre-github-*.tar.gz" && echo "✓ Backup VM OK" || echo "✗ ERREUR"

# Test 4: Taille cohérente (> 1MB)
SIZE=$(du -m ~/dev/lyra.old | cut -f1)
[ $SIZE -gt 1 ] && echo "✓ Taille OK ($SIZE MB)" || echo "✗ Taille suspecte"
```

## Checklist
- [ ] lyra.old créé
- [ ] Archive tar.gz créée
- [ ] Archive copiée sur preprod-09
- [ ] Taille > 1 MB
