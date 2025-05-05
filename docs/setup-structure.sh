mkdir -p .vscode
mkdir -p media
mkdir -p out
mkdir -p src/chat
mkdir -p src/agent/steps
mkdir -p src/parser
mkdir -p src/utils
mkdir -p test
mkdir -p debug_chunks
mkdir -p scripts

# Python backend for embedding + LanceDB (Epic 2.3)
mkdir -p backend
touch backend/__init__.py
touch backend/lance_store.py
touch backend/load_chunks.py
touch backend/search.py

# Script CLI
touch scripts/parse-and-chunk.ts

# Top-level files
touch package.json
touch tsconfig.json
touch README.md

echo "✅ Project structure created inside ai-code-assistant/"
