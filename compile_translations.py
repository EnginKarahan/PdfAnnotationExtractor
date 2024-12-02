#!/usr/bin/env python3
from babel.messages import frontend as babel
import os


def main():
    # Extrahiere Strings aus Python-Dateien
    extract = babel.extract_messages()
    extract.input_paths = ['.']
    extract.output_file = 'locale/messages.pot'
    extract.keywords = ['_']
    extract.no_location = False
    extract.omit_header = False
    extract.width = 80
    extract.finalize_options()
    extract.run()

    # Aktualisiere .po Dateien für Deutsch und Türkisch
    for lang in ['de', 'tr']:
        lang_dir = os.path.join('locale', lang, 'LC_MESSAGES')
        os.makedirs(lang_dir, exist_ok=True)

        if not os.path.exists(os.path.join(lang_dir, 'messages.po')):
            # Initialisiere neue .po Datei
            init = babel.init_catalog()
            init.input_file = 'locale/messages.pot'
            init.output_dir = 'locale'
            init.locale = lang
            init.domain = 'messages'
            init.finalize_options()
            init.run()
        else:
            # Aktualisiere existierende .po Datei
            update = babel.update_catalog()
            update.input_file = 'locale/messages.pot'
            update.output_dir = 'locale'
            update.locale = lang
            update.domain = 'messages'
            update.previous = True
            update.finalize_options()
            update.run()

        # Kompiliere .po zu .mo
        compile_cmd = babel.compile_catalog()
        compile_cmd.directory = 'locale'
        compile_cmd.domain = 'messages'
        compile_cmd.locale = lang
        compile_cmd.use_fuzzy = True
        compile_cmd.finalize_options()
        compile_cmd.run()


if __name__ == '__main__':
    main()