import os
import subprocess
import PySimpleGUI as sg

from main import windows_to_steam_conversion, steam_to_windows_conversion
from cogs import AstroLogging as Logger
from .i18n import LANGUAGES, set_language, tr


def _update_step_bar(window, step):
    """Highlight the current step in the step bar."""
    for idx in range(1, 4):
        color = "black" if idx == step else "grey"
        window[f"-S{idx}-"].update(text_color=color)

def _open_folder(path: str) -> None:
    """Open ``path`` in the system's file explorer."""
    if not os.path.exists(path):
        sg.popup(tr("path_not_found").format(path=path), keep_on_top=True)
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

    name_to_code = {v: k for k, v in LANGUAGES.items()}
    default_lang = "en"
    set_language(default_lang)
    lang_selector = sg.Combo(
        list(LANGUAGES.values()),
        default_value=LANGUAGES[default_lang],
        key="-LANG-",
        enable_events=True,
        readonly=True,
    )

    # Step bar
    step_bar = [
        sg.Text("", key="-S1-"),
        sg.Text("\u2192"),
        sg.Text("", key="-S2-"),
        sg.Text("\u2192"),
        sg.Text("", key="-S3-"),
    ]

    # Step 1: choose conversion type
    step1_layout = [
        [sg.Text("", key="-T1-")],
        [
            sg.Radio("", "MODE", key="-STEAM2WIN-"),
            sg.Radio("", "MODE", key="-WIN2STEAM-"),
        ],
        [sg.Button("", key="-NEXT1-")],
    ]

    # Step 2: choose folder
    step2_layout = [
        [sg.Text("", key="-T2-")],
        [sg.Input(key="-PATH-"), sg.FolderBrowse("", key="-BROWSE-")],
        [
            sg.Button("", key="-BACK2-"),
            sg.Button("", key="-NEXT2-"),
        ],
    ]

    # Step 3: done
    step3_layout = [
        [sg.Text("", key="-T3-")],
        [
            sg.Button("", key="-BACK3-"),
            sg.Button("", key="-FINISH-"),
        ],
    ]

    layout = [
        [sg.Text("", key="-LANG_LABEL-"), lang_selector],
        step_bar,
        [
            sg.Column(step1_layout, key="-STEP1-"),
            sg.Column(step2_layout, key="-STEP2-", visible=False),
            sg.Column(step3_layout, key="-STEP3-", visible=False),
        ],
        [sg.Text("", key="-LOGS_LABEL-")],
        [
            sg.Button("", key="-OPEN_LOGS-"),
            sg.Button("", key="-OPEN_SAVES-"),
            sg.Button("", key="-OPEN_BACKUPS-"),
        ],
    ]

    window = sg.Window("AstroSaveConverter", layout, finalize=True)

    current_step = 1

    def _update_texts():
        window["-LANG_LABEL-"].update(tr("language"))
        window["-S1-"].update(tr("step1_label"))
        window["-S2-"].update(tr("step2_label"))
        window["-S3-"].update(tr("step3_label"))
        window["-T1-"].update(tr("choose_conversion"))
        window["-STEAM2WIN-"].update(text=tr("steam_to_microsoft"))
        window["-WIN2STEAM-"].update(text=tr("microsoft_to_steam"))
        window["-NEXT1-"].update(tr("next"))
        window["-T2-"].update(tr("select_save_folder"))
        window["-BROWSE-"].update(tr("browse"))
        window["-BACK2-"].update(tr("back"))
        window["-NEXT2-"].update(tr("convert"))
        window["-T3-"].update(tr("conversion_done"))
        window["-BACK3-"].update(tr("back"))
        window["-FINISH-"].update(tr("finish"))
        window["-LOGS_LABEL-"].update(tr("logs_label").format(path=logs_path))
        window["-OPEN_LOGS-"].update(tr("open_logs"))
        window["-OPEN_SAVES-"].update(tr("open_saves"))
        window["-OPEN_BACKUPS-"].update(tr("open_backups"))
        _update_step_bar(window, current_step)

    _update_texts()

    state = {"conversion": None, "path": ""}

    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "-FINISH-"):
            break

        if event == "-LANG-":
            set_language(name_to_code[values["-LANG-"]])
            _update_texts()

        elif event == "-NEXT1-":
            if values.get("-STEAM2WIN-"):
                state["conversion"] = steam_to_windows_conversion
            elif values.get("-WIN2STEAM-"):
                state["conversion"] = windows_to_steam_conversion
            else:
                sg.popup(tr("choose_conversion_prompt"), keep_on_top=True)
                continue
            window["-STEP1-"].update(visible=False)
            window["-STEP2-"].update(visible=True)
            current_step = 2
            _update_step_bar(window, current_step)

        elif event == "-BACK2-":
            window["-STEP2-"].update(visible=False)
            window["-STEP1-"].update(visible=True)
            current_step = 1
            _update_step_bar(window, current_step)

        elif event == "-NEXT2-":
            path = values.get("-PATH-")
            if not path:
                sg.popup(tr("select_folder_prompt"), keep_on_top=True)
                continue
            state["path"] = path
            state["conversion"](path)
            window["-STEP2-"].update(visible=False)
            window["-STEP3-"].update(visible=True)
            current_step = 3
            _update_step_bar(window, current_step)

        elif event == "-BACK3-":
            window["-STEP3-"].update(visible=False)
            window["-STEP2-"].update(visible=True)
            current_step = 2
            _update_step_bar(window, current_step)

        elif event == "-OPEN_LOGS-":
            _open_folder(logs_path)

        elif event == "-OPEN_SAVES-":
            if state["path"]:
                _open_folder(state["path"])
            else:
                sg.popup(tr("no_save_selected"), keep_on_top=True)

        elif event == "-OPEN_BACKUPS-":
            _open_folder(backup_path)

    window.close()


if __name__ == "__main__":
    main()
