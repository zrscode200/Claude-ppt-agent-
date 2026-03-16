---
description: Run visual QA on a presentation
argument-hint: <path to .pptx file>
---

# QA Slides

Visual quality assurance on a presentation. Convert to images and inspect for issues.

## Workflow

1. **Convert to images:**
   ```bash
   python scripts/office/soffice.py --headless --convert-to pdf <deck>.pptx
   pdftoppm -jpeg -r 150 <deck>.pdf slide
   ```

2. **Spawn `qa-reviewer` sub-agent** with the slide images and this checklist:

   ### QA Checklist
   - [ ] **Overlapping elements** — text through shapes, lines through words, stacked elements
   - [ ] **Text overflow** — cut off at edges or box boundaries
   - [ ] **Element collisions** — footers colliding with content, elements too close (<0.3" gaps)
   - [ ] **Uneven spacing** — large empty area in one place, cramped in another
   - [ ] **Insufficient margins** — content too close to slide edges (<0.5")
   - [ ] **Alignment issues** — columns or similar elements not aligned consistently
   - [ ] **Low contrast** — light text on light backgrounds, dark icons on dark backgrounds
   - [ ] **Narrow text boxes** — causing excessive wrapping
   - [ ] **Leftover placeholders** — template text not replaced
   - [ ] **Layout repetition** — same layout used on consecutive slides
   - [ ] **Missing visuals** — text-only slides without any visual elements

3. **Report findings** — categorized by severity (critical / important / minor)

4. **If issues found:**
   - Fix them
   - Re-convert affected slides
   - Re-inspect to verify fixes didn't create new issues
   - Repeat until clean

5. **Save report** to the deck's version folder as `qa-review.md`
