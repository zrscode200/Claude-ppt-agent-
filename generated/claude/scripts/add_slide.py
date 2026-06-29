#!/usr/bin/env python3
"""Duplicate a slide in an unpacked .pptx directory.

Usage:
    python scripts/add_slide.py unpacked_dir/ slide2.xml

Duplicates the specified slide XML (and its relationships), assigns new IDs,
and prints the <p:sldId> element to add to presentation.xml's <p:sldIdLst>.
"""

import argparse
import re
import sys
from pathlib import Path
from xml.dom import minidom


def find_next_slide_number(slides_dir: Path) -> int:
    """Find the next available slide number."""
    existing = [
        int(m.group(1))
        for f in slides_dir.glob("slide*.xml")
        if (m := re.match(r"slide(\d+)\.xml", f.name))
    ]
    return max(existing, default=0) + 1


def find_next_id(pres_path: Path) -> tuple[int, int]:
    """Find next available slide ID and relationship ID."""
    content = pres_path.read_text(encoding="utf-8")

    # Find max sldId id attribute
    ids = [int(m) for m in re.findall(r'<p:sldId[^>]*\bid="(\d+)"', content)]
    next_id = max(ids, default=255) + 1

    # Find max rId number in presentation.xml.rels
    rels_path = pres_path.parent / "_rels" / "presentation.xml.rels"
    rels_content = rels_path.read_text(encoding="utf-8")
    rids = [int(m) for m in re.findall(r'Id="rId(\d+)"', rels_content)]
    next_rid = max(rids, default=0) + 1

    return next_id, next_rid


def duplicate_slide(unpacked_dir: Path, source_name: str) -> None:
    """Duplicate a slide and its relationships."""
    slides_dir = unpacked_dir / "ppt" / "slides"
    rels_dir = slides_dir / "_rels"
    pres_path = unpacked_dir / "ppt" / "presentation.xml"

    source_path = slides_dir / source_name
    if not source_path.exists():
        print(f"Error: Source slide not found: {source_path}", file=sys.stderr)
        sys.exit(1)

    # Determine new slide filename
    new_num = find_next_slide_number(slides_dir)
    new_name = f"slide{new_num}.xml"
    new_path = slides_dir / new_name

    # Copy slide XML
    content = source_path.read_text(encoding="utf-8")
    # Update the slide name attribute if present
    content = re.sub(
        r'name="Slide \d+"',
        f'name="Slide {new_num}"',
        content,
    )
    new_path.write_text(content, encoding="utf-8")

    # Copy relationships file if it exists
    source_rels = rels_dir / f"{source_name}.rels"
    if source_rels.exists():
        rels_dir.mkdir(parents=True, exist_ok=True)
        new_rels = rels_dir / f"{new_name}.rels"
        new_rels.write_text(source_rels.read_text(encoding="utf-8"), encoding="utf-8")

    # Update Content_Types.xml
    ct_path = unpacked_dir / "[Content_Types].xml"
    if ct_path.exists():
        ct_content = ct_path.read_text(encoding="utf-8")
        # Add entry for new slide if not already there
        new_entry = f'<Override PartName="/ppt/slides/{new_name}" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        if f"/ppt/slides/{new_name}" not in ct_content:
            ct_content = ct_content.replace("</Types>", f"  {new_entry}\n</Types>")
            ct_path.write_text(ct_content, encoding="utf-8")

    # Add relationship in presentation.xml.rels
    next_id, next_rid = find_next_id(pres_path)
    rid = f"rId{next_rid}"

    rels_path = pres_path.parent / "_rels" / "presentation.xml.rels"
    rels_content = rels_path.read_text(encoding="utf-8")
    new_rel = f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/{new_name}"/>'
    rels_content = rels_content.replace("</Relationships>", f"  {new_rel}\n</Relationships>")
    rels_path.write_text(rels_content, encoding="utf-8")

    # Print the sldId element to add to presentation.xml
    sld_id_element = f'<p:sldId id="{next_id}" r:id="{rid}"/>'

    print(f"Duplicated {source_name} → {new_name}")
    print(f"  New relationship: {rid}")
    print(f"\nAdd this to <p:sldIdLst> in ppt/presentation.xml:")
    print(f"  {sld_id_element}")


def main():
    parser = argparse.ArgumentParser(description="Duplicate a slide in an unpacked .pptx.")
    parser.add_argument("input", help="Unpacked directory")
    parser.add_argument("source", help="Source slide filename (e.g., slide2.xml)")
    args = parser.parse_args()

    duplicate_slide(Path(args.input), args.source)


if __name__ == "__main__":
    main()
