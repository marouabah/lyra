# Intégration Workflow Restauration de Snapshot

**Date**: 2026-02-07
**Status**: ✅ Intégré et prêt pour tests

---

## ✅ Changements effectués

### 1. Fonction principale - `_handle_snapshot_restore_with_safety()`

**Fichier**: `main_rag.py` (lignes 432-700)

Workflow séquentiel avec validations multiples:
- Liste les snapshots disponibles
- Propose création snapshot de sécurité (recommandé)
- Affiche le plan d'action complet
- Gère l'arrêt/redémarrage si VM running
- Confirme chaque étape critique
- Envoie notification Discord

### 2. Routing automatique

**Fichier**: `main_rag.py` (lignes 155-157)

```python
# Cas special: restauration de snapshot avec securite
if "vm_snapshot" in tool_name and arguments.get("action") == "revert":
    return _handle_snapshot_restore_with_safety(pipeline, arguments, vocal, voice)
```

**Détection**: Automatique quand l'utilisateur demande de restaurer un snapshot

### 3. Support Discord

**Fichier**: `main_rag.py`
- Ligne 52-55: Ajout `"vm_snapshot"` dans `ASYNC_TOOLS`
- Ligne 458: Mapping `"vm_snapshot": "📸 Snapshot VM"`

### 4. Documentation complète

**Fichier**: `WORKFLOW_SNAPSHOT_RESTORE.md`

Documentation détaillée avec:
- Workflow complet pas à pas
- Exemples de validations
- Scénarios de récupération
- Comparaison avec vm_clone
- Intégration technique

### 5. MEMORY.md mis à jour

Ajout section "Snapshot Restore Workflow (Phase 4+)" dans Recent Changes

---

## 🎯 Fonctionnalités

### Points de validation

**Minimum (VM arrêtée, sans snapshot de sécurité)**: 4 validations
1. Liste snapshots disponibles
2. Choix snapshot de sécurité (1/2/3)
3. Confirmation plan complet
4. Confirmation restauration

**Maximum (VM running, avec snapshot de sécurité)**: 6 validations
1. Liste snapshots disponibles
2. Choix snapshot de sécurité (1/2/3)
3. Confirmation plan complet
4. Confirmation création snapshot de sécurité
5. Confirmation arrêt VM
6. Confirmation restauration
7. Confirmation redémarrage (optionnel)

### Snapshot de sécurité

Option recommandée qui crée un snapshot automatique avant la restauration:
- Nom auto-généré: `restore-backup-{vm_name}-{timestamp}`
- Permet de revenir à l'état actuel si problème
- Proposé systématiquement à l'utilisateur (option 1/2/3)

### Gestion VM running

Si la VM est en cours d'exécution:
- Détection automatique de l'état
- Arrêt avant restauration (avec confirmation)
- Option de redémarrage après restauration
- Proposition de redémarrer même si annulation

### Notifications Discord

Envoi automatique avec champs:
- `vm_name`: Nom de la VM
- `action`: "revert"
- `snapshot_name`: Snapshot restauré
- `safety_snapshot`: Snapshot de sécurité créé (si applicable)

---

## 🧪 Tests à effectuer

### Test 1: Restauration simple (VM arrêtée, sans snapshot de sécurité)

```bash
./run.sh
>>> liste les snapshots de preprod-01
>>> restaure le snapshot pre-update de preprod-01
[Choisir option 2: Restaurer directement]
[Confirmer le plan]
[Confirmer la restauration]
```

**Attendu**: Restauration réussie avec notification Discord

### Test 2: Restauration avec snapshot de sécurité (VM arrêtée)

```bash
>>> restaure le snapshot pre-update de preprod-01
[Choisir option 1: Créer snapshot de sécurité]
[Confirmer le plan]
[Confirmer création snapshot de sécurité]
[Confirmer la restauration]
```

**Attendu**:
- Snapshot de sécurité créé avec nom `restore-backup-preprod-01-{timestamp}`
- Restauration réussie
- Notification Discord avec `safety_snapshot`

### Test 3: Restauration avec VM running

```bash
>>> demarre preprod-01
>>> restaure le snapshot pre-update de preprod-01
[Choisir option 1: Créer snapshot de sécurité]
[Choisir O pour redémarrer après]
[Confirmer le plan]
[Confirmer création snapshot]
[Confirmer arrêt VM]
[Confirmer restauration]
[Confirmer redémarrage]
```

**Attendu**:
- Snapshot de sécurité créé
- VM arrêtée
- Snapshot restauré
- VM redémarrée
- Notification Discord

### Test 4: Annulation pendant restauration (VM running)

```bash
>>> demarre preprod-01
>>> restaure le snapshot pre-update de preprod-01
[Choisir option 1]
[Confirmer le plan]
[Confirmer création snapshot]
[Confirmer arrêt VM]
[ANNULER la restauration avec 'n']
[Choisir O pour redémarrer quand même]
```

**Attendu**:
- Snapshot de sécurité créé
- VM arrêtée
- VM redémarrée
- Message: "⚠️ Restauration annulée"

### Test 5: Snapshot inexistant

```bash
>>> restaure le snapshot inexistant-123 de preprod-01
```

**Attendu**: Message d'erreur "Snapshot 'inexistant-123' introuvable!"

---

## 📋 Comparaison avec vm_clone_with_stop

| Aspect | vm_clone_with_stop | snapshot_restore_with_safety |
|--------|-------------------|------------------------------|
| **Type d'action** | Duplication | Restauration (destructif) |
| **Durée** | ~60s | ~5-10s |
| **Détection VM running** | ✅ Menu 3 options | ✅ Détection + plan |
| **Snapshot de sécurité** | ❌ N/A | ✅ Recommandé |
| **Points de validation** | 5 | 4-6 |
| **Notification Discord** | ✅ | ✅ |
| **Récupération échec** | Clone échoue | Snapshot de sécurité |

---

## 🔄 Workflow similaire

Les deux workflows partagent la même philosophie:

1. **Détection automatique** de l'état de la VM
2. **Plan d'action complet** avant toute exécution
3. **Validations multiples** à chaque étape critique
4. **Transparence maximale** sur les actions effectuées
5. **Notifications Discord** pour opérations async
6. **Récupération en cas d'erreur** ou d'annulation

---

## ✅ Checklist finale

- [x] Fonction `_handle_snapshot_restore_with_safety()` implémentée
- [x] Routing automatique dans `handle_action()`
- [x] Support Discord (ASYNC_TOOLS + title_map)
- [x] Documentation WORKFLOW_SNAPSHOT_RESTORE.md créée
- [x] MEMORY.md mis à jour
- [x] Fichier temporaire supprimé
- [ ] Tests utilisateur (Test 1 à 5)
- [ ] Validation production

---

## 🚀 Prêt pour tests

Le workflow est **100% intégré** et prêt à être testé. Tu peux maintenant:

```bash
./run.sh
>>> restaure le snapshot pre-update de preprod-01
```

Et suivre le workflow séquentiel avec validations ! 🎯
