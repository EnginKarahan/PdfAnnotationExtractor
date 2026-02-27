#!/bin/bash

# Dieses Skript startet die pdfcomments-Anwendung in ihrer korrekten Anaconda/Conda-Umgebung.

# 1. In das Verzeichnis des Skripts wechseln
# Dies stellt sicher, dass das Skript von überall aus korrekt ausgeführt werden kann.
cd "$(dirname "$0")"

# 2. Die Conda-Shell-Funktionen initialisieren
# Dieser Befehl macht den 'conda'-Befehl im Skript verfügbar.
source ~/anaconda3/etc/profile.d/conda.sh

# 3. Die Conda-Umgebung 'pdfcomments' aktivieren
# Conda verwendet einen einfachen Befehl mit dem Namen der Umgebung.
echo "Aktiviere Conda-Umgebung 'pdfcomments'..."
conda activate pdfcomments

# 4. Die Python-Anwendung als Modul starten
# KORREKTUR: Wir verwenden 'python -m', damit relative Imports funktionieren.
echo "Starte die Anwendung..."
python -m src.pdf_annotation_extractor.main

# 5. Nach dem Beenden der App
echo "Anwendung wurde beendet."
