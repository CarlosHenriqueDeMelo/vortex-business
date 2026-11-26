#!/usr/bin/env bash
# Cria o atalho "Vortex Business" no menu de aplicativos e na area de trabalho.
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
chmod +x "$RAIZ/scripts/iniciar-vortex.sh"
ARQ="$HOME/.local/share/applications/vortex-business.desktop"
mkdir -p "$(dirname "$ARQ")"
cat > "$ARQ" <<DESK
[Desktop Entry]
Type=Application
Name=Vortex Business
Comment=ERP Vortex Business
Exec=$RAIZ/scripts/iniciar-vortex.sh
Icon=$(ls "$RAIZ"/frontend/src/assets/*.png 2>/dev/null | head -1)
Terminal=false
Categories=Office;
DESK
chmod +x "$ARQ"
DESKTOP="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
[ -d "$DESKTOP" ] && cp "$ARQ" "$DESKTOP/" && chmod +x "$DESKTOP/vortex-business.desktop"
echo "Atalho criado. Procure 'Vortex Business' no menu de aplicativos."
