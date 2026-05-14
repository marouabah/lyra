# Workflow Clone avec Validations Multiples

## Vue d'ensemble

Le workflow de clonage de VM intègre maintenant **plusieurs validations** à chaque étape critique pour garantir la transparence et la sécurité.

---

## Workflow complet - Exemple détaillé

### **Commande initiale**
```
>>> clone preprod-01 en clone4test
```

---

### **Étape 0 : Détection VM en cours d'exécution**

```
⚠️  La VM **preprod-01** est en cours d'exécution!

Pour cloner une VM, elle doit être arrêtée.

💡 Options:
  1. **Arrêter** temporairement preprod-01, cloner, puis redémarrer
  2. **Arrêter** preprod-01 et cloner (sans redémarrage)
  3. **Annuler** le clonage

Ton choix ? (1/2/3)
```

**Réponse utilisateur** : `1`

---

### **Validation 1 : Confirmation du plan complet**

```
📋 Plan d'action:
  1. Arrêter preprod-01
  2. Cloner preprod-01 → clone4test
  3. Redémarrer preprod-01

Confirmer ce plan ? [O/n]
```

**Réponse utilisateur** : `O`

---

### **Validation 2 : Confirmation avant arrêt**

```
[i] Etape 1/3: Arrêt de preprod-01

État actuel:
  ========================================
    VM: preprod-01
  ========================================

  Status:  en cours d'exécution
  IP:      192.168.122.245

==================================================
  ACTION PROPOSEE
==================================================

  Outil: fedora.vm_stop
  Parametres:
    - vm_name: preprod-01

==================================================

Executer ? [O/n/d/m] (O=oui, n=non, d=details, m=modifier)
```

**Réponse utilisateur** : `O`

```
[i] Arrêt de preprod-01 en cours...
✅ preprod-01 arrêtée
```

---

### **Validation 3 : Confirmation avant clone**

```
[i] Etape 2/3: Clonage

📋 Récapitulatif du clonage:
  🔹 VM source     : **preprod-01** (arrêtée ✓)
  🔸 VM destination: **clone4test**

==================================================
  ACTION PROPOSEE
==================================================

  Outil: fedora.vm_clone
  Parametres:
    - source_vm: preprod-01
    - new_vm_name: clone4test

==================================================

Executer ? [O/n/d/m] (O=oui, n=non, d=details, m=modifier)
```

**Réponse utilisateur** : `O`

```
[i] Clonage de preprod-01 vers clone4test en cours...
✅ Clone clone4test créé avec succès
🔔 Notification Discord envoyée!
```

---

### **Validation 4 : Confirmation avant redémarrage**

```
[i] Etape 3/3: Redémarrage de preprod-01

Redémarrer preprod-01 maintenant ? [O/n]
```

**Réponse utilisateur** : `O`

```
[i] Redémarrage de preprod-01 en cours...
✅ preprod-01 redémarrée

+------------------------------------------------+
|  RESULTAT
+------------------------------------------------+

  ✅ preprod-01 arrêtée
  ✅ Clone clone4test créé
  ✅ preprod-01 redémarrée
```

---

## Avantages des validations multiples

| Validation | Avantage | Peut annuler ? |
|------------|----------|----------------|
| **Plan complet** | Vue d'ensemble avant toute action | ✅ Oui |
| **Avant arrêt** | Vérifier l'état, utiliser option "m" | ✅ Oui |
| **Avant clone** | Modifier le nom destination si besoin | ✅ Oui + "m" |
| **Avant redémarrage** | Choix de laisser arrêtée | ✅ Oui |

---

## Options disponibles à chaque validation

### **Validation du plan**
- `O` / `Entrée` : Continuer
- `n` : Annuler tout

### **Validations d'actions MCP**
- `O` / `Entrée` : Exécuter
- `n` : Annuler
- `d` : Voir détails techniques
- `m` : **Modifier les arguments**

### **Validation redémarrage**
- `O` / `Entrée` : Redémarrer
- `n` : Laisser arrêtée

---

## Scénarios de modification

### **Scénario 1 : Modifier le nom de destination pendant le clone**

```
Executer ? [O/n/d/m] m

[i] Modification des parametres du clone...

  new_vm_name [clone4test]: clone-production-backup

[i] Nouveaux parametres:
  - source_vm: preprod-01
  - new_vm_name: clone-production-backup

Executer ? [O/n/d/m] O
```

### **Scénario 2 : Annuler après avoir arrêté la VM**

```
Executer ? [O/n/d/m] n

⚠️  Clone annulé.

  Redémarrer preprod-01 quand même ? [O/n] O

[i] Redémarrage de preprod-01...
✅ preprod-01 redémarrée
```

---

## Résumé des points de validation

```
┌─────────────────────────────────────────┐
│ 1. Choix option (1/2/3)                 │ ← Utilisateur choisit le plan
├─────────────────────────────────────────┤
│ 2. Confirmation plan complet [O/n]      │ ← Vue d'ensemble
├─────────────────────────────────────────┤
│ 3. Confirmation arrêt VM [O/n/d/m]      │ ← Peut annuler
├─────────────────────────────────────────┤
│ 4. Confirmation clone [O/n/d/m]         │ ← Peut modifier nom destination
├─────────────────────────────────────────┤
│ 5. Confirmation redémarrage [O/n]       │ ← Peut laisser arrêtée
└─────────────────────────────────────────┘
```

**Total : 5 points de validation** pour un contrôle maximal ! 🛡️

---

## Philosophie

> **"Mieux vaut trop de validations que pas assez"**

Chaque validation permet :
- ✅ De **vérifier** ce qui va se passer
- ✅ De **modifier** si besoin
- ✅ D'**annuler** à tout moment
- ✅ De **comprendre** chaque étape

**Transparence maximale = Confiance maximale** 💯

---

## ✅ WORKFLOW VALIDÉ

**Date**: 2026-02-07
**Status**: Workflow complet fonctionnel en production

Toutes les validations (5 points) fonctionnent correctement :
1. ✅ Choix option (1/2/3) pour VM running
2. ✅ Confirmation plan complet [O/n]
3. ✅ Confirmation arrêt VM [O/n/d/m]
4. ✅ Confirmation clone [O/n/d/m] avec modification possible
5. ✅ Confirmation redémarrage [O/n]

**Notifications Discord** : ✅ Fonctionnelles pour toutes les opérations async

Voir **FIX_DISCORD_WEBHOOK.md** pour les corrections appliquées.
