"""Tkinter-based graphical interface for AstroSaveConverter.

This module replaces the previous PySimpleGUI implementation with a
fully libre solution built on Python's built-in ``tkinter`` toolkit.
The interface guides the user through three steps: selecting a
conversion type, choosing the save directory and confirming that the
conversion finished successfully.
"""

from __future__ import annotations

import os
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from main import steam_to_windows_conversion, windows_to_steam_conversion
from cogs import AstroLogging as Logger
from .i18n import LANGUAGES, set_language, tr


def _open_folder(path: str) -> None:
    """Open *path* in the system's file explorer."""
    if not os.path.exists(path):
        messagebox.showerror("AstroSaveConverter", tr("path_not_found").format(path=path))
        return
    if os.name == "nt":
        os.startfile(path)  # type: ignore[attr-defined]
    else:
        subprocess.Popen(["xdg-open", path])


def main() -> None:
    """Launch the AstroSaveConverter GUI."""
    root = tk.Tk()
    root.title("AstroSaveConverter")

    astro_path = os.getcwd()
    assets_path = os.path.join(astro_path, "assets")
    icon_path = os.path.join(assets_path, "astroconverterlogo.ico")
    try:
        root.iconbitmap(icon_path)
    except Exception:
        pass

    convert_photo = tk.PhotoImage(file=os.path.join(assets_path, "convert.ppm"))
    folder_photo = tk.PhotoImage(file=os.path.join(assets_path, "folder.ppm"))
    done_photo = tk.PhotoImage(file=os.path.join(assets_path, "done.ppm"))

    logs_path = os.path.join(astro_path, "logs")
    backup_path = os.path.join(astro_path, "backups")
    Logger.setup_logging(astro_path)

    name_to_code = {v: k for k, v in LANGUAGES.items()}
    default_lang = "en"
    set_language(default_lang)

    lang_var = tk.StringVar(value=LANGUAGES[default_lang])
    lang_frame = ttk.Frame(root)
    lang_label = ttk.Label(lang_frame)
    lang_label.pack(side="left", padx=(0, 5))
    lang_combo = ttk.Combobox(
        lang_frame,
        values=list(LANGUAGES.values()),
        textvariable=lang_var,
        state="readonly",
    )
    lang_combo.pack(side="left")
    lang_frame.pack(pady=(0, 10))

    step_bar = ttk.Frame(root)
    step_labels: list[ttk.Label] = []
    for idx in range(3):
        lbl = ttk.Label(step_bar)
        lbl.grid(row=0, column=idx * 2)
        step_labels.append(lbl)
        if idx < 2:
            ttk.Label(step_bar, text="\u2192").grid(row=0, column=idx * 2 + 1)
    step_bar.pack(pady=(0, 10))

    content = ttk.Frame(root)
    content.pack(pady=(0, 10))

    # Step 1 -----------------------------------------------------------------
    conv_var = tk.StringVar()
    step1 = ttk.Frame(content)
    ttk.Label(step1, image=convert_photo).pack()
    t1 = ttk.Label(step1)
    t1.pack()
    rb1 = ttk.Radiobutton(step1, variable=conv_var, value="steam2win")
    rb1.pack(anchor="w")
    rb2 = ttk.Radiobutton(step1, variable=conv_var, value="win2steam")
    rb2.pack(anchor="w")
    next1_btn = ttk.Button(step1)
    next1_btn.pack(pady=(5, 0))

    # Step 2 -----------------------------------------------------------------
    step2 = ttk.Frame(content)
    ttk.Label(step2, image=folder_photo).pack()
    t2 = ttk.Label(step2)
    t2.pack()
    path_var = tk.StringVar()
    path_frame = ttk.Frame(step2)
    path_entry = ttk.Entry(path_frame, textvariable=path_var, width=40)
    path_entry.pack(side="left", fill="x", expand=True)
    browse_btn = ttk.Button(path_frame)
    browse_btn.pack(side="left", padx=(5, 0))
    path_frame.pack(pady=(0, 5))
    btns2 = ttk.Frame(step2)
    back2_btn = ttk.Button(btns2)
    back2_btn.pack(side="left", padx=(0, 5))
    next2_btn = ttk.Button(btns2)
    next2_btn.pack(side="left")
    btns2.pack()

    # Step 3 -----------------------------------------------------------------
    step3 = ttk.Frame(content)
    ttk.Label(step3, image=done_photo).pack()
    t3 = ttk.Label(step3)
    t3.pack()
    btns3 = ttk.Frame(step3)
    back3_btn = ttk.Button(btns3)
    back3_btn.pack(side="left", padx=(0, 5))
    finish_btn = ttk.Button(btns3, command=root.destroy)
    finish_btn.pack(side="left")
    btns3.pack()

    step1.pack()

    logs_label = ttk.Label(root)
    logs_label.pack()

    bottom = ttk.Frame(root)
    open_logs_btn = ttk.Button(bottom, command=lambda: _open_folder(logs_path))
    open_logs_btn.pack(side="left", padx=(0, 5))
    open_saves_btn = ttk.Button(bottom)
    open_saves_btn.pack(side="left", padx=(0, 5))
    open_backups_btn = ttk.Button(bottom, command=lambda: _open_folder(backup_path))
    open_backups_btn.pack(side="left")
    bottom.pack(pady=(5, 0))

    current_step = 1
    state = {"conversion": None, "path": ""}

    def _update_step_bar(step: int) -> None:
        for idx, lbl in enumerate(step_labels, start=1):
            color = "black" if idx == step else "grey"
            lbl.config(foreground=color)

    def _update_texts() -> None:
        lang_label.config(text=tr("language"))
        step_labels[0].config(text=tr("step1_label"))
        step_labels[1].config(text=tr("step2_label"))
        step_labels[2].config(text=tr("step3_label"))
        t1.config(text=tr("choose_conversion"))
        rb1.config(text=tr("steam_to_microsoft"))
        rb2.config(text=tr("microsoft_to_steam"))
        next1_btn.config(text=tr("next"))
        t2.config(text=tr("select_save_folder"))
        browse_btn.config(text=tr("browse"))
        back2_btn.config(text=tr("back"))
        next2_btn.config(text=tr("convert"))
        t3.config(text=tr("conversion_done"))
        back3_btn.config(text=tr("back"))
        finish_btn.config(text=tr("finish"))
        logs_label.config(text=tr("logs_label").format(path=logs_path))
        open_logs_btn.config(text=tr("open_logs"))
        open_saves_btn.config(text=tr("open_saves"))
        open_backups_btn.config(text=tr("open_backups"))
        _update_step_bar(current_step)

    def on_language_change(event: object) -> None:  # pragma: no cover - GUI only
        set_language(name_to_code[lang_var.get()])
        _update_texts()

    def next1() -> None:
        nonlocal current_step
        if conv_var.get() == "steam2win":
            state["conversion"] = steam_to_windows_conversion
        elif conv_var.get() == "win2steam":
            state["conversion"] = windows_to_steam_conversion
        else:
            messagebox.showinfo("AstroSaveConverter", tr("choose_conversion_prompt"))
            return
        step1.pack_forget()
        step2.pack()
        current_step = 2
        _update_step_bar(current_step)

    def back2() -> None:
        nonlocal current_step
        step2.pack_forget()
        step1.pack()
        current_step = 1
        _update_step_bar(current_step)

    def browse() -> None:  # pragma: no cover - GUI only
        directory = filedialog.askdirectory()
        if directory:
            path_var.set(directory)

    def next2() -> None:
        nonlocal current_step
        path = path_var.get()
        if not path:
            messagebox.showinfo("AstroSaveConverter", tr("select_folder_prompt"))
            return
        state["path"] = path
        assert state["conversion"] is not None
        state["conversion"](path)
        step2.pack_forget()
        step3.pack()
        current_step = 3
        _update_step_bar(current_step)

    def back3() -> None:
        nonlocal current_step
        step3.pack_forget()
        step2.pack()
        current_step = 2
        _update_step_bar(current_step)

    def open_saves() -> None:
        if state["path"]:
            _open_folder(state["path"])
        else:
            messagebox.showinfo("AstroSaveConverter", tr("no_save_selected"))

    lang_combo.bind("<<ComboboxSelected>>", on_language_change)
    next1_btn.config(command=next1)
    browse_btn.config(command=browse)
    back2_btn.config(command=back2)
    next2_btn.config(command=next2)
    back3_btn.config(command=back3)
    open_saves_btn.config(command=open_saves)

    _update_texts()
    root.mainloop()


if __name__ == "__main__":  # pragma: no cover - manual launch
    main()

