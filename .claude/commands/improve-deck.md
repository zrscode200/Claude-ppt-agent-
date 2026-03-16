---
description: Improve or edit an existing presentation
argument-hint: <path to .pptx file>
---

# Improve Deck

Work on an existing presentation — fix issues, redesign sections, or make targeted edits.

## Two Modes

Detect which mode based on the scope of the request:

### Direct Edit Mode

For small, targeted changes: "fix the spacing on slide 3", "change the title font", "update the revenue number".

1. Analyze the deck (thumbnails + markitdown)
2. Apply the requested changes using the unpack/edit/pack workflow
3. Save as next version
4. Run QA on affected slides

### Spec-Driven Edit Mode

For broader changes: "redesign the data section", "make it more visual", "restructure the flow".

1. **Analyze** the existing deck:
   - `python scripts/thumbnail.py <deck>.pptx` for visual overview
   - `python -m markitdown <deck>.pptx` for content extraction
   - Present findings to user

2. **Write an edit spec** at `.ppt/decks/<deck-name>/edit-spec-draft-<n>.md`:
   ```markdown
   # Edit Spec: [Deck Name]

   ## Source
   - **File**: path/to/original.pptx
   - **Base Version**: v<n>

   ## Changes

   ### Slide 3: Revenue Overview
   - **Current**: Plain bullet list
   - **Change**: Replace with 3 stat callouts + bar chart
   - **Layout**: Two-column (stats left, chart right)

   ### Slide 5: Team
   - **Current**: 4-person grid
   - **Change**: Update to 3 people, remove person 4 entirely
   ...
   ```

3. **User approves** the edit spec

4. **Apply changes:**
   - Unpack with `unpack.py`
   - If >3 slides changing: spawn `slide-editor` sub-agents
   - If ≤3 slides: edit directly
   - Clean + pack

5. **Save as next version** (increment `v<n>/`)

6. **QA** on changed slides → save review → deliver

## Deck Registration

If the `.pptx` file is not already tracked in `.ppt/decks/`:
1. Create a deck folder from the filename
2. Copy the original `.pptx` to `v1/` as the baseline
3. New edits go to `v2/`

If it's already tracked, find the latest version and increment.

## Changelog

For v2+, create a `changelog.md` in the version folder:

```markdown
# Changelog: v2

## Changes from v1
- Slide 3: Replaced bullet list with stat callouts + bar chart
- Slide 5: Removed person 4 from team grid
- Slide 7: Updated footer text
```
