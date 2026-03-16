#!/usr/bin/env python3
"""Create thumbnail grids from PowerPoint presentation slides.

Usage:
    python scripts/thumbnail.py input.pptx [output_prefix] [--cols N]

Creates a grid layout of slide thumbnails for quick visual analysis.
Labels each thumbnail with its XML filename.

Requires: Pillow, python-pptx
Optional: LibreOffice (soffice) + pdftoppm (poppler) for higher-fidelity rendering
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.dom import minidom

from PIL import Image, ImageDraw, ImageFont

THUMBNAIL_WIDTH = 300
CONVERSION_DPI = 100
MAX_COLS = 6
DEFAULT_COLS = 3
JPEG_QUALITY = 95
GRID_PADDING = 20
BORDER_WIDTH = 2
FONT_SIZE_RATIO = 0.10
LABEL_PADDING_RATIO = 0.4


def get_soffice_path() -> str:
    """Find soffice binary for the current platform."""
    system = platform.system()

    if system == "Darwin":
        candidates = [
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",
            os.path.expanduser("~/Applications/LibreOffice.app/Contents/MacOS/soffice"),
        ]
    elif system == "Windows":
        candidates = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ]
    else:  # Linux / WSL
        candidates = [
            "/usr/bin/soffice",
            "/usr/lib/libreoffice/program/soffice",
        ]

    for p in candidates:
        if os.path.isfile(p):
            return p

    # Fallback to PATH
    return "soffice"


def get_slide_info(pptx_path: Path) -> list[dict]:
    """Get ordered slide info from the presentation."""
    with zipfile.ZipFile(pptx_path, "r") as zf:
        rels_content = zf.read("ppt/_rels/presentation.xml.rels").decode("utf-8")
        rels_dom = minidom.parseString(rels_content)

        rid_to_slide = {}
        for rel in rels_dom.getElementsByTagName("Relationship"):
            rid = rel.getAttribute("Id")
            target = rel.getAttribute("Target")
            rel_type = rel.getAttribute("Type")
            if "slide" in rel_type and target.startswith("slides/"):
                rid_to_slide[rid] = target.replace("slides/", "")

        pres_content = zf.read("ppt/presentation.xml").decode("utf-8")
        pres_dom = minidom.parseString(pres_content)

        slides = []
        for sld_id in pres_dom.getElementsByTagName("p:sldId"):
            rid = sld_id.getAttribute("r:id")
            if rid in rid_to_slide:
                slides.append({"name": rid_to_slide[rid]})

        return slides


def has_soffice() -> bool:
    """Check if LibreOffice is available."""
    soffice = get_soffice_path()
    if soffice != "soffice":
        return True
    return shutil.which("soffice") is not None


def convert_to_images_soffice(pptx_path: Path, temp_dir: Path) -> list[Path]:
    """Convert .pptx to slide images via LibreOffice + pdftoppm."""
    soffice = get_soffice_path()
    pdf_path = temp_dir / f"{pptx_path.stem}.pdf"

    result = subprocess.run(
        [soffice, "--headless", "--convert-to", "pdf", "--outdir", str(temp_dir), str(pptx_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0 or not pdf_path.exists():
        return []

    if not shutil.which("pdftoppm"):
        return []

    result = subprocess.run(
        ["pdftoppm", "-jpeg", "-r", str(CONVERSION_DPI), str(pdf_path), str(temp_dir / "slide")],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return []

    return sorted(temp_dir.glob("slide-*.jpg"))


def convert_to_images_pptx(pptx_path: Path, temp_dir: Path) -> list[Path]:
    """Create simple slide preview images using python-pptx + Pillow.

    This is a fallback when LibreOffice is not available.
    Renders slide backgrounds and text content as a visual summary.
    Not pixel-perfect, but useful for quick overview and QA.
    """
    from pptx import Presentation
    from pptx.util import Emu

    prs = Presentation(str(pptx_path))
    slide_w = prs.slide_width or Emu(9144000)  # default 10 inches
    slide_h = prs.slide_height or Emu(6858000)  # default 7.5 inches

    # Render at a reasonable size
    render_w = 960
    render_h = int(render_w * (slide_h / slide_w))
    scale = render_w / (slide_w / 914400)  # EMU to inches to pixels

    images = []
    for i, slide in enumerate(prs.slides, 1):
        img = Image.new("RGB", (render_w, render_h), "#FFFFFF")
        draw = ImageDraw.Draw(img)

        # Try to render background color
        bg_color = _get_slide_bg_color(slide)
        if bg_color:
            draw.rectangle([(0, 0), (render_w, render_h)], fill=bg_color)

        # Render text from shapes
        try:
            body_font = ImageFont.load_default(size=14)
            title_font = ImageFont.load_default(size=24)
        except Exception:
            body_font = ImageFont.load_default()
            title_font = body_font

        for shape in slide.shapes:
            if not shape.has_text_frame:
                continue

            # Convert EMU position to pixels
            x = int((shape.left or 0) / slide_w * render_w)
            y = int((shape.top or 0) / slide_h * render_h)
            w = int((shape.width or 0) / slide_w * render_w)

            text = shape.text_frame.text.strip()
            if not text:
                continue

            # Determine if this is likely a title (large text, near top)
            is_title = y < render_h * 0.35 and len(text) < 80
            font = title_font if is_title else body_font

            # Determine text color based on background
            text_color = "#000000" if not bg_color or _is_light(bg_color) else "#FFFFFF"

            # Word-wrap and draw
            lines = _wrap_text(draw, text, font, max(w, 100))
            for j, line in enumerate(lines[:8]):  # limit lines
                draw.text((x, y + j * (font.size + 4)), line, fill=text_color, font=font)

        # Draw shapes (non-text) as colored rectangles
        for shape in slide.shapes:
            if shape.has_text_frame:
                continue
            fill_color = _get_shape_fill(shape)
            if fill_color:
                sx = int((shape.left or 0) / slide_w * render_w)
                sy = int((shape.top or 0) / slide_h * render_h)
                sw = int((shape.width or 0) / slide_w * render_w)
                sh = int((shape.height or 0) / slide_h * render_h)
                draw.rectangle([(sx, sy), (sx + sw, sy + sh)], fill=fill_color, outline="#CCCCCC")

        out_path = temp_dir / f"slide-{i:02d}.jpg"
        img.save(str(out_path), quality=JPEG_QUALITY)
        images.append(out_path)

    return images


def _get_slide_bg_color(slide) -> str | None:
    """Extract background color from a slide."""
    try:
        bg = slide.background
        if bg and bg.fill and bg.fill.type is not None:
            color = bg.fill.fore_color
            if color and color.rgb:
                return f"#{color.rgb}"
    except Exception:
        pass
    return None


def _get_shape_fill(shape) -> str | None:
    """Extract fill color from a shape."""
    try:
        if shape.fill and shape.fill.type is not None:
            color = shape.fill.fore_color
            if color and color.rgb:
                return f"#{color.rgb}"
    except Exception:
        pass
    return None


def _is_light(hex_color: str) -> bool:
    """Check if a hex color is light."""
    c = hex_color.lstrip("#")
    if len(c) != 6:
        return True
    r, g, b = int(c[:2], 16), int(c[2:4], 16), int(c[4:], 16)
    return (r * 299 + g * 587 + b * 114) / 1000 > 128


def _wrap_text(draw: ImageDraw.Draw, text: str, font, max_width: int) -> list[str]:
    """Simple word-wrap for text rendering."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines or [text]


def convert_to_images(pptx_path: Path, temp_dir: Path) -> list[Path]:
    """Convert .pptx to slide images. Uses soffice if available, falls back to python-pptx."""
    if has_soffice():
        images = convert_to_images_soffice(pptx_path, temp_dir)
        if images:
            return images
        print("  soffice conversion failed, falling back to python-pptx renderer", file=sys.stderr)

    return convert_to_images_pptx(pptx_path, temp_dir)


def create_grid(
    slides: list[tuple[Path, str]], cols: int, width: int
) -> Image.Image:
    """Create a thumbnail grid image."""
    font_size = int(width * FONT_SIZE_RATIO)
    label_padding = int(font_size * LABEL_PADDING_RATIO)

    with Image.open(slides[0][0]) as img:
        aspect = img.height / img.width
    height = int(width * aspect)

    rows = (len(slides) + cols - 1) // cols
    grid_w = cols * width + (cols + 1) * GRID_PADDING
    grid_h = rows * (height + font_size + label_padding * 2) + (rows + 1) * GRID_PADDING

    grid = Image.new("RGB", (grid_w, grid_h), "white")
    draw = ImageDraw.Draw(grid)

    try:
        font = ImageFont.load_default(size=font_size)
    except Exception:
        font = ImageFont.load_default()

    for i, (img_path, slide_name) in enumerate(slides):
        row, col = i // cols, i % cols
        x = col * width + (col + 1) * GRID_PADDING
        y_base = row * (height + font_size + label_padding * 2) + (row + 1) * GRID_PADDING

        # Draw label
        bbox = draw.textbbox((0, 0), slide_name, font=font)
        text_w = bbox[2] - bbox[0]
        draw.text(
            (x + (width - text_w) // 2, y_base + label_padding),
            slide_name, fill="black", font=font,
        )

        # Draw thumbnail
        y_thumbnail = y_base + label_padding + font_size + label_padding
        with Image.open(img_path) as img:
            img.thumbnail((width, height), Image.Resampling.LANCZOS)
            w, h = img.size
            tx = x + (width - w) // 2
            ty = y_thumbnail + (height - h) // 2
            grid.paste(img, (tx, ty))

            if BORDER_WIDTH > 0:
                draw.rectangle(
                    [(tx - BORDER_WIDTH, ty - BORDER_WIDTH),
                     (tx + w + BORDER_WIDTH - 1, ty + h + BORDER_WIDTH - 1)],
                    outline="gray", width=BORDER_WIDTH,
                )

    return grid


def main():
    parser = argparse.ArgumentParser(description="Create thumbnail grids from PowerPoint slides.")
    parser.add_argument("input", help="Input .pptx file")
    parser.add_argument("output_prefix", nargs="?", default="thumbnails", help="Output prefix (default: thumbnails)")
    parser.add_argument("--cols", type=int, default=DEFAULT_COLS, help=f"Columns (default: {DEFAULT_COLS}, max: {MAX_COLS})")
    parser.add_argument("--slides-dir", default=None, help="Save individual slide images to this directory")
    args = parser.parse_args()

    cols = min(args.cols, MAX_COLS)
    input_path = Path(args.input)

    if not input_path.exists() or input_path.suffix.lower() != ".pptx":
        print(f"Error: Invalid PowerPoint file: {args.input}", file=sys.stderr)
        sys.exit(1)

    output_path = Path(f"{args.output_prefix}.jpg")

    slide_info = get_slide_info(input_path)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        images = convert_to_images(input_path, temp_path)

        if not images:
            print("Error: No slide images generated", file=sys.stderr)
            sys.exit(1)

        # Save individual slide images if requested
        if args.slides_dir:
            slides_dir = Path(args.slides_dir)
            slides_dir.mkdir(parents=True, exist_ok=True)
            for i, img_path in enumerate(images, 1):
                dst = slides_dir / f"slide-{i:02d}.jpg"
                shutil.copy2(img_path, dst)
                print(f"Slide: {dst}")

        # Pair images with slide names
        slides = list(zip(images, [s["name"] for s in slide_info[:len(images)]]))

        # Split into grids if many slides
        max_per_grid = cols * (cols + 1)
        for chunk_idx in range(0, len(slides), max_per_grid):
            chunk = slides[chunk_idx:chunk_idx + max_per_grid]
            grid = create_grid(chunk, cols, THUMBNAIL_WIDTH)

            if len(slides) <= max_per_grid:
                out_file = output_path
            else:
                out_file = output_path.parent / f"{output_path.stem}-{chunk_idx // max_per_grid + 1}{output_path.suffix}"

            grid.save(str(out_file), quality=JPEG_QUALITY)
            print(f"Created: {out_file}")


if __name__ == "__main__":
    main()
