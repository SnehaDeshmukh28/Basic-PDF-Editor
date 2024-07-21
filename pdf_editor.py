from PyPDF2 import PdfReader, PdfWriter
from tkinter import Tk, filedialog, Listbox, MULTIPLE, Frame, Scrollbar, Canvas
from tkinter import ttk
from tkinter.messagebox import showinfo, showerror

class SplashScreen:
    def __init__(self, root):
        self.root = root
        self.splash = ttk.Frame(root, padding=10)
        self.splash.pack(fill="both", expand=True)

        # Loading label
        self.label = ttk.Label(self.splash, text="Loading...", font=('Helvetica', 18))
        self.label.pack(pady=20)

        # Progress bar
        self.progress = ttk.Progressbar(self.splash, mode='indeterminate')
        self.progress.pack(pady=10, fill='x')
        self.progress.start()

        # Built by label
        self.built_by_label = ttk.Label(self.splash, text="Built by Sneha Deshmukh", font=('Helvetica', 10))
        self.built_by_label.pack(pady=10)

        # Transition to main app after a delay
        self.root.after(2000, self.show_main_app)  # Show main app after 3 seconds

    def show_main_app(self):
        self.progress.stop()
        self.splash.destroy()
        app = PDFEditor(self.root)  # Initialize the PDFEditor application

class PDFEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Editor")
        self.root.geometry("800x600")  # Set a reasonable default size

        # Apply modern styling to the root window
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f4f4f4')
        self.style.configure('TLabel', background='#f4f4f4', font=('Helvetica', 12))
        self.style.configure('TButton', font=('Helvetica', 12), padding=6)
        
        # Main frame
        self.main_frame = ttk.Frame(root, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        # Label
        self.label = ttk.Label(self.main_frame, text="Select PDF Files")
        self.label.pack(pady=5)

        # File Listbox
        self.file_listbox = Listbox(self.main_frame, selectmode=MULTIPLE, width=50, height=10, font=('Helvetica', 12))
        self.file_listbox.pack(pady=5)

        # Buttons Frame
        self.button_frame = ttk.Frame(self.main_frame)
        self.button_frame.pack(pady=10)

        # Add Button
        self.add_button = ttk.Button(self.button_frame, text="Add PDFs", command=self.add_pdfs)
        self.add_button.grid(row=0, column=0, padx=5)

        # Delete Button
        self.delete_button = ttk.Button(self.button_frame, text="Delete Pages", command=self.delete_pages)
        self.delete_button.grid(row=0, column=1, padx=5)

        # Save Button
        self.save_button = ttk.Button(self.button_frame, text="Save New PDF", command=self.save_new_pdf)
        self.save_button.grid(row=0, column=2, padx=5)

        # Merge Button
        self.merge_button = ttk.Button(self.button_frame, text="Merge PDFs", command=self.merge_pdfs)
        self.merge_button.grid(row=0, column=3, padx=5)

        # Clear Selection Button
        self.clear_selection_button = ttk.Button(self.button_frame, text="Clear Selection", command=self.clear_selection)
        self.clear_selection_button.grid(row=0, column=4, padx=5)

        # Pages Frame
        self.pages_frame = ttk.Frame(self.main_frame)
        self.pages_frame.pack(fill="both", expand=True)

        self.canvas = Canvas(self.pages_frame, bg='#ffffff')
        self.scrollbar = Scrollbar(self.pages_frame, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.pdf_pages = {}  # Maps file_name to a list of (page_num, label)
        self.selected_pages = {}  # Maps file_name to a set of selected page numbers
        self.current_pdf_writer = None  # Initialize as None

    def add_pdfs(self):
        files = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        for file in files:
            self.file_listbox.insert("end", file)
            self.display_pdf_pages(file)

    def display_pdf_pages(self, file_path):
        pdf_reader = PdfReader(file_path)
        file_name = file_path.split("/")[-1]
        self.pdf_pages[file_name] = []
        self.selected_pages[file_name] = set()  # Initialize selected pages as an empty set

        for page_num in range(len(pdf_reader.pages)):
            page_label = ttk.Label(self.scrollable_frame, text=f"{file_name} - Page {page_num + 1}")
            page_label.grid(row=page_num, column=0, sticky="w", pady=2)
            page_label.bind("<Button-1>", lambda e, lbl=page_label, fn=file_name, pn=page_num: self.toggle_selection(lbl, fn, pn))
            self.pdf_pages[file_name].append((page_num, page_label))

    def toggle_selection(self, label, file_name, page_num):
        current_color = label.cget("background")
        
        # Ensure selected_pages has an entry for the file_name
        if file_name not in self.selected_pages:
            self.selected_pages[file_name] = set()
        
        if current_color == "#f5b7b1":  # Light red
            # Unselect the page
            label.configure(background="#ffffff")  # White
            self.selected_pages[file_name].discard(page_num)  # Remove from set
        else:
            # Select the page
            label.configure(background="#f5b7b1")  # Light red
            self.selected_pages[file_name].add(page_num)  # Add to set

    def clear_selection(self):
        # Deselect all selected pages and reset the selected_pages dictionary
        for file_name, page_labels in self.pdf_pages.items():
            for page_num, label in page_labels:
                if page_num in self.selected_pages.get(file_name, set()):
                    label.configure(background="#ffffff")  # White
            self.selected_pages[file_name] = set()

    def delete_pages(self):
        selected_files = self.file_listbox.curselection()
        if not selected_files:
            showerror("Delete Pages", "No PDF selected.")
            return

        self.current_pdf_writer = PdfWriter()
        for file_index in selected_files:
            file_path = self.file_listbox.get(file_index)
            file_name = file_path.split("/")[-1]
            pdf_reader = PdfReader(file_path)

            pages_to_delete = self.selected_pages.get(file_name, set())

            if not pages_to_delete:
                showerror("Delete Pages", "No pages selected for deletion.")
                return

            for page_num in range(len(pdf_reader.pages)):
                if page_num not in pages_to_delete:
                    self.current_pdf_writer.add_page(pdf_reader.pages[page_num])

        showinfo("Delete Pages", "Pages marked for deletion. Click 'Save New PDF' to save the changes.")

    def save_new_pdf(self):
        if not self.current_pdf_writer:
            showerror("Save PDF", "No modifications to save.")
            return

        output_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if output_path:
            try:
                with open(output_path, 'wb') as output_pdf:
                    self.current_pdf_writer.write(output_pdf)
                showinfo("Save PDF", "New PDF saved successfully.")
            except Exception as e:
                showerror("Save PDF", f"Error saving PDF: {e}")
        else:
            showerror("Save PDF", "No output file specified.")

    def merge_pdfs(self):
        selected_files = self.file_listbox.curselection()
        if not selected_files:
            showerror("Merge PDFs", "No PDFs selected for merging.")
            return

        pdf_writer = PdfWriter()
        for file_index in selected_files:
            file_path = self.file_listbox.get(file_index)
            pdf_reader = PdfReader(file_path)
            for page_num in range(len(pdf_reader.pages)):
                pdf_writer.add_page(pdf_reader.pages[page_num])

        output_path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if output_path:
            try:
                with open(output_path, 'wb') as output_pdf:
                    pdf_writer.write(output_pdf)
                showinfo("Merge PDFs", "PDFs merged successfully and saved as new PDF.")
            except Exception as e:
                showerror("Merge PDFs", f"Error merging PDFs: {e}")
        else:
            showerror("Merge PDFs", "No output file specified.")

if __name__ == "__main__":
    root = Tk()
    SplashScreen(root)  # Show splash screen before main app
    root.mainloop()
