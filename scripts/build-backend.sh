#!/usr/bin/env bash
# Gera o executavel do backend (Linux) em frontend/backend-bin/vortex-backend
set -e
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ/backend"
[ -d venv ] || python3 -m venv venv
./venv/bin/pip install -r requirements.txt
./venv/bin/pyinstaller --noconfirm --onefile --name vortex-backend --distpath "$RAIZ/frontend/backend-bin" app.py
echo "OK: $RAIZ/frontend/backend-bin/vortex-backend"
