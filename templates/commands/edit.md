---
description: Modify an existing presentation
argument-hint: <path to .pptx file or description of changes>
---

# Edit

Modify an existing presentation. This is a fundamental action — it can be invoked directly or as part of a composed workflow (e.g., `/improve-deck`).

## Mode Detection

Detect the mode from the scope of the request:

| Mode | Trigger | Flow |
|------|---------|------|
| **Direct** | Small, targeted changes — "fix spacing on slide 3", "change the title font" | Apply changes → QA |
| **Plan** | Broader changes — "redesign the data section", "make it more modern" | Edit plan(s) → approve → apply → QA |

Default to **direct** for changes affecting <=2 slides. Default to **plan** for broader changes.

## Scope Detection

Detect what kind of change is needed:

| Scope | Trigger | Artifact |
|-------|---------|----------|
| **Content** | "add a Q4 section", "update the numbers", "restructure the flow" | `edit-content-plan` |
| **Style** | "make it more modern", "switch to dark theme", "fix the layouts" | `edit-style-plan` |
| **Both** | "redesign the data section with new charts", "overhaul slides 3-5" | Both plans |

## Direct Mode

For small, targeted changes:

1. **Analyze** the deck:
   - `python scripts/thumbnail.py <deck>.pptx` for visual overview
   - `python -m markitdown <deck>.pptx` for content extraction
2. **Apply** changes using the unpack/edit/pack workflow:
   - `python scripts/unpack.py <deck>.pptx unpacked/`
   - Edit the relevant slide XML files
   - `python scripts/clean.py unpacked/`
   - `python scripts/pack.py unpacked/ output.pptx --original <deck>.pptx`
3. **Save** as next version (`v<n+1>/`)
4. **QA** — run Review (style scope) on affected slides
5. **Changelog** — write `v<n+1>/changelog.md`

## Plan Mode

For broader changes:

### Planning Phase

**If scope includes style**, first understand the current design system:
1. Unpack: `python scripts/unpack.py <deck>.pptx unpacked/`
2. Read theme: `unpacked/ppt/theme/theme1.xml` → color scheme, font scheme
3. Generate individual slide images: `python scripts/thumbnail.py <deck>.pptx edit-thumbnails --slides-dir unpacked/slides/`
4. Spawn `style-extractor` sub-agent with: slide image paths from `unpacked/slides/` + theme summary (colors + fonts from step 2)
5. Use the extraction report to understand the current style before planning changes

For content-only scope, skip the above — use `python -m markitdown <deck>.pptx` and `python scripts/thumbnail.py <deck>.pptx` for a quick overview instead.

Create only the relevant edit plan(s). Present changes inline for the user to react to:

**Content changes:**
```
Slide 3: Replace bullet list with 4 stat callouts (add Q4 data)
Slide 6 (new): Q4 deep dive by region
Slide 7: Update conclusion with new projections
```

**Style changes:**
```
Global: Switch from warm-terracotta to midnight-executive
Slide 3: Change layout from bullets to two-column (stats + chart)
Slide 5: Replace icon rows with 2x2 grid
```

Iterate with the user. When happy, write the relevant plan(s):
- `edit-content-plan-draft-<n>.md` for content changes
- `edit-style-plan-draft-<n>.md` for style changes

Same iteration flow as Create — increment drafts, never overwrite, approve when ready.

### Apply Phase

1. **Unpack**: `python scripts/unpack.py <deck>.pptx unpacked/`
2. **Edit**:
   - If >8 slides changing: spawn `slide-editor` sub-agents with the relevant edit plan(s)
   - If <=8 slides: edit directly using the Edit tool
3. **Clean + pack**:
   - `python scripts/clean.py unpacked/`
   - `python scripts/pack.py unpacked/ output.pptx --original <deck>.pptx`
4. **Save** to next version folder (`v<n+1>/`)

### QA Phase

Run a Review (style scope) on changed slides:

1. Generate slide images:
   ```
   python scripts/thumbnail.py <deck>.pptx v<n>/slides/thumbnails --slides-dir v<n>/slides/
   ```
2. Spawn `qa-reviewer` sub-agent with:
   - Individual slide images from `v<n>/slides/`
   - Edit plan(s) for reference (what was intended)
3. Fix issues, re-verify — at least one fix-and-verify cycle
4. Save review report to `.ppt/decks/<deck-name>/review-<n>.md`

### Changelog

Write `v<n+1>/changelog.md`:

```markdown
# Changelog: v<n+1>

## Changes from v<n>
- Slide 3: Replaced bullet list with stat callouts + bar chart
- Slide 6: Added Q4 deep dive (new slide)
- Slide 7: Updated conclusion with new projections
```

## Deck Registration

If the `.pptx` file is not already tracked in `.ppt/decks/`:
1. Create a deck folder from the filename (kebab-case)
2. Copy the original `.pptx` to `v1/` as the baseline
3. New edits go to `v2/`

If already tracked, find the latest version and increment.

## Artifact Output

| Mode | Artifacts |
|------|-----------|
| Plan | `edit-content-plan-draft-<n>.md` and/or `edit-style-plan-draft-<n>.md`, `v<n>/<deck>.pptx`, `v<n>/changelog.md`, `v<n>/slides/`, `review-<n>.md` |
| Direct | `v<n>/<deck>.pptx`, `v<n>/changelog.md`, `v<n>/slides/`, `review-<n>.md` |
