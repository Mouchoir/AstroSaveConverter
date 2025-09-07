import os
import glob
import re
from datetime import datetime

from cogs import AstroLogging as Logger
import utils


def get_microsoft_save_folders() -> list:
    """Return list of Microsoft save folders found in %LocalAppdata%."""

    try:
        target = os.environ['LOCALAPPDATA'] + '\\Packages\\SystemEraSoftworks*\\SystemAppData\\wgs'
    except KeyError:
        Logger.logPrint("Local Appdata are missing, maybe you're on linux ?")
        Logger.logPrint("Press any key to exit")
        utils.wait_and_exit(1)

    microsoft_save_paths = list(glob.iglob(target))

    for path in microsoft_save_paths:
        Logger.logPrint(f'SES path found in appadata: {path}', 'debug')

    SES_appdata_path = microsoft_save_paths[-1]

    return get_save_folders_from_path(SES_appdata_path)


def select_microsoft_save_folder(folders, prompt='Select the save folder to use:') -> str:
    if not folders:
        Logger.logPrint('No save folder found.', 'debug')
        raise FileNotFoundError

    if len(folders) == 1:
        return folders[0]

    Logger.logPrint('Contents of detected save folders:')
    for i, folder in enumerate(folders, 1):
        details = get_save_details(folder)
        if details:
            formatted = ', '.join([f"{name} ({date})" for name, date in details])
        else:
            formatted = 'No saves found'
        Logger.logPrint(f"{i}) {formatted}")

    while True:
        Logger.logPrint(prompt)
        choice = input()
        Logger.logPrint(f'User choice: {choice}', 'debug')
        try:
            index = int(choice)
            if 1 <= index <= len(folders):
                return folders[index - 1]
        except ValueError:
            pass
        Logger.logPrint('Invalid selection. Please enter a valid number.')


def get_microsoft_save_folder() -> str:
    folders = get_microsoft_save_folders()
    return select_microsoft_save_folder(folders)


def get_save_folders_from_path(path) -> list:
    microsoft_save_folders = []

    for root, _, files in os.walk(path):
        for file in files:
            if re.search(r'^container\.', file):
                container_full_path = utils.join_paths(root, file)
                Logger.logPrint(f'Container file found: {container_full_path}', 'debug')

                container_text = read_container_text_from_path(container_full_path)

                if do_container_text_match_date(container_text):
                    Logger.logPrint(f'Matching save folder: {root}', 'debug')
                    microsoft_save_folders.append(root)

    return microsoft_save_folders


def get_save_details(folder_path: str):
    """Return list of (save_name, date_str) found in the folder's container file."""
    container_files = glob.glob(utils.join_paths(folder_path, 'container.*'))
    if not container_files:
        return []

    container_path = container_files[0]
    with open(container_path, 'rb') as container_file:
        text = container_file.read().decode('utf-16le', errors='ignore')

    pattern = re.compile(r'([A-Za-z0-9_]+)\$c?(\d{4}\.\d{2}\.\d{2}-\d{2}\.\d{2}\.\d{2})')
    details = []
    for name, date_str in pattern.findall(text):
        try:
            dt = datetime.strptime(date_str, '%Y.%m.%d-%H.%M.%S')
            formatted_date = dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            formatted_date = date_str
        details.append((name, formatted_date))
    return details


def read_container_text_from_path(path) -> str:
    with open(path, 'rb') as container_file:
        binary_content = container_file.read()
        text = binary_content.decode('utf-16le', errors='ignore')

        return text


def do_container_text_match_date(text) -> bool:
    return re.search(r'\$\d{4}\.\d{2}\.\d{2}', text)

