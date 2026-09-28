#!/bin/bash
# Build a standalone macOS .app for Ecos Learning Notes.
# Run this ON A MAC, in the same folder as ecos_learning_notes.py.

set -e

echo "Installing PyInstaller (if not already installed)..."
python3 -m pip install --upgrade pyinstaller

echo "Building Ecos Learning Notes.app ..."
python3 -m PyInstaller \
    --name "Ecos Learning Notes" \
    --windowed \
    --onefile \
    --noconfirm \
    ecos_learning_notes.py

echo ""
echo "Done. Find your app at: dist/Ecos Learning Notes.app"
echo "You can drag that into /Applications."
echo ""
echo "NOTE: since the app isn't signed with an Apple Developer certificate,"
echo "macOS Gatekeeper will block it the first time you open it. To run it:"
echo "  Right-click (or Control-click) the app -> Open -> Open, just once."
