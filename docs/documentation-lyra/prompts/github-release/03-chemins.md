# Phase 3 : Généralisation des Chemins

## Objectif
Remplacer tous les chemins hardcodés /home/amineutron par des chemins configurables.

## Fichiers à Modifier

### 1. modules/mcp.py

Trouver la ligne avec le chemin hardcodé (vers ligne 35) et modifier :

**Avant:**
```python
server_path: str = "/home/amineutron/dev/fedora-setup/scripts/agents/mcp-server/dist/index.js"
```

**Après:**
```python
def __init__(
    self,
    server_path: str = None,
    timeout: int = 120
):
    # Import du config loader
    from modules.config import get_mcp_server_path

    # Chemin par défaut: MCP server intégré
    if server_path is None:
        server_path = get_mcp_server_path()

    self.server_path = Path(server_path)
    self.timeout = timeout

    # Vérifier que le fichier existe
    if not self.server_path.exists():
        raise FileNotFoundError(f"MCP server not found: {self.server_path}")
```

### 2. modules/n8n.py (lignes ~240-244)

**Avant:**
```python
FALLBACK_COMMANDS = {
    "vm_clone": "/home/amineutron/dev/fedora-setup/scripts/kvm/kvm-clone.sh ...",
    "vm_clone_system": "/home/amineutron/dev/fedora-setup/scripts/agents/vm-controller/...",
    "backup_create": "/home/amineutron/dev/fedora-setup/scripts/agents/backup-manager/...",
    "backup_restore": "/home/amineutron/dev/fedora-setup/scripts/agents/backup-manager/...",
}
```

**Après:**
```python
from modules.config import get_scripts_base_path

def get_fallback_commands():
    """Génère les commandes fallback avec le bon chemin."""
    base = get_scripts_base_path()
    return {
        "vm_clone": f"sudo {base}/kvm/kvm-clone.sh {{source_vm}} {{new_vm_name}} --start",
        "vm_clone_system": f"sudo {base}/vm-controller/vm-clone-system.sh {{name}} --memory {{memory}} --cpus {{cpus}}",
        "backup_create": f"sudo {base}/backup-manager/backup-manager.sh create --type {{type}}",
        "backup_restore": f"sudo {base}/backup-manager/backup-manager.sh restore --type {{type}} --identifier {{identifier}}",
    }

# Initialiser au chargement du module
FALLBACK_COMMANDS = get_fallback_commands()
```

### 3. Vérifier main.py et autres fichiers

Chercher d'autres occurrences :
```bash
grep -rn "/home/amineutron" ~/dev/lyra --include="*.py" --include="*.yaml" --include="*.sh"
```

Remplacer chaque occurrence trouvée par une variable configurable ou un chemin relatif.

## Tests de Validation

```bash
# Test 1: Pas de /home/amineutron dans le code Python
grep -r "/home/amineutron" ~/dev/lyra/modules/*.py && echo "✗ CHEMIN HARDCODÉ!" || echo "✓ Pas de chemin hardcodé"

# Test 2: Pas dans config.yaml.example
grep -r "/home/amineutron" ~/dev/lyra/config.yaml.example && echo "✗ CHEMIN HARDCODÉ!" || echo "✓ Config OK"

# Test 3: Pas dans les scripts
grep -r "/home/amineutron" ~/dev/lyra/scripts/*.sh 2>/dev/null && echo "✗ CHEMIN HARDCODÉ!" || echo "✓ Scripts OK"

# Test 4: Lyra démarre toujours
cd ~/dev/lyra && source .venv/bin/activate && python -c "from modules.mcp import MCPClient; print('✓ MCP import OK')"

# Test 5: Config loader fonctionne
cd ~/dev/lyra && python -c "from modules.config import get_mcp_server_path, get_scripts_base_path; print(f'MCP: {get_mcp_server_path()}'); print(f'Scripts: {get_scripts_base_path()}')"
```

## Chemins à utiliser

| Ancien chemin | Nouveau chemin |
|---------------|----------------|
| `/home/amineutron/dev/fedora-setup/scripts/agents/mcp-server/dist/index.js` | `./mcp-server/dist/index.js` (relatif au projet) |
| `/home/amineutron/dev/fedora-setup/scripts/kvm/` | `~/.local/share/lyra/scripts/kvm/` ou variable SCRIPTS_BASE_PATH |
| `/home/amineutron/dev/fedora-setup/scripts/agents/vm-controller/` | `~/.local/share/lyra/scripts/vm-controller/` |
| `/home/amineutron/dev/fedora-setup/scripts/agents/backup-manager/` | `~/.local/share/lyra/scripts/backup-manager/` |

## Note importante

Les scripts externes (kvm-clone.sh, backup-manager.sh, etc.) doivent être :
1. Soit copiés dans `~/.local/share/lyra/scripts/` lors de l'installation
2. Soit référencés via la variable d'environnement `SCRIPTS_BASE_PATH`

Documenter cela dans le README.

## Checklist
- [ ] modules/mcp.py modifié (chemin relatif)
- [ ] modules/n8n.py modifié (chemin via env/défaut)
- [ ] modules/config.py créé avec get_mcp_server_path() et get_scripts_base_path()
- [ ] Aucun /home/amineutron dans *.py
- [ ] Aucun /home/amineutron dans *.yaml
- [ ] Lyra démarre sans erreur
