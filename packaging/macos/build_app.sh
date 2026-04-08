#!/usr/bin/env bash
set -euo pipefail

APP_NAME="ContractAutomation"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

ICON_PATH="$ROOT_DIR/assets/app.icns"
ICON_ARGS=()
if [[ -f "$ICON_PATH" ]]; then
  ICON_ARGS=(--icon "$ICON_PATH")
else
  echo "[info] Icon not found at assets/app.icns. Building without custom icon."
fi

echo "[build] Cleaning previous outputs"
rm -rf build dist

echo "[build] Building macOS .app with PyInstaller"
python -m PyInstaller \
  --noconfirm \
  --clean \
  --windowed \
  --name "$APP_NAME" \
  "${ICON_ARGS[@]}" \
  --add-data "templates_storage:templates_storage" \
  --add-data "exports:exports" \
  src/main.py

echo "[done] App bundle created: dist/$APP_NAME.app"
