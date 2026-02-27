#!/usr/bin/env python3
"""
PDF Annotation Extractor - Core Tests
"""

import os
import tempfile
import pytest
from pathlib import Path

from pdf_annotation_extractor.core import (
    PDFProcessor,
    PDFAnnotation,
    PDFProcessingError,
    extract_pdf_annotations,
    validate_pdf,
    get_supported_annotation_types,
)


class TestValidatePdf:
    """Tests for PDF validation"""

    def test_nonexistent_file(self):
        """Test validation of non-existent file"""
        is_valid, error = validate_pdf("/nonexistent/file.pdf")
        assert is_valid is False
        assert "does not exist" in error

    def test_invalid_extension(self):
        """Test validation of non-PDF file"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            f.write(b"not a pdf")
            temp_path = f.name

        try:
            is_valid, error = validate_pdf(temp_path)
            assert is_valid is False
            assert "not a PDF" in error
        finally:
            os.unlink(temp_path)


class TestSupportedAnnotationTypes:
    """Tests for annotation type definitions"""

    def test_annotation_types_not_empty(self):
        """Test that annotation types are defined"""
        types = get_supported_annotation_types()
        assert len(types) > 0
        assert 0 in types
        assert types[0] == "Highlight"

    def test_all_annotation_types_mapped(self):
        """Test that all annotation types are mapped"""
        types = get_supported_annotation_types()
        for i in range(24):
            assert i in types


class TestPDFAnnotation:
    """Tests for PDFAnnotation dataclass"""

    def test_annotation_creation(self):
        """Test creating a basic annotation"""
        annot = PDFAnnotation(
            page_num=1,
            content="Test comment",
            annot_type="Highlight",
            rect=(0, 0, 100, 100),
        )
        assert annot.page_num == 1
        assert annot.content == "Test comment"
        assert annot.annot_type == "Highlight"

    def test_annotation_str(self):
        """Test annotation string representation"""
        annot = PDFAnnotation(
            page_num=1, content="Test", annot_type="Highlight", rect=(0, 0, 100, 100)
        )
        assert "[Highlight] Test" in str(annot)


class TestExtractPdfAnnotations:
    """Integration tests for annotation extraction"""

    @pytest.fixture
    def sample_pdf_path(self):
        """Path to sample PDF - using a minimal valid PDF"""
        return str(Path(__file__).parent / "fixtures" / "sample.pdf")

    def test_extract_returns_string(self):
        """Test that extract returns output path"""
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Resources<<>>>>endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
trailer<</Size 4/Root 1 0 R>>
startxref
202
%%EOF""")
            temp_path = f.name

        try:
            result = extract_pdf_annotations(temp_path)
            assert isinstance(result, str)
            assert result.endswith("_annotations.md")
        finally:
            os.unlink(temp_path)
            if os.path.exists(result):
                os.unlink(result)

    def test_extract_with_progress_callback(self):
        """Test extraction with progress callback"""
        progress_messages = []

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            f.write(b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]/Resources<<>>>>endobj
xref
0 4
trailer<</Size 4/Root 1 0 R>>
startxref
202
%%EOF""")
            temp_path = f.name

        try:
            result = extract_pdf_annotations(
                temp_path, progress_callback=lambda m: progress_messages.append(m)
            )
            assert os.path.exists(result)
        finally:
            os.unlink(temp_path)
            if os.path.exists(result):
                os.unlink(result)
