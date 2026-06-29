# PPT Studio

A bootstrap toolkit that turns any directory into a presentation creation workspace for **Claude Code** or **OpenCode**.

For a conceptual walkthrough of what the agent does and how it works — plan-then-build, sub-agents, visual QA, version trail — see [`core/docs/product-overview.md`](core/docs/product-overview.md). It's also stamped into every target repo at `docs/product-overview.md`.

## Quick Start

```bash
# Claude Code (default)
python3.12 bootstrap/init-ppt-studio.py /path/to/your/project

# OpenCode
python3.12 bootstrap/init-ppt-studio.py /path/to/your/project --runtime opencode
```

Then open the chosen runtime in the target directory and use:

### Fundamental Commands

| Command | Purpose |
|---------|---------|
| `/review` | Analyze a deck, document, or slide images — produce a review report |
| `/create` | Build new slides (plan mode for iterating, direct mode for speed) |
| `/edit` | Modify existing slides (plan mode for broad changes, direct for quick fixes) |

### Composed Commands

| Command | Composition | Purpose |
|---------|-------------|---------|
| `/create-deck` | Conversation → `/create` | Full brainstorm + plan-driven creation |
| `/improve-deck` | `/review` → `/edit` | Review a deck then apply improvements |
| `/deck-from-doc` | `/review` → `/create` | Turn a document into slides |

Or just describe what you want — the skill routes your intent to the right command.

## What Gets Installed

The bootstrap script stamps the target directory with:

- **Instruction doc** — `CLAUDE.md` (Claude Code) or `AGENTS.md` (OpenCode); the agent operating manual
- **6 slash commands** — 3 fundamental actions + 3 composed workflows
- **4 sub-agents** — style extraction, slide building, editing, and QA
- **1 skill** — Intent routing (auto-triggers on PPT-related requests)
- **6 utility scripts** — Unpack, pack, clean, add slide, thumbnails, PDF conversion
- **6 themes** — Curated color/font palettes
- **Product overview doc** — Conceptual walkthrough at `docs/product-overview.md`
- **Python venv** — With markitdown, python-pptx, Pillow, defusedxml
- **npm packages** — pptxgenjs, react-icons, sharp

Runtime-specific wiring:

- **Claude Code:** `.claude/{commands,skills,agents,hooks}`, `.claude/settings.json`, and 2 session hooks (active-deck/phase context injection).
- **OpenCode:** `.opencode/{command,agent,skills}`, `opencode.json`, and a `/status` command (OpenCode has no session-start hook, so deck/phase status is explicit).

## Updating

To refresh system files without touching your work:

```bash
python3.12 bootstrap/init-ppt-studio.py /path/to/your/project --update
# add --runtime opencode for an OpenCode workspace
```

This updates the instruction doc, commands, skills, agents, scripts, themes, and (Claude) hooks. Your plans, decks, config, custom templates, and `opencode.json` are preserved.

## For Maintainers — the render pipeline

System files are authored once in `core/` (runtime-neutral, with `{{TOKENS}}`) plus per-runtime mechanics in `adapters/{claude,opencode}/`. A generator renders both into checked-in trees:

```bash
python3.12 scripts/render_templates.py          # rebuild generated/{claude,opencode}/
python3.12 scripts/render_templates.py --check  # verify generated/ is fresh (CI gate)
```

The installer copies from `generated/<runtime>/`; it never renders. After editing `core/` or `adapters/`, re-render and commit `generated/`. The Claude render is the identity baseline, so existing Claude output never drifts.

## Requirements

### Required

- **Python 3.12+**
- **Node.js / npm**

### Optional (higher-fidelity QA rendering)

LibreOffice and Poppler produce higher-fidelity slide images for visual QA, but **everything works without them** — the built-in python-pptx renderer handles QA inspection fine. These require admin/system-level installation, so skip them if your environment is locked down.

| Tool | macOS | Linux / WSL | Windows |
|------|-------|-------------|---------|
| **LibreOffice** | `brew install --cask libreoffice` | `sudo apt install libreoffice` | `choco install libreoffice-fresh` or [libreoffice.org](https://www.libreoffice.org/) |
| **Poppler** | `brew install poppler` | `sudo apt install poppler-utils` | `choco install poppler` or [GitHub release](https://github.com/oschwartz10612/poppler-windows) |

## Target Repo Structure

After bootstrapping, the target directory contains:

```
your-project/
├── CLAUDE.md                        # Agent operating manual
├── .claude/
│   ├── commands/                    # 6 slash commands (3 fundamental + 3 composed)
│   ├── skills/ppt-studio/          # Skill + reference docs
│   ├── agents/                      # Sub-agent definitions
│   ├── hooks/                       # Session hooks
│   └── settings.json                # Hook configuration
├── .ppt/
│   ├── config.md                    # Autonomy mode, defaults
│   ├── decks/                       # Per-deck artifacts
│   │   └── <deck-name>/
│   │       ├── content-plan-*.md    # Content plan drafts + approved
│   │       ├── style-plan-*.md      # Style plan drafts + approved
│   │       ├── review-*.md          # Review reports
│   │       ├── v1/                  # Edition 1
│   │       │   ├── deck.pptx
│   │       │   └── slides/          # Slide images
│   │       └── v2/                  # Edition 2 (with changelog)
│   └── logs/                        # Hook logs (gitignored)
├── scripts/                         # Utility scripts
├── themes/                          # Theme JSON files
├── templates/                       # Your .pptx templates
├── assets/                          # Shared icons, images
└── output/                          # Generated presentations
```

## Architecture

Three layers:

1. **Fundamental actions** (`/review`, `/create`, `/edit`) — atomic building blocks
2. **Composed commands** (`/create-deck`, `/improve-deck`, `/deck-from-doc`) — pre-wired workflows
3. **Skill routing** — detects user intent and picks the right command

Each action supports **plan mode** (iterate on content/style plans before building) or **direct mode** (just do it). Four artifact types track decisions: content plans, style plans, review reports, and changelogs.

## Workflows

### Creating a Deck

1. User describes what they want
2. Agent and user collaboratively build a content plan and/or style plan
3. Plans approved → sub-agents build slides in parallel (for decks >12 slides)
4. QA sub-agent inspects with fresh eyes
5. Fix-and-verify loop until clean
6. Deliver final `.pptx`

### Improving Existing Decks

- **Direct mode**: Small changes applied immediately
- **Plan mode**: Broader redesigns go through edit plan(s) → approve → apply cycle
- Each improvement creates a new version (`v2/`, `v3/`) with a changelog

### Visual QA

Every deck goes through visual QA before delivery:
1. Convert slides to images (thumbnail.py — uses soffice if available, python-pptx fallback)
2. Sub-agent inspects each slide for overlaps, contrast, spacing, alignment
3. Issues fixed and re-verified
