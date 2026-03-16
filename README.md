# PPT Studio

A bootstrap toolkit that turns any directory into a Claude Code-powered presentation creation workspace.

## Quick Start

```bash
python bootstrap/init-ppt-studio.py /path/to/your/project
```

Then open Claude Code in the target directory and use:

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

- **CLAUDE.md** — Agent operating manual (primes Claude as a PPT specialist)
- **6 slash commands** — 3 fundamental actions + 3 composed workflows
- **3 agent definitions** — Sub-agents for parallel slide building, editing, and QA
- **1 skill** — Intent routing (auto-triggers on PPT-related requests)
- **2 hooks** — Session context injection (active decks, current phase)
- **6 utility scripts** — Unpack, pack, clean, add slide, thumbnails, PDF conversion
- **6 themes** — Curated color/font palettes
- **Python venv** — With markitdown, python-pptx, Pillow, defusedxml
- **npm packages** — pptxgenjs, react-icons, sharp

## Updating

To refresh system files without touching your work:

```bash
python bootstrap/init-ppt-studio.py /path/to/your/project --update
```

This updates scripts, commands, skills, agents, hooks, and themes. Your plans, decks, config, and custom templates are preserved.

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
3. Plans approved → sub-agents build slides in parallel (for decks >5 slides)
4. QA sub-agent inspects with fresh eyes
5. Fix-and-verify loop until clean
6. Deliver final `.pptx`

### Improving Existing Decks

- **Direct mode**: Small changes applied immediately
- **Plan mode**: Broader redesigns go through edit plan(s) → approve → apply cycle
- Each improvement creates a new version (`v2/`, `v3/`) with a changelog

### Visual QA

Every deck goes through visual QA before delivery:
1. Convert slides to images (soffice → PDF → pdftoppm, or python-pptx fallback)
2. Sub-agent inspects each slide for overlaps, contrast, spacing, alignment
3. Issues fixed and re-verified
