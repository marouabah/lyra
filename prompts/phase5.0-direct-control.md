# Phase 5.0 - Vue d'ensemble Controle Direct

## Objectif

Setup controle direct TV + Hue avec latence minimale pour :
- Actions temps-reel
- Beat sync (lumieres synchronisees musique)
- Reactivite maximale

## Architecture Hybride

```
┌─────────────────────────────────────────────────────────────────┐
│                        LYRA - DOMOTIQUE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  [Commande] ──► [Ollama/Qwen] ──► [Tool Call]                  │
│                                        │                        │
│                                        ▼                        │
│                                 ┌────────────┐                  │
│                                 │ MCPManager │                  │
│                                 └─────┬──────┘                  │
│                    ┌──────────────────┼──────────────────┐      │
│                    ▼                  ▼                  ▼      │
│            [fedora-agents]     [pylips-mcp]        [hue-mcp]    │
│            (VM/Backup)         (TV direct)       (Lumieres)     │
│                    │                  │                  │      │
│                    ▼                  ▼                  ▼      │
│               [KVM/Virsh]      [Philips TV]      [Hue Bridge]   │
│                                  (<100ms)           (<50ms)     │
└─────────────────────────────────────────────────────────────────┘
```

## Stack Technique

| Composant | Technologie | Latence cible |
|-----------|-------------|---------------|
| TV Philips | pylips (API JointSpace) | <100ms |
| Lumieres Hue | hue-mcp (API locale) | <50ms |
| Home Assistant | Optionnel (scenes complexes) | ~500ms |

## Quand utiliser quel MCP ?

| Besoin | MCP | Latence |
|--------|-----|---------|
| Allumer/eteindre TV | `tv.power_on/off` | <100ms |
| Volume TV | `tv.volume_*` | <100ms |
| Ambilight on/off/mode | `tv.ambilight_*` | <100ms |
| Beat sync lumieres | `hue.set_light` | <50ms |
| Couleur/brightness | `hue.set_brightness` | <50ms |
| Scene complexe | `ha.scene_turn_on` | ~500ms |

## Prerequis

1. **TV Philips** avec API JointSpace activee
   - IP connue sur le reseau local
   - Pairing effectue (user/pass generes)

2. **Bridge Hue**
   - IP connue sur le reseau local
   - Token d'authentification

3. **Python 3.11+** avec environnement Lyra

## Mode Performance

Le mode performance permet une execution instantanee (<200ms) sans confirmation :
- Active avec `./run.sh --performance` ou commande `mode performance`
- Desactive les confirmations pour les outils domotique
- Garde les confirmations pour les outils destructifs (vm_destroy, etc.)

## Ordre d'implementation

1. **Phase 5.1** : pylips-mcp (TV Philips)
2. **Phase 5.2** : hue-mcp (Lumieres Hue)
3. **Phase 5.4** : Integration multi-MCP dans Lyra
4. **Phase 5.3** : Home Assistant (optionnel, pour scenes complexes)
