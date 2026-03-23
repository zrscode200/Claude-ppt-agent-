---
description: Analyze a presentation, document, or slide images and produce a review report
argument-hint: <path to .pptx, document, or slide images>
---

# Review

Analyze input and produce a structured assessment. This is a fundamental action — it can be invoked directly or as part of a composed workflow (e.g., `/improve-deck`, `/deck-from-doc`).

## Inputs

Accept any of:
- `.pptx` file (existing deck)
- Document (`.md`, `.txt`, `.docx`, `.pdf`) — use `python -m markitdown` for docx/pdf, except previous review reports (`review-*.md`)
- Slide images (`.jpg`, `.png`)
- Pasted text in conversation

**Do not** read previous review reports (`review-*.md`) from the deck folder — see Fresh Eyes Rule below.

If `$ARGUMENTS` is provided, treat it as the input path.

## Scope Detection

Detect the scope from the user's request:

| Scope | Trigger | Focus |
|-------|---------|-------|
| **Full** | "review this deck", "what do you think" | Content + style + structure |
| **Content** | "is the messaging right", "check the flow" | Messages, data, completeness, flow |
| **Style/Visual** | "check the visuals", "QA this", "any design issues" | Design, layout, contrast, spacing, alignment |

Default to **full** if ambiguous.

## Workflow

### For `.pptx` input

1. **Extract content**: `python -m markitdown <deck>.pptx`
2. **Inspect visual structure** (if scope includes style):
   - `python scripts/unpack.py <deck>.pptx unpacked/`
   - Read `unpacked/ppt/theme/theme1.xml` → color scheme, font scheme
   - Sample 3-5 slide XMLs → identify shapes (`<p:sp>`), connectors (`<p:cxnSp>`), groups (`<p:grpSp>`), images (`<p:pic>`), fills (`<a:solidFill>`), tables, charts
   - This is how you determine what visual elements the deck contains
3. **Generate images** (text layout and spacing):
   - `python scripts/thumbnail.py <deck>.pptx <slides-dir>/thumbnails --slides-dir <slides-dir>/`
   - Images show text positions, spacing, and alignment
   - With LibreOffice installed, images also show full visual fidelity (shapes, colors, etc.)
4. **Analyze** — combine sources:
   - Content (from markitdown): messages, data accuracy, completeness, flow
   - Visual elements (from XML): shapes, colors, connectors, images, design system
   - Text layout (from images): spacing, alignment, overflow, positioning
   - For style scope: spawn `qa-reviewer` sub-agent with slide images + summary of XML visual findings
5. **Write review report**
   - Be explicit about what was verified from XML vs. images
   - If LibreOffice is not installed, note that full visual composition rendering is available by installing it

### For document input

1. **Extract content**: read directly (markdown/text) or `python -m markitdown` (docx/pdf)
2. **Analyze**: key topics, structure, what translates to slides vs. what doesn't, implied audience/tone
3. **Write review report** — focused on content mapping potential

### For slide images

1. **Spawn `qa-reviewer` sub-agent** with images and checklist
2. **Write review report** from findings

## Review Report Format

```markdown
# Review: [Title or Filename]

## Summary
[1-2 sentence overall assessment]

## Scores (for .pptx full reviews)
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
- [Slide N / Section]: ...

### Important
- [Slide N / Section]: ...

### Minor
- [Slide N / Section]: ...

## Recommendations
1. ...
2. ...
```

For content-only or style-only reviews, include only the relevant sections.

## Artifact Output

**For `.pptx` input:** Save the review report to `.ppt/decks/<deck-name>/review-<n>.md` (increment `<n>` — never overwrite previous reviews). If the deck is not yet tracked in `.ppt/decks/`, create a deck folder from the filename.

**For document/text input (standalone):** Present the review in the conversation. Only persist to a deck folder if this Review is part of a composed workflow (e.g., `/deck-from-doc`) where a deck will be created.

If this Review is part of a composed workflow, the report is always saved — it serves as audit trail.

## Scoring Guide

- **Design**: Color palette, typography, spacing, visual elements, consistency
- **Content**: Key messages land, text is concise, data is clear
- **Structure**: Logical order, good pacing, appropriate slide count
- **Visual Consistency**: Same motif throughout, consistent spacing/fonts/colors

## Visual QA Checklist (for style scope)

When spawning the `qa-reviewer` agent, include this checklist:

- Overlapping elements (text through shapes, lines through words)
- Text overflow or cut off at edges/box boundaries
- Elements too close (< 0.3" gaps) or nearly touching
- Uneven spacing (large empty area vs. cramped area)
- Insufficient margin from slide edges (< 0.5")
- Columns or similar elements not aligned consistently
- Low-contrast text or icons
- Text boxes too narrow causing excessive wrapping
- Leftover placeholder content
- Same layout repeated on consecutive slides
- Text-only slides without visual elements
