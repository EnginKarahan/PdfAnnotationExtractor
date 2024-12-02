#!/usr/bin/env python3
"""
PDF Annotation Extractor - PDF processing utilities
Copyright (C) 2024  [Ihr Name]

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
"""

import os
import fitz
from typing import Callable, Optional, List
from datetime import datetime
import re
from translations import _


class PDFProcessingError(Exception):
    """Base class for PDF processing errors"""
    pass


class PDFAnnotation:
    def __init__(self, page_num: int, content: str, type: str, rect: tuple,
                 title: Optional[str] = None,
                 creation_date: Optional[str] = None,
                 modified_date: Optional[str] = None,
                 internal_page_num: Optional[str] = None,
                 highlighted_text: Optional[str] = None):
        self.page_num = page_num
        self.content = content
        self.type = type
        self.rect = rect
        self.title = title
        self.creation_date = creation_date
        self.modified_date = modified_date
        self.internal_page_num = internal_page_num
        self.highlighted_text = highlighted_text

    def __str__(self) -> str:
        return f"[{self.type}] {self.content}"


class PDFProcessor:
    ANNOTATION_TYPES = {
        0: _("Highlight"),
        1: _("Underline"),
        2: _("StrikeOut"),
        3: _("Squiggly"),
        4: _("Rectangle/Square"),
        5: _("Circle/Ellipse"),
        6: _("Line"),
        7: _("Polyline"),
        8: _("Text/Sticky Note/Highlight"),
        9: _("Strike Out"),
        10: _("Stamp"),
        11: _("Caret"),
        12: _("Ink"),
        13: _("Popup"),
        14: _("FileAttachment"),
        15: _("Sound"),
        16: _("Movie"),
        17: _("Widget"),
        18: _("Screen"),
        19: _("PrinterMark"),
        20: _("TrapNet"),
        21: _("Watermark"),
        22: _("3D"),
        23: _("Redact")
    }

    def __init__(self, pdf_path: str):
        if not os.path.exists(pdf_path):
            raise PDFProcessingError(_("The PDF file does not exist: {0}").format(pdf_path))
        self.pdf_path = pdf_path
        self.doc = None
        self.page_offset = 0
        self.annotations: List[PDFAnnotation] = []

    def __enter__(self):
        try:
            self.doc = fitz.open(self.pdf_path)
            return self
        except Exception as e:
            raise PDFProcessingError(_("Could not open PDF file: {0}").format(str(e)))

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.doc:
            self.doc.close()

    def detect_page_offset(self) -> int:
        if not self.doc:
            raise PDFProcessingError(_("No PDF document loaded"))

        for page_num in range(min(10, self.doc.page_count)):
            page = self.doc[page_num]
            text = page.get_text()

            numbers = re.findall(r'\b\d+\b', text)
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
            return f"{_('Page')} {absolute_number} ({_('Title page/Front matter')})"
        else:
            return f"{_('Page')} {absolute_number} ({_('Internal')}: {internal_number})"

    def extract_text_from_annotation(self, page, annot, page_num) -> str:
        try:
            text = page.get_textbox(annot.rect)
            if text.strip():
                return text.strip()
        except (AttributeError, ValueError) as e:
            print(f"{_('Could not extract text for annotation on page')} {page_num + 1}: {str(e)}")
        return ""

    def extract_annotations(self,
                            page_offset: int = -1,
                            progress_callback: Optional[Callable[[str], None]] = None) -> List[PDFAnnotation]:
        if not self.doc:
            raise PDFProcessingError(_("No PDF document loaded"))

        if page_offset == -1:
            if progress_callback:
                progress_callback(_("Detecting page offset..."))
            self.page_offset = self.detect_page_offset()
        else:
            self.page_offset = page_offset

        self.annotations.clear()

        for page_num in range(self.doc.page_count):
            if progress_callback:
                progress_callback(_("Processing page {0} of {1}...").format(
                    page_num + 1, self.doc.page_count))

            page = self.doc[page_num]
            internal_page = self.get_page_numbers(page)

            for annot in page.annots():
                try:
                    content = annot.info.get("content", "").strip()
                    annot_type = self.ANNOTATION_TYPES.get(annot.type[0], _("Unknown Type"))
                    rect = annot.rect
                    title = annot.info.get("title")
                    creation_date = annot.info.get("creationDate")
                    modified_date = annot.info.get("modDate")
                    highlighted_text = None

                    if annot.type[0] in [0, 8]:  # Highlight or Text/Sticky Note/Highlight
                        highlighted_text = self.extract_text_from_annotation(page, annot, page_num)
                    elif not content and annot.type[0] in [1, 2, 3, 9]:  # Underline, StrikeOut, etc.
                        highlighted_text = self.extract_text_from_annotation(page, annot, page_num)

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
                            highlighted_text
                        )
                        self.annotations.append(annotation)

                except Exception as e:
                    if progress_callback:
                        progress_callback(_("Warning: Could not process annotation on page {0}: {1}").format(
                            page_num + 1, str(e)))

        return self.annotations

    def save_annotations(self, output_path: Optional[str] = None) -> str:
        if not output_path:
            base_name = os.path.splitext(self.pdf_path)[0]
            output_path = f"{base_name}_annotations.md"

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"# {_('PDF Annotations Export')}\n\n")
            f.write(f"**{_('File')}:** {self.pdf_path}\n")
            f.write(f"**{_('Date')}:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**{_('Total Pages')}:** {self.doc.page_count}\n")
            f.write(f"**{_('Page Numbering Starts At')}:** {1 + self.page_offset}\n")
            f.write("\n---\n\n")

            current_page = None
            for annotation in sorted(self.annotations, key=lambda x: x.page_num):
                if current_page != annotation.internal_page_num:
                    current_page = annotation.internal_page_num
                    f.write(f"\n## {current_page}\n\n")

                f.write(f"### {annotation.type}\n\n")

                if annotation.highlighted_text:
                    f.write(f"**{_('Highlighted Text')}:** {annotation.highlighted_text}\n\n")

                if annotation.content:
                    f.write(f"**{_('Comment')}:** {annotation.content}\n\n")

                if annotation.title:
                    f.write(f"**{_('Author')}:** {annotation.title}\n")

                if annotation.modified_date:
                    f.write(f"**{_('Date')}:** {annotation.modified_date}\n")

                f.write("\n---\n\n")

        return output_path


def extract_pdf_annotations(
        pdf_path: str,
        page_offset: int = -1,
        progress_callback: Optional[Callable[[str], None]] = None
) -> str:
    """
    Main function for extracting PDF annotations.
    """
    try:
        with PDFProcessor(pdf_path) as processor:
            processor.extract_annotations(page_offset, progress_callback)
            return processor.save_annotations()
    except Exception as e:
        raise PDFProcessingError(str(e))