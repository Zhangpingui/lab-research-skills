import argparse
import hashlib
import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "skills"
    / "lab-research"
    / "scripts"
    / "extract_pdf_region.py"
)
SPEC = importlib.util.spec_from_file_location("extract_pdf_region", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class ExtractPdfRegionTests(unittest.TestCase):
    def test_parse_box_accepts_normalized_coordinates(self):
        self.assertEqual(MODULE.parse_box("0.1,0.2,0.8,0.9"), (0.1, 0.2, 0.8, 0.9))

    def test_parse_box_rejects_wrong_coordinate_count(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            MODULE.parse_box("0.1,0.2,0.8")

    def test_parse_box_rejects_reversed_coordinates(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            MODULE.parse_box("0.8,0.2,0.1,0.9")

    def test_parse_box_rejects_out_of_range_coordinates(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            MODULE.parse_box("-0.1,0.2,0.8,0.9")

    def test_sha256_matches_known_digest(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample.bin"
            path.write_bytes(b"lab-research")
            expected = hashlib.sha256(b"lab-research").hexdigest()
            self.assertEqual(MODULE.sha256(path), expected)


if __name__ == "__main__":
    unittest.main()
