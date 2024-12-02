import fitz
import os


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


def get_page_labels(doc):
    """Versucht, die logische Seitennummerierung aus dem PDF zu extrahieren"""
    try:
        page_labels = doc.get_page_labels()
        return page_labels
    except:
        return None


def get_page_number_string(doc, page_num, page_labels):
    """Erstellt einen Seitenzahl-String mit absoluter und (wenn verfügbar) logischer Seitennummer"""
    abs_num = page_num + 1  # Absolute Seitenzahl (1-basiert)

    if page_labels and page_num < len(page_labels):
        logical_num = page_labels[page_num]
        if logical_num != str(abs_num):  # Nur anzeigen wenn unterschiedlich
            return f"Seite {abs_num} (Print: {logical_num})"

    return f"Seite {abs_num}"


def extract_pdf_annotations(pdf_path):
    doc = fitz.open(pdf_path)
    output_file = os.path.splitext(pdf_path)[0] + '.md'

    # Hole Seitenlabels
    page_labels = get_page_labels(doc)

    with open(output_file, 'w', encoding='utf-8') as md_file:
        md_file.write(f"# Annotationen aus {os.path.basename(pdf_path)}\n\n")

        # Dokumentinformationen ausgeben
        md_file.write("## Dokumentinformationen\n\n")
        md_file.write(f"- Gesamtseitenzahl: {len(doc)}\n")
        if page_labels:
            md_file.write("- Seitennummerierung: Das Dokument verwendet eine separate Print-Seitennummerierung\n")
        md_file.write("\n---\n\n")

        for page_num in range(len(doc)):
            page = doc[page_num]
            annotations_on_page = False

            # Alle Annotationen auf der Seite
            annots = list(page.annots())
            if annots:
                annotations_on_page = True
                # Verwende die neue Funktion für die Seitenzahl-Ausgabe
                md_file.write(f"## {get_page_number_string(doc, page_num, page_labels)}\n\n")

                for annot in annots:
                    # Debug-Print
                    print(f"Verarbeite Annotation: Typ={annot.type}")

                    # Prüfe auf Highlight-Typ (entweder type[0] == 0 oder type[0] == 8)
                    is_highlight = annot.type[0] in [0, 8]

                    if is_highlight:
                        md_file.write("### Highlight/Kommentar\n")

                        # Extrahiere den markierten Text
                        text = page.get_text("text", clip=annot.rect).strip()
                        if text:
                            md_file.write(f"**Markierter Text:** {text}\n\n")

                        # Zusätzliche Informationen
                        if annot.info.get('title'):
                            md_file.write(f"**Autor:** {annot.info['title']}\n")
                        if annot.info.get('modDate'):
                            md_file.write(f"**Datum:** {annot.info['modDate']}\n")
                        if annot.info.get('content'):
                            md_file.write(f"**Kommentar:** {annot.info['content']}\n")

                        md_file.write("\n---\n\n")
                    else:
                        # Andere Annotationstypen
                        annot_type = get_annotation_type(annot.type)
                        md_file.write(f"### {annot_type}\n")

                        if annot.info.get('title'):
                            md_file.write(f"**Autor:** {annot.info['title']}\n")
                        if annot.info.get('modDate'):
                            md_file.write(f"**Datum:** {annot.info['modDate']}\n")
                        if annot.info.get('content'):
                            md_file.write(f"**Kommentar:** {annot.info['content']}\n")

                        # Für textbasierte Annotationen
                        if annot.type[0] in [1, 2, 3, 9]:
                            text = page.get_text("text", clip=annot.rect)
                            if text.strip():
                                md_file.write(f"**Markierter Text:** {text.strip()}\n")

                        md_file.write("\n---\n\n")

    doc.close()
    print(f"Annotationen wurden in {output_file} gespeichert.")


# Skript ausführen
pdf_file = "Kaupert2024.pdf"
extract_pdf_annotations(pdf_file)