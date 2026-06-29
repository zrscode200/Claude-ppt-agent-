#!/usr/bin/env python3
"""Setup hook — loads PPT Studio config and injects context at session init."""

import json
import os
import sys
from pathlib import Path


def main():
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))
    config_path = project_dir / ".ppt" / "config.md"
    context_parts = []

    # Parse config
    if config_path.exists():
        content = config_path.read_text()
        for line in content.splitlines():
            line = line.strip()
            if line.startswith("mode:"):
                mode = line.split(":", 1)[1].strip()
                context_parts.append(f"Autonomy mode: {mode}")
            elif line.startswith("default_theme:"):
                theme = line.split(":", 1)[1].strip()
                context_parts.append(f"Default theme: {theme}")

    # Count available themes
    themes_dir = project_dir / "themes"
    if themes_dir.exists():
        themes = list(themes_dir.glob("*.json"))
        context_parts.append(f"Available themes: {len(themes)}")

    # Count existing decks
    decks_dir = project_dir / ".ppt" / "decks"
    if decks_dir.exists():
        decks = [d for d in decks_dir.iterdir() if d.is_dir()]
        if decks:
            context_parts.append(f"Existing decks: {len(decks)}")

    # Check dependencies
    missing = []
    try:
        import importlib
        for mod in ["markitdown", "PIL", "defusedxml"]:
            try:
                importlib.import_module(mod)
            except ImportError:
                missing.append(mod)
    except Exception:
        pass

    if missing:
        context_parts.append(f"Missing Python packages: {', '.join(missing)}")

    output = {
        "additionalContext": "PPT Studio: " + "; ".join(context_parts) if context_parts else ""
    }
    print(json.dumps(output))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(json.dumps({}))
        sys.exit(0)
