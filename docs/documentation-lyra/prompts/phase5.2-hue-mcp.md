# Phase 5.2 - Hue MCP Setup

## Objectif

Installer et configurer hue-mcp pour controle direct des lumieres Philips Hue.

## Installation

```bash
cd /home/amineutron/dev
git clone https://github.com/ThomasRohde/hue-mcp.git
cd hue-mcp

# Installation avec uv (recommande)
uv sync

# Ou pip
pip install -e .
```

## Decouverte du Bridge

```bash
# Decouverte automatique
python -m hue_mcp discover

# Ou manuel si IP connue
export HUE_BRIDGE_IP="192.168.1.XXX"
```

## Pairing Bridge

1. Appuyer sur le bouton physique du Bridge Hue
2. Dans les 30 secondes, executer :

```bash
python -m hue_mcp pair
```

3. Sauvegarder le token genere

## Configuration

**Fichier**: `~/.config/hue-mcp/config.json`

```json
{
  "bridge_ip": "192.168.1.XXX",
  "username": "GENERATED_TOKEN"
}
```

Ou dans `/home/amineutron/dev/lyra/config.yaml` :

```yaml
hue:
  bridge_ip: "192.168.1.XXX"
  username: "GENERATED_TOKEN"
```

## Outils disponibles

| Outil | Description | Parametres |
|-------|-------------|------------|
| `turn_on_light` | Allume une lumiere | `entity_id` |
| `turn_off_light` | Eteint une lumiere | `entity_id` |
| `set_brightness` | Regle luminosite | `entity_id`, `brightness` (0-254) |
| `set_color_rgb` | Couleur RGB | `entity_id`, `r`, `g`, `b` |
| `set_color_temperature` | Temperature couleur | `entity_id`, `kelvin` |
| `set_scene` | Active une scene | `scene_name` |
| `get_all_lights` | Liste les lumieres | - |

## Test standalone

```bash
# Lancer le serveur MCP
python -m hue_mcp

# Tester avec Claude Code
# Utiliser les outils hue.* dans l'interface
```

## Validation

| Test | Resultat attendu |
|------|------------------|
| `hue.get_all_lights` | Liste des lumieres avec ID |
| `hue.turn_on_light` | Lumiere s'allume (<50ms) |
| `hue.set_color_rgb` | Couleur change (<50ms) |
| `hue.set_scene` | Scene activee |

## Entity IDs

Les entity_id correspondent aux noms des lumieres dans l'app Hue.
Utiliser `get_all_lights` pour obtenir la liste.

Exemples :
- `salon` : Lumiere principale du salon
- `bureau` : Lampe du bureau
- `all` : Toutes les lumieres (groupe)

## Troubleshooting

### Bridge non trouve
- Verifier que le Bridge est allume (LED bleue)
- Verifier la connexion reseau
- Utiliser l'IP fixe au lieu de la decouverte

### Token invalide
- Refaire le pairing (bouton + commande pair)
- Verifier les droits du fichier config.json

### Lumiere non reactive
- Verifier que la lumiere est accessible dans l'app Hue
- Verifier l'entity_id avec get_all_lights
