#!/usr/bin/env python3
"""
Ecos Learning Notes — a simple day-based note-taking desktop app.

Works on both macOS and Windows (and Linux) since it only uses Python's
standard library — no pip installs required.

FEATURES
  - Notes are saved by day as plain text files: day1.txt, day2.txt, ...
    inside a "EcosLearningNotes" folder in your home directory.
  - Highlight text (like a highlighter pen) — saved alongside the .txt
    file as day1.highlights.json, so the .txt itself stays plain text.
  - Freehand "Scribble" tab per day for doodles/diagrams — saved as
    day1.scribble.json (vector strokes, so no image library is needed).
  - Right-click (or Ctrl-click on some Mac trackpads) any word to see
    every note across every day that mentions it.
  - Optional "Quiz Me" button that asks Claude to generate a short quiz
    from the current day's notes. Requires an Anthropic API key (see
    Settings > Set API Key, or set the ANTHROPIC_API_KEY environment
    variable). This feature needs an internet connection; everything
    else works fully offline.

RUN
    python3 ecos_learning_notes.py

  macOS and Windows both ship Python with tkinter included when you
  install Python from python.org, so nothing else needs installing.
"""

import json
import os
import re
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, colorchooser

# ---------------------------------------------------------------------------
# Storage helpers
# ---------------------------------------------------------------------------

NOTES_DIR = os.path.join(os.path.expanduser("~"), "EcosLearningNotes")
HIGHLIGHT_COLOR = "#fff176"

os.makedirs(NOTES_DIR, exist_ok=True)


def list_day_numbers():
    days = []
    for fname in os.listdir(NOTES_DIR):
        m = re.match(r"^day(\d+)\.txt$", fname)
        if m:
            days.append(int(m.group(1)))
    return sorted(days)


def txt_path(day_num):
    return os.path.join(NOTES_DIR, f"day{day_num}.txt")


def highlights_path(day_num):
    return os.path.join(NOTES_DIR, f"day{day_num}.highlights.json")


def scribble_path(day_num):
    return os.path.join(NOTES_DIR, f"day{day_num}.scribble.json")


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

class EcosLearningNotesApp:
    def __init__(self, root):
        self.root = root
        root.title("Ecos Learning Notes")
        root.geometry("1050x680")

        self.current_day = None
        self.current_stroke = []
        self.pen_color = "#1f1c19"
        self._save_after_id = None

        self._build_ui()
        self._refresh_day_list()

        days = list_day_numbers()
        if days:
            self._select_day(days[-1])

    # ------------------------------------------------------------- UI ----

    def _build_ui(self):
        # Sidebar
        sidebar = ttk.Frame(self.root, width=200)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)
        ttk.Button(sidebar, text="+ New Day", command=self._new_day).pack(fill="x", padx=8, pady=8)
        self.day_listbox = tk.Listbox(sidebar, exportselection=False)
        self.day_listbox.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self.day_listbox.bind("<<ListboxSelect>>", self._on_day_select)
        ttk.Label(sidebar, text=f"Saved in:\n{NOTES_DIR}", wraplength=180,
                  foreground="#888", font=("Helvetica", 9)).pack(padx=8, pady=(0, 10))

        # Main area
        main = ttk.Frame(self.root)
        main.pack(side="left", fill="both", expand=True)

        toolbar = ttk.Frame(main)
        toolbar.pack(fill="x", padx=8, pady=6)
        self.title_label = ttk.Label(toolbar, text="No day selected", font=("Helvetica", 13, "bold"))
        self.title_label.pack(side="left")

        self.status_label = ttk.Label(toolbar, text="", foreground="#888")
        self.status_label.pack(side="right", padx=8)
        ttk.Button(toolbar, text="Quiz Me", command=self._quiz_me).pack(side="right", padx=2)
        ttk.Button(toolbar, text="Clear Highlight", command=self._clear_highlight).pack(side="right", padx=2)
        ttk.Button(toolbar, text="Highlight", command=self._apply_highlight).pack(side="right", padx=2)

        # Notebook: Notes tab / Scribble tab
        self.notebook = ttk.Notebook(main)
        self.notebook.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        notes_frame = ttk.Frame(self.notebook)
        self.notebook.add(notes_frame, text="Notes")
        self.text = tk.Text(notes_frame, wrap="word", undo=True, font=("Helvetica", 13),
                             borderwidth=0, highlightthickness=0)
        self.text.pack(fill="both", expand=True)
        self.text.tag_configure("highlight", background=HIGHLIGHT_COLOR)
        self.text.bind("<<Modified>>", self._on_text_modified)
        self.text.bind("<Button-3>", self._on_right_click)          # Windows / Linux right-click
        self.text.bind("<Button-2>", self._on_right_click)          # some Mac mice
        self.text.bind("<Control-Button-1>", self._on_right_click)  # Mac trackpad ctrl-click

        scribble_frame = ttk.Frame(self.notebook)
        self.notebook.add(scribble_frame, text="Scribble")
        scribble_tools = ttk.Frame(scribble_frame)
        scribble_tools.pack(fill="x")
        ttk.Button(scribble_tools, text="Clear Scribble", command=self._clear_scribble).pack(side="left", padx=4, pady=4)
        ttk.Button(scribble_tools, text="Pen Color", command=self._choose_pen_color).pack(side="left", padx=4, pady=4)
        self.canvas = tk.Canvas(scribble_frame, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self._scribble_start)
        self.canvas.bind("<B1-Motion>", self._scribble_move)
        self.canvas.bind("<ButtonRelease-1>", self._scribble_end)

        self.scribble_strokes = []  # list of {"color": str, "points": [x1,y1,x2,y2,...]}

    # --------------------------------------------------------- Day list --

    def _refresh_day_list(self):
        self.day_listbox.delete(0, "end")
        for n in list_day_numbers():
            self.day_listbox.insert("end", f"Day {n}")

    def _new_day(self):
        days = list_day_numbers()
        next_num = (max(days) + 1) if days else 1
        with open(txt_path(next_num), "w", encoding="utf-8") as f:
            f.write("")
        self._refresh_day_list()
        self._select_day(next_num)

    def _on_day_select(self, event):
        sel = self.day_listbox.curselection()
        if not sel:
            return
        label = self.day_listbox.get(sel[0])
        day_num = int(label.replace("Day ", ""))
        self._select_day(day_num)

    def _select_day(self, day_num):
        if self.current_day is not None:
            self._save_current(force=True)

        self.current_day = day_num
        self.title_label.config(text=f"Day {day_num}")

        # Load text
        content = ""
        if os.path.exists(txt_path(day_num)):
            with open(txt_path(day_num), "r", encoding="utf-8") as f:
                content = f.read()
        self.text.edit_modified(False)
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)

        # Load highlights
        if os.path.exists(highlights_path(day_num)):
            try:
                with open(highlights_path(day_num), "r", encoding="utf-8") as f:
                    ranges = json.load(f)
                for r in ranges:
                    self.text.tag_add("highlight", r["start"], r["end"])
            except Exception:
                pass
        self.text.edit_modified(False)

        # Select in sidebar
        for i in range(self.day_listbox.size()):
            if self.day_listbox.get(i) == f"Day {day_num}":
                self.day_listbox.selection_clear(0, "end")
                self.day_listbox.selection_set(i)
                break

        # Load scribble
        self.canvas.delete("all")
        self.scribble_strokes = []
        if os.path.exists(scribble_path(day_num)):
            try:
                with open(scribble_path(day_num), "r", encoding="utf-8") as f:
                    self.scribble_strokes = json.load(f)
                for stroke in self.scribble_strokes:
                    pts = stroke["points"]
                    if len(pts) >= 4:
                        self.canvas.create_line(*pts, fill=stroke.get("color", "#1f1c19"),
                                                 width=2, smooth=True, capstyle="round")
            except Exception:
                pass

    # ------------------------------------------------------------ Save --

    def _on_text_modified(self, event):
        self.text.edit_modified(False)
        self.status_label.config(text="Saving...")
        if self._save_after_id:
            self.root.after_cancel(self._save_after_id)
        self._save_after_id = self.root.after(700, self._save_current)

    def _save_current(self, force=False):
        if self.current_day is None:
            return
        content = self.text.get("1.0", "end-1c")
        with open(txt_path(self.current_day), "w", encoding="utf-8") as f:
            f.write(content)

        # Save highlight ranges
        ranges = []
        tag_ranges = self.text.tag_ranges("highlight")
        for i in range(0, len(tag_ranges), 2):
            ranges.append({"start": str(tag_ranges[i]), "end": str(tag_ranges[i + 1])})
        with open(highlights_path(self.current_day), "w", encoding="utf-8") as f:
            json.dump(ranges, f)

        self.status_label.config(text="Saved")
        self.root.after(1200, lambda: self.status_label.config(text=""))

    def _save_scribble(self):
        if self.current_day is None:
            return
        with open(scribble_path(self.current_day), "w", encoding="utf-8") as f:
            json.dump(self.scribble_strokes, f)

    # ------------------------------------------------------- Highlight --

    def _apply_highlight(self):
        try:
            start = self.text.index("sel.first")
            end = self.text.index("sel.last")
        except tk.TclError:
            messagebox.showinfo("Highlight", "Select some text first.")
            return
        self.text.tag_add("highlight", start, end)
        self._save_current()

    def _clear_highlight(self):
        try:
            start = self.text.index("sel.first")
            end = self.text.index("sel.last")
            self.text.tag_remove("highlight", start, end)
        except tk.TclError:
            self.text.tag_remove("highlight", "1.0", "end")
        self._save_current()

    # ---------------------------------------------------------- Scribble

    def _scribble_start(self, event):
        self.current_stroke = [event.x, event.y]

    def _scribble_move(self, event):
        if not self.current_stroke:
            return
        x0, y0 = self.current_stroke[-2], self.current_stroke[-1]
        self.canvas.create_line(x0, y0, event.x, event.y, fill=self.pen_color,
                                 width=2, smooth=True, capstyle="round")
        self.current_stroke.extend([event.x, event.y])

    def _scribble_end(self, event):
        if len(self.current_stroke) >= 4:
            self.scribble_strokes.append({"color": self.pen_color, "points": self.current_stroke})
            self._save_scribble()
        self.current_stroke = []

    def _clear_scribble(self):
        if not messagebox.askyesno("Clear Scribble", "Clear the scribble for this day?"):
            return
        self.canvas.delete("all")
        self.scribble_strokes = []
        self._save_scribble()

    def _choose_pen_color(self):
        color = colorchooser.askcolor(color=self.pen_color)[1]
        if color:
            self.pen_color = color

    # -------------------------------------------------- Cross-note search

    def _on_right_click(self, event):
        index = self.text.index(f"@{event.x},{event.y}")
        word_start = self.text.index(f"{index} wordstart")
        word_end = self.text.index(f"{index} wordend")
        word = self.text.get(word_start, word_end).strip()
        word = re.sub(r"[^\w'-]", "", word)
        if not word:
            return
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label=f'Find "{word}" in all notes',
                          command=lambda: self._search_term(word))
        menu.tk_popup(event.x_root, event.y_root)

    def _search_term(self, term):
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        results = []  # list of (day_num, line_num, line_text)
        for day_num in list_day_numbers():
            p = txt_path(day_num)
            if not os.path.exists(p):
                continue
            with open(p, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, start=1):
                    if pattern.search(line):
                        results.append((day_num, line_num, line.strip()))

        win = tk.Toplevel(self.root)
        win.title(f'"{term}" across all notes')
        win.geometry("520x400")

        if not results:
            ttk.Label(win, text=f'No other mentions of "{term}" found.', padding=20).pack()
            return

        ttk.Label(win, text=f'{len(results)} mention(s) of "{term}":',
                  font=("Helvetica", 11, "bold"), padding=(12, 12, 12, 4)).pack(anchor="w")

        list_frame = ttk.Frame(win)
        list_frame.pack(fill="both", expand=True, padx=12, pady=(0, 12))
        listbox = tk.Listbox(list_frame)
        listbox.pack(side="left", fill="both", expand=True)
        scroll = ttk.Scrollbar(list_frame, command=listbox.yview)
        scroll.pack(side="right", fill="y")
        listbox.config(yscrollcommand=scroll.set)

        for day_num, line_num, line_text in results:
            snippet = line_text if len(line_text) <= 70 else line_text[:67] + "..."
            listbox.insert("end", f"Day {day_num} (line {line_num}):  {snippet}")

        def jump_to(evt):
            sel = listbox.curselection()
            if not sel:
                return
            day_num, line_num, _ = results[sel[0]]
            win.destroy()
            self._select_day(day_num)
            self.notebook.select(0)
            self.text.see(f"{line_num}.0")
            self.text.tag_remove("sel", "1.0", "end")
            self.text.tag_add("sel", f"{line_num}.0", f"{line_num}.end")

        listbox.bind("<Double-Button-1>", jump_to)

    # ------------------------------------------------------------- Quiz --
    # Quiz Me is free: it doesn't call the paid Anthropic API. Instead it
    # copies your notes plus a ready-made quiz prompt to your clipboard and
    # opens claude.ai in your browser, where you can paste it into a chat
    # using whatever claude.ai access you already have (free or paid).

    def _quiz_me(self):
        if self.current_day is None:
            return
        content = self.text.get("1.0", "end-1c").strip()
        if not content:
            messagebox.showinfo("Quiz Me", "Write some notes for this day first.")
            return

        prompt = (
            f"Here are my notes from Day {self.current_day}. Please quiz me on them: "
            "write 5 questions that test my recall and understanding, and don't show "
            "me the answers until I try to answer each one.\n\n"
            f"NOTES:\n{content}"
        )

        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(prompt)
            self.root.update()  # keep the clipboard content after the app loses focus
        except tk.TclError:
            pass

        try:
            webbrowser.open("https://claude.ai/new")
        except Exception:
            pass

        messagebox.showinfo(
            "Quiz Me",
            f"Your Day {self.current_day} notes and a quiz prompt were copied to your "
            "clipboard, and claude.ai should now be opening in your browser.\n\n"
            "Just paste (Cmd+V / Ctrl+V) into the chat and send it — no API key or "
            "extra cost needed, it just uses your regular claude.ai access."
        )


def main():
    root = tk.Tk()
    app = EcosLearningNotesApp(root)

    def on_close():
        app._save_current(force=True)
        app._save_scribble()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


if __name__ == "__main__":
    main()
