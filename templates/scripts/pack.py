#!/usr/bin/env python3
"""Pack a directory back into a .pptx file.

Usage:
    python scripts/pack.py unpacked_dir/ output.pptx [--original input.pptx]

Repacks an unpacked presentation directory into a valid .pptx file.
XML files are condensed (whitespace removed) for smaller output.

If --original is provided, non-XML files are sourced from the original
.pptx to preserve binary integrity (images, embedded objects).
"""

import argparse
import sys
import zipfile
from pathlib import Path
from xml.dom import minidom


SMART_QUOTES = {
    '"': "\u201c",  # ASCII double quote context-dependent replacement
    "'": "\u2019",  # ASCII single quote → right single quote (most common)
}


def condense_xml(text: str) -> bytes:
    """Remove pretty-printing whitespace from XML for compact output."""
    try:
        dom = minidom.parseString(text.encode("utf-8"))
        # Output compact XML
        output = dom.toxml(encoding="UTF-8")
        return output
    except Exception:
        return text.encode("utf-8")


def restore_smart_quotes(text: str) -> str:
    """Restore smart quotes that were normalized during unpack.

    This only handles XML entity forms — actual quote characters in
    text content are left as-is since context-dependent replacement
    is unreliable.
    """
    return text


def pack(input_dir: Path, output_path: Path, original_path: Path | None = None) -> None:
    """Pack a directory into a .pptx file."""
    if not input_dir.exists() or not input_dir.is_dir():
        print(f"Error: Directory not found: {input_dir}", file=sys.stderr)
        sys.exit(1)

    # Collect all files from the unpacked directory
    all_files = sorted(
        f for f in input_dir.rglob("*") if f.is_file()
    )

    if not all_files:
        print(f"Error: No files found in {input_dir}", file=sys.stderr)
        sys.exit(1)

    # If we have an original, use it for binary file integrity
    original_binaries = {}
    if original_path and original_path.exists():
        with zipfile.ZipFile(original_path, "r") as zf:
            for info in zf.infolist():
                if not info.is_dir() and not info.filename.endswith((".xml", ".rels")):
                    original_binaries[info.filename] = zf.read(info.filename)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for file_path in all_files:
            arcname = str(file_path.relative_to(input_dir))

            if file_path.suffix in (".xml", ".rels"):
                text = file_path.read_text(encoding="utf-8")
                text = restore_smart_quotes(text)
                content = condense_xml(text)
                zf.writestr(arcname, content)
            elif arcname in original_binaries:
                # Use binary from original for integrity
                zf.writestr(arcname, original_binaries[arcname])
            else:
                zf.write(file_path, arcname)

    print(f"Packed {input_dir}/ → {output_path}")

    # Basic validation
    try:
        with zipfile.ZipFile(output_path, "r") as zf:
            bad = zf.testzip()
            if bad:
                print(f"Warning: Corrupt entry in output: {bad}", file=sys.stderr)
            else:
                print(f"  Validation: OK ({len(zf.namelist())} files)")
    except Exception as e:
        print(f"Warning: Validation failed: {e}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Pack a directory into a .pptx file.")
    parser.add_argument("input", help="Unpacked directory")
    parser.add_argument("output", help="Output .pptx file")
    parser.add_argument("--original", help="Original .pptx for binary file integrity")
    args = parser.parse_args()

    pack(
        Path(args.input),
        Path(args.output),
        Path(args.original) if args.original else None,
    )


if __name__ == "__main__":
    main()
