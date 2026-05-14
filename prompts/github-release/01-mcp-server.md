# Phase 1 : Intégrer le MCP Server

## Objectif
Copier le MCP server fedora-agents dans le repo Lyra pour le rendre autonome.

## Actions

### 1. Copier le code source
```bash
cd ~/dev/lyra

# Copier le MCP server
cp -r ~/dev/fedora-setup/scripts/agents/mcp-server .

# Vérifier la structure
ls -la mcp-server/
```

### 2. Nettoyer les fichiers inutiles
```bash
cd mcp-server

# Supprimer node_modules (sera recréé)
rm -rf node_modules

# Supprimer le build existant
rm -rf dist

# Vérifier
ls -la
```

### 3. Tester la compilation
```bash
cd ~/dev/lyra/mcp-server
npm install
npm run build

# Vérifier que dist/ est créé
ls -la dist/
```

## Tests de Validation

```bash
# Test 1: Dossier existe
[ -d ~/dev/lyra/mcp-server ] && echo "✓ mcp-server existe" || echo "✗ ERREUR"

# Test 2: package.json présent
[ -f ~/dev/lyra/mcp-server/package.json ] && echo "✓ package.json OK" || echo "✗ ERREUR"

# Test 3: Build réussi
[ -f ~/dev/lyra/mcp-server/dist/index.js ] && echo "✓ Build OK" || echo "✗ ERREUR"

# Test 4: Tester le serveur
cd ~/dev/lyra/mcp-server
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | node dist/index.js | head -1
```

## Checklist
- [ ] mcp-server/ copié
- [ ] node_modules supprimé
- [ ] npm install réussi
- [ ] npm run build réussi
- [ ] dist/index.js existe
