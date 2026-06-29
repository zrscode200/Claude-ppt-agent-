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
GENERATED = TOOLKIT_DIR / "generated"
DEFAULT_RUNTIME = "claude"

# The installer copies from a pre-rendered tree in generated/<runtime>/. It does
# not render; run scripts/render_templates.py to (re)build generated/.
def runtime_root(runtime: str) -> Path:
    return GENERATED / runtime

# Runtime-relative files that must be present in a rendered tree for it to be a
# valid stamp source. Kept minimal and runtime-agnostic: the instruction doc and
# a couple of always-present neutral files. The full per-runtime layout is
# whatever the renderer produced under generated/<runtime>/.
def required_files(runtime: str) -> list[str]:
    return [
        RUNTIME_INSTRUCTION_DOC[runtime],
        "config.md",
        "package.json",
        "requirements.txt",
        "gitignore",
        "scripts/thumbnail.py",
        "docs/product-overview.md",
    ]

# Per-runtime instruction-doc filename at the generated-tree root.
RUNTIME_INSTRUCTION_DOC = {
    "claude": "CLAUDE.md",
    "opencode": "AGENTS.md",
}

SUPPORTED_RUNTIMES = ("claude", "opencode")

# Generated-tree files that map to user-owned destinations or need special
# placement, handled outside the generic recursive copy.
#   config.md  -> .ppt/config.md  (user file, never overwritten)
#   gitignore  -> .gitignore      (section-merged, not a plain copy)
SPECIAL_SOURCE_FILES = {"config.md", "gitignore"}

# Files that, once present in the target, are never overwritten even with
# --update (the user owns them). Expressed as target-relative paths.
USER_OWNED_FILES = {
    ".ppt/config.md",
    ".claude/settings.local.json",
    "opencode.json",
}

SYSTEM = platform.system()  # 'Darwin', 'Linux', 'Windows'

# Runtime-neutral workspace directories created in every target. Runtime config
# directories (.claude/..., .opencode/...) are created implicitly by the
# recursive copy of the rendered tree.
DIRECTORIES = [
    ".ppt/decks",
    ".ppt/logs",
    "scripts",
    "themes",
    "templates",
    "assets",
    "output",
    "docs",
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


def validate_templates(src_root: Path, runtime: str) -> None:
    """Ensure the rendered runtime tree and its required files exist."""
    if not src_root.is_dir():
        print(
            f"Error: missing rendered tree: {src_root}\n"
            f"  Run: python3.12 scripts/render_templates.py",
            file=sys.stderr,
        )
        sys.exit(1)
    missing = [f for f in required_files(runtime) if not (src_root / f).exists()]
    if missing:
        print("Error: missing rendered files:", file=sys.stderr)
        for f in missing:
            print(f"  {src_root.name}/{f}", file=sys.stderr)
        print("  Run: python3.12 scripts/render_templates.py", file=sys.stderr)
        sys.exit(1)


def create_directories(target: Path) -> None:
    """Create workspace directory structure."""
    for d in DIRECTORIES:
        (target / d).mkdir(parents=True, exist_ok=True)


def copy_system_files(target: Path, src_root: Path, copy_fn) -> None:
    """Copy all system files from the rendered runtime tree.

    The rendered tree (generated/<runtime>/) already mirrors the final stamped
    layout, so this is a recursive copy: every file maps to the same relative
    path under the target. Special source files (config.md, gitignore) are
    handled elsewhere (user file / section-merged) and skipped here.
    """
    print("System files:")
    for src in sorted(src_root.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(src_root)
        # Use posix-style keys so set membership works on Windows too.
        rel_key = rel.as_posix()
        if rel_key in SPECIAL_SOURCE_FILES:
            continue
        # User-owned files (e.g. opencode.json) are never overwritten, even in
        # --update mode: force copy_if_missing regardless of the active copy_fn.
        fn = copy_if_missing if rel_key in USER_OWNED_FILES else copy_fn
        fn(src, target / rel)


def copy_user_files(target: Path, src_root: Path) -> None:
    """Copy user files (never overwrite)."""
    print("\nUser files:")
    copy_if_missing(src_root / "config.md", target / ".ppt" / "config.md")


def setup_gitignore(target: Path, src_root: Path, update_mode: bool) -> None:
    """Set up .gitignore with PPT Studio entries."""
    print("\nGitignore:")
    gitignore = target / ".gitignore"
    template_content = (src_root / "gitignore").read_text()

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

    req = target / "requirements.txt"

    def pip_install() -> None:
        # Non-fatal: a failed/absent pip must not abort stamping. File stamping
        # has already completed; deps can be installed later by the user.
        try:
            if not pip.exists():
                raise FileNotFoundError(pip)
            subprocess.run(
                [str(pip), "install", "-q", "-r", str(req)], check=True
            )
        except (subprocess.SubprocessError, OSError) as exc:
            print(f"  Warning: pip install skipped ({exc}).", file=sys.stderr)
            print(f"    Run later: {pip} install -r {req}", file=sys.stderr)

    if not venv_dir.exists():
        try:
            print(f"  Creating venv with {python}...")
            subprocess.run([python, "-m", "venv", str(venv_dir)], check=True)
        except (subprocess.SubprocessError, OSError) as exc:
            print(f"  Warning: venv creation skipped ({exc}).", file=sys.stderr)
            print(f"    Run later: {python} -m venv {venv_dir}", file=sys.stderr)
            return
        print("  Installing pip dependencies...")
        pip_install()
        print(f"  Python venv ready: {venv_dir}")
    else:
        if update_mode:
            print("  Updating pip dependencies...")
            pip_install()
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
    print("\nOptional enhancements:")

    soffice = find_soffice()
    if soffice:
        print("  LibreOffice: found (high-fidelity slide rendering)")
    else:
        print("  LibreOffice: not installed (using built-in renderer — works fine)")

    if shutil.which("pdftoppm"):
        print("  Poppler (pdftoppm): found")
    elif soffice:
        print("  Poppler (pdftoppm): not installed (needed alongside LibreOffice)")

    return soffice is not None


RUNTIME_LABEL = {"claude": "Claude Code", "opencode": "OpenCode"}


def print_summary(
    target: Path, runtime: str, update_mode: bool, soffice_found: bool
) -> None:
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
        print(f"  2. Open {RUNTIME_LABEL[runtime]} in this directory")
        print("  3. Try these commands:")
        print("     /create-deck    — brainstorm + plan-driven creation")
        print("     /improve-deck   — review + edit an existing deck")
        print("     /deck-from-doc  — turn a document into slides")
        print("     /review          — analyze a deck or document")
        print("     /create          — build slides (plan or direct mode)")
        print("     /edit            — modify existing slides")
        if runtime == "opencode":
            print("     /status          — show active decks and their phase")

    if not soffice_found:
        print()
        print("Note: QA visual inspection uses a built-in renderer.")
        print("For higher fidelity, install LibreOffice + Poppler (requires admin).")

    print("=" * 64)


# ─── Main ────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Set up a directory as a PPT Studio workspace for Claude Code or OpenCode.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Runtimes (--runtime):
  claude    Claude Code: CLAUDE.md + .claude/{commands,skills,agents,hooks}
  opencode  OpenCode: AGENTS.md + opencode.json + .opencode/{command,agent,skills}

System files (refreshed with --update):
  instruction doc, runtime command/skill/agent files, scripts/*, themes/*,
  docs/*, package.json, requirements.txt

User files (never overwritten, even with --update):
  .ppt/config.md, .claude/settings.local.json, opencode.json, .ppt/decks/*
  (plans, reviews, builds), templates/*, assets/*
""",
    )
    parser.add_argument("target", help="Directory to set up as a PPT Studio workspace")
    parser.add_argument(
        "--runtime",
        choices=SUPPORTED_RUNTIMES,
        default=DEFAULT_RUNTIME,
        help=f"Target agent runtime (default: {DEFAULT_RUNTIME})",
    )
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

    src_root = runtime_root(args.runtime)
    validate_templates(src_root, args.runtime)

    copy_fn = copy_and_overwrite if args.update else copy_if_missing

    print(f"Setting up PPT Studio ({RUNTIME_LABEL[args.runtime]}) in: {target}")
    print(f"Platform: {SYSTEM}")
    print()

    create_directories(target)
    copy_system_files(target, src_root, copy_fn)
    copy_user_files(target, src_root)
    setup_gitignore(target, src_root, args.update)
    setup_gitkeep(target)
    setup_git(target)
    setup_python_venv(target, args.update)
    setup_npm(target, args.update)
    soffice_found = check_system_dependencies()
    print_summary(target, args.runtime, args.update, soffice_found)


if __name__ == "__main__":
    main()
