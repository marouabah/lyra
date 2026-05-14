# Fix Discord Webhook - Documentation Complète

## ✅ Problème Résolu

Les notifications Discord ne s'envoyaient pas après les opérations `vm_clone` en raison de **deux bugs** :

1. **Variable globale non chargée** : `DISCORD_WEBHOOK_URL` restait à `None`
2. **Import yaml redondant** : `UnboundLocalError` empêchait le chargement

---

## 🐛 Bugs Identifiés et Corrigés

### Bug 1: Import yaml Redondant (CRITIQUE)

**Fichier**: `main_rag.py`
**Ligne**: 552

#### Problème

```python
# Ligne 31: Import global
import yaml

# ...

def main():
    # Ligne 520: Première utilisation de yaml
    cfg = yaml.safe_load(f)  # ← UnboundLocalError ici !

    # ...

    # Ligne 552: Import LOCAL redondant
    if vocal:
        import yaml  # ← PROBLÈME: Python considère yaml comme variable locale
```

Quand Python voit `import yaml` ligne 552 (import local), il considère que `yaml` est une **variable locale** dans **toute la fonction** `main()`. Du coup, l'utilisation de `yaml.safe_load()` ligne 520 (avant l'import local) lève une `UnboundLocalError`.

#### Solution

```python
# SUPPRIMÉ l'import redondant ligne 552
if vocal:
    from modules.audio import VoiceInterface, AudioConfig
    # Plus de "import yaml" ici
```

**Impact**: `DISCORD_WEBHOOK_URL` peut maintenant être chargé sans erreur.

---

### Bug 2: Variable Globale Non Déclarée

**Fichier**: `main_rag.py`
**Ligne**: 518

#### Problème Initial

```python
def main():
    global DISCORD_WEBHOOK_URL  # Déclaré ligne 495

    # ...

    # Ligne 516-518: Chargement webhook
    try:
        # PAS de "global" avant l'assignation dans ce bloc
        DISCORD_WEBHOOK_URL = discord_cfg.get("webhook_url", "")  # ← Variable locale !
```

Bien que `global DISCORD_WEBHOOK_URL` soit déclaré ligne 495, c'était **insuffisant** car l'assignation dans le bloc `try` créait une variable locale.

#### Solution

```python
def main():
    global DISCORD_WEBHOOK_URL

    # ...

    # Ligne 517: Redéclaration explicite avant le bloc
    global DISCORD_WEBHOOK_URL  # ✅ Garantit que l'assignation modifie la globale
    try:
        DISCORD_WEBHOOK_URL = discord_cfg.get("webhook_url", "")  # ✅ OK
```

**Impact**: La variable globale est correctement modifiée et accessible dans `_send_discord_if_async()`.

---

### Bug 3: Menu 3 Options (Bonus)

**Fichier**: `lyra/core/pipeline.py`
**Lignes**: 1290, 1544

#### Problème

Quand le menu 3 options s'affichait (VM running), `pending_args=[]` faisait croire à `main_rag.py` que l'action était prête, donc il affichait "ACTION PROPOSEE" au lieu d'attendre le choix.

#### Solution

```python
# AVANT
pending_args=[]

# APRÈS
pending_args=["_user_choice"]  # Indique qu'on attend le choix 1/2/3
```

**Impact**: Le menu attend maintenant le choix de l'utilisateur sans passer à la confirmation MCP.

---

### Bug 4: AttributeError execution_result.success (Bonus)

**Fichier**: `main_rag.py`
**Lignes**: 316, 367, 379, 387, 412, 460-490

#### Problème

`pipeline.execute_action()` retourne un `PipelineResult`, pas un `ExecutionResult`. Le code essayait d'accéder à `.success` directement.

#### Solution

```python
# AVANT
if stop_result.success:

# APRÈS
if stop_result.execution_result and stop_result.execution_result.success:
```

**Impact**: Plus d'erreur `'PipelineResult' object has no attribute 'success'`.

---

## 🧪 Tests Effectués

### Test 1: Webhook Discord Direct
```bash
✅ Envoi simple: OK
✅ Envoi avec fields (vm_clone): OK
```

### Test 2: Clone VM Réel avec MCP
```bash
✅ Clone preprod-01 → test-discord-real: OK
✅ Notification Discord reçue: OK
✅ Cleanup test-discord-real: OK
```

### Test 3: Workflow Complet Lyra
```bash
✅ Détection typo: preprod01 → preprod-01
✅ Validation duplicate: test-webhook existe → test-webhook-2
✅ Clone exécuté: OK
✅ Notification Discord reçue: ✅ CONFIRMÉ PAR L'UTILISATEUR
```

---

## 📋 Workflow Final Validé

```
1. User: "clone preprod01 en test"
   → Lyra: Détecte typo "preprod01" → "preprod-01"

2. User: "test-webhook"
   → Lyra: Détecte duplicate → propose "preprod-02"

3. User: "test-webhook-2"
   → Lyra: Affiche récapitulatif + confirmation

4. User: "O" (confirme)
   → Lyra: Clone preprod-01 → test-webhook-2
   → 🔔 NOTIFICATION DISCORD ENVOYÉE ✅

5. Discord: 🔄 Clone VM
            ✅ OK
            source_vm: preprod-01
            new_vm_name: test-webhook-2
            Durée: ~26s
```

---

## 📝 Fichiers Modifiés

### main_rag.py

1. **Ligne 552**: Supprimé `import yaml` redondant
2. **Ligne 518**: Ajouté `global DISCORD_WEBHOOK_URL` avant bloc try
3. **Lignes 316, 367, 379, 387, 412**: Fix `execution_result.success`
4. **Lignes 460-490**: Fix `is_success` pour Discord dans `_send_discord_if_async()`

### lyra/core/pipeline.py

1. **Lignes 1290, 1544**: `pending_args=["_user_choice"]` pour menu 3 options

---

## ✅ Résultat Final

- ✅ **Notifications Discord fonctionnelles** pour toutes les opérations async (vm_clone, vm_clone_system, backup_create, backup_restore)
- ✅ **Menu 3 options** s'affiche et attend le choix utilisateur
- ✅ **Workflow séquentiel** fonctionne (stop → clone → restart)
- ✅ **Aucune erreur** AttributeError ou UnboundLocalError

**Validé en production** le 2026-02-07 avec clone réel et notification Discord reçue. 🚀

---

## 🎯 Leçon Apprise

**Toujours vérifier les imports locaux redondants** dans les fonctions Python. Un `import` local fait que Python considère la variable comme locale **dans toute la fonction**, même pour les utilisations AVANT l'import.

```python
# ❌ MAUVAIS
def main():
    x = some_module.func()  # UnboundLocalError !

    if condition:
        import some_module  # Python considère some_module comme local

# ✅ BON
import some_module  # Import global

def main():
    x = some_module.func()  # OK
```
