# Phase 5.1 - Pylips MCP Wrapper ✅ COMPLETE

## Status: TERMINE (2025-01-23)

| Element | Status |
|---------|--------|
| pylips clone | ✅ `/home/amineutron/dev/pylips` |
| Pairing TV | ✅ Philips 55OLED705/12 @ 192.168.1.50 |
| config.yaml | ✅ TV configuree + activee |
| Serveur MCP | ✅ `mcp-servers/pylips-mcp/server.py` |
| Test API | ✅ Volume/Mute fonctionnels |

## Objectif

Creer un wrapper MCP autour de pylips pour exposer les commandes TV Philips.

## Installation pylips

```bash
cd /home/amineutron/dev
git clone https://github.com/eslavnov/pylips.git
cd pylips
pip install -r requirements.txt

# Test connexion
python pylips.py --host <TV_IP> --user <user> --pass <pass> --command powerstate
```

## Pairing TV (premiere fois)

```bash
cd /home/amineutron/dev/pylips
python pylips.py --host <TV_IP> --command pair
# Entrer le PIN affiche sur la TV
# Sauvegarder user/pass generes dans config.yaml
```

## Structure du MCP Server

**Fichier**: `/home/amineutron/dev/lyra/mcp-servers/pylips-mcp/server.py`

Le serveur MCP expose les outils suivants :

| Outil | Description | Parametres |
|-------|-------------|------------|
| `power_on` | Allume la TV | - |
| `power_off` | Eteint la TV (standby) | - |
| `volume_up` | Augmente le volume | - |
| `volume_down` | Baisse le volume | - |
| `volume_set` | Regle le volume | `level` (0-60) |
| `mute` | Coupe/remet le son | - |
| `ambilight_on` | Active l'Ambilight | - |
| `ambilight_off` | Desactive l'Ambilight | - |
| `ambilight_mode` | Change le mode Ambilight | `mode` |
| `launch_app` | Lance une application | `app` |
| `get_state` | Etat actuel de la TV | - |

## Configuration

Ajouter dans `/home/amineutron/dev/lyra/config.yaml` :

```yaml
tv:
  host: "192.168.1.XXX"  # IP de la TV
  user: "xxx"            # User genere par pairing
  pass: "xxx"            # Pass genere par pairing
```

## Validation

| Test | Commande | Resultat attendu |
|------|----------|------------------|
| Power | `tv.power_on` | TV s'allume (<100ms) |
| Volume | `tv.volume_up` | Volume +1 |
| Ambilight | `tv.ambilight_on` | Ambilight active |
| Etat | `tv.get_state` | `{"powerstate": "On"}` |

## Modes Ambilight disponibles

- `follow_video` : Suit le contenu video (standard)
- `follow_audio` : Reagit au son
- `lounge_light` : Lumiere d'ambiance
- `manual` : Couleur fixe

## Troubleshooting

### TV non accessible
- Verifier que la TV est allumee (pas en veille)
- Verifier l'IP dans config.yaml
- Tester `ping <TV_IP>`

### Pairing refuse
- Appuyer sur OK sur la telecommande quand demande
- La TV doit etre sur une source (pas en mode ambiance)

### Timeout
- Augmenter le timeout dans config.yaml
- Verifier le reseau Wi-Fi
