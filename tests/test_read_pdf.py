"""Behavior checks using synthetic PDF bytes, without retaining any papers."""

import importlib.util
import io
from pathlib import Path
import unittest

from reportlab.pdfgen import canvas
from reportlab.lib.pdfencrypt import StandardEncryption


SCRIPT = Path(__file__).resolve().parents[1] / "skills/lab-research/scripts/read_pdf.py"
SPEC = importlib.util.spec_from_file_location("read_pdf", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def sample_pdf(*, encrypted=False):
    stream = io.BytesIO()
    options = {"encrypt": StandardEncryption("private-test-password")} if encrypted else {}
    document = canvas.Canvas(stream, **options)
    document.drawString(40, 700, "Synthetic page one: text extraction is not evidence verification.")
    document.showPage()
    document.showPage()
    document.drawString(40, 700, "Synthetic page three: this is a separate physical page, not page two.")
    document.showPage()
    document.save()
    return stream.getvalue()


class ReadPdfTests(unittest.TestCase):
    def test_preserves_physical_page_numbers_and_scope(self):
        result = MODULE.extract_pdf(sample_pdf(), pages="3,1,3")
        self.assertEqual(result["total_pages"], 3)
        self.assertEqual(result["selected_pages"], [1, 3])
        self.assertEqual([p["pdf_page"] for p in result["pages"]], [1, 3])
        self.assertIn("page three", result["pages"][1]["text"])
        self.assertIsNone(result["pages"][1]["printed_page"])

    def test_blank_page_is_flagged_without_claiming_ocr(self):
        result = MODULE.extract_pdf(sample_pdf(), pages="2")
        self.assertEqual(result["pages"][0]["text"], "")
        self.assertIn("little_or_no_text_check_page_visually", result["pages"][0]["quality_flags"])
        self.assertFalse(result["ocr_performed"])

    def test_fingerprint_and_optional_table_scope(self):
        data = sample_pdf()
        text = MODULE.extract_pdf(data, pages="1")
        table = MODULE.extract_pdf(data, pages="1", tables=True)
        self.assertEqual(text["source_sha256"], table["source_sha256"])
        self.assertNotIn("candidate_tables", text["pages"][0])
        self.assertIn("candidate_tables", table["pages"][0])
        self.assertEqual(len(text["source_sha256"]), 64)

    def test_invalid_ranges_fail_instead_of_silently_reading_other_pages(self):
        for spec in ("0", "4", "3-1", "1-4", "one", "1,", ""):
            with self.subTest(spec=spec), self.assertRaises(ValueError):
                MODULE.select_pages(spec, 3)

    def test_invalid_pdf_fails(self):
        with self.assertRaises(Exception):
            MODULE.extract_pdf(b"This is not a PDF")

    def test_encrypted_pdf_is_not_reported_as_success(self):
        with self.assertRaises(Exception):
            MODULE.extract_pdf(sample_pdf(encrypted=True))


if __name__ == "__main__":
    unittest.main()
