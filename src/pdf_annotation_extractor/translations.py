import os
import gettext
import locale
from typing import Dict, List, Callable

LOCALE_DIR = os.path.join(os.path.dirname(__file__), 'locale')

LANGUAGES = {
    'en': 'English',
    'de': 'Deutsch',
    'tr': 'Türkçe'
}

DEFAULT_MESSAGES = {
    'title': 'PDF Annotation Extractor',
    'select_pdf': 'Select PDF file',
    'process': 'Process',
    'processing': 'Processing...',
    'success': 'Successfully processed!',
    'error': 'Error occurred: {}',
    'error_no_file': 'No file selected',
    'about_title': 'About PDF Annotation Extractor',
    'file_menu': 'File',
    'help_menu': 'Help',
    'about_menu': 'About',
    'exit_menu': 'Exit',
    'open_file': 'Open file',
    'save_file': 'Save file',
    'ready': 'Ready',
    'processing_file': 'Processing file...',
    'done': 'Done!',
    'no_file': 'No file selected',
    'invalid_pdf': 'Invalid PDF file',
    'language_menu': 'Language',
    'status_ready': 'Ready',
    'status_processing': 'Processing...',
    'status_done': 'Done!',
    'status_error': 'Error: {}',
    'select_file': 'Select File',
    'extract_comments': 'Extract Comments',
    'save_comments': 'Save Comments',
    'pdf_files': 'PDF Files',
    'text_files': 'Text Files',
    'all_files': 'All Files'
}

MESSAGES = DEFAULT_MESSAGES.copy()


class TranslationManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.current_language = 'en'
            self.observers: List[Callable] = []
            self._initialize_translations()
            self._initialized = True

    def _initialize_translations(self):
        try:
            system_language, _ = locale.getdefaultlocale()
            if system_language:
                system_language = system_language.split('_')[0]
                if system_language in LANGUAGES:
                    self.current_language = system_language
        except:
            pass

        self._setup_translation()
        self._update_messages()

    def _setup_translation(self):
        try:
            translation = gettext.translation(
                'messages',
                localedir=LOCALE_DIR,
                languages=[self.current_language],
                fallback=True
            )
            translation.install()
            global _
            _ = translation.gettext
        except:
            gettext.install('messages')
            _ = gettext.gettext

    def _update_messages(self):
        global MESSAGES
        MESSAGES = {key: _(value) for key, value in DEFAULT_MESSAGES.items()}

    def get_available_languages(self) -> Dict[str, str]:
        return LANGUAGES

    def get_current_language(self) -> str:
        return self.current_language

    def change_language(self, language_code: str):
        if language_code in LANGUAGES:
            self.current_language = language_code
            self._setup_translation()
            self._update_messages()
            self._notify_observers()

    def add_observer(self, callback: Callable):
        if callback not in self.observers:
            self.observers.append(callback)

    def remove_observer(self, callback: Callable):
        if callback in self.observers:
            self.observers.remove(callback)

    def _notify_observers(self):
        for callback in self.observers:
            callback()


translation_manager = TranslationManager()
_ = gettext.gettext