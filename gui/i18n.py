import json
import os

LANGUAGES = {
    "en": "English",
    "fr": "Français",
}

_current_lang = "en"
_translations = {}


def _locale_path(lang: str) -> str:
    base = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base, "locales", f"{lang}.json")


def set_language(lang: str) -> None:
    """Set the current language and load its translations."""
    global _current_lang, _translations
    _current_lang = lang
    path = _locale_path(lang)
    with open(path, encoding="utf-8") as f:
        _translations = json.load(f)


def tr(key: str) -> str:
    """Translate *key* in the current language."""
    return _translations.get(key, key)


# Load default language at import
set_language(_current_lang)
