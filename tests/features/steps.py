#!/usr/bin/env python3
"""
BDD Step Definitions for PDF Annotation Extractor
"""

import os
import tempfile
from behave import given, when, then
from pathlib import Path

from pdf_annotation_extractor.core import extract_pdf_annotations, PDFProcessingError


@given("a PDF file with annotations exists")
def step_pdf_file_with_annotations(context):
    """Create a minimal valid PDF file"""
    context.temp_dir = tempfile.mkdtemp()
    context.pdf_path = os.path.join(context.temp_dir, "test.pdf")

    with open(context.pdf_path, "wb") as f:
        f.write(b"""%PDF-1.4
1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj
2 0 obj<</Type/Pages/Kids[3 0 R]/Count 1>>endobj
3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 612 792]>>endobj
xref
0 4
trailer<</Size 4/Root 1 0 R>>
startxref
202
%%EOF""")


@given("no PDF file is selected")
def step_no_pdf_selected(context):
    """Set context to no file selected"""
    context.pdf_path = ""


@when("the user selects the file and clicks Extract")
def step_extract_annotations(context):
    """Extract annotations from PDF"""
    if context.pdf_path:
        context.output_path = extract_pdf_annotations(context.pdf_path)
    else:
        raise PDFProcessingError("No file selected")


@when("the user clicks Extract")
def step_click_extract(context):
    """Try to extract without file"""
    try:
        extract_pdf_annotations(context.pdf_path)
    except PDFProcessingError as e:
        context.error_message = str(e)


@then("a markdown file should be created with all annotations")
def step_markdown_created(context):
    """Check that output file exists"""
    assert os.path.exists(context.output_path)
    assert context.output_path.endswith("_annotations.md")


@then("an error message should be displayed")
def step_error_displayed(context):
    """Check error message"""
    assert hasattr(context, "error_message")
    assert (
        "No file" in context.error_message
        or "not found" in context.error_message.lower()
    )


@when("the user sets page offset to {offset}")
def step_set_page_offset(context, offset):
    """Set page offset"""
    context.page_offset = int(offset)


@then("the output should reflect the custom page offset")
def step_verify_page_offset(context):
    """Verify page offset in output"""
    output = extract_pdf_annotations(context.pdf_path, page_offset=context.page_offset)
    with open(output, "r") as f:
        content = f.read()
    assert str(context.page_offset + 1) in content
