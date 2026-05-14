# Phase 6 : Licence MIT et Documentation

## Objectif
Ajouter la licence MIT, les guidelines de contribution et le changelog.

## Actions

### 1. Créer LICENSE
```bash
cat > ~/dev/lyra/LICENSE << 'EOF'
MIT License

Copyright (c) 2024 amineutron

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
EOF
```

### 2. Créer CONTRIBUTING.md
```bash
cat > ~/dev/lyra/CONTRIBUTING.md << 'EOF'
# Contributing to Lyra

Merci de vouloir contribuer à Lyra ! 🎉

## 🐛 Signaler un Bug

1. Vérifiez que le bug n'a pas déjà été signalé dans les [Issues](../../issues)
2. Créez une nouvelle issue avec:
   - Description claire du problème
   - Étapes pour reproduire
   - Comportement attendu vs observé
   - Version de Lyra, Python, OS
   - Logs si disponibles

## 💡 Proposer une Feature

1. Ouvrez une issue avec le tag `enhancement`
2. Décrivez le cas d'usage
3. Discutons avant de coder !

## 🔧 Contribuer du Code

### Setup développement
```bash
git clone https://github.com/USER/lyra.git
cd lyra
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pytest  # Pour les tests
```

### Avant de commit
```bash
# Lancer les tests
pytest tests/ -v

# Vérifier pas de secrets/chemins hardcodés
./scripts/validate-for-release.sh
```

### Pull Request
1. Fork le repo
2. Créez une branche (`git checkout -b feature/ma-feature`)
3. Commitez (`git commit -m 'Add: ma feature'`)
4. Push (`git push origin feature/ma-feature`)
5. Ouvrez une Pull Request

### Convention de commits
- `Add:` Nouvelle fonctionnalité
- `Fix:` Correction de bug
- `Update:` Amélioration existante
- `Docs:` Documentation
- `Refactor:` Refactoring sans changement fonctionnel
- `Test:` Ajout/modification de tests

## 📝 Code Style

- Python: PEP 8
- Docstrings: Format Google ou NumPy
- Comments: Français ou anglais
- Pas de secrets/chemins hardcodés

## 🏗️ Architecture

```
lyra/
├── main.py          # Point d'entrée
├── modules/         # Modules Python
│   ├── llm.py       # Client Ollama
│   ├── mcp.py       # Client MCP
│   ├── ui.py        # Interface utilisateur
│   ├── audio.py     # STT/TTS
│   └── n8n.py       # Async operations
├── mcp-server/      # MCP server (TypeScript)
├── prompts/         # System prompts
└── scripts/         # Scripts utilitaires
```

## 🤝 Code of Conduct

- Soyez respectueux et constructif
- Pas de trolling, harcèlement ou discrimination
- Acceptez les critiques constructives
- Focus sur le code, pas sur les personnes

Merci pour votre contribution ! 🙏
EOF
```

### 3. Créer CHANGELOG.md
```bash
cat > ~/dev/lyra/CHANGELOG.md << 'EOF'
# Changelog

Toutes les modifications notables de ce projet sont documentées ici.

Le format est basé sur [Keep a Changelog](https://keepachangelog.com/fr/1.0.0/),
et ce projet adhère au [Semantic Versioning](https://semver.org/lang/fr/).

## [Unreleased]

### Added
- Publication initiale sur GitHub
- Documentation complète
- Scripts d'installation automatisés

---

## [1.0.0] - 2024-XX-XX

### Added
- 🎙️ **Mode vocal** - STT (Whisper) + TTS (Piper)
- 🖥️ **Gestion VMs KVM** - start, stop, clone, snapshot, destroy
- 💾 **Gestion Backups** - Timeshift, Borg, VM snapshots
- ✅ **Human-in-the-Loop** - Confirmation avant chaque action
- 📋 **Todo List** - Gestion d'actions multiples
- ⚡ **Opérations async** - n8n webhooks + fallback subprocess
- 🔒 **100% local** - Aucun appel API externe

### Stack
- **LLM**: Qwen 2.5 Coder 14B via Ollama
- **STT**: faster-whisper (base, CUDA)
- **TTS**: Piper (fr_FR-upmc-medium)
- **MCP**: fedora-agents intégré

### Security
- Read-First: Vérification d'état avant action
- Actions destructives signalées en rouge
- Pas de secrets dans le code source

---

## Versioning

- **MAJOR**: Changements incompatibles avec versions précédentes
- **MINOR**: Nouvelles fonctionnalités rétrocompatibles
- **PATCH**: Corrections de bugs rétrocompatibles
EOF
```

## Tests de Validation

```bash
# Test 1: LICENSE existe
[ -f ~/dev/lyra/LICENSE ] && echo "✓ LICENSE existe" || echo "✗ ERREUR"

# Test 2: Contient MIT
grep -q "MIT License" ~/dev/lyra/LICENSE && echo "✓ MIT OK" || echo "✗ ERREUR"

# Test 3: Copyright présent
grep -q "Copyright" ~/dev/lyra/LICENSE && echo "✓ Copyright OK" || echo "✗ ERREUR"

# Test 4: CONTRIBUTING.md existe
[ -f ~/dev/lyra/CONTRIBUTING.md ] && echo "✓ CONTRIBUTING OK" || echo "✗ ERREUR"

# Test 5: CHANGELOG.md existe
[ -f ~/dev/lyra/CHANGELOG.md ] && echo "✓ CHANGELOG OK" || echo "✗ ERREUR"

# Test 6: CHANGELOG contient version 1.0.0
grep -q "\[1.0.0\]" ~/dev/lyra/CHANGELOG.md && echo "✓ Version 1.0.0 OK" || echo "✗ ERREUR"
```

## Checklist
- [ ] LICENSE créé avec MIT
- [ ] Copyright avec ton nom/pseudo
- [ ] CONTRIBUTING.md créé
- [ ] CHANGELOG.md créé
- [ ] Date de release à mettre à jour avant publication
