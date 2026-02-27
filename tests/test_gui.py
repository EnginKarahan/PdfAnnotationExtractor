#!/usr/bin/env python3
"""
PDF Annotation Extractor - GUI Tests
"""

import pytest
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest

from pdf_annotation_extractor.gui import PDFAnnotationExtractorWindow


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def main_window(qapp):
    """Create main window for testing"""
    window = PDFAnnotationExtractorWindow()
    yield window
    window.close()


class TestMainWindow:
    """Tests for main window"""

    def test_window_title(self, main_window):
        """Test window title is set"""
        assert "PDF Annotation Extractor" in main_window.windowTitle()

    def test_initial_state(self, main_window):
        """Test initial UI state"""
        assert main_window.file_path_edit.text() == ""
        assert main_window.extract_button.isEnabled()

    def test_browse_button_exists(self, main_window):
        """Test browse button exists"""
        assert main_window.browse_button is not None

    def test_offset_spinbox_exists(self, main_window):
        """Test offset spinbox exists"""
        assert main_window.offset_spinbox is not None
        assert main_window.offset_spinbox.value() == -1


class TestMenuBar:
    """Tests for menu bar"""

    def test_file_menu_exists(self, main_window):
        """Test file menu exists"""
        menubar = main_window.menuBar()
        menus = [menubar.actions()[i].text() for i in range(menubar.actions().count())]
        assert any("File" in m or "&File" in m for m in menus)

    def test_settings_menu_exists(self, main_window):
        """Test settings menu exists"""
        menubar = main_window.menuBar()
        menus = [menubar.actions()[i].text() for i in range(menubar.actions().count())]
        assert any("Settings" in m or "&Settings" in m for m in menus)

    def test_help_menu_exists(self, main_window):
        """Test help menu exists"""
        menubar = main_window.menuBar()
        menus = [menubar.actions()[i].text() for i in range(menubar.actions().count())]
        assert any("Help" in m or "&Help" in m for m in menus)


class TestStatusBar:
    """Tests for status bar"""

    def test_status_bar_exists(self, main_window):
        """Test status bar exists"""
        assert main_window.status_bar is not None

    def test_initial_status_message(self, main_window):
        """Test initial status message"""
        assert "Ready" in main_window.status_bar.currentMessage()
