#!/usr/bin/env bash
set -eu

# ─── PPT Studio Bootstrap ──────────────────────────────────────────────
# Stamps a target directory as a PPT Studio workspace for Claude Code.
#
# Usage:
#   ./bootstrap/init-ppt-studio.sh /path/to/target
#   ./bootstrap/init-ppt-studio.sh /path/to/target --update
#
# --update: Refresh system files (scripts, commands, skills, agents,
#           hooks, themes, CLAUDE.md) without touching user files
#           (config.md, .ppt/decks/, settings.local.json).
# ────────────────────────────────────────────────────────────────────────

TOOLKIT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATES="$TOOLKIT_DIR/templates"

# ─── Help ───────────────────────────────────────────────────────────────

if [ "${1:-}" = "-h" ] || [ "${1:-}" = "--help" ]; then
  cat <<'HELP'
PPT Studio Bootstrap

Usage:
  init-ppt-studio.sh <target-directory>
  init-ppt-studio.sh <target-directory> --update

Arguments:
  <target-directory>   Directory to set up as a PPT Studio workspace.
  --update             Refresh system files only (preserves user files).

What it does:
  1. Copies Claude Code configuration (.claude/commands, skills, agents, hooks)
  2. Copies utility scripts (scripts/)
  3. Copies theme files (themes/)
  4. Copies CLAUDE.md (agent operating manual)
  5. Creates workspace directories (.ppt/decks, .ppt/logs, templates, assets, output)
  6. Creates Python venv and installs pip dependencies
  7. Installs npm dependencies (pptxgenjs, react-icons, sharp)
  8. Appends PPT Studio entries to .gitignore
  9. Checks for optional system dependencies (LibreOffice, Poppler)

System files (refreshed with --update):
  CLAUDE.md, .claude/commands/*, .claude/skills/*, .claude/agents/*,
  .claude/hooks/*, .claude/settings.json, scripts/*, themes/*,
  package.json, requirements.txt

User files (never overwritten):
  .ppt/config.md, .claude/settings.local.json, .ppt/decks/*
  (plans, reviews, builds), templates/*, assets/*
HELP
  exit 0
fi

# ─── Parse arguments ────────────────────────────────────────────────────

TARGET="${1:-}"
UPDATE_MODE=false

if [ -z "$TARGET" ]; then
  echo "Error: target directory required." >&2
  echo "Usage: init-ppt-studio.sh <target-directory> [--update]" >&2
  exit 1
fi

TARGET="$(cd "$TARGET" 2>/dev/null && pwd || echo "$TARGET")"

if [ "${2:-}" = "--update" ]; then
  UPDATE_MODE=true
fi

if [ "$TARGET" = "$TOOLKIT_DIR" ]; then
  echo "Error: cannot bootstrap into the toolkit repo itself." >&2
  exit 1
fi

if [ ! -d "$TARGET" ]; then
  echo "Error: target directory does not exist: $TARGET" >&2
  exit 1
fi

# ─── Validate templates ────────────────────────────────────────────────

REQUIRED_FILES=(
  "CLAUDE.md"
  "settings.json"
  "config.md"
  "package.json"
  "requirements.txt"
  "gitignore"
  "commands/review.md"
  "commands/create.md"
  "commands/edit.md"
  "commands/create-deck.md"
  "commands/improve-deck.md"
  "commands/deck-from-doc.md"
  "skills/ppt-studio/SKILL.md"
  "agents/slide-builder.md"
  "agents/slide-editor.md"
  "agents/qa-reviewer.md"
  "hooks/setup.py"
  "hooks/session_start.py"
  "scripts/unpack.py"
  "scripts/pack.py"
  "scripts/clean.py"
  "scripts/add_slide.py"
  "scripts/thumbnail.py"
  "scripts/soffice.py"
)

missing=()
for f in "${REQUIRED_FILES[@]}"; do
  if [ ! -f "$TEMPLATES/$f" ]; then
    missing+=("$f")
  fi
done

if [ ${#missing[@]} -gt 0 ]; then
  echo "Error: missing template files:" >&2
  for f in "${missing[@]}"; do
    echo "  templates/$f" >&2
  done
  exit 1
fi

# ─── Copy functions ────────────────────────────────────────────────────

copy_if_missing() {
  local src="$1" dst="$2"
  if [ -e "$dst" ]; then
    echo "  skip (exists): $dst"
    return
  fi
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
  echo "  create: $dst"
}

copy_and_overwrite() {
  local src="$1" dst="$2"
  if [ -e "$dst" ] && cmp -s "$src" "$dst"; then
    echo "  skip (unchanged): $dst"
    return
  fi
  local existed=false
  [ -e "$dst" ] && existed=true
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
  if $existed; then
    echo "  update: $dst"
  else
    echo "  create: $dst"
  fi
}

# Select copy function based on mode
if $UPDATE_MODE; then
  copy_system=copy_and_overwrite
else
  copy_system=copy_if_missing
fi

# ─── Create directories ────────────────────────────────────────────────

echo "Setting up PPT Studio in: $TARGET"
echo ""

mkdir -p "$TARGET/.claude/commands"
mkdir -p "$TARGET/.claude/skills/ppt-studio/references"
mkdir -p "$TARGET/.claude/agents"
mkdir -p "$TARGET/.claude/hooks"
mkdir -p "$TARGET/.ppt/decks"
mkdir -p "$TARGET/.ppt/logs"
mkdir -p "$TARGET/scripts"
mkdir -p "$TARGET/themes"
mkdir -p "$TARGET/templates"
mkdir -p "$TARGET/assets"
mkdir -p "$TARGET/output"

# ─── Copy system files ──────────────────────────────────────────────────

echo "System files:"

# CLAUDE.md
$copy_system "$TEMPLATES/CLAUDE.md" "$TARGET/CLAUDE.md"

# Settings
$copy_system "$TEMPLATES/settings.json" "$TARGET/.claude/settings.json"

# Commands
for f in "$TEMPLATES/commands/"*.md; do
  name="$(basename "$f")"
  $copy_system "$f" "$TARGET/.claude/commands/$name"
done

# Skills
$copy_system "$TEMPLATES/skills/ppt-studio/SKILL.md" "$TARGET/.claude/skills/ppt-studio/SKILL.md"
for f in "$TEMPLATES/skills/ppt-studio/references/"*.md; do
  name="$(basename "$f")"
  $copy_system "$f" "$TARGET/.claude/skills/ppt-studio/references/$name"
done

# Agents
for f in "$TEMPLATES/agents/"*.md; do
  name="$(basename "$f")"
  $copy_system "$f" "$TARGET/.claude/agents/$name"
done

# Hooks
for f in "$TEMPLATES/hooks/"*.py; do
  name="$(basename "$f")"
  $copy_system "$f" "$TARGET/.claude/hooks/$name"
done

# Scripts
for f in "$TEMPLATES/scripts/"*.py; do
  name="$(basename "$f")"
  $copy_system "$f" "$TARGET/scripts/$name"
done

# Themes
for f in "$TEMPLATES/themes/"*.json; do
  name="$(basename "$f")"
  $copy_system "$f" "$TARGET/themes/$name"
done

# Package files
$copy_system "$TEMPLATES/package.json" "$TARGET/package.json"
$copy_system "$TEMPLATES/requirements.txt" "$TARGET/requirements.txt"

# ─── Copy user files (never overwrite) ──────────────────────────────────

echo ""
echo "User files:"

copy_if_missing "$TEMPLATES/config.md" "$TARGET/.ppt/config.md"

# ─── Gitignore ──────────────────────────────────────────────────────────

echo ""
echo "Gitignore:"

GITIGNORE_MARKER="# PPT Studio"
if [ -f "$TARGET/.gitignore" ]; then
  if grep -qF "$GITIGNORE_MARKER" "$TARGET/.gitignore"; then
    if $UPDATE_MODE; then
      # Replace existing PPT Studio section
      # Remove from marker to end, then append fresh
      sed -i.bak "/$GITIGNORE_MARKER/,\$d" "$TARGET/.gitignore"
      rm -f "$TARGET/.gitignore.bak"
      cat "$TEMPLATES/gitignore" >> "$TARGET/.gitignore"
      echo "  update: .gitignore (PPT Studio section refreshed)"
    else
      echo "  skip (exists): .gitignore already has PPT Studio entries"
    fi
  else
    echo "" >> "$TARGET/.gitignore"
    cat "$TEMPLATES/gitignore" >> "$TARGET/.gitignore"
    echo "  append: .gitignore (added PPT Studio entries)"
  fi
else
  cp "$TEMPLATES/gitignore" "$TARGET/.gitignore"
  echo "  create: .gitignore"
fi

# ─── Gitkeep for empty directories ─────────────────────────────────────

for d in "$TARGET/templates" "$TARGET/assets" "$TARGET/output" "$TARGET/.ppt/decks" "$TARGET/.ppt/logs"; do
  touch "$d/.gitkeep" 2>/dev/null || true
done

# ─── Git init if needed ────────────────────────────────────────────────

if [ ! -d "$TARGET/.git" ]; then
  echo ""
  echo "Initializing git repository..."
  (cd "$TARGET" && git init -q)
fi

# ─── Python venv + dependencies ─────────────────────────────────────────

echo ""
echo "Python environment:"

PYTHON=""
for candidate in python3.13 python3.12 python3; do
  if command -v "$candidate" >/dev/null 2>&1; then
    ver="$("$candidate" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')"
    major="${ver%%.*}"
    minor="${ver#*.}"
    if [ "$major" -ge 3 ] && [ "$minor" -ge 12 ]; then
      PYTHON="$candidate"
      break
    fi
  fi
done

if [ -z "$PYTHON" ]; then
  echo "  Warning: Python 3.12+ not found. Please install it and create a venv manually:" >&2
  echo "    python3.12 -m venv $TARGET/.venv" >&2
  echo "    source $TARGET/.venv/bin/activate && pip install -r $TARGET/requirements.txt" >&2
else
  if [ ! -d "$TARGET/.venv" ]; then
    echo "  Creating venv with $PYTHON..."
    "$PYTHON" -m venv "$TARGET/.venv"
    echo "  Installing pip dependencies..."
    "$TARGET/.venv/bin/pip" install -q -r "$TARGET/requirements.txt"
    echo "  Python venv ready: $TARGET/.venv"
  else
    if $UPDATE_MODE; then
      echo "  Updating pip dependencies..."
      "$TARGET/.venv/bin/pip" install -q -r "$TARGET/requirements.txt"
    else
      echo "  skip (exists): .venv"
    fi
  fi
fi

# ─── npm dependencies ──────────────────────────────────────────────────

echo ""
echo "Node.js dependencies:"

if command -v npm >/dev/null 2>&1; then
  if [ ! -d "$TARGET/node_modules" ]; then
    echo "  Installing npm dependencies..."
    (cd "$TARGET" && npm install --silent 2>&1 | tail -1)
    echo "  npm packages ready"
  else
    if $UPDATE_MODE; then
      echo "  Updating npm dependencies..."
      (cd "$TARGET" && npm install --silent 2>&1 | tail -1)
    else
      echo "  skip (exists): node_modules"
    fi
  fi
else
  echo "  Warning: npm not found. Please install Node.js and run:" >&2
  echo "    cd $TARGET && npm install" >&2
fi

# ─── Check optional system dependencies ────────────────────────────────

echo ""
echo "System dependencies:"

soffice_found=false
if [ -x "/Applications/LibreOffice.app/Contents/MacOS/soffice" ] || command -v soffice >/dev/null 2>&1; then
  echo "  LibreOffice: found"
  soffice_found=true
else
  echo "  LibreOffice: NOT FOUND (optional — needed for visual QA)"
  echo "    Install: brew install --cask libreoffice"
fi

if command -v pdftoppm >/dev/null 2>&1; then
  echo "  Poppler (pdftoppm): found"
else
  echo "  Poppler (pdftoppm): NOT FOUND (optional — needed for visual QA)"
  echo "    Install: brew install poppler"
fi

# ─── Done ───────────────────────────────────────────────────────────────

echo ""
echo "════════════════════════════════════════════════════════════════"

if $UPDATE_MODE; then
  echo "PPT Studio updated in: $TARGET"
  echo ""
  echo "System files refreshed. User files untouched."
else
  echo "PPT Studio ready in: $TARGET"
  echo ""
  echo "Next steps:"
  echo "  1. cd $TARGET"
  echo "  2. Open Claude Code in this directory"
  echo "  3. Try these commands:"
  echo "     /create-deck    — brainstorm + plan-driven creation"
  echo "     /improve-deck   — review + edit an existing deck"
  echo "     /deck-from-doc  — turn a document into slides"
  echo "     /review          — analyze a deck or document"
  echo "     /create          — build slides (plan or direct mode)"
  echo "     /edit            — modify existing slides"
fi

if ! $soffice_found; then
  echo ""
  echo "Note: Install LibreOffice + Poppler for high-fidelity slide"
  echo "rendering and visual QA. Without them, thumbnail.py uses"
  echo "a basic fallback renderer."
fi

echo "════════════════════════════════════════════════════════════════"
