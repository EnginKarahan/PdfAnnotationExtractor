#!/usr/bin/env python3
"""
PDF Annotation Extractor - Main Entry Point
Copyright (C) 2024 Engin Karahan - https://karahan.net
"""

import sys


def main():
    """Main entry point"""
    from pdf_annotation_extractor.gui import main as gui_main

    gui_main()


if __name__ == "__main__":
    main()
