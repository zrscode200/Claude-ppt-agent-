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

2. **Propose a deck structure.** Present to the user:
   - Suggested slide count
   - Slide-by-slide outline with content mapping
   - Which parts of the document map to which slides
   - What to include vs. leave out (decks should be concise)
   - Suggested theme

3. **User confirms or adjusts** the proposed structure.

4. **Write a spec.** Create `spec-draft-1.md` in `.ppt/decks/<deck-name>/`.
   - Map source content to each slide
   - Note which content needs summarizing vs. direct use
   - Follow the standard spec format from CLAUDE.md

5. **Follow the standard creation workflow:**
   - User approves spec → build → QA → deliver
   - Same as `/create-deck` from Phase 2 onward

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
