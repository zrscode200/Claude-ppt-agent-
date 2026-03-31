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

**If user provides a reference `.pptx`** ("match this style", "use this as a template"):
1. Unpack: `python scripts/unpack.py <ref>.pptx unpacked-ref/`
2. Read theme: `unpacked-ref/ppt/theme/theme1.xml` → extract color scheme (dk1, lt1, accent1-6 as hex), font scheme (major/minor family)
3. Generate individual slide images: `python scripts/thumbnail.py <ref>.pptx ref-thumbnails --slides-dir unpacked-ref/slides/`
4. Spawn `style-extractor` sub-agent with: slide image paths from `unpacked-ref/slides/` + theme summary (colors + fonts from step 2)
5. Use the style extraction report to seed the style plan — map extracted colors to primary/secondary/accent, fonts to header/body, observed layouts and motif to per-slide layout suggestions

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
5. If >12 slides: spawn `slide-builder` sub-agents — split by sub-topic/section, each agent gets content plan + style plan + theme JSON for their section
6. If <=12 slides: build in a single PptxGenJS script
7. Output `.pptx` to the version folder

### QA Phase — MANDATORY

**DO NOT skip QA. DO NOT go directly from build to delivery.**

1. Unpack the freshly built deck: `python scripts/unpack.py <deck>.pptx unpacked/`
2. Generate slide images:
   ```
   python scripts/thumbnail.py <deck>.pptx v<n>/slides/thumbnails --slides-dir v<n>/slides/
   ```
3. Spawn QA agents — scale to the deck:
   - **≤6 slides**: single `qa-reviewer` (section mode) covering all slides with all images, XML, diagrams, and plans
   - **>6 slides**: per-section agents (one per content plan section, or grouped by section dividers in direct mode) + one holistic agent. Each section agent gets its slice of images, XML, diagrams, and plans. Holistic agent gets all thumbnails + full style plan.
4. Merge findings from all QA agents
5. Fix reported issues
6. Re-generate images for affected slides and re-verify — at least one fix-and-verify cycle
7. Save review report to `.ppt/decks/<deck-name>/review-<n>.md`

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
