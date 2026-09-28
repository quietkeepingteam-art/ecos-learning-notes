# Ecos Learning Notes

A simple day-by-day note-taking desktop app for macOS and Windows. Write a
note for each day, highlight the important parts, doodle on a scribble
canvas, jump straight to every other note that mentions a term, and quiz
yourself on what you wrote — all from one lightweight Python app.

## Features

- **Notes by day** — every day's note is saved as a plain text file
  (`day1.txt`, `day2.txt`, `day3.txt`, ...) so you can open them in any
  text editor, back them up, or sync the folder however you like.
- **Highlighting** — select text and mark it like a highlighter pen.
  Highlights are stored separately (`day1.highlights.json`) so the `.txt`
  files themselves always stay plain, portable text.
- **Free scribble** — a second tab per day with a blank canvas for
  freehand doodles or diagrams, saved as `day1.scribble.json`.
- **Search across all notes** — right-click (or Ctrl-click) any word to
  see every day that mentions it, with a jump-to-line shortcut.
- **Quiz Me** — copies the current day's notes plus a ready-made quiz
  prompt to your clipboard and opens claude.ai in your browser, so you
  can paste it in and get quizzed using your existing claude.ai access
  — no API key, no extra cost.

## Requirements

- Python 3.8 or newer.
- No extra packages to install — the app only uses Python's standard
  library (`tkinter`, which ships with the official installers from
  [python.org](https://python.org) for both macOS and Windows).
- An internet connection and a claude.ai account (free or paid) if you
  want to use the Quiz Me feature. Everything else works fully offline.

## Getting started

1. Install Python 3 if you don't already have it, from
   [python.org/downloads](https://www.python.org/downloads/). Use the
   default installer options — they include tkinter.
2. Download `ecos_learning_notes.py`.
3. Open a terminal (macOS: Terminal; Windows: Command Prompt or
   PowerShell) in the folder where you saved the file, and run:

   ```
   python3 ecos_learning_notes.py
   ```

   On Windows this may instead be `python ecos_learning_notes.py`,
   depending on how Python was installed.

That's it — the app window opens and you're ready to write.

## Where your notes are stored

All notes and their highlights/scribbles are saved automatically in an
`EcosLearningNotes` folder in your home directory:

- macOS: `/Users/<you>/EcosLearningNotes/`
- Windows: `C:\Users\<you>\EcosLearningNotes\`

Inside, each day gets up to three files:

| File | Contents |
|---|---|
| `dayN.txt` | The plain-text note itself |
| `dayN.highlights.json` | Which parts of the note are highlighted |
| `dayN.scribble.json` | The freehand scribble for that day |

## Using the app

- **+ New Day** — creates the next numbered day and switches to it.
- **Notes tab** — write freely; your note autosaves about a second
  after you stop typing.
- **Highlight / Clear Highlight** — select text first, then click.
- **Scribble tab** — click and drag to draw; use *Pen Color* to change
  color and *Clear Scribble* to start over.
- **Right-click a word → "Find '...' in all notes"** — lists every day
  that mentions that word; double-click a result to jump straight to it.
- **Quiz Me** — copies that day's notes and a quiz prompt to your
  clipboard and opens claude.ai in your browser. Paste (Cmd+V / Ctrl+V)
  into the chat and send it, and Claude will quiz you right there. This
  uses your normal claude.ai access (free or paid) — it does not call
  the paid Anthropic API and does not require any key or setup.

## Notes on the scribble feature

Scribbles are stored as the actual points you draw (a small vector
format), not as an image, so files stay tiny and there's no image
library to install. One side effect: when a scribble is reloaded, it's
redrawn as one smooth curve through all its points, so it can look very
slightly smoother than the exact strokes you originally drew.

## Building a standalone app (no Python required to run it)

If you'd rather have a double-click app instead of running a Python
script, you can package it with [PyInstaller](https://pyinstaller.org/).
This bundles Python itself into the app, so whoever runs it doesn't
need Python installed at all.

**Important:** PyInstaller packages for whatever operating system it
runs on — it can't cross-build. So you build the `.app` on a Mac and
the `.exe` on a Windows PC (or a Windows VM).

### macOS

1. Make sure `ecos_learning_notes.py` and `build_mac.sh` are in the
   same folder.
2. In Terminal, in that folder, run:
   ```
   chmod +x build_mac.sh
   ./build_mac.sh
   ```
3. Your app appears at `dist/Ecos Learning Notes.app`. Drag it into
   `/Applications` if you'd like.
4. Since it isn't signed with an Apple Developer certificate,
   Gatekeeper will block it the first time. Right-click the app →
   **Open** → **Open** (only needed once).

### Windows

1. Make sure `ecos_learning_notes.py` and `build_windows.bat` are in
   the same folder.
2. Double-click `build_windows.bat` (or run it from Command Prompt).
3. Your app appears at `dist\Ecos Learning Notes.exe`.
4. Since it isn't code-signed, SmartScreen may warn you the first time
   you run it — click **More info** → **Run anyway**.

### Notes

- The resulting `.app` / `.exe` is fairly large (often 30–60 MB)
  because it bundles a full Python runtime. That's normal.
- Your notes still save to `~/EcosLearningNotes` (or
  `C:\Users\<you>\EcosLearningNotes`) exactly as before — packaging
  doesn't change where anything is stored.
- If you update `ecos_learning_notes.py` later, just re-run the build
  script to get a fresh app.



- **`ModuleNotFoundError: No module named 'tkinter'`** (mostly a Linux
  issue) — install your distro's tkinter package, e.g.
  `sudo apt install python3-tk` on Debian/Ubuntu. macOS and Windows
  installers from python.org include tkinter already.
- **Quiz Me doesn't open a browser tab** — your default browser may be
  blocking automatic tab opening; just go to
  [claude.ai](https://claude.ai) yourself and paste (Cmd+V / Ctrl+V) —
  the notes and prompt are already on your clipboard.
