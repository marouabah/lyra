# PROMPT PHASE 2 — Ajout Vocal (STT/TTS)

## Contexte

Projet **Lyra** : Assistant vocal DevOps local.
**Prérequis** : Phase 1 validée (Goose + MCP fonctionnels en mode texte).

## Objectif de cette phase

Créer un wrapper Python qui ajoute la couche vocale autour de Goose :
```
Micro → STT (whisper) → Goose stdin → stdout → TTS (piper) → Speaker
```

## Stack vocale
- **STT** : faster-whisper (GPU, français)
- **TTS** : Piper (voix française)
- **Hardware** : RTX 3080 Ti

## Tâches à réaliser

### 1. Installer les dépendances vocales
```bash
pip install faster-whisper piper-tts sounddevice numpy pexpect --break-system-packages
```

> **Note importante** : `pexpect` est ajouté pour gérer l'interaction avec Goose CLI de manière robuste (détection fin de réponse, timeouts).

### 2. Télécharger le modèle Piper français
```bash
# Créer le dossier models
mkdir -p /home/amineutron/dev/lyra/models

# Télécharger la voix française
wget -O /home/amineutron/dev/lyra/models/fr_FR-upmc-medium.onnx \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx

wget -O /home/amineutron/dev/lyra/models/fr_FR-upmc-medium.onnx.json \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/fr/fr_FR/upmc/medium/fr_FR-upmc-medium.onnx.json
```

### 3. Créer le wrapper vocal `lyra.py`

Le wrapper doit :
1. Capturer l'audio du micro
2. Transcrire avec faster-whisper
3. Envoyer le texte à Goose (via pexpect)
4. Récupérer la réponse de Goose
5. Synthétiser avec Piper
6. Jouer l'audio

> **ATTENTION - Interaction CLI robuste** :
> L'interaction avec Goose via stdin/stdout est source de bugs classiques (buffers, détection fin de réponse).
> - Utiliser `pexpect` plutôt que `subprocess` pour gérer les CLI interactifs
> - Détecter le prompt Goose (ex: `>` ou `goose>`) pour savoir quand la réponse est complète
> - Implémenter un timeout pour éviter les blocages infinis
> - Ne pas lire le prompt en boucle dans le TTS

Structure minimale :
```python
#!/usr/bin/env python3
"""Lyra - Wrapper vocal pour Goose CLI"""

import pexpect
import sounddevice as sd
import numpy as np
from faster_whisper import WhisperModel
from piper import PiperVoice

# Pattern pour détecter que Goose attend une entrée
GOOSE_PROMPT = r'(goose>|>|\n\n)'  # À ajuster selon le prompt réel de Goose
RESPONSE_TIMEOUT = 60  # Timeout en secondes

class Lyra:
    def __init__(self):
        # Charger STT (GPU)
        self.stt = WhisperModel("base", device="cuda", compute_type="float16")
        # Charger TTS
        self.tts = PiperVoice.load("models/fr_FR-upmc-medium.onnx")
        # Démarrer Goose en mode interactif
        self.goose = pexpect.spawn('goose session', encoding='utf-8', timeout=RESPONSE_TIMEOUT)
        self.goose.expect(GOOSE_PROMPT)  # Attendre le prompt initial

    def listen(self) -> str:
        """Capture audio et transcrit"""
        # TODO: Implémenter capture micro + transcription
        pass

    def ask_goose(self, text: str) -> str:
        """Envoie texte à Goose et récupère réponse (robuste)"""
        self.goose.sendline(text)
        # Attendre que Goose ait fini de répondre (prompt suivant)
        self.goose.expect(GOOSE_PROMPT)
        # Récupérer la réponse (sans le prompt)
        response = self.goose.before.strip()
        # Nettoyer : enlever la commande envoyée (echo)
        lines = response.split('\n')
        if lines and text in lines[0]:
            lines = lines[1:]
        return '\n'.join(lines).strip()

    def speak(self, text: str):
        """Synthétise et joue l'audio"""
        # TODO: Implémenter TTS + playback
        pass

    def run(self):
        """Boucle principale"""
        print("Lyra écoute... (Ctrl+C pour quitter)")
        try:
            while True:
                text = self.listen()
                if text:
                    response = self.ask_goose(text)
                    self.speak(response)
        finally:
            self.goose.close()  # Fermer proprement la session Goose

if __name__ == "__main__":
    Lyra().run()
```

> **Points critiques** :
> - `GOOSE_PROMPT` doit matcher le vrai prompt de Goose (tester manuellement d'abord)
> - `pexpect.expect()` bloque jusqu'au pattern ou timeout
> - `self.goose.before` contient la réponse AVANT le pattern
> - Toujours nettoyer l'écho de la commande envoyée

### 4. Tester chaque composant séparément

```bash
# Test STT seul
python -c "from faster_whisper import WhisperModel; m = WhisperModel('base', device='cuda'); print('STT OK')"

# Test TTS seul
python -c "from piper import PiperVoice; v = PiperVoice.load('models/fr_FR-upmc-medium.onnx'); print('TTS OK')"

# Test micro
python -c "import sounddevice as sd; print(sd.query_devices())"
```

## Validation Phase 2

| Test | Résultat attendu |
|------|------------------|
| STT seul | Transcrit "Bonjour" correctement |
| TTS seul | Prononce "Test" clairement |
| `python lyra.py` | Démarre sans erreur |
| Dire "Status VMs" | Lyra répond vocalement avec l'état des VMs |

## Configuration audio

Dans `config.yaml`, section audio :
```yaml
audio:
  sample_rate: 16000
  channels: 1
  silence_threshold: 0.01
  silence_duration: 1.0  # Fin de phrase après 1s silence
```

## Dépannage

### Micro non détecté
```bash
# Lister les devices audio
python -c "import sounddevice; print(sounddevice.query_devices())"
```

### CUDA out of memory
Le STT et le LLM partagent le GPU. Solutions :
- Utiliser un modèle STT plus petit (`tiny` au lieu de `base`)
- Libérer la VRAM en fermant Ollama entre les appels

## Fichiers créés/modifiés

- `/home/amineutron/dev/lyra/lyra.py` : Wrapper vocal principal
- `/home/amineutron/dev/lyra/models/` : Modèles Piper

## Prochaine phase

Une fois validé, passer à **Phase 3 — Actions + Sécurité**
