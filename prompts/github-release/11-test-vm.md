# Phase 11 : Test d'Installation sur VM

## Objectif
Valider l'installation from scratch sur une VM vierge pour s'assurer que tout fonctionne pour un nouvel utilisateur.

## Prérequis
- VM de test disponible (preprod-09 ou autre)
- Lyra fonctionnel sur l'hôte pour piloter les VMs

## Actions

### 1. Cloner une VM de test
```bash
# Option A: Via Lyra
# Dans Lyra: "clone preprod-09 vers lyra-install-test"

# Option B: Commande directe
sudo virt-clone --original preprod-09 --name lyra-install-test --auto-clone
sudo virsh start lyra-install-test

# Attendre que la VM soit prête
sleep 30
VM_IP=$(sudo virsh domifaddr lyra-install-test | grep -oE '192\.[0-9.]+' | head -1)
echo "VM IP: $VM_IP"
```

### 2. Nettoyer la VM (simuler utilisateur externe)
```bash
ssh lyra-install-test << 'ENDSSH'
# Supprimer toute trace de Lyra existante
rm -rf ~/dev/lyra 2>/dev/null
rm -rf ~/lyra 2>/dev/null

# Supprimer les dépendances Python potentielles (optionnel)
pip uninstall -y faster-whisper piper-tts 2>/dev/null || true

# Vérifier Ollama est installé (garder)
ollama --version

# Supprimer les modèles Ollama (simuler fresh install)
ollama rm qwen2.5-coder:14b 2>/dev/null || true

echo "✓ VM nettoyée"
ENDSSH
```

### 3. Préparer l'archive du projet
```bash
cd ~/dev

# Créer archive SANS les fichiers de build/cache
tar --exclude='lyra/.venv' \
    --exclude='lyra/mcp-server/node_modules' \
    --exclude='lyra/mcp-server/dist' \
    --exclude='lyra/.git' \
    --exclude='lyra/__pycache__' \
    --exclude='lyra/.cache' \
    --exclude='lyra/config.yaml' \
    --exclude='lyra/.env' \
    --exclude='lyra/lyra.old' \
    --exclude='lyra/*.old' \
    -czvf lyra-release-test.tar.gz lyra

ls -lh lyra-release-test.tar.gz
```

### 4. Copier sur la VM
```bash
scp ~/dev/lyra-release-test.tar.gz lyra-install-test:~/
```

### 5. Installer sur la VM
```bash
ssh lyra-install-test << 'ENDSSH'
# Extraire
cd ~
tar -xzf lyra-release-test.tar.gz
cd lyra

# Lancer l'installation
./install.sh

# Note: Le téléchargement du modèle Ollama peut prendre du temps
# Si timeout, le faire manuellement après
ENDSSH
```

### 6. Tester Lyra sur la VM
```bash
ssh -t lyra-install-test << 'ENDSSH'
cd ~/lyra
source .venv/bin/activate

# Test 1: Help
echo "=== Test: --help ==="
./run.sh --help

# Test 2: Import des modules
echo "=== Test: Imports ==="
python -c "
from modules.mcp import MCPClient
from modules.llm import OllamaClient
from modules.ui import UI
print('✓ Tous les imports OK')
"

# Test 3: Lancer Lyra interactif (timeout après 10s)
echo "=== Test: Démarrage ==="
timeout 10 ./run.sh << 'LYRAEOF' || true
help
quit
LYRAEOF

echo ""
echo "✓ Tests terminés"
ENDSSH
```

### 7. Test avec vm_verify (méthode Lyra)

Alternative: utiliser l'outil vm_verify de Lyra pour vérifier l'installation :

```bash
# Dans Lyra sur l'hôte:
# "vérifie lyra-install-test"

# Ou via MCP directement:
# vm_verify avec vm_name=lyra-install-test, compare_packages=true
```

### 8. Checklist de validation VM

```
=== INSTALLATION ===
[ ] install.sh s'exécute sans erreur
[ ] Environnement Python créé (.venv)
[ ] Dépendances Python installées
[ ] MCP server compilé (mcp-server/dist/index.js)
[ ] Modèles Piper téléchargés (models/*.onnx)
[ ] config.yaml créé depuis example
[ ] .env créé depuis example

=== FONCTIONNEL ===
[ ] ./run.sh --help fonctionne
[ ] Imports Python réussissent
[ ] Lyra démarre sans crash
[ ] "help" affiche l'aide
[ ] "quit" quitte proprement

=== ERREURS ACCEPTABLES ===
[ ] Modèle Ollama non téléchargé (long)
[ ] Mode vocal non testé (pas de GPU sur VM)
[ ] Commandes VM échouent (pas de libvirt sur VM test)
```

### 9. Nettoyer après test
```bash
# Option A: Via Lyra
# "supprime lyra-install-test"

# Option B: Commande directe
sudo virsh destroy lyra-install-test 2>/dev/null
sudo virsh undefine lyra-install-test --remove-all-storage

# Supprimer l'archive
rm -f ~/dev/lyra-release-test.tar.gz
```

## Problèmes Courants

### "Module not found"
```bash
# S'assurer que le venv est activé
source .venv/bin/activate
pip install -r requirements.txt
```

### "MCP server not found"
```bash
# Recompiler le MCP server
cd mcp-server && npm install && npm run build && cd ..
```

### "Ollama connection refused"
```bash
# Vérifier qu'Ollama tourne
systemctl --user status ollama
# Ou
ollama serve &
```

### "Permission denied" sur scripts
```bash
chmod +x install.sh run.sh scripts/*.sh
```

## Tests de Validation

```bash
# Sur l'hôte, vérifier que la VM de test n'existe plus
sudo virsh list --all | grep lyra-install-test && echo "⚠ VM encore présente" || echo "✓ VM supprimée"

# Vérifier que l'archive de test est supprimée
[ -f ~/dev/lyra-release-test.tar.gz ] && echo "⚠ Archive encore présente" || echo "✓ Archive supprimée"
```

## Checklist Finale
- [ ] VM clonée et démarrée
- [ ] VM nettoyée (pas de Lyra existant)
- [ ] Archive créée et copiée
- [ ] install.sh exécuté avec succès
- [ ] Lyra fonctionne sur VM
- [ ] VM supprimée après test
- [ ] Archive supprimée
- [ ] Prêt pour publication GitHub
