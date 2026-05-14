# Changelog - Lyra

## [Phase 4] - 2026-01-23

### Operations Async via n8n + Fallback Subprocess

**Ajouts:**
- Module `modules/n8n.py` : Client n8n + executeur async fallback
- 3 workflows n8n crees avec noeud `code` (JS)
- Detection automatique des operations longues (vm_clone, backup_create, backup_restore)
- **Fallback subprocess** : Si n8n non disponible, execute en arriere-plan via threading
- Notification dans le terminal quand operation terminee (mode fallback)

**Workflows n8n:**
| Workflow | Webhook | Description |
|----------|---------|-------------|
| Lyra - Clone VM v2 | `/webhook/lyra-clone-vm-v2` | Clone VM via kvm-clone.sh |
| Lyra - Backup Create | `/webhook/lyra-backup-create` | Cree backup timeshift/borg |
| Lyra - Backup Restore | `/webhook/lyra-backup-restore` | Restaure backup |

**Note:** Les workflows utilisent le noeud `n8n-nodes-base.code` au lieu de `executeCommand`
(ce dernier n'etait pas reconnu par l'API).

**Fichiers modifies:**
- `main.py` : Integration n8n avec fallback subprocess
- `modules/n8n.py` : Client n8n + AsyncExecutor pour fallback
- `config.yaml` : n8n.enabled = true, webhook path mis a jour
- `prompts/system_prompt.txt` : Section operations async

**Mode fallback (subprocess):**
Quand n8n n'est pas disponible ou les webhooks ne sont pas actifs:
1. Lyra detecte l'echec du webhook
2. Lance la commande en arriere-plan via subprocess.Popen
3. Notifie dans le terminal quand c'est termine

**Configuration requise:**
```yaml
n8n:
  enabled: true
  base_url: http://localhost:5678
  api_key: <votre-cle-api>  # Optionnel
  webhooks:
    clone-vm: /webhook/lyra-clone-vm-v2
    backup-create: /webhook/lyra-backup-create
    backup-restore: /webhook/lyra-backup-restore
```

**Pour activer les webhooks n8n:**
1. Aller sur http://localhost:5678
2. Ouvrir chaque workflow Lyra
3. Cliquer sur le toggle "Active" en haut a droite
4. Les webhooks seront alors operationnels

---

## [Phase 3] - 2026-01-23

### Actions + Securite

**Ajouts:**
- Principe **Read-First** : verification automatique de l'etat VM avant toute action
- System prompt externe (`prompts/system_prompt.txt`) au lieu de hardcode
- Confirmation vocale avec mots-cles ("oui"/"non"/"oui je confirme")
- Affichage de l'etat VM dans la confirmation (status, IP)
- Description vocale naturelle des actions proposees

**Regles de securite:**
- `READ_FIRST_TOOLS` : vm_start, vm_stop, vm_destroy, vm_snapshot, vm_clone
- `READ_ONLY_TOOLS` : vm_status, backup_status, backup_list, backup_verify
- Actions dangereuses : confirmation explicite "oui je confirme" en vocal

**Fichiers modifies:**
- `main.py` : Chargement prompt externe, Read-First, descriptions vocales
- `modules/ui.py` : Confirmation vocale, affichage etat VM
- `prompts/system_prompt.txt` : Regles de securite detaillees

**Confirmation vocale:**
- Option `[v]` pour passer en mode vocal
- Mots-cles acceptes : oui, yes, ok, d'accord, confirme, vas-y
- Mots-cles annulation : non, no, annule, stop, arrete
- Actions destructives : exigent "oui je confirme"

---

## [Phase 2] - 2026-01-22

### Mode Vocal (STT/TTS)

**Ajouts:**
- Mode `--vocal` pour interaction vocale complete
- Module `modules/audio.py` : STT, TTS, AudioRecorder, VoiceInterface
- Script `run.sh` : Lancement avec configuration CUDA automatique
- Alias bash `lyra` et `lyra --vocal`
- Bip sonore avant l'ecoute
- Indicateur visuel de niveau audio en temps reel
- Detection de silence pour fin d'enregistrement automatique

**Stack vocale:**
- STT : faster-whisper (modele base, CUDA float16)
- TTS : Piper (voix fr_FR-upmc-medium)
- Audio : sounddevice avec resampling 48kHz

**Configuration (`config.yaml`):**
```yaml
audio:
  sample_rate: 48000      # Compatible PipeWire/ALSA
  silence_threshold: 0.005
  silence_duration: 1.0
stt:
  model: base
  device: cuda
  compute_type: float16
tts:
  model: fr_FR-upmc-medium
```

**Dependances ajoutees:**
- faster-whisper
- piper-tts
- sounddevice
- nvidia-cublas-cu12
- nvidia-cudnn-cu12

**Fixes techniques:**
- Resampling audio : 48kHz (PipeWire) <-> 16kHz (Whisper) <-> 22050Hz (Piper)
- `suppress_stderr()` : Masque les warnings cffi de sounddevice
- Configuration CUDA via `LD_LIBRARY_PATH` dans run.sh

**Issue connue:**
- Elgato Wave 3 non fonctionnel (necessite Wave Link sur Windows/Mac)
- Workaround : Utiliser G522 LIGHTSPEED comme micro par defaut

---

## [Phase 1] - 2024

### Wrapper Python + MCP (mode texte)

**Fonctionnalites:**
- Client Ollama avec parsing JSON des tool calls
- Client MCP pour fedora-agents
- Human-in-the-Loop : confirmation avant execution
- Interface CLI en francais
- Raccourcis clavier (Ctrl+L, double Ctrl+C)

**Outils MCP disponibles:**
- VM : vm_status, vm_start, vm_stop, vm_snapshot, vm_exec, vm_clone
- Backup : backup_status, backup_list, backup_create, backup_verify
