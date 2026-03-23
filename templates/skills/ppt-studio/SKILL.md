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

Route user intent to the appropriate command. Try fundamentals first, then composed commands:

### Fundamental Commands

| Intent | Command | Mode/Scope |
|--------|---------|------------|
| "review this deck", "what do you think" | `/review` | Full scope |
| "check the visuals", "QA this" | `/review` | Style scope |
| "is the messaging right", "check the flow" | `/review` | Content scope |
| "just make slides about X", "quick deck" | `/create` | Direct mode |
| "fix spacing on slide 3", "change the title font" | `/edit` | Direct mode |
| "redesign the data section" | `/edit` | Plan mode |

### Composed Commands

| Intent | Command | Composition |
|--------|---------|-------------|
| New deck, wants to brainstorm | `/create-deck` | Conversation → `/create` (plan) |
| Improve an existing deck | `/improve-deck` | `/review` → `/edit` |
| Turn a document into slides | `/deck-from-doc` | `/review` (doc) → `/create` |

**Ambiguous intent?**
- New work → `/create-deck`
- Existing file → `/improve-deck`
- "Quick" or "just do it" → `/create` (direct mode) or `/edit` (direct mode)

## Workflow Engine

### Phase Management

Track the current deck and phase. Artifacts live in `.ppt/decks/<deck-name>/`.

**Phase detection** (for resuming work):
```
if v<n>/<deck>.pptx exists
  and review-<n>.md exists (post-build) → QA complete, ready for delivery or next edition
elif v<n>/<deck>.pptx exists             → Build complete, needs QA (Review)
elif content-plan-approved.md exists
  or style-plan-approved.md exists       → Plan(s) approved, ready to build
elif content-plan-draft-*.md exists
  or style-plan-draft-*.md exists        → Planning in progress
elif edit-content-plan-draft-*.md exists
  or edit-style-plan-draft-*.md exists   → Edit planning in progress
elif review-*.md exists (no versions)    → Review complete, waiting for next action
else                                     → New deck, start from scratch
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

### Plan Lifecycle

**Planning (order-independent, individually optional):**
1. During conversation, detect whether user focuses on content or style
2. Start with whichever plan the user gravitates toward
3. Present lightweight inline outline → iterate → write `content-plan-draft-1.md` or `style-plan-draft-1.md`
4. If user requests changes, write `*-draft-2.md` (never overwrite)
5. When user approves a plan, copy to `*-approved.md`
6. Repeat for the other plan, or skip if user wants to move forward
7. At least one plan must be approved before building

**Edit plans (for `/edit` in plan mode):**
- Content-only change → `edit-content-plan-draft-<n>.md` only
- Style-only change → `edit-style-plan-draft-<n>.md` only
- Both → both edit plans

## Sub-Agent Orchestration

### Style Extraction Phase (reference .pptx analysis)

When the user provides a reference `.pptx` for style matching:

1. **Main agent extracts structured data**: unpack, read `ppt/theme/theme1.xml` (color scheme as hex, font scheme as family names)
2. **Generate slide images**: `python scripts/thumbnail.py <ref>.pptx ref-thumbnails --slides-dir unpacked-ref/slides/`
3. **Spawn `style-extractor` agent** with:
   - Individual slide image paths from `unpacked-ref/slides/`
   - Theme summary (color hex values + font names extracted from XML)
4. **Receive extraction report** — covers background strategy, layout vocabulary, shape language, color application, typography, motif, spacing, image treatment
5. **Main agent uses report** to seed the style plan discussion with the user

### Build Phase (PptxGenJS from scratch)

For decks with >12 slides:

1. **Divide slides** by sub-topic or section — each agent owns a coherent group
2. **Spawn `slide-builder` agents** — each gets:
   - Their assigned slides from the **content plan** (what to build)
   - The **style plan** or theme JSON (how it looks)
   - PptxGenJS API reference (`.claude/skills/ppt-studio/references/pptxgenjs-guide.md`)
   - Instruction: "Write a `buildSlides(pres, theme)` function"
   - If a plan was skipped, pass the defaults being used instead
3. **Assemble** — main agent creates wrapper script, inlines sub-agent functions, runs it
4. **Output** goes to `.ppt/decks/<name>/v<n>/<name>.pptx`

For decks with ≤12 slides: build directly in a single PptxGenJS script.

### Edit Phase (XML editing)

For improving existing decks with >8 slides to edit:

1. **Unpack** the `.pptx`: `python scripts/unpack.py <deck>.pptx unpacked/`
2. **Spawn `slide-editor` agents** — each gets:
   - Assigned slide XML file paths
   - The relevant edit plan(s) — content changes, style changes, or both
   - XML formatting rules (from `references/editing-guide.md`)
3. **Clean + pack** after all edits complete
4. **Output** to next version folder

### QA Phase (Review as sub-action)

Always use a sub-agent for visual QA:

1. **Convert** to images: `python scripts/thumbnail.py <deck>.pptx v<n>/slides/thumbnails --slides-dir v<n>/slides/`
2. **Spawn `qa-reviewer` agent** with:
   - Slide image paths
   - **Content plan** for completeness checks (expected content per slide)
   - **Style plan** for visual consistency checks (theme, layouts, motif)
   - The QA checklist (overlaps, overflow, contrast, spacing, alignment)
   - If a plan was skipped, use markitdown extraction or defaults instead
3. **Fix** reported issues
4. **Re-verify** affected slides (spawn another QA agent if needed)
5. **Save** findings to `.ppt/decks/<deck-name>/review-<n>.md`

## References

- Design guide: `.claude/skills/ppt-studio/references/design-guide.md`
- PptxGenJS API: `.claude/skills/ppt-studio/references/pptxgenjs-guide.md`
- Editing guide: `.claude/skills/ppt-studio/references/editing-guide.md`
- Sub-agent prompts: `.claude/skills/ppt-studio/references/subagent-prompts.md`
