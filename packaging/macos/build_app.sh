#!/usr/bin/env bash
set -euo pipefail

APP_NAME="ContractAutomation"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

ICON_PATH="$ROOT_DIR/assets/app.icns"
HAS_ICON=0
if [[ -f "$ICON_PATH" ]]; then
  HAS_ICON=1
else
  echo "[info] Icon not found at assets/app.icns. Building without custom icon."
fi

echo "[build] Cleaning previous outputs"
rm -rf build dist

# Ensure data directories exist even when empty and git-ignored.
mkdir -p templates_storage exports

echo "[build] Building macOS .app with PyInstaller"
if [[ "$HAS_ICON" -eq 1 ]]; then
  python -m PyInstaller \
    --noconfirm \
    --clean \
    --windowed \
    --name "$APP_NAME" \
    --icon "$ICON_PATH" \
    --add-data "templates_storage:templates_storage" \
    --add-data "exports:exports" \
    src/main.py
else
  python -m PyInstaller \
    --noconfirm \
    --clean \
    --windowed \
    --name "$APP_NAME" \
    --add-data "templates_storage:templates_storage" \
    --add-data "exports:exports" \
    src/main.py
fi

echo "[done] App bundle created: dist/$APP_NAME.app"
