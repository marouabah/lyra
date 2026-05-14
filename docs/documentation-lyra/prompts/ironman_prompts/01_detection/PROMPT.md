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