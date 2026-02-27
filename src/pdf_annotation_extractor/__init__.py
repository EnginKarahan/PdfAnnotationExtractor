#!/usr/bin/env python3
"""
PDF Annotation Extractor
Copyright (C) 2024 Engin Karahan - https://karahan.net

A tool for extracting and processing PDF annotations.
"""

__version__ = "1.0.0"
__author__ = "Engin Karahan"
__license__ = "GPL-3.0-or-later"

from .core import (
    PDFProcessor,
    PDFAnnotation,
    PDFProcessingError,
    extract_pdf_annotations,
    validate_pdf,
    get_supported_annotation_types,
    AnnotationPlugin,
)

from .config import get_config, AppConfig, ConfigManager

from .plugins import PluginManager, PluginBase

__all__ = [
    "PDFProcessor",
    "PDFAnnotation",
    "PDFProcessingError",
    "extract_pdf_annotations",
    "validate_pdf",
    "get_supported_annotation_types",
    "AnnotationPlugin",
    "get_config",
    "AppConfig",
    "ConfigManager",
    "PluginManager",
    "PluginBase",
]
