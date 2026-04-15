#!/usr/bin/env bash
# build/build_app.sh — build Forest.app with PyInstaller
#
# Prerequisites:
#   source ../venv/bin/activate
#   pip install pyinstaller
#
# Output: dist/Forest.app
# To distribute: drag dist/Forest.app to Applications or zip it.

set -e

FOREST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${FOREST_DIR}"

echo "=== Forest CUS — macOS App Builder ==="
echo "  Project root: ${FOREST_DIR}"
echo ""

# Activate venv
source venv/bin/activate

# Install PyInstaller if not present
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "  Installing PyInstaller…"
    pip install pyinstaller --quiet
fi

echo "  Building Forest.app…"

pyinstaller \
    --name "Forest" \
    --windowed \
    --onedir \
    --noconfirm \
    --icon build/forest_icon.icns \
    --osx-bundle-identifier "com.forest.cus" \
    --add-data "build/ForestLauncher.py:." \
    build/ForestLauncher.py 2>&1 | tail -20

# Inject a note about where the project lives
# (the .app reads PROJECT_DIR relative to its bundle path)
if [[ -d "dist/Forest.app" ]]; then
    echo ""
    echo "  ✓  Built: dist/Forest.app"
    echo ""
    echo "  To distribute:"
    echo "    1. Copy dist/Forest.app to the user's Applications folder"
    echo "    2. The user must have run 'bash setup.sh' first"
    echo "    3. The app reads ~/Forest/venv — so the project must be at ~/Forest"
    echo ""
    echo "  Notes:"
    echo "    - First macOS run may require: System Settings → Security → Open Anyway"
    echo "    - To skip Gatekeeper for testing: xattr -dr com.apple.quarantine dist/Forest.app"
else
    echo "  Build failed — check output above"
    exit 1
fi
