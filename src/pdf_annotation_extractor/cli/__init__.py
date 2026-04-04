#!/usr/bin/env python3
"""
PDF Annotation Extractor - Command Line Interface
Copyright (C) 2024 Engin Karahan
"""

import sys
import argparse
from pathlib import Path
from typing import Optional

from ..core import extract_pdf_annotations, validate_pdf, PDFProcessingError
from ..logger import set_debug


def create_parser() -> argparse.ArgumentParser:
    """Create the CLI argument parser"""
    parser = argparse.ArgumentParser(
        prog="pdf-annotation-extractor",
        description="Extract annotations from PDF files and save them as Markdown.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf
  %(prog)s document.pdf -o output.md
  %(prog)s document.pdf --offset 0
  %(prog)s document.pdf --page-offset -1 --verbose

For more information, visit: https://github.com/EnginKarahan/PdfAnnotationExtractor
        """,
    )

    parser.add_argument("input", type=str, help="Path to the input PDF file")

    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default=None,
        help="Path to the output file (default: <input>_annotations.md)",
    )

    parser.add_argument(
        "-p",
        "--page-offset",
        type=int,
        default=-1,
        dest="page_offset",
        help="Page offset for internal page numbering (-1 for automatic detection, default: -1)",
    )

    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")

    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug output")

    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    return parser


def print_progress(message: str) -> None:
    """Print progress message"""
    print(f"[INFO] {message}", file=sys.stderr)


def main(argv: Optional[list] = None) -> int:
    """Main entry point for CLI"""
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.debug:
        set_debug(True)

    input_path = Path(args.input)

    if not input_path.exists():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        return 1

    is_valid, error_msg = validate_pdf(str(input_path))
    if not is_valid:
        print(f"Error: {error_msg}", file=sys.stderr)
        return 1

    try:
        progress_callback = print_progress if args.verbose else None

        output_path = extract_pdf_annotations(
            str(input_path),
            page_offset=args.page_offset,
            progress_callback=progress_callback,
        )

        print(f"Annotations extracted successfully to: {output_path}")
        return 0

    except PDFProcessingError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        if args.verbose or args.debug:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
