#!/usr/bin/env python3
"""Clean an unpacked .pptx directory by removing orphaned files.

Usage:
    python scripts/clean.py unpacked_dir/

Removes:
- Slides not referenced in presentation.xml's <p:sldIdLst>
- Media files not referenced by any remaining relationship
- Orphaned .rels files for removed slides
"""

import argparse
import re
import sys
from pathlib import Path
from xml.dom import minidom


def get_referenced_slides(pres_path: Path) -> set[str]:
    """Get slide filenames referenced in presentation.xml's sldIdLst."""
    if not pres_path.exists():
        return set()

    content = pres_path.read_text(encoding="utf-8")
    dom = minidom.parseString(content.encode("utf-8"))

    # Get relationship IDs from sldIdLst
    rids = set()
    for sld_id in dom.getElementsByTagName("p:sldId"):
        rid = sld_id.getAttribute("r:id")
        if rid:
            rids.add(rid)

    # Map rids to slide filenames via presentation.xml.rels
    rels_path = pres_path.parent / "_rels" / "presentation.xml.rels"
    if not rels_path.exists():
        return set()

    rels_content = rels_path.read_text(encoding="utf-8")
    rels_dom = minidom.parseString(rels_content.encode("utf-8"))

    slides = set()
    for rel in rels_dom.getElementsByTagName("Relationship"):
        rid = rel.getAttribute("Id")
        target = rel.getAttribute("Target")
        if rid in rids and "slides/" in target:
            slides.add(target.split("/")[-1])

    return slides


def get_all_referenced_media(ppt_dir: Path) -> set[str]:
    """Scan all .rels files for media references."""
    media_refs = set()
    for rels_file in ppt_dir.rglob("*.rels"):
        content = rels_file.read_text(encoding="utf-8")
        # Find all Target attributes pointing to ../media/
        for match in re.finditer(r'Target="[^"]*?/?(media/[^"]+)"', content):
            media_refs.add(match.group(1).split("/")[-1])
    return media_refs


def clean(unpacked_dir: Path) -> None:
    """Remove orphaned files from an unpacked presentation."""
    pres_path = unpacked_dir / "ppt" / "presentation.xml"
    slides_dir = unpacked_dir / "ppt" / "slides"
    media_dir = unpacked_dir / "ppt" / "media"

    if not pres_path.exists():
        print(f"Error: No presentation.xml found in {unpacked_dir}", file=sys.stderr)
        sys.exit(1)

    removed = []

    # 1. Remove orphaned slides
    referenced_slides = get_referenced_slides(pres_path)
    if slides_dir.exists() and referenced_slides:
        for slide_file in sorted(slides_dir.glob("slide*.xml")):
            if slide_file.name not in referenced_slides:
                slide_file.unlink()
                removed.append(f"Slide: {slide_file.name}")

                # Remove corresponding .rels
                rels_file = slides_dir / "_rels" / f"{slide_file.name}.rels"
                if rels_file.exists():
                    rels_file.unlink()
                    removed.append(f"Rels: _rels/{slide_file.name}.rels")

    # 2. Remove orphaned media
    if media_dir.exists():
        referenced_media = get_all_referenced_media(unpacked_dir / "ppt")
        for media_file in sorted(media_dir.iterdir()):
            if media_file.is_file() and media_file.name not in referenced_media:
                media_file.unlink()
                removed.append(f"Media: {media_file.name}")

    if removed:
        print(f"Cleaned {unpacked_dir}/:")
        for item in removed:
            print(f"  Removed {item}")
    else:
        print(f"Clean: nothing to remove in {unpacked_dir}/")


def main():
    parser = argparse.ArgumentParser(description="Clean orphaned files from unpacked .pptx.")
    parser.add_argument("input", help="Unpacked directory")
    args = parser.parse_args()

    clean(Path(args.input))


if __name__ == "__main__":
    main()
