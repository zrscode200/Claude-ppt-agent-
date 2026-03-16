---
description: Create a new presentation using the spec-driven workflow
argument-hint: <topic or title>
---

# Create Deck

Build a new presentation through conversation → planning → spec → build → QA → deliver.

## Phase 1: Conversation

**Start freeform.** Ask the user about their presentation:

> "Tell me about this presentation — what's it for, who's the audience, and what are the key messages you want to land?"

Follow the user's thread naturally. Probe for:
- Purpose and context (why does this deck exist?)
- Audience (who will see it, what do they care about?)
- Key messages (what should the audience remember?)
- Tone (formal, casual, technical, creative?)
- Visual direction (dark, minimal, bold, branded?)
- Any existing content, data, or documents to incorporate

**User provides `$ARGUMENTS`?** Use it as the starting topic, but still explore. The argument is a seed, not a complete brief.

## Phase 2: Planning

Build two separate plans collaboratively with the user. **Start with whichever the user gravitates toward** — if they're talking about content and structure, start with the content plan. If they're talking about look and feel, start with the style plan.

### Content Plan

Present a lightweight inline outline for the user to react to:

```
Slides:
  1. Title — "Q3 Revenue Review"
  2. Agenda — 4 topics
  3. Key Metrics — revenue, margin, growth
  4. Revenue Breakdown — chart + takeaways
  5. Conclusion — next steps
```

Iterate piece by piece — "swap slides 3 and 4", "make the data section two slides", "add a team slide". When the user is happy, write `content-plan-draft-1.md` following the format in CLAUDE.md.

If changes requested after writing:
- Write `content-plan-draft-2.md` (never overwrite)
- Iterate until approved → copy to `content-plan-approved.md`

### Style Plan

Present visual direction for the user to react to:

```
Theme: midnight-executive (dark navy + light blue)
Motif: subtle gradient bars as section dividers
Layouts: dark title, icon rows, stat callouts, two-column, dark conclusion
Background: dark-sandwich (dark bookends, light content)
```

Iterate — "try a warmer palette", "I want all-dark", "use a grid instead of icon rows". When happy, write `style-plan-draft-1.md` following the format in CLAUDE.md.

Same iteration flow → `style-plan-approved.md`.

### Plan optionality

Both plans are encouraged but individually optional:
- If the user only cares about content → skip the style plan, agent uses sensible defaults during build
- If the user only cares about style → skip the content plan (rare for new decks, more common for edits)
- At least one plan must be approved before proceeding

## Phase 3: Spec

Write a thin build-ready spec at `.ppt/decks/<deck-name>/spec-approved.md` that references both plans and adds build details (method, layout, output path). If a plan was skipped, note the defaults.

Confirm: "Plans approved. Building your deck now."

## Phase 4: Build

1. Read the theme from the style plan (or default from `.ppt/config.md`)
2. Determine method: PptxGenJS (default for from-scratch) or template-based
3. Create version folder: `.ppt/decks/<deck-name>/v1/`
4. If >5 slides: spawn `slide-builder` sub-agents with content plan + style plan
5. If ≤5 slides: build directly in a single PptxGenJS script
6. Run the script → output `.pptx` to the version folder

## Phase 5: QA

1. Convert to images: `python scripts/soffice.py <deck>.pptx --output-dir slides/`
2. Save images to `.ppt/decks/<deck-name>/v1/slides/`
3. Spawn `qa-reviewer` sub-agent with content plan (for completeness) and style plan (for visual consistency)
4. Fix reported issues
5. Re-verify affected slides
6. Save QA findings to `.ppt/decks/<deck-name>/v1/qa-review.md`

## Phase 6: Deliver

Present the final deck to the user:
- Show the slide images for a quick visual preview
- Report the file path
- Ask if they want any changes (if yes, start a new version via `/improve-deck`)
