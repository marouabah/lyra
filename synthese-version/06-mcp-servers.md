# MCP Servers - Notes de Synthèse

## Vue d'Ensemble

**80 outils MCP** répartis sur **5 serveurs** :

| Serveur | Outils | Description | Localisation |
|---------|--------|-------------|--------------|
| **FEDORA** | 17 | VM KVM + Backups | fedora-setup/scripts/agents/mcp-server |
| **HUE** | 24 | Lumières Philips Hue | dev/hue-mcp |
| **TV** | 14 | TV Philips 55OLED705/12 | lyra/mcp-servers/pylips-mcp |
| **CATT** | 15 | Cast YouTube/Video | lyra/mcp-servers/catt-mcp |
| **DENON** | 10 | Home Cinema Denon AVR-X1700H | lyra/mcp-servers/denon-mcp |

**Total**: 80 outils

---

## FEDORA (17 outils)

**Serveur**: Node.js
**Config**: `config.yaml` → mcp.servers.fedora

### VM Controller (10 outils)

```bash
vm_start(vm_name)                 # Démarre VM
vm_stop(vm_name, force=false)     # Arrête VM
vm_destroy(vm_name)               # Supprime VM (DANGEREUX)
vm_status(vm_name?)               # Statut VM(s)
vm_clone(source_vm, new_vm_name, start=true)  # Clone VM
vm_clone_system(...)              # Clone système complet (10-30 min)
vm_exec(vm_name, command)         # Exécute commande SSH
vm_copy(vm_name, source, dest)    # Copie fichiers via SCP
vm_snapshot(vm_name, action, snapshot_name?, description?)  # Snapshots
vm_verify(vm_name)                # Vérifie intégrité VM
```

### Backup Manager (7 outils)

```bash
backup_create(vm_name, backup_name?)     # Crée backup
backup_list(vm_name?)                     # Liste backups
backup_restore(backup_name, vm_name?)    # Restaure backup (DANGEREUX)
backup_verify(backup_name)               # Vérifie intégrité
backup_clean(older_than_days?)           # Nettoie vieux backups (DANGEREUX)
backup_status(vm_name?)                  # Statut backups
```

### vm_snapshot Actions

**4 actions** possibles:

- `list`: Liste snapshots d'une VM
- `create`: Crée nouveau snapshot
- `revert`: Restaure snapshot (DANGEREUX)
- `delete`: Supprime snapshot

**Workflow snapshot restore** (Phase 4+):
- Détection automatique: `vm_snapshot` + action "revert"
- 4-6 points de validation selon état VM
- Snapshot de sécurité recommandé avant restauration
- Gestion VM running: arrêt + redémarrage optionnel
- Notifications Discord

### Configuration

```yaml
fedora:
  enabled: true
  command: node
  args:
    - /home/amineutron/dev/fedora-setup/scripts/agents/mcp-server/dist/index.js
  timeout: 120
```

### Scripts Backend

**Localisation**: `/home/amineutron/dev/fedora-setup/scripts/`

```
kvm/
  ├── kvm-start.sh
  ├── kvm-stop.sh
  ├── kvm-clone.sh
  ├── kvm-status.sh
  └── ...

agents/
  ├── vm-controller/
  │   ├── vm-start.sh
  │   ├── vm-exec.sh
  │   └── ...
  ├── backup-manager/
  │   ├── backup-create.sh
  │   ├── backup-restore.sh
  │   └── ...
  └── mcp-server/
      └── dist/index.js
```

### Permissions sudoers

**Fichier**: `/etc/sudoers.d/lyra`

```bash
amineutron ALL=(ALL) NOPASSWD: /home/amineutron/dev/fedora-setup/scripts/kvm/*.sh
amineutron ALL=(ALL) NOPASSWD: /home/amineutron/dev/fedora-setup/scripts/agents/**/*.sh
amineutron ALL=(ALL) NOPASSWD: /usr/bin/virsh
amineutron ALL=(ALL) NOPASSWD: /usr/bin/virt-clone
amineutron ALL=(ALL) NOPASSWD: /usr/bin/qemu-img
```

---

## HUE (24 outils)

**Serveur**: Python 3 + phue
**Config**: `config.yaml` → mcp.servers.hue

### Configuration

```yaml
hue:
  enabled: true
  command: python3
  args: [/home/amineutron/dev/hue-mcp/hue_server.py]
  env:
    HUE_BRIDGE_IP: "192.168.1.51"
  timeout: 10
  keep_alive: true

# Credentials
hue:
  bridge_ip: "192.168.1.51"
  username: "***REMOVED***"
```

### Outils Lumières (8)

```python
turn_on_light(light_id)           # Allume lumière
turn_off_light(light_id)          # Éteint lumière
set_brightness(light_id, brightness)  # Luminosité (0-254)
set_color_rgb(light_id, r, g, b)  # Couleur RGB
set_color_hex(light_id, hex)      # Couleur hex (#FF0000)
set_color_temp(light_id, temp)    # Température (153-500 mireds)
get_light(light_id)               # Info lumière
find_light_by_name(name)          # Cherche par nom
```

### Outils Groupes (8)

```python
turn_on_group(group_id=81)        # Allume groupe (défaut: Chambre)
turn_off_group(group_id=81)       # Éteint groupe
set_group_brightness(group_id=81, brightness)
set_group_color_rgb(group_id=81, r, g, b)
set_group_color_hex(group_id=81, hex)
set_group_color_temp(group_id=81, temp)
get_group(group_id)
find_group_by_name(name)
```

### Outils Scènes (4)

```python
activate_scene_by_name(scene_name)  # Active scène par nom
activate_scene(scene_id, group_id)
get_scene(scene_id)
find_scene_by_name(name)
```

### Outils Listing (4)

```python
get_all_lights()        # Liste toutes lumières
get_all_groups()        # Liste tous groupes
get_all_scenes()        # Liste toutes scènes
get_bridge_info()       # Info bridge
```

### Device

**Bridge Philips Hue**: 192.168.1.51
**Lumières**: 5 (Chambre à coucher = group 81)

---

## TV (14 outils)

**Serveur**: Python 3 + pylips
**Config**: `config.yaml` → mcp.servers.tv

### Configuration

```yaml
tv:
  enabled: true
  command: python
  args: [/home/amineutron/dev/lyra/mcp-servers/pylips-mcp/server.py]
  timeout: 10
  keep_alive: true

# Credentials
tv:
  host: "192.168.1.50"
  user: "***REMOVED***"
  pass: "***REMOVED***"
```

### Outils Power (2)

```python
power_on()          # Allume TV (Wake-on-LAN)
power_off()         # Éteint TV (standby)
```

### Outils Volume (5)

```python
volume_up()         # Monte volume (+5)
volume_down()       # Baisse volume (-5)
volume_set(level)   # Volume absolu (0-60)
mute()              # Mute/unmute toggle
get_volume()        # Volume actuel
```

**IMPORTANT**: Redirection automatique vers Denon si connecté en HDMI ARC.

### Outils Ambilight (3)

```python
ambilight_on()                    # Active Ambilight
ambilight_off()                   # Désactive Ambilight
ambilight_mode(mode="expert")     # Mode Ambilight
```

### Outils App (2)

```python
launch_app(app_name)              # Lance app
youtube_video(video_id)           # YouTube via ADB (Premium)
```

**Apps disponibles**: Netflix, YouTube, Prime Video, Disney+, Spotify...

### Outils Divers (2)

```python
list_apps()         # Liste apps disponibles
get_status()        # Statut TV
```

### Device

**Modèle**: Philips 55OLED705/12
**IP**: 192.168.1.50
**API**: JointSpace v6 + ADB (YouTube)

### YouTube via ADB

**Méthode** (pas de pubs, compte Premium):

```bash
adb connect 192.168.1.50:5555
adb shell am start -a android.intent.action.VIEW \
  -d "https://www.youtube.com/watch?v={video_id}" \
  com.google.android.youtube.tv
```

**Fallback**: catt (cast via Chromecast).

---

## CATT (15 outils)

**Serveur**: Python 3 + catt + yt-dlp
**Config**: `config.yaml` → mcp.servers.catt

### Configuration

```yaml
catt:
  enabled: true
  command: python3
  args: [/home/amineutron/dev/lyra/mcp-servers/catt-mcp/server.py]
  timeout: 60
  keep_alive: true

# Device
catt:
  device: "55OLED705/12"
```

### Outils Cast (9)

```python
cast_browser()                # Cast onglet actif Firefox
cast_youtube(url)             # Cast URL YouTube
cast_url(url)                 # Cast n'importe quelle URL
cast_stop()                   # Arrête cast
cast_pause()                  # Pause
cast_resume()                 # Reprend
cast_volume(level)            # Volume (0-100)
cast_seek(seconds)            # Avance/recule (négatif = reculer)
cast_status()                 # Statut cast en cours
```

### Outils Scan (1)

```python
cast_scan()         # Liste devices Chromecast/DLNA disponibles
```

### Outils Playlist (5)

```python
cast_add(url)               # Ajoute à playlist
cast_remove(index)          # Retire de playlist
cast_clear()                # Vide playlist
cast_save(name)             # Sauvegarde playlist
cast_restore(name)          # Restaure playlist
```

### Exemples

```bash
"caste cette video YouTube"
"caste https://youtu.be/xxx sur la TV"
"arrete le cast"
"avance de 30 secondes"
"recule de 10 secondes"
```

---

## DENON (10 outils)

**Serveur**: Python 3 + telnetlib
**Config**: `config.yaml` → mcp.servers.denon

### Configuration

```yaml
denon:
  enabled: true
  command: python3
  args: [/home/amineutron/dev/lyra/mcp-servers/denon-mcp/server.py]
  timeout: 10
  keep_alive: true

# Device
denon:
  host: "192.168.1.52"
  port: 23
  mac: "000678B4E8C8"
```

### Outils Volume (3)

```python
volume_set(level)       # Volume absolu (0-98, 80 = 0dB)
volume_up()             # Monte volume
volume_down()           # Baisse volume
```

**Échelle**: 0 = -80dB, 80 = 0dB (référence), 98 = +18dB

**Recommandé**:
- Écoute normale: 30-50
- Home cinema: 50-70
- Maximum: 80 (0dB)

### Outils Mute (3)

```python
mute_on()               # Active mute
mute_off()              # Désactive mute
mute_toggle()           # Toggle mute
```

### Outils Power (2)

```python
power_on()              # Allume Denon
power_off()             # Éteint Denon (standby)
```

### Outils Input (1)

```python
set_input(source)       # Change source
```

**Sources**: BD, TV, GAME, SAT/CBL, DVD, MPLAY
**Aliases**: bluray, blu-ray, cable, sat, media, mediaplayer

### Outils Status (1)

```python
get_status()            # Statut (volume, power, input)
```

### Device

**Modèle**: Denon AVR-X1700H DAB
**IP**: 192.168.1.52
**MAC**: 000678B4E8C8
**Connexion**: HDMI ARC/eARC vers TV

### Redirection HDMI ARC

**IMPORTANT**: Quand Denon connecté en HDMI ARC:

- Volume TV désactivé (sortie audio via HDMI)
- Commandes `tv.volume_*` **automatiquement redirigées** vers `denon.*`
- Utiliser indifféremment `tv.volume_set 44` ou `denon.volume_set 44`

**Détection automatique** dans `pylips-mcp/server.py`:

```python
if denon_config.get("enabled"):
    # Rediriger volume TV vers Denon
    tv.volume_set → denon.volume_set
    tv.volume_up → denon.volume_up
    tv.volume_down → denon.volume_down
    tv.mute → denon.mute_toggle
```

---

## Modes de Fonctionnement

### Mode Default

**Confirmation obligatoire** pour TOUTES les actions (VM, backup, domotique).

```yaml
modes:
  default:
    confirmation: true
    read_first: true
    tts_response: true
    verbose: true
```

### Mode Performance

**Skip confirmation** pour domotique, **JAMAIS** pour VM/backup dangereux.

```yaml
modes:
  performance:
    confirmation: false        # Skip pour domotique
    read_first: false
    tts_response: false
    verbose: false
    preload_connections: true
    timeout: 5
```

**Outils performance** (skip confirmation):

```python
PERFORMANCE_TOOLS = [
    "tv.power_on", "tv.volume_up", "tv.ambilight_on",
    "hue.turn_on_light", "hue.set_brightness",
    "cast_youtube", "cast_stop",
    # ... ~50 outils domotique
]
```

**Outils dangereux** (TOUJOURS confirmation):

```python
DANGEROUS_TOOLS = [
    "vm_destroy", "vm_stop", "backup_restore",
    "backup_clean", "vm_clone_system"
]
```

---

## Sécurité

### Règle Double Clé

**Avant `vm_destroy`**: Vérifier snapshot récent (<5 min).

```yaml
security:
  require_snapshot_before_delete: true
  snapshot_max_age_minutes: 5
```

### Read-First

**Avant action**: Lire état actuel pour afficher contexte.

```yaml
security:
  read_first_enabled: true
```

### Actions Destructives

**Confirmation explicite** obligatoire:

```yaml
security:
  destructive_tools:
    - vm_destroy
    - vm_delete
    - backup_restore
    - backup_clean
```

---

## Opérations Async

**Outils longues durées** exécutés en arrière-plan:

| Outil | Durée estimée | Description |
|-------|---------------|-------------|
| `vm_clone` | 1-2 min | Clonage VM |
| `vm_clone_system` | 10-30 min | Clone système complet |
| `backup_create` | 2-5 min | Création backup |
| `backup_restore` | 2-5 min | Restauration backup |
| `vm_snapshot` (revert) | 1-2 min | Restauration snapshot |

### Workflow Async

1. User demande action longue
2. LYRA génère message friendly ("Je lance en arrière-plan, ~1-2 min...")
3. BackgroundTaskManager lance subprocess
4. User continue à interagir
5. Notification Discord à la fin ("✅ Clone terminé!")

### n8n Webhooks (Optionnel)

**Alternative** à subprocess pour opérations async:

```yaml
n8n:
  base_url: http://localhost:5678
  webhooks:
    clone-vm: /webhook/lyra-clone-vm
    backup-create: /webhook/lyra-backup-create
    backup-restore: /webhook/lyra-backup-restore
  enabled: true
```

**Si n8n échoue** → fallback subprocess automatique.

---

## Récapitulatif

| Serveur | Outils | Type | Config clé |
|---------|--------|------|------------|
| **FEDORA** | 17 | VM + Backup | timeout: 120s |
| **HUE** | 24 | Domotique | keep_alive: true |
| **TV** | 14 | Domotique | Redirection HDMI ARC |
| **CATT** | 15 | Cast Video | timeout: 60s |
| **DENON** | 10 | Home Cinema | HDMI ARC auto-detect |

**Total**: 80 outils MCP
