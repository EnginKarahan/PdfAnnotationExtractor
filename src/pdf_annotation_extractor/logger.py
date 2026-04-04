#!/usr/bin/env python3
"""
PDF Annotation Extractor - Logging Module
Copyright (C) 2024 Engin Karahan

Optional logging wrapper - print() remains as default fallback.
"""

import logging
import sys
from typing import Optional


_logger: Optional[logging.Logger] = None
_debug_enabled: bool = False


def set_debug(enabled: bool) -> None:
    """Enable or disable debug logging"""
    global _debug_enabled
    _debug_enabled = enabled
    if _logger:
        _logger.setLevel(logging.DEBUG if enabled else logging.WARNING)


def get_logger(name: str = "pdf_annotation_extractor") -> logging.Logger:
    """Get or create logger instance"""
    global _logger

    if _logger is None:
        _logger = logging.getLogger(name)
        _logger.setLevel(logging.WARNING)

        if not _logger.handlers:
            handler = logging.StreamHandler(sys.stderr)
            handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
            _logger.addHandler(handler)

    return _logger


def debug(message: str) -> None:
    """Log debug message (only if debug enabled)"""
    if _debug_enabled:
        get_logger().debug(message)


def info(message: str) -> None:
    """Log info message"""
    get_logger().info(message)


def warning(message: str) -> None:
    """Log warning message"""
    get_logger().warning(message)


def error(message: str) -> None:
    """Log error message"""
    get_logger().error(message)
