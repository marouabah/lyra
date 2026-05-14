# Phase 8 : README Premium GitHub

## Objectif
Réécrire le README avec un design moderne et attrayant pour GitHub.

## Actions

### 1. Sauvegarder l'ancien README
```bash
cp ~/dev/lyra/README.md ~/dev/lyra/README.md.old
```

### 2. Créer le nouveau README.md

```bash
cat > ~/dev/lyra/README.md << 'READMEEOF'
<div align="center">

# 🎙️ Lyra

**Assistant vocal DevOps 100% local**

Contrôlez votre infrastructure KVM et vos backups par la voix, en français.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-green.svg)](https://ollama.ai)

[Demo](#-demo) • [Features](#-features) • [Installation](#-installation) • [Usage](#-usage) • [Architecture](#-architecture)

</div>

---

## 🎬 Demo

<!-- Option 1: GIF local -->
<div align="center">
  <img src="docs/demo.gif" alt="Lyra Demo" width="800">
</div>

<!-- Option 2: asciinema embed (décommenter si utilisé)
[![asciicast](https://asciinema.org/a/XXXXXX.svg)](https://asciinema.org/a/XXXXXX)
-->

---

## ❓ Why Lyra?

### 🔒 100% Local & Private
- **Zero API calls** - Tout tourne sur votre machine
- **Zero données envoyées** - Vos infras restent confidentielles
- **Zero coût récurrent** - Pas d'abonnement OpenAI/Claude

### 🎯 Conçu pour DevOps
- Commandes naturelles en **français**
- **Human-in-the-Loop** - Confirmation avant chaque action
- **Read-First** - Vérifie l'état avant d'agir

### 💡 Pourquoi pas juste des scripts?

| Scripts Bash | Lyra |
|--------------|------|
| "C'était quoi le nom exact de cette VM?" | "liste mes VMs" |
| `virsh start preprod-09` | "démarre preprod" |
| 3 commandes pour clone + start + check | "clone preprod vers sandbox" |

### 🆚 Pourquoi pas ChatGPT/Claude API?

| API Cloud | Lyra |
|-----------|------|
| $20-100/mois | **0€** |
| Données sur serveurs tiers | **100% local** |
| Latence réseau | **Instantané** |
| Dépendant d'internet | **Fonctionne offline** |

---

## ✨ Features

### 🗣️ Commandes Vocales
- Parlez en français, Lyra comprend et exécute
- STT local (Whisper) + TTS (Piper)
- Fonctionne 100% offline

### 🖥️ Gestion VMs KVM

| Commande | Action |
|----------|--------|
| "liste mes VMs" | 📋 Liste toutes les VMs |
| "démarre preprod" | 🟢 Start VM |
| "arrête sandbox" | 🔴 Stop VM |
| "clone preprod vers test" | 📋 Clone complet |
| "fais un snapshot de preprod" | 📸 Snapshot |
| "supprime sandbox" | 🗑️ Destroy VM |

### 💾 Gestion Backups

| Commande | Action |
|----------|--------|
| "status des backups" | 📊 Dashboard complet |
| "liste les backups" | 📋 Liste par type |
| "crée un backup timeshift" | 💾 Nouveau backup |

### 🔒 Sécurité Intégrée
- **Human-in-the-Loop** : Confirmation avant chaque action
- **Read-First** : Vérifie l'état avant d'agir
- Actions destructives signalées en **rouge**
- Todo List pour actions multiples

---

## 🚀 Installation

### Prérequis
- Linux (Fedora 39+, Ubuntu 22.04+)
- Python 3.10+
- Node.js 18+
- [Ollama](https://ollama.ai) installé
- GPU NVIDIA avec 12+ Go VRAM (recommandé)
- libvirt/KVM configuré

### Installation rapide

```bash
git clone https://github.com/USER/lyra.git
cd lyra
./install.sh
```

<details>
<summary>📋 Installation manuelle</summary>

```bash
# 1. Cloner
git clone https://github.com/USER/lyra.git
cd lyra

# 2. Environnement Python
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. MCP Server
cd mcp-server && npm install && npm run build && cd ..

# 4. Modèles
./scripts/download-models.sh
ollama pull qwen2.5-coder:14b

# 5. Configuration
cp config.yaml.example config.yaml
cp .env.example .env
# Éditer config.yaml selon votre setup
```

</details>

---

## 📖 Usage

### Mode Texte
```bash
source .venv/bin/activate
./run.sh
```

### Mode Vocal
```bash
./run.sh --vocal
```

### Exemples de commandes
```
Toi: liste mes VMs
Toi: démarre preprod-09
Toi: clone preprod-09 vers sandbox-test
Toi: status des backups
Toi: help
Toi: quit
```

---

## 📸 Screenshots

<table>
  <tr>
    <td><img src="docs/screenshot-text.png" alt="Mode texte" width="400"></td>
    <td><img src="docs/screenshot-vocal.png" alt="Mode vocal" width="400"></td>
  </tr>
  <tr>
    <td align="center"><b>Mode Texte</b></td>
    <td align="center"><b>Mode Vocal</b></td>
  </tr>
</table>

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         LYRA                                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [User] ──► [Whisper STT] ──► [Ollama/Qwen] ──► [Tool Call]│
│    │              │                                  │      │
│    │ (vocal)      │                                  ▼      │
│    ▼              │                    ┌──────────────────┐ │
│  [Micro]          │                    │ Human-in-Loop    │ │
│                   │                    │  Confirmation    │ │
│                   │                    └────────┬─────────┘ │
│                   │                             │           │
│                   │                             ▼           │
│                   │                    [MCP Server]         │
│                   │                             │           │
│                   │               ┌─────────────┼─────────┐ │
│                   │               ▼             ▼         ▼ │
│                   │          [VM Tools]  [Backup Tools]     │
│                   │               │             │           │
│                   │               ▼             ▼           │
│                   │          [libvirt]   [Timeshift/Borg]   │
│                   │                                         │
│  [Piper TTS] ◄────┴──── [LLM Response Summary]             │
│       │                                                     │
│       ▼                                                     │
│  [Speaker]                                                  │
│                                                             │
│              ════════ 100% Local ════════                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Stack Technique

| Composant | Technologie | Rôle |
|-----------|-------------|------|
| 🧠 **LLM** | Qwen 2.5 Coder 14B | Cerveau, génération tool calls |
| 🎤 **STT** | faster-whisper | Reconnaissance vocale (CUDA) |
| 🔊 **TTS** | Piper | Synthèse vocale française |
| 🔌 **MCP** | fedora-agents | 17 tools VM/Backup |
| ⚡ **Async** | n8n + subprocess | Opérations longues |

---

## ⚙️ Configuration

### config.yaml
```yaml
llm:
  model: qwen2.5-coder:14b  # ou qwen3:8b pour moins de VRAM

audio:
  silence_threshold: 0.005  # Ajuster selon micro
  silence_duration: 1.0     # Secondes avant fin d'écoute
```

### Scripts externes (optionnel)
Pour les opérations async, configurer le chemin des scripts :
```bash
export SCRIPTS_BASE_PATH=~/.local/share/lyra/scripts
```

---

## 🤝 Contributing

Les contributions sont les bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md).

---

## 📝 License

[MIT](LICENSE) © amineutron

---

<div align="center">

Made with ❤️ for DevOps who like to talk to their servers

**[⬆ Back to top](#-lyra)**

</div>
READMEEOF
```

### 3. Mettre à jour les liens

Remplacer `USER` par ton username GitHub :
```bash
sed -i 's|github.com/USER/lyra|github.com/TON_USERNAME/lyra|g' ~/dev/lyra/README.md
```

### 4. Vérifier les images référencées

```bash
# Liste des images dans le README
grep -oE 'docs/[^)"]+' ~/dev/lyra/README.md | sort -u

# Vérifier qu'elles existent
for img in $(grep -oE 'docs/[^)"]+' ~/dev/lyra/README.md | sort -u); do
    [ -f ~/dev/lyra/$img ] && echo "✓ $img" || echo "✗ $img MANQUANT"
done
```

## Tests de Validation

```bash
# Test 1: README existe
[ -f ~/dev/lyra/README.md ] && echo "✓ README OK" || echo "✗ ERREUR"

# Test 2: Contient les sections clés
grep -q "## 🎬 Demo" ~/dev/lyra/README.md && echo "✓ Demo section" || echo "✗ Demo manquant"
grep -q "## ✨ Features" ~/dev/lyra/README.md && echo "✓ Features section" || echo "✗ Features manquant"
grep -q "## 🚀 Installation" ~/dev/lyra/README.md && echo "✓ Installation section" || echo "✗ Installation manquant"
grep -q "## 📖 Usage" ~/dev/lyra/README.md && echo "✓ Usage section" || echo "✗ Usage manquant"

# Test 3: Badges présents
grep -q "img.shields.io" ~/dev/lyra/README.md && echo "✓ Badges présents" || echo "✗ Badges manquants"

# Test 4: Pas de chemins hardcodés
grep -q "/home/amineutron" ~/dev/lyra/README.md && echo "✗ CHEMIN HARDCODÉ!" || echo "✓ Pas de chemin hardcodé"

# Test 5: Architecture ASCII présente
grep -q "100% Local" ~/dev/lyra/README.md && echo "✓ Architecture présente" || echo "✗ Architecture manquante"
```

## Checklist
- [ ] README.md réécrit
- [ ] Header centré avec emoji et badges
- [ ] Section "Why Lyra?" présente
- [ ] Demo GIF/asciinema référencé
- [ ] Screenshots référencés
- [ ] Installation rapide + détaillée
- [ ] Architecture ASCII
- [ ] Stack technique
- [ ] Pas de chemin /home/amineutron
- [ ] Username GitHub mis à jour
- [ ] Liens vers LICENSE et CONTRIBUTING
