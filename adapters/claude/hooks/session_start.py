#!/usr/bin/env python3
"""Session start hook — detects active decks and their current phase."""

import json
import os
import sys
from pathlib import Path


def detect_phase(deck_dir: Path) -> str:
    """Detect the current workflow phase for a deck."""
    versions = sorted(deck_dir.glob("v*/"), key=lambda p: p.name)

    if versions:
        latest = versions[-1]
        pptx_files = list(latest.glob("*.pptx"))

        if pptx_files:
            # Check if a post-build review exists
            reviews = sorted(deck_dir.glob("review-*.md"))
            if reviews:
                return f"QA complete ({latest.name})"
            else:
                return f"Built, needs QA ({latest.name})"

    # Check plan status
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

        # Check if still drafting the other plan
        if content_approved and style_drafts:
            return f"Content approved, style planning ({style_drafts[-1].name})"
        elif style_approved and content_drafts:
            return f"Style approved, content planning ({content_drafts[-1].name})"
        else:
            return f"Plan(s) approved ({approved}), ready to build"

    if content_drafts or style_drafts:
        latest_draft = (content_drafts + style_drafts)[-1]
        return f"Planning ({latest_draft.name})"

    # Check edit plans
    edit_content_drafts = sorted(deck_dir.glob("edit-content-plan-draft-*.md"))
    edit_style_drafts = sorted(deck_dir.glob("edit-style-plan-draft-*.md"))
    if edit_content_drafts or edit_style_drafts:
        latest_edit = (edit_content_drafts + edit_style_drafts)[-1]
        return f"Edit planning ({latest_edit.name})"

    # Check if only reviews exist (reviewed but no plans or builds yet)
    reviews = sorted(deck_dir.glob("review-*.md"))
    if reviews:
        return f"Reviewed ({reviews[-1].name})"

    return "New deck (no artifacts)"


def main():
    project_dir = Path(os.environ.get("CLAUDE_PROJECT_DIR", Path.cwd()))
    decks_dir = project_dir / ".ppt" / "decks"
    context_parts = []

    if decks_dir.exists():
        for deck_dir in sorted(decks_dir.iterdir()):
            if deck_dir.is_dir():
                phase = detect_phase(deck_dir)
                context_parts.append(f"Deck '{deck_dir.name}': {phase}")

    if context_parts:
        output = {
            "additionalContext": "Active decks:\n" + "\n".join(f"  - {p}" for p in context_parts)
        }
    else:
        output = {
            "additionalContext": "No active decks. Start with /create-deck, /create, or /review."
        }

    print(json.dumps(output))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(json.dumps({}))
        sys.exit(0)
