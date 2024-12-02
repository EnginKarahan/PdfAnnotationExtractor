import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import os


class PDFAnnotationExtractor(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("PDF Annotations Extractor")
        self.geometry("600x400")

        # Hauptcontainer
        main_frame = ttk.Frame(self, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Dateiauswahl
        self.file_frame = ttk.LabelFrame(main_frame, text="PDF-Datei auswählen", padding="5")
        self.file_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        self.file_path = tk.StringVar()
        self.file_entry = ttk.Entry(self.file_frame, textvariable=self.file_path, width=50)
        self.file_entry.grid(row=0, column=0, padx=5)

        self.browse_button = ttk.Button(self.file_frame, text="Durchsuchen", command=self.browse_file)
        self.browse_button.grid(row=0, column=1, padx=5)

        # Offset-Einstellung
        self.offset_frame = ttk.LabelFrame(main_frame, text="Seitennummerierung", padding="5")
        self.offset_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(self.offset_frame, text="Seitenoffset:").grid(row=0, column=0, padx=5)
        self.offset_var = tk.IntVar(value=-1)
        self.offset_entry = ttk.Entry(self.offset_frame, textvariable=self.offset_var, width=5)
        self.offset_entry.grid(row=0, column=1, padx=5)
        ttk.Label(self.offset_frame, text="(-1 für automatische Erkennung)").grid(row=0, column=2, padx=5)

        # Fortschrittsanzeige
        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(main_frame, length=300, mode='determinate',
                                        variable=self.progress_var)
        self.progress.grid(row=2, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))

        # Status-Label
        self.status_var = tk.StringVar(value="Bereit")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=3, column=0, columnspan=2, pady=5)

        # Start-Button
        self.start_button = ttk.Button(main_frame, text="Annotationen extrahieren",
                                       command=self.start_extraction)
        self.start_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Konfiguriere Grid-Gewichtung
        self.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=1)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="PDF-Datei auswählen",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)

    def update_progress(self, value):
        self.progress_var.set(value)
        self.update_idletasks()

    def start_extraction(self):
        pdf_path = self.file_path.get()
        if not pdf_path:
            messagebox.showerror("Fehler", "Bitte wählen Sie eine PDF-Datei aus.")
            return

        if not os.path.exists(pdf_path):
            messagebox.showerror("Fehler", "Die ausgewählte Datei existiert nicht.")
            return

        try:
            self.status_var.set("Verarbeite PDF...")
            self.start_button.configure(state='disabled')
            self.update_idletasks()

            from pdf_utils import extract_pdf_annotations
            output_file = extract_pdf_annotations(pdf_path, self.update_progress)

            self.status_var.set("Fertig! Ausgabe gespeichert in: " + output_file)
            messagebox.showinfo("Erfolg",
                                f"Die Annotationen wurden erfolgreich extrahiert.\n\n"
                                f"Ausgabedatei: {output_file}")

        except Exception as e:
            messagebox.showerror("Fehler", f"Ein Fehler ist aufgetreten:\n{str(e)}")
            self.status_var.set("Fehler bei der Verarbeitung")

        finally:
            self.start_button.configure(state='normal')
            self.progress_var.set(0)