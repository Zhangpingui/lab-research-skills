#!/usr/bin/env python3
"""Render and crop a reproducible region from one PDF page."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from PIL import Image


def parse_box(value: str) -> tuple[float, float, float, float]:
    try:
        coords = tuple(float(item.strip()) for item in value.split(","))
    except ValueError as exc:
        raise argparse.ArgumentTypeError("box must contain four numbers") from exc
    if len(coords) != 4:
        raise argparse.ArgumentTypeError("box must be x0,y0,x1,y1")
    x0, y0, x1, y1 = coords
    if not (0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1):
        raise argparse.ArgumentTypeError(
            "box coordinates must satisfy 0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1"
        )
    return x0, y0, x1, y1


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Render one PDF page and crop a normalized top-left-origin box. "
            "Inspect the full page before choosing the box."
        )
    )
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--page", type=int, required=True, help="1-based PDF physical page")
    parser.add_argument(
        "--box",
        type=parse_box,
        required=True,
        help="normalized x0,y0,x1,y1 coordinates using a top-left origin",
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=240)
    parser.add_argument(
        "--pdftoppm",
        help="optional explicit path to pdftoppm; otherwise resolve it from PATH",
    )
    args = parser.parse_args()

    source = args.pdf.resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if args.page < 1:
        raise ValueError("--page must be at least 1")
    if args.dpi < 72:
        raise ValueError("--dpi must be at least 72")
    if args.output.suffix.lower() != ".png":
        raise ValueError("--output must end in .png")

    renderer = args.pdftoppm or shutil.which("pdftoppm")
    if not renderer:
        raise FileNotFoundError(
            "pdftoppm was not found; provide --pdftoppm with an absolute path"
        )

    with tempfile.TemporaryDirectory(prefix="lab-research-pdf-crop-") as temp_dir:
        prefix = Path(temp_dir) / "page"
        command = [
            str(renderer),
            "-f",
            str(args.page),
            "-l",
            str(args.page),
            "-r",
            str(args.dpi),
            "-png",
            "-singlefile",
            str(source),
            str(prefix),
        ]
        completed = subprocess.run(command, check=False, capture_output=True, text=True)
        if completed.returncode != 0:
            raise RuntimeError(
                "pdftoppm failed: " + (completed.stderr or completed.stdout).strip()
            )
        rendered = prefix.with_suffix(".png")
        if not rendered.is_file():
            raise RuntimeError("pdftoppm completed without producing the rendered page")

        with Image.open(rendered) as page_image:
            width, height = page_image.size
            x0, y0, x1, y1 = args.box
            pixel_box = (
                round(x0 * width),
                round(y0 * height),
                round(x1 * width),
                round(y1 * height),
            )
            cropped = page_image.crop(pixel_box)
            args.output.parent.mkdir(parents=True, exist_ok=True)
            cropped.save(args.output, format="PNG")
            crop_width, crop_height = cropped.size

    result = {
        "source": str(source),
        "source_sha256": sha256(source),
        "pdf_page": args.page,
        "box_normalized_top_left": list(args.box),
        "dpi": args.dpi,
        "output": str(args.output.resolve()),
        "output_pixels": [crop_width, crop_height],
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
