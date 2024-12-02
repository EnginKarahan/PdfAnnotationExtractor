#!/usr/bin/env python3
"""
PDF Annotation Extractor - Main entry point
Copyright (C) 2024  [Your Name]

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

from translations import translation_manager
from gui import PDFAnnotationExtractor

def main():
    app = PDFAnnotationExtractor()
    app.mainloop()

if __name__ == "__main__":
    main()