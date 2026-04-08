#!/usr/bin/env bash
set -euo pipefail

APP_NAME="ContractAutomation"
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$ROOT_DIR"

if [[ -n "${RELEASE_VERSION:-}" ]]; then
  VERSION="$RELEASE_VERSION"
elif git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  VERSION="$(git describe --tags --always --dirty 2>/dev/null || echo dev)"
else
  VERSION="dev"
fi

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
RELEASE_DIR="$ROOT_DIR/releases/macos"
mkdir -p "$RELEASE_DIR"

echo "[release] VERSION=$VERSION"
echo "[release] Building .app and .dmg"
"$ROOT_DIR/packaging/macos/build_dmg.sh"

APP_PATH="$ROOT_DIR/dist/$APP_NAME.app"
DMG_PATH="$ROOT_DIR/dist/$APP_NAME.dmg"
ZIP_NAME="${APP_NAME}_${VERSION}_${TIMESTAMP}_macos_app.zip"
DMG_NAME="${APP_NAME}_${VERSION}_${TIMESTAMP}_macos.dmg"

if [[ ! -d "$APP_PATH" ]]; then
  echo "[error] Missing app bundle: $APP_PATH"
  exit 1
fi

if [[ ! -f "$DMG_PATH" ]]; then
  echo "[error] Missing dmg file: $DMG_PATH"
  exit 1
fi

echo "[release] Archiving app bundle"
rm -f "$RELEASE_DIR/$ZIP_NAME"
/usr/bin/ditto -c -k --sequesterRsrc --keepParent "$APP_PATH" "$RELEASE_DIR/$ZIP_NAME"

cp "$DMG_PATH" "$RELEASE_DIR/$DMG_NAME"

cat <<EOF
[done] Release artifacts created:
- $RELEASE_DIR/$ZIP_NAME
- $RELEASE_DIR/$DMG_NAME
EOF
