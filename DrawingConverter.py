import os
import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image # pip install Pillow
import fitz # pip install PyMuPDF



def split_pdf_to_single_pages(pdf_path, output_dir):
    """Convert Multi-Page PDF to Single-Page PDF"""
    os.makedirs(output_dir, exist_ok=True)

    with fitz.open(pdf_path) as doc:
        for page_index in range(len(doc)):
            output_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_page_{page_index + 1}.pdf")
            doc.save(output_path, garbage=4, deflate=True)
            print(f"PDF saved:  {output_path}")
def split_pdf_to_multiple_pdfs(pdf_path, output_dir, pages_per_pdf=10):
    """Split multi-page PDF into multiple PDF files"""
    os.makedirs(output_dir, exist_ok=True)

    with fitz.open(pdf_path) as doc:
        total_pages = len(doc)
        for start_page in range(0, total_pages, pages_per_pdf):
            end_page = min(start_page + pages_per_pdf, total_pages)
            output_pdf_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_pages_{start_page + 1}-{end_page}.pdf")
            output_doc = fitz.Document()
            for page_index in range(start_page, end_page):
                output_doc.insert_pdf(doc, from_page=page_index, to_page=page_index)
            output_doc.save(output_pdf_path)
            print(f"PDF saved: {output_pdf_path}")
def pdf_to_jpg(pdf_path, output_dir):
    """Convert Single Page PDF to JPG"""
    os.makedirs(output_dir, exist_ok=True)

    with fitz.open(pdf_path) as doc:
        for page_index in range(len(doc)):
            page = doc[page_index]
            image_matrix = fitz.Matrix(2, 2)  # Set the image resolution to 300 dpi
            page_image = page.get_pixmap(matrix=image_matrix)

            image_path = os.path.join(output_dir, f"{os.path.splitext(os.path.basename(pdf_path))[0]}_page_{page_index + 1}.jpg")
            Image.frombytes("RGB", [page_image.width, page_image.height], page_image.samples).save(image_path)
            print(f"Image saved: {image_path}")
def merge_pdfs_to_single_pdf(pdf_paths, output_path):
    """Combine multiple PDF files into one PDF file"""
    output_doc = fitz.Document()
    for pdf_path in pdf_paths:
        with fitz.open(pdf_path) as doc:
            output_doc.insert_pdf(doc)
    output_doc.save(output_path)
    print(f"Saved merged PDF file:{output_path}")


def select_pdf_path():
    """Select PDF file path"""
    pdf_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
    pdf_path_entry.delete(0, tk.END)
    pdf_path_entry.insert(0, pdf_path)

def select_output_dir():
    """Select save path after conversion"""
    output_dir = filedialog.askdirectory()
    output_dir_entry.delete(0, tk.END)
    output_dir_entry.insert(0, output_dir)

def split_pdf_to_single_pages_command():
    """Convert multi-page PDF to single page"""
    pdf_path = pdf_path_entry.get()
    output_dir = output_dir_entry.get()
    split_pdf_to_single_pages(pdf_path, output_dir)
    status_label.config(text="Conversion of Multi-Page PDF to Single Page Completed")

def split_pdf_to_multiple_pdfs_command():
    """Split multi-page PDF into multiple PDF files"""
    pdf_path = pdf_path_entry.get()
    output_dir = output_dir_entry.get()
    pages_per_pdf = int(pages_per_pdf_entry.get())
    split_pdf_to_multiple_pdfs(pdf_path, output_dir, pages_per_pdf)
    status_label.config(text=f"Completed splitting multi-page PDF into one PDF file per {pages_per_pdf} pages.")
def convert_to_jpg():
    """Convert Single Page PDF to JPG"""
    pdf_path = pdf_path_entry.get()
    output_dir = output_dir_entry.get()
    pdf_to_jpg(pdf_path, output_dir)
    status_label.config(text="Conversion of single page PDF to JPG completed")
def merge_pdfs_to_single_pdf_command():
    """Combine multiple PDF files into one PDF file"""
    pdf_paths = filedialog.askopenfilenames(filetypes=[("PDF Files", "*.pdf")])
    output_path = os.path.join(output_dir_entry.get(), "merged.pdf")
    merge_pdfs_to_single_pdf(pdf_paths, output_path)
    status_label.config(text="Finished merging multiple PDF files into one PDF file")

# Creating the Tkinter Window
root = tk.Tk()
root.title("Construction Drawings Converter")


pdf_path_label = ttk.Label(root, text="PDF Path:")
pdf_path_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")

pdf_path_entry = ttk.Entry(root, width=50)
pdf_path_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")

select_pdf_button = ttk.Button(root, text="Select PDF file", command=select_pdf_path)
select_pdf_button.grid(row=0, column=2, padx=10, pady=10)
convert_to_jpg_button = ttk.Button(root, text="Convert single-page PDF to JPG", command=convert_to_jpg)
convert_to_jpg_button.grid(row=2, column=0, columnspan=3, padx=10, pady=10)
# 输出路径输入框
output_dir_label = ttk.Label(root, text="Output Path:")
output_dir_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")

output_dir_entry = ttk.Entry(root, width=50)
output_dir_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")

select_output_button = ttk.Button(root, text="Selecting the output directory", command=select_output_dir)
select_output_button.grid(row=1, column=2, padx=10, pady=10)


pages_per_pdf_label = ttk.Label(root, text="Number of pages per PDF file.")
pages_per_pdf_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")

pages_per_pdf_entry = ttk.Entry(root, width=10)
pages_per_pdf_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
pages_per_pdf_entry.insert(0, "1")


split_to_multiple_pdfs_button = ttk.Button(root, text="Convert multi-page PDFs to single pages", command=split_pdf_to_multiple_pdfs_command)
split_to_multiple_pdfs_button.grid(row=4, column=0, columnspan=3, padx=10, pady=10)


status_label = ttk.Label(root, text="")
status_label.grid(row=6, column=0, columnspan=3, padx=10, pady=10)

root.mainloop()