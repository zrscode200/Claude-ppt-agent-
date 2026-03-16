# PPT Studio

## Trigger

Activate when the user's intent involves PowerPoint presentations:

**Trigger phrases:**
- "make me a deck", "create a presentation", "build slides"
- "improve this deck", "fix this presentation", "update these slides"
- "review this deck", "check this presentation", "what do you think of these slides"
- "turn this into slides", "make a deck from this document"
- Any mention of `.pptx` files in the context of creation or editing

**Do NOT trigger for:**
- General file operations that happen to involve `.pptx` (e.g., "move this file")
- Questions about PowerPoint format or specs (answer directly)
- Simple one-line requests about a single element (just do it)

## Routing

Route user intent to the appropriate command:

| Intent Pattern | Command | Notes |
|---------------|---------|-------|
| Wants a new presentation, willing to brainstorm | `/create-deck` | Spec-driven, thorough |
| Wants a quick deck, minimal back-and-forth | `/quick-deck` | Fast, no spec file |
| Has an existing `.pptx` to improve or edit | `/improve-deck` | Direct or spec-driven edits |
| Wants feedback on a deck, no changes | `/review-deck` | Analysis + report only |
| Wants visual QA on slides | `/qa-slides` | Convert + inspect |
| Has a document/notes to turn into slides | `/deck-from-doc` | Parse → spec → build |

**Ambiguous intent?** Default to `/create-deck` for new work, `/improve-deck` for existing files.

## Workflow Engine

### Phase Management

Track the current deck and phase. Artifacts live in `.ppt/decks/<deck-name>/`.

**Phase detection** (for resuming work):
```
if v<n>/qa-review.md exists           → QA complete, ready for next edition or delivery
elif v<n>/<deck>.pptx exists          → Build complete, needs QA
elif spec-approved.md exists          → Spec approved, ready to build
elif content-plan-approved.md exists
  and style-plan-approved.md exists   → Both plans approved, ready for spec
elif content-plan-approved.md exists  → Content plan approved, style plan pending (or skipped)
elif style-plan-approved.md exists    → Style plan approved, content plan pending (or skipped)
elif content-plan-draft-*.md exists
  or style-plan-draft-*.md exists     → Planning in progress
elif edit-content-plan-draft-*.md exists
  or edit-style-plan-draft-*.md exists → Edit planning in progress
else                                  → New deck, start from scratch
```

### Deck Naming

When creating a new deck:
1. Derive a kebab-case name from the topic (e.g., "Q3 Sales Review" → `q3-sales-review`)
2. Create the folder at `.ppt/decks/<name>/`
3. All artifacts for this deck live in that folder

### Version Management

Each build or edit cycle creates a new version:
- `v1/` — first build
- `v2/` — after first round of improvements
- `v3/` — and so on

Detect current version: find the highest `v<n>/` folder. New builds go to `v<n+1>/`.

For the first build, use `v1/`.

### Plan & Spec Lifecycle

**Planning (order-independent, individually optional):**
1. During conversation, detect whether user focuses on content or style
2. Start with whichever plan the user gravitates toward
3. Present lightweight inline outline → iterate → write `content-plan-draft-1.md` or `style-plan-draft-1.md`
4. If user requests changes, write `*-draft-2.md` (never overwrite)
5. When user approves a plan, copy to `*-approved.md`
6. Repeat for the other plan, or skip if user wants to move forward

**Spec:**
7. When at least one plan is approved, write `spec-approved.md` (thin doc referencing plans + build details)

**Edit plans (for `/improve-deck`):**
- Content-only change → `edit-content-plan-draft-<n>.md` only
- Style-only change → `edit-style-plan-draft-<n>.md` only
- Both → both edit plans

## Sub-Agent Orchestration

### Build Phase (PptxGenJS from scratch)

For decks with >5 slides:

1. **Divide slides** into groups of 2-4 by visual similarity
2. **Spawn `slide-builder` agents** — each gets:
   - Their assigned slides from the **content plan** (what to build)
   - The **style plan** or theme JSON (how it looks)
   - PptxGenJS API reference (`.claude/skills/ppt-studio/references/pptxgenjs-guide.md`)
   - Instruction: "Write a `buildSlides(pres, theme)` function"
   - If a plan was skipped, pass the defaults being used instead
3. **Assemble** — main agent creates wrapper script, inlines sub-agent functions, runs it
4. **Output** goes to `.ppt/decks/<name>/v<n>/<name>.pptx`

For decks with ≤5 slides: build directly, no sub-agents.

### Edit Phase (XML editing)

For improving existing decks with >3 slides to edit:

1. **Unpack** the `.pptx`: `python scripts/unpack.py <deck>.pptx unpacked/`
2. **Spawn `slide-editor` agents** — each gets:
   - Assigned slide XML file paths
   - The relevant edit plan(s) — content changes, style changes, or both
   - XML formatting rules (from `references/editing-guide.md`)
3. **Clean + pack** after all edits complete
4. **Output** to next version folder

### QA Phase

Always use a sub-agent:

1. **Convert** to images: `python scripts/soffice.py <deck>.pptx --output-dir slides/`
2. **Spawn `qa-reviewer` agent** with:
   - Slide image paths
   - **Content plan** for completeness checks (expected content per slide)
   - **Style plan** for visual consistency checks (theme, layouts, motif)
   - The QA checklist (overlaps, overflow, contrast, spacing, alignment)
   - If a plan was skipped, use markitdown extraction or defaults instead
3. **Fix** reported issues
4. **Re-verify** affected slides (spawn another QA agent if needed)
5. **Save** findings to `v<n>/qa-review.md`

## References

- Design guide: `.claude/skills/ppt-studio/references/design-guide.md`
- PptxGenJS API: `.claude/skills/ppt-studio/references/pptxgenjs-guide.md`
- Editing guide: `.claude/skills/ppt-studio/references/editing-guide.md`
- Sub-agent prompts: `.claude/skills/ppt-studio/references/subagent-prompts.md`
