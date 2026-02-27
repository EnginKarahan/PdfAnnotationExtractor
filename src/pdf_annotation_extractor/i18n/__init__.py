#!/usr/bin/env python3
"""
PDF Annotation Extractor - i18n Module
Copyright (C) 2024 Engin Karahan

Internationalization support using Qt Linguist.
"""

import os
from pathlib import Path
from typing import Optional, List, Tuple
from dataclasses import dataclass

from PyQt6.QtCore import QTranslator, QLocale


@dataclass
class LanguageInfo:
    code: str
    name: str
    native_name: str


AVAILABLE_LANGUAGES = [
    LanguageInfo("en", "English", "English"),
    LanguageInfo("de", "German", "Deutsch"),
    LanguageInfo("tr", "Turkish", "Türkçe"),
]


class I18nManager:
    """Manages application translations"""

    def __init__(self, app_name: str = "pdf-annotation-extractor"):
        self.app_name = app_name
        self.translator: Optional[QTranslator] = None
        self.current_language: str = "en"

    def get_available_languages(self) -> List[Tuple[str, str]]:
        """Return list of available (code, name) tuples"""
        return [(lang.code, lang.native_name) for lang in AVAILABLE_LANGUAGES]

    def load_translation(self, language_code: str) -> bool:
        """Load translation for given language code"""
        if self.translator:
            QApplication.instance().removeTranslator(self.translator)

        self.translator = QTranslator()

        translation_file = f":/i18n/{self.app_name}_{language_code}.qm"

        if self.translator.load(translation_file):
            QApplication.instance().installTranslator(self.translator)
            self.current_language = language_code
            return True

        return False

    def get_current_language(self) -> str:
        """Get current language code"""
        return self.current_language

    def set_system_language(self) -> None:
        """Set language to system default"""
        system_lang = QLocale.system().name()
        if system_lang.startswith("de"):
            self.load_translation("de")
        elif system_lang.startswith("tr"):
            self.load_translation("tr")
        else:
            self.load_translation("en")


from PyQt6.QtWidgets import QApplication

i18n_manager = I18nManager()
