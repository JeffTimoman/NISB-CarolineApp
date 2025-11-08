# webdata/utils/pdf.py

import fitz 
import os
import concurrent.futures
from functools import partial

from PyPDF2 import PdfReader, PdfMerger, errors

# This is the new function that will be run in parallel for each page.
# It's designed to be self-contained for a single worker process.
def convert_single_page(page_num, pdf_path, output_dir, dpi):
    """Converts a single page of a PDF to a PNG image."""
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=dpi)

        output_image_path = os.path.join(output_dir, f"page_{page_num + 1}.png")
        pix.save(output_image_path)

        doc.close()
        print(f"  - Converted page {page_num + 1}")
        return output_image_path
    except Exception as e:
        print(f"Error converting page {page_num + 1}: {e}")
        return None

# This is the updated main function that orchestrates the parallel conversion.
def convert_pdf_to_png_parallel(pdf_path, output_dir, dpi=300):
    """
    Converts a PDF to PNG images in parallel using multiple processes.
    """
    os.makedirs(output_dir, exist_ok=True)

    try:
        doc = fitz.open(pdf_path)
        num_pages = len(doc)
        doc.close()
    except Exception as e:
        print(f"Error opening PDF file to get page count: {e}")
        return

    print(f"Converting '{pdf_path}' ({num_pages} pages) to PNGs in parallel...")

    # Use functools.partial to create a version of our function with the
    # pdf_path, output_dir, and dpi arguments already filled in.
    task = partial(convert_single_page, pdf_path=pdf_path, output_dir=output_dir, dpi=dpi)

    # Use a ProcessPoolExecutor to run the conversion in parallel.
    # It will use all available CPU cores by default.
    with concurrent.futures.ProcessPoolExecutor() as executor:
        # map() applies the 'task' function to each item in the 'range(num_pages)' iterable.
        # It executes them in parallel and returns the results as they complete.
        results = list(executor.map(task, range(num_pages)))

    # Filter out any failed conversions (which return None)
    successful_conversions = [r for r in results if r is not None]

    print(f"Finished conversion. {len(successful_conversions)}/{num_pages} pages converted successfully.")


# The old function is no longer needed. I've removed it for clarity.
# def convert_pdf_to_png(pdf_path, output_dir): ...


def combine_pdfs(pdf_paths, output_path):
    merger = PdfMerger()
    for pdf in pdf_paths:
        try:
            # Validate PDF before merging
            with open(pdf, 'rb') as f:
                PdfReader(f)
            merger.append(pdf)
        except errors.PdfReadError as e:
            print(f"Invalid PDF detected: {pdf} ({e})")
            continue  # Skip invalid PDFs
    merger.write(output_path)
    merger.close()