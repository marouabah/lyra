# PROMPT PHASE 3 — Actions + Sécurité

## Contexte

Projet **Lyra** : Assistant vocal DevOps local.
**Prérequis** : Phase 2 validée (vocal fonctionnel en lecture seule).

## Objectif de cette phase

Activer les commandes d'écriture (vm_start, vm_stop, snapshot) avec les garde-fous de sécurité.

## Commandes à activer

| Commande vocale | Tool MCP | Risque |
|-----------------|----------|--------|
| "Démarre [VM]" | `vm_start` | Faible |
| "Arrête [VM]" | `vm_stop` | Moyen |
| "Crée snapshot [name]" | `vm_snapshot` | Faible |
| "Liste snapshots" | `vm_snapshot --list` | Aucun |

## Tâches à réaliser

### 1. Implémenter le principe "Read-First"

Avant toute action, Goose doit lire l'état. Ajouter au system prompt de Goose :

```
RÈGLE OBLIGATOIRE: Avant d'exécuter vm_start, vm_stop ou vm_snapshot,
tu DOIS d'abord appeler vm_status pour connaître l'état actuel.
Ne jamais agir "dans le noir".
```

Créer le fichier `~/.config/goose/system_prompt.txt` :
```text
Tu es Lyra, un assistant DevOps vocal. Tu contrôles des VMs via MCP.

RÈGLES DE SÉCURITÉ:
1. TOUJOURS appeler vm_status AVANT toute action (start/stop/snapshot)
2. Confirmer l'action à l'utilisateur AVANT de l'exécuter
3. Résumer le résultat après l'action

RÉPONSES:
- Réponds en français
- Sois concis (réponses vocales)
- Annonce ce que tu vas faire avant de le faire
```

### 2. Ajouter la confirmation vocale

Dans `lyra.py`, avant d'envoyer une commande d'action à Goose :

```python
ACTIONS_AVEC_CONFIRMATION = ['start', 'stop', 'arrête', 'démarre', 'snapshot']

def requires_confirmation(text: str) -> bool:
    return any(action in text.lower() for action in ACTIONS_AVEC_CONFIRMATION)

def run(self):
    while True:
        text = self.listen()
        if text:
            if self.requires_confirmation(text):
                self.speak(f"Tu veux que je {text} ?")
                confirm = self.listen()
                if 'oui' not in confirm.lower():
                    self.speak("Action annulée")
                    continue
            response = self.ask_goose(text)
            self.speak(response)
```

### 3. Tester les actions

```bash
# Dans Goose (texte d'abord)
goose session

# Tester le flow complet
> "Démarre la VM preprod"
# Goose doit: 1) vm_status 2) Confirmer 3) vm_start 4) Résumer

> "Arrête la VM test"
# Idem

> "Crée un snapshot avant-test"
# Goose doit: 1) vm_status 2) vm_snapshot create avant-test 3) Confirmer
```

### 4. Valider avec Lyra vocal

```bash
python lyra.py
```

Dire :
- "Démarre la VM preprod" → Lyra demande confirmation
- "Oui" → Lyra exécute et confirme
- "Arrête la VM preprod" → Confirmation → Exécution

## Validation Phase 3

| Test | Résultat attendu |
|------|------------------|
| "Démarre VM" sans VM | Goose refuse poliment |
| "Démarre preprod" | Read-First → Confirm → Action → Résumé |
| "Non" après confirmation | Action annulée |
| "Snapshot test" | Snapshot créé, confirmé vocalement |

## Garde-fous actifs

| Règle | Implémentation |
|-------|----------------|
| Read-First | System prompt Goose |
| Confirmation | Code Python `lyra.py` |
| Double-Clé | Phase 4 (actions destructives) |

## Dépannage

### Goose n'applique pas Read-First
Vérifier que le system prompt est chargé :
```bash
cat ~/.config/goose/system_prompt.txt
```

### Confirmation vocale rate
Ajuster le seuil de silence dans `config.yaml` :
```yaml
audio:
  silence_duration: 1.5  # Plus de temps pour répondre
```

## Fichiers modifiés

- `~/.config/goose/system_prompt.txt` : Règles de sécurité
- `/home/amineutron/dev/lyra/lyra.py` : Ajout confirmation vocale

## Prochaine phase

Une fois validé, passer à **Phase 4 — Async n8n**
