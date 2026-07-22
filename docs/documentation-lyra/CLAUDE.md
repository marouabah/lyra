# CLAUDE.md

## Project Overview

Lyra is a **voice-controlled DevOps assistant** providing local voice interface (French) for managing KVM virtual machines and backup systems.

## Architecture V2 (RAG) - Par defaut

```
[User Input] ──► [IntentClassifier] ──► demande/info/discussion
     │ (vocal)         │
     ▼                 ▼
[Whisper STT]    ┌─────┴─────┐
                 │           │
            [demande]   [info/discussion]
                 │           │
                 ▼           ▼
            [RAG Hybrid] ──► [LYRA]
            (Semantic+BM25)    │
                 │             ▼
                 ▼         [Reponse]
            [TOON Encode]
            (Specs compact)
                 │
                 ▼
            [EPHAISTOS]
            (Analyse specs)
                 │
                 ▼
            [HESTIA] ──► [MCP] ──► [LYRA] ──► [Piper TTS]
            (Execution)
```

### Composants V2

| Composant | Role | Modele |
|-----------|------|--------|
| **IntentClassifier** | Classification intention (demande/info/discussion) | LYRA (Llama 3B) |
| **RAG Hybrid** | Recherche specs MCP (semantic + keyword BM25) | all-MiniLM-L6-v2 |
| **TOON** | Encoding compact des specs avant EPHAISTOS (~40% tokens) | Python natif |
| **EPHAISTOS** | Analyse specs, extraction arguments | Qwen 2.5 Coder 7B |
| **LYRA** | Dialogue, personnalite, formatage | Llama 3.2 3B |
| **HESTIA** | Execution MCP, gestion erreurs | - |

### Classification des intentions

| Intent | Description | Exemple |
|--------|-------------|---------|
| **demande** | Action MCP a executer | "demarre preprod-01", "quels sont mes vm" |
| **info** | Question de connaissance | "c'est quoi vm_clone", "comment ca marche" |
| **discussion** | Conversation generale | "salut", "merci", "ok" |

---

## Architecture V1 (Legacy)

```
[User Input] ──► [Ollama/Qwen] ──► [Tool Call JSON]
     │ (vocal)                           │
     ▼                                   ▼
[Whisper STT]                   [Human-in-Loop Confirmation]
                                         │
                    ┌────────────────────┼────────────────┐
                    ▼                    ▼                ▼
              [Sync MCP]          [Async n8n]      [Fallback subprocess]
                    └────────────────────┴────────────────┘
                                         │
                                         ▼
                                [Resultat ──► LLM Resume ──► Piper TTS]
```

---

## Stack Technique

| Composant | Technologie |
|-----------|-------------|
| **LLM Backend** | Qwen 2.5 Coder 7B via Ollama (EPHAISTOS) |
| **LLM Frontend** | Llama 3.2 3B via Ollama (LYRA) |
| **RAG** | ChromaDB + BM25 (rank-bm25) |
| **TOON** | Encodeur token-compact pour specs MCP (~40% economie) |
| **Embeddings** | all-MiniLM-L6-v2 |
| **MCP** | fedora-agents (VM/Backup), pylips-mcp (TV), hue-mcp (Lumieres) |
| **Async** | n8n webhooks + fallback subprocess |
| **STT/TTS** | faster-whisper (CUDA) + Piper (fr_FR-upmc-medium) |

### VRAM estimee (~10.5 GB)

- EPHAISTOS (Qwen 7B): ~5 GB
- LYRA (Llama 3B): ~2.5 GB
- Embeddings: ~0.5 GB
- Whisper (mode vocal): ~1.5 GB

## Build Commands

```bash
./run.sh                    # Mode RAG V2 (defaut)
./run.sh --vocal            # Mode vocal STT/TTS
./run.sh -p                 # Mode performance (domotique sans confirmation)
./run.sh --vocal -p         # Combinaison
./run.sh --legacy           # Mode V1 classique (Qwen 14B)
```

## Project Structure

```
lyra/
├── main.py                 # Orchestrateur V1 (legacy)
├── main_rag.py             # Orchestrateur V2 RAG (defaut)
├── config.yaml             # Configuration centralisee
├── run.sh                  # Script de lancement
├── lyra/                   # Package RAG V2
│   ├── core/
│   │   ├── config.py       # Configuration RAG
│   │   └── pipeline.py     # Pipeline principal
│   ├── models/
│   │   ├── model_manager.py    # Orchestration LLMs
│   │   ├── ephaistos.py        # Backend Qwen 7B
│   │   ├── lyra_voice.py       # Frontend Llama 3B
│   │   └── intent_classifier.py # Classification intentions
│   ├── rag/
│   │   ├── semantic_retriever.py  # ChromaDB embeddings
│   │   ├── keyword_retriever.py   # BM25
│   │   ├── fusion.py              # RRF fusion
│   │   └── session_memory.py      # Contexte multi-tour
│   ├── utils/
│   │   └── toon.py                # Encodeur TOON (compact ~40%)
│   └── hestia/
│       └── executor.py     # Execution MCP
├── modules/                # Modules V1 (compatibilite)
│   ├── llm.py, mcp.py, ui.py, audio.py, n8n.py
├── mcp-servers/
│   ├── pylips-mcp/         # Wrapper MCP TV Philips
│   └── catt-mcp/           # Cast YouTube via catt
├── scenes/ironman/         # Scene Iron Man (Phase 6)
└── prompts/                # System prompts
```

## MCP Tools

**VM Controller**: `vm_start`, `vm_stop`, `vm_destroy`, `vm_status`, `vm_exec`, `vm_copy`, `vm_snapshot`, `vm_clone`, `vm_clone_system`, `vm_verify`

**Backup Manager**: `backup_create`, `backup_list`, `backup_restore`, `backup_verify`, `backup_clean`, `backup_status`

**TV Philips** (Phase 5): `tv.power_on/off`, `tv.volume_up/down/set`, `tv.mute`, `tv.ambilight_*`, `tv.launch_app`, `tv.youtube_video`

**Hue** (Phase 5): `hue.turn_on/off_light`, `hue.set_brightness`, `hue.set_color_rgb`, `hue.set_group_*`, `hue.activate_scene_by_name`

**Cast** (Phase 5.4): `cast_youtube`, `cast_url`, `cast_stop`, `cast_pause`, `cast_resume`, `cast_volume`, `cast_seek`, `cast_status`, `cast_scan`

**Denon** (Phase 5.5): `volume_set`, `volume_up`, `volume_down`, `mute_on`, `mute_off`, `mute_toggle`, `power_on`, `power_off`, `set_input`, `get_status`

## Securite

- **Confirmation obligatoire** pour toutes les actions MCP
- **Actions dangereuses** (rouge): `vm_destroy`, `vm_stop --force`, `backup_restore`, `backup_clean`
- **Mode performance**: Skip confirmation pour domotique, JAMAIS pour VM/backup dangereux

## Flux Interactif - Liste des Outils MCP

Quand l'utilisateur demande les outils disponibles, Lyra propose un menu interactif:

```
>>> donne moi la liste des mcp stp

J'ai 80 outils disponibles. Quel serveur veux-tu explorer?

  1. **CATT** (15 outils) - Cast video
  2. **DENON** (10 outils) - Home Cinema Denon AVR
  3. **FEDORA** (17 outils) - VM KVM et backups
  4. **HUE** (24 outils) - Lumieres Philips Hue
  5. **TV** (14 outils) - Controle TV Philips
  6. **TOUS** - Afficher tous les outils

>>> 3

**FEDORA** (17 outils):
  - **vm_start**: Demarre une VM KVM...
  - **vm_stop**: Arrete une VM KVM...
  ...
```

---

## Workflow Human-in-the-Loop

### Action simple
```
User: "demarre preprod-09"
    ↓
LLM genere: {"name": "vm_start", "arguments": {"vm_name": "preprod-09"}}
    ↓
Wrapper affiche: "ACTION PROPOSEE: vm_start"
                 "Etat actuel: Arrete"
                 "Executer ? [O/n/d]"
    ↓
User confirme: O
    ↓
Wrapper execute MCP → resultat
    ↓
LLM resume: "La VM preprod-09 est demarree (IP: 192.168.122.146)"
```

### Actions multiples (Todo List)
```
User: "supprime sandbox-01 et sandbox-02"
    ↓
LLM genere: {"name": "vm_destroy", "arguments": {"vm_name": "sandbox-01"}}
            {"name": "vm_destroy", "arguments": {"vm_name": "sandbox-02"}}
    ↓
Wrapper affiche: "[i] Todo list: 2 actions proposees"
                 "  [1] vm_destroy -> sandbox-01"
                 "  [2] vm_destroy -> sandbox-02"
                 "Executer ? [T]out / [1] par 1 / [n]on"
    ↓
User confirme: T (tout) ou 1 (une par une)
    ↓
Wrapper execute sequentiellement
```

## Key Constraints

- **Language**: French (UI, voice, docs)
- **Hardware**: RTX 3080 Ti (12 Go VRAM)
- **VRAM**: ~10.1 GB Qwen + ~0.5 GB Whisper
- **Offline**: 100% local

## Commandes Internes

`help`, `clear`, `clearscreen`, `quit`/`stop`, `mode`, `mode performance`, `mode default`

## Raccourcis

| Raccourci | Action |
|-----------|--------|
| `Ctrl+L` | Efface terminal |
| `Ctrl+C` (2x <1.5s) | Quitte Lyra |

---

## Phases de Developpement

- [x] **Phase 1**: Wrapper Python + MCP
- [x] **Phase 2**: Mode Vocal (STT/TTS)
- [x] **Phase 3**: Read-First + Securite
- [x] **Phase 4**: Operations async + Todo List
- [x] **Phase 5**: Controle Domotique (TV + Hue)
- [ ] **Phase 6**: Scene Iron Man

---

## Phase 4 - Operations Async ✅

Operations longues executees en arriere-plan: `vm_clone` (~60s), `vm_clone_system` (~10-30min), `backup_create/restore` (~2min)

Architecture: n8n webhook → si echec → fallback subprocess avec callback.

### Configuration sudoers

Pour les operations async sans mot de passe (`/etc/sudoers.d/lyra`):
```bash
amineutron ALL=(ALL) NOPASSWD: /home/amineutron/dev/fedora-setup/scripts/kvm/*.sh
amineutron ALL=(ALL) NOPASSWD: /home/amineutron/dev/fedora-setup/scripts/agents/vm-controller/*.sh
amineutron ALL=(ALL) NOPASSWD: /home/amineutron/dev/fedora-setup/scripts/agents/backup-manager/*.sh
amineutron ALL=(ALL) NOPASSWD: /usr/bin/virsh
amineutron ALL=(ALL) NOPASSWD: /usr/bin/virt-clone
amineutron ALL=(ALL) NOPASSWD: /usr/bin/qemu-img
```

### Exemple workflow async
```
User: "clone preprod-09 en test-clone"
    ↓
LLM genere: {"name": "vm_clone", "arguments": {"source_vm": "preprod-09", "new_vm_name": "test-clone"}}
    ↓
Wrapper: Confirmation → Essai n8n webhook → Echec 404
    ↓
Fallback: subprocess.Popen("sudo kvm-clone.sh preprod-09 test-clone --start")
    ↓
Wrapper: "Operation lancee en arriere-plan"
    ↓
(~60s plus tard, callback)
    ↓
Terminal: "[+] [ASYNC] Operation vm_clone terminee avec succes!"
```

---

## Phase 5 - Domotique ✅

### Configuration

```yaml
tv:
  host: "192.168.1.50"       # Philips 55OLED705/12
  user: "***REMOVED***"
  pass: "..."                # 64 chars hex

hue:
  bridge_ip: "192.168.1.51"
  username: "<cle-api-hue>"
```

### Devices

- **TV**: Philips 55OLED705/12 @ 192.168.1.50 (JointSpace API + ADB pour YouTube)
- **Hue**: Bridge @ 192.168.1.51, 5 lumieres (group 81 = Chambre a coucher)
- **Home Assistant**: http://localhost:8123 (Docker, optionnel)

### Mode Performance

Outils domotique executes sans confirmation. Activer via `./run.sh -p` ou `mode performance`.

### YouTube via ADB

`tv.youtube_video` utilise ADB pour lancer YouTube avec compte Premium (pas de pubs). Fallback: catt.

### Cast via catt (Phase 5.4)

MCP server pour caster des videos YouTube et autres contenus vers la TV via Chromecast/DLNA.

**Prerequis**:
- `catt`: `pip install catt`
- `yt-dlp`: `pip install yt-dlp`

**Configuration** (`config.yaml`):
```yaml
catt:
  device: "55OLED705/12"  # Nom du device (voir cast_scan)
```

**Outils disponibles**:
| Outil | Description |
|-------|-------------|
| `cast_browser` | Caste la video de l'onglet actif Firefox |
| `cast_youtube` | Caste une URL YouTube sur la TV |
| `cast_url` | Caste n'importe quelle URL video/audio |
| `cast_stop` | Arrete le cast en cours |
| `cast_pause` | Met en pause |
| `cast_resume` | Reprend la lecture |
| `cast_volume` | Regle le volume (0-100) |
| `cast_seek` | Avance/recule (secondes, negatif = reculer) |
| `cast_status` | Statut du cast en cours |
| `cast_scan` | Liste les devices disponibles |

**Exemples d'utilisation**:
```
"caste la video sur la TV"           # cast_browser - onglet actif Firefox
"caste cette video: https://youtu.be/xxx"
"arrete le cast"
"mets la lecture en pause"
"avance de 30 secondes"
```

---

## Phase 5.5 - Home Cinema Denon ✅

Controle du home cinema Denon AVR-X1700H DAB via protocole telnet.

### Configuration

```yaml
denon:
  host: "192.168.1.52"       # IP du Denon AVR-X1700H DAB
  port: 23                    # Port telnet (default: 23)
  mac: "000678B4E8C8"        # MAC address (ethernet)
```

### Outils disponibles

| Outil | Description |
|-------|-------------|
| `denon.volume_set` | Regle le volume (0-98, 80 = 0dB) |
| `denon.volume_up` | Augmente le volume |
| `denon.volume_down` | Baisse le volume |
| `denon.mute_on` | Active le mute |
| `denon.mute_off` | Desactive le mute |
| `denon.mute_toggle` | Toggle le mute |
| `denon.power_on` | Allume le Denon |
| `denon.power_off` | Eteint le Denon (standby) |
| `denon.set_input` | Change la source (BD, TV, GAME, SAT/CBL, DVD, MPLAY) |
| `denon.get_status` | Statut du Denon (volume, power) |

### Redirection automatique HDMI ARC

**IMPORTANT:** Quand un home cinema est connecte en **HDMI ARC/eARC** a la TV :
- Le volume de la TV est desactive (sortie audio via HDMI)
- Les commandes `tv.volume_*` et `tv.mute` sont **automatiquement redirigees** vers `denon.*`
- Vous pouvez utiliser indifferemment `tv.volume_set 44` ou `denon.volume_set 44`

Le serveur `pylips-mcp` detecte automatiquement si un Denon est configure et redirige les commandes volume/mute vers le Denon.

### Echelle de volume

- **0-98** : Echelle Denon (0 = -80 dB, 80 = 0 dB reference, 98 = +18 dB)
- Pour une ecoute normale : **30-50**
- Pour un home cinema : **50-70**
- Maximum recommande : **80** (0 dB)

### Sources d'entree

- `BD` : Blu-ray / Lecteur BD
- `TV` : Entree TV
- `GAME` : Console de jeu
- `SAT/CBL` : Satellite / Cable
- `DVD` : Lecteur DVD
- `MPLAY` : Media Player

Aliases supportes : `bluray`, `blu-ray`, `cable`, `sat`, `media`, `mediaplayer`

### Exemples d'utilisation

```
"passe le volume a 44"              # denon.volume_set 44 (via tv.volume_set redirige)
"monte le volume"                    # denon.volume_up (via tv.volume_up redirige)
"mets le son en mute"               # denon.mute_on
"change la source en bluray"        # denon.set_input BD
"allume le denon"                   # denon.power_on
```

---

## Phase 6 - Scene Iron Man

Experience immersive ~33s synchronisant TV + Hue sur trigger vocal "je suis iron man".

### Timeline

| Phase | Duree | Description |
|-------|-------|-------------|
| 0-Detection | 2s | Validation devices + sauvegarde rollback |
| 1-Blackout | 3s | Noir total |
| 2-Impact | 3.5s | Flash blanc + bleu + YouTube AC/DC + Ambilight |
| 3-Buildup | 12s | Pulsations rouge/bleu 120 BPM, brightness 0→254 |
| 4-Transition | 7s | Ralentissement + stabilisation bleu @150 |
| 5-TTS | 5.5s | Voix J.A.R.V.I.S. + pulse confirmation |

### Workflow Claude Code

Quand l'utilisateur dit "phase suivante" ou "continue phase 6":
1. Trouver la premiere sous-phase `[ ]` non cochee ci-dessous
2. Lire `prompts/ironman_prompts/XX_phaseY/PROMPT.md`
3. Implementer dans `scenes/ironman/`
4. Cocher `[x]` dans ce fichier

### Sous-phases

- [x] **6.0**: Detection & Validation
- [x] **6.1**: Blackout Dramatique
- [x] **6.2**: Premier Impact
- [x] **6.3**: Pulsations Synchronisees
- [x] **6.4**: Transition & Stabilisation
- [x] **6.5**: TTS J.A.R.V.I.S.
- [x] **6.6**: Orchestrateur
- [ ] **6.7**: Integration Lyra
- [ ] **6.8**: Suite de Tests

### Triggers Vocaux

"je suis iron man", "je suis tony stark", "je suis tony", "mode iron man", "scene iron man"

### Configuration

```yaml
scenes:
  ironman:
    enabled: true
    triggers: ["je suis iron man", "je suis tony stark", "mode iron man"]
    youtube_video_id: "pAgnJDJN4VA"
    tts_phrase: "random"
```

### State Machine

```
IDLE → VALIDATING → BLACKOUT → IMPACT → BUILDUP → TRANSITION → TTS → STABLE
  ↑                                                                     │
  └──────────────────────── ROLLBACK ◄──────────────────────────────────┘
```

### Gestion Erreurs

- Phase 0 echoue → annuler, rester IDLE
- Phase 1-5 echoue → rollback auto
- TV/Hue offline → annuler scene
- YouTube echoue → continuer lights-only

### Structure Fichiers

```
scenes/ironman/
├── orchestrator.py
├── phases/
│   ├── phase0_detection.py
│   ├── phase1_blackout.py
│   ├── phase2_impact.py
│   ├── phase3_buildup.py
│   ├── phase4_transition.py
│   └── phase5_tts.py
└── tests/
```

---

## Bugs Connus et Fixes

| Bug | Fichier | Solution |
|-----|---------|----------|
| backup_status erreur arithmetique | backup-status.sh | Nettoyer variable count |
| LLM ne genere pas JSON | system_prompt.txt | Instructions explicites |
| vm_status 1 seule VM | common.sh | `ssh -n` |
| beep_short callback error | ui.py | `sd.OutputStream.write()` |
| JSON dans markdown | llm.py | Strip ```json blocks |
| Hue group 0 inexistant | mcp.py | Utiliser group 81 |
| Scenes Hue par ID | hue_server.py | `activate_scene_by_name` |
| Volume TV +1 au lieu de +5 | server.py | Lire/modifier volume actuel |
| Ambilight reste blanc | server.py | Ajouter `menuSetting` |
| YouTube deep linking | server.py | ADB au lieu de JointSpace |
| hue-mcp pollue stdout | hue_server.py | `print(..., file=sys.stderr)` |
| Elgato Wave 3 capture nulle | - | Workaround: G522 par defaut |

---

## Development Notes

- MCP server: `/home/amineutron/dev/fedora-setup/scripts/agents/mcp-server/`
- MCP timeout: 120s
- Wrapper parse JSON du content (pas tool_calls natif)
- Double Ctrl+C (< 1.5s) pour quitter
