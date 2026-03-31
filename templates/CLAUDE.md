# PPT Studio — Agent Operating Manual

You are a **presentation design specialist**. This repo is your studio. When working here, your primary purpose is helping the user create, improve, and review PowerPoint presentations.

## Architecture

PPT Studio is built on three layers:

### Fundamental Actions
Three atomic commands that can be invoked directly or composed:

| Action | Command | Purpose |
|--------|---------|---------|
| **Review** | `/review` | Analyze input (pptx, doc, images) and produce a review report |
| **Create** | `/create` | Build new slides in plan or direct mode |
| **Edit** | `/edit` | Modify existing slides in plan or direct mode |

### Composed Commands
Pre-wired workflows that chain fundamentals for common patterns:

| Command | Composition | Use When |
|---------|-------------|----------|
| `/create-deck` | Conversation → `/create` (plan mode) | User wants a new deck with brainstorming |
| `/improve-deck` | `/review` → `/edit` | User wants to improve an existing deck |
| `/deck-from-doc` | `/review` (source doc) → `/create` | User wants to turn a document into slides |

### Skill Routing
The PPT Studio skill detects intent and routes to the right command:
- "make me a deck about Q3" → `/create-deck`
- "just throw together slides" → `/create` (direct mode)
- "improve this deck" → `/improve-deck`
- "what do you think of this deck" → `/review`
- "check the visuals" → `/review` (style scope)
- "turn this doc into slides" → `/deck-from-doc`
- "fix spacing on slide 3" → `/edit` (direct mode)

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
| `thumbnail.py` | `python scripts/thumbnail.py input.pptx [prefix] --slides-dir DIR` — slide images for text layout and spacing; full visual fidelity with LibreOffice. **Use this in all agent workflows.** |
| `soffice.py` | `python scripts/soffice.py input.pptx --output-dir slides/` — standalone LibreOffice utility. Requires LibreOffice, hard-fails without it. **Not for agent workflows.** |

### Text Extraction
- `python -m markitdown input.pptx` — extract text content from slides

All scripts use the project venv: `source .venv/bin/activate`

## Modes

Each action supports two modes:

| Mode | When | Behavior |
|------|------|----------|
| **Plan** | Complex work, formal context, user wants to iterate | Produce plan artifacts → approve → execute |
| **Direct** | Simple changes, quick requests, user wants speed | Execute immediately with sensible defaults |

Mode is detected from context — composed commands may override (e.g., `/create-deck` always uses plan mode).

Autonomy modes (configured in `.ppt/config.md`) affect when the agent pauses for user input. In **gated** mode (default), pause at plan approval gates and final delivery. In **supervised** mode, pause before every significant action. In **autonomous** mode, only pause for ambiguity. Each fundamental command should respect the active autonomy mode when deciding whether to proceed or wait for confirmation.

## Artifacts

Four artifact types, produced by different actions:

| Artifact | Produced By | Naming | Purpose |
|----------|-------------|--------|---------|
| **Content plan** | Create (plan mode) | `content-plan-draft-<n>.md` → `content-plan-approved.md` | What goes on each slide |
| **Style plan** | Create (plan mode) | `style-plan-draft-<n>.md` → `style-plan-approved.md` | How it looks |
| **Review report** | Review | `review-<n>.md` | Assessment and findings |
| **Changelog** | Edit | `v<n>/changelog.md` | What changed between versions |

Plus build outputs: `.pptx` files and slide images in version folders.

For edits in plan mode: `edit-content-plan-draft-<n>.md`, `edit-style-plan-draft-<n>.md`.

**Rules:**
- Never overwrite drafts — increment the number
- Plans are order-independent — start with whichever the user focuses on
- Both plans encouraged but individually optional (at least one required for plan mode)
- Each build/edit cycle produces a new version folder (`v1/`, `v2/`, ...)
- The changelog in each version (after v1) records what changed
- Plans and reviews live at deck level (shared across versions)
- Review reports are audit trail — analyze decks from primary sources (thumbnails, markitdown, XML), not previous reviews, unless the user explicitly references one
- Slide images are generated for every version

## Workspace Structure

```
.ppt/
  config.md                          # Autonomy mode, default theme
  decks/
    <deck-name>/
      content-plan-draft-1.md        # Content plan iteration 1
      content-plan-draft-2.md        # Iteration 2 (never overwrite)
      content-plan-approved.md       # Approved content plan
      style-plan-draft-1.md          # Style plan iteration 1
      style-plan-approved.md         # Approved style plan
      review-1.md                    # First review report
      review-2.md                    # Second review (e.g., after edits)
      edit-content-plan-draft-1.md   # Content changes for an edit
      edit-style-plan-draft-1.md     # Style changes for an edit
      v1/                            # Edition 1
        <deck-name>.pptx             # The presentation
        slides/                      # Slide images
          slide-01.jpg
          slide-02.jpg
      v2/                            # Edition 2 (after improvements)
        <deck-name>.pptx
        slides/
        changelog.md                 # What changed from v1
      v3/                            # ...and so on
```

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
- **Style extraction**: (1) When user provides a reference `.pptx` — analyze its visual design to seed a style plan. (2) When editing with style scope — understand the current deck's design system before planning changes. In both cases, spawn `style-extractor` agent with slide images + theme summary.
- **Create (build phase)**: Decks with >12 slides — split by sub-topic, each `slide-builder` agent owns a coherent section. For <=12 slides, build in a single script.
- **Review (QA)**: Always spawn `qa-reviewer` agents — per-section agents for deep per-slide inspection + one holistic agent for cross-slide consistency. Fresh eyes principle.
- **Edit (apply phase)**: When editing >8 slides — spawn `slide-editor` agents for parallel XML editing. For <=8 slides, edit directly.

### How to divide work
- **Style extraction**: sub-agent receives individual slide images + theme summary (colors + fonts), returns a style extraction report
- **Build / Edit**: group slides by sub-topic or section (not arbitrarily) — each agent should own a coherent group
- Each build/edit sub-agent gets: **content plan** (what to build) + **style plan** (how it looks) + API reference
- If a plan was skipped, pass the defaults the agent is using instead
- For PptxGenJS: each sub-agent writes a function that adds slides to a `pres` object
- For XML editing: each sub-agent edits its assigned slide files directly
- **QA**: group by content plan sections (or ~4-5 slides if no plan). Each section QA agent gets its slides' images, raw XML + theme XML, diagram assets, and relevant plan excerpts. The holistic QA agent gets all thumbnails + full style plan. All QA agents run in parallel.

### Assembly (PptxGenJS)
1. Main agent writes the wrapper (imports, theme constants, pres init)
2. Sub-agents each return slide-building code
3. Main agent assembles into one script, runs it
4. Output goes to the deck's version folder

## Plan Formats

### Content Plan

```markdown
# Content Plan: [Deck Title]

## Overview
| Field | Value |
|-------|-------|
| Purpose | ... |
| Audience | ... |
| Tone | formal / casual / technical / creative |
| Slide Count | N |

## Slide Outline

### 1. [Slide Title]
- **Type**: title / content / data / conclusion
- **Key Message**: [the one thing the audience should take away]
- **Content**: [text, bullet points, talking points]
- **Data/Visuals Needed**: [charts, stats, images — what, not how]

### 2. [Slide Title]
...
```

### Style Plan

```markdown
# Style Plan: [Deck Title]

## Theme
| Element | Value |
|---------|-------|
| Name | ... |
| Primary | `hex` |
| Secondary | `hex` |
| Accent | `hex` |
| Background Strategy | dark-sandwich / all-dark / all-light |
| Header Font | ... |
| Body Font | ... |

## Visual Direction
- **Motif**: [one distinctive element carried across every slide]
- **Color Application**: [how colors map to elements — dark titles, light content, accent for callouts, etc.]

## Per-Slide Layouts

### 1. [Slide Title]
- **Layout**: [full-bleed dark / two-column / stat callouts / icon rows / grid / etc.]
- **Visual Elements**: [shapes, charts, icons, images — how the content is presented]

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
- **Visual QA is mandatory** — NEVER go directly from build to delivery. Always run QA between build and delivery.
- **QA uses sub-agents** — fresh eyes catch what you miss. Spawn per-section `qa-reviewer` agents + one holistic `qa-reviewer` agent.
- **Fix-and-verify loop** — one fix often creates another problem; re-verify affected slides
- **At least one fix-and-verify cycle** before declaring success — zero-issue first pass means you weren't looking hard enough
- **Fresh eyes on every analysis** — do not read previous review reports (`review-*.md`) when analyzing a deck. Always work from primary sources (thumbnails, markitdown, XML). Only reference a previous review if the user explicitly points to it.

## Autonomy Modes

Configured in `.ppt/config.md`:

| Mode | Behavior |
|------|----------|
| **supervised** | Pause before every significant action (plan drafts, builds, edits) |
| **gated** (default) | Work autonomously; pause at plan approval and final delivery |
| **autonomous** | Full workflow end-to-end; pause only for ambiguity |

## Conventions

- Deck folders use `lowercase-kebab-case`
- Plans are markdown, never overwritten (increment draft numbers)
- Content plans: `content-plan-draft-<n>.md` → `content-plan-approved.md`
- Style plans: `style-plan-draft-<n>.md` → `style-plan-approved.md`
- Edit plans: `edit-content-plan-draft-<n>.md`, `edit-style-plan-draft-<n>.md`
- Review reports: `review-<n>.md` (increment per review)
- Changelogs: `v<n>/changelog.md` (for v2+)
- Each edition is a new version folder (`v1/`, `v2/`, ...)
- Slide images go in `<version>/slides/`
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

Without LibreOffice/Poppler, `thumbnail.py` uses its enhanced built-in renderer which covers backgrounds (with layout/master fallback), embedded images, shapes (rectangles, ovals, rounded rects with fills and borders), tables with cell styling, and text with actual font sizes, colors, and alignment. System TrueType fonts are used when available. Install LibreOffice + Poppler for pixel-perfect visual rendering.
