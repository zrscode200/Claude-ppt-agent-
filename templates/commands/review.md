---
description: Analyze a presentation, document, or slide images and produce a review report
argument-hint: <path to .pptx, document, or slide images>
---

# Review

Analyze input and produce a structured assessment. This is a fundamental action — it can be invoked directly or as part of a composed workflow (e.g., `/improve-deck`, `/deck-from-doc`).

## Inputs

Accept any of:
- `.pptx` file (existing deck)
- Document (`.md`, `.txt`, `.docx`, `.pdf`) — use `python -m markitdown` for docx/pdf
- Slide images (`.jpg`, `.png`)
- Pasted text in conversation

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
2. **Generate visuals** (if scope includes style):
   - `python scripts/soffice.py <deck>.pptx --output-dir <slides-dir>/`
   - Or `python scripts/thumbnail.py <deck>.pptx` for a quick overview
3. **Analyze**:
   - Content scope: assess messages, data accuracy, completeness, flow, conciseness
   - Style scope: spawn `qa-reviewer` sub-agent with slide images and the inspection checklist
   - Full scope: both
4. **Write review report**

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
