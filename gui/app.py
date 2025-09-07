"""Simple Tkinter-based GUI for selecting Astroneer save folders.

This module provides a folder-selection page that automatically calls the
existing detection helpers to pre-populate text fields with the most likely
save locations.  Users can freely edit the paths or choose alternative ones
via standard directory selection dialogs.
"""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog
from typing import Tuple

from cogs import AstroMicrosoftSaveFolder, AstroSteamSaveFolder


def _detect_paths() -> Tuple[str, str]:
    """Try to detect Microsoft and Steam save folders.

    The detection functions are designed for Windows environments and will
    exit the program if required environment variables are missing.  To keep
    the GUI usable on other platforms, we first check for the relevant
    variables before calling the detection functions.

    Returns:
        Tuple[str, str]: Detected (microsoft_path, steam_path).
    """

    microsoft_path = ""
    steam_path = ""

    if os.environ.get("LOCALAPPDATA"):
        try:
            microsoft_path = AstroMicrosoftSaveFolder.get_microsoft_save_folder()
        except Exception:
            pass

        try:
            steam_path = AstroSteamSaveFolder.get_steam_save_folder()
        except Exception:
            pass

    return microsoft_path, steam_path


class FolderSelectionPage(tk.Tk):
    """Main window allowing users to select save folders."""

    def __init__(self) -> None:
        super().__init__()
        self.title("AstroSaveConverter - Folder Selection")

        self.microsoft_var = tk.StringVar()
        self.steam_var = tk.StringVar()

        ms_path, steam_path = _detect_paths()
        if ms_path:
            self.microsoft_var.set(ms_path)
        if steam_path:
            self.steam_var.set(steam_path)

        self._build_widgets()

    def _build_widgets(self) -> None:
        """Create and layout widgets for the page."""
        tk.Label(self, text="Microsoft/Xbox save folder:").grid(row=0, column=0, sticky="w")
        tk.Entry(self, textvariable=self.microsoft_var, width=60).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self, text="Browse…", command=lambda: self._browse(self.microsoft_var)).grid(row=0, column=2)

        tk.Label(self, text="Steam save folder:").grid(row=1, column=0, sticky="w")
        tk.Entry(self, textvariable=self.steam_var, width=60).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(self, text="Browse…", command=lambda: self._browse(self.steam_var)).grid(row=1, column=2)

    def _browse(self, var: tk.StringVar) -> None:
        """Open a directory selection dialog and update ``var`` if chosen."""
        path = filedialog.askdirectory()
        if path:
            var.set(path)


if __name__ == "__main__":
    app = FolderSelectionPage()
    app.mainloop()
