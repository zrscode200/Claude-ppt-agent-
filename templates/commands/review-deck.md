---
description: Review an existing presentation and provide feedback
argument-hint: <path to .pptx file>
---

# Review Deck

Analyze a presentation and provide a detailed feedback report. **No changes made.**

## Workflow

1. **Analyze the deck:**
   - `python scripts/thumbnail.py <deck>.pptx` — visual overview
   - `python -m markitdown <deck>.pptx` — content extraction
   - Convert to full-res images for detailed inspection

2. **Inspect each slide.** For each, note:
   - Layout effectiveness
   - Visual hierarchy and readability
   - Color usage and contrast
   - Spacing and alignment
   - Content clarity and conciseness

3. **Write the review report.** Structure:

   ```markdown
   # Deck Review: [Title]

   ## Summary
   [1-2 sentence overall assessment]

   ## Scores
   | Category | Score | Notes |
   |----------|-------|-------|
   | Design | X/10 | ... |
   | Content | X/10 | ... |
   | Structure | X/10 | ... |
   | Visual Consistency | X/10 | ... |
   | Overall | X/10 | ... |

   ## Strengths
   - ...

   ## Issues

   ### Critical
   - [Slide N]: ...

   ### Important
   - [Slide N]: ...

   ### Minor
   - [Slide N]: ...

   ## Recommendations
   1. ...
   2. ...
   ```

4. **Present to user.** Offer: "Want me to improve this deck? I can apply these fixes with `/improve-deck`."

## Scoring Guide

- **Design (visual quality)**: Color palette, typography, spacing, visual elements, consistency
- **Content (message clarity)**: Key messages land, text is concise, data is clear
- **Structure (flow)**: Logical order, good pacing, appropriate slide count
- **Visual Consistency**: Same motif throughout, consistent spacing/fonts/colors
