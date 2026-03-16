# PPT Studio

A bootstrap toolkit that turns any directory into a Claude Code-powered presentation creation workspace.

## Quick Start

```bash
./bootstrap/init-ppt-studio.sh /path/to/your/project
```

Then open Claude Code in the target directory and use:

| Command | Purpose |
|---------|---------|
| `/create-deck` | Spec-driven presentation creation (brainstorm → spec → build → QA) |
| `/quick-deck` | Fast creation without a spec |
| `/improve-deck` | Edit or redesign an existing `.pptx` |
| `/review-deck` | Get a feedback report on a deck (no changes) |
| `/qa-slides` | Visual quality inspection |
| `/deck-from-doc` | Turn a document or notes into slides |

## What Gets Installed

The bootstrap script stamps the target directory with:

- **CLAUDE.md** — Agent operating manual (primes Claude as a PPT specialist)
- **6 slash commands** — Workflows for creating, editing, and reviewing decks
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
./bootstrap/init-ppt-studio.sh /path/to/your/project --update
```

This updates scripts, commands, skills, agents, hooks, and themes. Your specs, decks, config, and custom templates are preserved.

## Requirements

- **Python 3.12+**
- **Node.js / npm**
- **LibreOffice** (optional) — `brew install --cask libreoffice` — for high-fidelity slide rendering
- **Poppler** (optional) — `brew install poppler` — for PDF-to-image conversion

Without LibreOffice/Poppler, thumbnail generation falls back to a basic python-pptx renderer.

## Target Repo Structure

After bootstrapping, the target directory contains:

```
your-project/
├── CLAUDE.md                        # Agent operating manual
├── .claude/
│   ├── commands/                    # 6 slash commands
│   ├── skills/ppt-studio/          # Skill + reference docs
│   ├── agents/                      # Sub-agent definitions
│   ├── hooks/                       # Session hooks
│   └── settings.json                # Hook configuration
├── .ppt/
│   ├── config.md                    # Autonomy mode, defaults
│   ├── decks/                       # Per-deck artifacts
│   │   └── <deck-name>/
│   │       ├── spec-draft-*.md      # Brainstorm iterations
│   │       ├── spec-approved.md     # Approved spec
│   │       ├── v1/                  # Edition 1
│   │       │   ├── deck.pptx
│   │       │   ├── slides/          # QA images
│   │       │   └── qa-review.md
│   │       └── v2/                  # Edition 2 (with changelog)
│   └── logs/                        # Hook logs (gitignored)
├── scripts/                         # Utility scripts
├── themes/                          # Theme JSON files
├── templates/                       # Your .pptx templates
├── assets/                          # Shared icons, images
└── output/                          # Generated presentations
```

## Workflows

### Spec-Driven Creation

1. User describes what they want
2. Claude brainstorms (adaptive: freeform → checklist)
3. Writes a spec → user reviews and approves
4. Sub-agents build slides in parallel (for decks >5 slides)
5. QA sub-agent inspects with fresh eyes
6. Fix-and-verify loop until clean
7. Deliver final `.pptx`

### Improving Existing Decks

- **Direct mode**: Small changes applied immediately
- **Spec-driven mode**: Broader redesigns go through an edit spec → approve → apply cycle
- Each improvement creates a new version (`v2/`, `v3/`) with a changelog

### Visual QA

Every deck goes through visual QA before delivery:
1. Convert slides to images (soffice → PDF → pdftoppm, or python-pptx fallback)
2. Sub-agent inspects each slide for overlaps, contrast, spacing, alignment
3. Issues fixed and re-verified
