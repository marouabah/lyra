# PROMPT PHASE 4 — Async via n8n

## Contexte

Projet **Lyra** : Assistant vocal DevOps local.
**Prérequis** : Phase 3 validée (actions avec sécurité).

## Objectif de cette phase

Les opérations longues (clone VM ~60s, backup ~120s) ne doivent pas bloquer Lyra.
Architecture "Fire & Forget" via webhooks n8n.

```
Lyra → "Clone la prod" → Webhook n8n → ACK immédiat → ... → Discord notif
```

## Opérations async

| Commande | Durée | Webhook |
|----------|-------|---------|
| Clone VM | ~60s | `/webhook/clone-vm` |
| Backup create | ~120s | `/webhook/backup-create` |
| Backup restore | ~60s | `/webhook/backup-restore` |

## Tâches à réaliser

### 1. Créer les workflows n8n

#### Workflow: Clone VM

1. **Trigger** : Webhook `POST /webhook/clone-vm`
   - Body: `{ "source": "preprod", "target": "sand-01" }`

2. **Nodes** :
   - Execute Command: `vm_snapshot create pre-clone`
   - Execute Command: `vm_clone --source {source} --target {target}`
   - Execute Command: `vm_start {target}`
   - Execute Command: `vm_verify {target}`

3. **Notification** : Discord webhook
   - Message: `"VM '{target}' créée. IP: {ip}. Santé: {score}/100"`

#### Workflow: Backup Create

1. **Trigger** : Webhook `POST /webhook/backup-create`
2. **Nodes** :
   - Execute Command: `backup_create`
3. **Notification** : Discord
   - Message: `"Backup créé: {id}. Taille: {size}"`

### 2. Ajouter l'outil MCP `trigger_n8n`

Dans le serveur MCP fedora-agents, ajouter un tool simple :

```typescript
// Dans tools/n8n-trigger.ts
export const triggerN8nWorkflow = {
  name: 'trigger_n8n',
  description: 'Déclenche un workflow n8n async (clone, backup). Retourne immédiatement.',
  parameters: z.object({
    workflow: z.enum(['clone-vm', 'backup-create', 'backup-restore']),
    data: z.record(z.string()).optional()
  }),
  execute: async ({ workflow, data }) => {
    const response = await fetch(`http://localhost:5678/webhook/${workflow}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data || {})
    });
    return { status: 'started', workflow };
  }
};
```

### 3. Ajouter l'outil `check_n8n_logs`

Pour diagnostiquer si un workflow a planté :

```typescript
export const checkN8nLogs = {
  name: 'check_n8n_logs',
  description: 'Vérifie le status des derniers workflows n8n',
  parameters: z.object({
    workflow: z.string().optional(),
    limit: z.number().default(5)
  }),
  execute: async ({ workflow, limit }) => {
    // Appel API n8n pour récupérer les exécutions
    const response = await fetch(
      `http://localhost:5678/api/v1/executions?limit=${limit}`,
      { headers: { 'X-N8N-API-KEY': process.env.N8N_API_KEY } }
    );
    return await response.json();
  }
};
```

### 4. Mettre à jour le system prompt Goose

Ajouter dans `~/.config/goose/system_prompt.txt` :

```text
OPÉRATIONS LONGUES (async):
- Pour clone VM, backup create/restore: utilise trigger_n8n
- Après trigger_n8n, dis "C'est lancé, tu recevras une notification Discord"
- Si l'utilisateur demande le status d'une opération en cours: utilise check_n8n_logs
```

### 5. Activer dans config.yaml

```yaml
n8n:
  enabled: true  # Était false
```

### 6. Tester le flow complet

```bash
# 1. Dans Goose
> "Clone la VM preprod vers sand-01"
# Attendu: "C'est lancé. Tu recevras une notification Discord."

# 2. Vérifier n8n
# Le workflow doit être en cours d'exécution

# 3. Attendre ~60s
# Discord doit recevoir: "VM 'sand-01' UP. IP: 192.168.x.x"

# 4. Test diagnostic
> "Vérifie les derniers workflows n8n"
# Attendu: Liste des exécutions récentes
```

## Validation Phase 4

| Test | Résultat attendu |
|------|------------------|
| "Clone preprod" | ACK immédiat, terminal libéré |
| Attendre 60s | Discord notifie "VM UP" |
| "Status workflows" | Goose liste les exécutions |
| Workflow échoue | Discord notifie l'erreur |

## Règle Double-Clé (actions destructives)

Pour `vm_destroy` et `backup_restore`, le workflow n8n vérifie :
1. Snapshot existe < 5 minutes
2. Sinon, refuse avec message explicite

```javascript
// Dans le workflow n8n
if (!hasRecentSnapshot(vmName, 5)) {
  throw new Error("Snapshot requis avant suppression. Crée d'abord un snapshot.");
}
```

## Dépannage

### Webhook n8n ne répond pas
```bash
# Vérifier que n8n tourne
curl http://localhost:5678/healthz

# Vérifier les logs n8n
journalctl -u n8n -f
```

### Discord ne notifie pas
Vérifier le webhook Discord dans n8n :
- URL correcte
- Payload JSON valide

### Workflow échoue silencieusement
Utiliser `check_n8n_logs` ou l'UI n8n pour voir les erreurs.

## Fichiers créés/modifiés

- Workflows n8n (via UI n8n)
- `fedora-agents/src/tools/n8n-trigger.ts` : Nouveau tool
- `~/.config/goose/system_prompt.txt` : Règles async
- `/home/amineutron/dev/lyra/config.yaml` : n8n enabled

## V1 Complète

Après Phase 4, Lyra V1 est fonctionnelle :
- Commandes vocales en français
- Lecture d'état instantanée
- Actions avec confirmation
- Opérations longues async + notifications Discord
