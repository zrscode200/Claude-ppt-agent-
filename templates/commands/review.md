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
2. **Unpack**: `python scripts/unpack.py <deck>.pptx unpacked/`
3. **Generate images** (text layout and spacing):
   - `python scripts/thumbnail.py <deck>.pptx <slides-dir>/thumbnails --slides-dir <slides-dir>/`
   - Images show text positions, spacing, and alignment
   - With LibreOffice installed, images also show full visual fidelity (shapes, colors, etc.)
4. **Analyze** — combine sources:
   - Content (from markitdown): messages, data accuracy, completeness, flow
   - For style scope: spawn QA agents — scale to the deck:
     - **≤6 slides**: single `qa-reviewer` (section mode) with all slide images, raw XML + theme XML from `unpacked/`, and content summary from markitdown
     - **>6 slides**: per-section agents (each gets its section's images, XML, content summary) + one holistic agent (all thumbnails, cross-slide consistency)
   - For content-only scope: main agent reviews content structure and flow directly
5. **Write review report**
   - Merge QA agent findings (if style scope) with main agent's content analysis
   - If LibreOffice is not installed, note that full visual composition rendering is available by installing it

### For document input

1. **Extract content**: read directly (markdown/text) or `python -m markitdown` (docx/pdf)
2. **Analyze**: key topics, structure, what translates to slides vs. what doesn't, implied audience/tone
3. **Write review report** — focused on content mapping potential

### For slide images

1. **Spawn QA agents** — if ≤6 images, single agent; if >6, section agents (grouped by ~4-5 slides) + holistic agent
2. **Write review report** from merged findings

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

## Visual QA (for style scope)

Spawn QA agents per the standard pattern (see `subagent-prompts.md` for section and holistic prompt templates). The full inspection checklists live in `.claude/agents/qa-reviewer.md` — do not duplicate them here.
