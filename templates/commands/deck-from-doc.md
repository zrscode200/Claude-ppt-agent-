---
description: Create a presentation from a document, outline, or notes
argument-hint: <path to source document>
---

# Deck From Doc

Turn an existing document, meeting notes, outline, or brief into a presentation.

## Workflow

1. **Read the source document.** Extract:
   - Key topics and sections
   - Data points, stats, quotes
   - Structure and flow
   - Implied audience and tone

2. **Content plan from the document.** Present a lightweight inline outline mapping source content to slides:

   ```
   Slides:
     1. Title — from document title / intro
     2. Problem Statement — from section 1 (summarized)
     3. Key Findings — from section 2 (3 stat callouts)
     4. Recommendations — from section 3 (distilled to 4 points)
     5. Next Steps — from conclusion
   ```

   Note what to include vs. leave out — decks should be concise. Iterate with the user, then write `content-plan-draft-1.md`. Same iteration flow as `/create-deck` → `content-plan-approved.md`.

3. **Style plan.** Suggest visual direction based on the document's tone and audience. Present inline, iterate, then write `style-plan-draft-1.md` → `style-plan-approved.md`.

   Style plan is optional here — if the user wants to focus on content mapping, agent uses sensible defaults.

4. **Spec + Build + QA + Deliver** — same as `/create-deck` from Phase 3 onward.

## Supported Source Formats

- Markdown files (`.md`)
- Text files (`.txt`)
- Word documents (`.docx`) — use `python -m markitdown` to extract
- PDF files (`.pdf`) — use `python -m markitdown` to extract
- Or just pasted text in the conversation

## Key Principle

**Decks are not documents.** Don't put every sentence on a slide. Distill, summarize, and visualize. A good deck:
- Has 1 key message per slide
- Uses visuals to support the message
- Leaves detail for speaker notes or handouts
