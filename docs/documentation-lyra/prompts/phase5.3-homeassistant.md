# Phase 5.3 - Home Assistant (Optionnel)

## Objectif

Setup Home Assistant pour scenes complexes et automations.

**Note**: HA n'est PAS utilise pour le controle direct (trop lent).
Utiliser uniquement pour :
- Scenes multi-devices (TV + lumieres + musique)
- Automations temporelles (allumer a 18h)
- Integration devices Zigbee futurs
- Capteurs et conditions

## Installation Docker

```bash
mkdir -p /home/amineutron/docker/homeassistant

cat > /home/amineutron/docker/homeassistant/docker-compose.yml << 'EOF'
services:
  homeassistant:
    container_name: homeassistant
    image: ghcr.io/home-assistant/home-assistant:stable
    volumes:
      - ./config:/config
      - /etc/localtime:/etc/localtime:ro
    restart: unless-stopped
    network_mode: host
    privileged: true
EOF

cd /home/amineutron/docker/homeassistant
docker compose up -d
```

## Configuration initiale

1. Acceder a `http://localhost:8123`
2. Creer compte admin
3. Configurer le nom de la maison
4. Detecter les devices sur le reseau

## Integrations a ajouter

### Philips Hue
- Settings > Integrations > Add > Philips Hue
- Decouverte automatique du Bridge
- Appuyer sur le bouton du Bridge pour confirmer

### Philips TV (philips_js)
- Settings > Integrations > Add > Philips TV
- Entrer l'IP de la TV
- Suivre le pairing (PIN sur TV)

## Generation du Long-Lived Token

1. Profile utilisateur (en bas a gauche)
2. Security > Long-Lived Access Tokens
3. Create Token > Nommer "Lyra MCP"
4. Copier et sauvegarder le token

## Configuration MCP

Ajouter dans `/home/amineutron/dev/lyra/config.yaml` :

```yaml
homeassistant:
  url: "http://localhost:8123"
  token: "${HA_TOKEN}"
  enabled: false  # Activer quand pret
```

## Scenes a creer

| Scene | Devices | Action |
|-------|---------|--------|
| `scene.cinema` | TV + Ambilight + Lumieres | TV on, Ambilight video, lumieres tamisees |
| `scene.soiree` | Lumieres | Couleurs festives |
| `scene.detente` | Lumieres | Blanc chaud, 30% |
| `scene.travail` | Bureau | Blanc froid, 100% |
| `scene.nuit` | Toutes | Eteindre tout |

### Creation d'une scene

1. Settings > Automations & Scenes > Scenes
2. Create Scene
3. Ajouter les devices et leurs etats
4. Sauvegarder

## Automations utiles

### Extinction automatique
```yaml
alias: "Extinction nuit"
trigger:
  - platform: time
    at: "23:00:00"
action:
  - service: scene.turn_on
    target:
      entity_id: scene.nuit
```

### Allumage au coucher de soleil
```yaml
alias: "Lumieres coucher soleil"
trigger:
  - platform: sun
    event: sunset
action:
  - service: scene.turn_on
    target:
      entity_id: scene.soiree
```

## Outils MCP Home Assistant

| Outil | Description |
|-------|-------------|
| `ha.scene_turn_on` | Active une scene |
| `ha.automation_trigger` | Declenche une automation |
| `ha.light_turn_on` | Allume une lumiere (via HA) |
| `ha.media_play` | Controle media |

## Validation

| Test | Resultat |
|------|----------|
| HA accessible | `http://localhost:8123` OK |
| Scene cinema | TV + lumieres changent ensemble |
| Token valide | API repond sans erreur 401 |

## Quand utiliser HA vs MCP direct ?

| Besoin | Solution | Pourquoi |
|--------|----------|----------|
| Allumer TV seule | `tv.power_on` | Plus rapide |
| Changer couleur | `hue.set_color_rgb` | Plus rapide |
| Scene cinema | `ha.scene_turn_on` | Coordonne plusieurs devices |
| Automation horaire | HA automation | Fonctionne sans Lyra |
