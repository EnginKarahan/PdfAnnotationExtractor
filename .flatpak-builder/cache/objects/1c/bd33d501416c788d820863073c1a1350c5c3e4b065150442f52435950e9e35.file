#!/usr/bin/env python3
"""
PDF Annotation Extractor - Graphical user interface
Copyright (C) 2024 Engin Karahan - https://karahan.net

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
from __future__ import annotations

import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

from . import translations
from .pdf_utils import extract_pdf_annotations, PDFProcessingError

translation_manager = translations.translation_manager
_ = translations._


def get_messages() -> dict[str, str]:
    return translations.MESSAGES


class PDFAnnotationExtractor(tk.Tk):
    def __init__(self):
        super().__init__()

        self.language_menu_codes: list[str] = []
        self.file_menu_index: int | None = None
        self.language_menu_index: int | None = None
        self.help_menu_index: int | None = None

        # Referenzen für Offset-Labels
        self.offset_label: ttk.Label | None = None
        self.offset_hint_label: ttk.Label | None = None

        translation_manager.add_observer(self.update_ui_texts)

        self.title(self.get_text('title'))
        self.geometry("600x400")

        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_menu()
        self.create_file_frame()
        self.create_offset_frame()

        self.status_var = tk.StringVar()
        self._status_key: str | None = None
        self._status_extra: str | None = None
        self.set_status_message('status_ready')

        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_label.grid(row=3, column=0, columnspan=2, pady=5)

        self.start_button = ttk.Button(
            self.main_frame,
            text=self.get_text('extract_comments'),
            command=self.start_extraction
        )
        self.start_button.grid(row=4, column=0, columnspan=2, pady=10)

    def get_text(self, key: str) -> str:
        return get_messages()[key]

    def compose_status_message(self, key: str, extra: str | None = None) -> str:
        text = get_messages().get(key, "")
        if extra is not None:
            if '{' in text:
                return text.format(extra)
            return f"{text}{extra}"
        return text

    def set_status_message(self, key: str, extra: str | None = None) -> None:
        self._status_key = key
        self._status_extra = extra
        self.status_var.set(self.compose_status_message(key, extra))

    def clear_status_tracking(self) -> None:
        self._status_key = None
        self._status_extra = None

    def create_menu(self):
        self.menubar = tk.Menu(self, tearoff=0)
        self.config(menu=self.menubar)

        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=self.get_text('file_menu'), menu=self.file_menu)
        self.file_menu_index = self.menubar.index('end')
        self.file_menu.add_command(label=self.get_text('exit_menu'), command=self.quit)

        self.language_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=self.get_text('language_menu'), menu=self.language_menu)
        self.language_menu_index = self.menubar.index('end')

        self.language_menu_codes.clear()
        for lang_code, lang_name in translation_manager.get_available_languages().items():
            self.language_menu_codes.append(lang_code)
            self.language_menu.add_command(
                label=lang_name,
                command=lambda code=lang_code: self.change_language(code)
            )

        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=self.get_text('help_menu'), menu=self.help_menu)
        self.help_menu_index = self.menubar.index('end')
        self.help_menu.add_command(label=self.get_text('about_menu'), command=self.show_about)

    def create_file_frame(self):
        self.file_frame = ttk.LabelFrame(
            self.main_frame,
            text=self.get_text('select_file'),
            padding="5"
        )
        self.file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.file_path = tk.StringVar()
        self.file_entry = ttk.Entry(
            self.file_frame,
            textvariable=self.file_path,
            width=50
        )
        self.file_entry.grid(row=0, column=0, padx=5)

        self.browse_button = ttk.Button(
            self.file_frame,
            text=self.get_text('open_file'),
            command=self.browse_file
        )
        self.browse_button.grid(row=0, column=1, padx=5)

    def create_offset_frame(self):
        self.offset_frame = ttk.LabelFrame(
            self.main_frame,
            text=_("Page Numbering"),
            padding="5"
        )
        self.offset_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.offset_label = ttk.Label(
            self.offset_frame,
            text=_("Page offset:")
        )
        self.offset_label.grid(row=0, column=0, padx=5)

        self.offset_var = tk.IntVar(value=-1)
        self.offset_entry = ttk.Entry(
            self.offset_frame,
            textvariable=self.offset_var,
            width=5
        )
        self.offset_entry.grid(row=0, column=1, padx=5)

        self.offset_hint_label = ttk.Label(
            self.offset_frame,
            text=_("(-1 for automatic detection)")
        )
        self.offset_hint_label.grid(row=0, column=2, padx=5)

    def change_language(self, language: str):
        translation_manager.change_language(language)

    def update_language_menu_labels(self):
        available = translation_manager.get_available_languages()
        for index, code in enumerate(self.language_menu_codes):
            label = available.get(code, code)
            self.language_menu.entryconfig(index, label=label)

    def update_ui_texts(self):
        """Update all UI texts after language change"""
        if not hasattr(self, 'menubar'):
            return

        self.title(self.get_text('title'))
        self.file_frame.configure(text=self.get_text('select_file'))
        self.browse_button.configure(text=self.get_text('open_file'))
        self.offset_frame.configure(text=_("Page Numbering"))

        # Offset-Labels aktualisieren
        if self.offset_label is not None:
            self.offset_label.configure(text=_("Page offset:"))
        if self.offset_hint_label is not None:
            self.offset_hint_label.configure(text=_("(-1 for automatic detection)"))

        self.start_button.configure(text=self.get_text('extract_comments'))

        if self.file_menu_index is not None:
            self.menubar.entryconfig(self.file_menu_index, label=self.get_text('file_menu'))
        if self.language_menu_index is not None:
            self.menubar.entryconfig(self.language_menu_index, label=self.get_text('language_menu'))
        if self.help_menu_index is not None:
            self.menubar.entryconfig(self.help_menu_index, label=self.get_text('help_menu'))

        self.file_menu.entryconfig(0, label=self.get_text('exit_menu'))
        self.help_menu.entryconfig(0, label=self.get_text('about_menu'))
        self.update_language_menu_labels()

        if self._status_key is not None:
            self.set_status_message(self._status_key, self._status_extra)

    def show_about(self):
        about_text = _("""PDF Annotation Extractor
Version 0.0.1-alpha

Copyright (C) 2024 Engin Karahan - https://karahan.net
This program is licensed under GNU GPL v3.""")

        messagebox.showinfo(self.get_text('about_title'), about_text)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title=self.get_text('select_pdf'),
            filetypes=[
                (self.get_text('pdf_files'), "*.pdf"),
                (self.get_text('all_files'), "*.*")
            ]
        )
        if filename:
            self.file_path.set(filename)

    def start_extraction(self):
        pdf_path = self.file_path.get()
        if not pdf_path:
            messagebox.showerror(
                _("Error"),
                self.get_text('error_no_file')
            )
            return

        if not os.path.exists(pdf_path):
            messagebox.showerror(
                _("Error"),
                _("The selected file does not exist.")
            )
            return

        try:
            self.set_status_message('status_processing')
            self.start_button.configure(state='disabled')
            self.update_idletasks()

            output_file = extract_pdf_annotations(
                pdf_path,
                self.offset_var.get(),
                self.update_progress
            )

            self.set_status_message('status_done', output_file)
            messagebox.showinfo(
                self.get_text('success'),
                _("Annotations were successfully extracted.\n\n"
                  "Output file: {0}").format(output_file)
            )

        except PDFProcessingError as e:
            error_message = str(e)
            messagebox.showerror(
                _("Error"),
                self.get_text('error').format(error_message)
            )
            self.set_status_message('status_error', error_message)
        finally:
            self.start_button.configure(state='normal')

    def update_progress(self, message: str):
        self.clear_status_tracking()
        self.status_var.set(message)
        self.update_idletasks()