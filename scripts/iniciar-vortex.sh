#!/usr/bin/env bash
# Inicia o backend (Flask) e o desktop (Electron) do Vortex Business.
# Fecha o backend automaticamente quando o app for fechado.
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
cd "$RAIZ/backend" || exit 1

if [ ! -d venv ]; then
  python3 -m venv venv && ./venv/bin/pip install -r requirements.txt
fi
if [ ! -d "$RAIZ/frontend/node_modules" ]; then
  (cd "$RAIZ/frontend" && npm install)
fi

# libera a porta 5000 se sobrou algum backend antigo
fuser -k 5000/tcp >/dev/null 2>&1

./venv/bin/python app.py >/tmp/vortex-backend.log 2>&1 &
BACK=$!
trap 'kill $BACK 2>/dev/null' EXIT

sleep 3
cd "$RAIZ/frontend" && npm start
