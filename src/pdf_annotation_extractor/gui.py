#!/usr/bin/env python3
"""
PDF Annotation Extractor - Graphical user interface
Copyright (C) 2024  [Ihr Name]

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
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os
from translations import translation_manager, MESSAGES, _
from pdf_utils import extract_pdf_annotations, PDFProcessingError


class PDFAnnotationExtractor(tk.Tk):
    def __init__(self):
        super().__init__()

        translation_manager.add_observer(self.update_ui_texts)

        self.title(MESSAGES['title'])
        self.geometry("600x400")

        self.main_frame = ttk.Frame(self, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_menu()
        self.create_file_frame()
        self.create_offset_frame()

        self.status_var = tk.StringVar(value=MESSAGES['status_ready'])
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_label.grid(row=3, column=0, columnspan=2, pady=5)

        self.start_button = ttk.Button(
            self.main_frame,
            text=MESSAGES['extract_comments'],
            command=self.start_extraction
        )
        self.start_button.grid(row=4, column=0, columnspan=2, pady=10)

    def create_menu(self):
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)

        self.file_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=MESSAGES['file_menu'], menu=self.file_menu)
        self.file_menu.add_command(label=MESSAGES['exit_menu'], command=self.quit)

        self.language_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=MESSAGES['language_menu'], menu=self.language_menu)

        for lang_code, lang_name in translation_manager.get_available_languages().items():
            self.language_menu.add_command(
                label=lang_name,
                command=lambda l=lang_code: self.change_language(l)
            )

        self.help_menu = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label=MESSAGES['help_menu'], menu=self.help_menu)
        self.help_menu.add_command(label=MESSAGES['about_menu'], command=self.show_about)

    def create_file_frame(self):
        self.file_frame = ttk.LabelFrame(
            self.main_frame,
            text=MESSAGES['select_file'],
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
            text=MESSAGES['open_file'],
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

        ttk.Label(
            self.offset_frame,
            text=_("Page offset:")
        ).grid(row=0, column=0, padx=5)

        self.offset_var = tk.IntVar(value=-1)
        self.offset_entry = ttk.Entry(
            self.offset_frame,
            textvariable=self.offset_var,
            width=5
        )
        self.offset_entry.grid(row=0, column=1, padx=5)

        ttk.Label(
            self.offset_frame,
            text=_("(-1 for automatic detection)")
        ).grid(row=0, column=2, padx=5)

    def change_language(self, language):
        translation_manager.change_language(language)

    def update_ui_texts(self):
        """Update all UI texts after language change"""
        self.title(MESSAGES['title'])
        self.file_frame.configure(text=MESSAGES['select_file'])
        self.browse_button.configure(text=MESSAGES['open_file'])
        self.offset_frame.configure(text=_("Page Numbering"))
        self.start_button.configure(text=MESSAGES['extract_comments'])

        self.menubar.entryconfig(1, label=MESSAGES['language_menu'])
        self.menubar.entryconfig(2, label=MESSAGES['help_menu'])
        self.file_menu.entryconfig(0, label=MESSAGES['exit_menu'])
        self.help_menu.entryconfig(0, label=MESSAGES['about_menu'])

    def show_about(self):
        about_text = _("""PDF Annotation Extractor
Version 1.0

Copyright (C) 2024 [Your Name]
This program is licensed under GNU GPL v3.""")

        messagebox.showinfo(MESSAGES['about_title'], about_text)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title=MESSAGES['select_pdf'],
            filetypes=[
                (MESSAGES['pdf_files'], "*.pdf"),
                (MESSAGES['all_files'], "*.*")
            ]
        )
        if filename:
            self.file_path.set(filename)

    def start_extraction(self):
        pdf_path = self.file_path.get()
        if not pdf_path:
            messagebox.showerror(
                _("Error"),
                MESSAGES['error_no_file']
            )
            return

        if not os.path.exists(pdf_path):
            messagebox.showerror(
                _("Error"),
                _("The selected file does not exist.")
            )
            return

        try:
            self.status_var.set(MESSAGES['status_processing'])
            self.start_button.configure(state='disabled')
            self.update_idletasks()

            output_file = extract_pdf_annotations(
                pdf_path,
                self.offset_var.get(),
                self.update_progress
            )

            self.status_var.set(MESSAGES['status_done'] + output_file)
            messagebox.showinfo(
                MESSAGES['success'],
                _("Annotations were successfully extracted.\n\n"
                  "Output file: {0}").format(output_file)
            )

        except PDFProcessingError as e:
            messagebox.showerror(
                _("Error"),
                MESSAGES['error'].format(str(e))
            )
            self.status_var.set(MESSAGES['status_error'].format(str(e)))
        finally:
            self.start_button.configure(state='normal')

    def update_progress(self, message):
        self.status_var.set(message)
        self.update_idletasks()