import fitz
import os
import re


def get_annotation_type(annot_type):
    types = {
        0: "Highlight",
        1: "Underline",
        2: "StrikeOut",
        3: "Squiggly",
        4: "Rectangle/Square",
        5: "Circle/Ellipse",
        6: "Line",
        7: "Polyline",
        8: "Text/Sticky Note/Highlight",
        9: "Strike Out",
        10: "Stamp",
        11: "Caret",
        12: "Ink",
        13: "Popup",
        14: "FileAttachment",
        15: "Sound",
        16: "Movie",
        17: "Widget",
        18: "Screen",
        19: "PrinterMark",
        20: "TrapNet",
        21: "Watermark",
        22: "3D",
        23: "Redact"
    }
    return types.get(annot_type[0], "Unbekannter Typ")


def detect_page_number_offset(doc):
    """Ermittelt den Offset zwischen absoluter und dokumentinterner Seitennummerierung"""
    for page_num in range(min(10, len(doc))):  # Prüfe die ersten 10 Seiten oder weniger
        page = doc[page_num]
        text = page.get_text()

        # Suche nach Seitenzahlen im Text
        numbers = re.findall(r'\b\d+\b', text)
        for number in numbers:
            try:
                doc_page_num = int(number)
                if doc_page_num > 0 and abs(doc_page_num - (page_num + 1)) <= 2:
                    return doc_page_num - (page_num + 1)
            except ValueError:
                continue

    return -1  # Standard-Offset, wenn keine eindeutige Erkennung möglich ist


def get_page_numbers(page, page_offset):
    """Gibt sowohl die absolute als auch die dokumentinterne Seitenzahl zurück"""
    absolute_number = page.number + 1  # Absolute Seitenzahl (beginnt bei 1)
    internal_number = absolute_number + page_offset

    if internal_number <= 0:
        return f"Seite {absolute_number} (Titelseite/Vorspann)"
    else:
        return f"Seite {absolute_number} (Dokumentintern: {internal_number})"


def write_annotation_info(md_file, annot):
    """Schreibt die gemeinsamen Annotationsinformationen in die Markdown-Datei"""
    if annot.info.get('title'):
        md_file.write(f"**Autor:** {annot.info['title']}\n")
    if annot.info.get('modDate'):
        md_file.write(f"**Datum:** {annot.info['modDate']}\n")
    if annot.info.get('content'):
        md_file.write(f"**Kommentar:** {annot.info['content']}\n")


def extract_text_from_annotation(page, annot, page_num):
    """Extrahiert Text aus einer Annotation"""
    try:
        text = page.get_textbox(annot.rect)
        if text.strip():
            return f"**Markierter Text:** {text.strip()}\n"
    except (AttributeError, ValueError) as e:
        print(f"Konnte Text für Annotation auf Seite {page_num + 1} nicht extrahieren: {str(e)}")
    return ""


def get_page_count(doc):
    """Ermittelt die tatsächliche Seitenzahl"""
    return len(doc)


def extract_pdf_annotations(pdf_path, callback=None):
    """
    Extrahiert PDF-Annotationen und speichert sie in einer Markdown-Datei
    callback: Optionale Funktion für Fortschrittsanzeige in der GUI
    """
    doc = fitz.open(pdf_path)
    output_file = os.path.splitext(pdf_path)[0] + '.md'

    total_pages = get_page_count(doc)
    page_offset = detect_page_number_offset(doc)

    with open(output_file, 'w', encoding='utf-8') as md_file:
        md_file.write(f"# Annotationen aus {os.path.basename(pdf_path)}\n\n")
        md_file.write("## Dokumentinformationen\n\n")
        md_file.write(f"- Gesamtseitenzahl: {total_pages}\n")
        md_file.write(f"- Seitennummerierung beginnt bei: {1 + page_offset}\n\n")
        md_file.write("---\n\n")

        for page_num in range(total_pages):
            if callback:
                progress = int((page_num + 1) * 100 / total_pages)
                callback(progress)

            try:
                page = doc[page_num]
                annots = list(page.annots())
                if annots:
                    md_file.write(f"## {get_page_numbers(page, page_offset)}\n\n")

                    for annot in annots:
                        is_highlight = annot.type[0] in [0, 8]

                        if is_highlight:
                            md_file.write("### Highlight/Kommentar\n")
                            extracted_text = extract_text_from_annotation(page, annot, page_num)
                            if extracted_text:
                                md_file.write(extracted_text + "\n")

                            write_annotation_info(md_file, annot)
                            md_file.write("\n---\n\n")
                        else:
                            annot_type = get_annotation_type(annot.type)
                            md_file.write(f"### {annot_type}\n")

                            write_annotation_info(md_file, annot)

                            if annot.type[0] in [1, 2, 3, 9]:
                                extracted_text = extract_text_from_annotation(page, annot, page_num)
                                if extracted_text:
                                    md_file.write(extracted_text)

                            md_file.write("\n---\n\n")
            except IndexError:
                print(f"Warnung: Konnte Seite {page_num + 1} nicht verarbeiten")
                continue

    doc.close()
    return output_file