@echo off
REM Build a standalone Windows .exe for Ecos Learning Notes.
REM Run this ON WINDOWS, in the same folder as ecos_learning_notes.py.

echo Installing PyInstaller (if not already installed)...
python -m pip install --upgrade pyinstaller

echo Building Ecos Learning Notes.exe ...
python -m PyInstaller ^
    --name "Ecos Learning Notes" ^
    --windowed ^
    --onefile ^
    --noconfirm ^
    ecos_learning_notes.py

echo.
echo Done. Find your app at: dist\Ecos Learning Notes.exe
echo You can copy that .exe anywhere, or pin it to your taskbar/Start menu.
echo.
echo NOTE: since the .exe isn't signed with a code-signing certificate,
echo Windows SmartScreen may show a warning the first time you run it.
echo Click "More info" then "Run anyway" to proceed.
pause
