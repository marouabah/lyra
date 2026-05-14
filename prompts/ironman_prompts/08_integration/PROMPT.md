# INTÉGRATION DANS LYRA

## CONTEXTE
Intégrer l'orchestrateur Iron Man dans le système principal Lyra.
Permettre déclenchement vocal naturel.

## TON RÔLE
Modifier le code existant de Lyra pour ajouter la scène Iron Man.

## MODIFICATIONS NÉCESSAIRES

### 1. Fichier main.py

**Où modifier:**
Dans la fonction qui traite les commandes vocales.
Avant l'appel au LLM.

**Quoi faire:**
- Importer IronManOrchestrator
- Initialiser orchestrateur au démarrage
- Vérifier trigger AVANT LLM
- Si trigger détecté: Skip LLM
- Sinon: Flow normal

**Logique:**
```
process_voice_command(user_text):
    # Vérifier scènes AVANT LLM
    if ironman_orchestrator.trigger(user_text):
        return  # Scène gérée
    
    # Sinon flow normal LLM
    llm.process(user_text)
```

### 2. Configuration YAML

**Fichier:** config.yaml

**Section à ajouter:**
```yaml
scenes:
  ironman:
    enabled: true
    triggers:
      - "je suis iron man"
      - "je suis tony stark"
      - "je suis tony"
      - "mode iron man"
    auto_performance_mode: true
    youtube_video_id: "pAgnJDJN4VA"
    tts_phrase: "random"
```

**Paramètres:**

**enabled:** true/false pour activer/désactiver

**triggers:** Liste phrases d'activation

**auto_performance_mode:** Si true, active mode perf temporairement

**youtube_video_id:** ID vidéo YouTube (modifiable)

**tts_phrase:**
- "random" pour sélection aléatoire
- Ou phrase spécifique

### 3. Mode performance automatique

**Comportement:**
- Scène Iron Man détectée
- Mode performance activé temporairement
- Désactive confirmations tools TV/Hue
- Après scène: Restaure mode précédent

**Pourquoi:**
- Scène nécessite rapidité
- Pas de confirmations manuelles
- Expérience fluide

### 4. Fallback devices offline

**Si TV offline:**
- Message vocal: "TV Philips non disponible. Impossible de lancer la scène."
- Proposition: "Voulez-vous que je réessaye ?"
- Ou: "Voulez-vous la version lights-only ?" (sans TV)

**Si Hue offline:**
- Message: "Bridge Hue non disponible. Scène annulée."
- Proposition: "Vérifiez la connexion du Bridge."

**Si YouTube Cast échoue:**
- Continuer en mode lights-only
- Notification: "Musique indisponible, mode lumières uniquement."

## STRUCTURE FICHIER

Modifications dans: `~/lyra/main.py`

Classe Lyra:

**__init__:**
- Charger config scenes
- Si ironman.enabled: Initialiser orchestrateur
- Sinon: ironman = None

**process_command:**
- Check scènes AVANT LLM
- Si trigger scène: Gérer et return
- Sinon: Flow normal

## GESTION CONFLITS

**Pas de conflit avec LLM:**
- Scènes checkées EN PREMIER
- Si trigger scène: Skip LLM complètement
- Triggers spécifiques, peu de risque faux positif

**Pas de conflit entre scènes:**
- Actuellement 1 seule scène (Iron Man)
- Si autre scène future: Check chacune
- Première match = execute

## TESTS INTÉGRATION

Fichier: `test_integration.py`

Tests:
1. "je suis iron man" → Lance scène
2. "autre commande" → LLM normal
3. Scène running → Ignore autre trigger
4. Config enabled=false → Skip scène
5. Mode perf auto activé/désactivé
6. Fallback TV offline
7. Fallback Hue offline

## DOCUMENTATION UTILISATEUR

Fichier: `README_USER.md`

Contenu:

**Activation:**
- Comment activer/désactiver dans config
- Phrases trigger disponibles

**Utilisation:**
- Comment lancer la scène
- Durée attendue
- Que faire si problème

**Customisation:**
- Changer vidéo YouTube
- Changer phrase TTS
- Ajouter triggers custom

**Troubleshooting:**
- TV ne répond pas
- Hue ne répond pas
- Musique ne démarre pas
- Lumières désynchronisées

## DÉPLOIEMENT

**Prérequis:**
- Toutes phases implémentées
- Orchestrateur fonctionnel
- Tests passent

**Étapes:**
1. Backup config.yaml actuel
2. Ajouter section scenes
3. Modifier main.py
4. Tester avec "je suis iron man"
5. Vérifier logs
6. Ajuster si besoin

**Rollback si problème:**
- Restaurer config.yaml
- Restaurer main.py
- Redémarrer Lyra

## CRITÈRES DE SUCCÈS

✅ "je suis iron man" lance scène
✅ Pas conflit avec LLM
✅ Mode perf auto fonctionne
✅ Gère devices offline
✅ Config facile modifier
✅ Doc utilisateur claire
✅ Tests intégration passent

## LIVRABLES

1. Modifications `main.py`
2. Exemple `config.yaml`
3. `README_USER.md` documentation
4. `test_integration.py` tests
