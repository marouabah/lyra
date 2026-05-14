# PHASE 0 - DÉTECTION & VALIDATION

## CONTEXTE
Tu travailles sur la scène "Iron Man" pour Lyra, un assistant vocal local.
Cette scène dure 33 secondes et synchronise TV + lumières Hue.

## TON RÔLE
Créer le système qui détecte quand l'utilisateur dit "je suis iron man" et valide que tout est prêt.

## OBJECTIFS

### 1. Détection des triggers vocaux

Phrases qui activent la scène:
- "je suis iron man"
- "je suis tony stark"
- "je suis tony"
- "mode iron man"
- "scène iron man"

Contraintes:
- Insensible à la casse (majuscules/minuscules)
- Insensible aux accents
- Peut être dans une phrase plus longue ("Lyra, je suis iron man")

### 2. Validation disponibilité devices

**TV Philips:**
- IP: 192.168.1.50
- Test de connexion: Requête HTTP GET sur http://192.168.1.50:1925/6/system
- Timeout: 2 secondes maximum
- Si offline: Annuler avec message "TV Philips non disponible"

**Bridge Hue:**
- IP: 192.168.1.51
- Test via bibliothèque phue
- Timeout: 2 secondes maximum
- Si offline: Annuler avec message "Bridge Hue non disponible"

### 3. Sauvegarde état actuel (rollback)

Sauvegarder dans /tmp/ironman_rollback.json:

**TV:**
- État power (on/off)
- Volume actuel (0-60)
- Application ouverte si détectable

**Lumières Hue:**
Pour chaque lumière (ID 1 à 5):
- État on/off
- Luminosité (0-254)
- Couleur RGB actuelle

Groupe 81 (toutes lumières):
- Scène active si applicable

Format: JSON structuré

### 4. Gestion des erreurs

**Device offline:**
- Logger l'erreur complète avec stacktrace
- Message utilisateur clair et actionnable
- Ne PAS lancer la scène

**Autre erreur:**
- Logger tout le contexte
- Message: "Erreur technique, vérifiez les logs"
- Annuler proprement

## STRUCTURE ATTENDUE

Fichier: `phase0_detection.py`
Emplacement: `~/lyra/scenes/ironman/phases/`

Classe principale: `Phase0Detection`

Méthodes nécessaires:

**is_trigger_detected(text: str) -> bool**
- Vérifie si le texte contient un des triggers
- Retourne True si match, False sinon

**check_tv_available() -> (bool, str)**
- Teste connectivité TV
- Retourne (True, "") si OK
- Retourne (False, "message erreur") si KO

**check_hue_available() -> (bool, str)**
- Teste connectivité Bridge Hue
- Retourne (True, "") si OK
- Retourne (False, "message erreur") si KO

**save_current_state() -> dict**
- Récupère état actuel TV + Hue
- Sauvegarde dans JSON
- Retourne le dictionnaire sauvegardé

**validate_and_prepare() -> (bool, str, dict)**
- Fonction principale qui orchestre tout
- Check devices
- Sauvegarde état
- Retourne (success, message, saved_state)

## TESTS À CRÉER

Fichier: `test_phase0.py`

Tests unitaires:
1. Détection triggers positifs (toutes variantes)
2. Détection triggers négatifs (phrases similaires mais non-triggers)
3. Case insensitive ("JE SUIS IRON MAN" marche)
4. Détection dans phrase longue
5. TV online (mock)
6. TV offline (mock)
7. Hue online (mock)
8. Hue offline (mock)
9. Sauvegarde JSON correcte

## DOCUMENTATION

Fichier: `README.md`

Contenu:
- Description de la phase
- Comment tester manuellement
- Exemples de triggers valides/invalides
- Comment simuler TV/Hue offline pour tests
- Format du JSON de sauvegarde

## CRITÈRES DE SUCCÈS

✅ Détecte tous les triggers correctement
✅ Gère variations casse/accents
✅ Vérifie TV en <2s
✅ Vérifie Hue en <2s
✅ Sauvegarde état complet au format JSON
✅ Messages erreur clairs
✅ Tous tests passent

## LIVRABLES

1. `phase0_detection.py` - Implémentation complète
2. `test_phase0.py` - Suite de tests
3. `README.md` - Documentation
