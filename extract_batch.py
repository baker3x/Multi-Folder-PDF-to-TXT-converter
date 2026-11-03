#!/usr/bin/env python3
"""Recursively extract text from PDFs into a mirrored output directory."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PyPDF2 import PdfReader


def extract_text(pdf_path: Path) -> str:
    """Return text extracted from every page of one PDF."""
    reader = PdfReader(str(pdf_path))
    if reader.is_encrypted and not reader.decrypt(""):
        raise ValueError("PDF is encrypted and cannot be opened with an empty password")

    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(page for page in pages if page)


def convert(input_dir: Path, output_dir: Path, overwrite: bool = False) -> int:
    """Convert PDFs and return a nonzero exit status if any conversion fails."""
    input_dir = input_dir.expanduser().resolve()
    output_dir = output_dir.expanduser().resolve()

    if not input_dir.is_dir():
        print(f"Input directory does not exist: {input_dir}", file=sys.stderr)
        return 2
    if input_dir == output_dir:
        print("Input and output directories must differ.", file=sys.stderr)
        return 2

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        print(f"Cannot create output directory: {error}", file=sys.stderr)
        return 2

    pdf_files = sorted(
        path for path in input_dir.rglob("*")
        if path.is_file() and path.suffix.lower() == ".pdf"
    )

    converted = skipped = failed = 0
    output_paths: set[Path] = set()

    for pdf_path in pdf_files:
        relative_path = pdf_path.relative_to(input_dir)
        text_path = output_dir / relative_path.with_suffix(".txt")

        if text_path in output_paths:
            print(f"Collision: multiple PDFs map to {text_path}", file=sys.stderr)
            failed += 1
            continue
        output_paths.add(text_path)

        if text_path.exists() and not overwrite:
            print(f"Skip existing: {text_path}")
            skipped += 1
            continue

        try:
            text = extract_text(pdf_path)
            text_path.parent.mkdir(parents=True, exist_ok=True)
            text_path.write_text(text, encoding="utf-8")
        except Exception as error:
            print(f"Failed: {relative_path}: {error}", file=sys.stderr)
            failed += 1
            continue

        if not text:
            print(f"No extractable text: {relative_path} (the PDF may be image-only)")
        print(f"Converted: {relative_path} -> {text_path.relative_to(output_dir)}")
        converted += 1

    print(
        f"PDFs found: {len(pdf_files)}; converted: {converted}; "
        f"skipped: {skipped}; failed: {failed}"
    )
    return 1 if failed else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_dir", type=Path, help="Directory containing source PDFs")
    parser.add_argument("output_dir", type=Path, help="Directory for mirrored text files")
    parser.add_argument(
        "--overwrite", action="store_true", help="Replace existing output text files"
    )
    args = parser.parse_args(argv)
    return convert(args.input_dir, args.output_dir, args.overwrite)


if __name__ == "__main__":
    raise SystemExit(main())
