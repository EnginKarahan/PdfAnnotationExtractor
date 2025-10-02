#!/usr/bin/env python3
"""Hilfsskript zum Extrahieren, Aktualisieren und Kompilieren der Übersetzungen."""

import os
from pathlib import Path
from babel.messages import frontend as babel


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    locale_dir = base_dir / "locale"

    locale_dir.mkdir(parents=True, exist_ok=True)

    # 1) Strings aus dem Paket extrahieren
    extract = babel.extract_messages()
    extract.input_paths = [str(base_dir)]
    extract.output_file = str(locale_dir / "messages.pot")
    extract.keywords = ["_"]
    extract.no_location = False
    extract.omit_header = False
    extract.width = 80
    extract.finalize_options()
    extract.run()

    # 2) .po-Dateien für alle gewünschten Sprachen aktualisieren/erstellen
    for lang in ("de", "tr"):
        lang_dir = locale_dir / lang / "LC_MESSAGES"
        lang_dir.mkdir(parents=True, exist_ok=True)
        po_file = lang_dir / "messages.po"

        if not po_file.exists():
            init = babel.init_catalog()
            init.input_file = str(locale_dir / "messages.pot")
            init.output_dir = str(locale_dir)
            init.locale = lang
            init.domain = "messages"
            init.finalize_options()
            init.run()
        else:
            update = babel.update_catalog()
            update.input_file = str(locale_dir / "messages.pot")
            update.output_dir = str(locale_dir)
            update.locale = lang
            update.domain = "messages"
            update.previous = True
            update.finalize_options()
            update.run()

        # 3) .mo-Datei kompilieren
        compile_cmd = babel.compile_catalog()
        compile_cmd.directory = str(locale_dir)
        compile_cmd.domain = "messages"
        compile_cmd.locale = lang
        compile_cmd.use_fuzzy = True
        compile_cmd.finalize_options()
        compile_cmd.run()


if __name__ == "__main__":
    main()