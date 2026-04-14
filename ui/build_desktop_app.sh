#!/bin/bash
# Build Forest Desktop Controller as macOS .app

echo "🌲 Building Forest Desktop Controller..."
echo "This will compile all 8 modules into a native macOS application"

cd "$(cd "$(dirname "$0")/.." && pwd)"

# Activate venv
source venv/bin/activate

# Clean old builds
rm -rf ui/build ui/dist ui/*.spec

# Build with PyInstaller
python3 -m PyInstaller \
  --onedir \
  --windowed \
  --name "ForestController" \
  --icon=ui/assets/forest_icon.icns \
  --add-data "ui/forest_desktop_controller.py:." \
  --add-data "agents:agents" \
  --add-data "core:core" \
  --hidden-import=PyQt6 \
  --hidden-import=PyQt6.QtCore \
  --hidden-import=PyQt6.QtGui \
  --hidden-import=PyQt6.QtWidgets \
  --hidden-import=PyQt6.QtChart \
  --hidden-import=psutil \
  ui/forest_desktop_controller.py

echo ""
echo "✅ Build complete!"
echo "📍 Location: $(pwd)/ui/dist/ForestController.app"
echo ""
echo "To launch:"
echo "  open $(pwd)/ui/dist/ForestController.app"
echo ""
echo "Or directly:"
echo "  $(pwd)/ui/dist/ForestController.app/Contents/MacOS/ForestController"
