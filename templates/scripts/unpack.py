#!/usr/bin/env python3
"""Unpack a .pptx file into a directory with pretty-printed XML.

Usage:
    python scripts/unpack.py input.pptx output_dir/

Extracts all files from the .pptx archive. XML files are pretty-printed
for readability. Smart quotes are normalized to ASCII for safe editing.
"""

import argparse
import sys
import zipfile
from pathlib import Path
from xml.dom import minidom


def pretty_print_xml(content: bytes) -> str:
    """Parse and pretty-print XML content."""
    try:
        dom = minidom.parseString(content)
        pretty = dom.toprettyxml(indent="  ", encoding="UTF-8")
        # minidom adds an XML declaration; decode and return
        text = pretty.decode("utf-8")
        # Remove extra blank lines minidom sometimes adds
        lines = [line for line in text.splitlines() if line.strip()]
        return "\n".join(lines) + "\n"
    except Exception:
        # If XML parsing fails, return raw content
        return content.decode("utf-8", errors="replace")


def normalize_quotes(text: str) -> str:
    """Replace smart quotes with ASCII equivalents for safe editing."""
    replacements = {
        "\u201c": '"',  # left double quote
        "\u201d": '"',  # right double quote
        "\u2018": "'",  # left single quote
        "\u2019": "'",  # right single quote
    }
    for smart, ascii_char in replacements.items():
        text = text.replace(smart, ascii_char)
    return text


def unpack(pptx_path: Path, output_dir: Path) -> None:
    """Extract .pptx contents with pretty-printed XML."""
    if not pptx_path.exists():
        print(f"Error: File not found: {pptx_path}", file=sys.stderr)
        sys.exit(1)

    if not zipfile.is_zipfile(pptx_path):
        print(f"Error: Not a valid .pptx file: {pptx_path}", file=sys.stderr)
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(pptx_path, "r") as zf:
        for info in zf.infolist():
            if info.is_dir():
                (output_dir / info.filename).mkdir(parents=True, exist_ok=True)
                continue

            content = zf.read(info.filename)
            out_path = output_dir / info.filename
            out_path.parent.mkdir(parents=True, exist_ok=True)

            if info.filename.endswith((".xml", ".rels")):
                text = pretty_print_xml(content)
                text = normalize_quotes(text)
                out_path.write_text(text, encoding="utf-8")
            else:
                out_path.write_bytes(content)

    print(f"Unpacked {pptx_path} → {output_dir}/")
    # List slide files for quick reference
    slides_dir = output_dir / "ppt" / "slides"
    if slides_dir.exists():
        slides = sorted(slides_dir.glob("slide*.xml"))
        print(f"  Slides: {len(slides)}")
        for s in slides:
            print(f"    {s.name}")


def main():
    parser = argparse.ArgumentParser(description="Unpack a .pptx file with pretty-printed XML.")
    parser.add_argument("input", help="Input .pptx file")
    parser.add_argument("output", help="Output directory")
    args = parser.parse_args()

    unpack(Path(args.input), Path(args.output))


if __name__ == "__main__":
    main()
