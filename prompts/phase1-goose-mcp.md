# PROMPT PHASE 1 — Installation Goose + MCP (texte)

## Contexte

Projet **Lyra** : Assistant vocal DevOps local. Cette phase configure Goose CLI avec le LLM et le serveur MCP fedora-agents.

## Stack cible
- **LLM** : Qwen 2.5 Coder 14B via Ollama
- **Client** : Goose CLI
- **MCP** : fedora-agents (déjà opérationnel)

## Objectif de cette phase

Valider la chaîne : `Terminal → Goose → fedora-agents MCP → Résultat`

## Tâches à réaliser

### 1. Installer le modèle Ollama
```bash
ollama pull qwen2.5-coder:14b
```

### 2. Installer Goose CLI
```bash
# Via pipx (recommandé)
pipx install goose-ai

# Ou via pip
pip install goose-ai --break-system-packages
```

### 3. Configurer Goose avec Ollama

Créer/modifier `~/.config/goose/profiles.yaml` :
```yaml
default:
  provider: ollama
  model: qwen2.5-coder:14b
  temperature: 0.3
```

### 4. Vérifier que le MCP est compilé

```bash
# Le serveur MCP est en TypeScript, il doit être compilé en JS
cd /home/amineutron/dev/fedora-setup/scripts/agents/mcp-server

# Vérifier si dist/index.js existe
ls -la dist/index.js

# Si le fichier n'existe pas ou est ancien, recompiler :
npm run build
```

### 5. Ajouter le serveur MCP fedora-agents

```bash
goose mcp add fedora-agents -- node /home/amineutron/dev/fedora-setup/scripts/agents/mcp-server/dist/index.js
```

### 6. Tester la connexion

```bash
goose session
```

Dans Goose, tester :
- "Liste mes VMs"
- "Quel est le status de la VM preprod ?"
- "Status des backups"

## Validation Phase 1

| Test | Résultat attendu |
|------|------------------|
| `ollama list` | qwen2.5-coder:14b présent |
| `goose session` | Session démarre sans erreur |
| "Liste mes VMs" | Goose appelle `vm_status` et affiche les VMs |
| "Status backups" | Goose appelle `backup_status` et affiche l'état |

## Dépannage

### Goose ne voit pas le MCP
```bash
# Vérifier que le MCP démarre
node /home/amineutron/dev/fedora-setup/scripts/agents/mcp-server/dist/index.js

# Vérifier la config Goose
cat ~/.config/goose/profiles.yaml
```

### Ollama trop lent
```bash
# Vérifier que le GPU est utilisé
nvidia-smi
# Le modèle doit être chargé sur le GPU
```

## Fichiers modifiés

- `~/.config/goose/profiles.yaml` : Config Goose
- Aucun fichier du projet Lyra modifié

## Prochaine phase

Une fois validé, passer à **Phase 2 — Ajout Vocal (STT/TTS)**
