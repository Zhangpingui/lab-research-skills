"""Local PDF text extraction with physical page anchors; no OCR or network calls."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import sys


def select_pages(spec: str | None, total: int) -> list[int]:
    if spec is None:
        return list(range(1, total + 1))
    selected: set[int] = set()
    for token in spec.split(","):
        match = re.fullmatch(r"\s*(\d+)(?:\s*-\s*(\d+))?\s*", token)
        if not match:
            raise ValueError("Pages must use a format such as 1,3-5.")
        first = int(match.group(1))
        last = int(match.group(2) or first)
        if first < 1 or last < first or last > total:
            raise ValueError(f"Page range {token!r} is outside 1-{total} or reversed.")
        selected.update(range(first, last + 1))
    return sorted(selected)


def extract_pdf(data: bytes, *, pages: str | None = None, tables: bool = False) -> dict:
    import pdfplumber

    with pdfplumber.open(io.BytesIO(data)) as document:
        selected = select_pages(pages, len(document.pages))
        records = []
        for number in selected:
            page = document.pages[number - 1]
            text = page.extract_text() or ""
            flags = ["layout_and_figures_not_verified"]
            if len("".join(text.split())) < 40:
                flags.append("little_or_no_text_check_page_visually")
            record = {
                "pdf_page": number,
                "printed_page": None,
                "text": text,
                "quality_flags": flags,
            }
            if tables:
                record["candidate_tables"] = page.extract_tables()
            records.append(record)
    return {
        "schema_version": "0.1",
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "total_pages": len(document.pages),
        "selected_pages": selected,
        "extraction_scope": "text_and_candidate_tables" if tables else "text_only",
        "ocr_performed": False,
        "pages": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--pages", help="1-based physical PDF pages, e.g. 1,3-5")
    parser.add_argument("--tables", action="store_true", help="Extract unverified candidate tables")
    args = parser.parse_args()
    try:
        result = extract_pdf(args.pdf.read_bytes(), pages=args.pages, tables=args.tables)
    except ImportError:
        print("Missing pdfplumber. Install scripts/requirements.txt in your Python environment.", file=sys.stderr)
        return 2
    except Exception as error:
        print(f"PDF extraction failed ({type(error).__name__}): {error}", file=sys.stderr)
        return 2
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
