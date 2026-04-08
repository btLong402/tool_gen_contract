#!/usr/bin/env bash
set -euo pipefail

APP_NAME="ContractAutomation"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

APP_PATH="dist/$APP_NAME.app"
DMG_PATH="dist/$APP_NAME.dmg"
STAGING_DIR="dist/dmg_staging"

if [[ ! -d "$APP_PATH" ]]; then
  echo "[info] App bundle not found. Building app first..."
  "${ROOT_DIR}/packaging/macos/build_app.sh"
fi

echo "[build] Preparing staging directory"
rm -rf "$STAGING_DIR"
mkdir -p "$STAGING_DIR"
cp -R "$APP_PATH" "$STAGING_DIR/"
ln -s /Applications "$STAGING_DIR/Applications"

echo "[build] Creating dmg with hdiutil"
rm -f "$DMG_PATH"
hdiutil create \
  -volname "$APP_NAME" \
  -srcfolder "$STAGING_DIR" \
  -ov \
  -format UDZO \
  "$DMG_PATH"

echo "[done] DMG created: $DMG_PATH"
