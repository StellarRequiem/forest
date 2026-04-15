#!/usr/bin/env bash
# build/build_app.sh — produce Forest.app
#
# Run from the Forest project root:
#   cd ~/Forest
#   bash build/build_app.sh
#
# Output: dist/Forest.app
# To install: cp -r dist/Forest.app /Applications/
# To distribute: zip -r Forest.zip dist/Forest.app

set -e

FOREST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${FOREST_DIR}"

BOLD="\033[1m"; GREEN="\033[32m"; YELLOW="\033[33m"; RED="\033[31m"; RESET="\033[0m"

echo -e "${BOLD}"
echo "  ╔══════════════════════════════════════╗"
echo "  ║   🌲  Forest CUS — App Builder        ║"
echo "  ╚══════════════════════════════════════╝"
echo -e "${RESET}"

# ── Activate venv ─────────────────────────────────────────────────────────────
if [[ ! -f "venv/bin/activate" ]]; then
    echo -e "${RED}  ✗ venv not found. Run setup.sh first.${RESET}"
    exit 1
fi
source venv/bin/activate
echo -e "${GREEN}  ✓ venv active ($(python3 --version))${RESET}"

# ── PyInstaller check ─────────────────────────────────────────────────────────
if ! python3 -c "import PyInstaller" 2>/dev/null; then
    echo "  Installing PyInstaller…"
    pip install pyinstaller --quiet
fi
echo -e "${GREEN}  ✓ PyInstaller $(pyinstaller --version)${RESET}"

# ── Clean previous build ──────────────────────────────────────────────────────
echo ""
echo "  Cleaning previous build…"
rm -rf dist/Forest dist/Forest.app build/Forest build/__pycache__
echo -e "${GREEN}  ✓ Clean${RESET}"

# ── Build ─────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}  Building Forest.app…${RESET}"
echo "  (This takes ~60 seconds)"
echo ""

pyinstaller \
    --noconfirm \
    --distpath dist \
    --workpath build/pyinstaller_work \
    build/Forest.spec 2>&1 | grep -v "^$" | grep -v "^INFO:" | tail -30

if [[ ! -d "dist/Forest.app" ]]; then
    echo -e "${RED}  ✗ Build failed — check output above${RESET}"
    exit 1
fi

# ── Strip quarantine (for local testing) ─────────────────────────────────────
xattr -cr dist/Forest.app 2>/dev/null || true

# ── Result ────────────────────────────────────────────────────────────────────
APP_SIZE=$(du -sh dist/Forest.app | cut -f1)
echo ""
echo -e "${GREEN}${BOLD}  ✓ Built: dist/Forest.app (${APP_SIZE})${RESET}"
echo ""
echo "  Install to Applications:"
echo "    cp -r dist/Forest.app /Applications/"
echo ""
echo "  Or open right now:"
echo "    open dist/Forest.app"
echo ""
echo "  Notes:"
echo "  • The app manages Forest CUS using the venv at: ${FOREST_DIR}/venv"
echo "  • Streamlit and Ollama are NOT bundled — they run via your venv"
echo "  • First macOS open may need: System Settings → Privacy & Security → Open Anyway"
echo ""
