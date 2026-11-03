# Multi-folder PDF to text converter

A small Python utility that extracts text from PDFs beneath an input directory and writes `.txt` files into a matching directory structure.

## What it does

- Finds files ending in `.pdf` or `.PDF` recursively.
- Extracts text from each page with PyPDF2.
- Mirrors the source folder structure in the output directory.
- Reports processed and failed files at the end.

For example, `input/manuals/guide.pdf` becomes `output/manuals/guide.txt`.

## Run it

1. Use Python 3 and install the dependency:

   ```bash
   python3 -m pip install PyPDF2
   ```

2. Edit the two configuration values near the top of [extract_batch.py](extract_batch.py):

   ```python
   pdf_base_folder_path = "/absolute/path/to/input"
   output_base_folder_path = "/absolute/path/to/output"
   ```

   Use a separate output directory so extracted files do not mix with source PDFs.

3. Run:

   ```bash
   python3 extract_batch.py
   ```

The script creates output subdirectories as needed. It writes UTF-8 text and **overwrites an existing output file with the same path**.

## Limits

- This performs text extraction, not OCR. Scanned or image-only PDFs may produce empty text files.
- Some encrypted or malformed PDFs cannot be read; the script logs the error and continues.
- PDF text extraction can lose reading order, tables, and layout.
- Paths are configured in the script; there is no command-line interface yet.

This is a personal utility, not an evaluated document-processing pipeline.
