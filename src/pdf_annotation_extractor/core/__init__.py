#!/usr/bin/env python3
"""
PDF Annotation Extractor - Core Engine
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

import os
import re
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional, List, Protocol, runtime_checkable
from dataclasses import dataclass, field
from enum import Enum, auto

import fitz


class PDFProcessingError(Exception):
    """Base class for PDF processing errors"""

    pass


@dataclass
class PDFAnnotation:
    page_num: int
    content: str
    annot_type: str
    rect: tuple
    title: Optional[str] = None
    creation_date: Optional[str] = None
    modified_date: Optional[str] = None
    internal_page_num: Optional[str] = None
    highlighted_text: Optional[str] = None

    def __str__(self) -> str:
        return f"[{self.annot_type}] {self.content}"


class AnnotationType(Enum):
    HIGHLIGHT = 0
    UNDERLINE = 1
    STRIKEOUT = 2
    SQUIGGLY = 3
    RECTANGLE = 4
    CIRCLE = 5
    LINE = 6
    POLYLINE = 7
    TEXT = 8
    STRIKE_OUT = 9
    STAMP = 10
    CARET = 11
    INK = 12
    POPUP = 13
    FILEATTACHMENT = 14
    SOUND = 15
    MOVIE = 16
    WIDGET = 17
    SCREEN = 18
    PRINTERMARK = 19
    TRAPNET = 20
    WATERMARK = 21
    REDACT_3D = 22
    REDACT = 23

    @classmethod
    def from_number(cls, num: int) -> "AnnotationType":
        try:
            return cls(num)
        except ValueError:
            return cls.WIDGET


@runtime_checkable
class AnnotationPlugin(Protocol):
    """Protocol for annotation processing plugins"""

    @property
    def name(self) -> str:
        """Plugin name"""
        ...

    @property
    def version(self) -> str:
        """Plugin version"""
        ...

    def process(
        self, annotations: List[PDFAnnotation], context: dict
    ) -> List[PDFAnnotation]:
        """Process annotations"""
        ...

    def supports_format(self, output_format: str) -> bool:
        """Check if plugin supports output format"""
        ...


class PDFProcessor:
    ANNOTATION_TYPES = {
        0: "Highlight",
        1: "Underline",
        2: "StrikeOut",
        3: "Squiggly",
        4: "Rectangle/Square",
        5: "Circle/Ellipse",
        6: "Line",
        7: "Polyline",
        8: "Text/Sticky Note/Highlight",
        9: "Strike Out",
        10: "Stamp",
        11: "Caret",
        12: "Ink",
        13: "Popup",
        14: "FileAttachment",
        15: "Sound",
        16: "Movie",
        17: "Widget",
        18: "Screen",
        19: "PrinterMark",
        20: "TrapNet",
        21: "Watermark",
        22: "3D",
        23: "Redact",
    }

    def __init__(self, pdf_path: str):
        if not os.path.exists(pdf_path):
            raise PDFProcessingError(f"The PDF file does not exist: {pdf_path}")
        self.pdf_path = pdf_path
        self.doc: Optional[fitz.Document] = None
        self.page_offset = 0
        self.plugins: List[AnnotationPlugin] = []
        self._progress_callback: Optional[Callable[[str], None]] = None

    def __enter__(self):
        try:
            self.doc = fitz.open(self.pdf_path)
            return self
        except Exception as e:
            raise PDFProcessingError(f"Could not open PDF file: {e}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.doc:
            self.doc.close()

    def register_plugin(self, plugin: AnnotationPlugin) -> None:
        """Register a plugin for annotation processing"""
        if isinstance(plugin, AnnotationPlugin):
            self.plugins.append(plugin)

    def remove_plugin(self, plugin_name: str) -> None:
        """Remove a plugin by name"""
        self.plugins = [p for p in self.plugins if p.name != plugin_name]

    def detect_page_offset(self) -> int:
        if not self.doc:
            raise PDFProcessingError("No PDF document loaded")

        for page_num in range(min(10, self.doc.page_count)):
            page = self.doc[page_num]
            text = page.get_text()

            numbers = re.findall(r"\b\d+\b", text)
            for number in numbers:
                try:
                    doc_page_num = int(number)
                    if doc_page_num > 0 and abs(doc_page_num - (page_num + 1)) <= 2:
                        return doc_page_num - (page_num + 1)
                except ValueError:
                    continue

        return -1

    def get_page_numbers(self, page) -> str:
        absolute_number = page.number + 1
        internal_number = absolute_number + self.page_offset

        if internal_number <= 0:
            return f"Page {absolute_number} (Title page/Front matter)"
        else:
            return f"Page {absolute_number} (Internal: {internal_number})"

    def extract_text_from_annotation(self, page, annot, page_num) -> str:
        try:
            text = page.get_textbox(annot.rect)
            if text.strip():
                return text.strip()
        except (AttributeError, ValueError) as e:
            print(f"Could not extract text for annotation on page {page_num + 1}: {e}")
        return ""

    def extract_annotations(
        self,
        page_offset: int = -1,
        progress_callback: Optional[Callable[[str], None]] = None,
    ) -> List[PDFAnnotation]:
        if not self.doc:
            raise PDFProcessingError("No PDF document loaded")

        self._progress_callback = progress_callback

        if page_offset == -1:
            if progress_callback:
                progress_callback("Detecting page offset...")
            self.page_offset = self.detect_page_offset()
        else:
            self.page_offset = page_offset

        annotations: List[PDFAnnotation] = []

        for page_num in range(self.doc.page_count):
            if progress_callback:
                progress_callback(
                    f"Processing page {page_num + 1} of {self.doc.page_count}..."
                )

            page = self.doc[page_num]
            internal_page = self.get_page_numbers(page)

            for annot in page.annots():
                try:
                    content = annot.info.get("content", "").strip()
                    annot_type = self.ANNOTATION_TYPES.get(
                        annot.type[0], "Unknown Type"
                    )
                    rect = annot.rect
                    title = annot.info.get("title")
                    creation_date = annot.info.get("creationDate")
                    modified_date = annot.info.get("modDate")
                    highlighted_text = None

                    if annot.type[0] in [0, 8]:
                        highlighted_text = self.extract_text_from_annotation(
                            page, annot, page_num
                        )
                    elif not content and annot.type[0] in [1, 2, 3, 9]:
                        highlighted_text = self.extract_text_from_annotation(
                            page, annot, page_num
                        )

                    if content or highlighted_text:
                        annotation = PDFAnnotation(
                            page_num + 1,
                            content,
                            annot_type,
                            rect,
                            title,
                            creation_date,
                            modified_date,
                            internal_page,
                            highlighted_text,
                        )
                        annotations.append(annotation)

                except Exception as e:
                    if progress_callback:
                        progress_callback(
                            f"Warning: Could not process annotation on page {page_num + 1}: {e}"
                        )

        for plugin in self.plugins:
            try:
                context = {
                    "pdf_path": self.pdf_path,
                    "page_count": self.doc.page_count,
                    "page_offset": self.page_offset,
                }
                annotations = plugin.process(annotations, context)
            except Exception as e:
                if progress_callback:
                    progress_callback(f"Plugin {plugin.name} error: {e}")

        return annotations

    def save_annotations(
        self,
        annotations: List[PDFAnnotation],
        output_path: Optional[str] = None,
        output_format: str = "markdown",
    ) -> str:
        if not output_path:
            base_name = os.path.splitext(self.pdf_path)[0]
            output_path = f"{base_name}_annotations.md"

        if output_format == "markdown":
            return self._save_markdown(annotations, output_path)
        else:
            raise PDFProcessingError(f"Unsupported output format: {output_format}")

    def _save_markdown(self, annotations: List[PDFAnnotation], output_path: str) -> str:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(f"# PDF Annotations Export\n\n")
            f.write(f"**File:** {self.pdf_path}\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Total Pages:** {self.doc.page_count if self.doc else 'N/A'}\n")
            f.write(f"**Page Numbering Starts At:** {1 + self.page_offset}\n")
            f.write("\n---\n\n")

            current_page = None
            for annotation in sorted(annotations, key=lambda x: x.page_num):
                if current_page != annotation.internal_page_num:
                    current_page = annotation.internal_page_num
                    f.write(f"\n## {current_page}\n\n")

                f.write(f"### {annotation.annot_type}\n\n")

                if annotation.highlighted_text:
                    f.write(f"**Highlighted Text:** {annotation.highlighted_text}\n\n")

                if annotation.content:
                    f.write(f"**Comment:** {annotation.content}\n\n")

                if annotation.title:
                    f.write(f"**Author:** {annotation.title}\n")

                if annotation.modified_date:
                    f.write(f"**Date:** {annotation.modified_date}\n")

                f.write("\n---\n\n")

        return output_path


def extract_pdf_annotations(
    pdf_path: str,
    page_offset: int = -1,
    progress_callback: Optional[Callable[[str], None]] = None,
    plugins: Optional[List[AnnotationPlugin]] = None,
) -> str:
    """Main function for extracting PDF annotations."""
    try:
        with PDFProcessor(pdf_path) as processor:
            if plugins:
                for plugin in plugins:
                    processor.register_plugin(plugin)
            annotations = processor.extract_annotations(page_offset, progress_callback)
            return processor.save_annotations(annotations)
    except Exception as e:
        raise PDFProcessingError(str(e))


def get_supported_annotation_types() -> dict:
    """Return dictionary of supported annotation types"""
    return PDFProcessor.ANNOTATION_TYPES.copy()


def validate_pdf(pdf_path: str) -> tuple[bool, Optional[str]]:
    """Validate if a file is a valid PDF"""
    if not os.path.exists(pdf_path):
        return False, f"File does not exist: {pdf_path}"

    if not pdf_path.lower().endswith(".pdf"):
        return False, "File is not a PDF"

    try:
        doc = fitz.open(pdf_path)
        page_count = doc.page_count
        doc.close()
        if page_count == 0:
            return False, "PDF has no pages"
        return True, None
    except Exception as e:
        return False, f"Cannot open PDF: {e}"
