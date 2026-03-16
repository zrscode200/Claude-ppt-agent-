---
description: Build new presentation slides from plans or conversation
argument-hint: <topic, title, or description>
---

# Create

Build a new presentation. This is a fundamental action — it can be invoked directly or as part of a composed workflow (e.g., `/create-deck`, `/deck-from-doc`).

## Mode Detection

Detect the mode from context:

| Mode | Trigger | Flow |
|------|---------|------|
| **Plan** | User wants to iterate, complex deck, formal context | Content/style plans → build → QA |
| **Direct** | "just make it", "quick", simple request | Build with sensible defaults → QA |

Default to **plan** if ambiguous. Composed commands may override (e.g., `/create-deck` always uses plan mode).

## Plan Mode

### Planning Phase

Build two separate plans collaboratively with the user. **Start with whichever the user gravitates toward.**

**Detecting user focus:**
- Talking about messages, data, structure, audience → start **content plan**
- Talking about look, feel, colors, theme, layout → start **style plan**
- Talking about both → pick the more developed thread first

**Content plan** — present a lightweight inline outline:
```
Slides:
  1. Title — "Q3 Revenue Review"
  2. Agenda — 4 topics
  3. Key Metrics — revenue, margin, growth
  4. Revenue Breakdown — chart + takeaways
  5. Conclusion — next steps
```

Iterate piece by piece with the user. When happy, write `content-plan-draft-1.md` in `.ppt/decks/<deck-name>/` following the format in CLAUDE.md.

If changes requested after writing: write `content-plan-draft-2.md` (never overwrite). When approved → copy to `content-plan-approved.md`.

**Style plan** — present visual direction inline:
```
Theme: midnight-executive (dark navy + light blue)
Motif: subtle gradient bars as section dividers
Layouts: dark title, icon rows, stat callouts, two-column, dark conclusion
Background: dark-sandwich (dark bookends, light content)
```

Same iteration flow → `style-plan-approved.md`.

**Plan optionality:**
- Both plans encouraged but individually optional
- At least one plan must be approved before building
- If one is skipped, fill in sensible defaults during build (note what defaults were used)

### Build Phase

1. Read the theme from the style plan, or default from `.ppt/config.md`
2. Create deck folder: `.ppt/decks/<deck-name>/`
3. Create version folder: `v1/` (or next version if deck exists)
4. Determine method: PptxGenJS (default) or template-based
5. **If >5 slides: YOU MUST spawn `slide-builder` sub-agents** — split into groups of 2-4 slides, each agent gets content plan + style plan + theme JSON. Do NOT build all slides in one script.
6. If <=5 slides: build directly in a single PptxGenJS script
7. Output `.pptx` to the version folder

### QA Phase — MANDATORY

**DO NOT skip QA. DO NOT go directly from build to delivery.**

1. Generate slide images:
   ```
   python scripts/thumbnail.py <deck>.pptx v<n>/slides/thumbnails --slides-dir v<n>/slides/
   ```
   This produces individual slide images (`slide-01.jpg`, `slide-02.jpg`, ...) for QA inspection, plus a grid thumbnail. Works with or without LibreOffice.
2. Spawn `qa-reviewer` sub-agent with:
   - Individual slide images from `v<n>/slides/`
   - Content plan for completeness checks (plan mode), or markitdown extraction (direct mode)
   - Style plan for visual consistency checks (plan mode), or visual inspection only (direct mode)
3. Fix reported issues
4. Re-generate images for affected slides and re-verify — at least one fix-and-verify cycle
5. Save review report to `.ppt/decks/<deck-name>/review-<n>.md`

### Delivery

- Show slide images for visual preview
- Report the file path
- Ask if the user wants changes (→ `/edit` or `/improve-deck`)

## Direct Mode

Skip planning. Build from the user's description with sensible defaults:

1. Infer content (topic, slide count, key messages) from conversation
2. Pick theme from `.ppt/config.md` default or best fit for topic
3. Pick layouts (varied, never repeat consecutive)
4. Build directly (same build phase as above)
5. Run QA (same QA phase as above)
6. Deliver

No plan artifacts are created. The agent makes design decisions autonomously.

## Artifact Output

| Mode | Artifacts |
|------|-----------|
| Plan | `content-plan-draft-<n>.md`, `content-plan-approved.md`, `style-plan-draft-<n>.md`, `style-plan-approved.md`, `v<n>/<deck>.pptx`, `v<n>/slides/`, `review-<n>.md` |
| Direct | `v<n>/<deck>.pptx`, `v<n>/slides/`, `review-<n>.md` |
