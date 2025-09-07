import os
import subprocess
import PySimpleGUI as sg

from main import windows_to_steam_conversion, steam_to_windows_conversion
from cogs import AstroLogging as Logger


# Mapping of step numbers to their labels
_STEPS = [
    "1. Type de conversion",
    "2. Dossier de sauvegarde",
    "3. Termin\u00e9",
]


def _update_step_bar(window, step):
    """Highlight the current step in the step bar."""
    for idx in range(1, 4):
        color = "black" if idx == step else "grey"
        window[f"-S{idx}-"].update(text_color=color)


def _open_folder(path: str) -> None:
    """Open ``path`` in the system's file explorer."""
    if not os.path.exists(path):
        sg.popup(f"Chemin introuvable: {path}", keep_on_top=True)
        return
    if os.name == "nt":
        os.startfile(path)
    else:
        subprocess.Popen(["xdg-open", path])


def main():
    """Launch the AstroSaveConverter GUI as a wizard."""
    sg.theme("SystemDefault")
    sg.set_options(font=("Segoe UI", 12), button_color=("white", "#0078D7"), border_width=0)

    astro_path = os.getcwd()
    logs_path = os.path.join(astro_path, "logs")
    backup_path = os.path.join(astro_path, "backups")
    Logger.setup_logging(astro_path)

    # Step bar
    step_bar = [
        sg.Text(_STEPS[0], key="-S1-"),
        sg.Text("\u2192"),
        sg.Text(_STEPS[1], key="-S2-"),
        sg.Text("\u2192"),
        sg.Text(_STEPS[2], key="-S3-"),
    ]

    # Step 1: choose conversion type
    step1_layout = [
        [sg.Text("Choisissez le type de conversion")],
        [
            sg.Radio("Steam \u2794 Microsoft", "MODE", key="-STEAM2WIN-"),
            sg.Radio("Microsoft \u2794 Steam", "MODE", key="-WIN2STEAM-"),
        ],
        [sg.Button("Suivant", key="-NEXT1-")],
    ]

    # Step 2: choose folder
    step2_layout = [
        [sg.Text("S\u00e9lectionnez le dossier de sauvegarde")],
        [sg.Input(key="-PATH-"), sg.FolderBrowse("Parcourir")],
        [
            sg.Button("Retour", key="-BACK2-"),
            sg.Button("Convertir", key="-NEXT2-"),
        ],
    ]

    # Step 3: done
    step3_layout = [
        [sg.Text("Conversion termin\u00e9e !")],
        [
            sg.Button("Retour", key="-BACK3-"),
            sg.Button("Terminer", key="-FINISH-"),
        ],
    ]

    layout = [
        step_bar,
        [
            sg.Column(step1_layout, key="-STEP1-"),
            sg.Column(step2_layout, key="-STEP2-", visible=False),
            sg.Column(step3_layout, key="-STEP3-", visible=False),
        ],
        [sg.Text(f"Logs : {logs_path}")],
        [
            sg.Button("Ouvrir les logs", key="-OPEN_LOGS-"),
            sg.Button("Ouvrir saves", key="-OPEN_SAVES-"),
            sg.Button("Ouvrir backups", key="-OPEN_BACKUPS-"),
        ],
    ]

    window = sg.Window("AstroSaveConverter", layout, finalize=True)
    _update_step_bar(window, 1)

    state = {"conversion": None, "path": ""}

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "-FINISH-"):
            break

        if event == "-NEXT1-":
            if values.get("-STEAM2WIN-"):
                state["conversion"] = steam_to_windows_conversion
            elif values.get("-WIN2STEAM-"):
                state["conversion"] = windows_to_steam_conversion
            else:
                sg.popup("Veuillez choisir un type de conversion", keep_on_top=True)
                continue
            window["-STEP1-"].update(visible=False)
            window["-STEP2-"].update(visible=True)
            _update_step_bar(window, 2)

        elif event == "-BACK2-":
            window["-STEP2-"].update(visible=False)
            window["-STEP1-"].update(visible=True)
            _update_step_bar(window, 1)

        elif event == "-NEXT2-":
            path = values.get("-PATH-")
            if not path:
                sg.popup("Veuillez s\u00e9lectionner un dossier", keep_on_top=True)
                continue
            state["path"] = path
            state["conversion"](path)
            window["-STEP2-"].update(visible=False)
            window["-STEP3-"].update(visible=True)
            _update_step_bar(window, 3)

        elif event == "-BACK3-":
            window["-STEP3-"].update(visible=False)
            window["-STEP2-"].update(visible=True)
            _update_step_bar(window, 2)

        elif event == "-OPEN_LOGS-":
            _open_folder(logs_path)

        elif event == "-OPEN_SAVES-":
            if state["path"]:
                _open_folder(state["path"])
            else:
                sg.popup("Aucun dossier de sauvegarde s\u00e9lectionn\u00e9", keep_on_top=True)

        elif event == "-OPEN_BACKUPS-":
            _open_folder(backup_path)

    window.close()


if __name__ == "__main__":
    main()
