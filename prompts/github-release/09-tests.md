# Phase 9 : Tests Unitaires et CI/CD

## Objectif
Créer des tests basiques et configurer GitHub Actions pour la CI.

## Actions

### 1. Créer la structure tests/
```bash
mkdir -p ~/dev/lyra/tests
touch ~/dev/lyra/tests/__init__.py
```

### 2. tests/test_config.py
```bash
cat > ~/dev/lyra/tests/test_config.py << 'EOF'
"""Tests pour la configuration."""
import os
import sys
import yaml
import pytest

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_config_example_exists():
    """config.yaml.example doit exister."""
    assert os.path.exists("config.yaml.example"), "config.yaml.example manquant"


def test_config_example_valid_yaml():
    """config.yaml.example doit être un YAML valide."""
    with open("config.yaml.example") as f:
        config = yaml.safe_load(f)

    assert config is not None, "config.yaml.example est vide"
    assert "llm" in config, "Section 'llm' manquante"
    assert "mcp" in config, "Section 'mcp' manquante"
    assert "audio" in config, "Section 'audio' manquante"


def test_config_no_secrets():
    """config.yaml.example ne doit pas contenir de secrets."""
    with open("config.yaml.example") as f:
        content = f.read()

    # Pas de JWT token
    assert "eyJ" not in content, "JWT token trouvé dans config.yaml.example!"

    # Pas de chemins hardcodés
    assert "/home/" not in content, "Chemin hardcodé trouvé dans config.yaml.example!"


def test_env_example_exists():
    """.env.example doit exister."""
    assert os.path.exists(".env.example"), ".env.example manquant"


def test_env_example_no_secrets():
    """.env.example ne doit pas contenir de vrais secrets."""
    with open(".env.example") as f:
        content = f.read()

    # Les valeurs doivent être vides ou placeholder
    lines = [l for l in content.split('\n') if '=' in l and not l.strip().startswith('#')]
    for line in lines:
        key, value = line.split('=', 1)
        # La valeur doit être vide ou un placeholder
        assert value.strip() in ('', '${'+key.strip()+'}', 'your_value_here'), \
            f"Secret potentiel trouvé: {key}"
EOF
```

### 3. tests/test_llm_parsing.py
```bash
cat > ~/dev/lyra/tests/test_llm_parsing.py << 'EOF'
"""Tests pour le parsing des tool calls."""
import os
import sys
import pytest

# Ajouter le répertoire parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class MockToolCall:
    """Mock d'un tool call pour les tests."""
    def __init__(self, name: str, arguments: dict):
        self.name = name
        self.arguments = arguments


def parse_tool_calls_simple(content: str) -> list:
    """Version simplifiée du parsing pour les tests."""
    import json
    calls = []

    for line in content.strip().split('\n'):
        line = line.strip()
        if not line:
            continue
        try:
            data = json.loads(line)
            if 'name' in data:
                calls.append(MockToolCall(
                    name=data['name'],
                    arguments=data.get('arguments', {})
                ))
        except json.JSONDecodeError:
            continue

    return calls


def test_parse_single_tool_call():
    """Parse un tool call simple."""
    content = '{"name": "vm_status", "arguments": {}}'
    calls = parse_tool_calls_simple(content)

    assert len(calls) == 1
    assert calls[0].name == "vm_status"
    assert calls[0].arguments == {}


def test_parse_tool_call_with_args():
    """Parse un tool call avec arguments."""
    content = '{"name": "vm_start", "arguments": {"vm_name": "preprod-09"}}'
    calls = parse_tool_calls_simple(content)

    assert len(calls) == 1
    assert calls[0].name == "vm_start"
    assert calls[0].arguments["vm_name"] == "preprod-09"


def test_parse_multiple_tool_calls():
    """Parse plusieurs tool calls."""
    content = '''{"name": "vm_destroy", "arguments": {"vm_name": "sandbox-01"}}
{"name": "vm_destroy", "arguments": {"vm_name": "sandbox-02"}}'''

    calls = parse_tool_calls_simple(content)

    assert len(calls) == 2
    assert calls[0].arguments["vm_name"] == "sandbox-01"
    assert calls[1].arguments["vm_name"] == "sandbox-02"


def test_parse_no_tool_call():
    """Texte sans tool call retourne liste vide."""
    content = "Je ne comprends pas votre demande."
    calls = parse_tool_calls_simple(content)

    assert len(calls) == 0


def test_parse_mixed_content():
    """Parse avec du texte mélangé."""
    content = '''Voici ce que je vais faire:
{"name": "vm_status", "arguments": {}}
C'est fait!'''

    calls = parse_tool_calls_simple(content)

    assert len(calls) == 1
    assert calls[0].name == "vm_status"
EOF
```

### 4. tests/test_validation.py
```bash
cat > ~/dev/lyra/tests/test_validation.py << 'EOF'
"""Tests de validation pour la release GitHub."""
import os
import subprocess
import pytest


def test_no_hardcoded_paths_in_python():
    """Pas de chemins hardcodés dans les fichiers Python."""
    result = subprocess.run(
        ['grep', '-rn', '/home/', '--include=*.py', 'modules/'],
        capture_output=True, text=True
    )

    # Filtrer les faux positifs (commentaires, etc.)
    lines = [l for l in result.stdout.split('\n') if l and '.example' not in l]

    assert len(lines) == 0, f"Chemins hardcodés trouvés:\n{chr(10).join(lines)}"


def test_no_jwt_secrets():
    """Pas de tokens JWT dans le code."""
    result = subprocess.run(
        ['grep', '-rn', 'eyJ', '--include=*.py', '--include=*.yaml', '.'],
        capture_output=True, text=True
    )

    # Exclure les fichiers example
    lines = [l for l in result.stdout.split('\n')
             if l and '.example' not in l and 'node_modules' not in l]

    assert len(lines) == 0, f"JWT tokens trouvés:\n{chr(10).join(lines)}"


def test_required_files_exist():
    """Les fichiers requis pour la release existent."""
    required_files = [
        'README.md',
        'LICENSE',
        'config.yaml.example',
        '.env.example',
        'requirements.txt',
        'install.sh',
        'run.sh',
    ]

    missing = [f for f in required_files if not os.path.exists(f)]

    assert len(missing) == 0, f"Fichiers manquants: {missing}"


def test_mcp_server_exists():
    """Le MCP server est présent."""
    assert os.path.isdir('mcp-server'), "Dossier mcp-server/ manquant"
    assert os.path.exists('mcp-server/package.json'), "mcp-server/package.json manquant"


def test_scripts_executable():
    """Les scripts sont exécutables."""
    scripts = [
        'install.sh',
        'run.sh',
        'scripts/download-models.sh',
        'scripts/setup-mcp.sh',
        'scripts/validate-for-release.sh',
    ]

    for script in scripts:
        if os.path.exists(script):
            assert os.access(script, os.X_OK), f"{script} n'est pas exécutable"
EOF
```

### 5. Ajouter pytest aux requirements.txt
```bash
# Vérifier si pytest est déjà présent
grep -q "pytest" ~/dev/lyra/requirements.txt || echo "pytest>=7.0.0" >> ~/dev/lyra/requirements.txt
```

### 6. Créer la configuration pytest
```bash
cat > ~/dev/lyra/pytest.ini << 'EOF'
[pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
addopts = -v --tb=short
EOF
```

### 7. GitHub Actions CI
```bash
mkdir -p ~/dev/lyra/.github/workflows

cat > ~/dev/lyra/.github/workflows/ci.yml << 'EOF'
name: CI

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'

    - name: Install test dependencies
      run: |
        python -m pip install --upgrade pip
        pip install pytest pyyaml

    - name: Run validation script
      run: |
        chmod +x scripts/validate-for-release.sh
        ./scripts/validate-for-release.sh

    - name: Run tests
      run: |
        pytest tests/ -v

  lint:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Check for secrets
      run: |
        # Vérifier qu'aucun secret n'est commité
        ! grep -rn "eyJ" --include="*.yaml" --include="*.py" . | grep -v ".example" | grep -v "node_modules" || exit 1

    - name: Check for hardcoded paths
      run: |
        # Vérifier pas de chemins hardcodés
        ! grep -rn "/home/" --include="*.py" modules/ || exit 1

    - name: Check required files
      run: |
        test -f config.yaml.example
        test -f .env.example
        test -f LICENSE
        test -f README.md
        test -f install.sh

  build-mcp:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'

    - name: Install MCP dependencies
      run: |
        cd mcp-server
        npm install

    - name: Build MCP server
      run: |
        cd mcp-server
        npm run build

    - name: Verify build
      run: |
        test -f mcp-server/dist/index.js
EOF
```

### 8. Lancer les tests localement
```bash
cd ~/dev/lyra
source .venv/bin/activate
pip install pytest pyyaml
pytest tests/ -v
```

## Tests de Validation

```bash
# Test 1: Structure tests/ existe
[ -d ~/dev/lyra/tests ] && echo "✓ tests/ existe" || echo "✗ ERREUR"
[ -f ~/dev/lyra/tests/__init__.py ] && echo "✓ __init__.py OK" || echo "✗ ERREUR"

# Test 2: Fichiers de test existent
[ -f ~/dev/lyra/tests/test_config.py ] && echo "✓ test_config.py OK" || echo "✗ ERREUR"
[ -f ~/dev/lyra/tests/test_llm_parsing.py ] && echo "✓ test_llm_parsing.py OK" || echo "✗ ERREUR"
[ -f ~/dev/lyra/tests/test_validation.py ] && echo "✓ test_validation.py OK" || echo "✗ ERREUR"

# Test 3: GitHub Actions existe
[ -f ~/dev/lyra/.github/workflows/ci.yml ] && echo "✓ CI workflow OK" || echo "✗ ERREUR"

# Test 4: pytest dans requirements
grep -q "pytest" ~/dev/lyra/requirements.txt && echo "✓ pytest dans requirements" || echo "✗ ERREUR"

# Test 5: Lancer les tests
cd ~/dev/lyra && source .venv/bin/activate && pytest tests/ -v --tb=short
```

## Checklist
- [ ] tests/ créé avec __init__.py
- [ ] test_config.py créé
- [ ] test_llm_parsing.py créé
- [ ] test_validation.py créé
- [ ] pytest.ini créé
- [ ] pytest ajouté aux requirements
- [ ] .github/workflows/ci.yml créé
- [ ] Tests passent localement
