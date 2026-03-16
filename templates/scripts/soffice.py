#!/usr/bin/env python3
"""Convert .pptx to PDF and slide images using LibreOffice + pdftoppm.

Usage:
    python scripts/soffice.py input.pptx [--output-dir DIR]

Converts a .pptx to PDF, then to individual slide JPGs.
Output: <name>.pdf, slide-01.jpg, slide-02.jpg, etc.

Requires: LibreOffice (soffice), pdftoppm (poppler)
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def get_soffice_path() -> str:
    """Find soffice binary."""
    mac_paths = [
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        os.path.expanduser("~/Applications/LibreOffice.app/Contents/MacOS/soffice"),
    ]
    for p in mac_paths:
        if os.path.exists(p):
            return p

    if shutil.which("soffice"):
        return "soffice"

    return ""


def check_dependencies() -> list[str]:
    """Check for required external tools."""
    missing = []
    if not get_soffice_path():
        missing.append("soffice (LibreOffice)")
    if not shutil.which("pdftoppm"):
        missing.append("pdftoppm (poppler)")
    return missing


def convert(pptx_path: Path, output_dir: Path, dpi: int = 150) -> list[Path]:
    """Convert .pptx → PDF → slide images."""
    missing = check_dependencies()
    if missing:
        print(f"Error: Missing dependencies: {', '.join(missing)}", file=sys.stderr)
        print("  Install LibreOffice: brew install --cask libreoffice", file=sys.stderr)
        print("  Install poppler: brew install poppler", file=sys.stderr)
        sys.exit(1)

    soffice = get_soffice_path()
    output_dir.mkdir(parents=True, exist_ok=True)

    # Step 1: PPTX → PDF
    pdf_name = f"{pptx_path.stem}.pdf"
    result = subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(output_dir), str(pptx_path)],
        capture_output=True, text=True,
    )
    pdf_path = output_dir / pdf_name
    if result.returncode != 0 or not pdf_path.exists():
        print(f"Error: PDF conversion failed", file=sys.stderr)
        print(f"  stderr: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    print(f"PDF: {pdf_path}")

    # Step 2: PDF → JPGs
    result = subprocess.run(
        ["pdftoppm", "-jpeg", "-r", str(dpi), str(pdf_path), str(output_dir / "slide")],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"Error: pdftoppm failed", file=sys.stderr)
        print(f"  stderr: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    images = sorted(output_dir.glob("slide-*.jpg"))
    print(f"Slides: {len(images)} images at {dpi} DPI")
    for img in images:
        print(f"  {img.name}")

    return images


def main():
    parser = argparse.ArgumentParser(description="Convert .pptx to PDF and slide images.")
    parser.add_argument("input", help="Input .pptx file")
    parser.add_argument("--output-dir", default=".", help="Output directory (default: current)")
    parser.add_argument("--dpi", type=int, default=150, help="Image resolution (default: 150)")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    convert(input_path, Path(args.output_dir), args.dpi)


if __name__ == "__main__":
    main()
