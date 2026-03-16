---
description: Create a new presentation using the spec-driven workflow
argument-hint: <topic or title>
---

# Create Deck

Build a new presentation through brainstorm → spec → build → QA → deliver.

## Phase 1: Brainstorm (Adaptive)

**Start freeform.** Ask the user about their presentation:

> "Tell me about this presentation — what's it for, who's the audience, and what are the key messages you want to land?"

Follow the user's thread naturally. Probe for:
- Purpose and context (why does this deck exist?)
- Audience (who will see it, what do they care about?)
- Key messages (what should the audience remember?)
- Tone (formal, casual, technical, creative?)
- Any existing content, data, or documents to incorporate

**Then run the checklist.** Before writing the spec, verify you have:

- [ ] Purpose
- [ ] Audience
- [ ] Tone
- [ ] Key messages / content outline
- [ ] Approximate slide count
- [ ] Theme preference (or suggest 2-3 from `themes/`)
- [ ] Any images, data, or branding to include
- [ ] Layout preferences (if any)

If anything is missing, ask. Don't assume.

**User provides `$ARGUMENTS`?** Use it as the starting topic, but still brainstorm. The argument is a seed, not a complete brief.

## Phase 2: Write the Spec

Create `.ppt/decks/<deck-name>/spec-draft-1.md` following the spec format in CLAUDE.md.

Present the spec to the user. Ask: "Does this capture what you're looking for? Anything to change?"

If changes requested:
- Write `spec-draft-2.md` (never overwrite draft 1)
- Iterate until the user approves

When approved:
- Copy to `spec-approved.md`
- Confirm: "Spec approved. Building your deck now."

## Phase 3: Build

1. Read the theme JSON from `themes/<theme-name>.json`
2. Determine method: PptxGenJS (default for from-scratch) or template-based
3. Create version folder: `.ppt/decks/<deck-name>/v1/`
4. If >5 slides: spawn `slide-builder` sub-agents (see SKILL.md for orchestration)
5. If ≤5 slides: build directly in a single PptxGenJS script
6. Run the script → output `.pptx` to the version folder

## Phase 4: QA

1. Convert to images: `soffice` → PDF → `pdftoppm`
2. Save images to `.ppt/decks/<deck-name>/v1/slides/`
3. Spawn `qa-reviewer` sub-agent
4. Fix reported issues
5. Re-verify affected slides
6. Save QA findings to `.ppt/decks/<deck-name>/v1/qa-review.md`

## Phase 5: Deliver

Present the final deck to the user:
- Show the slide images for a quick visual preview
- Report the file path
- Ask if they want any changes (if yes, start a new version via `/improve-deck`)
