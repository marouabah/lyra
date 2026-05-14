# Phase 5.4 - Integration Multi-MCP Lyra

## Objectif

Integrer tous les MCP dans Lyra avec routage intelligent et mode performance.

## Architecture MCPManager

Le `MCPManager` gere plusieurs serveurs MCP avec prefixage automatique :

```
fedora.vm_start    -> fedora-agents MCP
tv.power_on        -> pylips-mcp
hue.turn_on_light  -> hue-mcp
ha.scene_turn_on   -> home-assistant MCP (optionnel)
```

## Fichiers modifies

### 1. modules/mcp.py

Ajout de la classe `MCPManager` pour :
- Gerer plusieurs clients MCP
- Prefixer les noms d'outils
- Router les appels vers le bon serveur
- Maintenir les connexions (keep_alive)

### 2. config.yaml

Nouvelle structure pour les serveurs MCP :

```yaml
mcp:
  servers:
    fedora:
      enabled: true
      command: node
      args: ["/path/to/mcp-server/dist/index.js"]
      timeout: 120

    tv:
      enabled: true
      command: python
      args: ["/path/to/pylips-mcp/server.py"]
      timeout: 10
      keep_alive: true

    hue:
      enabled: true
      command: python
      args: ["-m", "hue_mcp"]
      timeout: 10
      keep_alive: true
```

### 3. main.py

Ajouts :
- `PERFORMANCE_TOOLS` : Outils executables sans confirmation
- `ALWAYS_CONFIRM_TOOLS` : Outils toujours avec confirmation
- Mode switching (`mode performance`, `mode default`)
- Argument `--performance` / `-p`

### 4. modules/ui.py

Ajout de `beep_short()` pour feedback minimal en mode performance.

### 5. prompts/system_prompt.txt

Ajout des outils TV et Hue avec exemples.

### 6. run.sh

Ajout de l'argument `--performance` / `-p`.

## Mode Performance

### Activation

```bash
# Via argument
./run.sh --performance
./run.sh -p

# Via commande interne
Toi: mode performance
[+] Mode performance active

Toi: mode default
[+] Mode default active
```

### Comportement

| Aspect | Mode default | Mode performance |
|--------|--------------|------------------|
| Confirmation | "Executer ? [O/n]" | Execution directe |
| Read-first | Verifie etat avant | Non |
| Reponse | "La TV est allumee" | "OK" ou bip |
| TTS | Synthese vocale | Silence |
| Latence | ~2-3s | <200ms |

### Outils autorises en mode performance

```python
PERFORMANCE_TOOLS = {
    # TV
    "tv.power_on", "tv.power_off",
    "tv.volume_up", "tv.volume_down", "tv.mute",
    "tv.ambilight_on", "tv.ambilight_off", "tv.ambilight_mode",
    # Lumieres
    "hue.turn_on_light", "hue.turn_off_light",
    "hue.set_brightness", "hue.set_color_rgb",
    "hue.set_scene",
}
```

### Securite

Les outils dangereux IGNORENT le mode performance :

```python
ALWAYS_CONFIRM_TOOLS = {
    "fedora.vm_destroy",
    "fedora.vm_stop",
    "fedora.backup_restore",
    "fedora.backup_clean",
}
```

## Commandes internes ajoutees

| Commande | Description |
|----------|-------------|
| `mode performance` | Active le mode performance |
| `mode default` | Retour au mode normal |
| `mode` | Affiche le mode actuel |

## Validation End-to-End

1. **pylips-mcp seul** :
   ```bash
   python mcp-servers/pylips-mcp/server.py
   # Tester avec Claude Code
   ```

2. **hue-mcp seul** :
   ```bash
   python -m hue_mcp
   # Tester avec Claude Code
   ```

3. **Lyra texte** :
   ```bash
   ./run.sh
   # "Allume la TV" -> TV s'allume (avec confirmation)
   ```

4. **Lyra vocal** :
   ```bash
   ./run.sh --vocal
   # "Eteins les lumieres" -> Lumieres off
   ```

5. **Mixte** :
   ```
   "Demarre preprod et allume la TV"
   # Les deux fonctionnent
   ```

6. **Mode performance** :
   ```bash
   ./run.sh --performance
   # "Lumieres rouge" -> Execution instantanee
   ```

7. **Switch mode** :
   ```
   "mode performance" -> "lumieres bleu" -> pas de confirmation
   ```

8. **Securite perf** :
   ```
   "mode performance" -> "supprime sandbox" -> Confirmation quand meme
   ```

## Troubleshooting

### Outil non trouve
- Verifier le prefixe (`tv.`, `hue.`, `fedora.`)
- Verifier que le serveur est enabled dans config.yaml
- Verifier les logs de demarrage

### Timeout MCP
- Augmenter le timeout dans config.yaml
- Verifier que le serveur MCP est accessible
- Tester le serveur en standalone

### Mode performance ne fonctionne pas
- Verifier que l'outil est dans PERFORMANCE_TOOLS
- Verifier que active_mode est bien "performance"
- Les outils fedora.* ne sont pas en mode performance
