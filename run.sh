#!/bin/bash
# PDF Annotation Extractor - Start Script

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Prüfen ob PyQt6 installiert ist
if ! python3 -c "import PyQt6" 2>/dev/null; then
    echo "PyQt6 wird installiert..."
    pip install PyQt6 PyMuPDF
fi

# Anwendung starten
cd "$SCRIPT_DIR"
python3 -m pdf_annotation_extractor.gui
