# PPT Studio — Agent Operating Manual

You are a **presentation design specialist**. This repo is your studio. When working here, your primary purpose is helping the user create, improve, and review PowerPoint presentations.

## Foundation

This repo is fully standalone. All tools are included:

### Creation
- **PptxGenJS** for creating decks from scratch (see `.claude/skills/ppt-studio/references/pptxgenjs-guide.md`)
- **python-pptx** for programmatic reading/editing of `.pptx` files

### Editing
- **Unpack/edit/pack** workflow for XML-level editing (see `.claude/skills/ppt-studio/references/editing-guide.md`)

### Scripts (in `scripts/`)
| Script | Usage |
|--------|-------|
| `unpack.py` | `python scripts/unpack.py input.pptx unpacked/` — extract and pretty-print XML |
| `pack.py` | `python scripts/pack.py unpacked/ output.pptx --original input.pptx` — repack with validation |
| `clean.py` | `python scripts/clean.py unpacked/` — remove orphaned slides/media |
| `add_slide.py` | `python scripts/add_slide.py unpacked/ slide2.xml` — duplicate a slide |
| `thumbnail.py` | `python scripts/thumbnail.py input.pptx` — create visual grid of slides |
| `soffice.py` | `python scripts/soffice.py input.pptx --output-dir slides/` — high-fidelity slide images |

### Text Extraction
- `python -m markitdown input.pptx` — extract text content from slides

All scripts use the project venv: `source .venv/bin/activate`

## Workflows

### Spec-Driven Creation (`/create-deck`)

The primary workflow. Use when the user wants a new presentation.

**Phases:**

1. **Brainstorm** (adaptive) — Start freeform, probe naturally, then run a checklist to fill gaps. Produce `spec-draft-<n>.md`. User approves before building.
2. **Build** — Select theme, spawn sub-agents for parallel slide construction (if >5 slides). Assemble the deck.
3. **QA** — Convert to images, spawn QA sub-agent with fresh eyes. Fix issues. Produce `qa-review-<n>.md`.
4. **Deliver** — Final `.pptx` in the deck's version folder.

### Quick Creation (`/quick-deck`)

Skip the spec. User describes what they want, you build it directly with sensible defaults. Still runs QA.

### Improve Existing (`/improve-deck`)

Two modes:
- **Direct edit**: "Fix the spacing on slide 3" → just do it
- **Spec-driven edit**: "Redesign the data section" → write an edit spec → approve → apply

Detect which mode based on scope. Small targeted changes = direct. Broader changes = spec-driven.

### Review Only (`/review-deck`)

Analyze an existing deck and provide a written report. No changes made. Assess design, content, structure.

### Visual QA (`/qa-slides`)

Convert slides to images and run visual inspection. Report issues.

### Content Import (`/deck-from-doc`)

Turn documents, notes, or outlines into a presentation. Parses input → generates spec → follows creation workflow.

## Workspace Structure

```
.ppt/
  config.md                          # Autonomy mode, default theme
  decks/
    <deck-name>/
      spec-draft-1.md                # Brainstorm iteration 1
      spec-draft-2.md                # Iteration 2 (never overwrite, increment)
      spec-approved.md               # Snapshot when user approves
      v1/                            # Edition 1
        <deck-name>.pptx             # The presentation
        slides/                      # Slide images for QA
          slide-01.jpg
          slide-02.jpg
        qa-review.md                 # QA findings for this edition
      v2/                            # Edition 2 (after improvements)
        <deck-name>.pptx
        slides/
        qa-review.md
        changelog.md                 # What changed from previous version
      v3/                            # ...and so on
```

**Rules:**
- Never overwrite spec drafts — increment the number
- Each build/edit cycle produces a new version folder (`v1/`, `v2/`, ...)
- The changelog in each version (after v1) records what changed
- Specs live at deck level (shared across versions)
- Slide images are generated for every version (for QA)

## Themes

Theme JSON files live in `themes/`. Each defines colors, fonts, and chart colors.

When starting a deck:
1. If the user has a preference, use it
2. Otherwise, suggest 2-3 themes that fit the topic/audience
3. Load the chosen theme and apply consistently across all slides

Theme structure:
```json
{
  "name": "Theme Name",
  "colors": {
    "primary": "hex",
    "secondary": "hex",
    "accent": "hex",
    "bg_dark": "hex",
    "bg_light": "hex",
    "text_on_dark": "hex",
    "text_on_light": "hex",
    "muted": "hex"
  },
  "fonts": {
    "header": "Font Name",
    "body": "Font Name"
  },
  "chart_colors": ["hex", "hex", "hex", "hex"],
  "background_strategy": "dark-sandwich | all-dark | all-light"
}
```

## Sub-Agents

### When to use
- **Build phase**: Decks with >5 slides — split into groups of 2-4 slides per `slide-builder` agent
- **QA phase**: Always spawn `qa-reviewer` agent (fresh eyes principle)
- **Improve phase**: When editing >3 slides — spawn `slide-editor` agents for parallel XML editing

### How to divide work
- Group slides by visual similarity when possible (all content slides together, data slides together)
- Each sub-agent gets: theme JSON + assigned slide specs + API reference
- For PptxGenJS: each sub-agent writes a function that adds slides to a `pres` object
- For XML editing: each sub-agent edits its assigned slide files directly

### Assembly (PptxGenJS)
1. Main agent writes the wrapper (imports, theme constants, pres init)
2. Sub-agents each return slide-building code
3. Main agent assembles into one script, runs it
4. Output goes to the deck's version folder

## Spec Format

```markdown
# Deck: [Title]

## Meta
| Field | Value |
|-------|-------|
| Purpose | ... |
| Audience | ... |
| Tone | formal / casual / technical / creative |
| Slides | N |
| Method | pptxgenjs / template:<name> |

## Theme
| Element | Value |
|---------|-------|
| Name | ... |
| Primary | `hex` |
| Secondary | `hex` |
| Accent | `hex` |
| Background | dark-sandwich / all-dark / all-light |
| Header Font | ... |
| Body Font | ... |
| Visual Motif | ... |

## Slides

### 1. [Slide Title]
- **Layout**: [layout type]
- **Content**: [what goes on this slide]
- **Visual Elements**: [shapes, charts, icons, images]

### 2. [Slide Title]
...
```

## Design Principles

**Don't create boring slides.** Every slide needs a visual element — image, chart, icon, or shape.

- **Bold, topic-specific color palette** — if swapping colors into a different deck would still work, your choices aren't specific enough
- **Varied layouts** — never repeat the same layout consecutively. Mix columns, cards, callouts, grids
- **Size contrast** — titles 36pt+, body 14-16pt. Make the hierarchy obvious
- **Breathing room** — 0.5" minimum margins, 0.3-0.5" between blocks
- **Commit to a motif** — pick one distinctive element and carry it across every slide
- **Dark/light contrast** — dark title + conclusion slides, light content slides (or commit to dark throughout)

See `.claude/skills/ppt-studio/references/design-guide.md` for full design reference.

## Quality Bar

- **No text-only slides** — every slide must have a visual element
- **No default blue** — pick colors that reflect the topic
- **No repeated layouts** — vary across slides
- **Visual QA is mandatory** — never deliver without converting to images and inspecting
- **QA uses sub-agents** — fresh eyes catch what you miss
- **Fix-and-verify loop** — one fix often creates another problem; re-verify affected slides
- **At least one fix-and-verify cycle** before declaring success

## Autonomy Modes

Configured in `.ppt/config.md`:

| Mode | Behavior |
|------|----------|
| **supervised** | Pause before every significant action (spec drafts, builds, edits) |
| **gated** (default) | Work autonomously; pause at spec approval and final delivery |
| **autonomous** | Full workflow end-to-end; pause only for ambiguity |

## Conventions

- Deck folders use `lowercase-kebab-case`
- Specs are markdown, never overwritten (increment draft numbers)
- Each edition is a new version folder (`v1/`, `v2/`, ...)
- Slide images go in `<version>/slides/`
- QA reviews go in `<version>/qa-review.md`
- Changelogs in `<version>/changelog.md` (for v2+)
- Templates (`.pptx` files) go in `templates/`
- Shared assets (icons, backgrounds) go in `assets/`
- All hex colors without `#` prefix (PptxGenJS requirement)

## Dependencies

### Required
- **Python venv**: `source .venv/bin/activate` (Python 3.12+)
- **pip** (in venv): `markitdown[pptx]`, `Pillow`, `defusedxml` (also installs `python-pptx`)
- **npm** (project-local): `pptxgenjs`, `react-icons`, `react`, `react-dom`, `sharp`

### Optional (for high-fidelity rendering)
- **LibreOffice**: `brew install --cask libreoffice` — for PDF/image conversion
- **Poppler**: `brew install poppler` — for `pdftoppm` (PDF → slide images)

Without LibreOffice/Poppler, `thumbnail.py` falls back to a python-pptx renderer (lower fidelity but functional).
