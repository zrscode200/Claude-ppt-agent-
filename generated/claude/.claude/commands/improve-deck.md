---
description: Review and improve an existing presentation
argument-hint: <path to .pptx file>
---

# Improve Deck

Composed workflow: **Review → Edit**

Analyze an existing deck, then apply improvements. Combines the `/review` and `/edit` fundamentals.

## Workflow

### Step 1: Review

Run `/review` on the existing deck:

1. Generate thumbnails: `python scripts/thumbnail.py <deck>.pptx`
2. Extract content: `python -m markitdown <deck>.pptx`
3. If the user hasn't specified what to change: present findings and ask what they'd like to improve
4. If the user already specified changes: use the review to understand the current state
5. Save review report to `.ppt/decks/<deck-name>/review-<n>.md`

### Step 2: Edit

Run `/edit` on the deck with the requested changes:

- **Direct mode** for small, targeted changes (<=2 slides)
- **Plan mode** for broader changes (>2 slides or structural)

The `/edit` fundamental handles:
- Mode and scope detection (content/style/both)
- Edit plan creation and iteration (if plan mode)
- Unpack/edit/pack workflow
- Sub-agent orchestration
- Versioning and changelog
- QA on changed slides

See `/edit` for the full flow.

### Step 3: Deliver

- Show slide images of the new version
- Report the file path and changelog
- Offer further refinement

## What this adds over `/edit` alone

- The Review step first — understand the deck before changing it
- Presents findings to the user for context
- Natural entry point for "improve this deck" intent

Note: deck registration (creating a folder for untracked files, copying original to v1) is handled by `/edit`.
