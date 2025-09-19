#!/usr/bin/env python3
"""
PDF Data Extraction Tool - GUI Version
User-friendly interface for extracting core functionality data from PDF documents
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from pathlib import Path
import sys

# Import our PDF extractor
try:
    from pdf_extractor import PDFExtractor
except ImportError:
    messagebox.showerror("Import Error", "Could not import pdf_extractor module")
    sys.exit(1)


class PDFExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Data Extractor")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variables
        self.pdf_directory = tk.StringVar(value="pdfs")
        self.output_file = tk.StringVar(value="extracted_data.xlsx")
        self.is_processing = False
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="PDF Data Extractor", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # PDF Directory Selection
        ttk.Label(main_frame, text="PDF Directory:").grid(row=1, column=0, sticky=tk.W, pady=5)
        
        dir_frame = ttk.Frame(main_frame)
        dir_frame.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        dir_frame.columnconfigure(0, weight=1)
        
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.pdf_directory, width=50)
        self.dir_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(dir_frame, text="Browse", 
                  command=self.browse_directory).grid(row=0, column=1)
        
        # Output File Selection
        ttk.Label(main_frame, text="Output File:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=2, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        output_frame.columnconfigure(0, weight=1)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_file, width=50)
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(output_frame, text="Browse", 
                  command=self.browse_output_file).grid(row=0, column=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                          mode='indeterminate')
        self.progress_bar.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), 
                              pady=(20, 10))
        
        # Status label
        self.status_var = tk.StringVar(value="Ready to process PDF files")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var)
        self.status_label.grid(row=4, column=0, columnspan=3, pady=5)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        self.process_button = ttk.Button(button_frame, text="Extract Data", 
                                        command=self.start_processing, 
                                        style='Accent.TButton')
        self.process_button.pack(side=tk.LEFT, padx=5)
        
        self.preview_button = ttk.Button(button_frame, text="Preview Files", 
                                        command=self.preview_files)
        self.preview_button.pack(side=tk.LEFT, padx=5)
        
        self.open_output_button = ttk.Button(button_frame, text="Open Output", 
                                           command=self.open_output_file)
        self.open_output_button.pack(side=tk.LEFT, padx=5)
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="Processing Log", padding="5")
        log_frame.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), 
                      pady=(20, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main_frame row weights
        main_frame.rowconfigure(6, weight=1)
        
    def browse_directory(self):
        """Browse for PDF directory"""
        directory = filedialog.askdirectory(
            title="Select PDF Directory",
            initialdir=self.pdf_directory.get() if os.path.exists(self.pdf_directory.get()) else "."
        )
        if directory:
            self.pdf_directory.set(directory)
            self.log_message(f"Selected PDF directory: {directory}")
            
    def browse_output_file(self):
        """Browse for output file location"""
        filename = filedialog.asksaveasfilename(
            title="Save Excel file as",
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=self.output_file.get()
        )
        if filename:
            self.output_file.set(filename)
            self.log_message(f"Output file set to: {filename}")
            
    def preview_files(self):
        """Preview PDF files in the selected directory"""
        pdf_dir = Path(self.pdf_directory.get())
        
        if not pdf_dir.exists():
            messagebox.showerror("Error", f"Directory '{pdf_dir}' does not exist")
            return
            
        pdf_files = list(pdf_dir.glob("*.pdf"))
        
        if not pdf_files:
            messagebox.showinfo("No Files", f"No PDF files found in '{pdf_dir}'")
            return
            
        # Create preview window
        preview_window = tk.Toplevel(self.root)
        preview_window.title("PDF Files Preview")
        preview_window.geometry("600x400")
        
        # Create treeview for file list
        tree_frame = ttk.Frame(preview_window, padding="10")
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        tree = ttk.Treeview(tree_frame, columns=('size', 'modified'), show='tree headings')
        tree.heading('#0', text='Filename')
        tree.heading('size', text='Size (KB)')
        tree.heading('modified', text='Modified')
        
        # Add files to tree
        for pdf_file in pdf_files:
            try:
                stat = pdf_file.stat()
                size_kb = round(stat.st_size / 1024, 1)
                modified = os.path.getmtime(pdf_file)
                modified_str = pd.to_datetime(modified, unit='s').strftime('%Y-%m-%d %H:%M')
                
                tree.insert('', tk.END, text=pdf_file.name, 
                           values=(size_kb, modified_str))
            except Exception as e:
                tree.insert('', tk.END, text=pdf_file.name, 
                           values=("Error", str(e)))
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
        
        # Summary label
        summary_label = ttk.Label(preview_window, 
                                 text=f"Found {len(pdf_files)} PDF files")
        summary_label.pack(pady=10)
        
    def log_message(self, message):
        """Add message to log area"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def update_status(self, status):
        """Update status label"""
        self.status_var.set(status)
        self.root.update_idletasks()
        
    def start_processing(self):
        """Start the PDF processing in a separate thread"""
        if self.is_processing:
            messagebox.showwarning("Processing", "Already processing files. Please wait.")
            return
            
        # Validate inputs
        pdf_dir = Path(self.pdf_directory.get())
        if not pdf_dir.exists():
            messagebox.showerror("Error", f"PDF directory '{pdf_dir}' does not exist")
            return
            
        output_file = self.output_file.get()
        if not output_file:
            messagebox.showerror("Error", "Please specify an output file")
            return
            
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Start processing thread
        self.is_processing = True
        self.process_button.config(state='disabled')
        self.progress_bar.start()
        
        thread = threading.Thread(target=self.process_pdfs, daemon=True)
        thread.start()
        
    def process_pdfs(self):
        """Process PDFs in background thread"""
        try:
            self.update_status("Initializing PDF extractor...")
            self.log_message("Starting PDF data extraction process...")
            
            # Create extractor
            extractor = PDFExtractor(
                pdf_directory=self.pdf_directory.get(),
                output_file=self.output_file.get()
            )
            
            # Redirect logging to GUI
            import logging
            
            class GUILogHandler(logging.Handler):
                def __init__(self, gui_instance):
                    super().__init__()
                    self.gui = gui_instance
                    
                def emit(self, record):
                    msg = self.format(record)
                    self.gui.root.after(0, lambda: self.gui.log_message(msg))
            
            # Add GUI handler to logger
            gui_handler = GUILogHandler(self)
            gui_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
            extractor.logger.addHandler(gui_handler)
            
            # Process PDFs
            self.update_status("Processing PDF files...")
            success = extractor.run()
            
            # Update UI based on results
            if success:
                self.update_status(f"Processing completed successfully! Output: {self.output_file.get()}")
                self.log_message("\n" + "="*50)
                self.log_message("PROCESSING COMPLETED SUCCESSFULLY!")
                self.log_message(f"Output file: {self.output_file.get()}")
                self.log_message("="*50)
                
                # Show success message
                self.root.after(0, lambda: messagebox.showinfo(
                    "Success", 
                    f"Data extraction completed successfully!\n\nOutput file: {self.output_file.get()}"
                ))
            else:
                self.update_status("Processing completed with errors")
                self.log_message("\nProcessing completed with errors. Check log for details.")
                
                self.root.after(0, lambda: messagebox.showwarning(
                    "Warning", 
                    "Processing completed but some errors occurred. Check the log for details."
                ))
                
        except Exception as e:
            error_msg = f"Error during processing: {str(e)}"
            self.update_status("Error occurred during processing")
            self.log_message(f"\nERROR: {error_msg}")
            
            self.root.after(0, lambda: messagebox.showerror("Error", error_msg))
            
        finally:
            # Re-enable UI
            self.root.after(0, self.processing_finished)
            
    def processing_finished(self):
        """Called when processing is finished"""
        self.is_processing = False
        self.process_button.config(state='normal')
        self.progress_bar.stop()
        
    def open_output_file(self):
        """Open the output Excel file"""
        output_path = Path(self.output_file.get())
        
        if not output_path.exists():
            messagebox.showwarning("File Not Found", 
                                 f"Output file '{output_path}' does not exist yet.\n"
                                 "Please run the extraction process first.")
            return
            
        try:
            # Try to open with default application
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(output_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', output_path])
            else:  # Linux
                subprocess.run(['xdg-open', output_path])
                
            self.log_message(f"Opened output file: {output_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Could not open file: {str(e)}")


def main():
    """Main function for GUI application"""
    root = tk.Tk()
    
    # Set theme
    try:
        root.tk.call("source", "azure.tcl")
        root.tk.call("set_theme", "light")
    except:
        pass  # Theme not available, use default
    
    app = PDFExtractorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()