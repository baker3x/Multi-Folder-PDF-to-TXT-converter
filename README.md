# Multi-folder PDF to text converter

A small Python command-line utility that extracts text from PDFs beneath an
input directory and writes `.txt` files into a matching directory structure.

For example, `input/manuals/guide.pdf` becomes
`output/manuals/guide.txt`.

## Run it

Use Python 3.10 or newer:

```bash
python3 -m pip install -r requirements.txt
python3 extract_batch.py /path/to/input /path/to/output
```

The input directory must already exist. The output directory is created as
needed and must differ from the input directory. Files ending in `.pdf`
(regardless of extension case) are discovered recursively.

Existing output text files are skipped by default. To replace them:

```bash
python3 extract_batch.py /path/to/input /path/to/output --overwrite
```

The command prints counts of converted, skipped, and failed files. It returns
a nonzero exit status if any conversion fails. Run `python3 extract_batch.py
--help` for the full command-line help.

## Limits

- This performs text extraction, not OCR. Scanned or image-only PDFs may
  produce empty text files.
- Encrypted or malformed PDFs may fail; the utility logs each error and
  continues with the remaining files.
- PDF text extraction can lose reading order, tables, and layout.
- The utility does not evaluate whether extracted text is complete or correct.

This is a personal batch-processing utility, not a validated document pipeline.
