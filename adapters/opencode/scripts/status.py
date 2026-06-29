#!/usr/bin/env python3
"""PPT Studio status — report active decks and their current workflow phase.

OpenCode has no SessionStart hook, so this replaces the Claude session_start
hook as an explicit command (`/status`). It reads decks from .ppt/decks/ under
the current working directory and prints a human-readable summary to stdout.
"""

import sys
from pathlib import Path


def detect_phase(deck_dir: Path) -> str:
    """Detect the current workflow phase for a deck."""
    versions = sorted(deck_dir.glob("v*/"), key=lambda p: p.name)

    if versions:
        latest = versions[-1]
        pptx_files = list(latest.glob("*.pptx"))
        if pptx_files:
            reviews = sorted(deck_dir.glob("review-*.md"))
            if reviews:
                return f"QA complete ({latest.name})"
            return f"Built, needs QA ({latest.name})"

    content_approved = (deck_dir / "content-plan-approved.md").exists()
    style_approved = (deck_dir / "style-plan-approved.md").exists()
    content_drafts = sorted(deck_dir.glob("content-plan-draft-*.md"))
    style_drafts = sorted(deck_dir.glob("style-plan-draft-*.md"))

    if content_approved or style_approved:
        parts = []
        if content_approved:
            parts.append("content")
        if style_approved:
            parts.append("style")
        approved = " + ".join(parts)
        if content_approved and style_drafts:
            return f"Content approved, style planning ({style_drafts[-1].name})"
        if style_approved and content_drafts:
            return f"Style approved, content planning ({content_drafts[-1].name})"
        return f"Plan(s) approved ({approved}), ready to build"

    if content_drafts or style_drafts:
        latest_draft = (content_drafts + style_drafts)[-1]
        return f"Planning ({latest_draft.name})"

    edit_content_drafts = sorted(deck_dir.glob("edit-content-plan-draft-*.md"))
    edit_style_drafts = sorted(deck_dir.glob("edit-style-plan-draft-*.md"))
    if edit_content_drafts or edit_style_drafts:
        latest_edit = (edit_content_drafts + edit_style_drafts)[-1]
        return f"Edit planning ({latest_edit.name})"

    reviews = sorted(deck_dir.glob("review-*.md"))
    if reviews:
        return f"Reviewed ({reviews[-1].name})"

    return "New deck (no artifacts)"


def main() -> None:
    project_dir = Path.cwd()
    decks_dir = project_dir / ".ppt" / "decks"
    context_parts = []

    if decks_dir.exists():
        for deck_dir in sorted(decks_dir.iterdir()):
            if deck_dir.is_dir():
                context_parts.append(f"Deck '{deck_dir.name}': {detect_phase(deck_dir)}")

    if context_parts:
        print("Active decks:")
        for p in context_parts:
            print(f"  - {p}")
    else:
        print("No active decks. Start with /create-deck, /create, or /review.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # pragma: no cover - defensive
        print(f"status: could not read deck state: {exc}", file=sys.stderr)
        sys.exit(0)
