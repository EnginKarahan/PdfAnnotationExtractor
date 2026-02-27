#!/usr/bin/env python3
"""
PDF Annotation Extractor - PyQt6 GUI with Preview
Copyright (C) 2024 Engin Karahan - https://karahan.net

Graphical user interface using PyQt6 with KDE Plasma integration.
Features:
- 3-panel layout (Files, Functions, Preview)
- PDF preview with annotations highlighting
- Markdown editor
- Directory browser
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from typing import Optional, List
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QProgressBar,
    QStatusBar,
    QMenuBar,
    QMenu,
    QSpinBox,
    QGroupBox,
    QFormLayout,
    QFrame,
    QStyleFactory,
    QSplitter,
    QTreeView,
    QListWidget,
    QListWidgetItem,
    QTabWidget,
    QTextEdit,
    QSplitter,
    QAbstractItemView,
    QToolBar,
)
from PyQt6.QtCore import (
    Qt,
    QTranslator,
    QLocale,
    pyqtSignal,
    QSize,
    QDir,
    QModelIndex,
    QMimeData,
    QUrl,
)
from PyQt6.QtGui import (
    QAction,
    QIcon,
    QKeySequence,
    QFileSystemModel,
    QStandardItemModel,
    QStandardItem,
)
from PyQt6.QtPdfWidgets import QPdfView
from PyQt6.QtPdf import QPdfDocument

from ..core import (
    extract_pdf_annotations,
    validate_pdf,
    PDFProcessingError,
    PDFProcessor,
)
from ..config import get_config


class FileTreePanel(QWidget):
    """Left panel - File browser"""

    directory_changed = pyqtSignal(str)
    file_selected = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        title = QLabel(self.tr("Files"))
        title.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(title)

        self.dir_button = QPushButton(self.tr("Choose Directory..."))
        self.dir_button.clicked.connect(self.choose_directory)
        layout.addWidget(self.dir_button)

        self.dir_label = QLabel(self.tr("No directory selected"))
        self.dir_label.setStyleSheet("color: gray; font-size: 9pt;")
        self.dir_label.setWordWrap(True)
        layout.addWidget(self.dir_label)

        self.file_tree = QTreeView()
        self.file_tree.setHeaderHidden(True)
        self.file_tree.setAnimated(True)
        self.file_tree.setIndentation(20)
        self.file_tree.setSortingEnabled(True)
        self.file_tree.doubleClicked.connect(self.on_file_double_clicked)

        self.file_model = QFileSystemModel()
        self.file_model.setRootPath("")
        self.file_model.setNameFilters(["*.pdf", "*.md", "*.PDF", "*.MD"])
        self.file_model.setNameFilterDisables(False)

        self.file_tree.setModel(self.file_model)
        self.file_tree.setRootIndex(QModelIndex())

        layout.addWidget(self.file_tree)

        self.file_tree.setColumnHidden(1, True)
        self.file_tree.setColumnHidden(2, True)
        self.file_tree.setColumnHidden(3, True)

    def set_directory(self, path: str):
        """Set the directory to display"""
        if os.path.isdir(path):
            index = self.file_model.setRootPath(path)
            self.file_tree.setRootIndex(index)
            self.dir_label.setText(path)
            self.directory_changed.emit(path)

    def choose_directory(self):
        """Open directory chooser"""
        directory = QFileDialog.getExistingDirectory(
            self,
            self.tr("Choose Directory"),
            self.dir_label.text()
            if self.dir_label.text() != self.tr("No directory selected")
            else str(Path.home()),
        )
        if directory:
            self.set_directory(directory)

    def on_file_double_clicked(self, index: QModelIndex):
        """Handle file double-click"""
        file_path = self.file_model.filePath(index)
        if os.path.isfile(file_path):
            self.file_selected.emit(file_path)


class FunctionPanel(QWidget):
    """Center panel - Functions and actions"""

    extract_requested = pyqtSignal(str)
    load_requested = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file_path = ""
        self.file_panel_ref = None
        self._init_ui()

    def set_file_panel(self, file_panel):
        """Set reference to file panel for accessing selection"""
        self.file_panel_ref = file_panel

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        title = QLabel(self.tr("Functions"))
        title.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(title)

        file_group = QGroupBox(self.tr("Current File"))
        file_layout = QVBoxLayout(file_group)

        self.file_label = QLabel(self.tr("No file selected"))
        self.file_label.setWordWrap(True)
        self.file_label.setStyleSheet(
            "color: #333; padding: 5px; background: #f0f0f0; border-radius: 3px;"
        )
        file_layout.addWidget(self.file_label)

        self.load_button = QPushButton(self.tr("Load File"))
        self.load_button.clicked.connect(self.on_load_clicked)
        file_layout.addWidget(self.load_button)

        layout.addWidget(file_group)

        extract_group = QGroupBox(self.tr("Extraction"))
        extract_layout = QFormLayout(extract_group)

        self.offset_spinbox = QSpinBox()
        self.offset_spinbox.setRange(-1, 1000)
        self.offset_spinbox.setValue(-1)
        self.offset_spinbox.setToolTip(self.tr("-1 for automatic detection"))
        extract_layout.addRow(self.tr("Page offset:"), self.offset_spinbox)

        offset_hint = QLabel(self.tr("(-1 for automatic detection)"))
        offset_hint.setStyleSheet("color: gray; font-size: 9pt;")
        extract_layout.addRow("", offset_hint)

        self.extract_button = QPushButton(self.tr("Extract Annotations"))
        self.extract_button.setMinimumHeight(40)
        self.extract_button.setStyleSheet("""
            QPushButton {
                background-color: #3daee9;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #5dc4f3; }
            QPushButton:disabled { background-color: #cccccc; }
        """)
        self.extract_button.clicked.connect(self.on_extract_clicked)
        extract_layout.addRow("", self.extract_button)

        layout.addWidget(extract_group)

        layout.addStretch()

    def set_file(self, file_path: str):
        """Set current file"""
        self.current_file_path = file_path
        self.file_label.setText(
            os.path.basename(file_path) if file_path else self.tr("No file selected")
        )

    def on_load_clicked(self):
        """Handle load button click"""
        if self.file_panel_ref:
            current_index = self.file_panel_ref.file_tree.currentIndex()
            if current_index.isValid():
                file_path = self.file_panel_ref.file_model.filePath(current_index)
                if file_path and os.path.isfile(file_path):
                    self.current_file_path = file_path
                    self.file_label.setText(os.path.basename(file_path))
                    self.load_requested.emit(file_path)
                    return

        if self.current_file_path and os.path.isfile(self.current_file_path):
            self.load_requested.emit(self.current_file_path)

    def on_extract_clicked(self):
        """Handle extract button click"""
        if self.current_file_path and os.path.isfile(self.current_file_path):
            self.extract_requested.emit(self.current_file_path)


class PreviewPanel(QWidget):
    """Right panel - Preview (PDF/Markdown)"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_file = None
        self.annotations = []
        self.pdf_document = QPdfDocument(self)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        title = QLabel(self.tr("Preview"))
        title.setStyleSheet("font-weight: bold; font-size: 11pt;")
        layout.addWidget(title)

        self.tab_widget = QTabWidget()

        self.pdf_view = QPdfView(self)
        self.pdf_view.setDocument(self.pdf_document)
        self.pdf_view.setPageMode(QPdfView.PageMode.MultiPage)

        self.tab_widget.addTab(self.pdf_view, "PDF")

        self.markdown_edit = QTextEdit()
        self.markdown_edit.setReadOnly(False)
        self.markdown_edit.setPlaceholderText(
            self.tr("Markdown content will appear here...")
        )
        self.tab_widget.addTab(self.markdown_edit, self.tr("Markdown"))

        layout.addWidget(self.tab_widget)

    def load_pdf(self, file_path: str):
        """Load PDF file for preview"""
        self.current_file = file_path
        self.pdf_document.load(file_path)
        self.pdf_view.resetZoom()
        self.tab_widget.setCurrentWidget(self.pdf_view)

    def load_markdown(self, file_path: str):
        """Load markdown file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.markdown_edit.setPlainText(content)
            self.tab_widget.setCurrentWidget(self.markdown_edit)
        except Exception as e:
            self.markdown_edit.setPlainText(f"Error loading file: {e}")

    def highlight_annotations(self, annotations: List, pdf_path: str):
        """Highlight annotations in PDF preview"""
        self.annotations = annotations
        self.load_pdf(pdf_path)


class PDFAnnotationExtractorWindow(QMainWindow):
    """Main application window with 3-panel layout"""

    def __init__(self):
        super().__init__()

        self.config = get_config()
        self.translator: Optional[QTranslator] = None
        self.current_pdf = None
        self.current_annotations = []

        self._init_ui()
        self._apply_theme()
        self._load_settings()
        self._connect_signals()

    def _init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle(self.tr("PDF Annotation Extractor"))
        self.setMinimumSize(QSize(1000, 700))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.file_panel = FileTreePanel()
        self.file_panel.setMinimumWidth(200)
        splitter.addWidget(self.file_panel)

        self.function_panel = FunctionPanel()
        self.function_panel.setMinimumWidth(250)
        self.function_panel.set_file_panel(self.file_panel)
        splitter.addWidget(self.function_panel)

        self.preview_panel = PreviewPanel()
        self.preview_panel.setMinimumWidth(300)
        splitter.addWidget(self.preview_panel)

        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 4)
        splitter.setStretchFactor(2, 4)

        main_layout.addWidget(splitter)

        self._create_menu_bar()
        self._create_status_bar()

    def _create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()

        file_menu = menubar.addMenu(self.tr("&File"))

        self.open_dir_action = QAction(self.tr("Open &Directory..."), self)
        self.open_dir_action.setShortcut(QKeySequence("Ctrl+O"))
        self.open_dir_action.triggered.connect(self.file_panel.choose_directory)
        file_menu.addAction(self.open_dir_action)

        self.open_file_action = QAction(self.tr("Open &File..."), self)
        self.open_file_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        self.open_file_action.triggered.connect(self.open_file)
        file_menu.addAction(self.open_file_action)

        file_menu.addSeparator()

        self.exit_action = QAction(self.tr("E&xit"), self)
        self.exit_action.setShortcut(QKeySequence.StandardKey.Quit)
        self.exit_action.triggered.connect(self.close)
        file_menu.addAction(self.exit_action)

        settings_menu = menubar.addMenu(self.tr("&Settings"))

        language_menu = QMenu(self.tr("&Language"), self)
        settings_menu.addMenu(language_menu)

        self.language_group = []
        for lang_code, lang_name in self._get_available_languages():
            action = QAction(lang_name, self)
            action.setData(lang_code)
            action.setCheckable(True)
            action.triggered.connect(
                lambda checked, code=lang_code: self.change_language(code)
            )
            language_menu.addAction(action)
            self.language_group.append(action)

        help_menu = menubar.addMenu(self.tr("&Help"))

        self.about_action = QAction(self.tr("&About"), self)
        self.about_action.triggered.connect(self.show_about)
        help_menu.addAction(self.about_action)

    def _create_status_bar(self):
        """Create status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(self.tr("Ready"))

    def _apply_theme(self):
        """Apply theme"""
        theme = self.config.get("theme", "system")
        if theme == "system":
            self.setStyle(QStyleFactory.create("Fusion"))
        elif theme == "dark":
            self.setStyle(QStyleFactory.create("Fusion"))
            self.setStyleSheet("""
                QMainWindow { background-color: #232629; }
                QGroupBox { color: white; }
                QLabel { color: white; }
                QTreeView { background-color: #35373a; color: white; }
                QTextEdit { background-color: #35373a; color: white; }
            """)

    def _load_settings(self):
        """Load settings"""
        current_lang = self.config.get("language", "en")
        for action in self.language_group:
            if action.data() == current_lang:
                action.setChecked(True)
                break

        last_dir = self.config.get("last_directory", "")
        if last_dir and os.path.isdir(last_dir):
            self.file_panel.set_directory(last_dir)

    def _connect_signals(self):
        """Connect panel signals"""
        self.file_panel.file_selected.connect(self.on_file_selected)
        self.file_panel.directory_changed.connect(self.on_directory_changed)
        self.function_panel.extract_requested.connect(self.on_extract_requested)
        self.function_panel.load_requested.connect(self.on_load_requested)

    def _get_available_languages(self):
        """Get available languages"""
        return [("en", "English"), ("de", "Deutsch"), ("tr", "Türkçe")]

    def change_language(self, lang_code: str):
        """Change language"""
        self.config.set("language", lang_code)
        self.config.save()

    def on_file_selected(self, file_path: str):
        """Handle file selection"""
        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            self.current_pdf = file_path
            self.function_panel.set_file(file_path)
            self.preview_panel.load_pdf(file_path)
            self.status_bar.showMessage(f"Loaded: {os.path.basename(file_path)}")
        elif ext == ".md":
            self.preview_panel.load_markdown(file_path)
            self.status_bar.showMessage(f"Loaded: {os.path.basename(file_path)}")

    def on_directory_changed(self, directory: str):
        """Handle directory change"""
        self.config.set("last_directory", directory)
        self.config.save()

    def on_extract_requested(self, pdf_path: str):
        """Handle extract request"""
        if not pdf_path:
            return

        is_valid, error_msg = validate_pdf(pdf_path)
        if not is_valid:
            QMessageBox.critical(self, self.tr("Error"), error_msg)
            return

        self.status_bar.showMessage(self.tr("Extracting annotations..."))

        try:
            output_path = extract_pdf_annotations(
                pdf_path,
                page_offset=self.function_panel.offset_spinbox.value(),
                progress_callback=self.update_progress,
            )

            with PDFProcessor(pdf_path) as processor:
                self.current_annotations = processor.extract_annotations(
                    page_offset=self.function_panel.offset_spinbox.value()
                )

            self.preview_panel.highlight_annotations(self.current_annotations, pdf_path)

            self.status_bar.showMessage(f"Annotations extracted to: {output_path}")
            QMessageBox.information(
                self,
                self.tr("Success"),
                self.tr("Annotations extracted and highlighted in preview."),
            )

        except PDFProcessingError as e:
            QMessageBox.critical(self, self.tr("Error"), str(e))
            self.status_bar.showMessage(self.tr("Error occurred"))

    def on_load_requested(self, file_path: str):
        """Handle load request"""
        self.on_file_selected(file_path)

    def update_progress(self, message: str):
        """Update progress"""
        self.status_bar.showMessage(message)
        QApplication.processEvents()

    def open_file(self):
        """Open file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            self.tr("Open File"),
            self.file_panel.dir_label.text(),
            self.tr("PDF Files (*.pdf);;Markdown Files (*.md);;All Files (*)"),
        )
        if file_path:
            self.on_file_selected(file_path)

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            self.tr("About PDF Annotation Extractor"),
            self.tr("""<h3>PDF Annotation Extractor</h3>
<p>Version 1.0.0</p>
<p>Copyright (C) 2024 Engin Karahan</p>
<p>A tool for extracting and processing PDF annotations.</p>
<p>Licensed under GNU GPL v3.</p>"""),
        )

    def closeEvent(self, event):
        """Handle close"""
        self.config.save()
        event.accept()


def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    app.setApplicationName("PDF Annotation Extractor")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("karahan.net")

    window = PDFAnnotationExtractorWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
