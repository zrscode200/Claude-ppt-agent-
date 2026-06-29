---
description: Show active decks and their current workflow phase
---

# Status

Report the active decks in this workspace and where each one is in the PPT
Studio workflow (planning, ready to build, built/needs QA, QA complete, etc.).

OpenCode does not run an automatic session-start hook, so run this command when
you want a quick picture of deck state before creating, editing, or reviewing.

## Instructions

1. Run the status script from the workspace root:

   ```bash
   .venv/bin/python scripts/status.py 2>/dev/null || python3 scripts/status.py
   ```

2. Summarize the output for the user. If there are no active decks, suggest
   `/create-deck`, `/create`, or `/review` as starting points.
