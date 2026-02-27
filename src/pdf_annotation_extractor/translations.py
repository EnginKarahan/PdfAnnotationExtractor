import os
import gettext
import locale
from typing import Callable, Dict, List

# Platzhalter-_ für die Extraktion durch Babel/xgettext
try:
    from gettext import gettext as _  # type: ignore
except ImportError:
    def _(message: str) -> str:
        return message


SEARCH_PATHS = [
    # 1. Relativ zum aktuellen Skript (für die lokale Entwicklung)
    os.path.join(os.path.dirname(__file__), "locale"),
    # 2. Systemweiter Pfad im Flatpak (/app/share/...)
    # Wir verwenden die Umgebungsvariable, die Flatpak setzt.
    os.path.join(os.environ.get('FLATPAK_APP_DIR', '/app'), 'share', 'pdf-annotation-extractor', 'locale')
]

LOCALE_DIR = ""
for path in SEARCH_PATHS:
    if os.path.isdir(path):
        LOCALE_DIR = path
        break

if not LOCALE_DIR:
    # Fallback mit einer Warnung, falls nichts gefunden wird
    print("Warning: Locale directory not found. Falling back to default.")
    LOCALE_DIR = os.path.join(os.path.dirname(__file__), "locale")

LANGUAGES: Dict[str, str] = {
    "en": "English",
    "de": "Deutsch",
    "tr": "Türkçe",
}

DEFAULT_MESSAGES: Dict[str, str] = {
    "title": _("PDF Annotation Extractor"),
    "select_pdf": _("Select PDF file"),
    "process": _("Process"),
    "processing": _("Processing..."),
    "success": _("Successfully processed!"),
    "error": _("Error occurred: {}"),
    "error_no_file": _("No file selected"),
    "about_title": _("About PDF Annotation Extractor"),
    "file_menu": _("File"),
    "help_menu": _("Help"),
    "about_menu": _("About"),
    "exit_menu": _("Exit"),
    "open_file": _("Open file"),
    "save_file": _("Save file"),
    "ready": _("Ready"),
    "processing_file": _("Processing file..."),
    "done": _("Done!"),
    "no_file": _("No file selected"),
    "invalid_pdf": _("Invalid PDF file"),
    "language_menu": _("Language"),
    "status_ready": _("Ready"),
    "status_processing": _("Processing..."),
    "status_done": _("Done!"),
    "status_error": _("Error: {}"),
    "select_file": _("Select File"),
    "extract_comments": _("Extract Comments"),
    "save_comments": _("Save Comments"),
    "pdf_files": _("PDF Files"),
    "text_files": _("Text Files"),
    "all_files": _("All Files"),
}

MESSAGES: Dict[str, str] = DEFAULT_MESSAGES.copy()


class TranslationManager:
    _instance: "TranslationManager | None" = None

    def __new__(cls) -> "TranslationManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False  # type: ignore[attr-defined]
        return cls._instance

    def __init__(self) -> None:
        if not getattr(self, "_initialized", False):
            self.current_language: str = "en"
            self.observers: List[Callable[[], None]] = []
            self._translator: Callable[[str], str] = gettext.gettext
            self._initialize_translations()
            self._initialized = True  # type: ignore[attr-defined]

    def _initialize_translations(self) -> None:
        try:
            system_language, _ = locale.getdefaultlocale()
            if system_language:
                candidate = system_language.split("_")[0]
                if candidate in LANGUAGES:
                    self.current_language = candidate
        except Exception:
            pass

        self._setup_translation()
        self._update_messages()

    def _setup_translation(self) -> None:
        translation = gettext.translation(
            "messages",
            localedir=LOCALE_DIR,
            languages=[self.current_language],
            fallback=True,
        )
        self._translator = translation.gettext

    def gettext(self, message: str) -> str:
        return self._translator(message)

    def _update_messages(self) -> None:
        global MESSAGES
        MESSAGES = {key: self.gettext(value) for key, value in DEFAULT_MESSAGES.items()}

    def get_available_languages(self) -> Dict[str, str]:
        return LANGUAGES

    def get_current_language(self) -> str:
        return self.current_language

    def change_language(self, language_code: str) -> None:
        if language_code in LANGUAGES and language_code != self.current_language:
            self.current_language = language_code
            self._setup_translation()
            self._update_messages()
            self._notify_observers()

    def add_observer(self, callback: Callable[[], None]) -> None:
        if callback not in self.observers:
            self.observers.append(callback)

    def remove_observer(self, callback: Callable[[], None]) -> None:
        if callback in self.observers:
            self.observers.remove(callback)

    def _notify_observers(self) -> None:
        for callback in list(self.observers):
            callback()


translation_manager = TranslationManager()


def _(message: str) -> str:
    return translation_manager.gettext(message)