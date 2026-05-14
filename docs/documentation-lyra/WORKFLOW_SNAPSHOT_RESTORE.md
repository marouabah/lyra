# Workflow Restauration de Snapshot avec Sécurité

## Vue d'ensemble

Le workflow de restauration de snapshot intègre **plusieurs validations** et une option de **snapshot de sécurité** pour protéger l'état actuel avant toute restauration destructive.

---

## Workflow complet - Exemple détaillé

### **Commande initiale**
```
>>> restaure le snapshot pre-update de preprod-01
```

---

### **Étape 0 : Vérifications préalables**

```
[i] Vérifications préalables...

📸 Snapshots disponibles:
  pre-update (2026-02-06 14:32)
  pre-config (2026-02-05 10:15)
  clean-state (2026-02-01 09:00)

État actuel de la VM:
  ========================================
    VM: preprod-01
  ========================================

  Status:  arrêté
```

---

### **Validation 1 : Choix snapshot de sécurité**

```
⚠️  ATTENTION: La restauration va écraser l'état actuel!

[i] 💡 Je recommande de créer un snapshot de sécurité
   pour pouvoir revenir à l'état actuel si besoin.

  1. Créer snapshot de sécurité puis restaurer (recommandé)
  2. Restaurer directement (sans snapshot de sécurité)
  3. Annuler

Ton choix ? (1/2/3)
```

**Réponse utilisateur** : `1`

---

### **Validation 2 : Confirmation du plan complet**

```
[i] 📋 Plan d'action:
  1. Créer snapshot de sécurité «restore-backup-preprod-01-20260207-143045»
  2. Restaurer snapshot «pre-update»

  Redémarrer preprod-01 après restauration ? [O/n] n

[i] 📋 Plan d'action:
  1. Créer snapshot de sécurité «restore-backup-preprod-01-20260207-143045»
  2. Restaurer snapshot «pre-update»

Confirmer ce plan ? [O/n]
```

**Réponse utilisateur** : `O`

---

### **Validation 3 : Confirmation création snapshot de sécurité**

```
[i] Étape 1/2: Création snapshot de sécurité

==================================================
  ACTION PROPOSEE
==================================================

  Outil: fedora.vm_snapshot
  Parametres:
    - vm_name: preprod-01
    - action: create
    - snapshot_name: restore-backup-preprod-01-20260207-143045

==================================================

Executer ? [O/n/d/m] (O=oui, n=non, d=details, m=modifier)
```

**Réponse utilisateur** : `O`

```
[i] Création de 'restore-backup-preprod-01-20260207-143045' en cours...
✅ Snapshot de sécurité 'restore-backup-preprod-01-20260207-143045' créé
```

---

### **Validation 4 : Confirmation restauration (action destructive)**

```
[i] Étape 2/2: Restauration snapshot 'pre-update'

⚠️  ATTENTION: Cette action va remplacer l'état actuel de preprod-01
   par l'état du snapshot 'pre-update'.

==================================================
  ACTION PROPOSEE
==================================================

  Outil: fedora.vm_snapshot
  Parametres:
    - vm_name: preprod-01
    - action: revert
    - snapshot_name: pre-update

==================================================

Executer ? [O/n/d/m] (O=oui, n=non, d=details, m=modifier)
```

**Réponse utilisateur** : `O`

```
[i] Restauration du snapshot 'pre-update' en cours...
✅ Snapshot 'pre-update' restauré
🔔 Notification Discord envoyée!

+------------------------------------------------+
|  RESULTAT
+------------------------------------------------+

  ✅ Snapshot de sécurité créé
  ✅ Snapshot 'pre-update' restauré
  ℹ️  preprod-01 reste arrêtée
```

---

## Cas avec VM Running

Si la VM est en cours d'exécution, le workflow ajoute automatiquement les étapes d'arrêt/redémarrage:

```
État actuel de la VM:
  Status:  en cours d'exécution
  IP:      192.168.122.245

[i] 📋 Plan d'action:
  1. Créer snapshot de sécurité «restore-backup-preprod-01-20260207-143510»
  2. Arrêter preprod-01
  3. Restaurer snapshot «pre-update»

  Redémarrer preprod-01 après restauration ? [O/n] O

[i] 📋 Plan d'action:
  1. Créer snapshot de sécurité «restore-backup-preprod-01-20260207-143510»
  2. Arrêter preprod-01
  3. Restaurer snapshot «pre-update»
  4. Redémarrer preprod-01
```

Avec 2 validations supplémentaires:
- **Validation arrêt** : Confirmation avant `vm_stop`
- **Validation redémarrage** : Confirmation finale avant `vm_start`

---

## Avantages des validations multiples

| Validation | Avantage | Peut annuler ? |
|------------|----------|----------------|
| **Liste snapshots** | Vérifier que le snapshot existe | - |
| **État VM** | Savoir si la VM sera arrêtée | - |
| **Snapshot de sécurité** | Créer un point de retour | ✅ Oui (option 3) |
| **Plan complet** | Vue d'ensemble avant toute action | ✅ Oui |
| **Avant création snapshot** | Confirmer le nom du snapshot | ✅ Oui |
| **Avant arrêt VM** | Si VM running, confirmer arrêt | ✅ Oui |
| **Avant restauration** | Dernière chance d'annuler | ✅ Oui |
| **Avant redémarrage** | Choisir de laisser arrêtée | ✅ Oui |

---

## Scénarios de récupération

### **Scénario 1 : Annulation pendant la restauration**

Si l'utilisateur annule pendant la restauration et que la VM a été arrêtée:

```
Executer ? [O/n/d/m] n

⚠️  Restauration annulée.

  Redémarrer preprod-01 quand même ? [O/n] O

[i] Redémarrage de preprod-01...
✅ preprod-01 redémarrée

  ✅ Snapshot de sécurité créé
  ✅ preprod-01 arrêtée
  ✅ preprod-01 redémarrée
  ⚠️  Restauration annulée
```

### **Scénario 2 : Échec de restauration avec snapshot de sécurité**

Si la restauration échoue et qu'un snapshot de sécurité a été créé:

```
[!] Échec de la restauration

⚠️  💡 Tu peux restaurer le snapshot de sécurité 'restore-backup-preprod-01-20260207-143045'
   pour revenir à l'état avant cette tentative de restauration.

  ✅ Snapshot de sécurité créé
  ✅ preprod-01 arrêtée
  ❌ Échec de la restauration: ...
```

---

## Points de validation au total

```
┌──────────────────────────────────────────┐
│ 0. Lister snapshots disponibles          │ ← Vérifier existence
├──────────────────────────────────────────┤
│ 1. Choix snapshot de sécurité (1/2/3)    │ ← Utilisateur choisit la protection
├──────────────────────────────────────────┤
│ 2. Confirmation plan complet [O/n]       │ ← Vue d'ensemble
├──────────────────────────────────────────┤
│ 3. Confirmation création snapshot [O/n/m]│ ← Si option 1 choisie
├──────────────────────────────────────────┤
│ 4. Confirmation arrêt VM [O/n/m]         │ ← Si VM running
├──────────────────────────────────────────┤
│ 5. Confirmation restauration [O/n/m]     │ ← Action destructive
├──────────────────────────────────────────┤
│ 6. Confirmation redémarrage [O/n]        │ ← Si demandé
└──────────────────────────────────────────┘
```

**Total : 4 à 6 points de validation** selon l'état de la VM et les choix ! 🛡️

---

## Comparaison avec vm_clone

| Aspect | vm_clone | vm_snapshot restore |
|--------|----------|---------------------|
| **Action** | Duplication | Restauration (destructif) |
| **Durée** | ~60s | ~5-10s |
| **Sécurité** | VM source préservée | Snapshot de sécurité recommandé |
| **Validations** | 5 points | 4-6 points |
| **Discord** | ✅ | ✅ |
| **Détection VM running** | ✅ | ✅ |

---

## Philosophie de sécurité

> **"Pour une action destructive, le snapshot de sécurité n'est pas optionnel"**

La restauration de snapshot **écrase définitivement** l'état actuel de la VM. Le workflow propose systématiquement:

1. ✅ **Option recommandée** : Créer un snapshot de sécurité AVANT de restaurer
2. ⚠️ **Option avancée** : Restaurer directement (pour utilisateurs experts)
3. ❌ **Option prudente** : Annuler l'opération

**Transparence maximale + Protection maximale = Confiance totale** 💯

---

## Intégration technique

### Fichiers modifiés

| Fichier | Lignes | Changement |
|---------|--------|------------|
| `main_rag.py` | 432-700 | Ajout fonction `_handle_snapshot_restore_with_safety()` |
| `main_rag.py` | 155-157 | Routing automatique pour `vm_snapshot` action `revert` |
| `main_rag.py` | 52-55 | Ajout `vm_snapshot` dans `ASYNC_TOOLS` |
| `main_rag.py` | 458 | Ajout mapping Discord `"vm_snapshot": "📸 Snapshot VM"` |

### Détection automatique

Le workflow est déclenché automatiquement quand:
- Tool name contient `"vm_snapshot"`
- Arguments contiennent `"action": "revert"`

### Discord notification

La notification Discord est envoyée avec les champs:
- `vm_name` : Nom de la VM
- `action` : "revert"
- `snapshot_name` : Snapshot restauré
- `safety_snapshot` : Snapshot de sécurité créé (si applicable)

---

## ✅ STATUS

**Date**: 2026-02-07
**Status**: Implémenté et intégré dans `main_rag.py`
**Prêt pour**: Tests utilisateur

Workflow complet fonctionnel avec:
- ✅ Détection automatique des restaurations de snapshot
- ✅ Snapshot de sécurité recommandé (option 1/2/3)
- ✅ Plan d'action séquentiel avec 4-6 validations
- ✅ Gestion VM running (arrêt/redémarrage)
- ✅ Notifications Discord pour opérations async
- ✅ Récupération en cas d'annulation ou échec

**Voir aussi**:
- `WORKFLOW_CLONE_VALIDATION.md` : Workflow clone avec détection VM running
- `FIX_DISCORD_WEBHOOK.md` : Corrections webhook Discord
- `RESUME_FINAL.md` : Résumé complet des corrections Phase 4
