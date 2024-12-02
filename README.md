# PDF Annotation Extractor

A tool for extracting and processing PDF annotations.

![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)
![Platform](https://img.shields.io/badge/platform-windows%20%7C%20linux%20%7C%20macos-lightgrey)

## Description

This program allows you to extract annotations from PDF files and save them in a structured format. It features a user-friendly graphical interface and supports various annotation types.

## Features

- Extract PDF annotations
- User-friendly graphical interface
- Progress tracking
- Automatic page numbering detection
- Batch processing support
- Export to structured text format

## Installation

### From Source

# Clone the repository
git clone https://github.com/EnginKarahan/pdf-annotation-extractor.git

# Change into the directory
cd pdf-annotation-extractor

# Install dependencies
pip install -r requirements.txt

### Using pip

pip install pdf-annotation-extractor

## Usage

### Graphical Interface

python main.py

Or use the pre-compiled executable from the releases section.

### Command Line Interface

python pdf_utils.py input.pdf

## Dependencies

- Python 3.x
- PyMuPDF
- tkinter (included in most Python distributions)

## Building

To create a standalone executable:

python -m PyInstaller --onefile --windowed main.py

## Documentation

For detailed documentation, please visit the [Wiki](https://github.com/EnginKarahan/pdf-annotation-extractor/wiki).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Author

Engin Karahan - engin.karahan@gmail.com

## Acknowledgments

- PyMuPDF developers for their excellent PDF processing library
- All contributors and users of this project

## Support

If you encounter any problems or have suggestions, please [open an issue](https://github.com/EnginKarahan/pdf-annotation-extractor/issues).