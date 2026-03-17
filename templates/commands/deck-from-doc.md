---
description: Turn a document, outline, or notes into a presentation
argument-hint: <path to source document>
---

# Deck From Doc

Composed workflow: **Review (source document) → Create**

Parse a source document, then build a presentation from it. Combines the `/review` and `/create` fundamentals.

## Workflow

### Step 1: Review the Source Document

Run `/review` on the source document:

1. **Extract content**: read directly (markdown/text) or `python -m markitdown` (docx/pdf)
2. **Analyze**: key topics, sections, data points, stats, quotes, structure, implied audience/tone
3. **Assess** what translates to slides vs. what should be left out
4. Save review report to `.ppt/decks/<deck-name>/review-<n>.md`

### Step 1b: Extract Style (if source is `.pptx`)

When the source is an existing `.pptx`, also extract its design language:

1. Unpack: `python scripts/unpack.py <source>.pptx unpacked-ref/`
2. Read `unpacked-ref/ppt/theme/theme1.xml` → color scheme (dk1, lt1, accent1-6), font scheme (major/minor)
3. Inspect 2-3 slide XMLs → layout patterns, shape usage, background fills, spacing
4. Generate thumbnail: `python scripts/thumbnail.py <source>.pptx`
5. Summarize: colors, fonts, motif, background strategy, layout vocabulary

This extraction seeds the style plan in Step 2. The user can keep, modify, or discard the extracted style.

### Step 2: Create from Review

Run `/create` in plan mode, seeded with the review findings:

1. **Content plan** — map source content to slides. Present inline:
   ```
   Slides:
     1. Title — from document title / intro
     2. Problem Statement — from section 1 (summarized)
     3. Key Findings — from section 2 (3 stat callouts)
     4. Recommendations — from section 3 (distilled to 4 points)
     5. Next Steps — from conclusion
   ```
   Note what's included vs. left out. Iterate with user. The review report informs these decisions.

2. **Style plan** — if source was a `.pptx`, pre-populate from the style extraction (Step 1b). Otherwise, suggest visual direction based on the document's tone and audience. Optional — if the user wants to focus on content mapping, use sensible defaults.

3. **Build → QA → Deliver** — same as `/create` from the build phase onward.

## Supported Source Formats

- Markdown files (`.md`)
- Text files (`.txt`)
- Word documents (`.docx`) — use `python -m markitdown` to extract
- PDF files (`.pdf`) — use `python -m markitdown` to extract
- Existing `.pptx` files — recycle content or style from another deck
- Pasted text in conversation

## Key Principle

**Decks are not documents.** Don't put every sentence on a slide. Distill, summarize, and visualize. A good deck:
- Has 1 key message per slide
- Uses visuals to support the message
- Leaves detail for speaker notes or handouts

## What this adds over `/create` alone

- The Review step parses and analyzes the source document first
- Content plan is seeded from the review findings (not from scratch)
- Handles various input formats (docx, pdf, markdown, pptx, text)
- Natural entry point for "turn this into slides" intent
