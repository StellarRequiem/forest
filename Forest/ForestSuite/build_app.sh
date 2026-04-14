#!/bin/bash
echo "Building Forest Trainer Suite as macOS .app..."

pip install pyinstaller

pyinstaller --onefile --windowed \
  --name "ForestTrainerSuite" \
  --add-data "trainer_suite_launcher.py:." \
  --hidden-import tkinter \
  trainer_suite_launcher.py

echo "Build complete. .app is in dist/ForestTrainerSuite.app"
echo "You can distribute the .app file directly."
