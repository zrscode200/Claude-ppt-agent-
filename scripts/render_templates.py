#!/usr/bin/env python3
"""Render PPT Studio runtime templates.

Combines the shared source in ``core/`` with per-runtime mechanics in
``adapters/<runtime>/`` and writes a complete, ready-to-stamp tree into
``generated/<runtime>/``. The bootstrap installer (``init-ppt-studio.py``)
copies from ``generated/<runtime>/``; it never renders.

Usage:
    python3.12 scripts/render_templates.py            # render all runtimes
    python3.12 scripts/render_templates.py --runtime claude
    python3.12 scripts/render_templates.py --check    # verify generated/ is fresh

The Claude render is the identity baseline: with the default (empty) token map
its output is byte-identical to the legacy ``templates/`` tree. Per-runtime
token substitution is layered on in later waves; the Claude token values always
reproduce the canonical Claude dialect so existing output never drifts.
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CORE = REPO_ROOT / "core"
ADAPTERS = REPO_ROOT / "adapters"
GENERATED = REPO_ROOT / "generated"

RUNTIMES = ("claude", "opencode")

# Per-runtime placement + token configuration.
#
# ``dirs`` maps a logical core group to its destination directory inside the
# generated tree. ``files`` maps a single core file to a destination path.
# ``tokens`` is the ordered substitution map applied to text bodies (commands,
# skills, agents, instruction doc). Wave 1 uses an empty token map for Claude so
# output is byte-identical to the legacy templates.
RUNTIME_CONFIG = {
    # Claude is the identity baseline: each token maps back to the canonical
    # Claude-dialect string, so generated/claude/ stays byte-identical to the
    # legacy templates/ output even though core/ now carries {{TOKENS}}.
    "claude": {
        "instruction_doc": "CLAUDE.md",
        "command_dir": ".claude/commands",
        "skill_dir": ".claude/skills",
        "agent_dir": ".claude/agents",
        "tokens": {
            "{{RUNTIME_NAME}}": "Claude Code",
            "{{INSTRUCTION_DOC}}": "CLAUDE.md",
            "{{SKILL_DIR}}": ".claude/skills",
            "{{AGENT_DIR}}": ".claude/agents",
        },
    },
    # OpenCode uses AGENTS.md as the instruction doc, singular agent/command
    # dirs (verified against the opencode 1.17.9 loader), and plural skills/.
    "opencode": {
        "instruction_doc": "AGENTS.md",
        "command_dir": ".opencode/command",
        "skill_dir": ".opencode/skills",
        "agent_dir": ".opencode/agent",
        "tokens": {
            "{{RUNTIME_NAME}}": "OpenCode",
            "{{INSTRUCTION_DOC}}": "AGENTS.md",
            "{{SKILL_DIR}}": ".opencode/skills",
            "{{AGENT_DIR}}": ".opencode/agent",
        },
    },
}


def fail(msg: str) -> None:
    print(f"render_templates: error: {msg}", file=sys.stderr)
    sys.exit(1)


def apply_tokens(text: str, tokens: dict[str, str]) -> str:
    for key, value in tokens.items():
        text = text.replace(key, value)
    return text


def copy_file(src: Path, dst: Path, tokens: dict[str, str]) -> None:
    """Copy src to dst, substituting tokens when a non-empty token map is given.

    The CALLER decides whether a file is tokenized by passing tokens or {}.
    Files that must stay verbatim (themes, scripts, requirements.txt, config.md,
    gitignore, opencode.json) are always copied with an empty token map.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    if tokens:
        dst.write_text(apply_tokens(src.read_text(), tokens))
        shutil.copymode(src, dst)
    else:
        shutil.copy2(src, dst)


def copy_glob(src_dir: Path, pattern: str, dst_dir: Path, tokens: dict[str, str]) -> None:
    for f in sorted(src_dir.glob(pattern)):
        if f.is_file():
            copy_file(f, dst_dir / f.name, tokens)


# OpenCode subagent frontmatter, keyed by core agent filename. Description is
# the routing hint the primary uses to delegate; mode: subagent registers it as
# a delegatable helper (not a user-driven primary). These agents are read-only
# advisors invoked by the main session, mirroring the prose-driven spawn model.
OPENCODE_AGENT_FRONTMATTER = {
    "style-extractor.md": (
        "Extracts the visual style (colors, fonts, layout language) from a "
        "reference .pptx or slide images and returns a concise style report."
    ),
    "slide-builder.md": (
        "Builds an assigned range of slides from an approved content plan and "
        "style plan, writing its slide code to a designated file."
    ),
    "slide-editor.md": (
        "Applies a scoped set of edits to existing slides per an approved edit "
        "plan, preserving deck style and structure."
    ),
    "qa-reviewer.md": (
        "Inspects rendered slides with fresh eyes for layout, spacing, "
        "contrast, typography, diagram, and consistency issues; writes a QA "
        "report and returns a summary."
    ),
}


def opencode_agent_frontmatter(name: str) -> str:
    desc = OPENCODE_AGENT_FRONTMATTER.get(name)
    if desc is None:
        fail(f"missing OpenCode frontmatter for agent: {name}")
    stem = name[:-3] if name.endswith(".md") else name
    return f"---\nname: {stem}\ndescription: {desc}\nmode: subagent\n---\n\n"


def render_agents(runtime: str, dst_dir: Path, tokens: dict[str, str]) -> None:
    """Render core agent prompt bodies into the runtime's agent dir.

    Claude: plain prompt body, byte-identical to the legacy templates.
    OpenCode: same body with OpenCode subagent frontmatter prepended.
    """
    for f in sorted((CORE / "agents").glob("*.md")):
        body = apply_tokens(f.read_text(), tokens) if tokens else f.read_text()
        if runtime == "opencode":
            body = opencode_agent_frontmatter(f.name) + body
        dst = dst_dir / f.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(body)
        shutil.copymode(f, dst)


def render_runtime(runtime: str, out_root: Path) -> Path:
    cfg = RUNTIME_CONFIG[runtime]
    tokens = cfg["tokens"]
    out = out_root / runtime
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    # --- Shared core content (placed into the runtime's native layout) ---
    # Commands
    copy_glob(CORE / "commands", "*.md", out / cfg["command_dir"], tokens)
    # Skill + references
    copy_file(
        CORE / "skills/ppt-studio/SKILL.md",
        out / cfg["skill_dir"] / "ppt-studio/SKILL.md",
        tokens,
    )
    copy_glob(
        CORE / "skills/ppt-studio/references",
        "*.md",
        out / cfg["skill_dir"] / "ppt-studio/references",
        tokens,
    )
    # Agents — Claude uses the plain prompt body (no frontmatter); OpenCode
    # needs `name`/`description`/`mode: subagent` frontmatter prepended so the
    # loader registers them as native subagents.
    render_agents(runtime, out / cfg["agent_dir"], tokens)
    # Scripts (runtime-neutral, no token substitution)
    copy_glob(CORE / "scripts", "*", out / "scripts", {})
    # Themes (runtime-neutral)
    copy_glob(CORE / "themes", "*.json", out / "themes", {})
    # Docs (carry runtime tokens: product-overview references the instruction
    # doc and skill dir)
    copy_glob(CORE / "docs", "*.md", out / "docs", tokens)
    # Root package files (package.json carries {{RUNTIME_NAME}})
    copy_file(CORE / "package.json", out / "package.json", tokens)
    copy_file(CORE / "requirements.txt", out / "requirements.txt", {})
    # config.md and gitignore are kept at the generated-tree root; the installer
    # places them at their final destinations (.ppt/config.md, .gitignore).
    copy_file(CORE / "config.md", out / "config.md", {})
    copy_file(CORE / "gitignore", out / "gitignore", {})
    # Shared instruction doc -> the runtime's instruction-doc filename at root
    # (CLAUDE.md for Claude, AGENTS.md for OpenCode), token-substituted.
    copy_file(CORE / "instruction-doc.md", out / cfg["instruction_doc"], tokens)

    # --- Per-runtime adapter mechanics (overlaid, may token-substitute) ---
    if runtime == "claude":
        render_claude_adapter(out, tokens)
    elif runtime == "opencode":
        render_opencode_adapter(out, tokens)
    else:  # pragma: no cover - guarded by RUNTIME_CONFIG
        fail(f"no adapter renderer for runtime: {runtime}")

    return out


def render_claude_adapter(out: Path, tokens: dict[str, str]) -> None:
    adapter = ADAPTERS / "claude"
    # Instruction doc (CLAUDE.md) is rendered from core/instruction-doc.md.
    # settings.json -> .claude/settings.json (Claude hook wiring).
    copy_file(adapter / "settings.json", out / ".claude/settings.json", {})
    # Hooks
    copy_glob(adapter / "hooks", "*.py", out / ".claude/hooks", {})


def render_opencode_adapter(out: Path, tokens: dict[str, str]) -> None:
    adapter = ADAPTERS / "opencode"
    # Instruction doc (AGENTS.md) is rendered from core/instruction-doc.md.
    # opencode.json config at root (verbatim).
    copy_file(adapter / "opencode.json", out / "opencode.json", {})
    # OpenCode has no SessionStart hook; the Claude session_start/setup hooks are
    # replaced by an explicit /status command + a status script. These are
    # OpenCode-only so Claude output is unaffected.
    copy_glob(adapter / "command", "*.md", out / ".opencode/command", tokens)
    copy_glob(adapter / "scripts", "*.py", out / "scripts", {})


def render_all(out_root: Path, only: str | None) -> None:
    runtimes = (only,) if only else RUNTIMES
    for rt in runtimes:
        if rt not in RUNTIME_CONFIG:
            fail(f"unknown runtime: {rt}")
        dest = render_runtime(rt, out_root)
        print(f"rendered: {dest.relative_to(REPO_ROOT) if out_root == GENERATED else dest}")


def _relfiles(root: Path) -> set[str]:
    return {
        str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()
    }


def dir_diff(committed: Path, rendered: Path) -> list[str]:
    """Return human-readable differences between two trees.

    Uses a deep, byte-level content comparison (NOT filecmp.dircmp, whose
    default shallow os.stat comparison can false-pass on same-size/same-mtime
    files with different content). This gate is the drift guarantee for every
    later wave, so it must compare content, not metadata.
    """
    diffs: list[str] = []
    left = _relfiles(committed)
    right = _relfiles(rendered)

    for rel in sorted(left - right):
        diffs.append(f"only in committed: {rel}")
    for rel in sorted(right - left):
        diffs.append(f"only in freshly-rendered: {rel}")
    for rel in sorted(left & right):
        # shallow=False forces a byte-for-byte content comparison.
        if not filecmp.cmp(committed / rel, rendered / rel, shallow=False):
            diffs.append(f"content differs: {rel}")
    return diffs


def check(only: str | None) -> None:
    runtimes = (only,) if only else RUNTIMES
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        all_diffs: list[str] = []
        for rt in runtimes:
            if rt not in RUNTIME_CONFIG:
                fail(f"unknown runtime: {rt}")
            render_runtime(rt, tmp_root)
            committed = GENERATED / rt
            if not committed.exists():
                all_diffs.append(f"missing committed tree: generated/{rt}")
                continue
            for d in dir_diff(committed, tmp_root / rt):
                all_diffs.append(f"[{rt}] {d}")
        if all_diffs:
            print("render_templates: generated/ is STALE:", file=sys.stderr)
            for d in all_diffs:
                print(f"  {d}", file=sys.stderr)
            print(
                "\nRe-run: python3.12 scripts/render_templates.py", file=sys.stderr
            )
            sys.exit(1)
        print("render_templates: generated/ is fresh.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render PPT Studio runtime templates.")
    parser.add_argument(
        "--runtime",
        choices=sorted(RUNTIME_CONFIG),
        help="Render only one runtime (default: all).",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Verify committed generated/ matches a fresh render; exit 1 if stale.",
    )
    args = parser.parse_args()

    if not CORE.is_dir():
        fail(f"missing core/ at {CORE}")
    if not ADAPTERS.is_dir():
        fail(f"missing adapters/ at {ADAPTERS}")

    if args.check:
        check(args.runtime)
    else:
        render_all(GENERATED, args.runtime)


if __name__ == "__main__":
    main()
