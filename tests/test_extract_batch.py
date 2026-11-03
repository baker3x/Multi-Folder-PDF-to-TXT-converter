"""Tests for path mirroring and overwrite behavior."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from extract_batch import convert


class BatchConverterTests(unittest.TestCase):
    def test_mirrors_mixed_case_pdf_and_skips_existing_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            input_dir = root / "input"
            output_dir = root / "output"
            pdf_path = input_dir / "manuals" / "Guide.PdF"
            pdf_path.parent.mkdir(parents=True)
            pdf_path.write_bytes(b"sample")

            with patch("extract_batch.extract_text", return_value="first pass"):
                self.assertEqual(convert(input_dir, output_dir), 0)

            text_path = output_dir / "manuals" / "Guide.txt"
            self.assertEqual(text_path.read_text(encoding="utf-8"), "first pass")

            with patch("extract_batch.extract_text", return_value="second pass") as extract:
                self.assertEqual(convert(input_dir, output_dir), 0)
                extract.assert_not_called()
                self.assertEqual(convert(input_dir, output_dir, overwrite=True), 0)
            self.assertEqual(text_path.read_text(encoding="utf-8"), "second pass")

    def test_reports_failed_conversion(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            input_dir = root / "input"
            input_dir.mkdir()
            (input_dir / "broken.pdf").write_bytes(b"not a pdf")
            with patch("extract_batch.extract_text", side_effect=ValueError("invalid PDF")):
                self.assertEqual(convert(input_dir, root / "output"), 1)
            self.assertFalse((root / "output" / "broken.txt").exists())

    def test_rejects_same_input_and_output(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self.assertEqual(convert(directory, directory), 2)


if __name__ == "__main__":
    unittest.main()
