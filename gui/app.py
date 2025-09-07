import os
import PySimpleGUI as sg

from main import windows_to_steam_conversion, steam_to_windows_conversion
from cogs import AstroLogging as Logger


def _select_folder_and_convert(conversion_func):
    """Ask the user for a folder then run the given conversion function."""
    layout = [
        [sg.Text("Sélectionnez le dossier de sauvegarde")],
        [sg.Input(key="-PATH-"), sg.FolderBrowse("Parcourir")],
        [sg.Button("Convertir", key="GO"), sg.Button("Annuler")],
    ]
    window = sg.Window("Choix du dossier", layout, finalize=True)
    while True:
        event, values = window.read()
        if event in (sg.WINDOW_CLOSED, "Annuler"):
            break
        if event == "GO":
            path = values.get("-PATH-")
            if not path:
                sg.popup("Veuillez sélectionner un dossier", keep_on_top=True)
                continue
            window.close()
            conversion_func(path)
            sg.popup("Conversion terminée !", keep_on_top=True)
            return
    window.close()


def main():
    """Launch the AstroSaveConverter GUI."""
    sg.theme("SystemDefault")
    sg.set_options(font=("Segoe UI", 12), button_color=("white", "#0078D7"), border_width=0)

    layout = [
        [sg.Text("AstroSaveConverter", font=("Segoe UI", 16))],
        [sg.Button("Steam \u2794 Microsoft", key="STEAM2WIN", size=(20, 2))],
        [sg.Button("Microsoft \u2794 Steam", key="WIN2STEAM", size=(20, 2))],
    ]

    Logger.setup_logging(os.getcwd())

    window = sg.Window("AstroSaveConverter", layout, element_justification="center")
    while True:
        event, _ = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        if event == "STEAM2WIN":
            _select_folder_and_convert(steam_to_windows_conversion)
        elif event == "WIN2STEAM":
            _select_folder_and_convert(windows_to_steam_conversion)
    window.close()


if __name__ == "__main__":
    main()
