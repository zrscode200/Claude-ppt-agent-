#!/usr/bin/env python3
"""PPT Studio Bootstrap — Cross-platform setup script.

Stamps a target directory as a PPT Studio workspace for Claude Code.

Usage:
    python bootstrap/init-ppt-studio.py /path/to/target
    python bootstrap/init-ppt-studio.py /path/to/target --update

--update: Refresh system files (scripts, commands, skills, agents,
          hooks, themes, CLAUDE.md) without touching user files
          (config.md, .ppt/decks/, settings.local.json).
"""

import argparse
import filecmp
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

TOOLKIT_DIR = Path(__file__).resolve().parent.parent
TEMPLATES = TOOLKIT_DIR / "templates"

REQUIRED_FILES = [
    "CLAUDE.md",
    "settings.json",
    "config.md",
    "package.json",
    "requirements.txt",
    "gitignore",
    "commands/review.md",
    "commands/create.md",
    "commands/edit.md",
    "commands/create-deck.md",
    "commands/improve-deck.md",
    "commands/deck-from-doc.md",
    "skills/ppt-studio/SKILL.md",
    "agents/slide-builder.md",
    "agents/slide-editor.md",
    "agents/qa-reviewer.md",
    "hooks/setup.py",
    "hooks/session_start.py",
    "scripts/unpack.py",
    "scripts/pack.py",
    "scripts/clean.py",
    "scripts/add_slide.py",
    "scripts/thumbnail.py",
    "scripts/soffice.py",
]

SYSTEM = platform.system()  # 'Darwin', 'Linux', 'Windows'

DIRECTORIES = [
    ".claude/commands",
    ".claude/skills/ppt-studio/references",
    ".claude/agents",
    ".claude/hooks",
    ".ppt/decks",
    ".ppt/logs",
    "scripts",
    "themes",
    "templates",
    "assets",
    "output",
]

GITKEEP_DIRS = ["templates", "assets", "output", ".ppt/decks", ".ppt/logs"]

GITIGNORE_MARKER = "# PPT Studio"


# ─── Platform helpers ────────────────────────────────────────────────


def find_soffice() -> str | None:
    """Find LibreOffice soffice binary for the current platform."""
    if SYSTEM == "Darwin":
        candidates = [
            "/Applications/LibreOffice.app/Contents/MacOS/soffice",
            os.path.expanduser("~/Applications/LibreOffice.app/Contents/MacOS/soffice"),
        ]
    elif SYSTEM == "Windows":
        candidates = [
            r"C:\Program Files\LibreOffice\program\soffice.exe",
            r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
        ]
    else:  # Linux / WSL
        candidates = [
            "/usr/bin/soffice",
            "/usr/lib/libreoffice/program/soffice",
        ]

    for path in candidates:
        if os.path.isfile(path):
            return path

    if shutil.which("soffice"):
        return "soffice"

    return None


def install_hint(tool: str) -> str:
    """Return platform-appropriate install instructions."""
    hints = {
        "libreoffice": {
            "Darwin": "brew install --cask libreoffice",
            "Linux": "sudo apt install libreoffice  # or: sudo dnf install libreoffice",
            "Windows": "choco install libreoffice-fresh  # or download from libreoffice.org",
        },
        "poppler": {
            "Darwin": "brew install poppler",
            "Linux": "sudo apt install poppler-utils  # or: sudo dnf install poppler-utils",
            "Windows": "choco install poppler  # or download from github.com/oschwartz10612/poppler-windows",
        },
        "python": {
            "Darwin": "brew install python@3.12",
            "Linux": "sudo apt install python3.12 python3.12-venv  # or: sudo dnf install python3.12",
            "Windows": "Download from python.org or: choco install python --version=3.12",
        },
        "npm": {
            "Darwin": "brew install node",
            "Linux": "sudo apt install nodejs npm  # or use nvm: nvm install --lts",
            "Windows": "Download from nodejs.org or: choco install nodejs",
        },
    }
    return hints.get(tool, {}).get(SYSTEM, f"Install {tool} for your platform")


def venv_python(target: Path) -> Path:
    """Return the path to the venv Python binary."""
    if SYSTEM == "Windows":
        return target / ".venv" / "Scripts" / "python.exe"
    return target / ".venv" / "bin" / "python"


def venv_pip(target: Path) -> Path:
    """Return the path to the venv pip binary."""
    if SYSTEM == "Windows":
        return target / ".venv" / "Scripts" / "pip.exe"
    return target / ".venv" / "bin" / "pip"


# ─── Copy helpers ────────────────────────────────────────────────────


def copy_if_missing(src: Path, dst: Path) -> None:
    """Copy file only if destination doesn't exist."""
    if dst.exists():
        print(f"  skip (exists): {dst}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"  create: {dst}")


def copy_and_overwrite(src: Path, dst: Path) -> None:
    """Copy file, overwriting if changed."""
    if dst.exists() and filecmp.cmp(src, dst, shallow=False):
        print(f"  skip (unchanged): {dst}")
        return
    existed = dst.exists()
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    print(f"  {'update' if existed else 'create'}: {dst}")


# ─── Setup steps ─────────────────────────────────────────────────────


def validate_templates() -> None:
    """Ensure all required template files exist."""
    missing = [f for f in REQUIRED_FILES if not (TEMPLATES / f).exists()]
    if missing:
        print("Error: missing template files:", file=sys.stderr)
        for f in missing:
            print(f"  templates/{f}", file=sys.stderr)
        sys.exit(1)


def create_directories(target: Path) -> None:
    """Create workspace directory structure."""
    for d in DIRECTORIES:
        (target / d).mkdir(parents=True, exist_ok=True)


def copy_system_files(target: Path, copy_fn) -> None:
    """Copy all system files using the given copy function."""
    print("System files:")

    # CLAUDE.md
    copy_fn(TEMPLATES / "CLAUDE.md", target / "CLAUDE.md")

    # Settings
    copy_fn(TEMPLATES / "settings.json", target / ".claude" / "settings.json")

    # Commands
    for f in sorted((TEMPLATES / "commands").glob("*.md")):
        copy_fn(f, target / ".claude" / "commands" / f.name)

    # Skills
    copy_fn(
        TEMPLATES / "skills" / "ppt-studio" / "SKILL.md",
        target / ".claude" / "skills" / "ppt-studio" / "SKILL.md",
    )
    for f in sorted((TEMPLATES / "skills" / "ppt-studio" / "references").glob("*.md")):
        copy_fn(f, target / ".claude" / "skills" / "ppt-studio" / "references" / f.name)

    # Agents
    for f in sorted((TEMPLATES / "agents").glob("*.md")):
        copy_fn(f, target / ".claude" / "agents" / f.name)

    # Hooks
    for f in sorted((TEMPLATES / "hooks").glob("*.py")):
        copy_fn(f, target / ".claude" / "hooks" / f.name)

    # Scripts
    for f in sorted((TEMPLATES / "scripts").glob("*.py")):
        copy_fn(f, target / "scripts" / f.name)

    # Themes
    for f in sorted((TEMPLATES / "themes").glob("*.json")):
        copy_fn(f, target / "themes" / f.name)

    # Package files
    copy_fn(TEMPLATES / "package.json", target / "package.json")
    copy_fn(TEMPLATES / "requirements.txt", target / "requirements.txt")


def copy_user_files(target: Path) -> None:
    """Copy user files (never overwrite)."""
    print("\nUser files:")
    copy_if_missing(TEMPLATES / "config.md", target / ".ppt" / "config.md")


def setup_gitignore(target: Path, update_mode: bool) -> None:
    """Set up .gitignore with PPT Studio entries."""
    print("\nGitignore:")
    gitignore = target / ".gitignore"
    template_content = (TEMPLATES / "gitignore").read_text()

    if gitignore.exists():
        existing = gitignore.read_text()
        if GITIGNORE_MARKER in existing:
            if update_mode:
                # Remove from marker to end, append fresh
                before = existing[: existing.index(GITIGNORE_MARKER)]
                gitignore.write_text(before + template_content)
                print("  update: .gitignore (PPT Studio section refreshed)")
            else:
                print("  skip (exists): .gitignore already has PPT Studio entries")
        else:
            gitignore.write_text(existing.rstrip() + "\n\n" + template_content)
            print("  append: .gitignore (added PPT Studio entries)")
    else:
        gitignore.write_text(template_content)
        print("  create: .gitignore")


def setup_gitkeep(target: Path) -> None:
    """Add .gitkeep to empty directories."""
    for d in GITKEEP_DIRS:
        gitkeep = target / d / ".gitkeep"
        gitkeep.touch(exist_ok=True)


def setup_git(target: Path) -> None:
    """Initialize git repo if needed."""
    if not (target / ".git").exists():
        print("\nInitializing git repository...")
        subprocess.run(["git", "init", "-q"], cwd=target, check=True)


def find_python() -> str | None:
    """Find Python 3.12+ on the system."""
    candidates = ["python3.13", "python3.12", "python3", "python"]
    for candidate in candidates:
        path = shutil.which(candidate)
        if not path:
            continue
        try:
            result = subprocess.run(
                [path, "--version"], capture_output=True, text=True
            )
            version_str = result.stdout.strip().split()[-1]
            parts = version_str.split(".")
            major, minor = int(parts[0]), int(parts[1])
            if major >= 3 and minor >= 12:
                return path
        except (subprocess.SubprocessError, ValueError, IndexError):
            continue
    return None


def setup_python_venv(target: Path, update_mode: bool) -> None:
    """Create Python venv and install dependencies."""
    print("\nPython environment:")
    python = find_python()

    if not python:
        print("  Warning: Python 3.12+ not found.", file=sys.stderr)
        print(f"    Install: {install_hint('python')}", file=sys.stderr)
        venv_py = venv_python(target)
        print(f"    Then: {python or 'python3.12'} -m venv {target / '.venv'}", file=sys.stderr)
        print(f"    Then: {venv_pip(target)} install -r {target / 'requirements.txt'}", file=sys.stderr)
        return

    venv_dir = target / ".venv"
    pip = venv_pip(target)

    if not venv_dir.exists():
        print(f"  Creating venv with {python}...")
        subprocess.run([python, "-m", "venv", str(venv_dir)], check=True)
        print("  Installing pip dependencies...")
        subprocess.run(
            [str(pip), "install", "-q", "-r", str(target / "requirements.txt")],
            check=True,
        )
        print(f"  Python venv ready: {venv_dir}")
    else:
        if update_mode:
            print("  Updating pip dependencies...")
            subprocess.run(
                [str(pip), "install", "-q", "-r", str(target / "requirements.txt")],
                check=True,
            )
        else:
            print("  skip (exists): .venv")


def setup_npm(target: Path, update_mode: bool) -> None:
    """Install npm dependencies."""
    print("\nNode.js dependencies:")

    if not shutil.which("npm"):
        print("  Warning: npm not found.", file=sys.stderr)
        print(f"    Install: {install_hint('npm')}", file=sys.stderr)
        print(f"    Then: cd {target} && npm install", file=sys.stderr)
        return

    node_modules = target / "node_modules"
    if not node_modules.exists():
        print("  Installing npm dependencies...")
        subprocess.run(
            ["npm", "install", "--silent"], cwd=target,
            capture_output=True, text=True,
        )
        print("  npm packages ready")
    else:
        if update_mode:
            print("  Updating npm dependencies...")
            subprocess.run(
                ["npm", "install", "--silent"], cwd=target,
                capture_output=True, text=True,
            )
        else:
            print("  skip (exists): node_modules")


def check_system_dependencies() -> bool:
    """Check and report optional system dependencies. Returns whether soffice was found."""
    print("\nSystem dependencies:")

    soffice = find_soffice()
    if soffice:
        print("  LibreOffice: found")
    else:
        print("  LibreOffice: NOT FOUND (optional — needed for visual QA)")
        print(f"    Install: {install_hint('libreoffice')}")

    if shutil.which("pdftoppm"):
        print("  Poppler (pdftoppm): found")
    else:
        print("  Poppler (pdftoppm): NOT FOUND (optional — needed for visual QA)")
        print(f"    Install: {install_hint('poppler')}")

    return soffice is not None


def print_summary(target: Path, update_mode: bool, soffice_found: bool) -> None:
    """Print final summary."""
    print()
    print("=" * 64)

    if update_mode:
        print(f"PPT Studio updated in: {target}")
        print()
        print("System files refreshed. User files untouched.")
    else:
        print(f"PPT Studio ready in: {target}")
        print()
        print("Next steps:")
        print(f"  1. cd {target}")
        print("  2. Open Claude Code in this directory")
        print("  3. Try these commands:")
        print("     /create-deck    — brainstorm + plan-driven creation")
        print("     /improve-deck   — review + edit an existing deck")
        print("     /deck-from-doc  — turn a document into slides")
        print("     /review          — analyze a deck or document")
        print("     /create          — build slides (plan or direct mode)")
        print("     /edit            — modify existing slides")

    if not soffice_found:
        print()
        print("Note: Install LibreOffice + Poppler for high-fidelity slide")
        print("rendering and visual QA. Without them, thumbnail.py uses")
        print("a basic fallback renderer.")

    print("=" * 64)


# ─── Main ────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Set up a directory as a PPT Studio workspace for Claude Code.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
System files (refreshed with --update):
  CLAUDE.md, .claude/commands/*, .claude/skills/*, .claude/agents/*,
  .claude/hooks/*, .claude/settings.json, scripts/*, themes/*,
  package.json, requirements.txt

User files (never overwritten):
  .ppt/config.md, .claude/settings.local.json, .ppt/decks/*
  (plans, reviews, builds), templates/*, assets/*
""",
    )
    parser.add_argument("target", help="Directory to set up as a PPT Studio workspace")
    parser.add_argument(
        "--update", action="store_true",
        help="Refresh system files only (preserves user files)",
    )
    args = parser.parse_args()

    target = Path(args.target).resolve()

    if target == TOOLKIT_DIR:
        print("Error: cannot bootstrap into the toolkit repo itself.", file=sys.stderr)
        sys.exit(1)

    if not target.is_dir():
        print(f"Error: target directory does not exist: {target}", file=sys.stderr)
        sys.exit(1)

    validate_templates()

    copy_fn = copy_and_overwrite if args.update else copy_if_missing

    print(f"Setting up PPT Studio in: {target}")
    print(f"Platform: {SYSTEM}")
    print()

    create_directories(target)
    copy_system_files(target, copy_fn)
    copy_user_files(target)
    setup_gitignore(target, args.update)
    setup_gitkeep(target)
    setup_git(target)
    setup_python_venv(target, args.update)
    setup_npm(target, args.update)
    soffice_found = check_system_dependencies()
    print_summary(target, args.update, soffice_found)


if __name__ == "__main__":
    main()
