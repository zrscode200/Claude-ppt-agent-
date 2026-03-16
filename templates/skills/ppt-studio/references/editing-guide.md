# Editing Existing Presentations

## Template-Based Workflow

When editing an existing .pptx file:

1. **Analyze existing slides:**
   ```bash
   python scripts/thumbnail.py template.pptx
   python -m markitdown template.pptx
   ```

2. **Plan slide mapping.** For each content section, choose a template slide.
   Use varied layouts — don't repeat the same text-heavy layout.

3. **Unpack:** `python scripts/unpack.py template.pptx unpacked/`

4. **Structural changes** (do before content editing):
   - Delete: remove `<p:sldId>` from `<p:sldIdLst>` in `ppt/presentation.xml`
   - Duplicate: `python scripts/add_slide.py unpacked/ slide2.xml`
   - Reorder: rearrange `<p:sldId>` elements

5. **Edit content:** Update text in each `slide{N}.xml`.
   Use sub-agents for parallel editing (each slide is a separate XML file).

6. **Clean:** `python scripts/clean.py unpacked/`

7. **Pack:** `python scripts/pack.py unpacked/ output.pptx --original template.pptx`

---

## Scripts Quick Reference

| Script | Purpose |
|--------|---------|
| `unpack.py` | Extract and pretty-print PPTX |
| `add_slide.py` | Duplicate a slide |
| `clean.py` | Remove orphaned files |
| `pack.py` | Repack with validation |
| `thumbnail.py` | Create visual grid of slides |

---

## Slide Operations

Slide order is in `ppt/presentation.xml` → `<p:sldIdLst>`.

- **Reorder:** Rearrange `<p:sldId>` elements
- **Delete:** Remove `<p:sldId>`, then run `clean.py`
- **Add:** Use `add_slide.py` (handles Content_Types, rels, IDs)

---

## Editing Content

Use the **Edit tool** for all XML changes — not sed or Python scripts.

For each slide:
1. Read the slide's XML
2. Identify ALL placeholder content
3. Replace each placeholder with final content

### Formatting Rules

- **Bold headers:** Use `b="1"` on `<a:rPr>` for titles, section headers, and inline labels
- **Never use unicode bullets:** Use `<a:buChar>` or `<a:buAutoNum>`
- **Bullet consistency:** Let bullets inherit from layout

### Multi-Item Content

Create separate `<a:p>` for each item — never concatenate:

```xml
<!-- CORRECT -->
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799" b="1"/><a:t>Step 1</a:t></a:r>
</a:p>
<a:p>
  <a:pPr algn="l"><a:lnSpc><a:spcPts val="3919"/></a:lnSpc></a:pPr>
  <a:r><a:rPr lang="en-US" sz="2799"/><a:t>Do the first thing.</a:t></a:r>
</a:p>
```

Copy `<a:pPr>` from the original paragraph to preserve line spacing.

### Smart Quotes

When adding text with quotes, use XML entities:

| Character | XML Entity |
|-----------|------------|
| Left double " | `&#x201C;` |
| Right double " | `&#x201D;` |
| Left single ' | `&#x2018;` |
| Right single ' | `&#x2019;` |

### Other Rules

- **Whitespace:** Use `xml:space="preserve"` on `<a:t>` with leading/trailing spaces
- **XML parsing:** If you need to parse XML programmatically, use `defusedxml.minidom` — never `xml.etree.ElementTree` (it corrupts namespaces)

---

## Template Adaptation Pitfalls

**Fewer items than template:**
- Remove excess elements entirely (images, shapes, text boxes) — don't just clear text
- Check for orphaned visuals after clearing content

**More text than template:**
- Shorter replacements: usually safe
- Longer replacements: may overflow — flag for QA
- Consider truncating or splitting to fit design

---

## Using python-pptx for Edits

For simpler edits, `python-pptx` can be more convenient than XML manipulation:

```python
from pptx import Presentation
from pptx.util import Inches, Pt

prs = Presentation("input.pptx")
slide = prs.slides[0]

for shape in slide.shapes:
    if shape.has_text_frame:
        for para in shape.text_frame.paragraphs:
            for run in para.runs:
                if run.text == "OLD TEXT":
                    run.text = "NEW TEXT"

prs.save("output.pptx")
```

Use python-pptx when:
- Making simple text replacements
- Changing colors or fonts programmatically
- Adding/removing shapes
- Working with slide layouts

Use XML editing (unpack/edit/pack) when:
- Making complex structural changes
- Need fine-grained control over XML attributes
- Working with template-specific markup
